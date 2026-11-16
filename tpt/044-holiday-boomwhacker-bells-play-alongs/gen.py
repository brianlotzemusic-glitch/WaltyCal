#!/usr/bin/env python3
"""Color-Coded Carol Play-Alongs for Tuned Tubes, Bells & Xylophone (TpT 044): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   verify melodies, colours, staff positions, bar sums, layout, pages, fonts and files

Melodies live in tunes.py, each typed in C major and ALSO read from a second source file in its original key (MIDI, LilyPond or a printed
part) and transposed by code; the two must agree note for note.  Every page is drawn from those note lists: colour-coded notes on a staff
and colour-block play-along strips.  `--check` does not trust the drawing code: it parses the rendered HTML and recomputes, for every
note, the colour from the pitch (by semitone number), the staff height from the pitch, every bar's length from its note values, and
compares the notes read back with the transcription data.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in ../fonts.
"""
import json
import os
import re
import subprocess
import sys
from fractions import Fraction as F
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tunes as T  # noqa: E402

TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "color-coded-carol-play-alongs-tubes-bells"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#C23B35"   # Christmas red: this product's one accent (store chrome and cover only)
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Color-Coded Carol Play-Alongs for Tuned Tubes, Bells & Xylophone"
TM_NOTE = ("Boomwhackers® is a registered trademark of Whacky Music, Inc. This resource is not affiliated with, sponsored or endorsed by "
           "Whacky Music, Inc.; it uses the widely shared tube color scheme so it works with any C-to-C set of color-coded tubes, "
           "resonator bells or xylophones.")

# ------------------------------------------------------------------ colours (standard tube colour scheme, C major)
COLOR_NAME = {"C": "red", "D": "orange", "E": "yellow", "F": "green", "G": "turquoise", "A": "blue", "B": "purple"}
NAME_HEX = {"red": "#E3262E", "orange": "#F58A1F", "yellow": "#FFE21F", "green": "#3FAE49", "turquoise": "#12A8CE", "blue": "#2F5FBF", "purple": "#8B4CB0"}
TEXT_ON = {"red": "#fff", "orange": "#000", "yellow": "#000", "green": "#000", "turquoise": "#000", "blue": "#fff", "purple": "#fff"}
STEP = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}


def letter_color(letter):
    return NAME_HEX[COLOR_NAME[letter]]


def letter_text(letter):
    return TEXT_ON[COLOR_NAME[letter]]


def is_high_c(pitch):
    return pitch[0] == "C" and int(pitch[1:]) >= 5


def blk_label(pitch):
    return "C+" if is_high_c(pitch) else pitch[0]


# ------------------------------------------------------------------ notation glyphs (Bravura, SMuFL)
HEAD = {"black": 0xE0A4, "half": 0xE0A3, "whole": 0xE0A2}
COMPOSITE = {  # dur -> (up, down) glyph
    F(4): (0xE1D2, 0xE1D2), F(3): (0xE1D3, 0xE1D4), F(2): (0xE1D3, 0xE1D4), F(3, 2): (0xE1D5, 0xE1D6), F(1): (0xE1D5, 0xE1D6),
    F(3, 4): (0xE1D7, 0xE1D8), F(1, 2): (0xE1D7, 0xE1D8), F(1, 4): (0xE1D9, 0xE1DA)}
DOT_GLYPH = 0xE1E7
DOTTED = {F(3), F(3, 2), F(3, 4)}
FLAGS = {F(3, 4): 1, F(1, 2): 1, F(1, 4): 2}
HOLLOW = {F(4), F(3), F(2)}
CLEF_G = 0xE050
TIMESIG0 = 0xE080

W = 540.0
LEFT = 64.0
PAD = 5.0
CLEF_X = 3.0


