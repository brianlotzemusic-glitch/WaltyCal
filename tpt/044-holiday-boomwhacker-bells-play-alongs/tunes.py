"""Melody data for TpT 044 (carol play-alongs): transcriptions, independent second encodings, and the checks between them.

Every tune is stored twice:
  * PRIMARY  - typed in C major (white keys), bar by bar, as "PITCH:beats" (quarter note = 1 beat), "~" = tied to the next note.
  * SECOND   - a different encoding read from a different file (a MIDI file, a LilyPond score, or a printed part) in its ORIGINAL key,
               transposed to C by code.  `verify_tunes()` demands that both agree note for note.
Sources are listed in SOURCES and printed in UPLOAD.md.
"""
import re
from fractions import Fraction as F
from collections import namedtuple

Note = namedtuple("Note", "pitch dur tie")

PCN = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
PC_NAME = {v: k for k, v in PCN.items()}


def midi(p):
    return 12 * (int(p[1:]) + 1) + PCN[p[0]]


def from_midi(m):
    if m % 12 not in PC_NAME:
        raise ValueError(f"black key {m}")
    return f"{PC_NAME[m % 12]}{m // 12 - 1}"


def parse_bars(s):
    bars = []
    for b in s.split("|"):
        row = []
        for tok in b.split():
            tie = tok.endswith("~")
            p, d = tok.rstrip("~").split(":")
            row.append(Note(p, F(d), tie))
        bars.append(row)
    return bars


def bar_beats(bar):
    return sum(n.dur for n in bar)


# ----------------------------------------------------------------- PRIMARY data (C major)
JB_A = "E4:1 E4:1 E4:2 | E4:1 E4:1 E4:2 | E4:1 G4:1 C4:1.5 D4:.5 | E4:4 | F4:1 F4:1 F4:1.5 F4:.5 | F4:1 E4:1 E4:1 E4:.5 E4:.5 | E4:1 D4:1 D4:1 E4:1 | D4:2 G4:2"
JB = JB_A + " | " + " | ".join(JB_A.split(" | ")[:6]) + " | G4:1 G4:1 F4:1 D4:1 | C4:4"

DECK_A = "G4:1.5 F4:.5 E4:1 D4:1 | C4:1 D4:1 E4:1 C4:1 | D4:.5 E4:.5 F4:.5 D4:.5 E4:1.5 D4:.5 | C4:1 B3:1 C4:2"
DECK = (DECK_A + " | " + DECK_A + " | D4:1.5 E4:.5 F4:1 D4:1 | E4:1.5 F4:.5 G4:1 D4:1 | E4:.5 F4:.5 G4:1 A4:.5 B4:.5 C5:1 | B4:1 A4:1 G4:2"
        " | G4:1.5 F4:.5 E4:1 D4:1 | C4:1 D4:1 E4:1 C4:1 | A4:.5 A4:.5 A4:.5 A4:.5 G4:1.5 F4:.5 | E4:1 D4:1 C4:2")

JOY = ("C5:1 B4:.75 A4:.25 | G4:1.5 F4:.5 | E4:1 D4:1 | C4:1.5 G4:.5 | A4:1.5 A4:.5 | B4:1.5 B4:.5 | C5:2~ | C5:1.5 C5:.5"
       " | C5:.5 B4:.5 A4:.5 G4:.5 | G4:.75 F4:.25 E4:.5 C5:.5 | C5:.5 B4:.5 A4:.5 G4:.5 | G4:.75 F4:.25 E4:.5 E4:.5"
       " | E4:.5 E4:.5 E4:.5 E4:.25 F4:.25 | G4:1.5 F4:.25 E4:.25 | D4:.5 D4:.5 D4:.5 D4:.25 E4:.25 | F4:1.5 E4:.25 D4:.25"
       " | E4:.5 C5:1 A4:.5 | G4:.75 F4:.25 E4:.5 F4:.5 | E4:1 D4:1 | C4:2")

