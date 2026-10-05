#!/usr/bin/env python3
"""Fall Rhythm Flashcards & Tracing (TpT 002): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, tpt.json) into this folder
    python3 gen.py --check   verify rhythms, answer keys, pages, fonts and files

Every card, tracing row and worksheet is drawn from the token data in
rhythm.py (q = quarter note, e = two beamed eighths, r = quarter rest,
h = half note). Pattern cards must add up to 4 beats; worksheet answer keys
are computed from the same patterns that are printed on the worksheets.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) through the shared
../tools/render.js, with the OFL fonts in ../fonts embedded as subsets.
"""
import json
import os
import re
import subprocess
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import rhythm as R  # noqa: E402
from art import art  # noqa: E402

TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "fall-rhythm-flashcards"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"      # copyright holder
BRAND = "Hudson Beat"      # store line on covers and previews (owner, 4 Oct)
YEAR = 2026
ACCENT = "#C4541B"         # this product's single accent (fall rust)
TITLE = "Fall Rhythm Flashcards"
PRICE = "4.00"

SYMBOLS = ["q", "e", "r", "h"]   # order used on cards and tracing pages

# 12 four-beat pattern cards in three sets; each set adds one symbol.
SETS = {
    "A": {"label": "Set A", "adds": "quarter notes & eighth notes", "patterns": ["qqeq", "eeqq", "qeeq", "eqee"]},
    "B": {"label": "Set B", "adds": "adds the quarter rest", "patterns": ["qqqr", "eeqr", "qreq", "erqe"]},
    "C": {"label": "Set C", "adds": "adds the half note", "patterns": ["qqh", "eeh", "hqr", "erh"]},
}
PATTERNS = [(k, p) for k, v in SETS.items() for p in v["patterns"]]

# Beat-count worksheets: printed items and (computed) answers.
WS = [
    {"id": 1, "title": "How Many Beats?", "kind": "single", "items": ["q", "h", "e", "r", "h", "q", "r", "e"],
     "how": "Look at each note or rest. Write how many beats it gets in the box."},
    {"id": 2, "title": "Count the Beats", "kind": "count", "items": ["qe", "hq", "qqrq", "eee", "hh", "rq"],
     "how": "Tap and count each pattern. Write the total number of beats in the box."},
    {"id": 3, "title": "Four Beats or Not?", "kind": "yesno", "items": ["qqh", "eqq", "hee", "qrqrq", "eeee", "hr"],
     "how": "Count the beats in each stick-notation pattern. Circle YES if it has exactly 4 beats, or NO if it does not."},
]


def answers(ws):
    if ws["kind"] == "yesno":
        return ["YES" if R.beats(p) == 4 else "NO" for p in ws["items"]]
    return [R.beats(p) for p in ws["items"]]


def sym_name(t):
    return R.TOKENS[t]["name"]


def beats_text(t):
    b = R.TOKENS[t]["beats"]
    return f"{b} beat" + ("s" if b != 1 else "")