def dia(midi_n):
    return 7 * (midi_n // 12) + {0: 0, 2: 1, 4: 2, 5: 3, 7: 4, 9: 5, 11: 6}[midi_n % 12]


E4_DIA = dia(64)


def step_of(pitch):
    return dia(T.midi(pitch)) - E4_DIA


def g(cp, x, y, size, fill="#000"):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Bravura" font-size="{size:.2f}" fill="{fill}">&#x{cp:X};</text>'


# ------------------------------------------------------------------ layout of one system
def bar_layout(bars, width=W, left=LEFT):
    """x ranges for the bars of one system: width proportional to beats, so every system has the same note density."""
    beats = [T.bar_beats(b) for b in bars]
    inner = width - left - 3
    usable = inner - 2 * PAD * len(bars)
    per_beat = usable / float(sum(beats))
    out, x = [], left
    for b in beats:
        bw = float(b) * per_beat + 2 * PAD
        out.append((x, x + bw, float(b)))
        x += bw
    return out, per_beat


def note_starts(bar):
    t, out = F(0), []
    for n in bar:
        out.append(t)
        t += n.dur
    return out


def beam_groups(bar, offset):
    """Runs of >=2 consecutive notes shorter than a quarter that start inside the same beat. `offset`: beats missing before a pickup."""
    starts = note_starts(bar)
    runs, cur = [], []
    for i, n in enumerate(bar):
        if n.dur < 1:
            if cur and int((starts[cur[-1]] + offset)) != int((starts[i] + offset)):
                runs.append(cur)
                cur = []
            cur.append(i)
        else:
            if cur:
                runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def head_w(dur):
    return 1.688 if dur == 4 else 1.18


def colored_head(cx, cy, s, dur, letter):
    fill = letter_color(letter)
    if dur == 4:
        out = f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{0.72 * s:.2f}" ry="{0.37 * s:.2f}" fill="{fill}"/>'
        out += f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{0.19 * s:.2f}" ry="{0.30 * s:.2f}" fill="#fff" transform="rotate(35 {cx:.2f} {cy:.2f})"/>'
    elif dur in HOLLOW:
        out = f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{0.52 * s:.2f}" ry="{0.355 * s:.2f}" fill="{fill}" transform="rotate(-20 {cx:.2f} {cy:.2f})"/>'
        out += f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{0.30 * s:.2f}" ry="{0.11 * s:.2f}" fill="#fff" transform="rotate(-38 {cx:.2f} {cy:.2f})"/>'
    else:
        out = f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{0.51 * s:.2f}" ry="{0.34 * s:.2f}" fill="{fill}" transform="rotate(-20 {cx:.2f} {cy:.2f})"/>'
    return out


def staff_group(bars, sysno, first_bar_no, meter, s, show_ts, bar_nos, tune_key, ver, tie_arcs=True):
    """SVG pieces (staff, notes) for one system. Returns (svg_string, height, yb, per_beat, layout)."""
    layout, per_beat = bar_layout(bars)
    top = 1.9 * s
    yb = top + 4 * s
    height = yb + 3.6 * s
    out = []
    for i in range(5):
        y = yb - i * s
        out.append(f'<line x1="{CLEF_X - 1:.1f}" y1="{y:.2f}" x2="{W - 1:.1f}" y2="{y:.2f}" stroke="#000" stroke-width="{0.16 * s:.2f}"/>')
    out.append(f'<line x1="{CLEF_X - 1:.1f}" y1="{yb - 4 * s:.2f}" x2="{CLEF_X - 1:.1f}" y2="{yb:.2f}" stroke="#000" stroke-width="1.1"/>')
    out.append(g(CLEF_G, CLEF_X, yb - s, 4 * s))
    if show_ts:
        n, d = meter
        out.append(g(TIMESIG0 + n, CLEF_X + 2.9 * s + 3, yb - 3 * s, 4 * s))
        out.append(g(TIMESIG0 + d, CLEF_X + 2.9 * s + 3, yb - s, 4 * s))
    offset_pick = F(0)
    prev_tie = None
    for bi, bar in enumerate(bars):
        x0, x1, blen = layout[bi]
        no = bar_nos[bi]
        is_pick = no == 0
        L = F(meter[0] * 4, meter[1])
        offset = (L - T.bar_beats(bar)) if is_pick else F(0)
        if no:
            out.append(f'<text x="{x0 + 2:.1f}" y="{yb - 4 * s - 0.9 * s + 0.5:.1f}" font-family="Oswald" font-weight="500" font-size="7" fill="#555">{no}</text>')
        starts = note_starts(bar)
        runs = beam_groups(bar, offset)
        in_run = {i: r for r in runs for i in r}
        xs = []
        for i, n in enumerate(bar):
            xs.append(x0 + PAD + float(starts[i]) / blen * (x1 - x0 - 2 * PAD) + 0.5)
        heads = []
        for i, n in enumerate(bar):
            st = step_of(n.pitch)
            cy = yb - st * s / 2
            left = xs[i]
            cx = left + head_w(n.dur) * s / 2
            heads.append((cx, cy, st))
        for i, n in enumerate(bar):
            cx, cy, st = heads[i]
            left = xs[i]
            letter = n.pitch[0]
            attrs = (f'class="nt" data-tune="{tune_key}" data-ver="{ver}" data-bar="{no}" data-pitch="{n.pitch}" data-dur="{n.dur}" '
                     f'data-cy="{cy:.2f}" data-cx="{cx:.2f}" data-sys="{sysno}" data-fill="{letter_color(letter)}" data-tie="{int(n.tie)}"')
            piece = [f"<g {attrs}>"]
            # ledger lines
            led = []
            if st <= -2:
                led = list(range(-2, st - 1, -2))
            elif st >= 10:
                led = list(range(10, st + 1, 2))
            for ls in led:
                ly = yb - ls * s / 2
                piece.append(f'<line x1="{left - 0.4 * s:.2f}" y1="{ly:.2f}" x2="{left + head_w(n.dur) * s + 0.4 * s:.2f}" y2="{ly:.2f}" stroke="#000" stroke-width="{0.2 * s:.2f}"/>')
            if i in in_run:
                run = in_run[i]
                up_dir = (sum(heads[j][2] for j in run) / len(run)) < 4
                piece.append(g(HEAD["black"], left, cy, 4 * s))
            else:
                up_dir = st < 4
                cp = COMPOSITE[n.dur][0 if up_dir else 1]
                piece.append(g(cp, left, cy, 4 * s))
            piece.append(colored_head(cx, cy, s, n.dur, letter))
            if n.dur in DOTTED:
                dy = cy - 0.5 * s if st % 2 == 0 else cy
                piece.append(g(DOT_GLYPH, left + head_w(n.dur) * s + 0.35 * s, dy, 4 * s))
            piece.append("</g>")
            out.append("".join(piece))
        # beams
        sw = 0.13 * s
        for run in runs:
            up_dir = (sum(heads[j][2] for j in run) / len(run)) < 4
            if up_dir:
                yend = min(heads[j][1] for j in run) - 3.3 * s
            else:
                yend = max(heads[j][1] for j in run) + 3.3 * s
            for j in run:
                left = xs[j]
                sx = left + 1.18 * s - sw / 2 if up_dir else left + sw / 2
                y0 = heads[j][1] - 0.168 * s if up_dir else heads[j][1] + 0.168 * s
                out.append(f'<line x1="{sx:.2f}" y1="{y0:.2f}" x2="{sx:.2f}" y2="{yend:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')

            def sx_of(j):
                return xs[j] + 1.18 * s - sw / 2 if up_dir else xs[j] + sw / 2
            xa, xb = sx_of(run[0]) - sw / 2, sx_of(run[-1]) + sw / 2
            by = yend if up_dir else yend - 0.5 * s
            out.append(f'<rect x="{xa:.2f}" y="{by:.2f}" width="{xb - xa:.2f}" height="{0.5 * s:.2f}" fill="#000"/>')
            # second beam for sixteenths: full between neighbours, stub otherwise
            sy = by + (0.75 * s if up_dir else -0.75 * s)
            for k, j in enumerate(run):
                if bar[j].dur != F(1, 4):
                    continue
                nb_right = k + 1 < len(run) and bar[run[k + 1]].dur == F(1, 4)
                nb_left = k > 0 and bar[run[k - 1]].dur == F(1, 4)
                if nb_right:
                    out.append(f'<rect x="{sx_of(j) - sw / 2:.2f}" y="{sy:.2f}" width="{sx_of(run[k + 1]) - sx_of(j) + sw:.2f}" height="{0.5 * s:.2f}" fill="#000"/>')
                elif not nb_left:
                    stub = 1.0 * s
                    xx = sx_of(j) - sw / 2 - (stub if k > 0 else 0) if k > 0 else sx_of(j) - sw / 2
                    out.append(f'<rect x="{xx:.2f}" y="{sy:.2f}" width="{stub:.2f}" height="{0.5 * s:.2f}" fill="#000"/>')
                elif nb_left and not nb_right:
                    pass
        # tie to next note (same system only)
        for i, n in enumerate(bar):
            if n.tie:
                nxt = None
                if i + 1 < len(bar):
                    nxt = (heads[i + 1][0], heads[i + 1][1])
                elif bi + 1 < len(bars):
                    nx0, nx1, nblen = layout[bi + 1]
                    nxt = (nx0 + PAD + 0.5 + head_w(bars[bi + 1][0].dur) * s / 2, yb - step_of(bars[bi + 1][0].pitch) * s / 2)
                if nxt:
                    cx, cy, st = heads[i]
                    up_stem = st < 4
                    sign = 1 if up_stem else -1     # tie sits on the side opposite the stem
                    ya = cy + sign * 0.75 * s
                    out.append(f'<path d="M{cx + 0.3 * s:.2f} {ya:.2f} Q{(cx + nxt[0]) / 2:.2f} {ya + sign * 1.4 * s:.2f} {nxt[0] - 0.3 * s:.2f} {ya:.2f}" fill="none" stroke="#000" stroke-width="{0.14 * s:.2f}"/>')
        # barline at the end of the bar
        last = (bi == len(bars) - 1)
        out.append(f'<line x1="{x1 - 1:.2f}" y1="{yb - 4 * s:.2f}" x2="{x1 - 1:.2f}" y2="{yb:.2f}" stroke="#000" stroke-width="1.1"/>')
    return "".join(out), height, yb, per_beat, layout


def strip_rows(bars, layout, meter, bar_nos, ys, h, tune_key, ver, letters=None, row=0, rest_style=True):
    """Colour-block play-along strip for one system. `letters`: only these pitch letters get blocks (parts rows)."""
    out = []
    L = F(meter[0] * 4, meter[1])
    for bi, bar in enumerate(bars):
        x0, x1, blen = layout[bi]
        starts = note_starts(bar)
        ux = x1 - x0 - 2 * PAD
        out.append(f'<line x1="{x0 + 1:.2f}" y1="{ys:.2f}" x2="{x1 - 1:.2f}" y2="{ys:.2f}" stroke="#bbb" stroke-width="0.6"/>')
        out.append(f'<line x1="{x0 + 1:.2f}" y1="{ys + h:.2f}" x2="{x1 - 1:.2f}" y2="{ys + h:.2f}" stroke="#bbb" stroke-width="0.6"/>')
        for i, n in enumerate(bar):
            bx = x0 + PAD + float(starts[i]) / blen * ux
            bw = float(n.dur) / blen * ux
            letter = n.pitch[0]
            if letters is not None and letter not in letters:
                continue
            nm = COLOR_NAME[letter]
            lab = blk_label(n.pitch)
            fs = max(6.5, min(13.0, bw * 0.78 if len(lab) == 1 else bw * 0.5))
            out.append(f'<g class="blk" data-tune="{tune_key}" data-ver="{ver}" data-bar="{bar_nos[bi]}" data-pitch="{n.pitch}" data-dur="{n.dur}" data-row="{row}" data-w="{bw - 2:.2f}">'
                       f'<rect x="{bx + 1:.2f}" y="{ys:.2f}" width="{bw - 2:.2f}" height="{h:.2f}" rx="3" fill="{NAME_HEX[nm]}" stroke="#000" stroke-width="1"/>'
                       f'<text x="{bx + bw / 2:.2f}" y="{ys + h / 2 + fs * 0.36:.2f}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="{fs:.1f}" fill="{TEXT_ON[nm]}">{lab}</text></g>')
    return "".join(out)


def beat_ruler(bars, layout, meter, bar_nos, y):
    L = F(meter[0] * 4, meter[1])
    out = []
    for bi, bar in enumerate(bars):
        x0, x1, blen = layout[bi]
        ux = x1 - x0 - 2 * PAD
        first = int(L - T.bar_beats(bar)) if bar_nos[bi] == 0 else 0
        for k in range(int(blen)):
            bx = x0 + PAD + k / blen * ux
            out.append(f'<text x="{bx + 3:.2f}" y="{y:.2f}" font-family="Source Sans 3" font-size="6.5" fill="#666">{first + k + 1}</text>')
    return "".join(out)


def system_svg(tune, ver, sysno, idxs, bars_all, s, strip_h, with_staff=True, rows=None, show_ts=True, ruler=True, px=None):
    """One system: (staff +) strip(s). rows: None = one full-colour strip; else list of letter-lists (parts)."""
    meter = tune["meter"]
    bars = [bars_all[i] for i in idxs]
    bar_nos = [i for i in idxs]   # index 0 is the pickup when the tune has one, else bar 1 is index 0
    if not tune["pickup"]:
        bar_nos = [i + 1 for i in idxs]
    parts, y = [], 0.0
    layout, per_beat = bar_layout(bars)
    if with_staff:
        grp, hgt, yb, per_beat, layout = staff_group(bars, sysno, idxs[0], meter, s, show_ts, bar_nos, tune["key"], ver)
        parts.append(grp)
        y = hgt + 4
    else:
        for bi in range(len(bars)):
            if bar_nos[bi]:
                parts.append(f'<text x="{layout[bi][0] + 2:.1f}" y="9" font-family="Oswald" font-weight="500" font-size="7" fill="#555">{bar_nos[bi]}</text>')
        y = 11
        yb = 0
    if rows is None:
        parts.append(strip_rows(bars, layout, meter, bar_nos, y, strip_h, tune["key"], ver))
        y += strip_h
    else:
        for r, letters in enumerate(rows):
            parts.append(f'<g class="chip" data-row="{r}"><rect x="0" y="{y:.1f}" width="{LEFT - 8:.1f}" height="{strip_h:.1f}" rx="4" fill="#000"/>'
                         f'<text x="{(LEFT - 8) / 2:.1f}" y="{y + strip_h / 2 + 1:.1f}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="13" fill="#fff">{r + 1}</text>'
                         f'<text x="{(LEFT - 8) / 2:.1f}" y="{y + strip_h - 4:.1f}" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="6.5" fill="#fff">{" ".join(letters)}</text></g>')
            parts.append(strip_rows(bars, layout, meter, bar_nos, y, strip_h, tune["key"], ver, letters=set(letters), row=r))
            y += strip_h + 4
        y -= 4
    if ruler:
        parts.append(beat_ruler(bars, layout, meter, bar_nos, y + 8))
        y += 11
    total = y + 2
    size = f'width="{px}px" height="{total * px / W:.1f}px"' if px else f'width="{W:.0f}pt" height="{total:.1f}pt"'
    return (f'<svg class="sys" data-tune="{tune["key"]}" data-ver="{ver}" data-s="{s}" data-yb="{yb:.2f}" data-meter="{meter[0]}/{meter[1]}" '
            f'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {total:.1f}" {size} style="display:block">{"".join(parts)}</svg>')


def split_systems(n_bars, per):
    out, i = [], 0
    while i < n_bars:
        out.append(list(range(i, min(i + per, n_bars))))
        i += per
    return out


# ------------------------------------------------------------------ the three versions of a tune
def tune_bars(tune, ver):
    if ver == "easy":
        return T.easy_bars(tune)
    return tune["bars"]


def ver_systems(tune, ver):
    if ver == "easy":
        a, b = tune["easy"]
        per = tune["per_sys_easy"]
        return [[a + i for i in s] for s in split_systems(b - a, per)]
    return split_systems(len(tune["bars"]), tune["per_sys"])


def ver_bars_all(tune, ver):
    """Bars indexed like tune['bars'] (easy: simplified bars placed at their original index; others left unused)."""
    if ver == "easy":
        a, b = tune["easy"]
        arr = [None] * len(tune["bars"])
        for i, bar in zip(range(a, b), T.easy_bars(tune)):
            arr[i] = bar
        return arr
    return tune["bars"]


# ------------------------------------------------------------------ CSS and page frame
def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"),
             ("Oswald", 700, "normal", "oswald-latin-700-normal"),
             ("Source Sans 3", 400, "normal", "source-sans-3-latin-400-normal"),
             ("Source Sans 3", 400, "italic", "source-sans-3-latin-400-italic"),
             ("Source Sans 3", 600, "normal", "source-sans-3-latin-600-normal"),
             ("Source Sans 3", 700, "normal", "source-sans-3-latin-700-normal"),
             ("Bravura", 400, "normal", "bravura")]
    return "".join(f"@font-face{{font-family:'{n}';font-weight:{w};font-style:{s};src:url('{f}/{file}.woff2') format('woff2');}}"
                   for n, w, s, file in faces)


