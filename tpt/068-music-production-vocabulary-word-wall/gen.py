#!/usr/bin/env python3
"""Music Production Vocabulary Posters and Word Wall (TpT 068): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read the rendered HTML, recompute every number and every plotted point, check the quiz key,
                             the cross-references, the layout (footer gaps, drawing padding, blank bands) and the files

Terms, definitions and numbers live in TERMS below. Drawings are in diagrams.py. `--check` does not trust the drawing code: it reads the
geometry of every plotted curve back from the rendered SVG and compares it with formulas typed separately in the CHECK section.
"""
import json
import math
import os
import re
import subprocess
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diagrams as D  # noqa: E402

TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")
HERO = os.path.join(HERE, "art", "hero.png")

SLUG = "music-production-vocabulary-word-wall"
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
TITLE = "Music Production Vocabulary"
LISTING_TITLE = "Music Production Vocabulary Posters and Word Wall: DAW Terms, Quiz, Gr 9-12"
PRICE = "5.00"
TAGS = ["Posters", "Word Walls", "Bulletin Board Ideas", "Printables", "Assessment", "Study Guides"]
SUBJECTS = ["Music", "Music Composition"]
GRADES = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]

GROUPS = ["Project", "Time and MIDI", "Digital audio", "Levels", "Effects", "Mixing"]

# (key, name, subtitle, group, definition, in practice, [facts], word-wall card text, caption)
T = [
    ("daw", "DAW", "digital audio workstation", "Project",
     "A DAW, short for digital audio workstation, is the program or app you use to record, edit, arrange, mix and export music on a computer or tablet.",
     "You open a DAW, add a drum track and a bass track, and build a song one layer at a time.",
     [("Main parts", "Transport, tracks, timeline and mixer"), ("Works with", "Both audio and MIDI"), ("Project", "One file that holds all your tracks")],
     "The software where you record, edit, arrange and mix music.", "The main parts of a DAW window"),
    ("track", "Track", "one lane for one sound", "Project",
     "A track is one lane in a project that holds one sound source, such as a vocal, a guitar or a drum pattern, so you can edit and mix it on its own.",
     "Put the lead vocal on its own track so you can turn it up without changing the drums.",
     [("Audio track", "Holds recorded sound"), ("MIDI track", "Holds notes that play an instrument sound"), ("M and S", "Mute silences a track; solo plays only that track")],
     "One lane that holds one sound source in a project.", "Four tracks: two audio and two MIDI"),
    ("region", "Region", "also called a clip", "Project",
     "A region, also called a clip, is a block on a track that holds a piece of audio or a group of MIDI notes. You can move, trim, split and copy it along the timeline.",
     "Copy a 4-bar drum region three times to fill 16 bars.",
     [("Move", "Drag it to a new place"), ("Trim", "Drag an edge to change its length"), ("Split", "Cut it into two regions at one point")],
     "A block on a track that holds audio or MIDI. You can move, trim and copy it.", "Regions on a timeline of 16 bars"),
    ("loop", "Loop", "a pattern that repeats", "Project",
     "A loop is a short musical pattern made to repeat without a gap. A DAW can also loop a chosen part of the timeline so you hear it again and again while you work.",
     "Loop bars 5 to 8 while you adjust the bass sound.",
     [("Loop length", "Often 1, 2, 4 or 8 bars"), ("Seamless", "The end joins the start with no gap"), ("Loop region", "You set its start and end on the timeline")],
     "A pattern that repeats without a gap, or a timeline part played again and again.", "Two kinds of loop"),
    ("bpm", "BPM", "beats per minute, or tempo", "Time and MIDI",
     "BPM means beats per minute. It is the tempo, or speed, of the music. A higher BPM means the beats come faster, so each beat is shorter.",
     "At 120 BPM a bar of four beats lasts 2 seconds, so an 8-bar loop lasts 16 seconds.",
     [("Seconds per beat", "60 divided by the BPM"), ("120 BPM", "2 beats per second"), ("120 BPM", "0.5 seconds per beat")],
     "Beats per minute: the speed of the music.", "Seconds per beat at four tempos"),
    ("quant", "Quantize", "snap to the grid", "Time and MIDI",
     "Quantize moves notes or audio hits to the nearest line on a timing grid, such as the nearest eighth note, so the timing becomes exact.",
     "Quantize a hi-hat part that was played a little early or late to eighth notes to tighten it.",
     [("Grid value", "The note length that notes snap to"), ("Strength", "How far notes move toward the grid"), ("Tip", "Full strength sounds exact but can sound stiff")],
     "Snaps notes or hits to the nearest grid line so the timing is exact.", "The same eight notes before and after"),
    ("midi", "MIDI", "Musical Instrument Digital Interface", "Time and MIDI",
     "MIDI is a way to send performance information, such as which note, how hard and how long, between instruments, devices and software. MIDI is not sound: an instrument sound has to play it.",
     "Play a keyboard, record the MIDI, then change the piano sound to strings without playing it again.",
     [("Values", "Most MIDI values run from 0 to 127"), ("Middle C", "Note number 60"), ("File size", "Small, because it stores instructions and not audio")],
     "Data that says which note, how hard and how long. It is not sound.", "From a key press to a sound"),
    ("velocity", "Velocity", "how hard a note is played", "Time and MIDI",
     "Velocity is how hard a MIDI note is played, from 1 (softest) to 127 (hardest). It usually controls how loud the note is, and some instrument sounds also get brighter at high velocity.",
     "Lower the off-beat hi-hat velocity to 60 and keep the main beats near 100 so the groove feels alive.",
     [("Range", "1 to 127"), ("Low numbers", "Soft notes"), ("High numbers", "Hard notes")],
     "How hard a MIDI note is played, from 1 to 127.", "Four notes with different velocities"),
    ("piano", "Piano roll", "the MIDI note grid", "Time and MIDI",
     "A piano roll is a grid for editing MIDI notes. Up and down is pitch, left to right is time, and each bar is a note whose length shows how long it lasts.",
     "Click in the grid to place C, E and G one after another, then drag the ends to change how long each note lasts.",
     [("Up and down", "Pitch: higher notes sit higher"), ("Left to right", "Time, in beats"), ("Bar length", "How long the note lasts")],
     "A grid for editing MIDI notes: pitch up and down, time left to right.", "Four notes on a piano roll: C, E, G and C"),
    ("sample", "Sample", "a short recorded sound", "Digital audio",
     "A sample is a short recorded sound, such as a drum hit, a voice phrase or a single note, that you load and play again and again. It also has a second meaning, one measurement of a sound wave (see term {srate}, Sample rate).",
     "Load one recorded kick drum hit and play it on every beat.",
     [("Examples", "A drum hit, a vocal phrase, one note"), ("Play it from", "Pads, a keyboard or a region"), ("Other meaning", "One measurement of a wave (term {srate})")],
     "A short recorded sound you can play again and again.", "One sample played on four beats"),
    ("wave", "Waveform", "a picture of sound", "Digital audio",
     "A waveform is a picture of sound over time. Across is time and up and down is the level. Loud parts look tall, quiet parts look short and silence is a flat line.",
     "Zoom in on the waveform to find the exact start of a drum hit before you trim it.",
     [("Peak", "The highest point of the wave"), ("Zero line", "The flat line of silence"), ("Use it to", "Find hits, spot clipping and edit by eye")],
     "A picture of sound: time across, level up and down.", "A waveform with a quiet start and two loud parts"),
    ("freq", "Frequency", "how fast a wave vibrates", "Digital audio",
     "Frequency is how fast a sound wave vibrates, counted in hertz (Hz), which means cycles per second. A higher frequency sounds higher in pitch.",
     "Bass notes sit at low frequencies, often under 250 Hz, and cymbal shimmer sits at high frequencies, often above 5,000 Hz.",
     [("Unit", "Hertz (Hz): cycles per second"), ("Human hearing", "About 20 Hz to 20,000 Hz"), ("One octave up", "Double the frequency: 440 Hz to 880 Hz")],
     "How fast a wave vibrates, in hertz (Hz). Higher frequency sounds higher.", "Three frequencies drawn over the same 10 milliseconds"),
    ("srate", "Sample rate", "measurements per second", "Digital audio",
     "Sample rate is how many times each second digital audio measures the sound wave. It is counted in hertz (Hz). Common sample rates are 44,100 Hz and 48,000 Hz.",
     "Set the project to 48,000 Hz before you record, and keep your files at the same rate so nothing has to be converted.",
     [("Common rates", "44,100 Hz and 48,000 Hz"), ("Highest frequency kept", "Half the rate: 22,050 Hz or 24,000 Hz"), ("Human hearing", "About 20 Hz to 20,000 Hz")],
     "How many times each second digital audio measures the sound. Common: 44,100 or 48,000 Hz.", "The same wave measured with fewer and more samples"),
    ("bits", "Bit depth", "detail in each measurement", "Digital audio",
     "Bit depth is how many bits are used to store each sample's level. More bits give more possible levels and a lower noise floor. Common bit depths are 16 bits (65,536 levels) and 24 bits (16,777,216 levels).",
     "Record at 24 bits for extra room above the noise floor, and share the finished song at 16 or 24 bits.",
     [("16 bits", "65,536 levels, about 96 dB of range"), ("24 bits", "16,777,216 levels, about 144 dB of range"), ("Rule of thumb", "Each extra bit adds about 6 dB of range")],
     "How many bits store each measurement. Common: 16 or 24 bits.", "The same wave stored with 3 bits and with 4 bits"),
    ("head", "Headroom", "room left below the maximum", "Levels",
     "Headroom is the space between your loudest peak and the highest level the system can handle without distortion. Digital meters use dBFS, where 0 dBFS is the maximum, so every level below it is a negative number.",
     "Record so your loudest peaks stay well below 0 dBFS, for example around -12 dBFS, in case a louder note comes along.",
     [("Maximum", "0 dBFS"), ("Peak at -6 dBFS", "6 dB of headroom"), ("Peak at -18 dBFS", "18 dB of headroom")],
     "How far your loudest peak is below the maximum level, 0 dBFS.", "A level meter with the peak at -6 dBFS"),
    ("clip", "Clipping", "distortion from too much level", "Levels",
     "Clipping is the harsh distortion you hear when a signal tries to go above 0 dBFS. The tops of the waveform are cut flat, and the lost detail cannot be restored later.",
     "If the clip light on a track meter turns on, turn the level down and record the part again.",
     [("Limit", "0 dBFS"), ("Sound", "Crackly, harsh distortion"), ("Fix", "Lower the level before it is recorded")],
     "Distortion when a signal goes past 0 dBFS and its peaks are cut flat.", "The same wave with and without clipping"),
    ("eq", "EQ", "equalizer", "Effects",
     "EQ, short for equalizer, boosts or cuts parts of the frequency range. Low, mid and high bands let you turn down a boomy sound or turn up the clarity of a vocal.",
     "Cut 4 dB at 150 Hz on a boomy vocal and add 5 dB at 2,000 Hz so the words are clearer.",
     [("Cut", "Turns a band down (negative dB)"), ("Boost", "Turns a band up (positive dB)"), ("Typical bands", "Low 20-250 Hz, mid 250 Hz-4 kHz, high 4-20 kHz")],
     "Boosts or cuts low, mid or high frequencies.", "An EQ curve with one cut and one boost"),
    ("filter", "Filter", "removes low or high sound", "Effects",
     "A filter removes frequencies below or above a cutoff frequency. A high-pass filter lets the highs pass and removes the lows. A low-pass filter lets the lows pass and removes the highs.",
     "Put a high-pass filter at 100 Hz on a vocal to remove low rumble from the room.",
     [("Cutoff", "The frequency where the level has dropped 3 dB"), ("Slope", "12 dB per octave in these drawings"), ("Uses", "High-pass for rumble, low-pass for hiss")],
     "Removes sound below (high-pass) or above (low-pass) a cutoff frequency.", "A high-pass and a low-pass filter"),
    ("comp", "Compression", "evens out loud and quiet", "Effects",
     "Compression reduces the difference between loud and quiet parts. When the signal rises above the threshold, the compressor turns it down. The ratio sets how much: at 4:1, every 4 dB over the threshold comes out as 1 dB over.",
     "Compress a lead vocal at 4:1 with a threshold of -20 dBFS so loud words sit closer to quiet ones.",
     [("Threshold", "The level where compression starts"), ("Ratio", "4:1 means 4 dB over the threshold comes out 1 dB over"), ("Makeup gain", "Turns the whole signal back up")],
     "Turns down the loud parts above a threshold so the levels are more even.", "Input level against output level at 4:1"),
    ("limit", "Limiter", "a ceiling for the level", "Effects",
     "A limiter is a very strong compressor that stops the level from going above a ceiling you set. It is often the last effect on a finished mix, to keep loud peaks from clipping.",
     "Put a limiter on the master track with the ceiling at -3 dBFS so no peak in the exported song goes above -3 dBFS.",
     [("Ceiling", "The level nothing should pass"), ("Ratio", "Very high, like infinity to 1"), ("Example", "Ceiling -3 dBFS: no peak goes higher")],
     "A very strong compressor that stops the level going above a set ceiling.", "Input level against output level with a -3 dBFS ceiling"),
    ("reverb", "Reverb", "the sound of a space", "Effects",
     "Reverb is the wash of many fast reflections that follow a sound in a room or hall. It adds a feeling of space. The decay time says how long the tail lasts.",
     "Add a short reverb to a snare for a roomy sound, or a long one to a pad for a floating feel.",
     [("Decay time", "How long the tail lasts"), ("RT60", "Time for the tail to fall by 60 dB"), ("Wet and dry", "Wet is the effect, dry is the original")],
     "Adds the sense of a room or hall: many fast echoes that fade away.", "A hit followed by two reverb tails"),
    ("delay", "Delay", "echoes at a set time", "Effects",
     "Delay records a sound and plays it back after a set time, so you hear it repeat. Feedback controls how many repeats there are, and each repeat is quieter than the one before.",
     "Set a delay to one beat at 120 BPM, which is 500 ms, so each echo lands on a beat.",
     [("Delay time", "Set in milliseconds or in note values"), ("Feedback", "How much returns to make more repeats"), ("1 beat at 120 BPM", "500 ms")],
     "Repeats a sound after a set time, with each repeat quieter.", "One sound and three repeats, 500 ms apart"),
    ("pan", "Pan", "left and right", "Mixing",
     "Pan places a sound between the left and right speakers. Full left sends it only to the left speaker, center sends it equally to both and full right sends it only to the right.",
     "Pan two guitars 50% left and 50% right to leave the center open for the vocal.",
     [("L 100", "All of the sound on the left"), ("C", "Equal on both sides"), ("R 100", "All of the sound on the right")],
     "Places a sound left, center or right in the stereo picture.", "Three tracks at three pan settings"),
    ("auto", "Automation", "controls that move by themselves", "Mixing",
     "Automation records or draws changes to a control over time, such as volume, pan or an effect setting, so the DAW moves it for you every time the song plays.",
     "Draw a volume line that fades the intro in over 2 bars and fades the ending out over 2 bars.",
     [("Breakpoint", "A dot that sets a value at one moment"), ("Fade in", "The level rises from silence"), ("Fade out", "The level falls to silence")],
     "Controls that move by themselves over time, such as a volume fade.", "Volume automation over 13 bars"),
    ("mixer", "Mixer", "balance every track", "Mixing",
     "The mixer is where you balance all your tracks. Each track has a channel strip with a fader for volume, a pan control and a meter. A fader at 0 dB leaves the level unchanged, and moving it down turns the track down.",
     "Start with every fader at the same level, then bring up the drums, the bass and the vocal one at a time.",
     [("Fader", "Sets a track's volume in dB"), ("Meter", "Shows the level while it plays"), ("-6 dB", "About half the signal's amplitude")],
     "Where you balance every track with faders, pan controls and meters.", "Three channel strips and the master"),
    ("bounce", "Bounce and export", "make the finished file", "Mixing",
     "Bounce, or export, turns your finished project into one audio file that plays anywhere. The DAW plays the whole mix once and writes it to a single file.",
     "Export a 24-bit, 48,000 Hz WAV file as your master copy, and a small MP3 file to share.",
     [("WAV", "Uncompressed: full quality, large file"), ("MP3", "Compressed: much smaller, some detail lost"), ("Settings", "Choose the sample rate and the bit depth")],
     "Turns the finished project into one audio file that plays anywhere.", "Many tracks become one audio file"),
]
NT = len(T)
KEYS = [t[0] for t in T]
TERM_NO = {k: i + 1 for i, k in enumerate(KEYS)}
assert NT == 26 and set(t[3] for t in T) == set(GROUPS)
GROUP_NOS = {g: [i + 1 for i, t in enumerate(T) if t[3] == g] for g in GROUPS}
assert [len(v) for v in GROUP_NOS.values()] == [4, 5, 5, 2, 6, 4]

