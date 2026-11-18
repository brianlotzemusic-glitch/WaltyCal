#!/usr/bin/env python3
"""Holiday Music Word Puzzles (TpT 052): build the resource and verify it.

    python3 gen.py                     build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check             re-solve every puzzle from the rendered HTML and verify layout, pages, fonts and files
    python3 gen.py --find-crosswords   (development) search for crossword layouts; the chosen ones are stored in CW_PLACEMENTS

Word searches are placed by code (random but seeded), filled with random letters, and re-filled until every listed word occurs
exactly once in all 8 directions. Crosswords are laid out by a randomized search whose results are stored in CW_PLACEMENTS.
`--check` does not trust those tables: it parses the rendered HTML, rebuilds each grid, and solves / validates it with its own code.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in ../fonts.
"""
import json
import math
import os
import random
import re
import subprocess
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "holiday-music-word-puzzles"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#2F86B8"      # icy blue: the one accent of this product
TINT = "#DCEEF8"        # pale tint of the accent (cover art only)
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Holiday Music Word Puzzles"
LISTING_TITLE = "Music Word Searches and Crosswords: Instruments, Symbols, Rhythm | Gr 3-6"
PREFERRED_TITLE = "Holiday Music Word Puzzles: Word Searches and Crosswords | Music Gr 3-6"
PRICE = "3.50"
TAGS = ["Winter", "Worksheets", "Printables", "Activities", "Centers"]
SUBJECTS = ["Music", "Instrumental Music", "Vocabulary"]
GRADES = ["3rd-grade", "4th-grade", "5th-grade", "6th-grade"]

# ================================================================== puzzle engines and word tables

DIRS = {"R": (0, 1), "D": (1, 0), "DR": (1, 1), "UR": (-1, 1), "L": (0, -1), "U": (-1, 0), "UL": (-1, -1), "DL": (1, -1)}
DIR_NAME = {"R": "right", "D": "down", "DR": "down-right", "UR": "up-right", "L": "left", "U": "up", "UL": "up-left", "DL": "down-left"}

# ---- word searches: (title, theme blurb, grid size, directions allowed, words)
WORD_SEARCHES = [
    ("Instruments of the Orchestra", 12, ["R", "D"],
     "VIOLIN VIOLA CELLO HARP FLUTE OBOE CLARINET BASSOON TRUMPET TROMBONE TUBA TIMPANI".split()),
    ("Band Instruments", 12, ["R", "D", "DR"],
     "SAXOPHONE EUPHONIUM CORNET PICCOLO SNARE CYMBALS XYLOPHONE MARIMBA TRIANGLE DRUMS HORN FLUTE".split()),
    ("Music Symbols and Terms", 13, ["R", "D", "DR", "UR"],
     "FORTE PIANO TEMPO STACCATO LEGATO CRESCENDO FERMATA CLEF SHARP FLAT STAFF MEASURE DYNAMICS".split()),
    ("Winter Music Words", 14, ["R", "D", "DR", "UR", "L"],
     "SNOWFLAKE SLEIGH BELLS CHOIR CONCERT MITTENS SCARF ICICLE SNOWMAN COCOA WINTER CHORUS FROST SNOWBALL".split()),
    ("Rhythm Words", 15, ["R", "D", "DR", "UR", "L", "U", "UL", "DL"],
     "BEAT PULSE METER MEASURE BARLINE QUARTER EIGHTH WHOLE DOTTED TRIPLET RHYTHM SYNCOPATION HALF SIXTEENTH".split()),
    ("Music Makers and Jobs", 15, ["R", "D", "DR", "UR", "L", "U", "UL", "DL"],
     "CONDUCTOR COMPOSER SINGER PIANIST DRUMMER VIOLINIST SOLOIST ARRANGER BASSIST CELLIST GUITARIST SONGWRITER PERFORMER TEACHER".split()),
]


def find_all(grid, word):
    n = len(grid)
    m = len(grid[0])
    hits = []
    L = len(word)
    for r in range(n):
        for c in range(m):
            for d, (dr, dc) in DIRS.items():
                er, ec = r + dr * (L - 1), c + dc * (L - 1)
                if not (0 <= er < n and 0 <= ec < m):
                    continue
                if all(grid[r + dr * i][c + dc * i] == word[i] for i in range(L)):
                    hits.append((r, c, d))
    return hits


def make_word_search(words, size, dirs, seed):
    """Place every word (random, varied directions), then fill with random letters until each word occurs exactly once."""
    rng = random.Random(seed)
    order = sorted(words, key=lambda w: -len(w))
    for attempt in range(400):
        grid = [[""] * size for _ in range(size)]
        placed = {}
        ok = True
        # cycle through allowed directions so every one is used
        cyc = dirs[:]
        rng.shuffle(cyc)
        for k, w in enumerate(order):
            want = cyc[k % len(cyc)]
            tries = [want] + [d for d in dirs if d != want]
            cands = []
            for d in tries:
                dr, dc = DIRS[d]
                opts = []
                for r in range(size):
                    for c in range(size):
                        er, ec = r + dr * (len(w) - 1), c + dc * (len(w) - 1)
                        if not (0 <= er < size and 0 <= ec < size):
                            continue
                        good, ov = True, 0
                        for i, ch in enumerate(w):
                            cur = grid[r + dr * i][c + dc * i]
                            if cur and cur != ch:
                                good = False
                                break
                            if cur == ch:
                                ov += 1
                        if good and ov <= 2:
                            opts.append((r, c, d))
                if opts:
                    cands = opts
                    break
            if not cands:
                ok = False
                break
            r, c, d = rng.choice(cands)
            dr, dc = DIRS[d]
            for i, ch in enumerate(w):
                grid[r + dr * i][c + dc * i] = ch
            placed[w] = (r, c, d)
        if not ok:
            continue
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for fill_try in range(60):
            g2 = [row[:] for row in grid]
            for r in range(size):
                for c in range(size):
                    if not g2[r][c]:
                        g2[r][c] = rng.choice(letters)
            if all(len(find_all(g2, w)) == 1 for w in words):
                # the single hit must be the placed position
                if all(find_all(g2, w)[0] == placed[w] for w in words):
                    return g2, placed
    raise RuntimeError("could not build word search")


# ---- crossword words: answer -> clue
CLUES = {
    # instruments
    "VIOLIN": "Smallest and highest-sounding bowed string instrument",
    "CELLO": "String instrument that you hold between your knees and play with a bow",
    "HARP": "Large string instrument whose strings are plucked with both hands",
    "FLUTE": "Woodwind you play by blowing across a hole near one end",
    "OBOE": "Double-reed woodwind that gives the orchestra its tuning note",
    "CLARINET": "Woodwind with a single reed and a straight tube",
    "TRUMPET": "Brass instrument with three valves and a bright, high sound",
    "TROMBONE": "Brass instrument with a slide that changes the pitch",
    "TUBA": "The lowest-sounding brass instrument",
    "TIMPANI": "Large kettle-shaped drums that can be tuned to different pitches",
    "XYLOPHONE": "Percussion instrument with wooden bars that you play with mallets",
    "PICCOLO": "Tiny flute that plays the highest notes in the orchestra",
    "SAXOPHONE": "Curved metal woodwind with a single reed, popular in jazz",
    "GUITAR": "String instrument with six strings that you strum or pluck",
    # symbols and terms
    "FORTE": "Italian word that means loud",
    "PIANO": "Italian word that means soft",
    "TEMPO": "How fast or slow the music goes",
    "CLEF": "Symbol at the start of a staff that tells you the note names",
    "STAFF": "Five lines and four spaces where music is written",
    "SHARP": "Symbol that raises a note by a half step",
    "FLAT": "Symbol that lowers a note by a half step",
    "REST": "Symbol for a silent beat",
    "TIE": "Curved line that joins two notes of the same pitch",
    "FERMATA": "Symbol that tells you to hold a note longer",
    "STACCATO": "Played short and separated",
    "LEGATO": "Played smoothly, with the notes connected",
    "CRESCENDO": "Gradually getting louder",
    "BARLINE": "Vertical line that divides the staff into measures",
    "DYNAMICS": "Markings that tell you how loud or soft to play",
    # winter
    "SLEIGH": "Vehicle with runners that glides over snow",
    "BELLS": "Metal instruments that ring when struck or shaken",
    "CHOIR": "A group of singers who perform together",
    "ICICLE": "Pointed stick of ice hanging from a roof",
    "COCOA": "Hot chocolate drink",
    "MITTENS": "Warm coverings for your hands with a space for the thumb",
    "SCARF": "Warm wrap you wear around your neck",
    "WINTER": "The coldest season of the year",
    "SNOWMAN": "Figure made from three big rolled snowballs",
    "CONCERT": "A music show for an audience",
    "FROST": "Thin layer of ice crystals on a window",
    "SNOWFLAKE": "Tiny six-sided crystal of ice that falls from the sky",
    "CHORUS": "The part of a song that repeats",
    # rhythm and people
    "BEAT": "The steady pulse of the music",
    "METER": "How the beats are grouped into measures",
    "MEASURE": "A group of beats between two bar lines",
    "RHYTHM": "A pattern of long and short sounds",
    "QUARTER": "Note that gets one beat in 4/4 time",
    "EIGHTH": "Two of these notes make one beat in 4/4 time",
    "HALF": "Note that gets two beats in 4/4 time",
    "WHOLE": "Note that gets four beats in 4/4 time",
    "TRIPLET": "Group of three notes played in the time of two",
    "CONDUCTOR": "Person who leads an orchestra with a baton",
    "COMPOSER": "Person who writes music",
    "SOLOIST": "Performer who plays alone while the others accompany",
    "DRUMMER": "Band member who plays the snare, toms and cymbals",
    "SINGER": "Musician who uses a voice as an instrument",
    "PIANIST": "Musician who plays a keyboard with 88 keys",
    "ARRANGER": "Person who adapts a song for different instruments",
    "TEACHER": "Person who helps students learn music",
}

CROSSWORDS = [
    ("Orchestra Instruments", "VIOLIN CELLO HARP FLUTE OBOE CLARINET TRUMPET TROMBONE TUBA TIMPANI XYLOPHONE PICCOLO".split()),
    ("Music Symbols and Terms", "FORTE PIANO TEMPO CLEF STAFF SHARP FLAT REST TIE FERMATA STACCATO LEGATO CRESCENDO".split()),
    ("Winter Music Words", "SLEIGH BELLS CHOIR ICICLE COCOA MITTENS SCARF WINTER SNOWMAN CONCERT FROST SNOWFLAKE CHORUS".split()),
    ("Rhythm and Music Makers", "BEAT METER MEASURE RHYTHM QUARTER EIGHTH HALF WHOLE TRIPLET CONDUCTOR COMPOSER SOLOIST DRUMMER".split()),
]


def runs(cells):
    """Across and down runs (length >= 2) of a set of (r, c) cells -> list of (dir, r, c, length)."""
    out = []
    for (r, c) in cells:
        if (r, c - 1) not in cells and (r, c + 1) in cells:
            n = 0
            while (r, c + n) in cells:
                n += 1
            out.append(("A", r, c, n))
        if (r - 1, c) not in cells and (r + 1, c) in cells:
            n = 0
            while (r + n, c) in cells:
                n += 1
            out.append(("D", r, c, n))
    return sorted(out, key=lambda x: (x[1], x[2], x[0]))


