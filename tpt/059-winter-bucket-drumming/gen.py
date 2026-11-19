#!/usr/bin/env python3
"""Winter Bucket Drumming (TpT 059): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read every staff from the rendered HTML/SVG and verify numbers, notation and layout

Six original four-bar grooves in 4/4. Each groove has three parts meant to be layered: Part 1 Bass, Part 2 Groove, Part 3 Sparkle.
Parts are stored as bars of beat tokens (ta, shh, ti-ti, ta-a, ti-ka-ti-ka, ti-ti-ka, ti-ka-ti; a trailing ">" is an accent, a
trailing "*" is a rim click). `--check` does not trust that data: it parses the rendered SVG of every staff (one line, neutral clef,
4/4, noteheads, stems, beams, rests, accents, hand letters, syllables), derives every note value from the head glyph and the beams,
adds up every bar, recomputes the say-it syllables and the hand letters, compares them with the printed ones and with the data,
checks that the three stacked parts have the same bar count and that every beat sits at the same x in every part, and then checks
the page layout, the rendered pixels of every drawing, the images, the PDFs, the cross-references, UPLOAD.md and tpt.json.
"""
import json
import math
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from fractions import Fraction
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")
HERO = os.path.join(HERE, "art", "hero.png")

SLUG = "winter-bucket-drumming"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#2F86B8"
TINT = "#DCEEF8"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Winter Bucket Drumming"
LISTING_TITLE = "Bucket Drumming Play-Along Charts: 6 Rhythm Grooves, Layering, Grades 3-8"
PREFERRED_TITLE = "Winter Bucket Drumming: 6 Play-Along Rhythm Grooves with Layering Activity"
PRICE = "4.50"
TAGS = ["Winter", "Activities", "Lessons", "Printables", "Rubrics"]
SUBJECTS = ["Music", "Instrumental Music"]
GRADES = ["3rd-grade", "4th-grade", "5th-grade", "6th-grade"]

# ------------------------------------------------------------------ rhythm data
# One beat pattern = one token, named by its rhythm syllables. Each event is (kind, duration in beats): n note, r rest, h half note.
TOKDEF = {
    "ta": [("n", Fraction(1))],
    "shh": [("r", Fraction(1))],
    "ti-ti": [("n", Fraction(1, 2))] * 2,
    "ta-a": [("h", Fraction(2))],
    "ti-ka-ti-ka": [("n", Fraction(1, 4))] * 4,
    "ti-ti-ka": [("n", Fraction(1, 2)), ("n", Fraction(1, 4)), ("n", Fraction(1, 4))],
    "ti-ka-ti": [("n", Fraction(1, 4)), ("n", Fraction(1, 4)), ("n", Fraction(1, 2))],
}
# the independent table used by --check: (kind, duration) pattern of one beat -> syllables
BEAT_SYL = {
    (("n", Fraction(1)),): "ta",
    (("r", Fraction(1)),): "shh",
    (("n", Fraction(1, 2)), ("n", Fraction(1, 2))): "ti-ti",
    (("n", Fraction(1, 4)),) * 4: "ti-ka-ti-ka",
    (("n", Fraction(1, 2)), ("n", Fraction(1, 4)), ("n", Fraction(1, 4))): "ti-ti-ka",
    (("n", Fraction(1, 4)), ("n", Fraction(1, 4)), ("n", Fraction(1, 2))): "ti-ka-ti",
}
HALF_SYL = "ta-a"
SIXTEENTH_TOKENS = {"ti-ka-ti-ka", "ti-ti-ka", "ti-ka-ti"}
PART_NAMES = ["Bass", "Groove", "Sparkle"]
PART_ROLE = ["low and steady", "the main pattern", "clicks, offbeat fills and rests"]
BARS = 4
BEATS = 4

# Six original grooves, four bars of 4/4 each, three parts each (Bass, Groove, Sparkle). "*" = rim click, ">" = accent.
GROOVES = [
    {"n": 1, "name": "Snow Boots", "bpm": 70, "parts": [
        ["ta ta ta ta", "ta ta ta ta", "ta ta ta ta", "ta ta ta-a"],
        ["ta ta ti-ti ta", "ta ti-ti ta shh", "ta ta ti-ti ta", "ti-ti ti-ti ta shh"],
        ["shh ta* shh ta*", "shh ta* shh ta*", "shh ta* shh ta*", "shh ta* shh shh"]]},
    {"n": 2, "name": "Icicle Drip", "bpm": 70, "parts": [
        ["ta ta ta ta", "ta ta ta shh", "ta ta ta ta", "ta shh ta-a"],
        ["ta shh ti-ti ta", "ta ta ta shh", "ti-ti ta ti-ti ta", "ta ti-ti ta-a"],
        ["shh ta* shh shh", "shh ta* shh ta*", "shh ta* shh shh", "shh ta* ti-ti* shh"]]},
    {"n": 3, "name": "Sled Run", "bpm": 70, "parts": [
        ["ta> ta ta ta", "ta> ta ta ta", "ta> ta ta ta", "ta> ta ta-a"],
        ["ta ti-ti ta ti-ti", "ta ta ta> shh", "ta ti-ti ta ti-ti", "ti-ti ti-ti ta-a"],
        ["shh ta* shh ta*", "shh ti-ti* shh ta*", "shh ta* shh ta*", "ti-ti* ti-ti* shh shh"]]},
    {"n": 4, "name": "Shovel Shuffle", "bpm": 70, "parts": [
        ["ta ta ta ta", "ta ta ta shh", "ta ta ta ta", "ta ta ta-a"],
        ["ta> ti-ti ta ti-ti", "ta> ti-ti ta shh", "ta> ti-ti ta ti-ti", "ta ta ta-a"],
        ["shh ta* ti-ti* ta*", "shh ta* shh ta*", "shh ta* ti-ti* ta*", "shh ta* shh shh"]]},
    {"n": 5, "name": "Ice Skate Spin", "bpm": 60, "parts": [
        ["ta ta ta ta", "ta ta ta ta", "ta-a ta ta", "ta ta ta-a"],
        ["ti-ka-ti-ka ta ti-ti ta", "ta ti-ti ti-ka-ti-ka ta", "ti-ka-ti-ka ta ti-ti ta", "ti-ti ta> ta-a"],
        ["shh ta* shh ta*", "shh ti-ti* shh ta*", "shh ta* shh ta*", "ti-ti* ti-ti* ta* shh"]]},
    {"n": 6, "name": "Blizzard", "bpm": 60, "parts": [
        ["ta ta ta ta", "ta ta ta ta", "ta> ta ta> ta", "ta-a ta> ta"],
        ["ti-ka-ti-ka ti-ti-ka ta ta", "ta ti-ka-ti ta ti-ti", "ti-ka-ti-ka ti-ti-ka ta ta", "ti-ti ti-ka-ti-ka ta-a"],
        ["shh ta* shh ta*", "shh ti-ti* shh ti-ti*", "shh ta* shh ta*", "shh ta* ti-ti* ta*"]]},
]
N_GROOVES = len(GROOVES)
N_PARTS = N_GROOVES * 3


def parse_tok(t):
    acc, rim = t.endswith(">"), t.endswith("*")
    base = t.rstrip(">*")
    assert base in TOKDEF, t
    assert not (acc and rim), t
    if acc:
        assert base == "ta", f"accent only on a quarter note: {t}"
    if rim:
        assert base not in ("shh", "ta-a"), f"rim click on a rest or half note: {t}"
    return base, acc, rim


def token_beats(base):
    return sum(d for _, d in TOKDEF[base])


def part_events(bars):
    """Flatten a part (list of 4 bar strings) into events, beamed groups and token spans, and assign the hand letters."""
    ev, groups, toks, t = [], [], [], Fraction(0)
    for bar in bars:
        start = t
        for tk in bar.split():
            base, acc, rim = parse_tok(tk)
            idxs, t0 = [], t
            for kind, dur in TOKDEF[base]:
                ev.append({"kind": kind, "dur": dur, "t": t, "head": "x" if (rim and kind != "r") else "n", "acc": acc and kind != "r"})
                idxs.append(len(ev) - 1)
                t += dur
            if len(TOKDEF[base]) > 1 and TOKDEF[base][0][1] < 1:
                groups.append(idxs)
            toks.append({"tok": tk, "base": base, "t0": t0, "idx": idxs})
        assert t - start == BEATS, bar
    h = 0
    for e in ev:
        if e["kind"] != "r":
            e["hand"] = "RL"[h % 2]
            h += 1
    return ev, groups, toks


def validate_data():
    seen_g, seen_p = set(), set()
    for g in GROOVES:
        assert len(g["parts"]) == 3
        for pi, bars in enumerate(g["parts"]):
            assert len(bars) == BARS, (g["n"], pi)
            ev, _, toks = part_events(bars)
            for tk in toks:
                if tk["base"] == "ta-a":
                    assert tk["t0"] % BEATS in (0, 2), f"half note off beats 1 and 3 in groove {g['n']}"
                if tk["base"] in SIXTEENTH_TOKENS:
                    assert g["n"] >= 5 and pi == 1, "sixteenths only in the last grooves, Part 2"
            seen_p.add(" | ".join(bars))
            if pi == 0:      # Bass: low, steady, quarter-note based
                assert all(tk["base"] in ("ta", "shh", "ta-a") for tk in toks), f"bass of groove {g['n']} is not quarter-note based"
                assert sum(1 for e in ev if e["kind"] == "r") <= 2, "bass has too many rests to be steady"
                assert not any(e["head"] == "x" for e in ev)
            if pi == 1:
                assert not any(e["head"] == "x" for e in ev) and any(tk["base"] == "ti-ti" for tk in toks)
            if pi == 2:      # Sparkle: rim clicks and rests only
                assert all(e["head"] == "x" for e in ev if e["kind"] != "r"), "sparkle must be rim clicks"
                assert sum(1 for e in ev if e["kind"] == "r") >= 4
        seen_g.add(" || ".join(" | ".join(b) for b in g["parts"]))
    assert len(seen_g) == N_GROOVES and len(seen_p) == N_PARTS, "grooves or parts are not all different"
    assert sum(1 for g in GROOVES if any(set(b.replace(">", "").replace("*", "").split()) & SIXTEENTH_TOKENS for p in g["parts"] for b in p)) == 2


validate_data()


def part_stats(bars):
    ev, _, _ = part_events(bars)
    return {"notes": sum(1 for e in ev if e["kind"] != "r"), "rests": sum(1 for e in ev if e["kind"] == "r"),
            "acc": sum(1 for e in ev if e["acc"]), "rim": sum(1 for e in ev if e["kind"] != "r" and e["head"] == "x")}


def stats_text(st):
    s = f'{st["notes"]} notes, {st["rests"]} rests'
    if st["acc"]:
        s += f', {st["acc"]} accents'
    if st["rim"]:
        s += f', {st["rim"]} rim clicks'
    return s


# ------------------------------------------------------------------ drawing helpers
HEAD_W = 1.18
G_HEAD, G_HALF, G_X, G_QREST, G_NEUTRAL, G_TS4 = 0xE0A4, 0xE0A3, 0xE0A9, 0xE4E5, 0xE069, 0xE084
HW = {G_HEAD: 1.18, G_HALF: 1.18, G_X: 1.16}
REST_W = 1.08
STEM_X = 0.168
STEM_LEN = 3.5
CLEF_W, TS_W = 1.528, 1.88
SUBF = 0.8        # inside a beat the notes use 80% of the beat column, so the next beat starts clearly apart from a group of sixteenths
ACC_DY, ACC_HH, ACC_HW = 1.15, 0.42, 0.62     # accent: centre above the stem tip, half height, half width (staff spaces)


def fx(v):
    return f"{v:.2f}"


def gl(cp, x, y, size, cls="", fill="#000"):
    c = f' class="{cls}"' if cls else ""
    return f'<text{c} x="{fx(x)}" y="{fx(y)}" font-family="Bravura" font-size="{fx(size)}" fill="{fill}">&#x{cp:X};</text>'


def pos(t):
    t = Fraction(t)
    b = t.numerator // t.denominator
    return b + SUBF * float(t - b)