HOUSE_V = "G4:1 G4:.5 A4:.5 G4:1 E4:.5 D4:.5 | C4:1 E4:1 G4:2 | A4:1 A4:1 G4:1 E4:1 | D4:1 G4:1 G4:2"
HOUSE = (HOUSE_V + " | G4:1 G4:.5 A4:.5 G4:1 E4:.5 D4:.5 | C4:1 E4:1 G4:2 | A4:1 A4:.5 A4:.5 G4:.5 G4:.5 E4:1 | D4:1 G4:1 C4:2"
         " | F4:1 F4:1 A4:2 | G4:1 G4:.5 G4:.5 E4:2 | D4:1 F4:1 F4:2 | E4:1 G4:.5 G4:.5 C4:1 E4:1"
         " | G4:1 G4:.5 A4:.5 G4:1 E4:1 | F4:1 G4:1 A4:2 | G4:1 G4:.5 A4:.5 G4:1 E4:.5 E4:.5 | D4:1 G4:1 C4:2")

CRADLE = ("G3:1 | C4:1 C4:1 D4:.5 E4:.5 | C4:1 C4:1 E4:.5 F4:.5 | G4:1 G4:1 A4:1 | F4:2 D4:.5 E4:.5 | F4:1 F4:1 G4:1 | E4:1 E4:1 C4:.5 E4:.5 | D4:1 A3:1 C4:1 | B3:2 G3:1"
          " | C4:1 C4:1 D4:.5 E4:.5 | C4:1 C4:1 E4:.5 F4:.5 | G4:1 G4:1 A4:1 | F4:2 D4:.5 E4:.5 | F4:1 F4:1 G4:1 | E4:1 E4:1 C4:.5 E4:.5 | D4:1 A3:1 B3:1 | C4:2")

# ----------------------------------------------------------------- SECOND encodings (original keys)
# Jingle Bells: melody (top voice) of Wikimedia Commons "Jingle_Bells_refrain_vector.mid", in G major (pitch:beats).
JB_G_MIDI = ("B4:1 B4:1 B4:2 B4:1 B4:1 B4:2 B4:1 D5:1 G4:1.5 A4:0.5 B4:4 C5:1 C5:1 C5:1.5 C5:0.5 C5:1 B4:1 B4:1 B4:0.5 B4:0.5 B4:1 A4:1 A4:1 B4:1 A4:2 D5:2 "
             "B4:1 B4:1 B4:2 B4:1 B4:1 B4:2 B4:1 D5:1 G4:1.5 A4:0.5 B4:4 C5:1 C5:1 C5:1.5 C5:0.5 C5:1 B4:1 B4:1 B4:0.5 B4:0.5 D5:1 D5:1 C5:1 A4:1 G4:4")
JB_LETTERS = "EEEEEE EGCDE FFFFFEE EEEDDEDG EEEEEE EGCDE FFFFFEE EEGGFDC"   # second source B: piano-keyboard-guide.com chorus, in C

# Deck the Halls: onsets (beats) of the melody track of Wikimedia Commons "Deck_the_Halls.mid", D major; bars start at beat 0.5; ends at 64.5.
DECK_D_ONSETS = ("0.5 A4 2.0 G4 2.5 F#4 3.5 E4 4.5 D4 5.5 E4 6.5 F#4 7.5 D4 8.5 E4 9.0 F#4 9.5 G4 10.0 E4 10.5 F#4 12.0 E4 12.5 D4 13.5 C#4 14.5 D4 "
                 "16.5 A4 18.0 G4 18.5 F#4 19.5 E4 20.5 D4 21.5 E4 22.5 F#4 23.5 D4 24.5 E4 25.0 F#4 25.5 G4 26.0 E4 26.5 F#4 28.0 E4 28.5 D4 29.5 C#4 30.5 D4 "
                 "32.5 E4 34.0 F#4 34.5 G4 35.5 E4 36.5 F#4 38.0 G4 38.5 A4 39.5 E4 40.5 F#4 41.0 G4 41.5 A4 42.5 B4 43.0 C#5 43.5 D5 44.5 C#5 45.5 B4 46.5 A4 "
                 "48.5 A4 50.0 G4 50.5 F#4 51.5 E4 52.5 D4 53.5 E4 54.5 F#4 55.5 D4 56.5 B4 57.0 B4 57.5 B4 58.0 B4 58.5 A4 60.0 G4 60.5 F#4 61.5 E4 62.5 D4")
DECK_LETTERS = "GFEDCDEC DEFDEDCBC GFEDCDEC DEFDEDCBC DEFDEFGD EFGABCBAG GFEDCDEC AAAAGFEDC"   # source B: piano-keyboard-guide.com (D major, transposed here)