def try_crossword(words, rng, size):
    """Greedy random placement; returns dict word -> (r, c, dir) for the words that fit, or None."""
    grid = {}
    placed = {}
    order = words[:]
    rng.shuffle(order)
    order.sort(key=lambda w: -len(w) + rng.random() * 3)
    first = order[0]
    r0 = size // 2
    c0 = (size - len(first)) // 2
    for i, ch in enumerate(first):
        grid[(r0, c0 + i)] = ch
    placed[first] = (r0, c0, "A")
    rest = order[1:]
    for w in rest:
        best = []
        for d in ("A", "D"):
            for (r, c), ch in list(grid.items()):
                for i, wc in enumerate(w):
                    if wc != ch:
                        continue
                    sr, sc = (r, c - i) if d == "A" else (r - i, c)
                    cells = [((sr, sc + k) if d == "A" else (sr + k, sc)) for k in range(len(w))]
                    if any(not (0 <= a < size and 0 <= b < size) for a, b in cells):
                        continue
                    cross = 0
                    ok = True
                    for (a, b), x in zip(cells, w):
                        if (a, b) in grid:
                            if grid[(a, b)] != x:
                                ok = False
                                break
                            cross += 1
                    if not ok or cross == 0 or cross == len(w):
                        continue
                    best.append((cross, sr, sc, d))
        rng.shuffle(best)
        for cross, sr, sc, d in sorted(best, key=lambda x: -x[0] + rng.random() * 1.2):
            newg = dict(grid)
            for k, x in enumerate(w):
                newg[((sr, sc + k) if d == "A" else (sr + k, sc))] = x
            rs = runs(set(newg))
            want = {(dd, rr, cc, ln) for ww, (rr, cc, dd) in list(placed.items()) + [(w, (sr, sc, d))] for ln in [len(ww)]}
            if {(a, b, c2, e) for a, b, c2, e in rs} == {(dd, rr, cc, ln) for dd, rr, cc, ln in want}:
                grid = newg
                placed[w] = (sr, sc, d)
                break
    return placed, grid


def bbox(cells):
    rs = [r for r, c in cells]
    cs = [c for r, c in cells]
    return min(rs), min(cs), max(rs), max(cs)


def sym_score(cells):
    r0, c0, r1, c1 = bbox(cells)
    n = 0
    for (r, c) in cells:
        if (r0 + r1 - r, c0 + c1 - c) in cells:
            n += 1
    return n / len(cells)


def search_crossword(words, minwords, maxdim, trials, seed):
    rng = random.Random(seed)
    best = None
    for t in range(trials):
        placed, grid = try_crossword(words, rng, 30)
        if len(placed) < minwords:
            continue
        r0, c0, r1, c1 = bbox(set(grid))
        h, w = r1 - r0 + 1, c1 - c0 + 1
        if max(h, w) > maxdim:
            continue
        cross = sum(1 for k in grid if True)
        letters = len(grid)
        total_letters = sum(len(x) for x in placed)
        checked = total_letters - letters  # crossings
        score = len(placed) * 100 + sym_score(set(grid)) * 60 + checked * 4 - abs(h - w) * 3 - h * w * 0.2
        if best is None or score > best[0]:
            best = (score, placed, grid, (r0, c0, r1, c1))
    return best



# crossword layouts found by --find-crosswords (row, column, direction) per word; --check validates them
CW_PLACEMENTS = [
    {'XYLOPHONE': (9, 0, 'A'), 'CLARINET': (3, 8, 'D'), 'TRUMPET': (5, 4, 'D'), 'TIMPANI': (5, 4, 'A'), 'TROMBONE': (7, 6, 'D'), 'PICCOLO': (3, 6, 'A'), 'FLUTE': (8, 2, 'D'), 'HARP': (0, 6, 'D'), 'VIOLIN': (1, 10, 'D'), 'TUBA': (11, 4, 'A'), 'CELLO': (14, 5, 'A'), 'OBOE': (3, 12, 'D')},
    {'CRESCENDO': (6, 1, 'A'), 'STACCATO': (3, 5, 'D'), 'FERMATA': (4, 0, 'A'), 'LEGATO': (10, 0, 'A'), 'PIANO': (2, 9, 'D'), 'SHARP': (8, 3, 'A'), 'FORTE': (0, 1, 'D'), 'TEMPO': (2, 6, 'A'), 'CLEF': (8, 1, 'D'), 'STAFF': (8, 3, 'D'), 'REST': (2, 1, 'A'), 'FLAT': (0, 1, 'A'), 'TIE': (0, 7, 'D')},
    {'SNOWFLAKE': (6, 3, 'A'), 'SNOWMAN': (4, 5, 'D'), 'MITTENS': (10, 0, 'A'), 'CHORUS': (1, 3, 'D'), 'ICICLE': (1, 11, 'D'), 'COCOA': (2, 9, 'A'), 'FROST': (4, 2, 'A'), 'BELLS': (4, 8, 'D'), 'CONCERT': (1, 0, 'A'), 'SCARF': (0, 13, 'D'), 'CHOIR': (1, 0, 'D'), 'SLEIGH': (8, 8, 'A'), 'WINTER': (7, 2, 'D')},
    {'CONDUCTOR': (8, 2, 'A'), 'SOLOIST': (5, 3, 'D'), 'DRUMMER': (8, 5, 'D'), 'COMPOSER': (6, 2, 'A'), 'QUARTER': (0, 9, 'D'), 'RHYTHM': (11, 0, 'A'), 'TRIPLET': (3, 8, 'A'), 'WHOLE': (10, 1, 'D'), 'MEASURE': (14, 0, 'A'), 'EIGHTH': (5, 9, 'A'), 'HALF': (5, 14, 'D'), 'METER': (12, 5, 'A'), 'BEAT': (2, 13, 'D')},
]

# ================================================================== puzzle data built from the tables above
WS_SEEDS = [101, 202, 303, 404, 505, 606]


def build_searches():
    out = []
    for i, (title, size, dirs, words) in enumerate(WORD_SEARCHES):
        grid, placed = make_word_search(words, size, dirs, WS_SEEDS[i])
        out.append({"n": i + 1, "title": title, "size": size, "dirs": dirs, "words": words, "grid": grid, "placed": placed})
    return out


def cw_numbering(cells):
    """Standard rule: a cell is numbered if an across or a down entry starts there; numbers run row by row."""
    num, k = {}, 0
    for r, c in sorted(cells):
        starts_a = (r, c - 1) not in cells and (r, c + 1) in cells
        starts_d = (r - 1, c) not in cells and (r + 1, c) in cells
        if starts_a or starts_d:
            k += 1
            num[(r, c)] = k
    return num


def build_crosswords():
    out = []
    for i, ((title, pool), pl) in enumerate(zip(CROSSWORDS, CW_PLACEMENTS)):
        cells = {}
        for w, (r, c, d) in pl.items():
            for k, ch in enumerate(w):
                cells[(r + (k if d == "D" else 0), c + (k if d == "A" else 0))] = ch
        num = cw_numbering(set(cells))
        entries = []
        for w, (r, c, d) in pl.items():
            entries.append({"num": num[(r, c)], "dir": d, "word": w, "r": r, "c": c, "clue": CLUES[w]})
        entries.sort(key=lambda e: (e["dir"], e["num"]))
        rows = max(r for r, c in cells) + 1
        cols = max(c for r, c in cells) + 1
        out.append({"n": i + 1, "title": title, "cells": cells, "num": num, "entries": entries, "rows": rows, "cols": cols})
    return out


SEARCHES = build_searches()
CROSSES = build_crosswords()

# the worked examples on the how-to page and the cover use real, tiny puzzles
EX_CW_WORDS = {"TEMPO": (0, 0, "A"), "TIE": (0, 0, "D"), "PIANO": (0, 3, "D"), "FORTE": (4, 2, "A")}
EX_CW_CLUES = {"TEMPO": "How fast or slow the music goes", "TIE": "Curved line that joins two notes of the same pitch",
               "PIANO": "Italian word that means soft", "FORTE": "Italian word that means loud"}
EX_WS_ROWS = ["BLFXKRWC", "JTEMPONL", "ZAOHUCVE", "QDRSWYNF", "KMVGAEIB"]   # TEMPO across row 2, CLEF down column 8


def ex_cw():
    cells = {}
    for w, (r, c, d) in EX_CW_WORDS.items():
        for k, ch in enumerate(w):
            cells[(r + (k if d == "D" else 0), c + (k if d == "A" else 0))] = ch
    return {"cells": cells, "num": cw_numbering(set(cells)), "rows": 5, "cols": 7}


# ================================================================== page map
P_COVER, P_TEACH, P_HOW, P_WS0 = 1, 2, 3, 4
P_CW0 = P_WS0 + len(SEARCHES)
P_WK0 = P_CW0 + len(CROSSES)
N_WKEY = (len(SEARCHES) + 1) // 2
P_CK0 = P_WK0 + N_WKEY
N_CKEY = (len(CROSSES) + 1) // 2
P_TERMS = P_CK0 + N_CKEY
TOTAL_PAGES = P_TERMS


def ws_page(n):
    return P_WS0 + n - 1


def cw_page(n):
    return P_CW0 + n - 1


def wkey_page(n):
    return P_WK0 + (n - 1) // 2


def ckey_page(n):
    return P_CK0 + (n - 1) // 2


# ================================================================== drawing: icons
def snowflake_g(cx, cy, r, color="#000", sw=1.3):
    out = []
    for k in range(6):
        a = math.radians(60 * k - 90)
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append(f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}"/>')
        bx, by = cx + 0.58 * r * math.cos(a), cy + 0.58 * r * math.sin(a)
        for da in (-50, 50):
            b = math.radians(60 * k - 90 + da)
            out.append(f'<line x1="{bx:.2f}" y1="{by:.2f}" x2="{bx + 0.34 * r * math.cos(b):.2f}" y2="{by + 0.34 * r * math.sin(b):.2f}"/>')
    return f'<g stroke="{color}" stroke-width="{sw}" stroke-linecap="round" fill="none">{"".join(out)}</g>'


def bell_g(cx, cy, r, fill=TINT, sw=1.4):
    """A round sleigh bell: ball, groove, slot and a hanging loop."""
    o = [f'<g stroke="#000" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">']
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>')
    o.append(f'<path d="M{cx - r * 0.96:.2f},{cy + r * 0.28:.2f} Q{cx},{cy + r * 0.62:.2f} {cx + r * 0.96:.2f},{cy + r * 0.28:.2f}" fill="none"/>')
    o.append(f'<line x1="{cx}" y1="{cy + r * 0.45:.2f}" x2="{cx}" y2="{cy + r * 0.92:.2f}"/>')
    o.append(f'<circle cx="{cx}" cy="{cy + r * 0.38:.2f}" r="{r * 0.1:.2f}" fill="#000"/>')
    o.append(f'<circle cx="{cx}" cy="{cy - r - r * 0.26:.2f}" r="{r * 0.26:.2f}" fill="#fff"/>')
    o.append("</g>")
    return "".join(o)


def note_g(cx, cy, size, eighth=False, fill="#000"):
    cp = 0xE1D7 if eighth else 0xE1D5      # noteEighthUp / noteQuarterUp (Bravura glyphs carry their own stems and flags)
    return f'<text x="{cx - (0.25 if eighth else 0.15) * size:.2f}" y="{cy:.2f}" font-family="Bravura" font-size="{size}" fill="{fill}">&#x{cp:X};</text>'


def compass_g(cx, cy, r, color="#000"):
    o = [f'<g stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" fill="none">']
    for k in range(8):
        a = math.radians(45 * k)
        x0, y0 = cx + 0.28 * r * math.cos(a), cy + 0.28 * r * math.sin(a)
        x1, y1 = cx + r * math.cos(a), cy + r * math.sin(a)
        o.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}"/>')
        for da in (155, -155):
            b = a + math.radians(da)
            o.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x1 + 0.26 * r * math.cos(b):.2f}" y2="{y1 + 0.26 * r * math.sin(b):.2f}"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{0.2 * r:.2f}" fill="{ACCENT}" stroke="none"/>')
    o.append("</g>")
    return "".join(o)


ICONS = {
    "snowflake": ("-14 -14 28 28", lambda: snowflake_g(0, 0, 10, ACCENT, 1.4)),
    "bell": ("-14 -18 28 32", lambda: bell_g(0, 1, 9.5)),
    "note": ("-16 -24 32 44", lambda: note_g(0, 8, 28)),
    "eighth": ("-16 -24 32 44", lambda: note_g(0, 8, 28, True)),
    "compass": ("-26 -26 52 52", lambda: compass_g(0, 0, 21)),
}


def icon_svg(name, w, h=None, extra=""):
    vb, fn = ICONS[name]
    vw, vh = [float(x) for x in vb.split()[2:]]
    h = h if h else w * vh / vw
    return f'<svg class="icon" data-icon="{name}" width="{w}" height="{h:.2f}" viewBox="{vb}" {extra}>{fn()}</svg>'