def system_svg(uid, staves, b0, nb, mode="full", W=540.0, S=5.8, final=True, show_ts=True, counts=True, guides=False, fh=8.5, fs=7.2,
               groove=0, bl=BEATS, sym_u=42.0):
    """One system: 1-3 staves stacked, all sharing the same bar and beat x positions.
    staves: list of dicts {part, name, bars, label}; bars = the full list of bar strings of that part.
    mode: full (chips, clef, ts, hands, say-it), ex (clef, ts, hands, say-it, no chips), sym (a bare notation symbol)."""
    full, ex, sym = mode == "full", mode == "ex", mode == "sym"
    LW = 50.0 if full else 6.0
    fins = final and not sym
    if sym:
        xb0, u = 2.0, sym_u
        padL = 0.55 * u
        BW = padL + (bl - 0.4) * u + 0.55 * u
        W = xb0 + BW + 2.0
    else:
        xb0 = LW + 4 + CLEF_W * S + 0.9 * S + TS_W * S + 0.9 * S
        xe = W - 4.0 - 0.2 * S
        BW = (xe - xb0) / nb
        u = BW / (bl + 0.6)
        padL = 0.5 * u
    hw0 = HEAD_W * S
    sw = 0.13 * S
    if sym:
        HH, Hb, gap, off = 2.0, 8.4 * S, 0.0, 6.0 * S
    else:
        HH = 25.0 if counts else 4.0
        off = 6.2 * S
        Hb = off + 5.0 * S + 5.0
        gap = 10.0
    H = HH + len(staves) * Hb + (len(staves) - 1) * gap + (2.0 if not sym else 0.0)
    if sym:
        H = HH + off + 2.2 * S
    sxf = lambda t: xb0 + (int(Fraction(t) // bl) - b0) * BW + padL + pos(Fraction(t) - bl * int(Fraction(t) // bl)) * u
    o = [f'<svg class="ns" data-kind="{mode}" data-id="{uid}" data-s="{fx(S)}" data-xb0="{fx(xb0)}" data-bw="{fx(BW)}" data-padl="{fx(padL)}" data-u="{fx(u)}" '
         f'data-nb="{nb}" data-b0="{b0}" data-bl="{bl}" data-final="{int(fins)}" data-ts="{int(show_ts)}" data-groove="{groove}" xmlns="http://www.w3.org/2000/svg" '
         f'viewBox="0 0 {W:.2f} {H:.2f}" width="{W:.2f}pt" height="{H:.2f}pt" style="display:block">']
    if counts and not sym:
        for b in range(nb):
            o.append(f'<text class="bn" x="{fx(xb0 + b * BW + 3)}" y="9" font-family="Oswald" font-weight="500" font-size="7.6" fill="#333">BAR {b0 + b + 1}</text>')
            for k in range(bl):
                o.append(f'<text class="cnt" x="{fx(sxf((b0 + b) * bl + k))}" y="21" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="600" font-size="8.2" fill="#555">{k + 1}</text>')
    for si, st in enumerate(staves):
        yb = HH + si * (Hb + gap)
        y0 = yb + off
        ev, groups, toks = part_events(st["bars"]) if not sym else part_events_sym(st["bars"], bl)
        lo, hi = Fraction(b0 * bl), Fraction((b0 + nb) * bl)
        o.append(f'<g class="staff" data-groove="{groove}" data-part="{st.get("part", 0)}" data-y0="{fx(y0)}">')
        x_line0 = LW if full else 2.0
        o.append(f'<line class="sl" x1="{fx(x_line0)}" y1="{fx(y0)}" x2="{fx(W - 2)}" y2="{fx(y0)}" stroke="#000" stroke-width="{fx(sw)}"/>')
        if guides:
            for t in range(b0 * bl, (b0 + nb) * bl):
                gx = sxf(t)
                o.append(f'<line class="guide" x1="{fx(gx)}" y1="{fx(y0 - 4.0 * S)}" x2="{fx(gx)}" y2="{fx(y0 + 1.0 * S)}" stroke="#9CC6E0" stroke-width="0.7" stroke-dasharray="2 2"/>')
        if full:
            o.append(f'<rect class="chip" x="4" y="{fx(y0 - 12)}" width="40" height="24" rx="3" fill="#000"/>')
            o.append(f'<text class="chipn" x="24" y="{fx(y0 - 3.2)}" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="6.4" fill="#fff">PART {st["part"]}</text>')
            o.append(f'<text class="chipt" x="24" y="{fx(y0 + 8.4)}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="9.2" fill="#fff">{st["name"].upper()}</text>')
            o.append(f'<text class="rowlab" x="{LW - 4}" y="{fx(y0 + 3.2 * S)}" text-anchor="end" font-family="Source Sans 3, sans-serif" font-style="italic" font-size="6.6" fill="#555">hands</text>')
            o.append(f'<text class="rowlab" x="{LW - 4}" y="{fx(y0 + 5.0 * S)}" text-anchor="end" font-family="Source Sans 3, sans-serif" font-style="italic" font-size="6.6" fill="#555">say it</text>')
        if not sym:
            o.append(gl(G_NEUTRAL, LW + 4, y0, 4 * S, "clef"))
            if show_ts and si >= 0 and b0 == 0:
                o.append(gl(G_TS4, LW + 4 + CLEF_W * S + 0.9 * S, y0 - 1.25 * S, 4 * S, "tsd"))
                o.append(gl(G_TS4, LW + 4 + CLEF_W * S + 0.9 * S, y0 + 1.25 * S, 4 * S, "tsd"))
            for b in range(nb):
                bxx = xb0 + (b + 1) * BW
                if b < nb - 1 or not fins:
                    o.append(f'<line class="bar" x1="{fx(bxx)}" y1="{fx(y0 - 2 * S)}" x2="{fx(bxx)}" y2="{fx(y0 + 2 * S)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
                else:
                    o.append(f'<line class="bar" x1="{fx(bxx - 0.5 * S)}" y1="{fx(y0 - 2 * S)}" x2="{fx(bxx - 0.5 * S)}" y2="{fx(y0 + 2 * S)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
                    o.append(f'<rect class="fin" x="{fx(bxx - 0.18 * S)}" y="{fx(y0 - 2 * S)}" width="{fx(0.36 * S)}" height="{fx(4 * S)}" fill="#000"/>')
        tip = y0 - STEM_X * S - STEM_LEN * S
        stem_x, xcs = {}, {}
        for i, e in enumerate(ev):
            if not (lo <= e["t"] < hi):
                continue
            xc = sxf(e["t"])
            xcs[i] = xc
            if e["kind"] == "r":
                o.append(f'<g class="ev">{gl(G_QREST, xc - REST_W * S / 2, y0, 4 * S, "rest")}</g>')
                continue
            glyph = G_HALF if e["kind"] == "h" else (G_X if e["head"] == "x" else G_HEAD)
            hw = HW[glyph] * S
            left = xc - hw / 2
            sx = left + hw - sw / 2
            stem_x[i] = sx
            ystart = y0 - (0.40 if glyph == G_X else STEM_X) * S
            acc = ""
            if e["acc"]:
                cy, hh, hwid = tip - ACC_DY * S, ACC_HH * S, ACC_HW * S
                acc = (f'<polyline class="acc" points="{fx(sx - hwid)},{fx(cy - hh)} {fx(sx + hwid)},{fx(cy)} {fx(sx - hwid)},{fx(cy + hh)}" fill="none" '
                       f'stroke="#000" stroke-width="{fx(0.17 * S)}" stroke-linecap="round" stroke-linejoin="round"/>')
            o.append(f'<g class="ev">{gl(glyph, left, y0, 4 * S, "head")}'
                     f'<line class="stem" x1="{fx(sx)}" y1="{fx(ystart)}" x2="{fx(sx)}" y2="{fx(tip)}" stroke="#000" stroke-width="{fx(sw)}"/>{acc}</g>')
        for g in groups:
            if g[0] not in stem_x:
                continue
            x1, x2 = stem_x[g[0]] - sw / 2, stem_x[g[-1]] + sw / 2
            o.append(f'<rect class="beam" data-lvl="1" x="{fx(x1)}" y="{fx(tip)}" width="{fx(x2 - x1)}" height="{fx(0.5 * S)}" fill="#000"/>')
            run = []
            for i in g + [None]:
                if i is not None and ev[i]["dur"] == Fraction(1, 4):
                    run.append(i)
                    continue
                if len(run) >= 2:
                    a, b = stem_x[run[0]] - sw / 2, stem_x[run[-1]] + sw / 2
                    o.append(f'<rect class="beam" data-lvl="2" x="{fx(a)}" y="{fx(tip + 0.75 * S)}" width="{fx(b - a)}" height="{fx(0.5 * S)}" fill="#000"/>')
                run = []
        if not sym:
            for i, e in enumerate(ev):
                if i in xcs and e["kind"] != "r":
                    o.append(f'<text class="hand" x="{fx(xcs[i])}" y="{fx(y0 + 3.2 * S)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="700" font-size="{fh}">{e["hand"]}</text>')
            for tk in toks:
                if tk["idx"][0] not in xcs:
                    continue
                if tk["base"] == "ta-a":
                    cx = xcs[tk["idx"][0]] + 0.5 * u
                else:
                    cx = (xcs[tk["idx"][0]] + xcs[tk["idx"][-1]]) / 2
                o.append(f'<text class="syl" x="{fx(cx)}" y="{fx(y0 + 5.0 * S)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="700" font-size="{fs}">{tk["base"]}</text>')
        o.append("</g>")
    o.append("</svg>")
    return "".join(o)


def part_events_sym(bars, bl):
    """A bare symbol: bars = [one token string] of any length in beats."""
    ev, groups, toks, t = [], [], [], Fraction(0)
    for tk in bars[0].split():
        base, acc, rim = parse_tok(tk)
        idxs, t0 = [], t
        for kind, dur in TOKDEF[base]:
            ev.append({"kind": kind, "dur": dur, "t": t, "head": "x" if (rim and kind != "r") else "n", "acc": acc and kind != "r"})
            idxs.append(len(ev) - 1)
            t += dur
        if len(TOKDEF[base]) > 1 and TOKDEF[base][0][1] < 1:
            groups.append(idxs)
        toks.append({"tok": tk, "base": base, "t0": t0, "idx": idxs})
    assert t == bl, (bars, t, bl)
    return ev, groups, toks


def glyph_svg(uid, kind, S=7.0):
    """Small drawings for the key: clef, 4/4, barline, final barline, and the one-line staff, each on a short staff line."""
    w = {"clef": 6.0 * S, "ts": 5.2 * S, "bar": 4.4 * S, "fin": 4.4 * S, "staff": 8.0 * S, "stems": 6.0 * S}[kind]
    w = max(w, 30.0)
    y0 = 3.2 * S
    H = y0 + 3.2 * S
    sw = 0.13 * S
    o = [f'<svg class="ic" data-kind="{kind}" data-id="{uid}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {H:.2f}" width="{w:.2f}pt" height="{H:.2f}pt" style="display:block">']
    o.append(f'<line class="sl" x1="2" y1="{fx(y0)}" x2="{fx(w - 2)}" y2="{fx(y0)}" stroke="#000" stroke-width="{fx(sw)}"/>')
    cx = w / 2
    if kind == "clef":
        o.append(gl(G_NEUTRAL, cx - CLEF_W * S / 2, y0, 4 * S, "clef"))
    elif kind == "ts":
        o.append(gl(G_TS4, cx - TS_W * S / 2, y0 - 1.25 * S, 4 * S, "tsd"))
        o.append(gl(G_TS4, cx - TS_W * S / 2, y0 + 1.25 * S, 4 * S, "tsd"))
    elif kind == "bar":
        o.append(f'<line class="bar" x1="{fx(cx)}" y1="{fx(y0 - 2 * S)}" x2="{fx(cx)}" y2="{fx(y0 + 2 * S)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
    elif kind == "fin":
        bx = cx + 0.4 * S
        o.append(f'<line class="bar" x1="{fx(bx - 0.5 * S)}" y1="{fx(y0 - 2 * S)}" x2="{fx(bx - 0.5 * S)}" y2="{fx(y0 + 2 * S)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
        o.append(f'<rect class="fin" x="{fx(bx - 0.18 * S)}" y="{fx(y0 - 2 * S)}" width="{fx(0.36 * S)}" height="{fx(4 * S)}" fill="#000"/>')
    o.append("</svg>")
    return "".join(o)


def bucket_icon(kind, uid):
    """Top view of a bucket: where the stick lands. kind: center, between, rim. 100 x 100 box."""
    o = [f'<svg class="ic" data-kind="bucket-{kind}" data-id="{uid}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="70pt" height="70pt" style="display:block">']
    o.append('<circle cx="50" cy="50" r="42" fill="#fff" stroke="#000" stroke-width="2.4"/>')
    o.append('<circle cx="50" cy="50" r="33" fill="#fff" stroke="#000" stroke-width="1.4"/>')
    if kind == "center":
        o.append(f'<circle cx="50" cy="50" r="10" fill="{ACCENT}" stroke="#000" stroke-width="1.6"/>')
    elif kind == "between":
        o.append(f'<circle cx="50" cy="31" r="8" fill="{ACCENT}" stroke="#000" stroke-width="1.6"/>')
    else:
        a0, a1 = math.radians(-80), math.radians(-10)
        x0, y0_ = 50 + 37.5 * math.cos(a0), 50 + 37.5 * math.sin(a0)
        x1, y1_ = 50 + 37.5 * math.cos(a1), 50 + 37.5 * math.sin(a1)
        o.append(f'<path d="M {x0:.2f} {y0_:.2f} A 37.5 37.5 0 0 1 {x1:.2f} {y1_:.2f}" fill="none" stroke="{ACCENT}" stroke-width="6" stroke-linecap="round"/>')
    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------------ CSS and page frame
def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"),
             ("Oswald", 700, "normal", "oswald-latin-700-normal"),
             ("Source Sans 3", 400, "normal", "source-sans-3-latin-400-normal"), ("Source Sans 3", 400, "italic", "source-sans-3-latin-400-italic"),
             ("Source Sans 3", 600, "normal", "source-sans-3-latin-600-normal"), ("Source Sans 3", 700, "normal", "source-sans-3-latin-700-normal"),
             ("Bravura", 400, "normal", "bravura")]
    return "".join(f"@font-face{{font-family:'{n}';font-weight:{w};font-style:{s};src:url('{f}/{file}.woff2') format('woff2');}}" for n, w, s, file in faces)


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
.top .t { font-size: 22pt; white-space: nowrap; }
.top .tag { flex: none; white-space: nowrap; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.top.slim .t { font-size: 18pt; }
.top.slim .t small { font-size: 11pt; margin-top: 3pt; }
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 9pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.34; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3.5pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; margin: 6pt 0; }
.box h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 0 0 3pt; letter-spacing: .02em; }
.box p { margin: 0 0 4pt !important; font-size: 10.4pt !important; }
.cols { display: flex; gap: 12pt; }
.cols .box { flex: 1; margin: 6pt 0; }
.steps { display: flex; flex-direction: column; gap: 7pt; margin: 4pt 0 2pt; }
.step { display: flex; gap: 9pt; align-items: flex-start; border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt 8pt; }
.step .n { flex: none; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 13pt; border-radius: 50%; width: 22pt; height: 22pt; line-height: 22pt; text-align: center; }
.step p { margin: 0 0 3pt !important; font-size: 10.6pt !important; line-height: 1.3 !important; }
.pt { white-space: nowrap; }
.nd { display: flex; justify-content: flex-end; gap: 22pt; font-size: 10pt; margin: 6pt 0 2pt; }
.nd span { display: inline-block; }
.nd i { display: inline-block; border-bottom: .9pt solid #000; width: 120pt; height: 9pt; margin-left: 4pt; }
.sysbox { margin: 4pt 0 0; }
.pcards { display: flex; gap: 10pt; margin-top: 8pt; }
.pcard { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 8pt 3pt; }
.pcard h4 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; margin: 0 0 2pt; letter-spacing: .03em; }
.pcard h4 b { color: ACCENT; }
.pcard p { font-size: 9.2pt !important; line-height: 1.28 !important; margin: 0 0 3pt !important; }
.pcard .st { font-family: 'Oswald'; font-weight: 500; font-size: 8.6pt; letter-spacing: .03em; color: #333; }
.syt td.sy { text-align: center; padding: 2pt 4pt !important; }
.syt td.sy svg { margin: 0 auto; }
.syt td { padding: 2pt 6pt !important; font-size: 9.8pt !important; }
.syt td.sd { font-family: 'Oswald'; font-weight: 700; font-size: 14pt; letter-spacing: .02em; text-align: center; }
.icrow { display: flex; gap: 12pt; margin-top: 4pt; }
.icrow .ib { flex: 1; text-align: center; border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 8pt 3pt; }
.icrow .ib svg { margin: 0 auto 3pt; }
.icrow .ib h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11.5pt; margin: 0 0 2pt; letter-spacing: .02em; }
.icrow .ib p { font-size: 9.6pt !important; line-height: 1.28 !important; margin: 0 0 3pt !important; text-align: left; }
.kgrid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 7pt; margin: 3pt 0 2pt; }
.kgrid.k4 { grid-template-columns: repeat(4, 1fr); }
.kc { border: 1.1pt solid #000; border-radius: 6pt; padding: 4pt 7pt 2pt; text-align: center; }
.kc .kv { height: 46pt; display: flex; align-items: center; justify-content: center; }
.kc h3 { font-family: 'Oswald'; font-weight: 700; text-transform: none; font-size: 10pt; margin: 1pt 0 1pt; letter-spacing: .01em; }
.kc p { font-size: 9pt !important; line-height: 1.25 !important; margin: 0 0 2pt !important; }
.kc .sd { font-family: 'Oswald'; font-weight: 700; font-size: 11pt; }
.kc.ks .kv { height: 34pt; }
.kc.ks p { text-align: left; }
.blank td { height: 38pt; }
.blank td.rl { font-family: 'Oswald'; font-weight: 500; font-size: 10pt; text-transform: uppercase; letter-spacing: .04em; width: 62pt; }
.cb { display: inline-block; width: 11pt; height: 11pt; border: 1.2pt solid #000; border-radius: 2pt; vertical-align: -2pt; margin-right: 6pt; }
.chk td { height: 25pt; }
.chk td.cc { text-align: center; }
.lines p { border-bottom: .9pt solid #000; height: 25pt; margin: 0 0 4pt !important; font-size: 10pt !important; }
.rub td { height: 40pt; font-size: 9.6pt !important; line-height: 1.25; }
.rub td.sk { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10pt !important; letter-spacing: .03em; width: 94pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 40pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 70pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title><style>{font_css()}{CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"

# ------------------------------------------------------------------ page numbers (single source of truth)
(P_COVER, P_TEACH, P_SAFE, P_KEY, P_KEY2, P_LAYER, P_SCORE) = 1, 2, 3, 4, 5, 6, 7
P_G1 = 8                       # grooves on pages 8-13
P_PLAN, P_RUBRIC, P_TERMS = P_G1 + N_GROOVES, P_G1 + N_GROOVES + 1, P_G1 + N_GROOVES + 2
TOTAL_PAGES = P_TERMS


def gpage(n):
    return P_G1 + n - 1


PAGE_NAMES = {P_COVER: "cover", P_TEACH: "Teacher notes", P_SAFE: "Safety and setup", P_KEY: "Notation key", P_KEY2: "Notation key: staff and hands", P_LAYER: "Layering activity",
              P_SCORE: "Sample score", P_PLAN: "Ensemble planner", P_RUBRIC: "Rubric and score sheet", P_TERMS: "Terms of use"}
for _g in GROOVES:
    PAGE_NAMES[gpage(_g["n"])] = f'Groove {_g["n"]}: {_g["name"]}'
SHORT = {P_SAFE: "safety and setup page", P_KEY: "notation key", P_LAYER: "layering activity", P_SCORE: "sample score", P_PLAN: "ensemble planner",
         P_RUBRIC: "rubric and score sheet"}
XREFS = []


def xref(frm, to):
    text = f"{SHORT[to]} (pages {P_KEY}–{P_KEY2})" if to == P_KEY else f"{SHORT[to]} (page {to})"
    XREFS.append((frm, to, text))
    return text


def groove_pages_text():
    return f"{gpage(1)}–{gpage(N_GROOVES)}"


STEPS = [("Say it and pat it", "The whole class says Part 1 from its say-it line while patting knees in the order of the hand letters. Then do the same with Part 2 and with Part 3, one part at a time."),
         ("Bass starts", "Each ensemble counts in \"1 2 3 4\" and the Bass player plays Part 1 alone for two passes through the four bars."),
         ("Groove joins", "The Bass player keeps going. The Groove player comes in on beat 1 of the next pass. Play two passes with two parts."),
         ("Sparkle joins", "The Sparkle player comes in on beat 1 of the next pass. Play two passes with all three parts, then everyone stops together at the end of bar 4.")]
STEP_TICK = ["We can say and pat every part.", "The Bass player plays alone with a steady beat.", "The Groove player joins and the beat stays steady.",
             "The Sparkle player joins and we stop together."]
PASSES = {2: 2, 3: 2, 4: 2}     # passes through the four bars for steps 2, 3 and 4
TOTAL_PASSES = sum(PASSES.values())
TOTAL_BARS = TOTAL_PASSES * BARS
LAYER_BPM = 70
SECONDS = round(TOTAL_BARS * BEATS * 60 / LAYER_BPM / 10) * 10      # whole 10 seconds
ROUNDS = 4


def step_ref(n):
    return f"Step {n} ({STEPS[n - 1][0]})"


def wm_div(on):
    return '<div class="wm">PREVIEW</div>' if on else ""


def top_block(sub, tag, tagline, ak=False, slim=False):
    return (f'<div class="top{" slim" if slim else ""}"><div class="h t">{TITLE}<small>{sub}</small></div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')


def name_date():
    return '<div class="nd"><span>Name<i></i></span><span>Date<i></i></span></div>'


def sysbox(svg):
    return f'<div class="sysbox">{svg}</div>'


def staves_for(g, hide=()):
    return [{"part": i + 1, "name": PART_NAMES[i], "bars": g["parts"][i]} for i in range(3)]


# ------------------------------------------------------------------ pages
def cover_art_img(height):
    return f'<img src="../art/hero.png" alt="" style="display:block;height:{height};width:auto">'


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="height:5.1in;display:flex;align-items:center;justify-content:center">{cover_art_img("5.1in")}</div>'
            f'<div class="ctitle"><div class="a">WINTER</div><div class="b">BUCKET DRUMMING</div>'
            f'<div class="c">Six original play-along grooves · layering activity · notation key</div></div>'
            f'<div class="cband">Grades 3–8 <em>·</em> {N_GROOVES} grooves <em>·</em> {N_PARTS} parts <em>·</em> {TOTAL_PAGES} pages</div></section>')


def teacher_page(wm=False):
    pace = [("Session 1", "Safety and setup, then the notation key. Say it and pat it: all three parts of Groove 1.", f"{P_SAFE}–{P_KEY2}, {gpage(1)}"),
            ("Session 2", "Layering activity with the sample score. Ensembles build Groove 1 one part at a time and rotate roles, then try Groove 2.", f"{P_LAYER}–{P_SCORE}, {gpage(1)}–{gpage(2)}"),
            ("Session 3", "Grooves 3 and 4 in ensembles. Each ensemble fills in the planner.", f"{gpage(3)}–{gpage(4)}, {P_PLAN}"),
            ("Session 4", "Grooves 5 and 6, which add sixteenth notes to Part 2. Ensembles perform a groove for the class and the teacher uses the rubric.", f"{gpage(5)}–{gpage(6)}, {P_RUBRIC}")]
    prow = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in pace)
    return (f'<section class="page doc">{wm_div(wm)}<div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} · {N_GROOVES} grooves · {N_PARTS} parts · grades 3–8</div></div>'
            f'<p><b>What this is.</b> Six original four-bar bucket-drumming grooves in 4/4. Every groove is written as three parts that layer: Part 1 Bass is low and steady, '
            f'Part 2 Groove is the main pattern, and Part 3 Sparkle adds rim clicks and rests. Students say each rhythm with syllables, pat it, and then play it on buckets, adding one part at a time until an ensemble plays all three together. '
            f'Grooves 1 to 4 use quarter notes, quarter rests, half notes and eighth notes. Grooves 5 and 6 add sixteenth notes to Part 2. All the rhythms are original, so no tune is used.</p>'
            f'<p><b>Getting ready.</b> You need a plastic bucket for each student or each pair, sticks or just hands, and a flat floor with room to spread out. '
            f'Read the {xref(P_TEACH, P_SAFE)} first, then teach the {xref(P_TEACH, P_KEY)}. Each groove has its own chart on pages {groove_pages_text()} with the three parts stacked, so the bars line up. '
            f'The {xref(P_TEACH, P_LAYER)} and the {xref(P_TEACH, P_SCORE)} show how to build a groove one part at a time. '
            f'Ensembles of 3 or 4 students fill in the {xref(P_TEACH, P_PLAN)}, and the {xref(P_TEACH, P_RUBRIC)} records what each student can play.</p>'
            f'<h2>Suggested pacing: 4 sessions</h2><table><tr><th style="width:56pt">When</th><th>Focus</th><th style="width:76pt">Pages</th></tr>{prow}</table>'
            f'<h2>Differentiation</h2><ul>'
            f'<li><b>Grades 3–5.</b> Begin each session by saying and patting the parts on knees before any buckets come out. Use Parts 1 and 2 for Grooves 1 to 4, and add Part 3 once the class keeps a steady beat. '
            f'Leave out the accents at first, play with hands instead of sticks, and keep the tempo slow. Grooves 5 and 6 are a stretch goal for this age.</li>'
            f'<li><b>Grades 6–8.</b> Play all three parts from the start and rotate so every student plays every part. Add the sixteenth notes in Grooves 5 and 6, and ask ensembles to play from memory after two passes. '
            f'Challenge them to change the dynamics, for example soft for the first pass and loud for the last.</li></ul>'
            f'<h2>Assessment</h2><p>The {xref(P_TEACH, P_RUBRIC)} has two parts. Part A counts how many of the {N_PARTS} parts ({N_GROOVES} grooves with three parts each) a student plays correctly. '
            f'Part B rates four skills on a 3-point scale for a total of 12 points. Listen to each ensemble during Session 4 and score what you hear.</p>'
            f'<p class="small">No standards codes are cited, so please match the activities to the standards your school uses. No songs, lyrics or copyrighted characters are used. '
            f'The file has {TOTAL_PAGES} pages: page 1 cover, page 2 these notes, page {P_SAFE} safety and setup, pages {P_KEY}–{P_KEY2} notation key, page {P_LAYER} layering activity, page {P_SCORE} sample score, '
            f'pages {groove_pages_text()} the groove charts, page {P_PLAN} planner, page {P_RUBRIC} rubric and page {P_TERMS} terms.</p>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 2")}</section>')


def safety_page(wm=False):
    return (f'<section class="page doc">{wm_div(wm)}<div class="rule"><h1>Safety and Setup</h1>'
            f'<div class="l" style="font-size:13pt">Care of the buckets, protecting hearing, and where to play</div></div>'
            f'<p>Bucket drums get loud quickly, so agree on the rules before the first bucket is handed out.</p>'
            f'<div class="cols"><div class="box"><h3>Clean, safe buckets</h3><p>Use clean plastic buckets with no cracks and no sharp edges. Wash and dry them before the first session, and never use a bucket that held paint or chemicals. '
            f'Run a hand around each rim and tape over any rough spot. Plastic buckets are quieter than metal ones. A snap-on lid gives a clearer click on the rim. Take off or tape down any metal handle so it does not rattle.</p></div>'
            f'<div class="box"><h3>Protect hearing</h3><p>Loud sounds can damage hearing. Keep the volume low enough that students can still talk to each other between rounds. '
            f'Agree on a stop signal, such as a raised hand, and stop at once when you see it. Play short rounds of one or two minutes and rest between them. '
            f'Never hold a bucket near an ear. If the room is too loud, play more softly or use a larger space.</p></div></div>'
            f'<div class="cols"><div class="box"><h3>Sticks or hands</h3><p>Smooth wooden or plastic sticks work well. Hands are a good choice for younger students and for a quiet start. '
            f'Sticks only touch the bucket: they are never swung toward people or other buckets, and they go on the floor whenever the teacher is talking. Leave a stick length of space between ensembles.</p></div>'
            f'<div class="box"><h3>Setting up</h3><p>Turn each bucket upside down on a flat floor or a mat so it cannot tip. Sit on a chair or the floor with the bucket in front of you, and never set a bucket on a desk. '
            f'Put the Bass bucket, the Groove bucket and the Sparkle bucket of an ensemble close together so the players can see and hear each other.</p></div></div>'
            f'<h2>Where to play on the bucket</h2>'
            f'<div class="icrow">'
            f'<div class="ib">{bucket_icon("center", "bk-center")}<h3>Center</h3><p>A low, round sound. Part 1 Bass plays in the center of the bucket.</p></div>'
            f'<div class="ib">{bucket_icon("between", "bk-between")}<h3>Between center and edge</h3><p>A middle sound. Part 2 Groove plays here, halfway between the center and the edge.</p></div>'
            f'<div class="ib">{bucket_icon("rim", "bk-rim")}<h3>Rim click</h3><p>A light click, written with an x notehead. Part 3 Sparkle taps the rim with the tip of a stick or a fingertip.</p></div></div>'
            f'<h2>Quick rules for students</h2><ul>'
            f'<li>Play only when the Conductor or the teacher has counted in "1 2 3 4".</li>'
            f'<li>Stop playing at once on the stop signal, and put sticks down on the floor.</li>'
            f'<li>Play with a relaxed hand and let the stick bounce. Do not hit hard.</li>'
            f'<li>Listen to the other parts. If you cannot hear them, play more softly.</li>'
            f'<li>At the end, wipe the buckets, stack them, and count the sticks before anyone leaves.</li></ul>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_SAFE}")}</section>')


KEY_ROWS = [  # (tokens, name, beats, say)
    ("ta", "Quarter note", "1 beat", "ta"),
    ("shh", "Quarter rest (silence)", "1 beat", "shh"),
    ("ti-ti", "Two eighth notes, joined by one beam", "1 beat together", "ti-ti"),
    ("ta-a", "Half note (open notehead)", "2 beats", "ta-a"),
    ("ti-ka-ti-ka", "Four sixteenth notes, joined by two beams", "1 beat together", "ti-ka-ti-ka"),
    ("ti-ti-ka", "Eighth note, then two sixteenth notes", "1 beat together", "ti-ti-ka"),
    ("ti-ka-ti", "Two sixteenth notes, then an eighth note", "1 beat together", "ti-ka-ti"),
    ("ta>", "Accent: a quarter note played louder", "1 beat", "ta (louder)"),
    ("ta*", "Rim click: an x notehead, tap the rim", "1 beat", "ta (click)"),
]
EX_KEYS = [("key-ex1", "ta> ti-ti ta shh", "An accent on beat 1 and a rest on beat 4."),
           ("key-ex2", "ti-ka-ti-ka ta ti-ti-ka ta", "Sixteenth notes: say ti-ka-ti-ka, ta, ti-ti-ka, ta."),
           ("key-ex3", "shh ta* shh ta*", "Rim clicks (x) fall on beats 2 and 4. Rests fill beats 1 and 3, so Part 3 stays light.")]
KEY_STRUCT = [("clef", "Neutral clef", "Two short bars: this staff is for rhythm, so there are no pitches and every note sits on the one line."),
              ("ts", "Time signature 4/4", "Four beats in each bar, and a quarter note gets one beat."),
              ("bar", "Barline", "Marks the end of a bar. Every bar in this resource has four beats."),
              ("fin", "Final barline", "A thin and a thick line: the groove ends here.")]


def keyid(tok):
    return tok.replace(">", "-accent").replace("*", "-rim")


def ex_svg(uid, bar):
    return system_svg(uid, [{"bars": [bar], "part": 0, "name": ""}], 0, 1, mode="ex", W=228.0, S=5.4, counts=True, fh=8.2, fs=6.8)


def key_page(wm=False):
    cards = ""
    for tok, name, beats, say in KEY_ROWS:
        nbeat = int(token_beats(tok.rstrip(">*")))
        svg = system_svg(f"key-{keyid(tok)}", [{"bars": [tok]}], 0, 1, mode="sym", S=5.0, bl=nbeat, groove=0, sym_u=36.0)
        cards += (f'<div class="kc"><div class="kv">{svg}</div><h3>{name}</h3><p><b>Length:</b> {beats}<br><b>Say it:</b> <span class="sd">{say}</span></p></div>')
    exs = "".join(f'<div class="box"><h3>Reading a bar</h3>{ex_svg(u, b)}<p>{d}</p></div>' for u, b, d in EX_KEYS[:2])
    return (f'<section class="page doc">{wm_div(wm)}{top_block("Notation key", "KEY", "Notes and rests", slim=True)}{name_date()}'
            f'<p style="margin-top:2pt">A bar of 4/4 holds four beats. Every note sits on the one line of the staff.</p>'
            f'<h2 style="margin-top:2pt">Notes and rests</h2><div class="kgrid">{cards}</div>'
            f'<h2>Add up a bar</h2><p>A half note is 2 beats, so a half note plus two quarter notes makes 4. Two eighth notes make 1 beat, and so do four sixteenth notes.</p><div class="cols">{exs}</div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_KEY}")}</section>')


def key2_page(wm=False):
    scards = "".join(f'<div class="kc ks"><div class="kv">{glyph_svg(f"key-{k}", k, 5.0)}</div><h3>{n}</h3><p>{d}</p></div>' for k, n, d in KEY_STRUCT)
    u, b, d = EX_KEYS[2]
    trows = [("Part 1 Bass", "Low and steady", "Quarter notes, half notes and quarter rests; some accents", "Center of the bucket"),
             ("Part 2 Groove", "The main pattern", "Quarter notes, eighth notes and rests; sixteenth notes in Grooves 5 and 6", "Between center and edge"),
             ("Part 3 Sparkle", "Rim clicks and rests", "Only x noteheads and rests", "Rim of the bucket")]
    prow = "".join(f"<tr><td><b>{a}</b></td><td>{b_}</td><td>{c}</td><td>{d_}</td></tr>" for a, b_, c, d_ in trows)
    return (f'<section class="page doc">{wm_div(wm)}{top_block(PAGE_NAMES[P_KEY2], "KEY", "Staff, hands and parts", slim=True)}{name_date()}'
            f'<h2 style="margin-top:2pt">Staff and bar symbols</h2><div class="kgrid k4">{scards}</div>'
            f'<div class="cols"><div class="box"><h3>Hand letters</h3><p>R is the right hand and L is the left hand. A letter sits under every note. Hands alternate R, L, R, L from the first note of bar 1 to the end of bar 4, '
            f'and a rest does not change whose turn it is. No letter sits under a rest.</p></div>'
            f'<div class="box"><h3>Stems and beams</h3><p>On this one-line staff every stem points up and sits on the right side of its notehead. One beam joins eighth notes and two beams join sixteenth notes. '
            f'The say-it line under the letters gives the syllables for each beat.</p></div></div>'
            f'<h2>The three parts</h2><table class="syt"><tr><th style="width:84pt">Part</th><th style="width:96pt">Job</th><th>What you will see</th><th style="width:96pt">Where to play</th></tr>{prow}</table>'
            f'<h2>Reading a bar with rim clicks</h2>'
            f'<div class="cols"><div class="box"><h3>Reading a bar</h3>{ex_svg(u, b)}<p>{d}</p></div><div class="box"><h3>Check your count</h3><p>Count "1 2 3 4" out loud and tap the beat on your knee while you say the syllables. Each syllable lines up with the beat number above it. If a bar feels uneven, slow down and say the syllables before you play.</p></div></div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_KEY2}")}</section>')


def layer_page(wm=False):
    srows = "".join(f'<div class="step" data-step="{i + 1}"><span class="n">{i + 1}</span><div><p><b>{n}.</b> {d}</p></div></div>' for i, (n, d) in enumerate(STEPS))
    rr = "".join(f'<tr data-step="{s}"><td><b>{step_ref(s)}</b></td><td>{who}</td><td>{PASSES[s]} passes</td><td>{PASSES[s] * BARS} bars</td></tr>'
                 for s, who in ((2, "Part 1 Bass"), (3, "Part 1 Bass and Part 2 Groove"), (4, "Parts 1, 2 and 3")))
    return (f'<section class="page doc">{wm_div(wm)}{top_block("Layering activity", "ACTIVITY", "Build it one part at a time", slim=True)}'
            f'<p style="margin-top:8pt">Every groove has three parts that fit together like layers. Part 1 Bass is the low, steady base. Part 2 Groove is the main pattern. Part 3 Sparkle puts rim clicks and rests on top. '
            f'All three parts are in 4/4 and all have {BARS} bars, so they line up beat for beat. The {xref(P_LAYER, P_SCORE)} shows how.</p>'
            f'<h2>Four steps</h2><div class="steps">{srows}</div>'
            f'<h2>Build map</h2><table class="bm"><tr><th>When</th><th>Who plays</th><th style="width:60pt">Length</th><th style="width:60pt">Bars</th></tr>{rr}</table>'
            f'<p class="small">One pass is the four bars of the groove. Steps 2 to 4 are {TOTAL_PASSES} passes, or {TOTAL_BARS} bars. At about {LAYER_BPM} beats per minute that takes about {SECONDS} seconds.</p>'
            f'<div class="cols"><div class="box"><h3>Ensembles of 3 or 4</h3><p>Put students in ensembles of 3 or 4. Each ensemble has a <b>Bass</b> player, a <b>Groove</b> player and a <b>Sparkle</b> player. '
            f'In an ensemble of 4 the fourth student is the <b>Conductor</b>, who counts in "1 2 3 4", keeps the beat softly on a knee and gives the stop signal. In an ensemble of 3 the Bass player counts in.</p></div>'
            f'<div class="box"><h3>Swap and repeat</h3><p>After each build, rotate roles so every student plays every part. An ensemble of 4 takes {ROUNDS} rounds, and an ensemble of 3 takes 3. '
            f'Use the {xref(P_LAYER, P_PLAN)} to record who played what. If the layers fall apart, go back one step. Quiet and steady beats loud and fast.</p></div></div>'
            f'<div class="box"><h3>Cues that help</h3><p>The player who is about to enter gives a clear nod on beat 4 of the last bar of the pass before. Count in out loud for the first pass, and count silently in your head for the passes after that.</p></div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_LAYER}")}</section>')


def moment_sentence(g, bar, beat):
    """Plain-English line about what each part does at one beat of one bar, computed from the data."""
    st = []
    for pi in range(3):
        ev, _, _ = part_events(g["parts"][pi])
        t = Fraction((bar - 1) * BEATS + (beat - 1))
        cur = [e for e in ev if e["t"] <= t < e["t"] + e["dur"]]
        e = cur[0]
        st.append("rests" if e["kind"] == "r" else ("holds" if e["t"] < t else "plays"))
    return st


def join_parts(names_verbs):
    items = [f"{n} {v}" for n, v in names_verbs]
    return ", ".join(items[:-1]) + " and " + items[-1]


SCORE_MOMENTS = [(1, 1), (1, 2), (4, 3)]


def score_page(wm=False):
    g = GROOVES[0]
    svg = system_svg("score-g1", staves_for(g), 0, BARS, mode="full", S=6.0, W=540.0, guides=True, counts=True, fh=7.8, fs=6.8, groove=0)
    lines = ""
    for bar, beat in SCORE_MOMENTS:
        sts = moment_sentence(g, bar, beat)
        lines += (f'<li data-bar="{bar}" data-beat="{beat}" data-st="{",".join(sts)}"><b>Bar {bar}, beat {beat}:</b> '
                  f'{join_parts(list(zip(PART_NAMES, sts)))}.</li>')
    srows = "".join(f'<tr><td><b>{step_ref(s)}</b></td><td>{who}</td></tr>' for s, who in ((2, "Bass plays alone"), (3, "Bass plays and Groove joins"), (4, "Bass and Groove play and Sparkle joins")))
    return (f'<section class="page doc">{wm_div(wm)}{top_block("Sample score", "SCORE", f"Groove 1 stacked", slim=True)}'
            f'<p style="margin-top:8pt">A score stacks the parts so that notes that sound at the same moment sit straight above one another. Read left to right to follow the time, '
            f'and read straight down to see what everyone plays at once. The bars, the counts and the beats line up in all three parts. This sample is Groove 1, {GROOVES[0]["name"]}.</p>'
            f'{sysbox(svg)}'
            f'<h2>Read straight down</h2><ul class="mom">{lines}</ul>'
            f'<h2>Build it with this score</h2>'
            f'<table class="bm"><tr><th style="width:150pt">When</th><th>What the ensemble plays</th></tr>{srows}</table>'
            f'<div class="box"><h3>Try it</h3><p>Point at the score and follow one beat at a time while the teacher counts "1 2 3 4" slowly. When one part rests, listen for the parts that are still playing.</p></div>'
            f'<p class="small">Hands alternate on every note, and the pattern carries on across barlines and through rests. The dashed guide lines mark the beats. The same layout is used for every groove on pages {groove_pages_text()}.</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_SCORE}")}</section>')


def groove_page(g, wm=False):
    n = g["n"]
    page = gpage(n)
    st = staves_for(g)
    sys1 = system_svg(f"g{n}-s1", st, 0, 2, mode="full", S=5.6, final=False, show_ts=True, counts=True, groove=n)
    sys2 = system_svg(f"g{n}-s2", st, 2, 2, mode="full", S=5.6, final=True, show_ts=False, counts=True, groove=n)
    cards = ""
    wh = ["Play in the center of the bucket for a low, round sound.", "Play between the center and the edge for a middle sound.", "Tap the rim with a stick tip or a fingertip. Rests are silent."]
    for pi in range(3):
        s = part_stats(g["parts"][pi])
        cards += (f'<div class="pcard" data-groove="{n}" data-part="{pi + 1}" data-notes="{s["notes"]}" data-rests="{s["rests"]}" data-acc="{s["acc"]}" data-rim="{s["rim"]}">'
                  f'<h4><b>Part {pi + 1}</b> {PART_NAMES[pi]}</h4><p>{wh[pi]}</p><div class="st">{stats_text(s)}</div></div>')
    return (f'<section class="page doc">{wm_div(wm)}{top_block(PAGE_NAMES[page], f"GROOVE {n}", f"{BARS} bars of 4/4 · {N_GROOVES} grooves", slim=True)}{name_date()}'
            f'<div class="sysbox">{sys1}</div><div class="sysbox" style="margin-top:6pt">{sys2}</div>'
            f'<div class="pcards">{cards}</div>'
            f'<p class="small" style="margin-top:7pt">Start at about {g["bpm"]} beats per minute. Say it and pat it first, then play. Hands alternate on every note and carry on through the rests. '
            f'Build the groove with the {xref(page, P_LAYER)}.</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {page}")}</section>')


def plan_page(wm=False):
    rr = "".join(f'<tr><td class="rl">Round {i + 1}</td><td></td><td></td><td></td><td></td></tr>' for i in range(ROUNDS))
    ck = "".join(f'<tr><td><span class="cb"></span><b>{step_ref(i + 1)}.</b> {STEP_TICK[i]}</td></tr>' for i in range(len(STEPS)))
    return (f'<section class="page doc">{wm_div(wm)}{top_block("Ensemble planner", "STUDENT PAGE", "For ensembles of 3 or 4", slim=True)}{name_date()}'
            f'<p style="margin-top:4pt"><b>Our groove</b> (circle one): 1 2 3 4 5 6 &nbsp;&nbsp;&nbsp; <b>Our ensemble name:</b> ______________________________</p>'
            f'<h2>Who plays what</h2>'
            f'<table class="blank"><tr><th style="width:62pt">When</th><th>Bass</th><th>Groove</th><th>Sparkle</th><th>Conductor</th></tr>{rr}</table>'
            f'<p class="small">Write a name in each box and rotate roles after every round. Ensembles of 3 have no Conductor and use Rounds 1 to 3.</p>'
            f'<h2>Our build</h2><table class="chk">{ck}</table>'
            f'<p class="small">Tick each step when your whole ensemble can do it with a steady beat.</p>'
            f'<h2>Our plan</h2><div class="lines"><p>Our tempo (beats per minute):</p><p>How we count in:</p><p>How we stop together:</p><p>Our groove is ready when:</p><p>One thing we will do better next time:</p></div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_PLAN}")}</section>')


RUBRIC = [("Steady beat", "The beat speeds up or slows down a lot.", "The beat is mostly steady with a few wobbles.", "The beat stays steady from the count-in to the stop."),
          ("Rhythm matches the chart", "Several bars do not match the chart.", "Most bars match the chart.", "Every bar matches the chart."),
          ("Hands alternate as written", "Hands do not follow the R and L letters.", "Hands follow the letters most of the time.", "Hands follow the letters all the way through."),
          ("Listens and blends", "Plays over the other parts or loses place.", "Usually keeps in time with the other parts.", "Fits the layers together and keeps the balance.")]
RUBRIC_MAX = 3 * len(RUBRIC)


def rubric_page(wm=False):
    grid = ""
    for g in GROOVES:
        cells = "".join('<td class="cc"><span class="cb" style="margin:0"></span></td>' for _ in range(3))
        grid += f'<tr><td><b>Groove {g["n"]}:</b> {g["name"]}</td>{cells}</tr>'
    rub = "".join(f'<tr><td class="sk">{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in RUBRIC)
    return (f'<section class="page doc">{wm_div(wm)}{top_block("Rubric and score sheet", "ASSESSMENT", "Teacher use", slim=True)}{name_date()}'
            f'<h2>Part A: Parts played correctly</h2>'
            f'<table class="chk"><tr><th>Groove</th><th style="width:78pt">Part 1 Bass</th><th style="width:78pt">Part 2 Groove</th><th style="width:78pt">Part 3 Sparkle</th></tr>{grid}</table>'
            f'<p><b>Total parts played correctly: ______ out of {N_PARTS}</b></p>'
            f'<h2>Part B: Ensemble skills</h2>'
            f'<table class="rub"><tr><th>Skill</th><th>1 Not yet</th><th>2 Getting there</th><th>3 Got it</th></tr>{rub}</table>'
            f'<p><b>Rubric total: ______ out of {RUBRIC_MAX}</b></p>'
            f'<p class="small">Circle one score for each skill and add the four scores. Tick a part in Part A when the student plays it correctly with a steady beat.</p>'
            f'<h2>Notes</h2><div class="lines"><p></p><p></p></div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_RUBRIC}")}</section>')


def terms_page(wm=False):
    return (f'<section class="page doc">{wm_div(wm)}<div class="rule"><h1>Terms of Use</h1><div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>The grooves, charts, notation and activities are original work, {BRAND} by {STORE}.</li>'
            f'<li>Cover artwork: an illustration made with AI tools. The notation, charts and text are drawn in code.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>What is in this file</h2><p>Page 1 cover, page 2 teacher notes, page {P_SAFE} safety and setup, pages {P_KEY}–{P_KEY2} notation key, page {P_LAYER} layering activity, page {P_SCORE} sample score, '
            f'pages {groove_pages_text()} the {N_GROOVES} groove charts, page {P_PLAN} ensemble planner, page {P_RUBRIC} rubric and score sheet and page {P_TERMS} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p><div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def full_pages():
    XREFS.clear()
    pages = ([cover_page(), teacher_page(), safety_page(), key_page(), key2_page(), layer_page(), score_page()] + [groove_page(g) for g in GROOVES]
             + [plan_page(), rubric_page(), terms_page()])
    assert len(pages) == TOTAL_PAGES, len(pages)
    return pages


PREVIEW_PAGES = [P_KEY, P_LAYER, P_SCORE, gpage(3)]


def preview_pages():
    fn = {P_KEY: key_page, P_LAYER: layer_page, P_SCORE: score_page, gpage(3): lambda wm: groove_page(GROOVES[2], wm)}
    return [fn[p](True) for p in PREVIEW_PAGES]


# ------------------------------------------------------------------ square images
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
       color: rgba(0,0,0,.13); white-space: nowrap; letter-spacing: .06em; pointer-events: none; z-index: 5; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:#fff;font-family:"Source Sans 3",sans-serif}}{SQ_CSS}</style></head><body>'
            f'{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="height:580px;display:flex;align-items:center">{cover_art_img("580px")}</div>'
        f'<div><div class="hd" style="font-size:64px">Winter</div><div class="hd" style="font-size:106px">Bucket Drumming</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">Six original play-along grooves · layering activity</div></div>'
        f'</div><div class="band">Grades 3–8 <em>·</em> {N_GROOVES} grooves <em>·</em> {N_PARTS} parts <em>·</em> {TOTAL_PAGES} pages</div></div>')


def swm_over(size=230):
    return f'<div class="swm" style="font-size:{size}px">PREVIEW</div>'


def shot(src, w):
    return f'<div class="shot" style="width:{w}px"><img src="{src}"></div>'


def preview_square_1(img):
    caps = [(PAGE_NAMES[P_KEY], "Every symbol defined"), (PAGE_NAMES[gpage(5)], "Play-along chart with say-it line"), (PAGE_NAMES[P_SCORE], "Three parts stacked and aligned")]
    shots = "".join(
        f'<div style="width:290px;display:flex;flex-direction:column;align-items:center">{shot(img[i], 290)}'
        f'<div class="lbl" style="font-size:24px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:20px;line-height:1.25;text-align:center;margin-top:8px;width:270px">{caps[i][1]}</div></div>' for i in range(3))
    pills = "".join(f'<div style="border:2px solid #000;border-radius:30px;padding:6px 22px;font-family:Oswald;font-weight:500;font-size:24px;letter-spacing:.06em;text-transform:uppercase">{t}</div>'
                    for t in (f"{N_GROOVES} grooves", f"{N_PARTS} parts", "notation key"))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">What is inside</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">Charts, a key and a layering plan</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{shots}</div><div style="display:flex;gap:18px">{pills}</div></div>'
        f'{swm_over(230)}<div class="band">Say it <em>·</em> Pat it <em>·</em> Play it <em>·</em> {TOTAL_PAGES} pages</div></div>')


def preview_square_2(a, b):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}<span>{sub}</span></div></div>'
                   for src, lab, sub in ((a, PAGE_NAMES[P_LAYER], "Four steps, one part at a time"), (b, PAGE_NAMES[P_PLAN], "For ensembles of 3 or 4")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">Layer it up</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Bass, Groove and Sparkle build into one groove</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">Part 1 <em>·</em> Part 2 <em>·</em> Part 3 <em>·</em> {N_GROOVES} grooves</div></div>')


def preview_square_3(a, b):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}<span>{sub}</span></div></div>'
                   for src, lab, sub in ((a, PAGE_NAMES[gpage(1)], "Quarter notes and eighth notes"), (b, PAGE_NAMES[gpage(6)], "Adds sixteenth notes")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">Play-along charts</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Hand letters and a say-it line under every note</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">R <em>·</em> L <em>·</em> accents <em>·</em> rim clicks <em>·</em> rests</div></div>')


# ------------------------------------------------------------------ render / build
def node_env():
    env = dict(os.environ)
    if not env.get("NODE_PATH"):
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    return env


def render(jobs):
    path = os.path.join(BUILD, "jobs.json")
    with open(path, "w") as fh:
        json.dump(jobs, fh)
    subprocess.run(["node", RENDER_JS, path], check=True, env=node_env())


def write(name, text):
    p = os.path.join(BUILD, name)
    with open(p, "w") as fh:
        fh.write(text)
    return p


PAGE_LIST = [("Cover", 1), ("Teacher notes with pacing, differentiation and assessment", 1), ("Safety and setup", 1), ("Notation key (two pages)", 2),
             ("Layering activity", 1), ("Sample score", 1), (f"Groove charts, one page per groove ({N_GROOVES} grooves, {N_PARTS} parts)", N_GROOVES),
             ("Ensemble planner", 1), ("Rubric and score sheet", 1), ("Terms of use and credits", 1)]


def upload_md():
    lst = "\n".join(f"- {n}: {c}" for n, c in PAGE_LIST)
    desc_pages = "\n".join(f"• {n} ({c} page{'s' if c != 1 else ''})" for n, c in PAGE_LIST)
    names = ", ".join(f"{g['name']}" for g in GROOVES)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 059)

These fields follow the order of TpT's "Add a resource" form. Winter theme: build window is December. Never put Winter, Holiday or Christmas in the title field (TpT's Seasonal Titles notice).

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words. If TpT accepts it, the preferred title is "{PREFERRED_TITLE}" ({len(PREFERRED_TITLE)} characters).

## 2. Description

```
Winter Bucket Drumming gives your class {N_GROOVES} original four-bar grooves for bucket drums, each written as a play-along chart on a one-line rhythm staff. Every groove has three parts that layer: Part 1 Bass (low and steady), Part 2 Groove (the main pattern) and Part 3 Sparkle (rim clicks and rests). That is {N_PARTS} parts in all, and every part has the same meter (4/4) and the same four bars, so the beats line up when you stack them. Every note has a hand letter (R or L) under it and a say-it line of rhythm syllables (ta, ti-ti, shh, ta-a), so students can say it, pat it and then play it. Grooves 1 to 4 use quarter notes, quarter rests, half notes and eighth notes, and Grooves 5 and 6 add sixteenth notes. The grooves are original, so no tune is used. For music classes in grades 3 to 8.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
{desc_pages}
Total: {TOTAL_PAGES} pages, {N_GROOVES} grooves, {N_PARTS} parts.

HOW TO USE
Start with the safety and setup page and the notation key, then teach one groove at a time. Students say and pat each part, then build the groove in ensembles of 3 or 4: Bass starts, Groove joins, Sparkle joins. The sample score shows the three parts stacked on one page so the bars line up. The pacing plan runs over 4 sessions, and the teacher notes give differentiation for grades 3-5 and grades 6-8. The ensemble planner and the rubric (total parts played correctly out of {N_PARTS}, plus a 12-point skills rubric) cover assessment.

• Grades 3–8 (all {N_GROOVES} grooves, from quarter and eighth notes to sixteenth notes)
• Safety and care notes: clean plastic buckets, sticks or hands, protecting hearing
• Notation key that defines every symbol used: notes, rests, accents, rim clicks, hand letters
• Prints well in black and white

{DISCLOSURE}
```

## 3. Grades

TpT's form takes at most 4 grades, so `tpt.json` lists 3rd, 4th, 5th and 6th grade (the core age for bucket drumming). The listing text and the cover say grades 3-8 because the resource also includes upper-middle-school differentiation (grades 6-8) and the sixteenth-note grooves 5 and 6. If the form allows more, add 7th and 8th.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

{lst}
- Total: {TOTAL_PAGES}

Grooves: {names}.

## 6. Standards

None cited. The teacher notes ask teachers to match the activities to the standards their school uses.

## 7. Price

**${PRICE}** (paid; owner range $3-5).

## 8. Preview

Paid. Preview PDF: notation key (page {P_KEY}), layering activity (page {P_LAYER}), sample score (page {P_SCORE}) and {PAGE_NAMES[gpage(3)]} (page {gpage(3)}), all watermarked.

## 9. Before you click publish

- [ ] Season: December (build window 2 to 8 weeks ahead).
- Art: cover illustration made with AI tools (disclosure line covers it; library subject bucket-drums); notation, charts, icons and text are drawn in code.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS,
            "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Not included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in (P_KEY, P_LAYER, P_SCORE, gpage(1), gpage(5), gpage(6), P_PLAN):      # clean (unwatermarked) page shots from the product PDF
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(i), "-l", str(i), "-singlefile", PDF, os.path.join(BUILD, f"pg{i}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1([f"pg{P_KEY}.png", f"pg{gpage(5)}.png", f"pg{P_SCORE}.png"])),
          write("p2.html", preview_square_2(f"pg{P_LAYER}.png", f"pg{P_PLAN}.png")),
          write("p3.html", preview_square_3(f"pg{gpage(1)}.png", f"pg{gpage(6)}.png"))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as fh:
        fh.write(upload_md())
    with open(TPT_JSON, "w") as fh:
        json.dump(tpt_json(), fh, indent=2)
        fh.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


# ------------------------------------------------------------------ checks
NS = "{http://www.w3.org/2000/svg}"
SVG_RE = re.compile(r'<svg class="(?:ns|ic)".*?</svg>', re.S)


def parse_svg(txt):
    return ET.fromstring(txt)


def f(el, k, d=0.0):
    return float(el.get(k, d))


def cp_of(el):
    return ord((el.text or "?")[0])


_GLYPH = {}


def glyph_box(cp):
    """Ink box of a Bravura glyph in staff spaces: (xmin, ymin, xmax, ymax), y up, origin at the glyph origin."""
    if not _GLYPH:
        from fontTools.ttLib import TTFont
        from fontTools.pens.boundsPen import BoundsPen
        font = TTFont(os.path.join(FONTS, "bravura.woff2"))
        gs, cm, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
        for c in (G_HEAD, G_HALF, G_X, G_QREST, G_NEUTRAL, G_TS4):
            bp = BoundsPen(gs)
            gs[cm[c]].draw(bp)
            _GLYPH[c] = tuple(v / upm * 4 for v in bp.bounds)
    return _GLYPH[cp]


def text_box(el):
    """Estimated ink box (x0, y0, x1, y1) of a non-music text element, in svg units."""
    fs = f(el, "font-size")
    txt = (el.text or "").strip()
    fam = el.get("font-family", "")
    k = 0.46 if "Oswald" in fam else 0.52
    wd = len(txt) * k * fs
    x = f(el, "x")
    anchor = el.get("text-anchor", "start")
    x0 = x - wd / 2 if anchor == "middle" else (x - wd if anchor == "end" else x)
    return (x0, f(el, "y") - 0.72 * fs, x0 + wd, f(el, "y") + 0.2 * fs)


def box_of(el):
    tag = el.tag.replace(NS, "")
    sw = f(el, "stroke-width", 0.0) if el.get("stroke") not in (None, "none") else 0.0
    if tag == "line":
        xs, ys = [f(el, "x1"), f(el, "x2")], [f(el, "y1"), f(el, "y2")]
    elif tag == "rect":
        xs, ys = [f(el, "x"), f(el, "x") + f(el, "width")], [f(el, "y"), f(el, "y") + f(el, "height")]
    elif tag == "circle":
        r = f(el, "r")
        xs, ys = [f(el, "cx") - r, f(el, "cx") + r], [f(el, "cy") - r, f(el, "cy") + r]
    elif tag in ("polygon", "polyline"):
        nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", el.get("points", ""))]
        xs, ys = nums[0::2], nums[1::2]
    elif tag == "text":
        if el.get("font-family") == "Bravura":
            S = f(el, "font-size") / 4
            x0, y0b, x1, y1b = glyph_box(cp_of(el))
            return (f(el, "x") + x0 * S, f(el, "y") - y1b * S, f(el, "x") + x1 * S, f(el, "y") - y0b * S), 0.0
        return text_box(el), 0.0
    else:
        return None, 0.0
    return (min(xs) - sw / 2, min(ys) - sw / 2, max(xs) + sw / 2, max(ys) + sw / 2), sw


def check_extent(root, label, errs):
    """Every drawn shape and glyph sits inside the viewBox with padding at least its stroke width (and at least 1 unit)."""
    vb = [float(x) for x in root.get("viewBox").split()]
    W, H = vb[2], vb[3]
    for el in root.iter():
        b, sw = box_of(el)
        if b is None:
            continue
        pad = max(sw, 1.0)
        if b[0] < pad - 1e-6 or b[1] < pad - 1e-6 or b[2] > W - pad + 1e-6 or b[3] > H - pad + 1e-6:
            errs.append(f"{label}: a {el.tag.replace(NS, '')} (stroke {sw}) is closer to the viewBox edge than max(stroke, 1)")


def overlap(a, b, gap=0.0):
    return a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap


def read_staff(st, root, errs, label, exp_bars):
    """Re-read one staff group from its geometry. Returns dict(tokens per bar, hands, syllables, counts) or None."""
    S, xb0, BW, padL, u = (f(root, k) for k in ("data-s", "data-xb0", "data-bw", "data-padl", "data-u"))
    nb, b0, bl = int(root.get("data-nb")), int(root.get("data-b0")), int(root.get("data-bl"))
    kind, final = root.get("data-kind"), root.get("data-final") == "1"
    y0 = f(st, "data-y0")
    X = lambda t: xb0 + (int(t // bl) - b0) * BW + padL + pos(t - bl * int(t // bl)) * u
    sls = [el for el in st.iter(NS + "line") if el.get("class") == "sl"]
    if len(sls) != 1 or abs(f(sls[0], "y1") - y0) > 0.02 or abs(f(sls[0], "y2") - y0) > 0.02:
        errs.append(f"{label}: expected exactly one horizontal staff line")
        return None
    if f(sls[0], "stroke-width") < 0.08 * S:
        errs.append(f"{label}: staff line too thin")
    clefs = [t for t in st.iter(NS + "text") if t.get("class") == "clef"]
    tsd = sorted((f(t, "y"), cp_of(t)) for t in st.iter(NS + "text") if t.get("class") == "tsd")
    bars = sorted(f(l, "x1") for l in st.iter(NS + "line") if l.get("class") == "bar")
    fins = [r for r in st.iter(NS + "rect") if r.get("class") == "fin"]
    if kind == "sym":
        if clefs or tsd or bars or fins:
            errs.append(f"{label}: symbol example should have no clef, time signature or barline")
    else:
        if len(clefs) != 1 or cp_of(clefs[0]) != G_NEUTRAL or abs(f(clefs[0], "y") - y0) > 0.02:
            errs.append(f"{label}: neutral clef missing or off the line")
        want_ts = root.get("data-ts") == "1" and b0 == 0
        if want_ts:
            if [c for _, c in tsd] != [G_TS4, G_TS4] or abs(tsd[0][0] - (y0 - 1.25 * S)) > 0.02 or abs(tsd[1][0] - (y0 + 1.25 * S)) > 0.02:
                errs.append(f"{label}: time signature is not 4 over 4 around the line")
        elif tsd:
            errs.append(f"{label}: unexpected time signature")
        if len(bars) != nb or len(fins) != (1 if final else 0):
            errs.append(f"{label}: expected {nb} barlines and {'one' if final else 'no'} thick final barline, found {len(bars)} and {len(fins)}")
        else:
            for b, x in enumerate(bars):
                want = xb0 + (b + 1) * BW - (0.5 * S if (final and b == nb - 1) else 0.0)
                if abs(x - want) > 0.05:
                    errs.append(f"{label}: barline {b + 1} is not at the end of its bar")
    hw0 = HEAD_W * S
    beams = [(f(r, "x"), f(r, "x") + f(r, "width"), f(r, "y"), f(r, "height")) for r in st.iter(NS + "rect") if r.get("class") == "beam"]
    evs = []
    boxes = {"head": [], "stem": [], "beam": [], "rest": [], "acc": []}
    for g in st.iter(NS + "g"):
        if g.get("class") != "ev":
            continue
        head = next((t for t in g.iter(NS + "text") if t.get("class") == "head"), None)
        rest = next((t for t in g.iter(NS + "text") if t.get("class") == "rest"), None)
        stems = [l for l in g.iter(NS + "line") if l.get("class") == "stem"]
        accs = [p for p in g.iter(NS + "polyline") if p.get("class") == "acc"]
        if rest is not None:
            if head is not None or stems or accs or cp_of(rest) != G_QREST or abs(f(rest, "y") - y0) > 0.02:
                errs.append(f"{label}: rest is not a quarter rest on the line")
            evs.append({"kind": "r", "x": f(rest, "x") + REST_W * S / 2, "acc": False, "head": "n"})
            boxes["rest"].append(box_of(rest)[0])
            continue
        if head is None or len(stems) != 1:
            errs.append(f"{label}: note without exactly one head and one stem")
            continue
        gp = cp_of(head)
        if gp not in (G_HEAD, G_HALF, G_X) or abs(f(head, "y") - y0) > 0.02:
            errs.append(f"{label}: notehead glyph or position wrong")
            continue
        hw = HW[gp] * S
        left = f(head, "x")
        sm = stems[0]
        sx, y1, y2, swd = f(sm, "x1"), f(sm, "y1"), f(sm, "y2"), f(sm, "stroke-width")
        y1want = y0 - (0.40 if gp == G_X else STEM_X) * S
        if abs(sx - (left + hw - swd / 2)) > 0.03 * S or abs(y1 - y1want) > 0.03 * S or y2 >= y1:
            errs.append(f"{label}: stem is not on the RIGHT edge of its head going up")
        if y1 - y2 < 3.0 * S - 0.01:
            errs.append(f"{label}: stem shorter than 3 staff spaces")
        e = {"kind": "n", "x": left + hw / 2, "open": gp == G_HALF, "head": "x" if gp == G_X else "n", "sx": sx, "swd": swd, "tip": y2, "acc": bool(accs)}
        if accs:
            pts = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", accs[0].get("points"))]
            ax, ay = pts[0::2], pts[1::2]
            # a ">" mark: opens to the left (two ends at the same x, tip to the right and in the middle), centred on the stem, above the stem tip
            ok = len(ax) == 3 and abs(ax[0] - ax[2]) < 0.01 and ax[1] > ax[0] and abs(ay[1] - (ay[0] + ay[2]) / 2) < 0.01 and ay[0] < ay[2] \
                and abs((ax[0] + ax[1]) / 2 - sx) < 0.05 * S and max(ay) < y2 - 0.3 * S
            if not ok:
                errs.append(f"{label}: accent mark is malformed or not above its stem")
            e["accbox"] = box_of(accs[0])[0]
            boxes["acc"].append(e["accbox"])
        boxes["head"].append(box_of(head)[0])
        boxes["stem"].append(box_of(sm)[0])
        evs.append(e)
    for r in st.iter(NS + "rect"):
        if r.get("class") == "beam":
            boxes["beam"].append(box_of(r)[0])
    evs.sort(key=lambda e: e["x"])
    for e in evs:
        e["lv"] = 0
    lvl_sets = {1: [], 2: []}
    for bx1, bx2, by, bh in beams:
        cov = [e for e in evs if e["kind"] == "n" and bx1 - 0.02 <= e["sx"] - e["swd"] / 2 and e["sx"] + e["swd"] / 2 <= bx2 + 0.02]
        if len(cov) < 2:
            errs.append(f"{label}: a beam joins fewer than two stems")
            continue
        top = min(e["tip"] for e in cov)
        lvl = 1 if abs(by - top) < 0.03 else 2 if abs(by - (top + 0.75 * S)) < 0.03 else 0
        if lvl == 0 or abs(bh - 0.5 * S) > 0.03:
            errs.append(f"{label}: beam at an unexpected height")
            continue
        if abs(bx1 - (cov[0]["sx"] - cov[0]["swd"] / 2)) > 0.03 or abs(bx2 - (cov[-1]["sx"] + cov[-1]["swd"] / 2)) > 0.03:
            errs.append(f"{label}: beam does not end exactly at its outer stems")
        if lvl == 1 and any(abs(e["tip"] - by) > 0.03 for e in cov):
            errs.append(f"{label}: a stem does not end at its beam")
        if len({e["head"] for e in cov}) != 1:
            errs.append(f"{label}: a beamed group mixes head types")
        if any(e["acc"] for e in cov):
            errs.append(f"{label}: an accent on a beamed note")
        for e in cov:
            e["lv"] += 1
        lvl_sets[lvl].append(frozenset(id(e) for e in cov))
    for s2 in lvl_sets[2]:
        if not any(s2 <= s1 for s1 in lvl_sets[1]):
            errs.append(f"{label}: a second beam is not inside a first beam")
    for e in evs:
        if e["kind"] == "n":
            if e["open"]:
                e["dur"] = Fraction(2)
                if e["lv"] or e["head"] == "x" or e["acc"]:
                    errs.append(f"{label}: half note with a beam, an x head or an accent")
            else:
                e["dur"] = {0: Fraction(1), 1: Fraction(1, 2), 2: Fraction(1, 4)}.get(e["lv"])
                if e["dur"] is None:
                    errs.append(f"{label}: more than two beams on a stem")
                    e["dur"] = Fraction(1)
        else:
            e["dur"] = Fraction(1)
    # time positions and bars
    t = Fraction(b0 * bl)
    for e in evs:
        e["t"] = t
        if abs(e["x"] - X(t)) > 0.15:
            errs.append(f"{label}: an event is not where its time position puts it")
        if int(t // bl) != int((t + e["dur"] - Fraction(1, 1000)) // bl):
            errs.append(f"{label}: a note crosses a barline")
        t += e["dur"]
    if t != Fraction((b0 + nb) * bl):
        errs.append(f"{label}: the bars add up to {t - b0 * bl} beats, expected {nb * bl}")
    for b in range(nb):
        s_ = sum((e["dur"] for e in evs if int(e["t"] // bl) == b0 + b), Fraction(0))
        if s_ != bl:
            errs.append(f"{label}: bar {b0 + b + 1} adds up to {s_} beats, expected {bl}")
    if len(evs) > 1 and min(b["x"] - a["x"] for a, b in zip(evs, evs[1:])) < hw0 + 1.0:
        errs.append(f"{label}: neighbouring noteheads crowd or overlap")
    # syllables beat by beat, token strings per bar
    syls, bar_tokens, i = [], [[] for _ in range(nb)], 0
    b = b0 * bl
    while b < (b0 + nb) * bl and i < len(evs):
        e = evs[i]
        if e["t"] != b:
            errs.append(f"{label}: an event starts off the beat or a beat is empty ({e['t']} vs {b})")
            return None
        bi = int(b // bl) - b0
        if e["kind"] == "n" and e["dur"] == 2:
            if b % 2:
                errs.append(f"{label}: half note starts on beat {int(b % bl) + 1}")
            syls.append((HALF_SYL, e["x"] + 0.5 * u))
            bar_tokens[bi].append("ta-a")
            i += 1
            b += 2
            continue
        grp = []
        while i < len(evs) and evs[i]["t"] < b + 1:
            grp.append(evs[i])
            i += 1
        pattern = tuple((x["kind"], x["dur"]) for x in grp)
        sname = BEAT_SYL.get(pattern)
        if sname is None:
            errs.append(f"{label}: beat {int(b % bl) + 1} holds a pattern with no syllable {pattern}")
            return None
        marks = {("x" if x["head"] == "x" else "") + (">" if x["acc"] else "") for x in grp if x["kind"] == "n"}
        if len(marks) > 1:
            errs.append(f"{label}: one beat mixes head types or accents")
        m = next(iter(marks)) if marks else ""
        suffix = ("*" if "x" in m else "") + (">" if ">" in m else "")
        if ">" in m and sname != "ta":
            errs.append(f"{label}: accent on something other than a quarter note")
        syls.append((sname, (grp[0]["x"] + grp[-1]["x"]) / 2))
        bar_tokens[bi].append(sname + suffix)
        b += 1
    if i != len(evs):
        errs.append(f"{label}: events left over after the last beat")
    for bx1, bx2, by, bh in beams:
        cov = [e for e in evs if e["kind"] == "n" and bx1 - 0.02 <= e["sx"] - e["swd"] / 2 and e["sx"] + e["swd"] / 2 <= bx2 + 0.02]
        if cov and len({int(e["t"]) for e in cov}) != 1:
            errs.append(f"{label}: a beam crosses a beat")
    # hands and say-it text
    hands = sorted((f(t, "x"), f(t, "y"), (t.text or "").strip(), t) for t in st.iter(NS + "text") if t.get("class") == "hand")
    sy = sorted((f(t, "x"), f(t, "y"), (t.text or "").strip(), t) for t in st.iter(NS + "text") if t.get("class") == "syl")
    notes = [e for e in evs if e["kind"] == "n"]
    out = {"tokens": bar_tokens, "events": evs, "hands": [h[2] for h in hands], "boxes": boxes, "kind": kind}
    if kind != "sym":
        if len(hands) != len(notes):
            errs.append(f"{label}: {len(hands)} hand letters for {len(notes)} notes (a rest must have none)")
        else:
            for (hx, hy, htxt, _), e in zip(hands, notes):
                if abs(hx - e["x"]) > 0.2:
                    errs.append(f"{label}: a hand letter is not under its note")
                if htxt not in ("R", "L"):
                    errs.append(f"{label}: hand label '{htxt}' is not R or L")
            if any(abs(hy - y0 - 3.2 * S) > 0.05 for _, hy, _, _ in hands):
                errs.append(f"{label}: hand letters are not on their row")
        if [s for _, _, s, _ in sy] != [s for s, _ in syls]:
            errs.append(f"{label}: printed syllables differ from the notation ({[s for _, _, s, _ in sy]} vs {[s for s, _ in syls]})")
        else:
            for (sx_, _, _, _), (_, want) in zip(sy, syls):
                if abs(sx_ - want) > 0.2:
                    errs.append(f"{label}: a syllable is not under its beat")
        # no collisions: hand letters and syllables against everything else drawn on the staff
        hb = [box_of(h[3])[0] for h in hands]
        sb = [box_of(s_[3])[0] for s_ in sy]
        for hbx in hb:
            for grp_, bs in boxes.items():
                for bx in bs:
                    if overlap(hbx, bx, 0.6):
                        errs.append(f"{label}: a hand letter touches a {grp_}")
            for sbx in sb:
                if overlap(hbx, sbx, 0.3):
                    errs.append(f"{label}: a hand letter overlaps a syllable")
        for a_, b_ in zip(sb, sb[1:]):
            if overlap(a_, b_, 1.5):
                errs.append(f"{label}: syllable labels crowd each other")
        for sbx in sb:
            for grp_, bs in boxes.items():
                for bx in bs:
                    if overlap(sbx, bx, 0.3):
                        errs.append(f"{label}: a syllable touches a {grp_}")
        # accents must not touch other stems or beams
        for abx in boxes["acc"]:
            for grp_ in ("beam", "rest", "head"):
                for bx in boxes[grp_]:
                    if overlap(abx, bx, 0.5):
                        errs.append(f"{label}: an accent touches a {grp_}")
            hits = sum(1 for bx in boxes["stem"] if overlap(abx, bx, 0.0))
            if hits > 0:
                errs.append(f"{label}: an accent overlaps a stem")
    return out


def expected_alternation(n):
    return ["RL"[i % 2] for i in range(n)]


def sys_roots(html):
    out = []
    for s in SVG_RE.findall(html):
        out.append(parse_svg(s))
    return out


def verify_html():
    errs = []
    html = open(os.path.join(BUILD, "resource.html")).read()
    roots = sys_roots(html)
    n_ns = n_ic = 0
    per = {}          # (groove, part) -> {b0: staff read}
    sys_count = {}
    for root in roots:
        if root.get("class") == "ic":
            n_ic += 1
            check_extent(root, f"icon {root.get('data-id')}", errs)
            continue
        n_ns += 1
        kind = root.get("data-kind")
        label = f'{kind} {root.get("data-id")}'
        check_extent(root, label, errs)
        staves = [g for g in root.iter(NS + "g") if g.get("class") == "staff"]
        reads = []
        for st in staves:
            r = read_staff(st, root, errs, label + f' part {st.get("data-part")}', None)
            reads.append((st, r))
        if kind == "sym":
            continue
        # counts and bar labels on the header row
        xb0, BW, padL, u, bl = (f(root, k) for k in ("data-xb0", "data-bw", "data-padl", "data-u", "data-bl"))
        nb, b0 = int(root.get("data-nb")), int(root.get("data-b0"))
        cnt = [(f(t, "x"), (t.text or "").strip()) for t in root.iter(NS + "text") if t.get("class") == "cnt"]
        bn = [(t.text or "").strip() for t in root.iter(NS + "text") if t.get("class") == "bn"]
        if len(cnt) != nb * 4 or [c for _, c in cnt] != ["1", "2", "3", "4"] * nb:
            errs.append(f"{label}: counts 1 2 3 4 missing or wrong")
        else:
            for k, (x, _) in enumerate(cnt):
                bb, bt = divmod(k, 4)
                if abs(x - (xb0 + bb * BW + padL + bt * u)) > 0.15:
                    errs.append(f"{label}: a count is not on its beat")
        if bn != [f"BAR {b0 + b + 1}" for b in range(nb)]:
            errs.append(f"{label}: bar labels are wrong ({bn})")
        # stacked parts: same bars, same x for the same time in every part
        valid = [r for _, r in reads if r]
        if kind == "full":
            g_no = int(root.get("data-groove"))
            if len(reads) != 3 or [st.get("data-part") for st, _ in reads] != ["1", "2", "3"]:
                errs.append(f"{label}: a stacked system needs parts 1, 2 and 3 in order")
            for a in valid[1:]:
                if len(a["events"]) and valid[0]["events"]:
                    pass
            times = {}
            for r in valid:
                for e in r["events"]:
                    times.setdefault(e["t"], []).append(e["x"])
            for t, xs in times.items():
                if max(xs) - min(xs) > 0.05:
                    errs.append(f"{label}: beat {t} is not at the same x in every part")
            ys = [f(st, "data-y0") for st, _ in reads]
            if any(b2 - a2 < 12 * f(root, "data-s") for a2, b2 in zip(ys, ys[1:])):
                errs.append(f"{label}: staves are too close together (no gutter)")
            for st, r in reads:
                if r:
                    per.setdefault((g_no, int(st.get("data-part"))), {})[b0] = r
            sys_count[g_no] = sys_count.get(g_no, 0) + 1
    # ---- groove data against the rendered notation
    for g in GROOVES:
        n = g["n"]
        for pi in range(3):
            got = per.get((n, pi + 1), {})
            label = f"groove {n} part {pi + 1}"
            use = {0: got.get(0), 2: got.get(2)} if n != 1 else {0: got.get(0), 2: got.get(2)}
            if n == 1:      # groove 1 also appears as one four-bar system on the sample score page (groove=1, b0=0, nb=4)
                pass
            if got.get(0) is None or got.get(2) is None:
                errs.append(f"{label}: the chart does not show bars 1-2 and bars 3-4")
                continue
            toks = got[0]["tokens"] + got[2]["tokens"]
            if len(toks) != BARS:
                errs.append(f"{label}: {len(toks)} bars on the page, expected {BARS}")
            want = [b.split() for b in g["parts"][pi]]
            if toks != want:
                errs.append(f"{label}: rendered notation {toks} differs from the data {want}")
            hands = got[0]["hands"] + got[2]["hands"]
            if hands != expected_alternation(len(hands)):
                errs.append(f"{label}: hand letters do not alternate R L R L through the four bars")
            if got[0]["hands"] != expected_alternation(len(got[0]["hands"])):
                errs.append(f"{label}: hand letters in bars 1-2 do not start on R and alternate")
            n1 = len(got[0]["hands"])
            if got[2]["hands"] != expected_alternation(n1 + len(got[2]["hands"]))[n1:]:
                errs.append(f"{label}: hand letters in bars 3-4 do not continue the alternation")
        if sys_count.get(n) != 2:
            errs.append(f"groove {n}: {sys_count.get(n)} stacked systems found")
    # ---- the sample score (groove 1, four bars on one line)
    score = [r for r in roots if r.get("data-id") == "score-g1"]
    if len(score) != 1:
        errs.append("sample score system not found")
    else:
        root = score[0]
        sts = [g for g in root.iter(NS + "g") if g.get("class") == "staff"]
        reads = [read_staff(st, root, [], "score", None) for st in sts]
        for pi, r in enumerate(reads):
            if r is None:
                continue
            if r["tokens"] != [b.split() for b in GROOVES[0]["parts"][pi]]:
                errs.append(f"sample score part {pi + 1} differs from Groove 1")
            if len(r["tokens"]) != BARS:
                errs.append("sample score is not four bars")
        guides = [l for l in root.iter(NS + "line") if l.get("class") == "guide"]
        if len(guides) != 3 * 16:
            errs.append(f"sample score: {len(guides)} beat guides, expected 48 (16 beats in 3 staves)")
        for l in guides:
            # every guide sits on a beat position of the stacked parts
            xb0, BW, padL, u = (f(root, k) for k in ("data-xb0", "data-bw", "data-padl", "data-u"))
            k = (f(l, "x1") - xb0 - padL) / u
            bb = int((f(l, "x1") - xb0) // BW)
            kk = (f(l, "x1") - xb0 - bb * BW - padL) / u
            if abs(kk - round(kk)) > 0.01:
                errs.append("sample score: a beat guide is off the beat grid")
                break
        for s_ in re.findall(r'<li data-bar="(\d)" data-beat="(\d)" data-st="([a-z,]+)">', html):
            bar, beat, stt = int(s_[0]), int(s_[1]), s_[2].split(",")
            t = Fraction((bar - 1) * BEATS + beat - 1)
            for pi, r in enumerate(reads):
                cur = [e for e in r["events"] if e["t"] <= t < e["t"] + e["dur"]]
                have = "rests" if cur[0]["kind"] == "r" else ("holds" if cur[0]["t"] < t else "plays")
                if have != stt[pi]:
                    errs.append(f"sample score: text says part {pi + 1} {stt[pi]} at bar {bar} beat {beat} but the notation says {have}")
        if len(re.findall(r'<li data-bar=', html)) != len(SCORE_MOMENTS):
            errs.append("sample score: reading-down lines missing")
    # ---- the groove page cards: counts printed equal counts in the notation
    for m in re.finditer(r'<div class="pcard" data-groove="(\d)" data-part="(\d)" data-notes="(\d+)" data-rests="(\d+)" data-acc="(\d+)" data-rim="(\d+)">.*?<div class="st">([^<]*)</div>', html, re.S):
        n, pi = int(m.group(1)), int(m.group(2))
        got = per.get((n, pi), {})
        if got.get(0) is None or got.get(2) is None:
            continue
        evs = got[0]["events"] + got[2]["events"]
        have = (sum(1 for e in evs if e["kind"] == "n"), sum(1 for e in evs if e["kind"] == "r"), sum(1 for e in evs if e["acc"]), sum(1 for e in evs if e["kind"] == "n" and e["head"] == "x"))
        printed = tuple(int(m.group(k)) for k in (3, 4, 5, 6))
        if have != printed:
            errs.append(f"groove {n} part {pi}: card says {printed} (notes, rests, accents, rim clicks) but the notation has {have}")
        s_ = {"notes": have[0], "rests": have[1], "acc": have[2], "rim": have[3]}
        if m.group(7) != stats_text(s_):
            errs.append(f"groove {n} part {pi}: printed card text '{m.group(7)}' differs from the notation counts")
    if len(re.findall(r'<div class="pcard"', html)) != N_PARTS:
        errs.append(f"expected {N_PARTS} part cards")
    # ---- key page: each symbol row shows what it names; the worked bar adds up
    for tok, name, beats, say in KEY_ROWS:
        r = [x for x in roots if x.get("data-id") == f"key-{keyid(tok)}"]
        if len(r) != 1:
            errs.append(f"key row {tok}: svg not found")
            continue
        st = next(g for g in r[0].iter(NS + "g") if g.get("class") == "staff")
        res = read_staff(st, r[0], errs, f"key row {tok}", None)
        if res and res["tokens"][0] != [tok]:
            errs.append(f"key row {tok}: shows {res['tokens']} but is named '{name}'")
        # the length column
        nbeat = token_beats(tok.rstrip(">*"))
        if str(int(nbeat)) not in beats:
            errs.append(f"key row {tok}: length text '{beats}' disagrees with {nbeat} beats")
    for uid, bar, _d in EX_KEYS:
        ex = [x for x in roots if x.get("data-id") == uid]
        if len(ex) != 1:
            errs.append(f"key example {uid} missing")
            continue
        st = next(g for g in ex[0].iter(NS + "g") if g.get("class") == "staff")
        res = read_staff(st, ex[0], errs, uid, None)
        if res and res["tokens"] != [bar.split()]:
            errs.append(f"key example {uid} differs from its data")
    kinds = sorted(r.get("data-kind") for r in roots if r.get("class") == "ic" and r.get("data-id", "").startswith("key-"))
    if kinds != sorted(k for k, _, _ in KEY_STRUCT):
        errs.append(f"key page: structure symbols {kinds}")
    for r in roots:
        if r.get("class") == "ic" and r.get("data-id", "").startswith("key-"):
            k = r.get("data-kind")
            n_c = sum(1 for t in r.iter(NS + "text") if t.get("class") == "clef")
            n_t = sum(1 for t in r.iter(NS + "text") if t.get("class") == "tsd")
            n_b = sum(1 for l in r.iter(NS + "line") if l.get("class") == "bar")
            n_f = sum(1 for q in r.iter(NS + "rect") if q.get("class") == "fin")
            if (n_c, n_t, n_b, n_f) != {"clef": (1, 0, 0, 0), "ts": (0, 2, 0, 0), "bar": (0, 0, 1, 0), "fin": (0, 0, 1, 1)}[k]:
                errs.append(f"key symbol {k} is not drawn correctly")
    # ---- every symbol the key defines is used somewhere, and everything used is defined
    used_heads = set()
    for g in GROOVES:
        for bars in g["parts"]:
            for b in bars:
                for tk in b.split():
                    used_heads.add(tk)
    defined = {tok for tok, *_ in KEY_ROWS}
    for tk in used_heads:
        base, acc, rim = parse_tok(tk)
        need = base + (">" if acc else "") + ("*" if rim else "")
        if base in ("ti-ti", "ti-ka-ti-ka", "ti-ti-ka", "ti-ka-ti", "ta-a", "shh") and base not in defined:
            errs.append(f"symbol '{base}' is used in a groove but not defined in the key")
        if acc and ">" not in "".join(t for t in defined if t.endswith(">")):
            errs.append("accent used but not defined in the key")
        if rim and "ta*" not in defined:
            errs.append("rim click used but not defined in the key")
    for tok in defined:
        base = tok.rstrip(">*")
        if base not in {t.rstrip(">*") for t in used_heads} and tok not in used_heads:
            errs.append(f"key defines '{tok}' but no groove uses it")
    # ---- counts on the groove charts
    if len(GROOVES) != 6 or N_PARTS != 18:
        errs.append("expected 6 grooves and 18 parts")
    if n_ns == 0 or n_ic == 0:
        errs.append("no drawings found")
    verify_html.counts = (n_ns, n_ic)
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(p.split()[0], p.split()[-5]) for p in out]


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))


LAYOUT_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const out = [];
  const shotDir = process.argv[2];
  fs.mkdirSync(shotDir, { recursive: true });
  let shotN = 0;
  for (const f of process.argv.slice(3)) {
    const p = await b.newPage({ viewport: { width: 816, height: 1056 }, deviceScaleFactor: 4 });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const res = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        const boxes = [];
        pg.querySelectorAll('svg.ns, svg.ic, .box, .step, .pcard, .ib, .kc, .doc table, .doc p, .doc ul, .top, .sysbox, .nd').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 6) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -6)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: element ${el.tagName}.${el.getAttribute('class')} too close to the page edge`);
          if (el.matches('.box, .step, .pcard, .ib, .kc')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 8 && gy < 8) res.push(`page ${i + 1}: two boxes lack a gutter`);
        }
        // stacked systems keep a visible gutter between them
        const sys = [...pg.querySelectorAll('svg.ns')].filter(s => s.dataset.kind === 'full').map(s => s.getBoundingClientRect());
        for (let a = 0; a < sys.length - 1; a++) if (sys[a + 1].top - sys[a].bottom < 5) res.push(`page ${i + 1}: systems lack a gutter`);
        // drawings sit inside their boxes with padding
        pg.querySelectorAll('.box svg, .ib svg, .kc svg, .syt svg').forEach(sv => {
          const box = sv.closest('.box, .ib, .kc, td').getBoundingClientRect();
          const s = sv.getBoundingClientRect();
          if (s.left < box.left + 4 || s.right > box.right - 4 || s.top < box.top + 2 || s.bottom > box.bottom - 2) res.push(`page ${i + 1}: a drawing is too close to its box edge`);
        });
        pg.querySelectorAll('.pcard').forEach(cd => {
          if (cd.scrollHeight > cd.clientHeight + 1) res.push(`page ${i + 1}: a part card overflows`);
        });
        pg.querySelectorAll('.doc p, .doc li').forEach(el => {
          const range = document.createRange(); range.selectNodeContents(el);
          const rects = [...range.getClientRects()].filter(q => q.width > 1);
          const lines = {};
          rects.forEach(q => { const k = Math.round(q.top / 3); lines[k] = lines[k] ? [Math.min(lines[k][0], q.left), Math.max(lines[k][1], q.right)] : [q.left, q.right]; });
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length >= 2) {
            const last = lines[ks[ks.length - 1]];
            const w = el.getBoundingClientRect().width;
            const txt = el.innerText.trim().split(/\s+/);
            if (last[1] - last[0] < 0.12 * w && txt.length > 6) res.push(`page ${i + 1}: short last line in "${el.innerText.trim().slice(0, 40)}..."`);
          }
        });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (ft && ft.contains(el)) return; if (el.closest('.wm')) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && el.children.length === 0) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 78) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer`);
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    if (f.endsWith('resource.html')) {
      // every reusable drawing rendered alone on a transparent ground
      await p.evaluate(() => { document.documentElement.style.background = 'transparent'; document.body.style.background = 'transparent'; document.querySelectorAll('.page, .box, .ib, td, .sysbox, .pcard').forEach(e => { e.style.background = 'transparent'; }); });
      const handles = await p.$$('svg.ns, svg.ic');
      for (const h of handles) {
        const name = shotDir + '/s' + String(shotN++).padStart(4, '0') + '.png';
        await h.screenshot({ path: name, omitBackground: true });
      }
    }
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""


def verify_layout(n_drawings):
    js = os.path.join(BUILD, "layout.js")
    with open(js, "w") as fh:
        fh.write(LAYOUT_JS)
    files = [os.path.join(BUILD, "resource.html"), os.path.join(BUILD, "preview.html")]
    if not all(os.path.exists(x) for x in files):
        return ["build html missing: run gen.py first"]
    shots = os.path.join(BUILD, "svgshots")
    if os.path.isdir(shots):
        for x in os.listdir(shots):
            os.remove(os.path.join(shots, x))
    r = subprocess.run(["node", js, shots, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"layout script failed: {r.stderr[-300:]}"]
    errs = json.loads(r.stdout.strip().splitlines()[-1])
    from PIL import Image
    names = sorted(os.listdir(shots))
    if len(names) != n_drawings:
        errs.append(f"svg screenshots: {len(names)}, expected {n_drawings}")
    for nme in names:
        im = Image.open(os.path.join(shots, nme)).convert("RGBA")
        a = im.getchannel("A")
        px = a.load()
        w, h = im.size
        ring = 4          # device pixels (1 CSS px at 4x)
        bad = any(px[x, y] > 20 for x in range(w) for y in list(range(0, ring)) + list(range(h - ring, h))) or \
            any(px[x, y] > 20 for y in range(h) for x in list(range(0, ring)) + list(range(w - ring, w)))
        if bad:
            errs.append(f"rendered pixels: ink touches the edge of drawing {nme} rendered alone on a transparent ground")
    return errs


def verify_images():
    errs = []
    from PIL import Image
    h = Image.open(HERO).convert("RGBA")
    a = h.getchannel("A")
    pxa = a.load()
    w_, h_ = h.size
    edge = max([pxa[x, 0] for x in range(w_)] + [pxa[x, h_ - 1] for x in range(w_)] + [pxa[0, y] for y in range(h_)] + [pxa[w_ - 1, y] for y in range(h_)])
    if edge > 12:
        errs.append(f"hero art touches its image edge (alpha {edge})")
    if h.getpixel((0, 0))[3] > 12 or h.getpixel((w_ - 1, h_ - 1))[3] > 12:
        errs.append("hero art has a background box (corners are not transparent)")
    if Image.open(HERO).mode != "RGBA":
        errs.append("hero art is not a transparent PNG")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        name = os.path.basename(p)
        im = Image.open(p).convert("L")
        if im.size != (2000, 2000):
            errs.append(f"{name}: not 2000x2000")
            continue
        px = im.load()
        rows = [sum(1 for x in range(0, 2000, 8) if px[x, y] < 200) for y in range(0, 2000, 2)]
        ytop = 2000
        for y in range(1999, 0, -1):
            if px[2, y] < 60 and px[1997, y] < 60:
                ytop = y
            else:
                break
        for edge_, pts in (("top", [(x, y) for x in range(0, 2000, 2) for y in range(0, 14)]),
                           ("left", [(x, y) for x in range(0, 14) for y in range(0, ytop - 4, 2)]),
                           ("right", [(x, y) for x in range(1986, 2000) for y in range(0, ytop - 4, 2)])):
            if any(px[x, y] < 235 for x, y in pts):
                errs.append(f"{name}: art or ink touches the {edge_} edge")
        if ytop > 1990 or ytop < 1700:
            errs.append(f"{name}: bottom band not found (starts at {ytop})")
        elif any(px[x, y] > 40 for x in list(range(0, 6)) + list(range(1994, 2000)) for y in range(ytop + 40, 2000)):
            errs.append(f"{name}: bottom band is not solid black to the edge")
        run = best = 0
        for y in range(120, ytop, 2):
            if rows[y // 2] == 0:
                run += 2
                best = max(best, run)
            else:
                run = 0
        if best > 200:
            errs.append(f"{name}: blank band of {best}px")
        last = max((y for y in range(0, ytop, 2) if rows[y // 2] > 0), default=0)
        if ytop - last > 200:
            errs.append(f"{name}: {ytop - last}px blank above the bottom band")
        cols = [x for x in range(0, 2000, 2) if any(px[x, y] < 200 for y in range(120, ytop - 4, 4))]
        if cols and (min(cols) < 40 or max(cols) > 1960):
            errs.append(f"{name}: content within 40px of the left or right edge")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, HERO, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pg in enumerate(rd.pages):
            if abs(float(pg.mediabox.width) - 612) > 1 or abs(float(pg.mediabox.height) - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
        names = " ".join(n for n, _ in fonts).lower().replace(" ", "")
        for fam in ("bravura", "oswald", "sourcesans3"):
            if fam not in names:
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    rd = PdfReader(PDF)
    texts = [" ".join((pg.extract_text() or "").split()) for pg in rd.pages]
    for i, t in enumerate(texts):
        if len(t) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t.upper():
            errs.append(f"product PDF page {i + 1} carries a PREVIEW watermark")
        if i + 1 != 1 and f"Page {i + 1}" not in t:
            errs.append(f"PDF page {i + 1} does not print its own page number")
    for pg, name in PAGE_NAMES.items():
        if pg == P_COVER:
            continue
        if name.lower() not in texts[pg - 1].lower():
            errs.append(f"page {pg} does not show its name '{name}'")
    full_pages()
    for frm, to, text in XREFS:
        if text not in texts[frm - 1]:
            errs.append(f"page {frm}: cross-reference text '{text}' not found")
        if SHORT[to].split()[0].lower() not in PAGE_NAMES[to].lower():
            errs.append(f"cross-reference to page {to} names it '{SHORT[to]}' but the page is '{PAGE_NAMES[to]}'")
    allt = " ".join(texts)
    for i, t in enumerate(texts):
        for m in re.finditer(r"(?i)\bpages? (\d+)(?:–(\d+))?", t):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a < 1 or b > TOTAL_PAGES or b < a:
                errs.append(f"page {i + 1}: reference '{m.group(0)}' is outside the {TOTAL_PAGES}-page file")
        # every named page reference points at the right page
        for m in re.finditer(r"(?i)(safety and setup page|notation key|layering activity|sample score|ensemble planner|rubric and score sheet) \(page (\d+)\)", t):
            want = {v: k for k, v in SHORT.items()}[m.group(1).lower()]
            if int(m.group(2)) != want:
                errs.append(f"page {i + 1}: '{m.group(0)}' points at the wrong page")
        # steps: "Step N (Name)" must use the real name; plain "Step N" only 1-4
        for m in re.finditer(r"Step (\d) \(([^)]+)\)", t):
            n = int(m.group(1))
            if not 1 <= n <= len(STEPS) or STEPS[n - 1][0] != m.group(2):
                errs.append(f"page {i + 1}: '{m.group(0)}' does not match the step list")
        for m in re.finditer(r"\bStep (\d)\b", t):
            if not 1 <= int(m.group(1)) <= len(STEPS):
                errs.append(f"page {i + 1}: step {m.group(1)} does not exist")
    # the four numbered steps and the build map on the layering page; the planner ticks the same steps
    lay, plan, sc = texts[P_LAYER - 1], texts[P_PLAN - 1], texts[P_SCORE - 1]
    for n in range(1, len(STEPS) + 1):
        if step_ref(n) not in plan:
            errs.append(f"planner lacks '{step_ref(n)}'")
    for n in (2, 3, 4):
        if step_ref(n) not in lay or step_ref(n) not in sc:
            errs.append(f"layering page or sample score lacks '{step_ref(n)}'")
    if f"{TOTAL_PASSES} passes" not in lay or f"{TOTAL_BARS} bars" not in lay or f"{SECONDS} seconds" not in lay:
        errs.append("layering page: pass, bar or time totals missing")
    if TOTAL_BARS != sum(PASSES.values()) * BARS or SECONDS != round(TOTAL_BARS * BEATS * 60 / LAYER_BPM / 10) * 10:
        errs.append("layering totals disagree")
    # counts across the whole file
    for m in re.finditer(r"\b(\d+) grooves\b", allt):
        if int(m.group(1)) != N_GROOVES:
            errs.append(f"text says '{m.group(0)}' but there are {N_GROOVES} grooves")
    for m in re.finditer(r"\b(\d+) pages\b", allt):
        if int(m.group(1)) != TOTAL_PAGES:
            errs.append(f"text says '{m.group(0)}' but the file has {TOTAL_PAGES} pages")
    for m in re.finditer(r"\b(\d+) parts\b", allt):
        if int(m.group(1)) not in (N_PARTS,):
            errs.append(f"text says '{m.group(0)}'")
    teach, terms = texts[P_TEACH - 1], texts[P_TERMS - 1]
    for need in (f"pages {groove_pages_text()}", f"page {P_SAFE}", f"pages {P_KEY}–{P_KEY2}", f"page {P_LAYER}", f"page {P_SCORE}", f"page {P_PLAN}", f"page {P_RUBRIC}"):
        for nm, tx in (("teacher notes", teach), ("terms", terms)):
            if need not in tx:
                errs.append(f"{nm} page lacks the reference '{need}'")
    for g in GROOVES:
        if f"Groove {g['n']}: {g['name']}" not in texts[gpage(g["n"]) - 1]:
            errs.append(f"groove {g['n']} page is not labeled with its name")
        if f"Build the groove with the layering activity (page {P_LAYER})" not in texts[gpage(g["n"]) - 1]:
            errs.append(f"groove {g['n']} page lacks its layering reference")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        want = PAGE_NAMES[PREVIEW_PAGES[i]]
        if want.lower() not in t.lower():
            errs.append(f"preview PDF page {i + 1} is not '{want}'")
    errs += verify_images()
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80:
            errs.append(f"UPLOAD.md: title is {len(title)} chars")
        if re.search(r"winter|snow|holiday|christmas|december", title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
        if title != LISTING_TITLE:
            errs.append("UPLOAD.md: title block differs from LISTING_TITLE")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", f"{N_GROOVES} grooves", f"{N_PARTS} parts", "grades 3-8", "3rd, 4th, 5th and 6th"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    dn = [int(x) for x in re.findall(r"^• [^\n]*\((\d+) pages?\)", desc, re.M)]
    if sum(dn) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md description page list sums to {sum(dn)}, PDF has {TOTAL_PAGES}")
    for m in re.finditer(r"\b(\d+) grooves\b", up):
        if int(m.group(1)) != N_GROOVES:
            errs.append(f"UPLOAD.md: '{m.group(0)}'")
    for m in re.finditer(r"\b(\d+) pages\b", up):
        if int(m.group(1)) not in (TOTAL_PAGES, 4, N_GROOVES, 2):
            errs.append(f"UPLOAD.md: '{m.group(0)}'")
    low = up.lower()
    for bad in ("checked by hand", "handmade", "recomputed", "classroom-tested", "classroom tested", "hand-checked"):
        if bad in low:
            errs.append(f"UPLOAD.md says '{bad}'")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if any(t not in tags for t in tj["tags"]) or any(s not in subs for s in tj["subjects"]):
        errs.append("tpt.json tags or subjects invalid")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE or not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json pages, price or grades mismatch")
    first = texts[0].lower()
    if f"{TOTAL_PAGES} pages" not in first or f"{N_GROOVES} grooves" not in first or f"{N_PARTS} parts" not in first:
        errs.append("cover text does not state the page, groove and part counts")
    if DISCLOSURE not in terms:
        errs.append("terms page lacks the disclosure line")
    low = allt.lower()
    for bad in ("qa ", "checker", "recomputed", "verified by code", "todo", "lorem"):
        if bad in low.replace("answer keys are verified", ""):
            errs.append(f"buyer-facing text contains internal wording '{bad}'")
    for bad in ("colour", "favourite", "rhythmn", "centre", "grey "):
        if bad in low:
            errs.append(f"non-US spelling '{bad}'")
    # art bookkeeping: the hero is the library's bucket-drums and is logged in USAGE.md
    usage = os.path.join(TPT, "_art", "USAGE.md")
    if os.path.exists(usage) and not re.search(r"\| 059 \| hero\.png", open(usage).read()):
        errs.append("tpt/_art/USAGE.md has no line for 059")
    return errs


def check():
    errs = verify_html()
    n_ns, n_ic = verify_html.counts
    errs += verify_layout(n_ns + n_ic)
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: {N_GROOVES} grooves, {N_PARTS} parts (all different) re-read from the rendered SVG: one-line staff, neutral clef, 4/4, stems up on the right of the heads, "
          f"beams single for eighths and double for sixteenths, quarter rests on the line, accents and x heads; every bar adds to 4 beats, 4 bars per part, every note at its time position; "
          f"syllables and hand letters recomputed from the notation match the printed ones (hands alternate through the four bars); stacked parts share bar lines and beat positions; "
          f"{n_ns} staff drawings and {n_ic} icons inside their boxes with no ink on their edges (rendered alone on a transparent ground); layout clear; "
          f"PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each); images 2000x2000 with clean edges; cross-references, steps, counts, UPLOAD.md and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