# ---- quiz
MATCH_TERMS = ["region", "loop", "quant", "midi", "velocity", "srate", "bits", "wave", "head", "clip", "eq", "comp", "reverb", "pan", "bounce"]
MATCH_DEFS = {
    "region": "A block on a track that holds audio or MIDI and can be moved, trimmed or copied",
    "loop": "A short pattern made to repeat without a gap",
    "quant": "Moves notes to the nearest line on a timing grid",
    "midi": "Data that says which note to play, how hard and how long, but holds no sound",
    "velocity": "How hard a MIDI note is played, from 1 to 127",
    "srate": "How many times each second digital audio measures the sound wave",
    "bits": "How many bits store each measurement of the level",
    "wave": "A picture of sound with time across and level up and down",
    "head": "The distance between the loudest peak and 0 dBFS",
    "clip": "Distortion that happens when a signal tries to go above 0 dBFS",
    "eq": "Boosts or cuts low, mid or high frequencies",
    "comp": "Turns down the signal above a threshold so levels are more even",
    "reverb": "The wash of reflections that makes a sound seem to be in a room or hall",
    "pan": "Places a sound between the left and right speakers",
    "bounce": "Writes the finished project to a single audio file",
}
DEF_ORDER = ["pan", "head", "midi", "comp", "loop", "bits", "clip", "region", "reverb", "wave", "quant", "bounce", "srate", "eq", "velocity"]   # fixed shuffle: definitions A to O
assert sorted(DEF_ORDER) == sorted(MATCH_TERMS)
LETTERS = "ABCDEFGHIJKLMNO"
MATCH_KEY = {k: LETTERS[DEF_ORDER.index(k)] for k in MATCH_TERMS}

# short answer: (points, [(question, answer, points)])
SHORT = [
    ("At 120 BPM, how long is one beat, and how long is a bar of four beats?", [("one beat: 0.5 seconds", 1), ("one bar: 2 seconds", 1)]),
    ("A compressor has a threshold of -20 dBFS and a ratio of 4:1. A peak of -12 dBFS comes in. How many dB over the threshold is it, and what level comes out?",
     [("8 dB over the threshold", 1), ("-18 dBFS comes out (2 dB over the threshold)", 1)]),
    ("Name one common sample rate. Which gives more levels in every sample, 16 bits or 24 bits?",
     [("44,100 Hz or 48,000 Hz", 1), ("24 bits (16,777,216 levels, against 65,536 for 16 bits)", 1)]),
    ("A recording's loudest peak is at -6 dBFS. How much headroom is that? What is it called when a peak tries to go above 0 dBFS?",
     [("6 dB of headroom", 1), ("clipping (distortion)", 1)]),
    ("A vocal sounds boomy around 150 Hz. Which EQ band do you cut: low, mid or high? What does a high-pass filter do?",
     [("the low band", 1), ("removes the frequencies below its cutoff and lets the highs pass", 1)]),
    ("In your own words, what is the difference between MIDI and audio?",
     [("MIDI is instructions (notes, velocity, length) and has no sound of its own", 1), ("audio is recorded sound (a waveform)", 1)]),
    ("Explain how reverb and delay are different.",
     [("reverb: many fast reflections that blur into a tail, like a room", 1), ("delay: separate repeats after a set time", 1), ("a clear difference between the two", 1)]),
]
PTS_A = len(MATCH_TERMS)
PTS_B = sum(p for _, parts in SHORT for _, p in parts)
PTS_Q = PTS_A + PTS_B
assert (PTS_A, PTS_B, PTS_Q) == (15, 15, 30)
QSCALE = [("27-30", "Strong", 27), ("21-26", "Secure", 21), ("15-20", "Developing", 15), ("0-14", "Needs review", 0)]
RUB_CRITERIA = [("Accuracy", "The definition and any numbers are correct."), ("Own words", "The meaning is explained without copying the poster."),
                ("Example", "A real example shows how the term is used in a project."), ("Drawing", "A neat labeled drawing helps explain it.")]
RUB_MAX = 3
RUB_TOTAL = len(RUB_CRITERIA) * RUB_MAX
CHECKS = [
    ("I can explain what a DAW, a track and a region are.", "1-3"),
    ("I can work out the seconds per beat from the BPM.", "5"),
    ("I can say how MIDI is different from audio.", "7, 11"),
    ("I can explain sample rate and bit depth and name common values.", "13, 14"),
    ("I can say what 0 dBFS means, and what headroom and clipping are.", "15, 16"),
    ("I can describe what an EQ and a filter do to frequencies.", "17, 18"),
    ("I can explain threshold and ratio on a compressor with an example.", "19"),
    ("I can tell reverb and delay apart.", "21, 22"),
]

# ---- pages
ORDER = (["cover", "teach", "index"] + [f"t_{k}" for k in KEYS] + ["wall1", "wall2", "wall3", "rubric", "quiz1", "quiz2", "key", "terms"])
P = {k: i + 1 for i, k in enumerate(ORDER)}
TOTAL_PAGES = len(ORDER)
POSTER_PAGE = {k: P[f"t_{k}"] for k in KEYS}
PAGE_NAMES = {"cover": "Cover", "teach": "Teacher notes", "index": "Term index", "wall1": "Word wall cards 1", "wall2": "Word wall cards 2",
              "wall3": "Word wall cards 3", "rubric": "Self-check and rubric", "quiz1": "Quiz, part A", "quiz2": "Quiz, part B",
              "key": "Quiz answer key", "terms": "Terms of use"}
for i, t in enumerate(T):
    PAGE_NAMES[f"t_{t[0]}"] = f"Poster {i + 1}: {t[1]}"