def deco_header():
    parts = [icon_svg("snowflake", 24), icon_svg("bell", 24), icon_svg("eighth", 22)]
    return f'<div class="icons">{"".join(parts)}</div>'


# ================================================================== drawing: word search and crossword grids
FONT_SS = "'Source Sans 3', sans-serif"


def ws_svg(ws, key=False, w_pt=440.0, grid=None, placed=None, cls="wsgrid", mini=False, unit="pt"):
    """Letters carry data-r/data-c; the key adds one capsule per word with its end cells in data-*."""
    grid = grid if grid is not None else ws["grid"]
    placed = placed if placed is not None else ws["placed"]
    nr, nc = len(grid), len(grid[0])
    u = 10.0
    W, H = nc * u, nr * u
    k = w_pt / W
    lw = 1.25 / k if not mini else 0.8 / k
    fs = 6.2 if not key else 6.4
    o = [f'<svg class="{cls}" data-ws="{ws.get("n", 0)}" data-key="{int(key)}" width="{w_pt:.1f}{unit}" height="{H * k:.1f}{unit}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']
    o.append(f'<rect x="{lw / 2}" y="{lw / 2}" width="{W - lw}" height="{H - lw}" rx="{1.2}" fill="#fff" stroke="#000" stroke-width="{lw}"/>')
    inword = set()
    if key:
        for w, (r, c, d) in placed.items():
            dr, dc = DIRS[d]
            e = len(w) - 1
            for i in range(len(w)):
                inword.add((r + dr * i, c + dc * i))
            o.append(f'<line class="cap" data-word="{w}" data-r0="{r}" data-c0="{c}" data-r1="{r + dr * e}" data-c1="{c + dc * e}" '
                     f'x1="{c * u + u / 2:.2f}" y1="{r * u + u / 2:.2f}" x2="{(c + dc * e) * u + u / 2:.2f}" y2="{(r + dr * e) * u + u / 2:.2f}" '
                     f'stroke="{ACCENT}" stroke-opacity=".42" stroke-width="{u * 0.8:.2f}" stroke-linecap="round"/>')
    for r in range(nr):
        for c in range(nc):
            hot = (r, c) in inword
            col = "#000" if (not key or hot) else "#8a8a8a"
            wt = 700 if (not key or hot) else 400
            o.append(f'<text class="ch" data-r="{r}" data-c="{c}" x="{c * u + u / 2:.2f}" y="{r * u + u / 2 + fs * 0.34:.2f}" text-anchor="middle" '
                     f'font-family="{FONT_SS}" font-weight="{wt}" font-size="{fs}" fill="{col}">{grid[r][c]}</text>')
    o.append("</svg>")
    return "".join(o)


# crossword cell metrics (cell = 10 units): clue number small in the top-left corner, letter centred and shifted down/right
CW_NUM_X, CW_NUM_Y, CW_NUM_FS = 0.8, 3.3, 3.0
CW_LET_X, CW_LET_Y, CW_LET_FS = 5.7, 8.6, 5.6


def cw_svg(cw, key=False, w_pt=400.0, cls="cwgrid", max_h_pt=None, unit="pt"):
    cells, num = cw["cells"], cw["num"]
    nr, nc = cw["rows"], cw["cols"]
    u = 10.0
    W, H = nc * u, nr * u
    k = w_pt / W
    if max_h_pt and H * k > max_h_pt:
        k = max_h_pt / H
        w_pt = W * k
    lw = 1.1 / k
    o = [f'<svg class="{cls}" data-cw="{cw.get("n", 0)}" data-key="{int(key)}" data-rows="{nr}" data-cols="{nc}" width="{w_pt:.1f}{unit}" height="{H * k:.1f}{unit}" viewBox="{-lw} {-lw} {W + 2 * lw} {H + 2 * lw}" xmlns="http://www.w3.org/2000/svg">']
    for (r, c), ch in sorted(cells.items()):
        o.append(f'<rect class="cwc" data-r="{r}" data-c="{c}" x="{c * u}" y="{r * u}" width="{u}" height="{u}" fill="#fff" stroke="#000" stroke-width="{lw}"/>')
    for (r, c), n in sorted(num.items()):
        o.append(f'<text class="cwn" data-r="{r}" data-c="{c}" x="{c * u + CW_NUM_X}" y="{r * u + CW_NUM_Y}" font-family="{FONT_SS}" font-weight="600" font-size="{CW_NUM_FS}" fill="#000">{n}</text>')
    if key:
        for (r, c), ch in sorted(cells.items()):
            o.append(f'<text class="cwl" data-r="{r}" data-c="{c}" x="{c * u + CW_LET_X}" y="{r * u + CW_LET_Y}" text-anchor="middle" font-family="{FONT_SS}" font-weight="700" font-size="{CW_LET_FS}" fill="#000">{ch}</text>')
    o.append("</svg>")
    return "".join(o)