CSS = """
@page { size: 8.5in 11in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: 'Source Sans 3', sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; break-after: page;
        padding: 0.42in 0.5in 0.38in; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; break-after: auto; }
.h { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; }
.l { font-family: 'Oswald'; font-weight: 300; }
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-size: 25pt; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 18pt; font-size: 12pt; margin: 9pt 0 5pt; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.d { flex: 0 0 1.6in; }
.how { font-size: 11pt; margin: 2pt 0 6pt; line-height: 1.35; }
.how b { font-weight: 700; }
.legend { display: flex; flex-wrap: wrap; gap: 4pt 6pt; margin: 2pt 0 6pt; align-items: center; }
.lg { display: flex; align-items: center; gap: 4pt; border: 1pt solid #000; border-radius: 5pt; padding: 1pt 7pt 1pt 2pt; font-size: 8.5pt; }
.lg i { display: inline-block; width: 15pt; height: 13pt; border: 1pt solid #000; border-radius: 3pt; text-align: center; font-style: normal; font-family: 'Oswald'; font-weight: 700; font-size: 9pt; line-height: 12pt; }
.lg b { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 8pt; letter-spacing: .02em; }
.sysbox { flex: 1; display: flex; flex-direction: column; justify-content: space-around; padding: 4pt 0 2pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 11pt 0 4pt; letter-spacing: .02em; }
.doc h2 .acc { color: ACCENT; }
.doc p, .doc li { font-size: 10.5pt; line-height: 1.36; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; font-size: 9.5pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 5pt; text-align: left; vertical-align: top; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9pt; background: #000; color: #fff; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 6pt; padding: 6pt 9pt; margin: 5pt 0; }
.box b.t { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 10.5pt; letter-spacing: .03em; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 40pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 66pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 16pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
.tubes { display: flex; align-items: flex-end; justify-content: center; gap: 9pt; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


# ------------------------------------------------------------------ page numbers
P_COVER, P_GUIDE, P_KEY = 1, 2, 3
P_TUNE0 = 4
VERS = ["easy", "full", "parts"]
N_TUNES = len(T.TUNES)
P_OWN = P_TUNE0 + 3 * N_TUNES
P_TERMS = P_OWN + 1
TOTAL_PAGES = P_TERMS


def tune_page_no(ti, ver):
    return P_TUNE0 + 3 * ti + VERS.index(ver)


# ------------------------------------------------------------------ colour legend chips
def legend_html(letters):
    chips = []
    for L in letters:
        nm = COLOR_NAME[L]
        chips.append(f'<span class="lg"><i style="background:{NAME_HEX[nm]};color:{TEXT_ON[nm]}">{L}</i><b>{nm}</b></span>')
    return f'<div class="legend">{"".join(chips)}</div>'


def sys_pitch_letters(tune):
    return T.used_letters(tune["bars"])


# ------------------------------------------------------------------ carol pages
INFO = {"easy": ("EASY", "Grades 1–2"), "full": ("FULL", "Grades 3–5"), "parts": ("PARTS", "2–3 groups")}


def tune_header(tune, ver, ti):
    tag, ln = INFO[ver]
    tempo = tune["tempo"][0 if ver == "easy" else 1]
    n, d = tune["meter"]
    sub = f'{escape(tune["comp"])}, {tune["year"]} · {n}/{d} time · try {tempo} beats per minute'
    return (f'<div class="top"><div class="h t">{escape(tune["title"])}<small>{sub}</small></div>'
            f'<div class="tag"><div class="lv">{tag}</div><div class="ln">{ln}</div></div></div>'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>')


def tune_page(ti, ver, wm=False):
    tune = T.TUNES[ti]
    wmh = '<div class="wm">PREVIEW</div>' if wm else ""
    letters = used_letters_for(tune, ver)
    pg = tune_page_no(ti, ver)
    if ver == "easy":
        how = ('<div class="how"><b>Easy version.</b> Look at your color on the staff, then find it in the strip below. '
               'Each block is one note: a short block is a short note, a long block is a long note. Play your color when its block comes up. '
               'The small numbers under the strip are the beats: count them out loud.</div>')
        s, sh = 8.2, 36
    elif ver == "full":
        how = ('<div class="how"><b>Full version.</b> The whole tune with its real rhythm. Read the colored notes on the staff or just follow the blocks. '
               'C+ means the short, high C tube (also red). Short blocks are eighth notes or shorter.</div>')
        s, sh = 6.6, 25
    else:
        how = ('<div class="how"><b>Parts for groups.</b> Every group plays only its own colors. Row 1, row 2 and row 3 together play the whole carol. '
               'Everyone counts the beats under the strip and waits for their own blocks.</div>')
        s, sh = 6.6, 22
    systems = ver_systems(tune, ver)
    bars_all = ver_bars_all(tune, ver)
    body = []
    for si, idxs in enumerate(systems):
        if ver == "parts":
            body.append(system_svg(tune, "parts", si, idxs, bars_all, s, sh, with_staff=False, rows=tune["groups"]))
        else:
            body.append(system_svg(tune, ver, si, idxs, bars_all, s, sh, with_staff=True, show_ts=(si == 0)))
    extra = ""
    if ver == "parts":
        rows = "".join(f'<tr><td><b>Group {i + 1}</b></td><td>{" · ".join(f"{L} ({COLOR_NAME[L]})" for L in grp)}</td>'
                       f'<td>{count_notes(tune, grp)} notes</td></tr>' for i, grp in enumerate(tune["groups"]))
        extra = (f'<div class="doc" style="margin-top:6pt"><table><tr><th>Group</th><th>Plays these colors</th><th>In this carol</th></tr>{rows}</table></div>')
    elif ver == "easy":
        extra = ('<div class="box"><b class="t">Play-along checklist</b><br>'
                 '☐ Say the colors in rhythm, tapping the beat    ☐ Play it with your tubes, bells or bars, slowly '
                 '   ☐ Play it again without stopping    ☐ Speed up a little</div>')
    return (f'<section class="page">{wmh}{tune_header(tune, ver, ti)}{how}{legend_html(letters)}'
            f'<div class="sysbox">{"".join(body)}</div>{extra}'
            f'{foot(COPY, f"Page {pg}")}</section>')


def used_letters_for(tune, ver):
    if ver == "easy":
        return T.used_letters(T.easy_bars(tune))
    return T.used_letters(tune["bars"])


def count_notes(tune, grp):
    return sum(1 for b in tune["bars"] for n in b if n.pitch[0] in grp)


# ------------------------------------------------------------------ cover art: tubes
TUBE_LEN = {"C": 1.0, "D": 0.89, "E": 0.79, "F": 0.75, "G": 0.67, "A": 0.59, "B": 0.53, "C+": 0.5}
# Cover tubes use the real tube colours (exception to the STYLE.md cover-tint rule: the colours are the product)
TINTS_OLD = ["#6B1E1A", "#8A2A25", "#A6322D", "#C23B35", "#D4605A", "#E08A85", "#EDB5B1", "#F8DCD9"]


def tubes_svg(w=560, h=300, id_prefix="cv"):
    labels = ["C", "D", "E", "F", "G", "A", "B", "C+"]
    tw = 52
    gap = (w - 8 * tw) / 9
    out = []
    for i, lab in enumerate(labels):
        th = h * TUBE_LEN[lab] - 40
        x = gap + i * (tw + gap)
        y = h - th - 10
        cn = COLOR_NAME[lab[0]]
        fill = NAME_HEX[cn]
        txt = TEXT_ON[cn]
        out.append(f'<g><rect x="{x:.1f}" y="{y:.1f}" width="{tw}" height="{th:.1f}" rx="9" fill="{fill}" stroke="#000" stroke-width="3"/>'
                   f'<rect x="{x:.1f}" y="{y:.1f}" width="{tw}" height="16" rx="8" fill="none" stroke="#000" stroke-width="3"/>'
                   f'<rect x="{x:.1f}" y="{y + th - 16:.1f}" width="{tw}" height="16" rx="8" fill="none" stroke="#000" stroke-width="3"/>'
                   f'<text x="{x + tw / 2:.1f}" y="{y + th / 2 + 12:.1f}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="34" fill="{txt}">{lab}</text></g>')
    return f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(out)}</svg>'


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.7in">{tubes_svg()}</div>'
            f'<div class="ctitle"><div class="a">COLOR-CODED PLAY-ALONGS</div><div class="b">TUBES &amp; BELLS</div>'
            f'<div class="c">Note charts and play-along strips for 5 public-domain carols · easy and full versions · parts for 2–3 groups</div></div>'
            f'<div class="cband">Grades 1–5 <em>·</em> 5 carols <em>·</em> {TOTAL_PAGES} pages</div></section>')


# ------------------------------------------------------------------ guide, key, own, terms
def guide_page(wm=False):
    rows = "".join(
        f'<tr><td><b>{escape(t["title"])}</b></td><td>{re.sub(r"&#x27;(.+?)&#x27;", "\u2018\\1\u2019", escape(t["comp"]))}, {t["year"]}</td><td>{t["meter"][0]}/{t["meter"][1]}</td>'
        f'<td>{" ".join(T.used_letters(t["bars"]))}</td><td>{t["tempo"][0]}–{t["tempo"][1]}</td>'
        f'<td>{tune_page_no(i, "easy")}–{tune_page_no(i, "parts")}</td></tr>' for i, t in enumerate(T.TUNES))
    wmh = '<div class="wm">PREVIEW</div>' if wm else ""
    return (f'<section class="page doc">{wmh}<div class="rule"><h1>Teacher Guide</h1>'
            f'<div class="l" style="font-size:13pt">{escape(TITLE)} · grades 1–5</div></div>'
            f'<div class="cols"><div>'
            f'<h2>What you need</h2><ul><li>One C-to-C set of 8 color-coded tuned percussion tubes, <b>or</b> 8 resonator bells, a color-coded xylophone, '
            f'metallophone or handbells (stick a matching color dot on each bar).</li>'
            f'<li>Each page uses only the white notes C D E F G A B and high C, so one set plays all five carols. No sharps or flats, so no extra tubes.</li></ul>'
            f'<h2>How to use a page</h2><ol>'
            f'<li><b>Look.</b> Match the colors on the staff and strip to the colors of your tubes. Every block also has its note letter, so the page works in black and white.</li>'
            f'<li><b>Say it.</b> Read the colors aloud in rhythm while tapping the beat (the small numbers under the strip).</li>'
            f'<li><b>Play it.</b> Tap tubes on a knee, palm or the floor, or strike bells and bars. Start slowly.</li>'
            f'<li><b>Build it.</b> Easy version first, then the full version, then the group parts.</li></ol>'
            f'<h2>Which version?</h2><ul><li><b>Easy</b> (grades 1–2): the first part of each carol with a simplified rhythm: only quarter, half and whole notes.</li>'
            f'<li><b>Full</b> (grades 3–5): the whole melody with eighths, dotted rhythms and (in one carol) sixteenth notes, shown on the staff and as blocks.</li>'
            f'<li><b>Parts</b> (all grades): a score for 2–3 groups. Each group owns some colors and plays only those blocks.</li></ul>'
            f'</div><div>'
            f'<h2>Groups of players</h2><p>Divide the class into 2 or 3 groups and give each group a share of the colors. The suggested split is printed on each parts page. '
            f'With 2 groups, join groups 2 and 3. If some students share a set, give each student two tubes so every child has a job.</p>'
            f'<h2>Tempo</h2><p>Start at the slower number and move up when the class can play without stopping. Numbers are beats (quarter notes) per minute. '
            f'Count in two full bars out loud.</p>'
            f'<h2>Extensions</h2><ul><li>One student conducts by pointing at the strip.</li><li>Play the melody on bells while others hold the beat on tubes.</li>'
            f'<li>Cover one group’s row and ask the class to play it from memory.</li><li>Use the blank strips on page {P_OWN} to write a short tune.</li></ul>'
            f'</div></div>'
            f'<h2>The five carols</h2><table><tr><th>Carol</th><th>Melody by</th><th>Meter</th><th>Colors used</th><th>BPM</th><th>Pages</th></tr>{rows}</table>'
            f'<p class="small">All tunes were first published in 1930 or earlier and are in the public domain. Melodies only: no lyrics and no modern arrangements. '
            f'Supports National Core Arts Standards for Music, Performing (MU:Pr4.2, reading and performing notation; MU:Pr6.1, performing with expression), at a modest grade 1–5 level.</p>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 2")}</section>')


def key_page(wm=False):
    wmh = '<div class="wm">PREVIEW</div>' if wm else ""
    letters = ["C", "D", "E", "F", "G", "A", "B", "C+"]
    # a mini staff with the scale, as colored notes
    scale = [T.Note(p, F(1), False) for p in ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]]
    scale_svg = (system_svg(dict(key="key", meter=(8, 4), pickup=F(0)), "key", 0, [0], [scale], 8.0, 34, with_staff=True, show_ts=False))
    tube_rows = "".join(
        f'<div style="flex:1;text-align:center"><div style="height:{int(56 * TUBE_LEN[L])}pt;background:{NAME_HEX[COLOR_NAME[L[0]]]};border:1.3pt solid #000;border-radius:6pt;'
        f'margin:0 3pt;display:flex;align-items:flex-end;justify-content:center;font-family:Oswald;font-weight:700;font-size:15pt;color:{TEXT_ON[COLOR_NAME[L[0]]]};padding-bottom:3pt">{L}</div>'
        f'<div class="l" style="font-size:9pt;margin-top:2pt;text-transform:uppercase;font-weight:500">{COLOR_NAME[L[0]]}</div></div>' for L in letters)
    return (f'<section class="page doc">{wmh}<div class="rule"><h1>Color Key</h1>'
            f'<div class="l" style="font-size:13pt">Tubes, bells and bars in color order · the notes on the staff</div></div>'
            f'<h2>Your set, C to high C</h2><div style="display:flex;align-items:flex-end;height:64pt;margin:4pt 0 2pt">{tube_rows}</div>'
            f'<p class="small">The longest tube is the lowest note. C+ is the short high C tube (red, like C). If your set has only the 8 diatonic tubes, you have everything you need.</p>'
            f'<h2>The same notes on the staff</h2>{scale_svg}'
            f'<p class="small">C is on the first ledger line below the staff, D is the space under the bottom line, E is the bottom line, F the first space, G the second line, '
            f'A the second space, B the middle line and high C the third space.</p>'
            f'<div class="cols"><div><h2>How to read a strip</h2><ul>'
            f'<li>One colored block = one note. The block’s letter tells you which note.</li>'
            f'<li>Block length = note length: a wide block is a long note.</li>'
            f'<li>Space with no block = silence. The small numbers are the beats.</li>'
            f'<li>On the parts pages each row is one group: play only your own row.</li></ul></div>'
            f'<div><h2>Bells and xylophones</h2><ul>'
            f'<li>Put a color dot or tape on each bar: C red, D orange, E yellow, F green, G turquoise, A blue, B purple, high C red.</li>'
            f'<li>Resonator bells and handbells: hand each child the colors for their part.</li>'
            f'<li>Notes sounding an octave higher or lower than written do not change the colors.</li></ul></div></div>'
            f'<div class="box"><b class="t">Trademark note</b><br><span class="small">{escape(TM_NOTE)}</span></div>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 3")}</section>')


def own_page():
    s = 6.6
    rows = []
    for r in range(4):
        parts = []
        W2 = W
        layout, per_beat = bar_layout([[T.Note("C4", F(1), False)] * 4] * 4)
        yb = 1.9 * s + 4 * s
        for i in range(5):
            y = yb - i * s
            parts.append(f'<line x1="{CLEF_X - 1}" y1="{y:.2f}" x2="{W - 1}" y2="{y:.2f}" stroke="#000" stroke-width="{0.16 * s:.2f}"/>')
        parts.append(g(CLEF_G, CLEF_X, yb - s, 4 * s))
        if r == 0:
            parts.append(g(TIMESIG0 + 4, CLEF_X + 2.9 * s + 3, yb - 3 * s, 4 * s))
            parts.append(g(TIMESIG0 + 4, CLEF_X + 2.9 * s + 3, yb - s, 4 * s))
        ys = yb + 3.6 * s + 4
        for bi, (x0, x1, blen) in enumerate(layout):
            parts.append(f'<line x1="{x1 - 1:.1f}" y1="{yb - 4 * s:.1f}" x2="{x1 - 1:.1f}" y2="{yb:.1f}" stroke="#000" stroke-width="1.1"/>')
            ux = x1 - x0 - 2 * PAD
            for k in range(4):
                bx = x0 + PAD + k * ux / 4
                parts.append(f'<rect x="{bx + 1:.1f}" y="{ys:.1f}" width="{ux / 4 - 2:.1f}" height="26" rx="3" fill="#fff" stroke="#000" stroke-width="1"/>'
                             f'<text x="{bx + 4:.1f}" y="{ys + 34:.1f}" font-family="Source Sans 3" font-size="6.5" fill="#666">{k + 1}</text>')
        rows.append(f'<svg viewBox="0 0 {W:.0f} {ys + 38:.1f}" width="{W:.0f}pt" height="{ys + 38:.1f}pt" style="display:block">{"".join(parts)}</svg>')
    return (f'<section class="page">'
            f'<div class="top"><div class="h t">Write Your Own<small>Compose a short tune with the colors, then teach it to a friend</small></div>'
            f'<div class="tag"><div class="lv">BLANK</div><div class="ln">4/4 · 16 beats a line</div></div></div>'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="how"><b>Make a play-along.</b> Write each note on the staff, then color a box under it. A long note can fill two or more boxes. '
            f'Write the letter in each box so it still works in black and white.</div>'
            f'{legend_html(["C", "D", "E", "F", "G", "A", "B"])}'
            f'<div class="sysbox">{"".join(rows)}</div>{foot(COPY, f"Page {P_OWN}")}</section>')


def terms_page():
    return (f'<section class="page doc"><div class="rule"><h1>Terms of Use</h1>'
            f'<div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. '
            f'Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. '
            f'If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>The music</h2><p>All five melodies are in the public domain (first published in 1930 or earlier). Each page shows the melody only, in C major: '
            f'no lyrics and no modern arrangements. Layouts and play-along strips are original work, {BRAND} by {STORE}.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<div class="box"><span class="small">{escape(TM_NOTE)}</span></div>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def full_pages():
    pages = [cover_page(), guide_page(), key_page()]
    for ti in range(N_TUNES):
        for ver in VERS:
            pages.append(tune_page(ti, ver))
    pages += [own_page(), terms_page()]
    return pages


def preview_pages():
    """4 real pages, watermark applied once each (inside the page, never again in the PNGs)."""
    return [key_page(True), tune_page(0, "easy", True), tune_page(3, "full", True), tune_page(2, "parts", True)]


PREVIEW_PAGE_NOS = [P_KEY, tune_page_no(0, "easy"), tune_page_no(3, "full"), tune_page_no(2, "parts")]


# ------------------------------------------------------------------ square images
SQ_CSS = """
.sq { width: 1000px; height: 1000px; position: relative; overflow: hidden; background: #fff; display: flex; flex-direction: column; align-items: center; }
.sq .store { font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; margin-top: 34px; }
.sq .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; }
.sq .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.sq .band { position: absolute; left: 0; right: 0; bottom: 0; height: 66px; background: #000; color: #fff; text-align: center; font-family: 'Oswald';
            font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; padding-top: 17px; }