# ---------------------------------------------------------------- html scaffolding
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
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 18pt; font-size: 12pt; margin: 9pt 0 5pt; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.d { flex: 0 0 1.6in; }
.how { font-size: 12.5pt; margin: 3pt 0 6pt; }
.how b { font-weight: 700; }
.body { flex: 1; display: flex; align-items: center; justify-content: center; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
/* text pages */
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 12pt 0 4pt; letter-spacing: .02em; }
.doc h2 .acc { color: ACCENT; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.34; margin: 0 0 4pt; }
.doc ul { margin: 0 0 4pt; padding-left: 15pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 6pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; font-size: 10.5pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 4pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10pt; background: #000; color: #fff; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; }
.small { font-size: 9pt !important; color: #333; }
.ref td { text-align: center; }
.ref td.n { text-align: left; }
.ref .big { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; }
/* cover page (letter) */
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; font-size: 80pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(right):
    return f'<div class="foot"><span>{COPY}</span><span>{right}</span></div>'


def top(sub, tag, tagsub, ak=False, title=TITLE):
    return (f'<div class="top"><div class="h t">{escape(title)}<small>{sub}</small></div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagsub}</div></div></div>')


NAME = '<div class="name">Name<span></span>Date<span class="d"></span></div>'


def wm(on):
    return '<div class="wm">PREVIEW</div>' if on else ""


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}" style="display:block">{body}</svg>'


def text(x, y, s, size, weight=700, family="Oswald", anchor="middle", fill="#000", upper=False, extra=""):
    t = escape(s.upper() if upper else s)
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-weight="{weight}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}" {extra}>{t}</text>')


def pill(x, y, label, size=11, fill="#000", anchor="start"):
    w = len(label) * size * 0.56 + 14
    x0 = x if anchor == "start" else x - w
    return (f'<rect x="{x0:.1f}" y="{y:.1f}" width="{w:.1f}" height="{size + 9:.1f}" rx="4" fill="{fill}"/>'
            + text(x0 + w / 2, y + size + 3.2, label, size, 500, extra='letter-spacing="0.06em"', fill="#fff", upper=True))


# ---------------------------------------------------------------- flashcards
CARD_AREA = (540, 646)


def cut_grid(cols, rows, w, h):
    W, H = CARD_AREA
    out = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="#666" stroke-width="0.8" stroke-dasharray="6 4"/>']
    for c in range(1, cols):
        out.append(f'<line x1="{c * w}" y1="0" x2="{c * w}" y2="{H}" stroke="#666" stroke-width="0.8" stroke-dasharray="6 4"/>')
    for r in range(1, rows):
        out.append(f'<line x1="0" y1="{r * h}" x2="{W}" y2="{r * h}" stroke="#666" stroke-width="0.8" stroke-dasharray="6 4"/>')
    return "".join(out)


def card_frame(x, y, w, h):
    return f'<rect x="{x + 9}" y="{y + 9}" width="{w - 18}" height="{h - 18}" rx="14" fill="#fff" stroke="#000" stroke-width="2"/>'


def symbol_card(t, x, y, w, h, stick=False):
    info = R.TOKENS[t]
    out = [card_frame(x, y, w, h), art(info["art"], x + 20, y + 20, 46)]
    out.append(pill(x + w - 20, y + 22, beats_text(t), 12, anchor="end"))
    out.append(text(x + w / 2, y + 86, "stick notation" if stick else "standard notation", 11, 300))
    s = 25
    cy = y + h * 0.47
    if stick:
        yb = cy + 1.75 * s
        out.append(R.hand(t, x + w / 2, yb, s, heads=False, mode="solid"))
    else:
        yl = cy if t == "r" else cy + 1.5 * s
        out.append(R.engraved(t, x + w / 2, yl, s))
    out.append(text(x + w / 2, y + h - 64, info["name"], 21, 700, upper=True, extra='letter-spacing="0.02em"'))
    extra = {"q": "1 sound", "e": "2 sounds in 1 beat", "r": "1 silent beat", "h": "1 sound held for 2 beats"}[t]
    out.append(text(x + w / 2, y + h - 47, extra, 11.5, 400, "Source Sans 3"))
    out.append(text(x + w / 2, y + h - 30, f"Kodály syllable (optional): {info['kodaly']}", 9.5, 400, "Source Sans 3", fill="#333"))
    return "".join(out)


def pattern_card(n, setk, pattern, x, y, w, h, stick=False):
    out = [card_frame(x, y, w, h)]
    out.append(pill(x + 24, y + 24, f"Pattern {n}", 13))
    out.append(text(x + 24, y + 62, f'{SETS[setk]["label"]} · {SETS[setk]["adds"]}', 11, 300, anchor="start"))
    out.append(art(R.TOKENS[pattern[-1]]["art"] if n % 2 else "leaf", x + w - 70, y + 20, 48))
    s, W = 21, 98
    if stick:
        x0 = x + (w - 4 * W) / 2
        yb = y + 200
        body, centres, _ = R.stick_pattern(pattern, x0, yb, s, W)
        lead = yb
    else:
        tot = 2.6 * s + 4 * W + 1.2 * s + 0.5 * s
        x0 = x + (w - tot) / 2
        yl = y + 172
        body, centres, _ = R.engraved_pattern(pattern, x0, yl, s, W)
        lead = yl + 2 * s
    out.append(body)
    for i, cx in enumerate(centres):
        out.append(art("leaf", cx - 15, lead + 20, 30, 1.3))
        out.append(text(cx, lead + 66, str(i + 1), 12, 500))
    out.append(text(x + w / 2, y + h - 22, "stick notation" if stick else "standard notation · 4/4", 10, 300))
    return "".join(out)


def card_page(sub, tagsub, body, page_no, watermark=False):
    return (f'<section class="page">{wm(watermark)}{top(sub, "CARDS", tagsub)}'
            f'<div class="how" style="margin-top:7pt">Print on cardstock, then cut on the dashed lines. '
            f'<span class="small">Tip: laminate for years of use.</span></div>'
            f'<div class="body">{svg(*CARD_AREA, body)}</div>{foot(f"Page {page_no}")}</section>')


def symbol_cards_page(stick, page_no, watermark=False):
    w, h = CARD_AREA[0] / 2, CARD_AREA[1] / 2
    body = cut_grid(2, 2, w, h)
    for i, t in enumerate(SYMBOLS):
        body += symbol_card(t, (i % 2) * w, (i // 2) * h, w, h, stick)
    kind = "stick notation" if stick else "standard notation"
    return card_page(f"Symbol cards · {kind}", kind.capitalize(), body, page_no, watermark)


def pattern_cards_page(idx, stick, page_no, watermark=False):
    w, h = CARD_AREA[0], CARD_AREA[1] / 2
    body = cut_grid(1, 2, w, h)
    for j in range(2):
        n = idx * 2 + j + 1
        setk, p = PATTERNS[n - 1]
        body += pattern_card(n, setk, p, 0, j * h, w, h, stick)
    kind = "stick notation" if stick else "standard notation"
    return card_page(f"4-beat pattern cards {idx * 2 + 1}–{idx * 2 + 2} · {kind}", kind.capitalize(), body, page_no, watermark)


# ---------------------------------------------------------------- tracing
TR_W = 540


def guide(x1, x2, y):
    return f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="#999" stroke-width="0.8"/>'


def row_label(y, label):
    return text(0, y, label, 12, 700, anchor="start", upper=True, extra='letter-spacing="0.08em"')


def tracing_row(t, y, h, n, s, boxes=False):
    """A row of n symbols (dotted) or n empty boxes, centred vertically in [y, y + h]."""
    out = []
    cy = y + h / 2
    base = cy if t == "r" else cy + 1.5 * s
    step = TR_W / n
    if boxes:
        for i in range(n):
            bx = i * step
            out.append(f'<rect x="{bx + 3:.1f}" y="{y:.1f}" width="{step - 6:.1f}" height="{h:.1f}" rx="10" fill="none" stroke="#000" stroke-width="1.2"/>')
            out.append(guide(bx + 14, bx + step - 14, base))
    else:
        out.append(guide(0, TR_W, base))
        for i in range(n):
            out.append(R.hand(t, (i + 0.5) * step, base, s, heads=True, mode="dotted", accent=ACCENT))
    return "".join(out)


def tracing_page(t, num, page_no, watermark=False):
    info = R.TOKENS[t]
    out = []
    # LOOK panel
    out.append(f'<rect x="1" y="1" width="{TR_W - 2}" height="118" rx="12" fill="none" stroke="#000" stroke-width="1.6"/>')
    s = 20
    out.append(R.hand(t, 72, 60 if t == "r" else 90, s, heads=True, mode="solid"))
    out.append(text(140, 34, info["name"], 22, 700, anchor="start", upper=True))
    out.append(text(140, 55, f"{beats_text(t)} · " + {"q": "1 sound", "e": "2 sounds in 1 beat", "r": "silent: no sound",
                                                       "h": "1 sound held for 2 beats"}[t], 13, 400, "Source Sans 3", anchor="start"))
    out.append(text(140, 73, f"Kodály syllable (optional): {info['kodaly']}", 10.5, 400, "Source Sans 3", anchor="start", fill="#333"))
    steps = {"q": ("Draw an oval notehead and color it in.", "Add a stem going up on the right."),
             "e": ("Draw two noteheads and color them in. Add stems up", "on the right, then a thick beam joining the stems."),
             "r": ("Zig, zag, zig, then curl:", "like a Z with a little c at the bottom."),
             "h": ("Draw an open (empty) oval notehead.", "Add a stem going up on the right.")}[t]
    out.append(text(140, 93, steps[0], 11, 400, "Source Sans 3", anchor="start"))
    out.append(text(140, 107, steps[1], 11, 400, "Source Sans 3", anchor="start"))
    out.append(text(TR_W - 52, 22, "stick notation", 9.5, 300))
    out.append(R.hand(t, TR_W - 52, 100 if t != "r" else 84, 15, heads=False, mode="solid"))
    y = 134
    out.append(row_label(y + 12, "1 · Trace"))
    out.append(tracing_row(t, y + 18, 106, 4, 24))
    y += 132
    out.append(row_label(y + 12, "2 · Trace again"))
    out.append(tracing_row(t, y + 18, 78, 5, 17))
    y += 104
    out.append(row_label(y + 12, "3 · Your turn: draw your own"))
    out.append(tracing_row(t, y + 20, 110, 4, 24, boxes=True))
    y += 140
    out.append(text(TR_W / 2, y + 12, "All done? Color the pictures!", 12, 500, upper=True, extra='letter-spacing="0.06em"'))
    for i, n in enumerate(["maple", "acorn", info["art"] if info["art"] not in ("maple", "acorn") else "owl", "leaf"]):
        out.append(art(n, 90 + i * 100, y + 20, 48, 1.4))
    H = y + 72
    body = svg(TR_W, H, "".join(out))
    sub = f"Tracing {num} · " + info["name"].capitalize()
    return (f'<section class="page">{wm(watermark)}{top(sub, "TRACING", f"{num} of 5")}'
            f'{NAME}<div class="how"><b>Trace</b> the dotted lines. Start at the big dots. <b>Color in</b> any gray noteheads. Then <b>draw your own</b> in the boxes.</div>'
            f'<div class="body">{body}</div>{foot(f"Page {page_no}")}</section>')


TRACE_PATTERNS = ["qqeq", "eerq", "qqh"]


def tracing_patterns_page(page_no, watermark=False):
    out = []
    s, W = 17, 120
    y = 0
    for i, p in enumerate(TRACE_PATTERNS):
        out.append(row_label(y + 12, f"Pattern {i + 1} · trace it, then clap it"))
        base = y + 92
        out.append(guide(30, TR_W - 30, base))
        out.append(R.hand_pattern(p, 30, base, s, W, mode="dotted", accent=ACCENT))
        for k in range(4):
            out.append(art("leaf", 30 + (k + 0.5) * W - 11, base + 30, 22, 1.1))
        for t, cx, b in R.slots(p, 30, W):
            if t == "h":   # bracket under the two leaves a half note fills
                x1, x2, by = cx - 20, cx + W + 20, base + 58
                out.append(f'<path d="M{x1},{by - 5} L{x1},{by} L{x2},{by} L{x2},{by - 5}" fill="none" stroke="#000" stroke-width="1.3"/>')
                out.append(text((x1 + x2) / 2, by + 11, "half note: 2 beats", 9.5, 500, upper=True))
        y += 160
    out.append(row_label(y + 14, "Now write your own 4-beat pattern: one symbol group for each leaf"))
    by = y + 26
    out.append(f'<rect x="20" y="{by}" width="{TR_W - 40}" height="96" rx="10" fill="none" stroke="#000" stroke-width="1.2"/>')
    out.append(guide(34, TR_W - 34, by + 58))
    for k in range(4):
        out.append(art("leaf", 30 + (k + 0.5) * W - 11, by + 66, 22, 1.1))
    H = by + 100
    body = svg(TR_W, H, "".join(out))
    return (f'<section class="page">{wm(watermark)}{top("Tracing 5 · 4-beat patterns", "TRACING", "5 of 5")}'
            f'{NAME}<div class="how"><b>Trace</b> each pattern, starting at the big dots. <b>Color in</b> the gray noteheads; '
            f'leave the half-note head open. Then clap it while you count to 4. Every pattern fills 4 leaves; a half note fills 2.</div>'
            f'<div class="body">{body}</div>{foot(f"Page {page_no}")}</section>')


# ---------------------------------------------------------------- beat-count worksheets
def ws_body(ws, key):
    ans = answers(ws)
    out = []
    A = dict(fill=ACCENT)
    if ws["kind"] == "single":
        cw, ch = 135, 250
        for i, t in enumerate(ws["items"]):
            x, y = (i % 4) * cw, (i // 4) * ch
            out.append(f'<rect x="{x + 4}" y="{y + 4}" width="{cw - 8}" height="{ch - 10}" rx="12" fill="none" stroke="#000" stroke-width="1.5"/>')
            out.append(text(x + 20, y + 26, str(i + 1), 13, 700))
            s = 17
            cy = y + 80
            out.append(R.engraved(t, x + cw / 2, cy if t == "r" else cy + 1.5 * s, s))
            out.append(art("pumpkin", x + cw - 46, y + 12, 34, 1.2))
            out.append(f'<rect x="{x + cw / 2 - 34}" y="{y + 140}" width="68" height="62" rx="10" fill="#fff" stroke="#000" stroke-width="1.6"/>')
            if key:
                out.append(text(x + cw / 2, y + 185, str(ans[i]), 34, 700, **A))
            out.append(text(x + cw / 2, y + 226, ("beats" if ans[i] != 1 else "beat") if key else "beat(s)", 13, 500, upper=True))
        H = 2 * ch
    elif ws["kind"] == "count":
        rh, s, W = 104, 14, 72
        for i, p in enumerate(ws["items"]):
            y = i * rh
            out.append(f'<rect x="2" y="{y + 4}" width="{TR_W - 4}" height="{rh - 12}" rx="12" fill="none" stroke="#000" stroke-width="1.4"/>')
            out.append(text(22, y + 30, str(i + 1), 14, 700))
            body, _, end = R.engraved_pattern(p, 50, y + 64, s, W, staff=False, timesig=False)
            out.append(body)
            out.append(text(370, y + 60, "=", 30, 300))
            out.append(f'<rect x="398" y="{y + 22}" width="56" height="56" rx="8" fill="#fff" stroke="#000" stroke-width="1.6"/>')
            if key:
                out.append(text(426, y + 64, str(ans[i]), 32, 700, **A))
            out.append(text(466, y + 58, "beats", 14, 500, anchor="start", upper=True))
        H = len(ws["items"]) * rh
    else:
        rh, s, W = 96, 14, 62
        for i, p in enumerate(ws["items"]):
            y = i * rh
            out.append(f'<rect x="2" y="{y + 4}" width="{TR_W - 4}" height="{rh - 12}" rx="12" fill="none" stroke="#000" stroke-width="1.4"/>')
            out.append(text(22, y + 30, str(i + 1), 14, 700))
            body, _, _ = R.stick_pattern(p, 44, y + 72, s, W)
            out.append(body)
            for j, word in enumerate(("YES", "NO")):
                cx = 412 + j * 76
                out.append(text(cx, y + 58, word, 20, 700))
                if key and ans[i] == word:
                    out.append(f'<ellipse cx="{cx}" cy="{y + 51}" rx="31" ry="20" fill="none" stroke="{ACCENT}" stroke-width="3.4"/>')
            if key:
                out.append(text(TR_W - 14, y + 86, f"{R.beats(p)} beats", 10, 500, anchor="end", upper=True, fill=ACCENT))
        H = len(ws["items"]) * rh
    return svg(TR_W, H, "".join(out))


def ws_page(ws, page_no, key_page, watermark=False):
    n, title = ws["id"], ws["title"]
    return (f'<section class="page">{wm(watermark)}{top(f"Beat count {n} · {title}", "BEAT COUNT", f"Worksheet {n} of 3")}'
            f'{NAME}<div class="how"><b>How to:</b> {ws["how"]}</div>'
            f'<div class="body">{ws_body(ws, False)}</div>{foot(f"Answer key on page {key_page} · Page {page_no}")}</section>')


def key_page(ws, page_no, ws_page_no, watermark=False):
    note = {"single": "Quarter note, two eighth notes and quarter rest = 1 beat each; half note = 2 beats. Two eighth notes share one beat.",
            "count": "Totals are the sum of the beats in each pattern: quarter, eighth pair and rest = 1, half note = 2.",
            "yesno": "The small number under each row is the total beats in that pattern."}[ws["kind"]]
    n, title = ws["id"], ws["title"]
    return (f'<section class="page">{wm(watermark)}{top(f"Beat count {n}: {title}", "ANSWER KEY", f"Worksheet on page {ws_page_no}", ak=True, title="Answer Key")}'
            f'<div class="how" style="margin-top:9pt">{note}</div>'
            f'<div class="body">{ws_body(ws, True)}</div>{foot(f"Page {page_no}")}</section>')


# ---------------------------------------------------------------- teacher, reference, terms, cover
def plan():
    """Ordered (kind, args) for every page of the resource; page numbers come from the order."""
    p = [("cover",), ("teacher",), ("reference",), ("symcards", False), ("symcards", True)]
    p += [("patcards", i, False) for i in range(6)]
    p += [("patcards", i, True) for i in range(6)]
    p += [("trace", t, i + 1) for i, t in enumerate(SYMBOLS)] + [("tracepat",)]
    p += [("ws", w) for w in WS] + [("key", w) for w in WS]
    p += [("terms",)]
    return p


def page_index():
    idx = {}
    for i, item in enumerate(plan()):
        k = item[0]
        if k in ("ws", "key"):
            idx[(k, item[1]["id"])] = i + 1
        elif k == "patcards":
            idx[(k, item[1], item[2])] = i + 1
        elif k == "symcards":
            idx[(k, item[1])] = i + 1
        elif k == "trace":
            idx[(k, item[1])] = i + 1
        else:
            idx[k] = i + 1
    return idx


def ranges():
    ix = page_index()
    return {
        "symstd": ix[("symcards", False)], "symstick": ix[("symcards", True)],
        "patstd": f'{ix[("patcards", 0, False)]}–{ix[("patcards", 5, False)]}',
        "patstick": f'{ix[("patcards", 0, True)]}–{ix[("patcards", 5, True)]}',
        "trace": f'{ix[("trace", "q")]}–{ix["tracepat"]}',
        "ws": f'{ix[("ws", 1)]}–{ix[("ws", 3)]}', "keys": f'{ix[("key", 1)]}–{ix[("key", 3)]}',
        "terms": ix["terms"], "total": len(plan()),
    }


def teacher_page():
    rg = ranges()
    rows = [("Symbol cards (8)", f"{rg['symstd']}–{rg['symstick']}", "4 symbols, standard + stick"),
            ("Pattern cards (24)", f"{rg['patstd']}, {rg['patstick']}", "12 patterns, 3 sets, standard + stick"),
            ("Tracing (5 pages)", rg["trace"], "1 page per symbol + patterns"),
            ("Beat count", f"{rg['ws']}, keys {rg['keys']}", "3 worksheets + answer keys")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} &amp; Tracing · grades K–2</div></div>'
            f'<div class="cols"><div>'
            f'<h2>Getting the cards ready</h2><ul>'
            f'<li>Print the card pages single-sided on cardstock, cut on the dashed lines, and laminate if you like.</li>'
            f'<li>Start with the <b>symbol cards</b>, then the <b>pattern cards</b> in order: Set A (quarter and eighth notes), Set B (adds the rest), Set C (adds the half note).</li>'
            f'<li>Each card comes in <b>standard notation</b> and <b>stick notation</b>. Use stick notation first if your students know it, then move to standard notation.</li></ul>'
            f'<h2>Ways to use the cards</h2><ul>'
            f'<li><b>Flash &amp; clap:</b> show a card, count in “1, 2, ready, go,” and the class claps and says it.</li>'
            f'<li><b>Pat the leaves:</b> the leaves under each pattern card are the steady beat. Pat on each leaf while you clap the rhythm.</li>'
            f'<li><b>Which card did I clap?</b> Lay out 3–4 pattern cards, clap one, and students point to it.</li>'
            f'<li><b>Wise owl’s mistake:</b> clap a card with one change; students find the beat that is different.</li>'
            f'<li><b>Compose:</b> students line up symbol cards to make their own 4-beat pattern (a half note counts as 2).</li></ul>'
            f'<h2>Rhythm syllables</h2>'
            f'<p>Cards print the Kodály syllables (ta, ti-ti, ta-a) only as a small, labelled option. Many teachers use other systems: '
            f'Takadimi (ta, ta-di), Gordon (du, du-de), counting (1, 1-and) or word chants. Use whatever your students already know. '
            f'Fall word chant, if you like: <i>leaf</i> (quarter note), <i>pump-kin</i> (two eighths), <i>whoo-oo</i> like an owl (half note), <i>shh</i> (rest).</p>'
            f'</div><div>'
            f'<h2>What’s inside</h2><table><tr><th>Part</th><th>Pages</th><th>Contents</th></tr>{trs}</table>'
            f'<p class="small">Page 3 is a student reference (anchor chart) with every symbol, its beats and the optional syllables. Last page: terms of use and credits.</p>'
            f'<h2>Tracing &amp; worksheets</h2><ul>'
            f'<li>Tracing pages: trace big, trace small, then draw on the empty lines. The big dot shows where to start each line.</li>'
            f'<li>Beat-count worksheets have answer keys right after them (pages {rg["keys"]}).</li>'
            f'<li>Every page prints well in black and white.</li></ul>'
            f'<h2>Music notes</h2><p class="small">All pattern cards are exactly 4 beats in 4/4 time. Notes have stems up, as on a one-line rhythm staff; '
            f'the two eighth notes are beamed together and share one beat. The quarter rest is one silent beat. The half note lasts two beats.</p>'
            f'<h2>Standards</h2><p>Supports reading and performing rhythm patterns in iconic or standard notation (National Core Arts Standards, '
            f'Music, MU:Pr4.2 in grades 1–2) and steady-beat work in kindergarten.</p>'
            f'<p class="small">No songs, lyrics or copyrighted characters are used. All art is original.</p>'
            f'</div></div><div style="flex:1"></div>{foot("Page 2")}</section>')


def reference_page():
    rows = []
    for t in SYMBOLS:
        info = R.TOKENS[t]
        s = 12
        std = svg(70, 56, R.engraved(t, 35, 28 if t == "r" else 46, s * 0.9))
        stk = svg(70, 56, R.hand(t, 35, 48, s * 0.9, heads=False))
        rows.append(f'<tr><td>{std}</td><td>{stk}</td><td class="n"><span class="big">{info["name"]}</span></td>'
                    f'<td><b>{beats_text(t)}</b></td><td>{info["kodaly"]}</td><td>{info["word"]}</td></tr>')
    s, W = 13, 84
    tot = 2.6 * s + 4 * W + 1.1 * s
    body, centres, _ = R.engraved_pattern("eqh", 10, 58, s, W)
    leaves = "".join(art("leaf", cx - 11, 92, 22, 1.1) + text(cx, 128, str(i + 1), 11, 500) for i, cx in enumerate(centres))
    ex = svg(int(tot + 20), 134, body + leaves)
    return (f'<section class="page doc"><div class="rule"><h1>Rhythm Reference</h1>'
            f'<div class="l" style="font-size:13pt">Our four rhythm symbols · keep this page nearby or display it as an anchor chart</div></div>'
            f'<table class="ref"><tr><th>Standard</th><th>Stick</th><th>Name</th><th>Beats</th><th>Kodály syllable<br>(optional)</th><th>Fall word<br>(optional)</th></tr>'
            f'{"".join(rows)}</table>'
            f'<h2>The steady beat <span class="acc">·</span> one leaf for every beat</h2>'
            f'<p>A pattern card has 4 beats. Each quarter note, pair of eighth notes, or quarter rest fills <b>one</b> leaf. '
            f'A half note fills <b>two</b> leaves: say it and hold it.</p>'
            f'<div style="display:flex;justify-content:center;margin:6pt 0">{ex}</div>'
            f'<p class="small" style="text-align:center">Two eighth notes, a quarter note and a half note: 1 + 1 + 2 = 4 beats.</p>'
            f'<h2>Remember</h2><ul><li>Stems on these cards go <b>up</b> on the right side of the notehead.</li>'
            f'<li>A <b>filled</b> notehead is a quarter or eighth note. An <b>open</b> (empty) notehead with a stem is a half note.</li>'
            f'<li>Two eighth notes are joined by a <b>beam</b>. Together they make one beat.</li>'
            f'<li>A rest means <b>silence</b> for one beat. Keep the beat going in your head.</li></ul>'
            f'<p class="small">Syllables are optional. Your teacher may use different words, such as Takadimi, Gordon or counting.</p>'
            f'<div style="flex:1"></div>{foot("Page 3")}</section>')


def terms_page(page_no):
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
            f'<h2>Credits</h2><ul>'
            f'<li>Art, cards, layouts and answer keys: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">Designed with the help of digital and AI tools, and checked by hand.</p>'
            f'<div style="flex:1"></div>{foot(f"Page {page_no}")}</section>')


def mini_card(x, y, w, h, inner, rot=0, sw=3):
    cx, cy = x + w / 2, y + h / 2
    return (f'<g transform="rotate({rot} {cx:.1f} {cy:.1f})"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#fff" '
            f'stroke="#000" stroke-width="{sw}"/>{inner}</g>')


def hero_svg(width_css):
    """Cover art: a big pattern card with beat leaves, fall art around it; accent and black only."""
    A = ACCENT
    s, W = 17, 72
    body, centres, _ = R.engraved_pattern("erh", 136, 150, s, W)
    leaves = "".join(art("leaf", cx - 15, 200, 30, 2.0, fill=A) for cx in centres)
    card = mini_card(100, 46, 400, 210, body + leaves, rot=-3, sw=3.4)
    back = mini_card(118, 30, 380, 210, "", rot=-9, sw=2.6)
    deco = (art("maple", 12, 6, 96, 2.4, fill=A, rotate=-20) + art("leaf", 506, 4, 78, 2.4, fill=A, rotate=25)
            + art("owl", 8, 214, 126, 2.6) + art("pumpkin", 466, 222, 124, 2.6, fill=A)
            + art("acorn", 410, 290, 56, 2.2) + art("leaf", 150, 288, 56, 2.2, fill=A, rotate=-60))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="{width_css}" style="display:block">'
            f'{back}{card}{deco}</svg>')


def cover_page():
    rg = ranges()
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.9in">{hero_svg("100%")}</div>'
            f'<div class="ctitle"><div class="a">FALL RHYTHM</div><div class="b">FLASHCARDS</div>'
            f'<div class="c">&amp; tracing worksheets · quarter note, eighth notes, quarter rest, half note</div></div>'
            f'<div class="cband">Grades K–2 <em>·</em> 32 cards <em>·</em> {rg["total"]} pages</div></section>')