# ================================================================== CSS / page parts
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
.top .t { font-size: 23pt; }
.top .t .tt { display: inline-block; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.top .deco { flex: 1; display: flex; justify-content: center; align-items: center; padding-bottom: 2pt; }
.icons { display: flex; gap: 4pt; align-items: center; }
.icon { display: block; }
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 18pt; font-size: 12pt; margin: 9pt 0 5pt; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.d { flex: 0 0 1.6in; }
.how { font-size: 11.5pt; margin: 2pt 0 8pt; line-height: 1.3; text-wrap: pretty; }
.how b { font-weight: 700; }
.pz { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: space-between; padding: 2pt 0 12pt; }
.wlist { width: 100%; border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 12pt 8pt; }
.wlist .wt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11.5pt; letter-spacing: .03em; margin-bottom: 4pt; display: flex; justify-content: space-between; }
.wlist .wt span { font-weight: 300; text-transform: none; font-size: 10.5pt; letter-spacing: 0; }
.wl { display: grid; grid-auto-flow: column; grid-template-columns: repeat(4, 1fr); gap: 3pt 10pt; }
.wl .w { font-family: 'Source Sans 3'; font-weight: 700; font-size: 11.5pt; letter-spacing: .06em; display: flex; align-items: center; gap: 6pt; white-space: nowrap; }
.wl .cb { display: inline-block; width: 9pt; height: 9pt; border: 1.1pt solid #000; border-radius: 2pt; flex: none; }
.cluebox { width: 100%; display: flex; gap: 18pt; }
.cluebox .col { flex: 1; }
.cluebox h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; letter-spacing: .04em; margin: 0 0 3pt; border-bottom: 1.1pt solid #000; padding-bottom: 2pt; }
.cluebox ol { list-style: none; margin: 0; padding: 0; }
.cluebox li { font-size: 10.5pt; line-height: 1.22; margin: 0 0 2.6pt; padding-left: 17pt; position: relative; text-wrap: pretty; }
.cluebox li b { position: absolute; left: 0; width: 14pt; text-align: right; font-family: 'Oswald'; font-weight: 700; color: ACCENT; }
.cluebox li .len { color: #444; white-space: nowrap; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.keyblock { margin-top: 10pt; border: 1.1pt solid #000; border-radius: 7pt; padding: 6pt 10pt 8pt; display: flex; flex-direction: column; }
.keyblock .kt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; border-bottom: 1pt solid #000; padding-bottom: 2pt; margin-bottom: 6pt; display: flex; justify-content: space-between; }
.keyblock .kt span { font-weight: 300; text-transform: none; font-size: 10.5pt; }
.kbody { display: flex; gap: 16pt; align-items: flex-start; }
.klist { flex: 1; font-size: 9.5pt; line-height: 1.25; }
.klist .kr { display: flex; justify-content: space-between; gap: 6pt; border-bottom: .6pt solid #bbb; padding: 1.2pt 0; white-space: nowrap; }
.klist .kr b { font-family: 'Source Sans 3'; font-weight: 700; letter-spacing: .05em; }
.klist .kr span { color: #333; }
.klist h4 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 10pt; margin: 0 0 2pt; letter-spacing: .04em; color: ACCENT; }
.klist .two { display: flex; gap: 12pt; }
.klist .two > div { flex: 1; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 13pt 0 4pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 11pt; line-height: 1.38; margin: 0 0 5pt; text-wrap: pretty; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3.5pt 6pt; text-align: left; vertical-align: middle; }
.doc td.nw { white-space: nowrap; }
.doc table.glance td, .doc table.glance th { padding: 2.2pt 6pt; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.steps { display: flex; gap: 12pt; margin-top: 8pt; }
.step { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; }
.step .n { display: inline-block; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 12pt; border-radius: 50%; width: 20pt; height: 20pt; line-height: 20pt; text-align: center; margin-right: 6pt; }
.step b { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 11.5pt; letter-spacing: .02em; }
.step p { margin: 4pt 0 3pt !important; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; }
.small { font-size: 9.5pt !important; color: #333; }
.tbox { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 11pt 4pt; }
.tbox h2 { margin-top: 0; }
.howsec { display: flex; gap: 20pt; align-items: center; margin: 4pt 0 6pt; }
.howsec .st { flex: 1; }
.howsec .ex { flex: none; text-align: center; }
.howsec .ex .cap { font-family: 'Oswald'; font-weight: 300; font-size: 10pt; margin-top: 3pt; }
.stp { display: flex; gap: 8pt; align-items: flex-start; margin-bottom: 6pt; }
.stp .n { flex: none; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 12pt; border-radius: 50%; width: 20pt; height: 20pt; line-height: 20pt; text-align: center; }
.stp p { margin: 0 !important; font-size: 11pt; line-height: 1.32; text-wrap: pretty; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 78pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def header(sub, tag, label, ak=False):
    return (f'<div class="top"><div class="h t"><span class="tt">{TITLE}</span><small>{escape(sub)}</small></div>'
            f'<div class="deco">{deco_header()}</div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{escape(tag)}</div><div class="ln">{escape(label)}</div></div></div>')


DIR_TEXT = {
    1: "Words go across (left to right) and down (top to bottom).",
    2: "Words go across, down and diagonally (down and to the right).",
    3: "Words go across, down and diagonally, either up or down.",
    4: "Words go across, down and diagonally. Some words go backwards, from right to left.",
    5: "Words can go in any of the 8 directions, so some run backwards.",
    6: "Words can go in any of the 8 directions, so some run backwards.",
}


STATED_DIRS = {1: {"right", "down"}, 2: {"right", "down", "down-right"}, 3: {"right", "down", "down-right", "up-right"},
               4: {"right", "down", "down-right", "up-right", "left"}, 5: set(DIR_NAME.values()), 6: set(DIR_NAME.values())}


def wm_div(watermark):
    return '<div class="wm">PREVIEW</div>' if watermark else ""


WS_W = {12: 470.0, 13: 450.0, 14: 440.0, 15: 436.0}


def ws_page_html(ws, watermark=False):
    n = ws["n"]
    nw = len(ws["words"])
    words = sorted(ws["words"])
    items = "".join(f'<div class="w" data-w="{w}"><span class="cb"></span>{w}</div>' for w in words)
    rows = -(-nw // 4)
    return (f'<section class="page" data-kind="ws" data-n="{n}">{wm_div(watermark)}'
            + header(f"Word Search {n}. {ws['title']}", f"WORD SEARCH {n}", f"{ws['size']} × {ws['size']} grid · {nw} words")
            + f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="how"><b>Find and circle all {nw} words in the word list.</b> {DIR_TEXT[n]} Check off each word when you find it.</div>'
            f'<div class="pz">{ws_svg(ws, False, WS_W[ws['size']])}'
            f'<div class="wlist"><div class="wt">Word list<span>{nw} words to find</span></div>'
            f'<div class="wl" style="grid-template-rows:repeat({rows}, auto)">{items}</div></div></div>'
            + foot(COPY, f"Answer key on page {wkey_page(n)} · Page {ws_page(n)}") + "</section>")


def cw_clue_html(cw, key=False):
    cols = []
    for d, name in (("A", "Across"), ("D", "Down")):
        lis = "".join(
            f'<li data-dir="{d}" data-n="{e["num"]}" data-len="{len(e["word"])}"><b>{e["num"]}</b>{escape(e["clue"])} <span class="len">({len(e["word"])})</span></li>'
            for e in cw["entries"] if e["dir"] == d)
        cols.append(f'<div class="col"><h3>{name}</h3><ol>{lis}</ol></div>')
    return f'<div class="cluebox">{"".join(cols)}</div>'


def cw_page_html(cw, watermark=False):
    n = cw["n"]
    ne = len(cw["entries"])
    na = sum(1 for e in cw["entries"] if e["dir"] == "A")
    return (f'<section class="page" data-kind="cw" data-n="{n}">{wm_div(watermark)}'
            + header(f"Crossword {n}. {cw['title']}", f"CROSSWORD {n}", f"{na} across · {ne - na} down")
            + f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="how"><b>Use the clues to fill in the crossword.</b> Write one letter in each box. '
            f'The number in a box tells you which clue starts there, and the number in brackets is the number of letters.</div>'
            f'<div class="pz">{cw_svg(cw, False, 470.0, max_h_pt=350.0)}{cw_clue_html(cw)}</div>'
            + foot(COPY, f"Answer key on page {ckey_page(n)} · Page {cw_page(n)}") + "</section>")


def wkey_block(ws):
    n = ws["n"]
    rows = "".join(
        f'<div class="kr" data-word="{w}" data-r="{r}" data-c="{c}" data-d="{d}"><b>{w}</b><span>row {r + 1}, column {c + 1}, {DIR_NAME[d]}</span></div>'
        for w, (r, c, d) in sorted(ws["placed"].items()))
    return (f'<div class="keyblock" data-kind="wkey" data-n="{n}"><div class="kt"><div>Word Search {n}<span> · {escape(ws["title"])}</span></div><span>puzzle on page {ws_page(n)}</span></div>'
            f'<div class="kbody">{ws_svg(ws, True, 252.0)}<div class="klist">{rows}</div></div></div>')


def ckey_block(cw):
    n = cw["n"]
    cols = []
    for d, name in (("A", "Across"), ("D", "Down")):
        rows = "".join(f'<div class="kr" data-dir="{d}" data-n="{e["num"]}" data-word="{e["word"]}"><b>{e["num"]}</b><span>{e["word"]}</span></div>'
                       for e in cw["entries"] if e["dir"] == d)
        cols.append(f'<div><h4>{name}</h4>{rows}</div>')
    return (f'<div class="keyblock" data-kind="ckey" data-n="{n}"><div class="kt"><div>Crossword {n}<span> · {escape(cw["title"])}</span></div><span>puzzle on page {cw_page(n)}</span></div>'
            f'<div class="kbody">{cw_svg(cw, True, 268.0, max_h_pt=262.0)}<div class="klist"><div class="two">{"".join(cols)}</div></div></div></div>')


def wkey_page_html(pg, watermark=False):
    ids = [n for n in range(1, len(SEARCHES) + 1) if wkey_page(n) == pg]
    blocks = "".join(wkey_block(SEARCHES[n - 1]) for n in ids)
    lab = f"Word searches {ids[0]}" + (f" and {ids[-1]}" if len(ids) > 1 else "")
    return (f'<section class="page" data-kind="wkeypage">{wm_div(watermark)}' + header("Answer Key: word searches", "ANSWER KEY", lab, True)
            + f'<div class="how" style="margin:8pt 0 0">Each word is highlighted in the grid. The list says where each word starts: the row from the top and the column from the left.</div>'
            + blocks + '<div style="flex:1"></div>' + foot(COPY, f"Answer key · Page {pg}") + "</section>")


def ckey_page_html(pg, watermark=False):
    ids = [n for n in range(1, len(CROSSES) + 1) if ckey_page(n) == pg]
    blocks = "".join(ckey_block(CROSSES[n - 1]) for n in ids)
    lab = f"Crosswords {ids[0]}" + (f" and {ids[-1]}" if len(ids) > 1 else "")
    return (f'<section class="page" data-kind="ckeypage">{wm_div(watermark)}' + header("Answer Key: crosswords", "ANSWER KEY", lab, True)
            + blocks + '<div style="flex:1"></div>' + foot(COPY, f"Answer key · Page {pg}") + "</section>")


# ---- cover art
def cover_art(width=900, height=470):
    o = [f'<svg class="coverart" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:auto">']
    o.append(f'<ellipse cx="450" cy="{height - 58}" rx="420" ry="40" fill="{TINT}" stroke="#000" stroke-width="3"/>')
    # word search card
    grid, placed = make_word_search(["FORTE", "BELLS", "TEMPO"], 8, ["R", "D", "DR"], 77)
    ws = {"n": 0}
    o.append('<g transform="rotate(-3 235 215)">')
    o.append('<rect x="64" y="66" width="342" height="324" rx="16" fill="#000"/>')
    o.append('<rect x="56" y="58" width="342" height="324" rx="16" fill="#fff" stroke="#000" stroke-width="3"/>')
    inner = ws_svg(ws, True, 288.0, grid, placed, cls="miniws", unit="")
    o.append(f'<g transform="translate(83 76)">{inner}</g>')
    o.append("</g>")
    # crossword card
    ex = ex_cw()
    o.append('<g transform="rotate(3 665 215)">')
    o.append('<rect x="496" y="82" width="372" height="290" rx="16" fill="#000"/>')
    o.append('<rect x="488" y="74" width="372" height="290" rx="16" fill="#fff" stroke="#000" stroke-width="3"/>')
    inner = cw_svg({"cells": ex["cells"], "num": ex["num"], "rows": 5, "cols": 7, "n": 0}, True, 336.0, cls="minicw", unit="")
    o.append(f'<g transform="translate(506 100)">{inner}</g>')
    o.append("</g>")
    # two sleigh bells on a string between the cards
    o.append(f'<line x1="450" y1="96" x2="450" y2="196" stroke="#000" stroke-width="3" stroke-linecap="round"/>')
    o.append(f'<line x1="450" y1="196" x2="450" y2="286" stroke="#000" stroke-width="3" stroke-linecap="round"/>')
    o.append(f'<g transform="translate(450 62)">{snowflake_g(0, 0, 30, ACCENT, 3)}</g>')
    o.append(f'<g transform="translate(450 232)">{bell_g(0, 0, 27, TINT, 3.2)}</g>')
    o.append(f'<g transform="translate(450 330)">{bell_g(0, 0, 21, "#fff", 3.2)}</g>')
    o.append(f'<g transform="translate(30 40)">{snowflake_g(0, 0, 16, "#000", 2.6)}</g>')
    o.append(f'<g transform="translate(868 40)">{snowflake_g(0, 0, 20, ACCENT, 2.8)}</g>')
    o.append(f'<g transform="translate(26 210)">{snowflake_g(0, 0, 12, ACCENT, 2.4)}</g>')
    o.append(f'<g transform="translate(878 395)">{snowflake_g(0, 0, 11, "#000", 2.4)}</g>')
    o.append("</svg>")
    return "".join(o)


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:7.3in">{cover_art()}</div>'
            f'<div class="ctitle"><div class="a">HOLIDAY MUSIC</div><div class="b">WORD PUZZLES</div>'
            f'<div class="c">Word searches and crosswords · instruments, symbols and winter music words</div></div>'
            f'<div class="cband">Grades 3–6 <em>·</em> 6 word searches <em>·</em> 4 crosswords <em>·</em> answer keys</div></section>')


# ---- teacher notes
def table_rows():
    rows = []
    for ws in SEARCHES:
        n = ws["n"]
        gr = "3–4" if n <= 2 else "4–5" if n <= 4 else "5–6"
        rows.append(f'<tr><td class="nw"><b>Word Search {n}</b></td><td>{escape(ws["title"])}</td><td class="nw">{ws["size"]} × {ws["size"]}</td>'
                    f'<td class="nw">{len(ws["words"])} words</td><td class="nw">{gr}</td><td class="nw">{ws_page(n)} / {wkey_page(n)}</td></tr>')
    for cw in CROSSES:
        n = cw["n"]
        gr = {1: "3–4", 2: "4–5", 3: "3–4", 4: "5–6"}[n]
        rows.append(f'<tr><td class="nw"><b>Crossword {n}</b></td><td>{escape(cw["title"])}</td><td class="nw">{cw["rows"]} × {cw["cols"]}</td>'
                    f'<td class="nw">{len(cw["entries"])} clues</td><td class="nw">{gr}</td><td class="nw">{cw_page(n)} / {ckey_page(n)}</td></tr>')
    return "".join(rows)


CW_GRID_RANGE = f"up to {max(max(c['rows'], c['cols']) for c in CROSSES)}"
CW_CLUE_RANGE = f"{min(len(c['entries']) for c in CROSSES)} to {max(len(c['entries']) for c in CROSSES)} clues"


def teacher_page():
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} · 6 word searches and 4 crosswords · grades 3–6</div></div>'
            f'<div class="cols"><div>'
            f'<h2>What is included</h2><ul>'
            f'<li>6 word searches with grids from 12 × 12 to 15 × 15 and 12 to 14 words each. Search 1: across and down. Search 2 adds down-right diagonals, 3 adds up-right diagonals, 4 adds backwards words, and 5 and 6 use all 8 directions.</li>'
            f'<li>4 crosswords with numbered across and down clues, each with its letter count.</li>'
            f'<li>A full answer key for every puzzle: word search solutions are highlighted and crossword solutions are filled in. Page 3 is a how-to page for students.</li>'
            f'</ul>'
            f'<h2>Ways to use the puzzles</h2><ul>'
            f'<li><b>Early finishers.</b> Keep a folder of copies at the back of the room. Students take one puzzle, then check it with the key.</li>'
            f'<li><b>Centers.</b> Put the puzzles in a center with pencils and highlighters. Partners can work on one puzzle together.</li>'
            f'<li><b>Sub plans.</b> Leave a set of puzzles and the answer key pages. No music skills are needed to supervise.</li>'
            f'</ul>'
            f'</div><div>'
            f'<h2>Choosing a puzzle</h2><ul>'
            f'<li><b>Word Searches 1–2:</b> 1 is across and down, 2 adds down-right diagonals. Grades 3–4.</li>'
            f'<li><b>Word Searches 3–4:</b> 3 adds up-right diagonals, 4 adds backwards words. Grades 4–5.</li>'
            f'<li><b>Word Searches 5–6:</b> all 8 directions. Grades 5–6.</li>'
            f'<li><b>Crosswords 1–4:</b> grades 3–4, 4–5, 3–4 and 5–6.</li></ul>'
            f'<p class="small">Grade bands are suggestions. Students who need more support can tick words off the word list as they go.</p>'
            f'<h2>Skills practiced</h2><p>Music vocabulary, spelling, careful reading of clues and scanning a grid. The puzzles use instruments of the orchestra and band, music symbols and terms, winter music words, rhythm words and music jobs. No standards codes are listed: match the skills to your own curriculum.</p>'
            f'<h2>Good to know</h2><p class="small">The content is winter themed and non-denominational. No songs, lyrics, brands or characters are used.</p>'
            f'</div></div>'
            f'<h2>Every puzzle at a glance</h2>'
            f'<table class="glance"><colgroup><col style="width:20%"><col style="width:33%"><col style="width:12%"><col style="width:13%"><col style="width:10%"><col style="width:12%"></colgroup>'
            f'<tr><th>Puzzle</th><th>Theme</th><th>Grid</th><th>Count</th><th>Grades</th><th>Page / key</th></tr>{table_rows()}</table>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 2")}</section>')


def how_page():
    ws_ex = {"n": 0, "grid": [list(r) for r in EX_WS_ROWS], "placed": {"TEMPO": (1, 1, "R"), "CLEF": (0, 7, "D")}}
    ex = ex_cw()
    cwx = {"cells": ex["cells"], "num": ex["num"], "rows": ex["rows"], "cols": ex["cols"], "n": 0}
    cwk = {"cells": ex["cells"], "num": ex["num"], "rows": ex["rows"], "cols": ex["cols"], "n": 0}
    return (f'<section class="page doc"><div class="rule"><h1>How to Solve</h1>'
            f'<div class="l" style="font-size:13pt">Read this page first, then pick a puzzle.</div></div>'
            f'<div class="tbox"><h2>Word searches</h2><div class="howsec"><div class="st">'
            f'<div class="stp"><span class="n">1</span><p>Read the word list. Pick one word and look for its first letter in the grid.</p></div>'
            f'<div class="stp"><span class="n">2</span><p>Check the letters next to it in every direction the puzzle allows. The word is a straight line.</p></div>'
            f'<div class="stp"><span class="n">3</span><p>Circle the word and check it off the list. Each word is hidden exactly once.</p></div>'
            f'</div><div class="ex">{ws_svg(ws_ex, True, 190.0, ws_ex["grid"], ws_ex["placed"], cls="exws")}'
            f'<div class="cap">Example: TEMPO goes across and CLEF goes down.</div></div></div>'
            f'<div class="howsec"><div class="st"><p style="font-size:11pt;line-height:1.32;margin:0">Harder puzzles use all 8 directions. Words can also run backwards, so look for them from right to left and from bottom to top.</p></div>'
            f'<div class="ex">{icon_svg("compass", 70)}</div></div></div>'
            f'<div class="tbox" style="margin-top:12pt"><h2>Crosswords</h2><div class="howsec"><div class="st">'
            f'<div class="stp"><span class="n">1</span><p>Find the number in the grid. Across clues go left to right and down clues go top to bottom.</p></div>'
            f'<div class="stp"><span class="n">2</span><p>Read the clue and count the letters. The number in brackets tells you how many boxes to fill.</p></div>'
            f'<div class="stp"><span class="n">3</span><p>Write one letter in each box. Letters in crossing words must match, so use them to check your answers.</p></div>'
            f'</div><div class="ex">{cw_svg(cwk, True, 200.0, cls="excw")}'
            f'<div class="cap">Example, solved. Box 1 starts TEMPO across and TIE down.</div></div></div>'
            f'<div class="cols" style="gap:20pt"><div style="flex:1"><h2 style="margin-top:4pt">Across</h2><p class="small" style="margin:0"><b>1</b> How fast or slow the music goes (5)<br><b>3</b> Italian word that means loud (5)</p></div>'
            f'<div style="flex:1"><h2 style="margin-top:4pt">Down</h2><p class="small" style="margin:0"><b>1</b> Curved line that joins two notes of the same pitch (3)<br><b>2</b> Italian word that means soft (5)</p></div></div></div>'
            f'<div class="tbox" style="margin-top:12pt"><h2>Tips</h2><ul style="margin:0 0 2pt">'
            f'<li>In a word search, look for rare letters such as X, Y, Z and K first.</li>'
            f'<li>In a crossword, start with the clues you know and fill in short answers first.</li>'
            f'<li>When you are stuck, move on. Crossing letters from other answers will help.</li></ul></div>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 3")}</section>')


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
            f'<h2>Credits</h2><ul>'
            f'<li>Puzzles, icons and answer keys: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>What is in this file</h2><p>Page 1 cover, page 2 teacher notes, page 3 how to solve, pages {P_WS0}–{P_CW0 - 1} the 6 word searches, '
            f'pages {P_CW0}–{P_WK0 - 1} the 4 crosswords, pages {P_WK0}–{P_TERMS - 1} the answer keys and page {P_TERMS} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def full_pages():
    pages = [cover_page(), teacher_page(), how_page()]
    pages += [ws_page_html(w) for w in SEARCHES]
    pages += [cw_page_html(c) for c in CROSSES]
    pages += [wkey_page_html(P_WK0 + i) for i in range(N_WKEY)]
    pages += [ckey_page_html(P_CK0 + i) for i in range(N_CKEY)]
    pages.append(terms_page())
    return pages


# preview PDF: student word search 4 and its key page, student crossword 2 and its key page (all watermarked)
PV_WS, PV_CW = 4, 2


def preview_pages():
    return [ws_page_html(SEARCHES[PV_WS - 1], True), wkey_page_html(wkey_page(PV_WS), True),
            cw_page_html(CROSSES[PV_CW - 1], True), ckey_page_html(ckey_page(PV_CW), True)]


# ================================================================== square images
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
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 24px; text-align: center; margin-top: 18px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 20px; margin-top: 2px; }
.swm { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
       color: rgba(0,0,0,.13); white-space: nowrap; letter-spacing: .06em; pointer-events: none; z-index: 5; }
.tile { width: 178px; display: flex; flex-direction: column; align-items: center; }
.tile .art { width: 178px; height: 178px; border: 2px solid #000; border-radius: 8px; display: flex; align-items: center; justify-content: center; background: #fff; }
.tile .tg { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 17px; margin-top: 10px; letter-spacing: .02em; }
.tile .tn { font-family: 'Oswald'; font-weight: 300; font-size: 16px; text-align: center; line-height: 1.15; margin-top: 2px; text-wrap: balance; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="width:880px">{cover_art()}</div>'
        f'<div><div class="hd" style="font-size:66px">Holiday Music</div>'
        f'<div class="hd" style="font-size:124px">Word Puzzles</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">Word searches and crosswords with answer keys</div></div>'
        f'</div><div class="band">Grades 3–6 <em>·</em> 6 word searches <em>·</em> 4 crosswords</div></div>')


def preview_square_1(a, b):
    caps = ("Word searches", f"6 puzzles, 12 × 12 up to 15 × 15"), ("Crosswords", "4 puzzles with numbered clues")
    pair = "".join(
        f'<div style="width:420px"><div class="shot"><img src="{src}"></div><div class="lbl">{t}<span>{s}</span></div></div>'
        for src, (t, s) in zip((a, b), caps))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:24px">10 music puzzles</div>'
        f'<div class="sub" style="font-size:28px;margin-top:8px">Instruments, symbols, winter words and rhythm</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px">{pair}</div></div>'
        f'<div class="band">Grades 3–6 <em>·</em> early finishers <em>·</em> centers <em>·</em> sub plans</div></div>')


def preview_square_2(a, b):
    caps = ("Word search key", "Every word highlighted"), ("Crossword key", "Every answer filled in")
    pair = "".join(
        f'<div style="width:420px"><div class="shot"><img src="{src}"></div><div class="lbl">{t}<span>{s}</span></div></div>'
        for src, (t, s) in zip((a, b), caps))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:24px">Answer keys included</div>'
        f'<div class="sub" style="font-size:28px;margin-top:8px">A key for every word search and every crossword</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px">{pair}</div></div>'
        f'<div class="band">Check in seconds <em>·</em> easy to grade</div></div>')


def preview_square_3():
    tiles = []
    for ws in SEARCHES:
        art = ws_svg(ws, False, 150.0, cls="tilews", mini=True, unit="px")
        tiles.append((f"Word Search {ws['n']}", ws["title"], art, f'{ws["size"]} × {ws["size"]} · {len(ws["words"])} words'))
    for cw in CROSSES:
        art = cw_svg(cw, False, 150.0, cls="tilecw", max_h_pt=150.0, unit="px")
        tiles.append((f"Crossword {cw['n']}", cw["title"], art, f'{len(cw["entries"])} clues'))
    cells = "".join(f'<div class="tile"><div class="art">{art}</div><div class="tg">{tg}</div><div class="tn">{escape(t)}<br>{extra}</div></div>'
                    for tg, t, art, extra in tiles)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:24px">Ten different puzzles</div>'
        f'<div class="sub" style="font-size:28px;margin-top:8px">Easier to harder grids and four themed crosswords</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:grid;grid-template-columns:repeat(5,178px);gap:26px 18px">{cells}</div></div>'
        f'<div class="swm" style="font-size:230px;left:50%;top:54%">PREVIEW</div>'
        f'<div class="band">Six word searches <em>·</em> four crosswords</div></div>')


# ================================================================== render / build
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


def icons_html():
    cells = "".join(f'<div class="ic" style="left:{20 + (i % 5) * 150}px;top:{20 + (i // 5) * 150}px">{icon_svg(n, 120, 120, "")}</div>' for i, n in enumerate(ICONS))
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:#fff}}'
            f'.ic{{position:absolute;width:120px;height:120px}}.ic svg{{display:block;width:120px;height:120px}}</style></head><body>{cells}</body></html>')