.sq .band em { font-style: normal; color: ACCENT; }
.shot { background: #fff; border: 2px solid #000; box-shadow: 8px 8px 0 #000; position: relative; overflow: hidden; }
.shot img { display: block; width: 100%; }
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; text-align: center; margin-top: 16px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 18px; }
.card { box-sizing: border-box; border: 2px solid #000; border-radius: 6px; padding: 8px 10px 4px; background: #fff; }
.card .ct { font-family: 'Oswald'; font-weight: 700; font-size: 22px; text-transform: uppercase; line-height: 1.05; }
.card .cm { font-family: 'Oswald'; font-weight: 300; font-size: 16px; margin-bottom: 4px; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 70px">'
        f'<div style="width:760px">{tubes_svg()}</div>'
        f'<div><div class="hd" style="font-size:50px">Color-Coded Play-Alongs</div>'
        f'<div class="hd" style="font-size:118px">Tubes &amp; Bells</div>'
        f'<div class="sub" style="font-size:27px;margin-top:12px">5 public-domain carols · easy and full versions · group parts</div></div>'
        f'</div><div class="band">Grades 1–5 <em>·</em> 5 carols <em>·</em> {TOTAL_PAGES} pages</div></div>')


def preview_square_1(img):
    labs = [("Color key", "tubes, bells, staff"), ("Full version", "grades 3–5")]
    srcs = [img[0], img[2]]
    shots = "".join(
        f'<div style="width:440px"><div class="shot"><img src="{srcs[i]}"></div>'
        f'<div class="lbl">{labs[i][0]}<span>{labs[i][1]}</span></div></div>' for i in range(2))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:20px">Colors on the staff</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Colored notes and play-along blocks, side by side</div>'
        f'<div style="display:flex;flex:1;flex-direction:column;align-items:center;justify-content:center;width:100%;padding-bottom:66px;box-sizing:border-box"><div style="display:flex;gap:40px">{shots}</div></div>'
        f'<div class="band">Easy · full · group parts</div></div>')