# ---------------------------------------------------------------- assemble
def render_page(item, watermark=False):
    ix = page_index()
    k = item[0]
    if k == "cover":
        return cover_page()
    if k == "teacher":
        return teacher_page()
    if k == "reference":
        return reference_page()
    if k == "symcards":
        return symbol_cards_page(item[1], ix[("symcards", item[1])], watermark)
    if k == "patcards":
        return pattern_cards_page(item[1], item[2], ix[("patcards", item[1], item[2])], watermark)
    if k == "trace":
        return tracing_page(item[1], item[2], ix[("trace", item[1])], watermark)
    if k == "tracepat":
        return tracing_patterns_page(ix["tracepat"], watermark)
    if k == "ws":
        return ws_page(item[1], ix[("ws", item[1]["id"])], ix[("key", item[1]["id"])], watermark)
    if k == "key":
        return key_page(item[1], ix[("key", item[1]["id"])], ix[("ws", item[1]["id"])], watermark)
    if k == "terms":
        return terms_page(ix["terms"])
    raise KeyError(k)


PREVIEW_PICKS = [("symcards", False), ("patcards", 2, True), ("trace", "e", 2), ("ws", WS[1])]


def preview_pages():
    return [render_page(p, watermark=True) for p in PREVIEW_PICKS]