def upload_md():
    wsl = "\n".join(f"  - Word Search {w['n']}, {w['title']}: {w['size']} × {w['size']} grid, {len(w['words'])} words" for w in SEARCHES)
    cwl = "\n".join(f"  - Crossword {c['n']}, {c['title']}: {len(c['entries'])} clues" for c in CROSSES)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 052)

These fields follow the order of TpT's "Add a resource" form. Winter theme: build window is December. Never put Winter, Snow, Holiday or December in the title field (TpT's Seasonal Titles notice).

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words. If TpT accepts it, the preferred title is "{PREFERRED_TITLE}".

## 2. Description

```
Holiday Music Word Puzzles: 6 word searches and 4 crosswords for the music classroom. Students hunt for instruments, music symbols, winter music words, rhythm words and music jobs, then fill in crosswords with short, clear clues. Every puzzle has an answer key. The theme is winter and non-denominational, for music classes in grades 3 to 6.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes with ideas for early finishers, centers and sub plans (1 page)
• How to solve a word search and a crossword, with worked examples (1 page)
• 6 word searches, one per page (6 pages), with grids from 12 × 12 to 15 × 15 and 12 to 14 words each:
{wsl}
• 4 crosswords with numbered across and down clues, one per page (4 pages):
{cwl}
• Answer keys: word search solutions highlighted, 2 per page (3 pages)
• Answer keys: crossword solutions filled in, 2 per page (2 pages)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Word search 1 hides words across and down, search 2 adds down-right diagonals, search 3 adds up-right diagonals, search 4 adds backwards (right-to-left) words, and searches 5 and 6 use all 8 directions. Each word is hidden exactly once. In the crosswords every clue has one answer and shows its letter count. Good for early finishers, centers, sub plans, warm-ups and homework.

• Grades 3–6 (choose the puzzles that fit your students)
• Prints well in black and white
• No songs, lyrics, brands or copyrighted characters

{DISCLOSURE}
```

## 3. Grades

3, 4, 5, 6.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

- Cover: 1
- Teacher notes: 1
- How to solve: 1
- Word searches (1–6): {len(SEARCHES)}
- Crosswords (1–4): {len(CROSSES)}
- Word search answer keys: {N_WKEY}
- Crossword answer keys: {N_CKEY}
- Terms of use and credits: 1
- Total: {TOTAL_PAGES}

## 6. Standards

None cited. The teacher notes describe the skills and ask teachers to match them to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3–5).

## 8. Preview

Paid. Preview PDF: word search 4 (winter music words) with the answer key page for word searches 3 and 4, and crossword 2 (music symbols and terms) with the answer key page for crosswords 1 and 2, all watermarked.

## 9. Before you click publish

- [ ] Season: December (winter). Build for 2 to 8 weeks ahead.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {
        "price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
        "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS, "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png",
                  "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in range(1, 5):
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF,
                        os.path.join(BUILD, f"pv{i}")], check=True)
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1("pv1.png", "pv3.png")),
          write("p2.html", preview_square_2("pv2.png", "pv4.png")), write("p3.html", preview_square_3())]
    outs = [COVER_PNG] + PREVIEW_PNGS
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, outs)])
    with open(UPLOAD, "w") as f:
        f.write(upload_md())
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(), f, indent=2)
        f.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


# ================================================================== checks
# Independent solver for the word searches: reads the grid back from the rendered HTML, builds every line in all 8 directions
# as a string and counts overlapping occurrences. It shares no code with make_word_search / find_all.
def solve_lines(grid, word):
    n, m = len(grid), len(grid[0])
    found = []
    for (dr, dc, name) in ((0, 1, "right"), (1, 0, "down"), (1, 1, "down-right"), (-1, 1, "up-right"),
                           (0, -1, "left"), (-1, 0, "up"), (-1, -1, "up-left"), (1, -1, "down-left")):
        # every start cell on the border that a line in this direction can begin from
        starts = [(r, c) for r in range(n) for c in range(m) if not (0 <= r - dr < n and 0 <= c - dc < m)]
        for (r0, c0) in starts:
            cells, r, c = [], r0, c0
            while 0 <= r < n and 0 <= c < m:
                cells.append((r, c))
                r, c = r + dr, c + dc
            s = "".join(grid[a][b] for a, b in cells)
            i = s.find(word)
            while i != -1:
                found.append((cells[i], cells[i + len(word) - 1], name))
                i = s.find(word, i + 1)
    return found