def preview_square_2(img_a, img_b):
    pair = "".join(
        f'<div style="width:440px"><div class="shot"><img src="{src}"></div><div class="lbl">{lab}</div></div>'
        for src, lab in ((img_a, "Easy: first part of the carol"), (img_b, "Parts for 3 groups")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:20px">Split the class in 2–3 groups</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Each group plays only its own colors</div>'
        f'<div style="display:flex;flex:1;flex-direction:column;align-items:center;justify-content:center;width:100%;padding-bottom:66px;box-sizing:border-box"><div style="display:flex;gap:40px">{pair}</div></div>'
        f'<div class="band">Every carol has a parts page</div></div>')


def preview_square_3():
    cards = []
    for ti, t in enumerate(T.TUNES):
        bars = t["bars"]
        idxs = list(range(0, 3 if t["meter"][0] == 4 else (6 if t["meter"][0] == 2 else 4)))
        svg = system_svg(t, "card", 0, idxs, bars, 6.0, 24, with_staff=False, ruler=False, px=860)
        cards.append(f'<div class="card" style="width:900px"><div class="ct">{escape(t["title"])}</div>'
                     f'<div class="cm">{re.sub(r"&#x27;(.+?)&#x27;", "\u2018\\1\u2019", escape(t["comp"]))}, {t["year"]} · {t["meter"][0]}/{t["meter"][1]}</div>'
                     f'<div style="width:860px">{svg}</div></div>')
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:20px">5 carols, 20 pages</div>'
        f'<div style="display:flex;flex:1;flex-direction:column;align-items:center;justify-content:center;width:100%;padding-bottom:66px;box-sizing:border-box"><div style="display:flex;flex-wrap:wrap;gap:12px;width:900px;justify-content:center">{"".join(cards)}</div></div>'
        f'<div class="band">Grades 1–5 <em>·</em> {TOTAL_PAGES} pages</div></div>')