# Joy to the World: Mason 1839 as in the LilyPond score on Wikipedia (soprano), D major, 2/4.  The repeat block is read as an exact repeat.
JOY_LY = r"""d4 cis8. b16 | a4. g8 | fis4 e | d4. a'8 | b4. b8 | cis4. cis8 | d2~ | d4.
  \repeat unfold 2 { d8 | d [cis] b [a] | a8. [g16 fis8] }
  fis8 | fis fis fis fis16 [g] | a4. g16 [fis] | e8 e e e16 [fis] | g4. fis16 [e] | fis8\( d'4\) b8 | a8. [g16] fis8 g | fis4 e | d2"""

# Up on the Housetop: read from the IMSLP part "Violin 1" (Hanby, (c)1864), written in E-flat major, 4/4.
HOUSE_EB = ("Bb4:1 Bb4:.5 C5:.5 Bb4:1 G4:.5 F4:.5 | Eb4:1 G4:1 Bb4:2 | C5:1 C5:1 Bb4:1 G4:1 | F4:1 Bb4:1 Bb4:2"
            " | Bb4:1 Bb4:.5 C5:.5 Bb4:1 G4:.5 F4:.5 | Eb4:1 G4:1 Bb4:2 | C5:1 C5:.5 C5:.5 Bb4:.5 Bb4:.5 G4:1 | F4:1 Bb4:1 Eb4:2"
            " | Ab4:1 Ab4:1 C5:2 | Bb4:1 Bb4:.5 Bb4:.5 G4:2 | F4:1 Ab4:1 Ab4:2 | G4:1 Bb4:.5 Bb4:.5 Eb4:1 G4:1"
            " | Bb4:1 Bb4:.5 C5:.5 Bb4:1 G4:1 | Ab4:1 Bb4:1 C5:2 | Bb4:1 Bb4:.5 C5:.5 Bb4:1 G4:.5 G4:.5 | F4:1 Bb4:1 Eb4:2")

# Away in a Manger, "Cradle Song" (Kirkpatrick 1895): LilyPond score on Wikipedia, F major, 3/4 with a one-beat pickup.
CRADLE_LY = r"""c4 |
  f4 f4 g8 a8 | f4 f4 a8 bes8 | c4 c4 d4 | bes2 g8 a8 | bes4 bes4 c4 | a4 a4 f8 a8 | g4 d4 f4 | e2 c4 |
  f4 f4 g8 a8 | f4 f4 a8 bes8 | c4 c4 d4 | bes2 g8 a8 | bes4 bes4 c4 | a4 a4 f8 a8 | g4 d4 e4 | f2"""


# ----------------------------------------------------------------- readers for the second encodings
def read_pairs(s):
    out = []
    for tok in s.split():
        p, d = tok.split(":")
        out.append((p.replace("#", "s"), F(d)))
    return out


def sharp_midi(p):
    """midi of 'F#4' / 'Bb4' / 'E4' style names."""
    base = 12 * (int(p[-1]) + 1) + PCN[p[0]]
    if len(p) == 3:
        base += 1 if p[1] == "#" else -1
    return base


def bars_from_series(series, shift, meter_beats, pickup=F(0)):
    """series: list of (midi, dur, tie). Transpose by `shift` semitones and cut into bars (first bar may be a pickup)."""
    bars, cur, filled = [], [], F(0)
    target = pickup if pickup else meter_beats
    for m, d, tie in series:
        cur.append(Note(from_midi(m + shift), d, tie))
        filled += d
        if filled == target:
            bars.append(cur)
            cur, filled, target = [], F(0), meter_beats
        elif filled > target:
            raise ValueError("note crosses a barline")
    if cur:
        bars.append(cur)
    return bars


def second_jb():
    s = [(sharp_midi(p), d, False) for p, d in (t.split(":") and (t.split(":")[0], F(t.split(":")[1])) for t in JB_G_MIDI.split())]
    return bars_from_series(s, -7, F(4))