# ---------------------------------------------------------------- square images (2000 x 2000)
SQ_CSS = """
.sq { width: 1000px; height: 1000px; position: relative; overflow: hidden; background: #fff; display: flex; flex-direction: column; align-items: center; }
.sq .store { font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; margin-top: 34px; }
.sq .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; }
.sq .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.sq .band { position: absolute; left: 0; right: 0; bottom: 0; background: #000; color: #fff; text-align: center; font-family: 'Oswald';
            font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; padding: 16px 0 18px; }
.sq .band em { font-style: normal; color: ACCENT; }
.shot { background: #fff; border: 2px solid #000; box-shadow: 8px 8px 0 #000; position: relative; overflow: hidden; }
.shot img { display: block; width: 100%; }
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; text-align: center; margin-top: 16px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 18px; }
.swm { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
       color: rgba(0,0,0,.14); white-space: nowrap; letter-spacing: .06em; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="width:820px;margin-top:18px">{hero_svg("100%")}</div>'
        f'<div class="hd" style="font-size:66px;margin-top:10px">Fall Rhythm</div>'
        f'<div class="hd" style="font-size:118px">Flashcards</div>'
        f'<div class="sub" style="font-size:29px;margin-top:12px">&amp; tracing worksheets · ta, ti-ti, rest, half note</div>'
        f'<div class="band">Grades K–2 <em>·</em> 32 cards <em>·</em> tracing <em>·</em> answer keys</div></div>')


def preview_square_1(img):
    items = [(img[0], "Symbol cards", "standard + stick"), (img[1], "Pattern cards", "12 four-beat patterns"),
             (img[2], "Tracing", "trace, then draw")]
    shots = "".join(
        f'<div style="width:300px"><div class="shot"><img src="{src}"><div class="swm" style="font-size:54px">PREVIEW</div></div>'
        f'<div class="lbl">{a}<span>{b}</span></div></div>' for src, a, b in items)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:76px;margin-top:20px">Cards, tracing &amp; beats</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Everything for ta, ti-ti, rest and half note in one fall set</div>'
        f'<div style="display:flex;gap:24px;margin-top:80px">{shots}</div>'
        f'<div class="band">32 flashcards <em>·</em> 5 tracing pages <em>·</em> 3 worksheets</div></div>')


def preview_square_2(ws, key):
    pair = "".join(
        f'<div style="width:420px"><div class="shot"><img src="{src}"><div class="swm" style="font-size:80px">PREVIEW</div></div>'
        f'<div class="lbl">{lab}</div></div>' for src, lab in ((ws, "Worksheet"), (key, "Answer key")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:20px">Beat-count practice</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Three worksheets, each with an answer key</div>'
        f'<div style="display:flex;gap:40px;margin-top:30px">{pair}</div>'
        f'<div class="band">Every pattern checked: 4 beats in 4/4</div></div>')


def preview_square_3():
    cells = []
    for n, (setk, p) in enumerate(PATTERNS, 1):
        body, _, _ = R.engraved_pattern(p, 22, 66, 9, 46)
        cells.append(f'<div style="width:250px"><svg viewBox="0 0 250 110" width="250" style="display:block">'
                     f'<rect x="2" y="2" width="246" height="106" rx="10" fill="#fff" stroke="#000" stroke-width="2.2"/>'
                     f'{text(16, 24, str(n), 14, 700, anchor="start")}{body}</svg></div>')
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:16px">12 pattern cards</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">3 sets that build step by step · standard and stick notation</div>'
        f'<div style="position:relative;display:flex;flex-wrap:wrap;gap:22px 26px;width:810px;margin-top:34px;justify-content:center">{"".join(cells)}'
        f'<div class="swm" style="font-size:150px">PREVIEW</div></div>'
        f'<div class="band">Set A <em>·</em> Set B adds rest <em>·</em> Set C adds half note</div></div>')


# ---------------------------------------------------------------- render
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


def write(name, txt):
    p = os.path.join(BUILD, name)
    with open(p, "w") as f:
        f.write(txt)
    return p


def tpt_json(pages):
    return {
        "price": PRICE, "license_price": PRICE,
        "tax_code": "Other Digital Goods - No Physical Media",
        "grades": ["kindergarten", "1st-grade", "2nd-grade"],
        "subjects": ["Music"],
        "tags": ["Autumn"],
        "formats": ["PDF"],
        "pages": pages,
        "answer_key": "Included",
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


def build():
    os.makedirs(BUILD, exist_ok=True)
    problems = verify_data()
    if problems:
        print("\n".join(problems))
        sys.exit("data check failed; not rendering")
    full = write("resource.html", html_doc([render_page(p) for p in plan()], TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in range(1, 5):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF,
                        os.path.join(BUILD, f"pv{i}")], check=True)
    kp = page_index()[("key", 2)]
    subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(kp), "-l", str(kp), "-singlefile", PDF,
                    os.path.join(BUILD, "pvkey")], check=True)
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1(["pv1.png", "pv2.png", "pv3.png"])),
          write("p2.html", preview_square_2("pv4.png", "pvkey.png")), write("p3.html", preview_square_3())]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(len(plan())), f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"built {PDF} ({len(plan())} pages), {PREVIEW_PDF}, cover + 3 previews, tpt.json")


# ---------------------------------------------------------------- checks
def verify_data():
    errs = []
    for setk, p in PATTERNS:
        if R.beats(p) != 4:
            errs.append(f"pattern {p} in set {setk} has {R.beats(p)} beats, not 4")
        allowed = {"A": set("qe"), "B": set("qer"), "C": set("qerh")}[setk]
        if not set(p) <= allowed:
            errs.append(f"pattern {p} uses symbols outside set {setk}")
    if "r" not in "".join(SETS["B"]["patterns"]) or any("r" not in p for p in SETS["B"]["patterns"]):
        errs.append("every Set B card should contain the new rest")
    if any("h" not in p for p in SETS["C"]["patterns"]):
        errs.append("every Set C card should contain the new half note")
    if len({p for _, p in PATTERNS}) != len(PATTERNS):
        errs.append("duplicate pattern cards")
    for p in TRACE_PATTERNS:
        if R.beats(p) != 4:
            errs.append(f"tracing pattern {p} is not 4 beats")
    # token facts (independent of rhythm.py's table)
    want = {"q": (1, 1), "e": (1, 2), "r": (1, 0), "h": (2, 1)}
    for t, (b, n) in want.items():
        if (R.TOKENS[t]["beats"], R.TOKENS[t]["sounds"]) != (b, n):
            errs.append(f"token {t}: beats/sounds wrong")
    hand_key = {1: [1, 2, 1, 1, 2, 1, 1, 1], 2: [2, 3, 4, 3, 4, 2], 3: ["YES", "NO", "YES", "NO", "YES", "NO"]}
    for ws in WS:
        if answers(ws) != hand_key[ws["id"]]:
            errs.append(f"worksheet {ws['id']}: computed answers {answers(ws)} != hand-worked key {hand_key[ws['id']]}")
    # glyph codepoints are the SMuFL ones
    for name, cp in {"noteQuarterUp": 0xE1D5, "noteHalfUp": 0xE1D3, "restQuarter": 0xE4E5, "noteheadBlack": 0xE0A4, "timeSig4": 0xE084}.items():
        if R.GLYPH[name][0] != cp:
            errs.append(f"{name} codepoint wrong")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(ln.split()[0], ln.split()[-5]) for ln in out]


def verify_files():
    errs = []
    from pypdf import PdfReader
    from PIL import Image
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.basename(p)}")
    if errs:
        return errs
    for path, want in ((PDF, len(plan())), (PREVIEW_PDF, len(PREVIEW_PICKS))):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pg in enumerate(rd.pages):
            w, h = float(pg.mediabox.width), float(pg.mediabox.height)
            if abs(w - 612) > 1 or abs(h - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: {w:.0f}x{h:.0f}pt, not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
        names = " ".join(n for n, _ in fonts).lower()
        for fam in ("bravura", "oswald", "sourcesans3"):
            if fam not in names.replace(" ", ""):
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    rd = PdfReader(PDF)
    for i, pg in enumerate(rd.pages):
        if "Brian Lotze · Hudson Beat" not in pg.extract_text().replace("\n", " ") and i > 0:
            errs.append(f"page {i + 1}: footer missing")
    txt = [PdfReader(PREVIEW_PDF).pages[i].extract_text() for i in range(len(PREVIEW_PICKS))]
    if sum("PREVIEW" in t for t in txt) != len(PREVIEW_PICKS):
        errs.append("preview PDF: watermark missing on some pages")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
    tj = json.load(open(TPT_JSON))
    if tj["pages"] != len(rd.pages):
        errs.append("tpt.json pages != PDF pages")
    for k, f in tj["files"].items():
        if not os.path.exists(os.path.join(HERE, f)):
            errs.append(f"tpt.json file {k} missing: {f}")
    if not (1 <= len(tj["grades"]) <= 4 and 1 <= len(tj["subjects"]) <= 3 and 1 <= len(tj["tags"]) <= 6):
        errs.append("tpt.json grade/subject/tag counts out of range")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    elif len(m.group(1).strip()) > 80:
        errs.append(f"UPLOAD.md: title is {len(m.group(1).strip())} chars (max 80)")
    for need in ("Designed with the help of digital and AI tools, and checked by hand.", f"${PRICE}", f"{len(rd.pages)} pages"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    for f in ("release", "uploaded"):
        if os.path.exists(os.path.join(HERE, f)):
            errs.append(f"{f} exists: only the Manager / uploader writes it")
    return errs


def check():
    errs = verify_data() + verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs))
        sys.exit(1)
    print(f"CHECK OK: {len(PATTERNS)} pattern cards x 2 notations, all 4 beats; worksheet keys match hand-worked answers; "
          f"PDF {len(plan())} Letter pages with footers, preview {len(PREVIEW_PICKS)} watermarked pages, fonts embedded; "
          f"images 2000x2000; tpt.json and UPLOAD.md ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