# ------------------------------------------------------------------ render
def node_env():
    env = dict(os.environ)
    if not env.get("NODE_PATH"):
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    return env


def render(jobs):
    path = os.path.join(BUILD, "jobs.json")
    with open(path, "w") as f:
        json.dump(jobs, f)
    subprocess.run(["node", RENDER_JS, path], check=True, env=node_env())


def write(name, text):
    p = os.path.join(BUILD, name)
    with open(p, "w") as f:
        f.write(text)
    return p


SQUARES = {}


def build_squares():
    sq = {"cover": cover_square(), "p1": preview_square_1(["pv2.png", "pv3.png", "pv4.png"]), "p2": preview_square_2("pv3.png", "pv5.png"), "p3": preview_square_3()}
    return sq


def build():
    os.makedirs(BUILD, exist_ok=True)
    errs = T.verify_tunes()
    if errs:
        print("\n".join(errs))
        sys.exit("melody check failed; not rendering")
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    # images of the real pages (the watermark is already on them: it is never added again)
    for i, no in enumerate(PREVIEW_PAGE_NOS, 1):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF, os.path.join(BUILD, f"pv{i}")], check=True)
    # pv1 key, pv2 easy, pv3 full, pv4 parts ; map names used above
    os.replace(os.path.join(BUILD, "pv4.png"), os.path.join(BUILD, "pv5.png"))      # parts -> pv5
    os.replace(os.path.join(BUILD, "pv3.png"), os.path.join(BUILD, "pv4.png"))      # full  -> pv4
    os.replace(os.path.join(BUILD, "pv2.png"), os.path.join(BUILD, "pv3.png"))      # easy  -> pv3
    os.replace(os.path.join(BUILD, "pv1.png"), os.path.join(BUILD, "pv2.png"))      # key   -> pv2
    sqh = build_squares()
    paths = {k: write(f"{k}.html", v) for k, v in sqh.items()}
    outs = {"cover": COVER_PNG, "p1": PREVIEW_PNGS[0], "p2": PREVIEW_PNGS[1], "p3": PREVIEW_PNGS[2]}
    render([{"html": paths[k], "png": outs[k], "width": 1000, "height": 1000, "scale": 2} for k in ("cover", "p1", "p2", "p3")])
    write_upload()
    write_tpt_json()
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


# ------------------------------------------------------------------ UPLOAD.md and tpt.json
LISTING_TITLE = "Color-Coded Play-Along Charts | Tuned Tubes, Bells & Xylophone Carols, Gr 1-5"
PREFERRED_TITLE = "Christmas Boomwhacker and Bells Play-Alongs | Color-Coded Charts, Gr 1-5"
PRICE = "4.50"


def page_list():
    """(label, pages) rows; the sum must equal TOTAL_PAGES."""
    rows = [("Cover", 1), ("Teacher guide: tubes, bells and xylophones, tempo, groups, extensions", 1), ("Color key: your set, the staff, how to read a strip", 1)]
    for ti, t in enumerate(T.TUNES):
        rows.append((f"{t['title']}: easy version, full version and parts for 3 groups", 3))
    rows += [("Write-your-own blank staves and color strips", 1), ("Terms of use and credits", 1)]
    return rows


def write_upload():
    rows = page_list()
    assert sum(n for _, n in rows) == TOTAL_PAGES
    bullets = "\n".join(f"• {lab} ({n} page{'s' if n != 1 else ''})" for lab, n in rows)
    srcs = "\n".join(f"- **{t['title']}** ({t['comp']}, {t['year']}): {t['src']}" for t in T.TUNES)
    plain_pages = "\n".join(f"- {lab}: {n}" for lab, n in rows)
    md = f"""# UPLOAD: Color-Coded Carol Play-Alongs for Tuned Tubes, Bells & Xylophone (TpT 044)

These fields follow the order of TpT's "Add a resource" form. Holiday item: list by **early to mid Nov 2026** (Christmas searches build through December).

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 x 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages (color key, easy, full, parts).

## 1. Title

```
{LISTING_TITLE}
```

Title notes: no Christmas/Holiday/Winter in the title (TpT's seasonal-title notice blocked it for 027). If TpT accepts a seasonal title, the preferred one is
`{PREFERRED_TITLE}`. "Boomwhackers" is a registered trademark (Whacky Music, Inc.), so the title uses generic wording ("tuned tubes") and the
description mentions Boomwhacker® compatibility once with a "not affiliated" note. (Many TpT listings do use the word in titles; this one stays on the safe side. Owner's call.)

## 2. Description

```
Color-coded play-along charts for Christmas carols: five public-domain carols written as colored notes on the staff AND as colored play-along blocks, so every child can play along on tuned tubes, resonator bells, xylophones or handbells. Each carol comes in an EASY version (grades 1-2), a FULL version (grades 3-5) and a PARTS page that splits the tune between 2-3 groups of players.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
{bullets}

THE FIVE CAROLS (melody only, C major, white notes only)
• Jingle Bells (Pierpont, 1857)
• Deck the Halls (Welsh air "Nos Galan")
• Up on the Housetop (Hanby, 1864)
• Joy to the World (arr. Lowell Mason, 1839, adapted from Handel)
• Away in a Manger (Kirkpatrick, "Cradle Song", 1895)

HOW IT WORKS
Match the color of each note or block to your tube, bell or bar. The standard color scheme is used (C red, D orange, E yellow, F green, G turquoise, A blue, B purple, high C red), and every block also shows its note letter, so the pages work in black and white. Short blocks are short notes, long blocks are long notes, and small beat numbers under each strip help students count. Perfect for general music, music centers, December concerts and sub plans.

• Works with any C-to-C set of 8 color-coded tuned percussion tubes (Boomwhacker® compatible), resonator bells, color-coded xylophones and handbells
• Grades 1-5: simplified rhythm for younger students, the real rhythm for older ones
• No sharps or flats: one 8-note set plays all five carols
• No lyrics and no modern arrangements: public-domain melodies only

Boomwhackers® is a registered trademark of Whacky Music, Inc. This resource is not affiliated with, sponsored or endorsed by Whacky Music, Inc.

{DISCLOSURE}
```

## 3. Grades

1, 2, 3, 4 (TpT allows four; the description says grades 1-5).

## 4. Subjects, tags, resource type

- Subjects: Music, Instrumental Music (both are real entries, not headings).
- Tags: Christmas-Chanukah-Kwanzaa, Winter, Activities, Centers, Printables, Songs (all exact entries from `tpt/TAG-OPTIONS.json`, none are headings).
- Resource type: Activities, Printables.

## 5. Standards (optional)

National Core Arts Standards, Music: MU:Pr4.2 (reading and performing notation), MU:Pr6.1 (performing), grades 1-5.

## 6. Price

**${PRICE}** (paid; queue price).

## 7. Preview

Paid. Preview PDF: color key page, Jingle Bells easy, Joy to the World full, Up on the Housetop parts. Watermark applied once per page.

## 8. Page count (the PDF has {TOTAL_PAGES} pages, listed here exactly)

{plain_pages}
- Total: {TOTAL_PAGES}

## 9. Copyright and tune verification (internal; QA reads this)

**"We Wish You a Merry Christmas" was NOT used.** The familiar arrangement (Arthur Warrell, 1935) is not public domain in the US, so the queue line's fifth carol was
replaced by **Joy to the World** (arr. Mason 1839, adapted from Handel) and, because one tune could not be proven (below), **Jolly Old Saint Nicholas** was replaced by **Away in a Manger** (Kirkpatrick 1895).
Both are pre-1930 and verified in the table below. Melodies only; no lyrics anywhere in the PDF.

{srcs}

How each melody was checked (every tune is stored twice in `tunes.py` and `gen.py --check` fails if the two do not agree note for note, pitch and length):
- **Jingle Bells**: (A) top voice of Wikimedia Commons `Jingle_Bells_refrain_vector.mid` (G major, transposed down a fifth by code); (B) letter transcription of the chorus at piano-keyboard-guide.com (same notes). Agree on all 16 bars. Date/composer: Pierpont, "One Horse Open Sleigh", Boston, Oliver Ditson, 1857 (Wikipedia and a university sheet-music exhibit).
- **Deck the Halls**: (A) melody track of Wikimedia Commons `Deck_the_Halls.mid` (D major, transposed down a step by code); (B) piano-keyboard-guide.com letter lines. Agree on all 16 bars. Melody Welsh "Nos Galan", first printed 1794 (Edward Jones), older in tradition; English words (Oliphant 1862) are not used.
- **Up on the Housetop**: Hanby, 1864 (Wikipedia; the IMSLP page holds a 2010 CC BY 3.0 arrangement by R. A. Hudson; the melody itself is Hanby 1864, and no arrangement is reproduced here). (A) typed in C; (B) read from the IMSLP part "Violin 1" (E-flat major, transposed down a minor third by code). The two encodings agree, and the pitch set (C D E F G A) matches the set on musicplayonline.com. **Weakest source: the notes come from one scanned part; a second independent score would be better.**
- **Joy to the World**: (A) typed in C; (B) the LilyPond score on Wikipedia (Mason, The Modern Psalmist, 1839, p. 144; D major, 2/4), parsed and transposed down a step by code. Agree on all 20 bars. The score's "repeat unfold" block is read as an exact repeat (LilyPond relative-octave rules would drop the second pass an octave, which is an engraving artefact). Tune "Antioch", Mason 1839, "from Handel" (attribution doubtful, irrelevant: both dates are far before 1930).
- **Away in a Manger** ("Cradle Song"): Kirkpatrick, "Around the World with Christmas", Cincinnati, 1895 (Wikipedia). (A) typed in C; (B) the LilyPond score on Wikipedia (F major, 3/4, one-beat pickup), parsed and transposed down a fourth by code. Agree on all 17 bars.
- **Jolly Old Saint Nicholas was dropped**: the notes (A A A A G G G ... in F) were readable from a glockenspiel chart, but its rhythm was inconsistent (tied 16ths) and no second source could be opened, so the rule "music must be right" was not met. Melody is by James R. Murray (1874) per Wikipedia; could be added later once a clean score is found.

Rhythm of the "easy" versions: every note shorter than a beat is merged into the note that starts on the beat (two eighths become a quarter on the first pitch; dotted quarter + eighth becomes a half). `--check` recomputes this with a second method.

## 10. Before you click publish

- [ ] Title accepted by the form (the seasonal block). Try `{PREFERRED_TITLE}` first only if you want the Christmas keyword.
- [ ] Open question for the owner: keep "Boomwhacker" out of the title (current), or use it as many TpT sellers do?
"""
    open(UPLOAD, "w").write(md)