def second_deck():
    toks = DECK_D_ONSETS.split()
    ons = [(F(toks[i]), toks[i + 1]) for i in range(0, len(toks), 2)]
    end = F("64.5")
    series = []
    for i, (t, p) in enumerate(ons):
        nxt = ons[i + 1][0] if i + 1 < len(ons) else end
        series.append((sharp_midi(p), nxt - t, False))
    return bars_from_series(series, -2, F(4))


def second_house():
    s = []
    for t in HOUSE_EB.replace("|", " ").split():
        p, d = t.split(":")
        s.append((sharp_midi(p), F(d), False))
    return bars_from_series(s, -3, F(4))


LY_STEP = {"c": 0, "d": 1, "e": 2, "f": 3, "g": 4, "a": 5, "b": 6}
LY_PC = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}


def _ly_tokens(text):
    text = re.sub(r"\\(?:break|bar\s*\"[^\"]*\"|partial\s*\d+)", " ", text)
    text = text.replace("\\(", " ").replace("\\)", " ")
    text = re.sub(r"[\[\]()|]", " ", text)
    return re.findall(r"([a-g])(is|es|s)?([',]*)(\d+)?(\.*)(~)?", text)


def parse_ly(text, start_oct, repeat2=True):
    """Tiny LilyPond relative-mode reader. Returns list of (midi, dur, tie). \\repeat unfold 2 {..} is read as an exact repeat."""
    m = re.search(r"\\repeat unfold 2 \{(.*?)\}", text, re.S)
    parts = [text] if not m else [text[:m.start()], m.group(1), text[m.end():]]
    out, ref, dur = [], start_oct * 7, F(1, 4)
    seqs = []
    for pi, part in enumerate(parts):
        seq = []
        for letter, acc, marks, d, dots, tie in _ly_tokens(part):
            if d:
                dur = F(4, int(d))
            n = LY_STEP[letter]
            o = min(range(-1, 9), key=lambda o: (abs(o * 7 + n - ref), -o))
            o += marks.count("'") - marks.count(",")
            ref = o * 7 + n
            pc = LY_PC[letter] + (1 if acc == "is" else -1 if acc in ("es", "s") else 0)
            dd = dur * (F(2) - F(1, 2 ** len(dots)) if dots else 1)
            seq.append((12 * (o + 1) + pc, dd, bool(tie)))
        seqs.append(seq)
        if m and pi == 1:
            seqs.append(list(seq))   # the repeat: same notes again
    return [n for s in seqs for n in s]


def second_joy():
    # 2/4; bars are 2 beats; beats = quarter notes
    return bars_from_series(parse_ly(JOY_LY, 5), -2, F(2))


def second_cradle():
    return bars_from_series(parse_ly(CRADLE_LY, 4), -5, F(3), pickup=F(1))


# ----------------------------------------------------------------- the tunes
TUNES = [
    dict(key="jingle", title="Jingle Bells", comp="James Lord Pierpont", year="1857", meter=(4, 4), primary=JB, second=second_jb,
         easy=(0, 8), per_sys=4, per_sys_easy=4, tempo=(66, 84), groups=[["C", "D"], ["E"], ["F", "G"]],
         src="Pierpont, 'One Horse Open Sleigh', Boston: Oliver Ditson, 1857. Chorus melody, 16 bars."),
    dict(key="deck", title="Deck the Halls", comp="Welsh air 'Nos Galan'", year="1794", meter=(4, 4), primary=DECK, second=second_deck,
         easy=(0, 8), per_sys=4, per_sys_easy=4, tempo=(66, 88), groups=[["C", "D"], ["E", "F"], ["G", "A", "B"]],
         src="Traditional Welsh melody, first printed 1794 (Edward Jones), much older. Melody only, 16 bars."),
    dict(key="housetop", title="Up on the Housetop", comp="Benjamin R. Hanby", year="1864", meter=(4, 4), primary=HOUSE, second=second_house,
         easy=(0, 8), per_sys=4, per_sys_easy=4, tempo=(66, 84), groups=[["C", "D", "E"], ["F", "G"], ["A"]],
         src="Hanby, 1864. Verse and chorus melody, 16 bars."),
    dict(key="joy", title="Joy to the World", comp="arr. Lowell Mason", year="1839 (adapted from Handel)", meter=(2, 4), primary=JOY, second=second_joy,
         easy=(0, 7), per_sys=4, per_sys_easy=4, tempo=(60, 72), groups=[["C", "D", "E"], ["F", "G"], ["A", "B"]],
         src="Mason, The Modern Psalmist, Boston, 1839 (tune 'Antioch', first published 1836 'from Handel'). Full melody, 20 bars."),
    dict(key="manger", title="Away in a Manger", comp="William J. Kirkpatrick, 'Cradle Song'", year="1895", meter=(3, 4), primary=CRADLE, second=second_cradle,
         easy=(0, 9), per_sys=5, per_sys_easy=5, pickup=F(1), tempo=(54, 66), groups=[["C", "D", "E"], ["F", "G"], ["A", "B"]],
         src="Kirkpatrick, Around the World with Christmas, Cincinnati, 1895. Melody with one-beat pickup, 16 bars."),
]
for t in TUNES:
    t["bars"] = parse_bars(t["primary"])
    t["L"] = F(t["meter"][0] * 4, t["meter"][1])
    t.setdefault("pickup", F(0))