def first_svg(text, cls):
    return re.search(rf'<svg class="{cls}"([^>]*)>(.*?)</svg>', text, re.S)


def attr(s, name):
    m = re.search(rf'{name}="([^"]*)"', s)
    return m.group(1) if m else None


def parse_grid_svg(attrs, body):
    cells = {(int(r), int(c)): ch for r, c, ch in re.findall(r'<text class="ch" data-r="(\d+)" data-c="(\d+)"[^>]*>([A-Z])</text>', body)}
    nr = max(r for r, c in cells) + 1
    nc = max(c for r, c in cells) + 1
    grid = [[cells.get((r, c), "?") for c in range(nc)] for r in range(nr)]
    caps = [(m.group(1), (int(m.group(2)), int(m.group(3))), (int(m.group(4)), int(m.group(5))))
            for m in re.finditer(r'<line class="cap" data-word="(\w+)" data-r0="(\d+)" data-c0="(\d+)" data-r1="(\d+)" data-c1="(\d+)"', body)]
    return grid, caps


def sections(html):
    parts = html.split('<section class="page')[1:]
    return parts


BACKWARDS = {"left", "up", "up-left", "down-left"}
KEY_FACTS = {   # answer -> phrases of which at least one must appear in its clue (an independent second look at each clue)
    "VIOLIN": ["bowed string"], "CELLO": ["knees"], "HARP": ["plucked"], "FLUTE": ["blowing across"], "OBOE": ["double-reed"],
    "CLARINET": ["single reed"], "TRUMPET": ["three valves"], "TROMBONE": ["slide"], "TUBA": ["lowest"], "TIMPANI": ["kettle"],
    "XYLOPHONE": ["wooden bars"], "PICCOLO": ["highest"], "FORTE": ["loud"], "PIANO": ["soft"], "TEMPO": ["fast or slow"],
    "CLEF": ["start of a staff"], "STAFF": ["five lines"], "SHARP": ["raises"], "FLAT": ["lowers"], "REST": ["silent"],
    "TIE": ["same pitch"], "FERMATA": ["hold"], "STACCATO": ["short"], "LEGATO": ["smooth"], "CRESCENDO": ["louder"],
    "SLEIGH": ["snow"], "BELLS": ["ring"], "CHOIR": ["singers"], "ICICLE": ["ice"], "COCOA": ["hot chocolate"],
    "MITTENS": ["hands"], "SCARF": ["neck"], "WINTER": ["season"], "SNOWMAN": ["snowballs"], "CONCERT": ["audience"],
    "FROST": ["ice crystals"], "SNOWFLAKE": ["ice"], "CHORUS": ["repeats"], "BEAT": ["steady"], "METER": ["grouped"],
    "MEASURE": ["bar lines"], "RHYTHM": ["long and short"], "QUARTER": ["one beat"], "EIGHTH": ["one beat"], "HALF": ["two beats"],
    "WHOLE": ["four beats"], "TRIPLET": ["three notes"], "CONDUCTOR": ["leads"], "COMPOSER": ["writes music"],
    "SOLOIST": ["alone"], "DRUMMER": ["snare"], "TEMPO ": [],
}
KEY_FORBID = {"FORTE": ["soft"], "PIANO": ["loud"], "SHARP": ["lowers"], "FLAT": ["raises"], "QUARTER": ["two beats", "four beats"],
              "HALF": ["one beat", "four beats"], "WHOLE": ["one beat", "two beats"], "TUBA": ["highest"], "PICCOLO": ["lowest"]}


def verify_searches(html):
    errs = []
    secs = [s for s in sections(html) if 'data-kind="ws"' in s.split(">")[0]]
    keysecs = [s for s in sections(html) if 'data-kind="wkeypage"' in s.split(">")[0]]
    keyblocks = {}
    for ks in keysecs:
        for blk in re.split(r'<div class="keyblock"', ks)[1:]:
            n = int(re.search(r'data-kind="wkey" data-n="(\d+)"', blk).group(1))
            keyblocks[n] = blk
    if len(secs) != 6 or sorted(keyblocks) != list(range(1, 7)):
        errs.append(f"word searches: {len(secs)} pages and keys for {sorted(keyblocks)}")
        return errs, 0
    total_words = 0
    for sec in secs:
        n = int(re.search(r'data-n="(\d+)"', sec).group(1))
        tag = f"Word Search {n}"
        m = first_svg(sec, "wsgrid")
        grid, caps0 = parse_grid_svg(m.group(1), m.group(2))
        if caps0:
            errs.append(f"{tag}: the student page carries highlights")
        size = len(grid)
        if not (12 <= size <= 15) or any(len(r) != size for r in grid) or any("?" in r for r in grid):
            errs.append(f"{tag}: grid is not a square between 12 and 15 ({size})")
        words = re.findall(r'class="w" data-w="([A-Z]+)"', sec)
        if not 10 <= len(words) <= 14:
            errs.append(f"{tag}: {len(words)} words")
        if len(set(words)) != len(words):
            errs.append(f"{tag}: duplicate word in the list")
        if f"all {len(words)} words" not in sec:
            errs.append(f"{tag}: instructions do not state the word count")
        blk = keyblocks[n]
        km = first_svg(blk, "wsgrid")
        kgrid, caps = parse_grid_svg(km.group(1), km.group(2))
        if kgrid != grid:
            errs.append(f"{tag}: key grid differs from the puzzle grid")
        krows = [(w, int(r), int(c), d) for w, r, c, d in
                 re.findall(r'<div class="kr" data-word="([A-Z]+)" data-r="(\d+)" data-c="(\d+)" data-d="(\w+)"', blk)]
        if sorted(w for w, *_ in krows) != sorted(words):
            errs.append(f"{tag}: key words differ from the word list")
        if len(caps) != len(words) or len(krows) != len(words):
            errs.append(f"{tag}: {len(words)} words but {len(caps)} highlights and {len(krows)} key rows")
        capmap = {w: (a, b) for w, a, b in caps}
        used = set()
        for w in words:
            hits = solve_lines(grid, w)
            if len(hits) != 1:
                errs.append(f"{tag}: {w} found {len(hits)} times")
                continue
            a, b, dname = hits[0]
            used.add(dname)
            if capmap.get(w) != (a, b):
                errs.append(f"{tag}: highlight of {w} is {capmap.get(w)}, solver found {(a, b)}")
            kr = [x for x in krows if x[0] == w]
            if not kr or (kr[0][1], kr[0][2]) != a or DIR_NAME[kr[0][3]] != dname:
                errs.append(f"{tag}: key row for {w} says {kr}, solver found {a} {dname}")
        allowed = {DIR_NAME[d] for d in WORD_SEARCHES[n - 1][2]}
        if used != allowed:
            errs.append(f"{tag}: directions used {sorted(used)} differ from the stated {sorted(allowed)}")
        stated = STATED_DIRS[n]
        if stated != used:
            errs.append(f"{tag}: stated directions {sorted(stated)} differ from the directions actually used {sorted(used)}")
        txt = DIR_TEXT[n]
        if (n <= 4 and ("diagonal" in txt) != bool(used & {"down-right", "up-right"})) or \
           ("down and to the right" in txt) != ("down-right" in used and n == 2):
            errs.append(f"{tag}: on-page direction text does not match the grid")
        if n >= 4 and not (used & BACKWARDS):
            errs.append(f"{tag}: the harder puzzle has no backwards word")
        if n <= 3 and (used & BACKWARDS):
            errs.append(f"{tag}: an easier puzzle has a backwards word")
        # the text on the page must describe what the grid contains
        if "backwards" in sec and not (used & BACKWARDS):
            errs.append(f"{tag}: instructions mention backwards words but there are none")
        if (used & BACKWARDS) and "backwards" not in sec:
            errs.append(f"{tag}: grid has backwards words but the instructions do not say so")
        total_words += len(words)
    return errs, total_words


def parse_cw(attrs, body):
    cells = {(int(r), int(c)) for r, c in re.findall(r'<rect class="cwc" data-r="(\d+)" data-c="(\d+)"', body)}
    nums = {(int(r), int(c)): int(t) for r, c, t in re.findall(r'<text class="cwn" data-r="(\d+)" data-c="(\d+)"[^>]*>(\d+)</text>', body)}
    letters = {(int(r), int(c)): ch for r, c, ch in re.findall(r'<text class="cwl" data-r="(\d+)" data-c="(\d+)"[^>]*>([A-Z])</text>', body)}
    return cells, nums, letters


def cw_runs(cells):
    """Maximal straight runs of 2 or more cells, found by scanning each row and column (independent of the generator)."""
    out = []
    rmax = max(r for r, c in cells) + 1
    cmax = max(c for r, c in cells) + 1
    for r in range(rmax):
        c = 0
        while c < cmax:
            if (r, c) in cells:
                s = c
                while (r, c) in cells:
                    c += 1
                if c - s >= 2:
                    out.append(("A", r, s, c - s))
            else:
                c += 1
    for c in range(cmax):
        r = 0
        while r < rmax:
            if (r, c) in cells:
                s = r
                while (r, c) in cells:
                    r += 1
                if r - s >= 2:
                    out.append(("D", s, c, r - s))
            else:
                r += 1
    return out


def check_crossword(cells, nums, letters, clues, keyrows, tag, table=True):
    """clues: [(dir, n, len, text)], keyrows: [(dir, n, word)]. Returns errors."""
    errs = []
    runs_ = cw_runs(cells)
    # standard numbering
    starts = sorted({(r, c) for d, r, c, ln in runs_}, key=lambda x: x)
    want_num = {p: i + 1 for i, p in enumerate(starts)}
    if nums != want_num:
        errs.append(f"{tag}: numbering is not the standard row-by-row numbering")
    # every cell belongs to an entry
    covered = set()
    for d, r, c, ln in runs_:
        for k in range(ln):
            covered.add((r, c + k) if d == "A" else (r + k, c))
    if covered != cells:
        errs.append(f"{tag}: {len(cells - covered)} cells belong to no entry")
    # entries <-> clues <-> key
    ent = {}
    for d, r, c, ln in runs_:
        ent[(d, want_num[(r, c)])] = (r, c, ln)
    if sorted((d, n) for d, n, ln, t in clues) != sorted(ent):
        errs.append(f"{tag}: clue numbers {sorted((d, n) for d, n, _, _ in clues)} do not match the grid's entries {sorted(ent)}")
    if len(set(clues)) != len(clues) or len({t for *_, t in clues}) != len(clues):
        errs.append(f"{tag}: a clue appears twice")
    kmap = {(d, n): w for d, n, w in keyrows}
    if len(kmap) != len(keyrows) or sorted(kmap) != sorted(ent):
        errs.append(f"{tag}: key entries do not match the grid's entries")
    if len(set(kmap.values())) != len(kmap):
        errs.append(f"{tag}: an answer appears twice")
    for (d, n), (r, c, ln) in ent.items():
        word = "".join(letters.get((r, c + k) if d == "A" else (r + k, c), "?") for k in range(ln))
        if kmap.get((d, n)) != word:
            errs.append(f"{tag}: {n} {d}: key says {kmap.get((d, n))} but the grid spells {word}")
        cl = [x for x in clues if (x[0], x[1]) == (d, n)]
        if cl and cl[0][2] != ln:
            errs.append(f"{tag}: {n} {d}: clue says {cl[0][2]} letters, entry has {ln}")
        if cl and table:
            ans, clue = word, cl[0][3]
            if CLUES.get(ans) != clue:
                errs.append(f"{tag}: {n} {d} {ans}: clue differs from the word table")
            if ans.lower() in clue.lower() or ans[:5].lower() in clue.lower().replace(" ", ""):
                errs.append(f"{tag}: clue for {ans} contains the answer")
            facts = KEY_FACTS.get(ans)
            if not facts:
                errs.append(f"{tag}: no fact check for {ans}")
            elif not any(f in clue.lower() for f in facts):
                errs.append(f"{tag}: clue for {ans} lacks {facts}: {clue}")
            for bad in KEY_FORBID.get(ans, []):
                if bad in clue.lower():
                    errs.append(f"{tag}: clue for {ans} says '{bad}'")
    # crossing letters agree: every cell has one letter, and each across/down answer reads that same letter
    for (d, n), (r, c, ln) in ent.items():
        for k in range(ln):
            cell = (r, c + k) if d == "A" else (r + k, c)
            if kmap.get((d, n), "?" * 99)[k] != letters.get(cell):
                errs.append(f"{tag}: crossing letter mismatch at {cell} in {n} {d}")
    # connectivity and checked letters
    cross = {k: 0 for k in ent}
    cellent = {}
    for (d, n), (r, c, ln) in ent.items():
        for k in range(ln):
            cellent.setdefault((r, c + k) if d == "A" else (r + k, c), []).append((d, n))
    for cell, es in cellent.items():
        if len(es) == 2:
            for e in es:
                cross[e] += 1
    for e, k in cross.items():
        if k == 0:
            errs.append(f"{tag}: entry {e} crosses no other entry")
    seen, stack = set(), [next(iter(ent))]
    while stack:
        e = stack.pop()
        if e in seen:
            continue
        seen.add(e)
        r, c, ln = ent[e]
        for k in range(ln):
            for o in cellent[(r, c + k) if e[0] == "A" else (r + k, c)]:
                if o not in seen:
                    stack.append(o)
    if seen != set(ent):
        errs.append(f"{tag}: the grid is not connected")
    return errs