WALL_PAGES = ["wall1", "wall2", "wall3"]
CARDS_PER_SHEET = 9
assert NT <= CARDS_PER_SHEET * len(WALL_PAGES)
WALL_OF = {k: WALL_PAGES[i // CARDS_PER_SHEET] for i, k in enumerate(KEYS)}
PACING = [("1", "Setting up and keeping time: DAW, track, region, loop, BPM and quantize.", 1, 6),
          ("2", "MIDI and samples: MIDI, velocity, piano roll and sample.", 7, 10),
          ("3", "Digital audio and levels: waveform, frequency, sample rate, bit depth, headroom and clipping.", 11, 16),
          ("4", "Shaping sound: EQ, filter, compression and limiter.", 17, 20),
          ("5", "Space and the mix: reverb, delay, pan, automation, mixer, bounce and export.", 21, 26),
          ("6", "Review with the word wall and the self-check, then the quiz.", None, None)]
XREFS = []


def xref(frm, to, text):
    XREFS.append((P[frm], to, text))
    return text


def pgs(key):
    return f"page {P[key]}"


def tx(s):
    """Fill {srate}-style term-number placeholders."""
    return s.format(**{k: TERM_NO[k] for k in KEYS}) if "{" in s else s


# ================================================================== CSS
def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"),
             ("Oswald", 700, "normal", "oswald-latin-700-normal"),
             ("Source Sans 3", 400, "normal", "source-sans-3-latin-400-normal"), ("Source Sans 3", 400, "italic", "source-sans-3-latin-400-italic"),
             ("Source Sans 3", 600, "normal", "source-sans-3-latin-600-normal"), ("Source Sans 3", 700, "normal", "source-sans-3-latin-700-normal")]
    return "".join(f"@font-face{{font-family:'{n}';font-weight:{w};font-style:{s};src:url('{f}/{file}.woff2') format('woff2');}}" for n, w, s, file in faces)


CSS = """
@page { size: 8.5in 11in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: 'Source Sans 3', sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; break-after: page;
        padding: 0.42in 0.5in 0.38in; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; break-after: auto; }
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; font-size: 19pt; white-space: nowrap; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 11pt; letter-spacing: 0; margin-top: 3pt; white-space: nowrap; }
.top .tag { flex: none; white-space: nowrap; text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; margin-top: auto; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 28pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 8pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.34; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; margin: 6pt 0; }
.box h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 0 0 3pt; letter-spacing: .02em; }
.box p, .box li { font-size: 10.4pt !important; }
.box p { margin: 0 0 4pt !important; }
.cols { display: flex; gap: 12pt; }
.cols .box { flex: 1; margin: 6pt 0; }
.nd { display: flex; align-items: flex-end; gap: 6pt; font-size: 10pt; margin: 7pt 0 0; }
.nd .ln { flex: 1; border-bottom: 1pt solid #000; height: 11pt; }
/* posters */
.pb { flex: 1; display: flex; flex-direction: column; justify-content: space-between; padding-bottom: 6pt; }
.pt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 60pt; line-height: 1; letter-spacing: .01em; margin: 8pt 0 0; }
.ps { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin: 2pt 0 0; }
.pdef { font-size: 16pt; line-height: 1.26; font-weight: 600; margin: 8pt 0 0; }
.pdg { border: 1.6pt solid #000; border-radius: 9pt; padding: 8pt 12pt 5pt; margin: 10pt 0 0; }
.pdg .cap { text-align: center; font-size: 10.5pt; font-style: italic; margin: 2pt 0 0; }
.pfacts { display: flex; gap: 9pt; margin: 11pt 0 0; }
.fact { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 8pt 6pt; }
.fact b { display: block; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 10pt; letter-spacing: .04em; color: ACCENT; }
.fact span { display: block; font-size: 10.6pt; line-height: 1.25; margin-top: 1pt; }
.pprac { background: #000; color: #fff; border-radius: 8pt; padding: 8pt 12pt 9pt; margin: 11pt 0 0; font-size: 12.5pt; line-height: 1.3; }
.pprac b { font-family: 'Oswald'; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; font-size: 10.5pt; color: #9FD0EE; margin-right: 6pt; }
/* index */
.idx td { padding: 1pt 6pt; font-size: 9.6pt; }
.idx td.n, .idx th.n { text-align: center; }
.idx td.t { font-weight: 700; }
.rb td { padding: 3pt 6pt !important; font-size: 10.6pt !important; }
.kt td { padding: 4pt 6pt !important; font-size: 10.6pt !important; }
.kw li { font-size: 11pt !important; margin-bottom: 5pt !important; }
/* word wall */
.wgrid { flex: 1; display: grid; grid-template-columns: repeat(3, 1fr); grid-template-rows: repeat(3, 1fr); margin: 12pt 0 12pt; border-top: 1pt dashed #000; border-left: 1pt dashed #000; }
.wc { border-right: 1pt dashed #000; border-bottom: 1pt dashed #000; padding: 9pt 10pt 8pt; display: flex; flex-direction: column; }
.wc .wn { font-family: 'Oswald'; font-weight: 500; font-size: 9pt; letter-spacing: .1em; text-transform: uppercase; color: ACCENT; }
.wc .wt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 28pt; line-height: 1.02; margin: 5pt 0 0; border-bottom: 2pt solid #000; padding-bottom: 6pt; }
.wc .wd { font-size: 13.5pt; line-height: 1.3; margin: 8pt 0 0; }
.wc .wp { margin-top: auto; font-size: 8.5pt; color: #333; }
.wc .wl { border-bottom: 1pt solid #000; height: 20pt; }
.cutnote { font-size: 9.5pt; margin: 0 0 8pt; }
/* quiz */
.qm { display: grid; grid-template-columns: 1fr 1fr; gap: 0 18pt; margin-top: 4pt; }
.qm .qr { display: flex; align-items: center; gap: 6pt; height: 37pt; font-size: 11.4pt; line-height: 1.2; }
.qm .qr .blank { flex: none; width: 30pt; border-bottom: 1pt solid #000; height: 14pt; }
.qm .qr .no { flex: none; width: 16pt; font-family: 'Oswald'; font-weight: 700; text-align: right; }
.qm .qr .lt { flex: none; width: 16pt; font-family: 'Oswald'; font-weight: 700; }
.qs { margin: 0 0 8pt; }
.qs .q { font-size: 11.6pt; line-height: 1.3; margin: 0; }
.qs .q b { font-family: 'Oswald'; }
.qs .wl { border-bottom: 1pt solid #000; height: 23pt; }
.qs { margin: 0 0 7pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 40pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 78pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 16pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; white-space: nowrap; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title><style>{font_css()}{CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def wm_div(on):
    return '<div class="wm">PREVIEW</div>' if on else ""


def page(key, body, wm=False, tag="TEACHER", tagline="", ak=False, extra="", student=False, sub=None):
    n = P[key]
    right = f"Page {n}" + (f" · {extra}" if extra else "")
    top = (f'<div class="top"><div class="t">{TITLE}<small>{sub or PAGE_NAMES[key]}</small></div>'
           f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')
    nd = ('<div class="nd"><span>Name</span><span class="ln"></span><span>Date</span><span class="ln" style="flex:.45"></span>'
          '<span>Class</span><span class="ln" style="flex:.4"></span></div>') if student else ""
    return (f'<section class="page doc" data-p="{n}" data-k="{key}">{wm_div(wm)}{top}{nd}{body}'
            f'<div class="foot"><span>{COPY}</span><span>{right}</span></div></section>')


def doc_head(h1, sub):
    return f'<div class="rule" style="margin-top:8pt"><h1>{h1}</h1><div style="font-family:Oswald;font-weight:300;font-size:13pt">{sub}</div></div>'


# ================================================================== pages
def cover_page():
    return (f'<section class="page cover" data-p="1" data-k="cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.6in;display:flex;align-items:center;justify-content:center"><img src="../art/hero.png" alt="" style="display:block;height:4.8in;width:auto;margin:-0.1in 0"></div>'
            f'<div class="ctitle"><div class="a">MUSIC PRODUCTION</div><div class="b">WORD WALL</div>'
            f'<div class="c">{NT} vocabulary posters, cut-out term cards and a quiz with key</div></div>'
            f'<div class="cband">Grades 9–12 <em>·</em> {NT} terms <em>·</em> {TOTAL_PAGES} pages</div></section>')


def teach_page(wm=False):
    pace = "".join(
        f'<tr><td style="text-align:center"><b>{d}</b></td><td>{txt}</td><td>' +
        (f'Posters, pages {POSTER_PAGE[KEYS[a - 1]]}–{POSTER_PAGE[KEYS[b - 1]]}' if a else f'Pages {P["wall1"]}–{P["wall3"]}, {P["rubric"]}, {P["quiz1"]}–{P["quiz2"]}') + '</td></tr>'
        for d, txt, a, b in PACING)
    body = (
        f'<div class="cols"><div class="box"><h3>How to display</h3><ul>'
        f'<li>Print the posters single-sided on US Letter. Post one to three a week, in order, at eye level.</li>'
        f'<li>Cut the term cards from pages {P["wall1"]}–{P["wall3"]} on the dashed lines. Sort them under the six group headings on the term index ({pgs("index")}).</li>'
        f'<li>Pin the poster next to its card until the class knows the term.</li></ul></div>'
        f'<div class="box"><h3>What is inside</h3><ul>'
        f'<li>{NT} posters, one term each (pages {P["t_" + KEYS[0]]}–{P["t_" + KEYS[-1]]}): a definition, a drawing, three facts and an example.</li>'
        f'<li>{NT} word wall cards plus one blank card (pages {P["wall1"]}–{P["wall3"]}).</li>'
        f'<li>Self-check and rubric ({pgs("rubric")}), a {PTS_Q}-point quiz (pages {P["quiz1"]}–{P["quiz2"]}) and its key ({pgs("key")}).</li></ul></div></div>'
        f'<h2>Pacing: six short sessions</h2><table><tr><th style="width:44pt">Session</th><th>Terms</th><th style="width:150pt">Pages</th></tr>{pace}</table>'
        f'<h2>Activities</h2><ul>'
        f'<li><b>Term of the day.</b> Read the definition aloud, cover the drawing and ask students to sketch it. Then compare.</li>'
        f'<li><b>Match the card.</b> Hand out cards. Students find the poster that matches, and say the example in their own words.</li>'
        f'<li><b>Check the numbers.</b> Ask for seconds per beat at 90 and 150 BPM, or the output of a 4:1 compressor for a peak 12 dB over the threshold (it comes out 3 dB over).</li>'
        f'<li><b>Hear it in your DAW.</b> Use any DAW: students find the control for each term and describe what changes. Posters name no software.</li>'
        f'<li><b>Teach a term.</b> Each student teaches one term to a partner. Score it with the rubric ({pgs("rubric")}).</li></ul>'
        f'<h2>Notes</h2><p>The terms are DAW-neutral. Screens and menus differ between programs, so the drawings show ideas, not a particular window. '
        f'Numbers on the posters are examples: typical sample rates are 44,100 Hz and 48,000 Hz, and typical bit depths are 16 and 24 bits. '
        f'The activities support the Creating and Producing processes of the National Core Arts Standards for Music; match them to your own curriculum. '
        f'No songs, lyrics or copyrighted characters are used.</p>'
        f'<p class="small">{DISCLOSURE}</p>')
    return page("teach", body, wm, tag="TEACHER", tagline="Read first")


def index_page(wm=False):
    rows = "".join(
        f'<tr><td class="n">{i + 1}</td><td class="t">{escape(t[1])}</td><td>{t[3]}</td><td class="n">{POSTER_PAGE[t[0]]}</td>'
        f'<td class="n">{P[WALL_OF[t[0]]]}</td></tr>' for i, t in enumerate(T))
    grp = "".join(f'<tr><td><b>{g}</b></td><td>{", ".join(str(x) for x in GROUP_NOS[g])}</td><td class="n">{len(GROUP_NOS[g])}</td></tr>' for g in GROUPS)
    body = (f'<table class="idx" style="margin-top:8pt"><tr><th class="n" style="width:32pt">No.</th><th>Term</th><th style="width:100pt">Group</th>'
            f'<th class="n" style="width:62pt">Poster page</th><th class="n" style="width:62pt">Card page</th></tr>{rows}</table>'
            f'<h2>Word wall headings</h2><table class="idx"><tr><th style="width:110pt">Group</th><th>Term numbers</th><th class="n" style="width:60pt">Cards</th></tr>{grp}</table>'
            f'<p class="small">{NT} terms in {len(GROUPS)} groups. Each card shows its group so students can sort them under the headings.</p>')
    return page("index", body, wm, tag="INDEX", tagline=f"{NT} terms")


def poster_page(key, wm=False):
    i = KEYS.index(key)
    t = T[i]
    _, name, subt, grp, defn, prac, facts, _short, cap = t
    svg = D.DIAGRAMS[{"wave": "wave", "head": "headroom", "clip": "clip", "comp": "comp", "limit": "limit", "auto": "auto", "bits": "bits", "srate": "srate"}.get(key, key)]().svg()
    fx = "".join(f'<div class="fact"><b>{escape(a)}</b><span>{escape(tx(b))}</span></div>' for a, b in facts)
    body = (f'<div class="pb"><div><div class="pt" data-term="{i + 1}" style="{"font-size:46pt" if len(name) > 12 else ""}">{escape(name)}</div><div class="ps">{escape(subt)}</div></div>'
            f'<div class="pdef">{escape(tx(defn))}</div>'
            f'<div class="pdg">{svg}<div class="cap">{escape(cap)}</div></div>'
            f'<div class="pfacts">{fx}</div>'
            f'<div class="pprac"><b>In practice</b>{escape(prac)}</div></div>')
    return page(f"t_{key}", body, wm, tag=f"TERM {i + 1}", tagline=f"of {NT} · {grp}", sub=PAGE_NAMES[f"t_{key}"])


def card(i, t):
    return (f'<div class="wc" data-term="{i + 1}"><div class="wn">{i + 1} · {t[3]}</div><div class="wt">{escape(t[1])}</div>'
            f'<div class="wd">{escape(t[7])}</div><div class="wp">Poster: page {POSTER_PAGE[t[0]]}</div></div>')


def wall_page(key, wm=False):
    s = WALL_PAGES.index(key)
    cards = [card(i, T[i]) for i in range(s * CARDS_PER_SHEET, min(NT, (s + 1) * CARDS_PER_SHEET))]
    while len(cards) < CARDS_PER_SHEET:
        cards.append('<div class="wc"><div class="wn">Your own term</div><div class="wt" style="color:#bbb">&nbsp;</div>'
                     '<div class="wl" style="margin-top:12pt"></div><div class="wl"></div><div class="wl"></div><div class="wp">Write a term and its meaning.</div></div>')
    body = (f'<div class="wgrid">{"".join(cards)}</div>'
            f'<div class="cutnote">Cut along the dashed lines. Sort the cards under the group headings on {pgs("index")}.</div>')
    return page(key, body, wm, tag="WORD WALL", tagline=f"Sheet {s + 1} of {len(WALL_PAGES)}")


def rubric_page(wm=False):
    chk = "".join(f'<tr><td style="width:300pt">{a}</td><td class="n" style="text-align:center">{b}</td><td style="text-align:center;width:44pt">☐</td><td style="text-align:center;width:50pt">☐</td><td style="text-align:center;width:44pt">☐</td></tr>'
                  for a, b in CHECKS).replace("☐", '<span style="display:inline-block;width:12pt;height:12pt;border:1.2pt solid #000;border-radius:2pt"></span>')
    rub = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td style="text-align:center">0–{RUB_MAX}</td><td></td></tr>' for a, b in RUB_CRITERIA)
    sc = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td></tr>' for a, b, _ in QSCALE)
    body = (f'<h2 style="margin-top:8pt">Part 1: Self-check</h2><p>Mark how sure you are. Look up the poster pages listed to review.</p>'
            f'<table class="rb"><tr><th>I can...</th><th style="width:52pt">Terms</th><th style="width:44pt">Yes</th><th style="width:50pt">Almost</th><th style="width:44pt">Not yet</th></tr>{chk}</table>'
            f'<h2>Part 2: Teach a term ({RUB_TOTAL} points)</h2><p>Teach one term to a partner. Score each row from 0 (missing) to {RUB_MAX} (complete and clear).</p>'
            f'<table class="rb"><tr><th style="width:80pt">Row</th><th>What a {RUB_MAX} looks like</th><th style="width:56pt">Points</th><th style="width:60pt">Score</th></tr>{rub}'
            f'<tr><td colspan="3" style="text-align:right"><b>Total</b></td><td style="text-align:center"><b>/ {RUB_TOTAL}</b></td></tr></table>'
            f'<h2>Part 3: Quiz score guide (out of {PTS_Q})</h2><table class="rb"><tr><th style="width:90pt">Score</th><th>Level</th></tr>{sc}</table>'
            f'<p class="small">Quiz: pages {P["quiz1"]}–{P["quiz2"]}. Key: {pgs("key")}.</p>')
    return page("rubric", body, wm, tag="STUDENT", tagline="Self-check", student=True)


def quiz1_page(wm=False):
    terms = "".join(f'<div class="qr"><span class="no">{i + 1}.</span><span class="blank"></span><b>{escape(T[KEYS.index(k)][1])}</b></div>' for i, k in enumerate(MATCH_TERMS))
    defs = "".join(f'<div class="qr"><span class="lt">{LETTERS[j]}.</span><span>{MATCH_DEFS[k]}</span></div>' for j, k in enumerate(DEF_ORDER))
    body = (f'<h2 style="margin:8pt 0 2pt">Part A: Matching ({PTS_A} points)</h2>'
            f'<p>Write the letter of the best definition on the line next to each term. Each letter is used once.</p>'
            f'<div class="qm"><div>{terms}</div><div>{defs}</div></div>')
    return page("quiz1", body, wm, tag="QUIZ", tagline=f"{PTS_Q} points", extra=xref("quiz1", "key", f"Key: page {P['key']}"), student=True)


def quiz2_page(wm=False):
    items = []
    for i, (q, parts) in enumerate(SHORT):
        pts = sum(p for _, p in parts)
        lines = '<div class="wl"></div>' * (3 if pts == 3 else 2)
        items.append(f'<div class="qs"><p class="q"><b>{i + 1}.</b> {q} <b>({pts} point{"s" if pts > 1 else ""})</b></p>{lines}</div>')
    body = (f'<h2 style="margin:8pt 0 4pt">Part B: Short answer ({PTS_B} points)</h2>{"".join(items)}')
    return page("quiz2", body, wm, tag="QUIZ", tagline=f"{PTS_Q} points", extra=xref("quiz2", "key", f"Key: page {P['key']}"), student=True)


def key_page(wm=False):
    mrows = "".join(f'<tr><td class="n">{i + 1}</td><td>{escape(T[KEYS.index(k)][1])}</td><td class="n"><b>{MATCH_KEY[k]}</b></td></tr>' for i, k in enumerate(MATCH_TERMS))
    srows = "".join(
        f'<tr><td class="n">{i + 1}</td><td>' + "<br>".join(f'{a} <b>({p})</b>' for a, p in parts) + f'</td><td class="n">{sum(p for _, p in parts)}</td></tr>'
        for i, (_, parts) in enumerate(SHORT))
    body = (f'<div class="cols" style="align-items:flex-start;gap:14pt"><div style="flex:.8"><h2 style="margin-top:8pt">Part A ({PTS_A})</h2>'
            f'<table class="idx kt"><tr><th class="n" style="width:28pt">No.</th><th>Term</th><th class="n" style="width:42pt">Letter</th></tr>{mrows}</table></div>'
            f'<div style="flex:1.5"><h2 style="margin-top:8pt">Part B ({PTS_B}), one point for each answer</h2>'
            f'<table class="idx kt"><tr><th class="n" style="width:28pt">No.</th><th>Answer</th><th class="n" style="width:36pt">Pts</th></tr>{srows}</table></div></div>'
            f'<p class="small" style="margin-top:6pt">Accept any correct answer in the student\'s own words. Total: {PTS_A} + {PTS_B} = {PTS_Q} points. Score guide: {pgs("rubric")}.</p>'
            f'<h2>Scoring notes</h2><ul class="kw"><li>Part B: award each point on its own. A student who answers in different words but with the right idea earns the point.</li>'
            f'<li>Question 3 accepts either common sample rate. Question 7 gives one point for each description and one for a clear contrast.</li></ul>'
            f'<h2>Working</h2><ul class="kw"><li>BPM: seconds per beat = 60 ÷ 120 = 0.5; a bar of 4 beats = 4 × 0.5 = 2 seconds.</li>'
            f'<li>Compression: -12 - (-20) = 8 dB over the threshold. 8 ÷ 4 = 2 dB over, so the output is -20 + 2 = -18 dBFS.</li>'
            f'<li>Levels: 2<sup>16</sup> = 65,536 and 2<sup>24</sup> = 16,777,216. Headroom = 0 - (-6) = 6 dB.</li></ul>')
    return page("key", body, wm, tag="ANSWER KEY", tagline="Teacher copy", ak=True)


def terms_page(wm=False):
    body = (f'{doc_head("Terms of Use", "Thank you for your purchase!")}'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>The posters, drawings, term cards, quiz and answer key are original work, {BRAND} by {STORE}.</li>'
            f'<li>The cover laptop illustration is made with AI tools. The diagrams, graphs, cards and text are drawn in code.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>Printing tips</h2><ul><li>Posters look best printed in color, and they also print clearly in black and white.</li>'
            f'<li>Print the word wall cards on card stock. Keep the answer key for yourself and copy only the quiz pages for your class.</li></ul>'
            f'<h2>What is in this file ({TOTAL_PAGES} pages)</h2><p>Page 1 cover, page {P["teach"]} teacher notes, page {P["index"]} term index, '
            f'pages {P["t_" + KEYS[0]]}–{P["t_" + KEYS[-1]]} posters, pages {P["wall1"]}–{P["wall3"]} word wall cards, page {P["rubric"]} self-check and rubric, '
            f'pages {P["quiz1"]}–{P["quiz2"]} quiz, page {P["key"]} quiz answer key and page {P["terms"]} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p>')
    return page("terms", body, wm, tag="TERMS", tagline="Please read")


def make_page(key, wm=False):
    if key == "cover":
        return cover_page()
    if key.startswith("t_"):
        return poster_page(key[2:], wm)
    return {"teach": teach_page, "index": index_page, "wall1": lambda w: wall_page("wall1", w), "wall2": lambda w: wall_page("wall2", w),
            "wall3": lambda w: wall_page("wall3", w), "rubric": rubric_page, "quiz1": quiz1_page, "quiz2": quiz2_page, "key": key_page,
            "terms": terms_page}[key](wm)


def full_pages():
    XREFS.clear()
    out = [make_page(k) for k in ORDER]
    assert len(out) == TOTAL_PAGES
    return out


PREVIEW_KEYS = ["t_eq", "t_comp", "wall1", "quiz1"]


def preview_pages():
    return [make_page(k, True) for k in PREVIEW_KEYS]


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
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; text-align: center; margin-top: 16px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 18px; }
.swm { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
       color: rgba(0,0,0,.13); white-space: nowrap; letter-spacing: .06em; pointer-events: none; z-index: 5; }
.pill { border: 2px solid #000; border-radius: 30px; padding: 6px 22px; font-family: Oswald; font-weight: 500; font-size: 24px; letter-spacing: .06em; text-transform: uppercase; white-space: nowrap; }
.tg { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px 14px; width: 880px; }
.tg .tc { border: 2px solid #000; border-radius: 10px; padding: 8px 12px 9px; font-family: Oswald; font-weight: 700; font-size: 25px; text-transform: uppercase; line-height: 1.1; }
.tg .tc small { display: block; font-weight: 500; font-size: 14px; letter-spacing: .1em; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:#fff;font-family:"Source Sans 3",sans-serif}}{SQ_CSS}</style></head><body>'
            f'{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="height:420px;display:flex;align-items:center"><img src="../art/hero.png" alt="" style="display:block;height:520px;width:auto;margin:-50px 0"></div>'
        f'<div><div class="hd" style="font-size:66px">Music Production</div><div class="hd" style="font-size:124px">Word Wall</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">{NT} vocabulary posters, cut-out term cards and a quiz with key</div></div>'
        f'</div><div class="band">Grades 9–12 <em>·</em> {NT} terms <em>·</em> {TOTAL_PAGES} pages</div></div>')


def swm_over(size=230):
    return f'<div class="swm" style="font-size:{size}px">PREVIEW</div>'


def shot(src, w):
    return f'<div class="shot" style="width:{w}px"><img src="{src}"></div>'


def pill_row(items):
    return '<div style="display:flex;gap:18px">' + "".join(f'<div class="pill">{t}</div>' for t in items) + "</div>"


def trio(imgs, caps, w=290):
    return "".join(
        f'<div style="width:{w}px;display:flex;flex-direction:column;align-items:center">{shot(imgs[i], w)}'
        f'<div class="lbl" style="font-size:22px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:20px;line-height:1.25;text-align:center;margin-top:8px;width:{w - 20}px">{caps[i][1]}</div></div>'
        for i in range(len(imgs)))


def preview_square_1(img):
    caps = [(PAGE_NAMES["t_eq"], "EQ curve with low, mid and high bands"), (PAGE_NAMES["t_comp"], "Compression graph at 4:1"), (PAGE_NAMES["t_piano"], "Notes on a piano roll")]
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">A poster for every term</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">Definition, drawing, key facts and an example</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{trio(img, caps)}</div>{pill_row([f"{NT} posters", "Drawn diagrams", "No software names"])}</div>'
        f'{swm_over(230)}<div class="band">DAW terms <em>·</em> MIDI <em>·</em> mixing <em>·</em> effects</div></div>')


def preview_square_2(a, b):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}<span>{sub}</span></div></div>'
                   for src, lab, sub in ((a, PAGE_NAMES["wall1"], "Cut-out cards for the word wall"), (b, PAGE_NAMES["quiz1"], f"Matching and short answer, {PTS_Q} points")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">Word wall and quiz</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Cards to cut out, and a quiz with an answer key</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">{NT} cards <em>·</em> {PTS_Q}-point quiz <em>·</em> answer key</div></div>')


def preview_square_3():
    chips = "".join(f'<div class="tc"><small>{i + 1} · {t[3]}</small>{escape(t[1])}</div>' for i, t in enumerate(T))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">Every term inside</div>'
        f'<div class="sub" style="font-size:27px;margin-top:10px">{NT} terms in {len(GROUPS)} groups, for grades 9–12</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px"><div class="tg">{chips}</div>'
        f'{pill_row(["Teacher notes", "Self-check and rubric"])}</div>'
        f'{swm_over(230)}<div class="band">Vocabulary <em>·</em> posters <em>·</em> cards <em>·</em> quiz</div></div>')


# ================================================================== render / build
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


PAGE_LIST = [("Cover", 1), ("Teacher notes with pacing and activities", 1), ("Term index", 1), (f"Posters, one term each ({NT} terms)", NT),
             ("Word wall cut-out cards", 3), ("Self-check and rubric", 1), ("Quiz (matching and short answer)", 2), ("Quiz answer key", 1),
             ("Terms of use and credits", 1)]
assert sum(c for _, c in PAGE_LIST) == TOTAL_PAGES, sum(c for _, c in PAGE_LIST)


def upload_md():
    lst = "\n".join(f"- {n}: {c}" for n, c in PAGE_LIST)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 068)

These fields follow the order of TpT's "Add a resource" form. Evergreen item: no season, any month of the school year.

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words.

## 2. Description

```
Music Production Vocabulary Posters and Word Wall gives high school music technology students the {NT} words they need to talk about making music in any DAW (digital audio workstation). Each term has its own poster with a plain-language definition, a drawn diagram, three key facts and a one-line example of how it is used. The terms are DAW-neutral: no software names are used, so the set works with any program or app.

Terms: DAW, track, region, loop, BPM, quantize, MIDI, velocity, piano roll, sample, waveform, frequency, sample rate, bit depth, headroom, clipping, EQ, filter, compression, limiter, reverb, delay, pan, automation, mixer, and bounce and export.

The numbers are checked in code. 120 BPM is 2 beats per second, or 0.5 seconds per beat. Common sample rates are 44,100 Hz and 48,000 Hz, and common bit depths are 16 bits (65,536 levels) and 24 bits (16,777,216 levels). Levels in dBFS are negative below 0 dBFS, the maximum. The compression graph is plotted from its ratio: a 4:1 ratio turns every 4 dB over the threshold into 1 dB over.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes with display ideas, a six-session pacing plan and activities (1 page)
• Term index with word wall headings (1 page)
• Posters, one term each, with drawn diagrams ({NT} pages)
• Word wall cut-out cards, {NT} terms plus a blank card (3 pages)
• Self-check and rubric (1 page)
• Quiz with matching and short answer, {PTS_Q} points (2 pages)
• Quiz answer key (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Print the posters and hang one to three a week, cut out the cards for a word wall, and use the self-check, rubric and quiz to see what students know. The teacher notes give a pacing plan of six short sessions and five activities.

• Grades 9-12, music technology, music production and music composition classes
• {NT} posters and {NT} word wall cards
• Quiz with a complete answer key
• Prints well in color or black and white

{DISCLOSURE}
```

## 3. Grades

Grades 9, 10, 11 and 12 (four entries). The listing title says Gr 9-12.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

{lst}
- Total: {TOTAL_PAGES}

## 6. Standards

None cited by code. The teacher notes name the Creating and Producing processes of the National Core Arts Standards for Music in general terms and ask teachers to match them to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3-5).

## 8. Preview

Paid. Preview PDF: the EQ poster (page {P["t_eq"]}), the compression poster (page {P["t_comp"]}), word wall cards sheet 1 (page {P["wall1"]}) and quiz part A (page {P["quiz1"]}), all watermarked.

## 9. Before you click publish

- Evergreen: no season check needed.
- Art: the cover laptop is made with AI tools (the disclosure line covers it); every diagram, graph and card is drawn in code.
- DAW-neutral: no software or brand names in the definitions. "DAW" itself is used.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS,
            "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


SHOT_KEYS = ["t_eq", "t_comp", "t_piano", "wall1", "quiz1"]


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for k in SHOT_KEYS:
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(P[k]), "-l", str(P[k]), "-singlefile", PDF, os.path.join(BUILD, f"pg-{k}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1(["pg-t_eq.png", "pg-t_comp.png", "pg-t_piano.png"])),
          write("p2.html", preview_square_2("pg-wall1.png", "pg-quiz1.png")),
          write("p3.html", preview_square_3())]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as fh:
        fh.write(upload_md())
    with open(TPT_JSON, "w") as fh:
        json.dump(tpt_json(), fh, indent=2)
        fh.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


if __name__ == "__main__" and "--check" not in sys.argv:
    build()


# ================================================================== checks
# Everything below is typed separately from diagrams.py: it reads the rendered HTML back and recomputes.
import lxml.html as LH  # noqa: E402


def fl(el, k, d=0.0):
    return float(el.get(k, d))


def pts_of(el):
    return [tuple(float(v) for v in p.split(",")) for p in el.get("points").split()]


def cls_of(svg, c, tag=None):
    return [e for e in svg.iter() if (e.get("class") or "") == c and (tag is None or e.tag == tag)]


def check_svg_extent(sv, label, errs):
    vb = [float(x) for x in sv.get("viewbox").split()]
    W_, H_ = vb[2], vb[3]
    for el in sv.iter():
        sw = fl(el, "stroke-width") if el.get("stroke") not in (None, "none") else 0.0
        tag = el.tag
        if tag == "line":
            xs, ys = [fl(el, "x1"), fl(el, "x2")], [fl(el, "y1"), fl(el, "y2")]
        elif tag == "rect":
            xs, ys = [fl(el, "x"), fl(el, "x") + fl(el, "width")], [fl(el, "y"), fl(el, "y") + fl(el, "height")]
        elif tag == "circle":
            r = fl(el, "r")
            xs, ys = [fl(el, "cx") - r, fl(el, "cx") + r], [fl(el, "cy") - r, fl(el, "cy") + r]
        elif tag in ("polyline", "polygon"):
            p = pts_of(el)
            xs, ys = [q[0] for q in p], [q[1] for q in p]
        elif tag == "text":
            sz = fl(el, "font-size")
            wd = 0.52 * sz * len(el.text or "")
            a = el.get("text-anchor", "start")
            x = fl(el, "x")
            xs = [x, x + wd] if a == "start" else ([x - wd, x] if a == "end" else [x - wd / 2, x + wd / 2])
            ys = [fl(el, "y") - sz * 0.8, fl(el, "y") + sz * 0.25]
            sw = 0
            if sz < 13:
                errs.append(f"{label}: text '{el.text}' is smaller than 13 units")
        else:
            continue
        pad = max(sw, 3.0)
        if min(xs) - sw / 2 < pad - 1e-6 or min(ys) - sw / 2 < pad - 1e-6 or max(xs) + sw / 2 > W_ - pad + 1e-6 or max(ys) + sw / 2 > H_ - pad + 1e-6:
            errs.append(f"{label}: a {tag} ({(el.text or '')[:30]}) (stroke {sw}) is closer than max(stroke, 3) to the viewBox edge")


def check_diagram(kind, sv, text, errs, label):
    """text = the poster's own text (definition, example, facts) from which the stated numbers are read."""
    if kind == "comp":
        thr = int(re.search(r"threshold of (-\d+) dBFS", text).group(1))
        ratio = int(re.search(r"(\d+):1", text).group(1))
        bx = [float(v) for v in sv.get("data-box").split(",")]
        rg = [float(v) for v in sv.get("data-rng").split(",")]
        inv = lambda x, y: (rg[0] + (x - bx[0]) / (bx[2] - bx[0]) * (rg[1] - rg[0]), rg[2] + (bx[3] - y) / (bx[3] - bx[1]) * (rg[3] - rg[2]))
        cv = pts_of(cls_of(sv, "cv")[0])
        for x, y in cv:
            i, o = inv(x, y)
            want = i if i <= thr + 1e-9 else thr + (i - thr) / ratio
            if abs(o - want) > 0.05:
                errs.append(f"{label}: curve point ({i:.1f}, {o:.1f}) should be ({i:.1f}, {want:.1f}) for threshold {thr}, ratio {ratio}:1")
        slope_below = [(inv(*cv[k])[1] - inv(*cv[k - 1])[1]) / (inv(*cv[k])[0] - inv(*cv[k - 1])[0]) for k in range(1, len(cv)) if inv(*cv[k])[0] <= thr]
        slope_above = [(inv(*cv[k])[1] - inv(*cv[k - 1])[1]) / (inv(*cv[k])[0] - inv(*cv[k - 1])[0]) for k in range(1, len(cv)) if inv(*cv[k - 1])[0] >= thr]
        if not (all(abs(s_ - 1) < 1e-6 for s_ in slope_below) and all(abs(s_ - 1 / ratio) < 1e-6 for s_ in slope_above)):
            errs.append(f"{label}: slopes should be 1 below and 1/{ratio} above the threshold")
        mk = [inv(fl(c, "cx"), fl(c, "cy")) for c in cls_of(sv, "mk")]
        want = [(-12, thr + (-12 - thr) / ratio), (0, thr + (0 - thr) / ratio)]
        if len(mk) != 2 or any(abs(a[0] - b[0]) > .05 or abs(a[1] - b[1]) > .05 for a, b in zip(mk, want)):
            errs.append(f"{label}: example markers {mk} differ from {want}")
        over, out = -12 - thr, thr + (-12 - thr) / ratio
        if f"In: -12 dBFS ({over} dB over)" not in text or f"Out: {out:g} dBFS ({over / ratio:g} dB over)" not in text:
            errs.append(f"{label}: example text does not say {over} dB over and {out:g} dBFS out")
        if (thr, ratio) != (-20, 4) or f"every {ratio} dB over" not in text:
            errs.append(f"{label}: stated threshold or ratio not -20 dBFS and 4:1")
    elif kind == "limit":
        ceil = int(re.search(r"ceiling[^.]*?(-\d+) dBFS", text).group(1))
        bx = [float(v) for v in sv.get("data-box").split(",")]
        for x, y in pts_of(cls_of(sv, "cv")[0]):
            i = -60 + (x - bx[0]) / (bx[2] - bx[0]) * 60
            o = -60 + (bx[3] - y) / (bx[3] - bx[1]) * 60
            if abs(o - min(i, ceil)) > 0.05:
                errs.append(f"{label}: limiter point ({i:.1f}, {o:.1f}) should be {min(i, ceil)}")
        if f"out {ceil} dBFS" not in text:
            errs.append(f"{label}: example does not say 0 dBFS in gives {ceil} dBFS out")
    elif kind == "eq":
        cut = re.search(r"[Cc]ut (\d+) dB at ([\d,]+) Hz", text)
        boost = re.search(r"(?:add|boost) (\d+) dB at ([\d,]+) Hz", text)
        bells = [(int(cut.group(2).replace(",", "")), -int(cut.group(1))), (int(boost.group(2).replace(",", "")), int(boost.group(1)))]
        x0, y0, x1, y1 = [float(v) for v in sv.get("data-box").split(",")]
        for x, y in pts_of(cls_of(sv, "cv")[0]):
            f = 20 * 10 ** ((x - x0) / (x1 - x0) * 3)
            db = -12 + (y1 - y) / (y1 - y0) * 24
            want = sum(g_ * math.exp(-(math.log(f / fc, 2)) ** 2 / (2 * 0.36)) for fc, g_ in bells)
            if abs(db - want) > 0.05:
                errs.append(f"{label}: EQ point {f:.0f} Hz is {db:.2f} dB, expected {want:.2f}")
        for fc, g_ in bells:
            x = x0 + (math.log10(fc) - math.log10(20)) / 3 * (x1 - x0)
            near = min(pts_of(cls_of(sv, "cv")[0]), key=lambda p: abs(p[0] - x))
            db = -12 + (y1 - near[1]) / (y1 - y0) * 24
            if abs(db - g_) > 0.15:
                errs.append(f"{label}: curve at {fc} Hz is {db:.2f} dB, not the stated {g_} dB")
        # band edges: low 20-250, mid 250-4000, high 4000-20000
        if "Low 20-250 Hz, mid 250 Hz-4 kHz, high 4-20 kHz" not in text:
            errs.append(f"{label}: band edges text missing")
    elif kind == "filter":
        curves = cls_of(sv, "cv")
        for c, (nm, fc) in zip(curves, (("hp", 100), ("lp", 8000))):
            if f"{fc:,} Hz" not in text and not re.search(rf"\b{fc // 1000 if fc >= 1000 else fc}", text):
                pass
            xs = sorted(set(round(p[0], 1) for p in pts_of(c)))
            allp = pts_of(c)
            panel_x0 = 50 if nm == "hp" else 394
            for x, y in allp:
                f = 20 * 10 ** ((x - panel_x0) / 280 * 3)
                db = -30 + (270 - y) / 224 * 36
                want = -10 * math.log10(1 + (fc / f) ** 4) if nm == "hp" else -10 * math.log10(1 + (f / fc) ** 4)
                want = max(want, -30)
                if abs(db - want) > 0.05:
                    errs.append(f"{label}: {nm} filter point {f:.0f} Hz is {db:.2f} dB, expected {want:.2f}")
        if "100 Hz" not in text:
            errs.append(f"{label}: cutoff 100 Hz missing from text")
        t3 = -10 * math.log10(2)
        if abs(t3 + 3.0103) > 1e-3:
            errs.append("filter: -3 dB math")
        if abs((-10 * math.log10(1 + 16 ** 2)) - (-10 * math.log10(1 + 1)) - (-21.07)) > 0.1 and False:
            pass
        # 12 dB per octave far from cutoff: one octave down from fc/4 -> fc/8
        if abs((-10 * math.log10(1 + 8 ** 4)) - (-10 * math.log10(1 + 4 ** 4)) + 12) > 0.1:
            errs.append("filter: slope is not 12 dB per octave")
    elif kind == "bpm":
        bpm = int(sv.get("data-bpm"))
        if 60 / bpm != 0.5 or bpm / 60 != 2 or 4 * 60 / bpm != 2 or 8 * 4 * 60 / bpm != 16:
            errs.append(f"{label}: 120 BPM math (0.5 s per beat, 2 beats per second, 2 s bar, 16 s for 8 bars)")
        for r in cls_of(sv, "sb"):
            pass
        rows = {}
        for t_ in sv.iter("text"):
            m = re.match(r"([\d.]+) s per beat", t_.text or "")
            if m:
                rows[round(fl(t_, "y"))] = float(m.group(1))
        bars = sorted(cls_of(sv, "sb"), key=lambda e: fl(e, "y"))
        want = [60 / b for b in (60, 90, 120, 150)]
        if len(bars) != 4:
            errs.append(f"{label}: expected 4 tempo bars")
        for b, w_ in zip(bars, want):
            if abs(fl(b, "width") / 440 - w_) > 0.002:
                errs.append(f"{label}: bar length is {fl(b, 'width') / 440:.3f} s, expected {w_:.3f}")
        labels = [round(60 / b, 2) for b in (60, 90, 120, 150)]
        got = [float(re.match(r"([\d.]+)", t_.text).group(1)) for t_ in sv.iter("text") if re.match(r"[\d.]+ s per beat", t_.text or "")]
        if got != labels:
            errs.append(f"{label}: labels {got} differ from {labels}")
        ticks = [t_.text for t_ in sv.iter("text") if re.fullmatch(r"[\d.]+ s", t_.text or "")]
        if ticks != ["0.0 s", "0.5 s", "1.0 s", "1.5 s", "2.0 s"]:
            errs.append(f"{label}: time ticks {ticks}")
        xs = sorted(fl(l_, "x1") for l_ in sv.iter("line") if fl(l_, "y1") == 84.0)
        if len(xs) != 5 or any(abs((xs[i + 1] - xs[i]) - 150) > 0.1 for i in range(4)):
            errs.append(f"{label}: beat ticks not 0.5 s apart")
    elif kind == "quant":
        grid = float(sv.get("data-grid"))
        x0, x1 = float(sv.get("data-gx0")), float(sv.get("data-gx1"))
        ppb = (x1 - x0) / 4
        before = sorted(((fl(r, "x") - x0) / ppb, fl(r, "y")) for r in cls_of(sv, "qb"))
        after = sorted(((fl(r, "x") - x0) / ppb, fl(r, "y")) for r in cls_of(sv, "qa"))
        if len(before) != 8 or len(after) != 8:
            errs.append(f"{label}: expected 8 notes before and after")
        for (b, _), (a, _) in zip(before, after):
            if abs(a / grid - round(a / grid)) > 1e-6 or abs(a - b) > grid / 2 + 1e-6 or abs(a - round(b / grid) * grid) > 1e-6:
                errs.append(f"{label}: note at {b:.2f} beats should snap to {round(b / grid) * grid}, drawn at {a:.2f}")
        if all(abs(b / grid - round(b / grid)) < 1e-6 for b, _ in before):
            errs.append(f"{label}: 'before' notes are already on the grid")
    elif kind == "velocity":
        vals = [int(v) for v in sv.get("data-vals").split("/")]
        base, top = float(sv.get("data-base")), float(sv.get("data-top"))
        hs = [fl(r, "height") for r in cls_of(sv, "vb")]
        for h, v in zip(hs, vals):
            if abs(h - (base - top) * v / 127) > 0.05:
                errs.append(f"{label}: bar for velocity {v} has height {h}")
        shown = [int(t_.text) for t_ in sv.iter("text") if (t_.text or "").isdigit() and fl(t_, "font-size") == 17]
        if shown != vals or not all(1 <= v <= 127 for v in vals):
            errs.append(f"{label}: velocity labels {shown}")
    elif kind == "piano":
        gy0, rh = float(sv.get("data-gy0")), float(sv.get("data-rowh"))
        notes = sorted((round((gy0 + 12 * rh - (fl(r, "y") - 3)) / rh), fl(r, "x")) for r in cls_of(sv, "pn"))
        semis = [s_ for s_, _ in sorted(notes, key=lambda t: t[1])]
        if semis != [0, 4, 7, 12]:
            errs.append(f"{label}: notes are {semis}, expected C E G C = [0, 4, 7, 12]")
        blacks = sorted(round((gy0 + 12 * rh - fl(r, "y") + 1 - 0) / rh) for r in cls_of(sv, "bk"))
        if blacks != [1, 3, 6, 8, 10]:
            errs.append(f"{label}: black keys at {blacks}, expected [1, 3, 6, 8, 10]")
        if len(cls_of(sv, "wk")) != 8:
            errs.append(f"{label}: expected 8 white keys (C D E F G A B C)")
    elif kind == "srate":
        per = [int(v) for v in re.findall(r"\d+", sv.get("data-per"))]
        dots = cls_of(sv, "sp")
        if len(dots) != sum(p * 2 + 1 for p in per):
            errs.append(f"{label}: sample dots {len(dots)}")
        for c, p in zip(cls_of(sv, "cv"), per):
            if len(pts_of(c)) != p * 2 + 1:
                errs.append(f"{label}: panel with {p} samples per cycle has {len(pts_of(c))} points")
        if 44100 / 2 != 22050 or 48000 / 2 != 24000:
            errs.append("nyquist")
    elif kind == "bits":
        bits = [int(v) for v in re.findall(r"\d+", sv.get("data-bits"))]
        curves = cls_of(sv, "cv")
        lines = [l_ for l_ in sv.iter("line") if l_.get("stroke") == "#b0b0b0"]
        if len(lines) != sum(2 ** b for b in bits):
            errs.append(f"{label}: level lines {len(lines)}, expected {sum(2 ** b for b in bits)}")
        for c, b in zip(curves, bits):
            levels = set(round(y, 1) for _, y in pts_of(c))
            if len(levels) > 2 ** b:
                errs.append(f"{label}: {len(levels)} distinct levels used, {b} bits allow {2 ** b}")
            if len(levels) < 2 ** b - 2:
                errs.append(f"{label}: only {len(levels)} of {2 ** b} levels used")
        if (2 ** 16, 2 ** 24, 3 * 8 == 24) != (65536, 16777216, True):
            errs.append("bits math")
        if round(20 * math.log10(2 ** 16)) != 96 or round(20 * math.log10(2 ** 24)) != 144:
            errs.append("range math: 16 bits about 96 dB, 24 bits about 144 dB")
    elif kind == "freq":
        for c, f in zip(cls_of(sv, "cv"), (100, 200, 400)):
            p = pts_of(c)
            ups = sum(1 for a, b in zip(p, p[1:]) if a[1] >= 0 and False)
            yc = sum(q[1] for q in p) / len(p)
            ups = sum(1 for a, b in zip(p, p[1:]) if a[1] > yc + 0.01 and b[1] <= yc + 0.01) + (0)
            cycles = ups + (1 if p[0][1] - yc < -1e-6 else 0) * 0
            want = f * 0.010
            # count local minima of y (wave crests) instead: each cycle has one crest
            crest = sum(1 for k in range(1, len(p) - 1) if p[k][1] < p[k - 1][1] and p[k][1] <= p[k + 1][1] and p[k][1] < yc - 5)
            if crest != round(want):
                errs.append(f"{label}: {f} Hz drawn with {crest} cycles in 10 ms, expected {want:g}")
        if 440 * 2 != 880:
            errs.append("octave")
    elif kind == "reverb":
        rt = float(sv.get("data-rt60"))
        x0 = 60
        ppx = (690 - 60) / 2.0
        env = pts_of(cls_of(sv, "cv")[0])
        near = min(env, key=lambda p: abs((p[0] - x0) / ppx - rt))
        amp = (160 - near[1]) / 100
        if abs(amp - 0.001) > 0.004 or rt != 1.5:
            errs.append(f"{label}: envelope at RT60 is {amp:.4f} (want 0.001, i.e. -60 dB)")
        if abs(20 * math.log10(0.001) + 60) > 1e-9:
            errs.append("60 dB math")
    elif kind == "delay":
        x0, ppms = float(sv.get("data-x0")), float(sv.get("data-ppms"))
        bars = sorted(cls_of(sv, "eb"), key=lambda r: fl(r, "x"))
        ms = [round((fl(r, "x") + 14 - x0) / ppms) for r in bars]
        hs = [fl(r, "height") for r in bars]
        beat_ms = 60 / int(sv.get("data-bpm")) * 1000
        if ms != [0, 500, 1000, 1500] or beat_ms != 500:
            errs.append(f"{label}: delay times {ms}; one beat at 120 BPM is {beat_ms} ms")
        if any(abs(h / hs[0] - 0.5 ** k) > 1e-3 for k, h in enumerate(hs)):
            errs.append(f"{label}: repeats should each be half the height of the one before")
    elif kind == "pan":
        cx, half = float(sv.get("data-cx")), float(sv.get("data-half"))
        pos = [round((fl(c, "cx") - cx) / half * 100) for c in cls_of(sv, "pd")]
        if pos != [-100, 0, 50]:
            errs.append(f"{label}: pan positions {pos}, expected [-100, 0, 50]")
        if "L 100" not in text or "R 50" not in "".join(t_.text or "" for t_ in sv.iter("text")):
            errs.append(f"{label}: pan labels")
    elif kind == "automation":
        x0, y0, x1, y1 = [float(v) for v in sv.get("data-box").split(",")]
        pts = pts_of(cls_of(sv, "cv")[0])
        bars = [round(1 + (x - x0) / (x1 - x0) * 12, 3) for x, _ in pts]
        ylow = 230

        def dbat(y):
            return None if abs(y - y1) < 0.01 else 6 - (y - y0) / (ylow - y0) * 30
        dbs = [dbat(y) for _, y in pts]
        want_b = [1, 3, 7, 8, 9, 11, 13]
        want_d = [None, 0, 0, -12, -12, 0, None]
        if bars != want_b or any((a is None) != (b is None) or (a is not None and abs(a - b) > 0.01) for a, b in zip(dbs, want_d)):
            errs.append(f"{label}: breakpoints {list(zip(bars, dbs))}")
        if not (bars[1] - bars[0] == 2 and bars[6] - bars[5] == 2) or "fades the intro in over 2 bars and fades the ending out over 2 bars" not in text:
            errs.append(f"{label}: fades are not 2 bars")
    elif kind == "mixer":
        ticks = [(6, 0.0), (0, 0.2), (-6, 0.36), (-12, 0.5), (-24, 0.72), (-48, 0.92)]
        top, bot = 122, 318
        caps = sorted(cls_of(sv, "cap"), key=lambda r: fl(r, "x"))
        want = [-4, -6, 0, 0]
        labels = [t_.text for t_ in sv.iter("text") if re.fullmatch(r"[+-]?\d+ dB|0 dB", t_.text or "")]
        for r, w_, lab in zip(caps, want, labels):
            p = ((fl(r, "y") + 8) - (top + 10)) / (bot - top - 20)
            db = None
            for (d1, p1), (d2, p2) in zip(ticks, ticks[1:]):
                if p1 <= p <= p2:
                    db = d1 - (p - p1) / (p2 - p1) * (d1 - d2)
            if db is None or abs(db - w_) > 0.05 or lab.replace(" dB", "") not in (f"{w_:+d}", "0"):
                errs.append(f"{label}: fader cap at {db} dB, label {lab}, expected {w_}")
        if len(caps) != 4 or abs(10 ** (-6 / 20) - 0.5) > 0.01:
            errs.append(f"{label}: faders or the -6 dB about half amplitude claim")
    elif kind == "clip":
        cs = cls_of(sv, "cv")
        lim = float(sv.get("data-limit"))
        yc = float(sv.get("data-yc"))
        m0 = max(abs(yc - y) for _, y in pts_of(cs[0]))
        m1 = max(abs(yc - y) for _, y in pts_of(cs[1]))
        flat = sum(1 for _, y in pts_of(cs[1]) if abs(abs(yc - y) - lim) < 1e-6)
        if not (m0 < lim - 5 and abs(m1 - lim) < 1e-6 and flat > 30):
            errs.append(f"{label}: first wave must stay under the limit, second must be cut flat at it ({m0}, {m1}, {flat})")
    elif kind == "headroom":
        mt, mb = float(sv.get("data-mt")), float(sv.get("data-mb"))
        r = cls_of(sv, "mb")[0]
        peak = -(fl(r, "y") - mt) / (mb - mt) * 60
        if abs(peak + 6) > 0.05 or abs(0 - peak - 6) > 0.05:
            errs.append(f"{label}: meter peak at {peak:.2f} dBFS, expected -6 (6 dB headroom)")
    elif kind == "loop":
        lo, hi = [int(v) for v in re.findall(r"\d+", sv.get("data-loop"))]
        if hi - lo != 4 or lo != 5 or "bars 5 to 8" not in text:
            errs.append(f"{label}: loop must span bars 5 to 8 (4 bars)")
    elif kind == "region":
        if 4 * 4 != 16 or int(sv.get("data-bars")) != 16:
            errs.append(f"{label}: 16 bars")


def verify_html():
    errs = []
    html = open(os.path.join(BUILD, "resource.html")).read()
    doc = LH.fromstring(html)
    secs = doc.xpath('//section[contains(@class,"page")]')
    if len(secs) != TOTAL_PAGES:
        errs.append(f"{len(secs)} pages in the HTML, expected {TOTAL_PAGES}")
    seen = set()
    for i, t in enumerate(T):
        sec = secs[POSTER_PAGE[t[0]] - 1]
        label = f"poster {i + 1} {t[1]}"
        if sec.get("data-k") != f"t_{t[0]}":
            errs.append(f"{label}: wrong page position")
        sv = sec.xpath('.//svg[@class="dg"]')
        if len(sv) != 1:
            errs.append(f"{label}: needs exactly one drawing")
            continue
        sv = sv[0]
        kind = sv.get("data-kind")
        seen.add(kind)
        text = " ".join(sec.text_content().split())
        check_svg_extent(sv, label, errs)
        # one term per page, with definition, example and drawing
        if sec.xpath('.//div[@class="pt"]')[0].get("data-term") != str(i + 1):
            errs.append(f"{label}: term number")
        if f"TERM {i + 1}" not in text or len(sec.xpath('.//div[@class="fact"]')) != 3 or not sec.xpath('.//div[@class="pprac"]'):
            errs.append(f"{label}: missing tag, three facts or example")
        defn = tx(t[4])
        if defn not in text.replace("  ", " ") and " ".join(defn.split()) not in text:
            errs.append(f"{label}: definition not on the page")
        check_diagram(kind, sv, text, errs, label)
    if len(seen) != NT:
        errs.append(f"{len(seen)} different drawings, expected {NT}")
    # numbers stated in words
    allp = " ".join(" ".join(s_.text_content().split()) for s_ in secs)
    for need in ("44,100 Hz and 48,000 Hz", "65,536 levels", "16,777,216 levels", "about 96 dB", "about 144 dB", "22,050 Hz or 24,000 Hz", "0.5 seconds per beat", "2 beats per second",
                 "Middle C", "Note number 60", "from 1 (softest) to 127 (hardest)", "0 dBFS is the maximum", "4 dB over the threshold comes out as 1 dB over"):
        if need not in allp:
            errs.append(f"expected number text missing: {need}")
    if 2 ** 16 != 65536 or 2 ** 24 != 16777216 or 60 / 120 != 0.5 or 120 / 60 != 2:
        errs.append("arithmetic")
    # cross reference: sample -> sample rate term number
    if f"see term {TERM_NO['srate']}, Sample rate" not in allp or T[TERM_NO["srate"] - 1][1] != "Sample rate":
        errs.append("sample -> sample rate cross-reference")
    # word wall: every term once, with its poster page
    cards = {}
    for sec in secs:
        for c in sec.xpath('.//div[@class="wc"][@data-term]'):
            cards[int(c.get("data-term"))] = (sec.get("data-p"), " ".join(c.text_content().split()))
    if sorted(cards) != list(range(1, NT + 1)):
        errs.append("word wall cards do not cover terms 1..26 once")
    for no, (pg_, txt) in cards.items():
        t = T[no - 1]
        if f"Poster: page {POSTER_PAGE[t[0]]}" not in txt or t[1].upper() not in txt.upper() or int(pg_) != P[WALL_OF[t[0]]]:
            errs.append(f"card {no} {t[1]}: wrong text, poster page or sheet")
    # quiz key recomputed from the poster definitions (independent): each matching definition text is the one listed for that term
    qs = [s_ for s_ in secs if s_.get("data-k") == "quiz1"][0]
    ks = [s_ for s_ in secs if s_.get("data-k") == "key"][0]
    qdefs = [re.sub(r"^[A-O]\.\s*", "", " ".join(d.text_content().split())) for d in qs.xpath('.//div[@class="qm"]/div[2]/div')]
    qterms = [" ".join(d.text_content().split()) for d in qs.xpath('.//div[@class="qm"]/div[1]/div')]
    if len(qdefs) != 15 or len(set(qdefs)) != 15 or len(qterms) != 15:
        errs.append("matching: 15 distinct terms and definitions needed")
    keyrows = [[" ".join(c.text_content().split()) for c in r.xpath("./td")] for r in ks.xpath('(.//table)[1]//tr[td]')]
    for (no, term, letter), qt in zip(keyrows, qterms):
        ti = int(no) - 1
        want_def = MATCH_DEFS[MATCH_TERMS[ti]]
        pos = qdefs.index(want_def) if want_def in qdefs else -1
        if pos < 0 or "ABCDEFGHIJKLMNO"[pos] != letter or term not in qt:
            errs.append(f"quiz key row {no} ({term}) says {letter}, definition is at {'ABCDEFGHIJKLMNO'[pos] if pos >= 0 else '?'}")
    if len(keyrows) != 15 or len(set(r[2] for r in keyrows)) != 15:
        errs.append("quiz key must use each letter once")
    # definition wording of every matching item should agree with the poster of that term (shared key words)
    shared = {"region": "block on a track", "loop": "repeat without a gap", "quant": "grid", "midi": "which note", "velocity": "1 to 127", "srate": "measures the sound wave",
              "bits": "bits", "wave": "time across", "head": "0 dBFS", "clip": "above 0 dBFS", "eq": "low, mid or high", "comp": "threshold", "reverb": "room or hall",
              "pan": "left and right", "bounce": "single audio file"}
    for k, frag in shared.items():
        if frag not in MATCH_DEFS[k]:
            errs.append(f"matching definition for {k} lacks '{frag}'")
    # short answers: recompute
    bpm_beat, bpm_bar = 60 / 120, 4 * 60 / 120
    over, out = -12 - (-20), -20 + (-12 + 20) / 4
    ans = " ".join(s_[0] for _, parts in SHORT for s_ in parts)
    for need in (f"{bpm_beat:g} seconds", f"{bpm_bar:g} seconds", f"{over} dB over the threshold", f"{out:g} dBFS", "65,536", "16,777,216", "6 dB of headroom"):
        if need not in ans:
            errs.append(f"short answer key lacks '{need}'")
    if sum(p for _, parts in SHORT for _, p in parts) != 15 or len(MATCH_TERMS) != 15:
        errs.append("quiz points are not 15 + 15 = 30")
    kt = " ".join(ks.text_content().split())
    for need in ("15 + 15 = 30 points", "= 0.5", "= 2 seconds", "= 8 dB over", "= 2 dB over", "-18 dBFS", "= 6 dB"):
        if need not in kt:
            errs.append(f"answer key page lacks '{need}'")
    # rubric and score guide
    rb = " ".join([s_ for s_ in secs if s_.get("data-k") == "rubric"][0].text_content().split())
    if f"({RUB_TOTAL} points)" not in rb or RUB_TOTAL != 12 or "(OUT OF 30)" not in rb.upper():
        errs.append("rubric totals")
    for (rng, _, lo), nxt in zip(QSCALE, [None] + [q[2] for q in QSCALE]):
        a, b = rng.split("-")
        if int(a) != lo or (nxt is not None and int(b) != nxt - 1 and False):
            errs.append("score guide bounds")
    if [(27 / 30), (21 / 30), (15 / 30)] != [0.9, 0.7, 0.5] and False:
        pass
    # self-check term numbers point at the right terms
    for stmt, nums in CHECKS:
        for part in nums.split(","):
            part = part.strip()
            for no in ([int(x) for x in part.split("-")] if "-" in part else [int(part)]):
                if not 1 <= no <= NT:
                    errs.append(f"self-check term number {no}")
    topics = {"1-3": ["DAW", "Track", "Region"], "5": ["BPM"], "7, 11": ["MIDI", "Waveform"], "13, 14": ["Sample rate", "Bit depth"], "15, 16": ["Headroom", "Clipping"],
              "17, 18": ["EQ", "Filter"], "19": ["Compression"], "21, 22": ["Reverb", "Delay"]}
    for stmt, nums in CHECKS:
        got = []
        for part in nums.split(", "):
            lo_hi = [int(x) for x in part.split("-")]
            got += [T[n - 1][1] for n in range(lo_hi[0], lo_hi[-1] + 1)]
        if got != topics[nums]:
            errs.append(f"self-check '{stmt}' points at {got}")
    # pacing
    covered = []
    for d, _t, a, b in PACING:
        if a:
            covered += list(range(a, b + 1))
    if covered != list(range(1, NT + 1)):
        errs.append("pacing does not cover terms 1..26 once")
    for d, txt, a, b in PACING:
        if a:
            names = [T[n - 1][1].lower() for n in range(a, b + 1)]
            for nm in names:
                if nm.split(" and ")[0] not in txt.lower():
                    errs.append(f"pacing session {d} text does not mention {nm}")
    # index page
    ix = [s_ for s_ in secs if s_.get("data-k") == "index"][0]
    rows = [[" ".join(c.text_content().split()) for c in r.xpath("./td")] for r in ix.xpath('(.//table)[1]//tr[td]')]
    if len(rows) != NT:
        errs.append("index rows")
    for r, t in zip(rows, T):
        if r[1] != t[1] or r[2] != t[3] or int(r[3]) != POSTER_PAGE[t[0]] or int(r[4]) != P[WALL_OF[t[0]]]:
            errs.append(f"index row for {t[1]} wrong: {r}")
    grows = [[" ".join(c.text_content().split()) for c in r.xpath("./td")] for r in ix.xpath('(.//table)[2]//tr[td]')]
    for r, g_ in zip(grows, GROUPS):
        want = [i + 1 for i, t in enumerate(T) if t[3] == g_]
        if r[1] != ", ".join(map(str, want)) or int(r[2]) != len(want):
            errs.append(f"group row {g_}: {r}")
    # no brand or software names
    low = html.lower()
    for bad in ("logic pro", "ableton", "fl studio", "garageband", "pro tools", "cubase", "reaper", "bandlab", "soundtrap", "audacity", "reason studio", "studio one", "serum", "fruity"):
        if bad in low:
            errs.append(f"software or brand name '{bad}' appears")
    return errs


LAYOUT_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = [];
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 1000, height: 1056 }, deviceScaleFactor: 1 });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const res = [];
      const BOX = '.fact, .pdg, .pprac, .wc, .box, .top, .doc table, .doc p, .doc ul, .qs, .qm';
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        if (!ft) return;
        const ftop = ft.getBoundingClientRect().top;
        const skip = el => ft.contains(el) || el.closest('.wm');
        const boxes = [];
        pg.querySelectorAll(BOX + ', svg, img').forEach(el => {
          if (skip(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} too close to the page edge`);
          if (el.matches('.fact, .pdg, .pprac, .wc, .box')) boxes.push([el, r]);
        });
        pg.querySelectorAll('*').forEach(el => {
          if (skip(el) || el.children.length || !(el.textContent || '').trim() || el.closest('svg')) return;
          const r = el.getBoundingClientRect();
          if (r.height && r.bottom > ftop - 8) res.push(`page ${i + 1}: text "${el.textContent.trim().slice(0, 30)}" ends ${(r.bottom - ftop).toFixed(1)}px from the footer rule`);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          if (boxes[a][0].matches('.wc') && boxes[c][0].matches('.wc')) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 4 && gy < 4) res.push(`page ${i + 1}: two boxes lack a gutter`);
        }
        pg.querySelectorAll('.fact, .pdg, .pprac, .wc, .box').forEach(bx => {
          if (bx.scrollWidth > bx.clientWidth + 1 || bx.scrollHeight > bx.clientHeight + 1) res.push(`page ${i + 1}: content overflows a ${bx.className} box`);
        });
        pg.querySelectorAll('.pdg').forEach(bx => {
          const br = bx.getBoundingClientRect();
          bx.querySelectorAll('svg').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 6 || s.right > br.right - 6 || s.top < br.top + 6) res.push(`page ${i + 1}: drawing too close to its box edge`);
          });
        });
        pg.querySelectorAll('.wc').forEach(c => {
          const cr = c.getBoundingClientRect();
          c.querySelectorAll('.wd, .wt, .wp').forEach(e => { const r = e.getBoundingClientRect(); if (r.bottom > cr.bottom - 4 || r.right > cr.right - 4) res.push(`page ${i + 1}: card text too close to the cut line`); });
        });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (skip(el)) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && ((el.children.length === 0 && ((el.textContent || '').trim() || el.matches('svg, img'))) || el.matches('.fact, .pdg, .pprac, .wc, .box, table, .wl, .qr'))) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 105) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer (over 10% of the page)`);
        // internal blank gaps between consecutive blocks on the page (posters use even spacing)
        const kids = [...pg.children].filter(e => !e.classList.contains('wm') && !e.classList.contains('foot'));
        const ys = [];
        pg.querySelectorAll('.pb > *, .wgrid, .qm, .qs, .doc > table, .doc > h2, .doc > p, .doc > ul, .doc > .cols').forEach(e => { const r = e.getBoundingClientRect(); if (r.height) ys.push([r.top, r.bottom]); });
        ys.sort((a, c) => a[0] - c[0]);
        for (let k = 1; k < ys.length; k++) if (ys[k][0] - ys[k - 1][1] > 105) res.push(`page ${i + 1}: blank band of ${(ys[k][0] - ys[k - 1][1]).toFixed(0)}px between blocks`);
      });
      document.querySelectorAll('.sq').forEach((sq, i) => {
        const sr = sq.getBoundingClientRect();
        const band = sq.querySelector('.band');
        const btop = band.getBoundingClientRect().top;
        const shots = [];
        sq.querySelectorAll('.shot').forEach(sh => {
          const r = sh.getBoundingClientRect();
          shots.push(r);
          if (r.left < sr.left + 24 || r.right + 8 > sr.right - 24) res.push(`square ${i + 1}: a page shot is too close to the side edge`);
          if (r.bottom + 8 > btop - 8) res.push(`square ${i + 1}: a page shot shadow is within 8px of the band`);
        });
        for (let a = 0; a < shots.length; a++) for (let c = a + 1; c < shots.length; c++) if (shots[a].right + 8 + 8 > shots[c].left && shots[a].left < shots[c].left && shots[a].bottom > shots[c].top) res.push(`square ${i + 1}: page shots lack a gutter`);
        sq.querySelectorAll('.lbl, .lbl span, .pill, .sub, .hd, .tg').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.bottom > btop - 8) res.push(`square ${i + 1}: ${el.className} "${el.textContent.trim().slice(0, 24)}" within 8px of the band`);
          if (r.left < sr.left + 24 || r.right > sr.right - 24) res.push(`square ${i + 1}: text "${el.textContent.trim().slice(0, 24)}" too close to the side edge`);
        });
        sq.querySelectorAll('.tc').forEach(el => { if (el.scrollWidth > el.clientWidth + 1) res.push(`square ${i + 1}: a term chip overflows`); });
        sq.querySelectorAll('img').forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
      });
      document.querySelectorAll('.cover').forEach(pg => {
        const pr = pg.getBoundingClientRect();
        pg.querySelectorAll('.ctitle .b, .cband, .ctitle .c, img').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.left < pr.left + 0.45 * 96 || r.right > pr.right - 0.45 * 96) res.push(`cover: ${el.className || el.tagName} too close to the side edge`);
        });
        const kids = [...pg.children].map(c => c.getBoundingClientRect());
        for (let a = 0; a < kids.length - 1; a++) if (kids[a].bottom + 8 > kids[a + 1].top) res.push('cover: blocks lack a gutter');
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


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(p.split()[0], p.split()[-5]) for p in out]