# ----------------------------------------------------------------- simplified ("easy") rhythm
def easy_bar(bar):
    """Collapse everything shorter than a beat: a note that starts on a beat takes over the time up to the next beat-start note."""
    out, t, i = [], F(0), 0
    starts = []
    for n in bar:
        starts.append(t)
        t += n.dur
    total = t
    keep = [i for i, s in enumerate(starts) if s.denominator == 1]
    for j, i in enumerate(keep):
        end = starts[keep[j + 1]] if j + 1 < len(keep) else total
        out.append(Note(bar[i].pitch, end - starts[i], False))
    return out


def easy_bars(t):
    a, b = t["easy"]
    bars = t["bars"][a:b]
    out = []
    for bar in bars:
        e = easy_bar(bar)
        # a pickup bar keeps its (shifted) beat positions: its first note starts on a whole beat by construction
        out.append(e)
    return out


def used_letters(bars):
    return sorted({n.pitch[0] for b in bars for n in b}, key=lambda c: PCN[c])


def verify_tunes():
    errs = []
    for t in TUNES:
        k, L = t["key"], t["L"]
        bars = t["bars"]
        # (1) bar sums from the meter
        for i, b in enumerate(bars):
            want = t["pickup"] if (i == 0 and t["pickup"]) else (L - t["pickup"] if (i == len(bars) - 1 and t["pickup"]) else L)
            if bar_beats(b) != want:
                errs.append(f"{k} bar {i}: {bar_beats(b)} beats, meter wants {want}")
        for b in bars:
            for n in b:
                if n.pitch[0] not in PCN or midi(n.pitch) % 12 not in PC_NAME:
                    errs.append(f"{k}: {n.pitch} is not a white key")
        # (2) second encoding agrees note for note
        try:
            sec = t["second"]()
        except Exception as e:
            errs.append(f"{k}: second encoding failed: {e}")
            continue
        a = [(n.pitch, n.dur, n.tie) for b in bars for n in b]
        c = [(n.pitch, n.dur, n.tie) for b in sec for n in b]
        if a != c:
            first = next((i for i, (x, y) in enumerate(zip(a, c)) if x != y), min(len(a), len(c)))
            errs.append(f"{k}: primary and second encoding differ at note {first}: {a[first:first + 2]} vs {c[first:first + 2]} (lengths {len(a)}/{len(c)})")
        if [bar_beats(b) for b in sec] != [bar_beats(b) for b in bars]:
            errs.append(f"{k}: bar lengths differ between encodings")
    # (3) a third check: letter strings from a second website (source B), compared as plain text
    jb = "".join(n.pitch[0] for b in TUNES[0]["bars"] for n in b)
    if jb != JB_LETTERS.replace(" ", ""):
        errs.append("jingle: letters differ from source B")
    dk = "".join(n.pitch[0] for b in TUNES[1]["bars"] for n in b)
    if dk != DECK_LETTERS.replace(" ", ""):
        errs.append("deck: letters differ from source B")
    # groups
    for t in TUNES:
        letters = used_letters(t["bars"])
        flat = [c for g in t["groups"] for c in g]
        if sorted(flat) != sorted(set(flat)) or set(flat) != set(letters) or any(not g for g in t["groups"]):
            errs.append(f"{t['key']}: groups {t['groups']} do not partition the letters used {letters}")
    return errs