def verify_crosswords(html):
    errs = []
    secs = [s for s in sections(html) if 'data-kind="cw"' in s.split(">")[0]]
    keysecs = [s for s in sections(html) if 'data-kind="ckeypage"' in s.split(">")[0]]
    keyblocks = {}
    for ks in keysecs:
        for blk in re.split(r'<div class="keyblock"', ks)[1:]:
            keyblocks[int(re.search(r'data-kind="ckey" data-n="(\d+)"', blk).group(1))] = blk
    if len(secs) != 4 or sorted(keyblocks) != [1, 2, 3, 4]:
        return [f"crosswords: {len(secs)} pages and keys for {sorted(keyblocks)}"], 0
    total = 0
    for sec in secs:
        n = int(re.search(r'data-n="(\d+)"', sec).group(1))
        tag = f"Crossword {n}"
        m = first_svg(sec, "cwgrid")
        cells, nums, letters = parse_cw(m.group(1), m.group(2))
        if letters or 'class="cwl"' in sec:
            errs.append(f"{tag}: the student page shows letters")
        clues = [(d, int(k), int(ln), re.sub(r"\s*\(\d+\)$", "", html_unescape(re.sub(r"<[^>]+>", "", body)).strip()[len(str(k)):].strip()))
                 for d, k, ln, body in re.findall(r'<li data-dir="(\w)" data-n="(\d+)" data-len="(\d+)">(.*?)</li>', sec)]
        blk = keyblocks[n]
        km = first_svg(blk, "cwgrid")
        kcells, knums, kletters = parse_cw(km.group(1), km.group(2))
        if kcells != cells or knums != nums:
            errs.append(f"{tag}: key grid shape or numbers differ from the puzzle")
        if set(kletters) != kcells:
            errs.append(f"{tag}: key does not fill every box")
        keyrows = [(d, int(k), w) for d, k, w in re.findall(r'<div class="kr" data-dir="(\w)" data-n="(\d+)" data-word="([A-Z]+)"', blk)]
        errs += check_crossword(cells, nums, kletters, clues, keyrows, tag)
        # brackets in the rendered clue agree with the data-len attribute
        for d, k, ln, body in re.findall(r'<li data-dir="(\w)" data-n="(\d+)" data-len="(\d+)">(.*?)</li>', sec):
            mm = re.search(r'\((\d+)\)</span>$', body.strip())
            if not mm or int(mm.group(1)) != int(ln):
                errs.append(f"{tag}: clue {k} {d} shows the wrong letter count")
        pl = CW_PLACEMENTS[n - 1]
        if len(clues) != len(keyrows) or len(clues) != len(pl):
            errs.append(f"{tag}: {len(clues)} clues, {len(keyrows)} key rows, {len(pl)} placed words")
        if not 10 <= len(clues) <= 16:
            errs.append(f"{tag}: {len(clues)} clues is outside 10 to 16")
        total += len(clues)
        rows = max(r for r, c in cells) + 1
        cols = max(c for r, c in cells) + 1
        if max(rows, cols) > 15:
            errs.append(f"{tag}: grid larger than 15")
    return errs, total


def html_unescape(s):
    import html as _h
    return _h.unescape(s)


def verify_examples():
    """The worked examples (how-to page and cover) are real puzzles: solve them with the same independent code."""
    errs = []
    grid = [list(r) for r in EX_WS_ROWS]
    for w in ("TEMPO", "CLEF"):
        if len(solve_lines(grid, w)) != 1:
            errs.append(f"example word search: {w} is not found exactly once")
    ex = ex_cw()
    cells = set(ex["cells"])
    clues = []
    keyrows = []
    num = ex["num"]
    for w, (r, c, d) in EX_CW_WORDS.items():
        clues.append((d, num[(r, c)], len(w), EX_CW_CLUES[w]))
        keyrows.append((d, num[(r, c)], w))
    errs += check_crossword(cells, num, ex["cells"], clues, keyrows, "example crossword", table=False)
    for w, clue in EX_CW_CLUES.items():
        if clue != CLUES[w]:
            errs.append(f"example clue for {w} differs from the word table")
    return errs


def verify_text_tables():
    """Word table sanity: spelling, uniqueness and US English."""
    errs = []
    for t, size, dirs, words in WORD_SEARCHES:
        for w in words:
            if not re.fullmatch(r"[A-Z]+", w) or len(w) > size:
                errs.append(f"word '{w}' invalid or longer than the {size} grid")
    for t, pool in CROSSWORDS:
        for w in pool:
            if w not in CLUES:
                errs.append(f"no clue for {w}")
    text = " ".join(CLUES.values()) + " " + " ".join(t for t, *_ in WORD_SEARCHES)
    for bad in ("colour", "centre", "favourite", "grey"):
        if bad in text.lower():
            errs.append(f"non-US spelling: {bad}")
    for bad in ("christmas", "santa", "jesus", "church", "hanukkah", "kwanzaa", "rudolph", "frosty", "grinch", "jingle"):
        if bad in text.lower() or any(bad in w.lower() for ws_ in WORD_SEARCHES for w in ws_[3]):
            errs.append(f"religious or branded word: {bad}")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    rows = []
    for line in out:
        parts = line.split()
        rows.append((parts[0], parts[-5]))
    return rows


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))