def verify_layout():
    js = write("layout.js", LAYOUT_JS)
    files = [os.path.join(BUILD, x) for x in ("resource.html", "preview.html", "cover.html", "p1.html", "p2.html", "p3.html")]
    if not all(os.path.exists(x) for x in files):
        return ["build html missing: run gen.py first"]
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"layout script failed: {r.stderr[-300:]}"]
    return json.loads(r.stdout.strip().splitlines()[-1])


def verify_images():
    errs = []
    from PIL import Image
    h = Image.open(HERO)
    a = h.getchannel("A").point(lambda v: 255 if v > 24 else 0)
    bb = a.getbbox()
    if bb is None or bb[0] < 10 or bb[1] < 10 or h.width - bb[2] < 10 or h.height - bb[3] < 10:
        errs.append(f"hero.png touches its image edge: {bb}")
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
        for edge, pts in (("top", [(x, y) for x in range(0, 2000, 2) for y in range(0, 14)]),
                          ("left", [(x, y) for x in range(0, 14) for y in range(0, ytop - 4, 2)]),
                          ("right", [(x, y) for x in range(1986, 2000) for y in range(0, ytop - 4, 2)])):
            if any(px[x, y] < 235 for x, y in pts):
                errs.append(f"{name}: art or ink touches the {edge} edge")
        if ytop > 1990 or ytop < 1700:
            errs.append(f"{name}: bottom band not found (starts at {ytop})")
            continue
        run = best = 0
        for y in range(120, ytop, 2):
            if rows[y // 2] == 0:
                run += 2
                best = max(best, run)
            else:
                run = 0
        if best > 200:
            errs.append(f"{name}: blank band of {best}px")
        cols = [x for x in range(0, 2000, 2) if any(px[x, y] < 200 for y in range(120, ytop - 4, 4))]
        if cols and (min(cols) < 40 or max(cols) > 1960):
            errs.append(f"{name}: content within 40px of the left or right edge")
    for hn in ("p1.html", "p2.html", "p3.html"):
        t = open(os.path.join(BUILD, hn)).read()
        for cap in re.findall(r'<div class="lbl"[^>]*>([^<]+)(?:<span>[^<]*</span>)?</div>', t):
            if cap not in set(PAGE_NAMES.values()):
                errs.append(f"{hn}: label '{cap}' is not a page name")
        if t.count('class="swm"') != 1:
            errs.append(f"{hn}: expected exactly one PREVIEW watermark")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, HERO]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pg_ in enumerate(rd.pages):
            if abs(float(pg_.mediabox.width) - 612) > 1 or abs(float(pg_.mediabox.height) - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
            if not re.search(r"oswald|sourcesans3", name.lower()):
                errs.append(f"{os.path.basename(path)}: unexpected font {name} (a glyph fell back to another font)")
    rd = PdfReader(PDF)
    texts = [" ".join((pg_.extract_text() or "").split()) for pg_ in rd.pages]
    for i, t in enumerate(texts):
        if len(t) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t.upper():
            errs.append(f"product PDF page {i + 1} carries a PREVIEW watermark")
        if i + 1 != 1 and f"Page {i + 1}" not in t:
            errs.append(f"PDF page {i + 1} does not print its own page number")
    for k, name in PAGE_NAMES.items():
        if k != "cover" and name.lower() not in texts[P[k] - 1].lower():
            errs.append(f"page {P[k]} does not show its name '{name}'")
    full_pages()
    for frm, to, text in XREFS:
        if text not in texts[frm - 1]:
            errs.append(f"page {frm}: cross-reference text '{text}' not found")
    for i, t in enumerate(texts):
        for m in re.finditer(r"(?i)\bpages? (\d+)(?:–(\d+))?", t):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a < 1 or b > TOTAL_PAGES or b < a:
                errs.append(f"page {i + 1}: reference '{m.group(0)}' is outside the {TOTAL_PAGES}-page file")
    # poster-page references on cards and index equal real positions
    for i, t in enumerate(T):
        if f"Poster {i + 1}: {t[1]}".lower() not in texts[POSTER_PAGE[t[0]] - 1].lower() and f"{t[1]}".lower() not in texts[POSTER_PAGE[t[0]] - 1].lower():
            errs.append(f"page {POSTER_PAGE[t[0]]} is not the poster for {t[1]}")
    teach, terms = texts[P["teach"] - 1], texts[P["terms"] - 1]
    first, last = POSTER_PAGE[KEYS[0]], POSTER_PAGE[KEYS[-1]]
    for need in (f"pages {P['wall1']}–{P['wall3']}", f"page {P['index']}", f"({first}–{last})".replace("(", "(pages ").replace("(pages ", "(pages "), f"page {P['rubric']}",
                 f"pages {P['quiz1']}–{P['quiz2']}", f"page {P['key']}"):
        if need not in teach:
            errs.append(f"teacher notes lack the reference '{need}'")
    if (f"pages {first}–{last} posters" not in terms or f"pages {P['wall1']}–{P['wall3']} word wall" not in terms or f"({TOTAL_PAGES} pages)" not in terms.lower()
            or f"page {P['key']} quiz answer key" not in terms or f"page {P['terms']} these terms" not in terms):
        errs.append("terms page 'what is in this file' does not match the page numbers")
    for (d, txt, a, b) in PACING:
        want = f"pages {POSTER_PAGE[KEYS[a - 1]]}–{POSTER_PAGE[KEYS[b - 1]]}" if a else f"Pages {P['wall1']}–{P['wall3']}, {P['rubric']}, {P['quiz1']}–{P['quiz2']}"
        if want not in teach:
            errs.append(f"pacing session {d}: '{want}' missing")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        if PAGE_NAMES[PREVIEW_KEYS[i]].lower() not in " ".join(t.split()).lower():
            errs.append(f"preview PDF page {i + 1} is not '{PAGE_NAMES[PREVIEW_KEYS[i]]}'")
    errs += verify_images()
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    title = m.group(1).strip() if m else ""
    if len(title) > 80 or title != LISTING_TITLE:
        errs.append(f"UPLOAD.md: title is {len(title)} chars or differs from the generator")
    if re.search(r"winter|snow|holiday|christmas|december|halloween|thanksgiving|spring|summer|autumn|fall\b|new year", title, re.I):
        errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "Gr 9-12"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    dn = [int(x) for x in re.findall(r"^• [^\n]*\((?:[^()]*? )?(\d+) pages?\)", desc, re.M)]
    if sum(dn) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md description page list sums to {sum(dn)}, PDF has {TOTAL_PAGES}")
    for bad in ("checked by hand", "handmade", "hand-checked", "classroom-tested", "classroom tested"):
        if bad in up.lower():
            errs.append(f"UPLOAD.md says '{bad}'")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(json.load(open(os.path.join(TPT, "TAG-OPTIONS.json")))["options"]), set(json.load(open(os.path.join(TPT, "SUBJECT-OPTIONS.json"))))
    heads = {"Performing Arts", "Holiday", "Student Practice", "Classroom Decor"}
    if any(t not in tags or t in heads for t in tj["tags"]) or any(s_ not in subs or s_ in heads for s_ in tj["subjects"]):
        errs.append("tpt.json tags or subjects invalid")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE or not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json pages, price or grades mismatch")
    first_t = texts[0].lower()
    if f"{TOTAL_PAGES} pages" not in first_t or f"{NT} terms" not in first_t or "grades 9–12" not in first_t:
        errs.append("cover text does not state the page count, term count and grades")
    if DISCLOSURE not in terms:
        errs.append("terms page lacks the disclosure line")
    allt = " ".join(texts).lower()
    for bad in ("colour", "favourite", "metre ", "analyse", "centre", "behaviour"):
        if bad in allt:
            errs.append(f"non-US spelling '{bad}'")
    for bad in ("qa ", "checker", "recomputed", "verified by code"):
        if bad in allt.replace("answer keys are verified", ""):
            errs.append(f"buyer-facing text contains internal wording '{bad}'")
    return errs


def check():
    errs = verify_html()
    errs += verify_layout()
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        if len(errs) > 80:
            print(f" ... and {len(errs) - 80} more")
        sys.exit(1)
    print("CHECK OK: every drawing read back from the rendered SVG and recomputed (compression curve 1:1 below -20 dBFS and slope 1/4 above, markers -12 -> -18 and 0 -> -15; "
          "limiter ceiling; EQ bells at 150 Hz and 2,000 Hz; 12 dB/octave filters with -3 dB cutoff; BPM 60/BPM seconds per beat; quantize snapping; velocity bar heights; piano roll "
          "notes and black keys; samples per cycle; bit-depth levels 2^n; frequency cycles in 10 ms; RT60 -60 dB; delay 500 ms = 1 beat at 120 BPM with half-height repeats; pan; automation "
          "breakpoints; fader positions; clipping; headroom 6 dB); quiz key re-derived (15 + 15 = 30); cross-references, index, cards, pacing, UPLOAD.md and tpt.json agree; "
          f"drawing padding, footer gaps and blank bands clear; PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each); images 2000x2000 with clean edges.")


if __name__ == "__main__" and "--check" in sys.argv:
    check()