def write_tpt_json():
    cfg = {
        "price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
        "grades": ["1st-grade", "2nd-grade", "3rd-grade", "4th-grade"],
        "subjects": ["Music", "Instrumental Music"],
        "tags": ["Christmas-Chanukah-Kwanzaa", "Winter", "Activities", "Centers", "Printables", "Songs"],
        "formats": ["PDF"], "pages": TOTAL_PAGES,
        "files": {"product": os.path.basename(PDF), "preview": os.path.basename(PREVIEW_PDF), "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }
    with open(TPT_JSON, "w") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")


# ------------------------------------------------------------------ checks
# Independent tables for --check (not shared with the drawing code): semitone -> colour hex, semitone -> steps above E4.
CHECK_HEX = {0: "#E3262E", 2: "#F58A1F", 4: "#FFE21F", 5: "#3FAE49", 7: "#12A8CE", 9: "#2F5FBF", 11: "#8B4CB0"}
CHECK_STEP_NAMES = {0: 0, 2: 1, 4: 2, 5: 3, 7: 4, 9: 5, 11: 6}


def midi_of(pitch):
    pc = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[pitch[0]]
    return (int(pitch[1:]) + 1) * 12 + pc


def attr(tag, name):
    m = re.search(name + r'="([^"]*)"', tag)
    return m.group(1) if m else None


def read_systems(html):
    """Parse every rendered system: its notes (class nt) and blocks (class blk) back into python values."""
    systems = []
    for m in re.finditer(r'<svg class="sys"([^>]*)>(.*?)</svg>', html, re.S):
        head, body = m.group(1), m.group(2)
        notes = [dict(tag=t) for t in re.findall(r'<g class="nt"[^>]*>', body)]
        blks = re.findall(r'<g class="blk"[^>]*>', body)
        systems.append(dict(tune=attr(head, "data-tune"), ver=attr(head, "data-ver"), s=float(attr(head, "data-s")), yb=float(attr(head, "data-yb")),
                            meter=attr(head, "data-meter"), notes=[n["tag"] for n in notes], blks=blks))
    return systems


def expected_bars(tune, ver):
    if ver == "easy":
        a, b = tune["easy"]
        # second method for the simplification: sum durations of the notes that start between consecutive beat-starting notes
        out = []
        for bar in tune["bars"][a:b]:
            t, starts = F(0), []
            for n in bar:
                starts.append(t)
                t += n.dur
            keep = [i for i, st in enumerate(starts) if st.denominator == 1]
            nb = []
            for j, i in enumerate(keep):
                end = (starts[keep[j + 1]] if j + 1 < len(keep) else t)
                nb.append((bar[i].pitch, end - starts[i]))
            out.append(nb)
        return out
    return [[(n.pitch, n.dur) for n in bar] for bar in tune["bars"]]


def verify_render(html):
    errs = []
    systems = read_systems(html)
    n_nt = n_blk = 0
    seen = {}   # (tune, ver) -> list of (bar, pitch, dur)
    for sy in systems:
        s, yb = sy["s"], sy["yb"]
        if sy["tune"] in ("key", "card"):
            continue
        per_bar = {}
        for tag in sy["notes"]:
            n_nt += 1
            pitch, dur = attr(tag, "data-pitch"), F(attr(tag, "data-dur"))
            cy, fill, bar = float(attr(tag, "data-cy")), attr(tag, "data-fill"), attr(tag, "data-bar")
            m = midi_of(pitch)
            want_fill = CHECK_HEX[m % 12]
            if fill != want_fill:
                errs.append(f"{sy['tune']} {sy['ver']} bar {bar} {pitch}: fill {fill}, expected {want_fill}")
            steps = 7 * (m // 12) + CHECK_STEP_NAMES[m % 12] - (7 * 5 + CHECK_STEP_NAMES[4])
            want_y = yb - steps * s / 2
            if abs(cy - want_y) > 0.02:
                errs.append(f"{sy['tune']} {sy['ver']} bar {bar} {pitch}: staff y {cy}, expected {want_y:.2f}")
            per_bar.setdefault(bar, []).append((pitch, dur, float(attr(tag, "data-cx"))))
            seen.setdefault((sy["tune"], sy["ver"]), []).append((int(bar), pitch, dur))
            # heads must not collide
        for bar, row in per_bar.items():
            for (p1, d1, x1), (p2, d2, x2) in zip(row, row[1:]):
                if x2 - x1 < 1.18 * s + 0.3:
                    errs.append(f"{sy['tune']} {sy['ver']} bar {bar}: {p1} and {p2} heads overlap (gap {x2 - x1:.1f}pt)")
        blk_seen = {}
        for tag in sy["blks"]:
            n_blk += 1
            pitch, dur, bar, row = attr(tag, "data-pitch"), F(attr(tag, "data-dur")), attr(tag, "data-bar"), attr(tag, "data-row")
            if float(attr(tag, "data-w")) < 8.0:
                errs.append(f"{sy['tune']} {sy['ver']} bar {bar} {pitch}: strip block only {attr(tag, 'data-w')}pt wide")
            blk_seen.setdefault((bar, row), []).append((pitch, dur))
        sy["blk_seen"] = blk_seen
    # compare notes read back with the transcription (second encodings, recomputed here)
    for t in T.TUNES:
        sec = t["second"]()
        sec_bars = [[(n.pitch, n.dur) for n in bar] for bar in sec]
        for ver in ("easy", "full"):
            rows = sorted(seen.get((t["key"], ver), []), key=lambda r: r[0])
            want = expected_bars({**t, "bars": sec}, ver)
            a, b = (t["easy"] if ver == "easy" else (0, len(sec)))
            first_no = 0 if t["pickup"] else 1
            got = {}
            for no, p, d in seen.get((t["key"], ver), []):
                got.setdefault(no, []).append((p, d))
            want_by_no = {first_no + a + i: bar for i, bar in enumerate(want)}
            if got != want_by_no:
                errs.append(f"{t['key']} {ver}: rendered staff notes differ from the transcription")
            # bar sums (meter and durations) from the RENDERED durations
            L = F(t["meter"][0] * 4, t["meter"][1])
            for no, bar in got.items():
                tot = sum(d for _, d in bar)
                exp = t["pickup"] if (no == 0 and t["pickup"]) else (L - t["pickup"] if (t["pickup"] and no == len(t["bars"]) - 1 and ver == "full") else L)
                if ver == "easy" and no == 0 and t["pickup"]:
                    exp = t["pickup"]
                if tot != exp:
                    errs.append(f"{t['key']} {ver} bar {no}: rendered durations add to {tot}, meter/pickup requires {exp}")
        # strips: full-colour strips equal the staff notes; parts rows partition the notes
        blk_full, blk_parts = {}, {}
        for sy in systems:
            if sy["tune"] != t["key"]:
                continue
            for (bar, row), items in sy.get("blk_seen", {}).items():
                if sy["ver"] == "full":
                    blk_full.setdefault(int(bar), []).extend(items)
                elif sy["ver"] == "parts":
                    blk_parts.setdefault(int(bar), []).append((int(row), items))
        first_no = 0 if t["pickup"] else 1
        for i, bar in enumerate(sec_bars):
            no = first_no + i
            if blk_full.get(no) != bar:
                errs.append(f"{t['key']} full strip bar {no} differs from the notes")
            parts = blk_parts.get(no, [])
            groups_letters = t["groups"]
            merged = []
            for row, items in parts:
                for p, d in items:
                    if p[0] not in groups_letters[row]:
                        errs.append(f"{t['key']} parts bar {no}: {p} in the wrong group row {row + 1}")
                    merged.append((p, d))
            if sorted(merged, key=lambda x: (x[0], x[1])) != sorted(bar, key=lambda x: (x[0], x[1])):
                errs.append(f"{t['key']} parts bar {no}: the group rows together do not equal the full bar")
    return errs, n_nt, n_blk


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    rows = []
    for line in out:
        parts = line.split()
        rows.append((parts[0], parts[-5]))
    return rows


SQUARE_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of process.argv.slice(2)) {
    const page = await browser.newPage({ viewport: { width: 1000, height: 1000 } });
    await page.goto(url.pathToFileURL(require('path').join(process.env.BUILD_DIR, name + '.html')).href);
    await page.evaluate(() => document.fonts.ready);
    out[name] = await page.evaluate(() => {
      const band = document.querySelector('.band').getBoundingClientRect();
      const bad = [];
      for (const el of document.querySelectorAll('.sq *')) {
        if (el.closest('.band')) continue;
        if (el.tagName === 'DIV' && el.children.length > 0 && !el.classList.contains('shot') && !el.classList.contains('card')) continue;
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        if (r.bottom > band.top + 0.5) bad.push(el.tagName + '.' + el.className + ' bottom=' + r.bottom.toFixed(0) + ' band=' + band.top.toFixed(0));
        if (r.right > 1001 || r.left < -1) bad.push('outside ' + el.tagName + ' ' + r.left.toFixed(0) + ',' + r.right.toFixed(0));
      }
      return { bad: bad.slice(0, 5), wm: document.querySelectorAll('.swm, .wm').length };
    });
    await page.close();
  }
  console.log(JSON.stringify(out));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def verify_squares():
    """Open each square image's HTML in Chromium and check nothing sits behind the band or runs past the frame."""
    errs = []
    js = write("check_squares.js", SQUARE_JS)
    env = node_env()
    env["BUILD_DIR"] = BUILD
    r = subprocess.run(["node", js, "cover", "p1", "p2", "p3"], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        return [f"square layout check could not run: {r.stderr[-300:]}"]
    res = json.loads(r.stdout.strip().splitlines()[-1])
    for name, v in res.items():
        if v["bad"]:
            errs.append(f"{name}.png: content under the band or outside the frame: {v['bad']}")
        if v["wm"]:
            errs.append(f"{name}.png: adds its own watermark (the page images already carry one)")
    return errs


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))


def verify_files():
    errs = []
    from pypdf import PdfReader
    from PIL import Image
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want_pages in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want_pages:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want_pages}")
        for i, pg in enumerate(rd.pages):
            w, h = float(pg.mediabox.width), float(pg.mediabox.height)
            if abs(w - 612) > 1 or abs(h - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: {w:.0f}x{h:.0f}pt, not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
        names = " ".join(n for n, _ in fonts).lower().replace(" ", "")
        for fam in ("bravura", "oswald", "sourcesans3"):
            if fam not in names:
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    rd = PdfReader(PDF)
    for i, pg in enumerate(rd.pages):
        t = pg.extract_text() or ""
        if len(t.strip()) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t:
            errs.append(f"PDF page {i + 1}: contains the PREVIEW watermark")
    # each full-PDF page heading
    for ti, t in enumerate(T.TUNES):
        for ver in VERS:
            txt = rd.pages[tune_page_no(ti, ver) - 1].extract_text().upper().replace("\n", " ")
            if t["title"].upper() not in txt or INFO[ver][0] not in txt:
                errs.append(f"PDF page {tune_page_no(ti, ver)}: heading for {t['title']} {ver} missing")
    cover_txt = rd.pages[0].extract_text()
    if f"{TOTAL_PAGES} PAGES" not in cover_txt.upper():
        errs.append("cover page badge does not state the PDF page count")
    prd = PdfReader(PREVIEW_PDF)
    for i, pg in enumerate(prd.pages):
        c = (pg.extract_text() or "").count("PREVIEW")
        if c != 1:
            errs.append(f"preview PDF page {i + 1}: watermark appears {c} times (must be exactly once)")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
    cov_html = open(os.path.join(BUILD, "cover.html")).read()
    if f"{TOTAL_PAGES} pages" not in cov_html:
        errs.append("cover.png badge does not state the PDF page count")
    for k in ("p1", "p2", "p3"):
        if "swm" in open(os.path.join(BUILD, f"{k}.html")).read().split("</style>")[1]:
            errs.append(f"{k}.html adds a second watermark")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80:
            errs.append(f"UPLOAD.md: title is {len(title)} chars (max 80)")
        if re.search(r"christmas|holiday|winter|boomwhacker", title, re.I):
            errs.append("UPLOAD.md: title has a seasonal or trademark word")
    for need in (DISCLOSURE, "$4.50", f"{TOTAL_PAGES} pages", "We Wish You a Merry Christmas", "Warrell", "Whacky Music"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    pm = re.search(r"## 8\. Page count.*?\n((?:- .*\n)+)", up, re.S)
    nums = [int(x) for x in re.findall(r": (\d+)\n", pm.group(1))] if pm else []
    tot = re.search(r"- Total: (\d+)", up)
    if not pm or not tot or sum(nums[:-1]) != TOTAL_PAGES or int(tot.group(1)) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md: page list does not total {TOTAL_PAGES}")
    if "checked by hand" in up.lower() or "handmade" in up.lower():
        errs.append("UPLOAD.md: says hand-checked/handmade")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if tj["pages"] != TOTAL_PAGES:
        errs.append(f"tpt.json pages {tj['pages']} != {TOTAL_PAGES}")
    if tj["price"] != PRICE:
        errs.append("tpt.json price mismatch")
    if not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json grades must be 1-4")
    if any(t not in tags for t in tj["tags"]) or any(s not in subs for s in tj["subjects"]):
        errs.append("tpt.json tag or subject not an exact option")
    return errs


def check():
    errs = T.verify_tunes()
    html_path = os.path.join(BUILD, "resource.html")
    if not os.path.exists(html_path):
        sys.exit("run gen.py first")
    html = open(html_path).read()
    e2, n_nt, n_blk = verify_render(html)
    errs += e2
    errs += verify_files()
    errs += verify_squares()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:60]))
        sys.exit(1)
    nbars = sum(len(t["bars"]) for t in T.TUNES)
    nnotes = sum(len(b) for t in T.TUNES for b in t["bars"])
    print(f"CHECK OK: {len(T.TUNES)} carols, {nbars} bars, {nnotes} notes; each melody matches its second transcription and (Jingle Bells, Deck the Halls) a letter source; "
          f"{n_nt} rendered notes: color recomputed from pitch, staff height recomputed from pitch, every bar adds up to its meter; {n_blk} strip blocks match the staff; "
          f"parts rows partition every bar; easy versions recomputed; no overlapping heads; PDF {TOTAL_PAGES} Letter pages, preview 4 with one watermark each, fonts embedded; "
          f"images 2000x2000, nothing behind the bands; UPLOAD.md page list and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