LAYOUT_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = [];
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 816, height: 1056 } });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const res = [];
      const ink = el => {
        const cv = document.createElement('canvas').getContext('2d');
        const fs = parseFloat(el.getAttribute('font-size'));
        cv.font = `${el.getAttribute('font-weight')} 100px ${getComputedStyle(el).fontFamily}`;
        const m = cv.measureText(el.textContent), k = fs / 100;
        const x = parseFloat(el.getAttribute('x')), y = parseFloat(el.getAttribute('y'));
        const sh = el.getAttribute('text-anchor') === 'middle' ? m.width * k / 2 : 0;
        const x0 = x - sh - m.actualBoundingBoxLeft * k, x1 = x - sh + m.actualBoundingBoxRight * k;
        return { x: x0, y: y - m.actualBoundingBoxAscent * k, width: x1 - x0, height: (m.actualBoundingBoxAscent + m.actualBoundingBoxDescent) * k };
      };
      const boxHit = (a, b) => a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;
      const cls = el => (el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className);
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        const boxes = [];
        pg.querySelectorAll('svg.wsgrid, svg.cwgrid, svg.exws, svg.excw, svg.icon, .wlist, .cluebox, .keyblock, .klist, .doc table, .doc p, .doc ul, .how, .name, .top, .tbox, .step, .howsec, .stp').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${cls(el)} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${cls(el)} too close to the page edge`);
          if (el.matches('svg.wsgrid, svg.cwgrid, svg.exws, svg.excw, .wlist, .cluebox, .keyblock, .tbox, .step')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 8 && gy < 8) res.push(`page ${i + 1}: two boxes closer than 8px (${cls(boxes[a][0])} / ${cls(boxes[c][0])})`);
        }
        // crossword: a clue number's box may not touch the letter box in the same cell
        pg.querySelectorAll('svg.cwgrid, svg.excw, svg.minicw').forEach(sv => {
          sv.querySelectorAll('text.cwn').forEach(n => {
            const l = sv.querySelector(`text.cwl[data-r="${n.dataset.r}"][data-c="${n.dataset.c}"]`);
            if (l && boxHit(ink(n), ink(l))) res.push(`page ${i + 1}: clue number ${n.textContent} overlaps its letter ${l.textContent} (${cls(sv)})`);
          });
        });
        // title versus the icons next to it
        const tt = pg.querySelector('.top .tt'), ic = pg.querySelector('.top .icons'), tg = pg.querySelector('.top .tag');
        if (tt && ic && tg) {
          const rg = document.createRange(); rg.selectNodeContents(tt);
          const sub = pg.querySelector('.top .t small'); const rs = document.createRange(); rs.selectNodeContents(sub);
          const tr = Math.max(rg.getBoundingClientRect().right, rs.getBoundingClientRect().right);
          const ir = ic.getBoundingClientRect(), gr = tg.getBoundingClientRect();
          if (ir.left - tr < 22) res.push(`page ${i + 1}: title is ${(ir.left - tr).toFixed(1)}px from the header icons (needs >= 22)`);
          if (gr.left - ir.right < 22) res.push(`page ${i + 1}: header icons are ${(gr.left - ir.right).toFixed(1)}px from the tag (needs >= 22)`);
        }
        // a one-word last line in a paragraph or instruction
        pg.querySelectorAll('.how, .doc p, .doc li, .stp p, .cluebox li').forEach(el => {
          const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          const tops = [];
          let node;
          while ((node = w.nextNode())) {
            const t = node.nodeValue; const re = /\S+/g; let m;
            while ((m = re.exec(t))) {
              const rg = document.createRange(); rg.setStart(node, m.index); rg.setEnd(node, m.index + m[0].length);
              const rc = rg.getClientRects()[0]; if (rc) tops.push([Math.round(rc.top), m[0]]);
            }
          }
          if (!tops.length) return;
          const lastTop = tops[tops.length - 1][0];
          const lines = new Set(tops.map(x => x[0]));
          const lastLine = tops.filter(x => Math.abs(x[0] - lastTop) < 3);
          if (lines.size > 1 && lastLine.length === 1 && !el.closest('.cluebox')) res.push(`page ${i + 1}: one-word last line "${lastLine[0][1]}" in ${el.tagName}.${cls(el)}`);
        });
        // text that does not fit its box
        pg.querySelectorAll('.tag .ln, .tag .lv, .kt, .kr, .w, th, td').forEach(el => {
          if (el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).display !== 'inline') res.push(`page ${i + 1}: ${el.tagName}.${cls(el)} text wider than its box`);
        });
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""


SYN_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const r = await p.evaluate(() => {
    const res = [];
    const ink = el => {
      const cv = document.createElement('canvas').getContext('2d');
      const fs = parseFloat(el.getAttribute('font-size'));
      cv.font = `${el.getAttribute('font-weight')} 100px ${getComputedStyle(el).fontFamily}`;
      const m = cv.measureText(el.textContent), k = fs / 100;
      const x = parseFloat(el.getAttribute('x')), y = parseFloat(el.getAttribute('y'));
      const sh = el.getAttribute('text-anchor') === 'middle' ? m.width * k / 2 : 0;
      const x0 = x - sh - m.actualBoundingBoxLeft * k, x1 = x - sh + m.actualBoundingBoxRight * k;
      return { x: x0, y: y - m.actualBoundingBoxAscent * k, width: x1 - x0, height: (m.actualBoundingBoxAscent + m.actualBoundingBoxDescent) * k };
    };
    document.querySelectorAll('svg').forEach(sv => sv.querySelectorAll('text.cwn').forEach(n => {
      const l = sv.querySelector(`text.cwl[data-r="${n.dataset.r}"][data-c="${n.dataset.c}"]`);
      const a = ink(n), c = ink(l);
      const cell = sv.querySelector(`rect.cwc[data-r="${n.dataset.r}"][data-c="${n.dataset.c}"]`).getBBox();
      if (a.x < c.x + c.width && c.x < a.x + a.width && a.y < c.y + c.height && c.y < a.y + a.height) res.push(`number ${n.textContent} overlaps letter ${l.textContent}`);
      for (const t of [a, c]) if (t.x < cell.x + 0.3 || t.y < cell.y || t.x + t.width > cell.x + cell.width || t.y + t.height > cell.y + cell.height) res.push(`number ${n.textContent} or letter ${l.textContent} leaves its cell`);
    }));
    return res;
  });
  await b.close();
  console.log(JSON.stringify(r));
})().catch(e => { console.error(e); process.exit(1); });
"""


def verify_clue_numbers():
    """Synthetic grid with 1-, 2- and 3-digit numbers over the widest letters; DOM boxes of number and letter must not intersect."""
    letters = "MWMWQ"
    cells = {(0, i): letters[i] for i in range(5)}
    nums = {(0, 0): 1, (0, 1): 9, (0, 2): 12, (0, 3): 88, (0, 4): 123}
    svg = "".join(cw_svg({"cells": cells, "num": nums, "rows": 1, "cols": 5, "n": 0}, True, w_pt=w) for w in (150.0, 268.0, 470.0))
    f = write("numtest.html", f"<!doctype html><html><head><meta charset='utf-8'><style>{font_css()}</style></head><body>{svg}</body></html>")
    js = os.path.join(BUILD, "numtest.js")
    with open(js, "w") as fh:
        fh.write(SYN_JS)
    r = subprocess.run(["node", js, f], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"clue-number test failed: {r.stderr[-300:]}"]
    return [f"synthetic grid: {x}" for x in json.loads(r.stdout.strip().splitlines()[-1])]


def verify_layout():
    js = os.path.join(BUILD, "layout.js")
    with open(js, "w") as f:
        f.write(LAYOUT_JS)
    files = [os.path.join(BUILD, "resource.html"), os.path.join(BUILD, "preview.html")]
    if not all(os.path.exists(x) for x in files):
        return ["build html missing: run gen.py first"]
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"layout script failed: {r.stderr[-300:]}"]
    return json.loads(r.stdout.strip().splitlines()[-1])


def verify_icons():
    """Render every icon and the cover art alone in their own boxes at 300 dpi-ish scale; no ink may touch the box edge."""
    from PIL import Image
    errs = []
    ih = write("icons.html", icons_html())
    ch = write("coverart.html", sq_doc(f'<div style="position:absolute;left:0;top:0;width:900px;background:#fff">{cover_art()}</div>'))
    render([{"html": ih, "png": os.path.join(BUILD, "icons.png"), "width": 800, "height": 340, "scale": 3},
            {"html": ch, "png": os.path.join(BUILD, "coverart.png"), "width": 900, "height": 470, "scale": 2}])
    im = Image.open(os.path.join(BUILD, "icons.png")).convert("L")
    px = im.load()
    for i, name in enumerate(ICONS):
        x0, y0 = (20 + (i % 5) * 150) * 3, (20 + (i // 5) * 150) * 3
        box = 120 * 3
        ink = 0
        edge = 0
        for y in range(box):
            for x in range(box):
                v = px[x0 + x, y0 + y]
                if v < 235:
                    ink += 1
                    if x < 3 or y < 3 or x >= box - 3 or y >= box - 3:
                        edge += 1
        if ink < 300:
            errs.append(f"icon {name}: renders almost empty ({ink} px)")
        if edge:
            errs.append(f"icon {name}: ink touches the edge of its box ({edge} px)")
        # the art should not fill the box so tightly that it is nearly clipped
        xs = [x for y in range(0, box, 2) for x in range(box) if px[x0 + x, y0 + y] < 235]
        if xs and (min(xs) < 6 or max(xs) > box - 7):
            errs.append(f"icon {name}: ink within 6px of the box edge")
    ca = Image.open(os.path.join(BUILD, "coverart.png")).convert("L")
    w, h = ca.size
    cp = ca.load()
    bad = sum(1 for x in range(w) for y in (0, 1, 2, h - 3, h - 2, h - 1) if cp[x, y] < 235) + \
        sum(1 for y in range(h) for x in (0, 1, 2, w - 3, w - 2, w - 1) if cp[x, y] < 235)
    if bad:
        errs.append(f"cover art: ink touches the edge of its box ({bad} px): something is cut off")
    return errs


def verify_images():
    errs = []
    from PIL import Image
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        im = Image.open(p).convert("L")
        if im.size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
            continue
        px = im.load()
        rows = []
        for y in range(0, 2000, 2):
            dark = sum(1 for x in range(0, 2000, 8) if px[x, y] < 200)
            rows.append(dark)
        ytop = 2000
        for y in range(1998, 0, -2):
            if rows[y // 2] > 0.9 * 250:
                ytop = y
            else:
                break
        run = best = 0
        for y in range(120, ytop, 2):
            if rows[y // 2] == 0:
                run += 2
                best = max(best, run)
            else:
                run = 0
        if best > 200:
            errs.append(f"{os.path.basename(p)}: blank band of {best}px (more than 10% of the image)")
        # even side margins: leftmost and rightmost ink above the band
        cols = [min((x for x in range(0, 2000) if any(px[x, y] < 200 for y in range(300, ytop - 20, 6))), default=0),
                max((x for x in range(0, 2000) if any(px[x, y] < 200 for y in range(300, ytop - 20, 6))), default=1999)]
        left, right = cols[0], 1999 - cols[1]
        if abs(left - right) > 70:
            errs.append(f"{os.path.basename(p)}: uneven side margins ({left}px left, {right}px right)")
    # watermark rules for the square previews: pages already carry theirs, so no second overlay; the page-free one has exactly one
    for name, want in (("cover.html", 0), ("p1.html", 0), ("p2.html", 0), ("p3.html", 1)):
        t = open(os.path.join(BUILD, name)).read()
        got = len(re.findall(r'<div class="swm"', t))
        if got != want:
            errs.append(f"{name}: {got} overlay watermarks, expected {want}")
        if "pv" in t and got:
            errs.append(f"{name}: shows watermarked page images and adds a second watermark")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
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
        names = " ".join(n for n, _ in fonts)
        for fam in ("Oswald", "SourceSans3"):
            if fam.lower() not in names.lower().replace(" ", ""):
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    rd = PdfReader(PDF)
    texts = [(pg.extract_text() or "") for pg in rd.pages]
    for i, t in enumerate(texts):
        n = i + 1
        if len(t.strip()) < 40:
            errs.append(f"PDF page {n} looks blank")
        if "PREVIEW" in t.upper():
            errs.append(f"product PDF page {n} carries a PREVIEW watermark")
    flat = [re.sub(r"\s+", " ", t).upper() for t in texts]
    # page names and cross-references agree
    for ws in SEARCHES:
        n = ws["n"]
        if f"WORD SEARCH {n}. {ws['title'].upper()}" not in flat[ws_page(n) - 1]:
            errs.append(f"PDF page {ws_page(n)}: heading for Word Search {n} missing")
        if f"ANSWER KEY ON PAGE {wkey_page(n)}" not in flat[ws_page(n) - 1]:
            errs.append(f"PDF page {ws_page(n)}: key page reference should be {wkey_page(n)}")
        if f"WORD SEARCH {n}" not in flat[wkey_page(n) - 1] or f"PUZZLE ON PAGE {ws_page(n)}" not in flat[wkey_page(n) - 1]:
            errs.append(f"PDF page {wkey_page(n)}: key block for Word Search {n} missing or names the wrong puzzle page")
    for cw in CROSSES:
        n = cw["n"]
        if f"CROSSWORD {n}. {cw['title'].upper()}" not in flat[cw_page(n) - 1]:
            errs.append(f"PDF page {cw_page(n)}: heading for Crossword {n} missing")
        if f"ANSWER KEY ON PAGE {ckey_page(n)}" not in flat[cw_page(n) - 1]:
            errs.append(f"PDF page {cw_page(n)}: key page reference should be {ckey_page(n)}")
        if f"CROSSWORD {n}" not in flat[ckey_page(n) - 1] or f"PUZZLE ON PAGE {cw_page(n)}" not in flat[ckey_page(n) - 1]:
            errs.append(f"PDF page {ckey_page(n)}: key block for Crossword {n} missing or names the wrong puzzle page")
    for ws in SEARCHES:
        row = f"WORD SEARCH {ws['n']} {ws['title'].upper()} {ws['size']} × {ws['size']}"
        if row not in flat[P_TEACH - 1]:
            errs.append(f"teacher notes: table row for Word Search {ws['n']} missing or wrong")
        if f"{ws_page(ws['n'])} / {wkey_page(ws['n'])}" not in flat[P_TEACH - 1]:
            errs.append(f"teacher notes: page numbers for Word Search {ws['n']} wrong")
    for cw in CROSSES:
        if f"{cw_page(cw['n'])} / {ckey_page(cw['n'])}" not in flat[P_TEACH - 1]:
            errs.append(f"teacher notes: page numbers for Crossword {cw['n']} wrong")
    for k in ("6 WORD SEARCHES", "4 CROSSWORDS"):
        if k not in flat[0] and k.replace("6 ", "").replace("4 ", "") not in flat[0]:
            errs.append(f"cover lacks '{k}'")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
    errs += verify_images()
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80:
            errs.append(f"UPLOAD.md: title is {len(title)} chars (max 80)")
        if re.search(r"winter|snow|holiday|christmas|december", title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "6 word searches", "4 crosswords"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    low = up.lower()
    for bad in ("checked by hand", "handmade", "recomputed", "in code", "solved by computer", "classroom-tested"):
        if bad in low:
            errs.append(f"UPLOAD.md: contains '{bad}'")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if not 1 <= len(tj["tags"]) <= 6 or any(t not in tags for t in tj["tags"]):
        errs.append(f"tpt.json tags invalid: {tj['tags']}")
    if not 1 <= len(tj["subjects"]) <= 3 or any(s not in subs for s in tj["subjects"]):
        errs.append(f"tpt.json subjects invalid: {tj['subjects']}")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE:
        errs.append("tpt.json pages or price mismatch")
    if len(tj["grades"]) > 4:
        errs.append("tpt.json: more than 4 grades")
    return errs


def check():
    html = open(os.path.join(BUILD, "resource.html")).read() if os.path.exists(os.path.join(BUILD, "resource.html")) else ""
    if not html:
        sys.exit("build/resource.html missing: run gen.py first")
    errs = verify_text_tables() + verify_examples()
    e1, nw = verify_searches(html)
    e2, nc = verify_crosswords(html)
    errs += e1 + e2
    errs += verify_layout()
    errs += verify_clue_numbers()
    errs += verify_icons()
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: {len(SEARCHES)} word searches ({nw} words, each found exactly once and no extra occurrences in any direction; "
          f"highlights equal the found positions), {len(CROSSES)} crosswords ({nc} clues: lengths, crossings, numbering, clue table and key all agree); "
          f"puzzle and key counts match; layout clear of footers and boxes; icons and cover art unclipped; PDF {TOTAL_PAGES} Letter pages, "
          f"preview 4 (one watermark each), fonts embedded; images 2000x2000; UPLOAD.md and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    elif "--find-crosswords" in sys.argv:
        for title, words in CROSSWORDS:
            b = search_crossword(words, len(words), 15, 12000, 11)
            print(title, b[1] if b else None)
    else:
        build()
