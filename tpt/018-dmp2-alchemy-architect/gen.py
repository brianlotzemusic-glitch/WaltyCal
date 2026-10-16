#!/usr/bin/env python3
"""DMP2 project: Alchemy Architect (TpT 018): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Alchemy Architect > "Alchemy Architect - Project Sheet & Rubric" (rubric 5 categories scored 1-5, /25,
final grade = average of student and teacher scores), TEACHER NOTES > "Alchemy Architect - Teacher Notes" (7 class periods), and
the project's entry on "DMP2 - Project Menu" (the June 2026 menu with Type / Focus columns).

NO AUDIO IS INCLUDED. Students design three synthesizer patches in Logic's Alchemy and compose a 45-60 second track with them.
The worked example is three invented patches described on paper (Slow Tide, Sub Pulse, Glass Bell) and an invented 26-bar track plan;
every picture (waveforms, filter, envelope, LFO, track lanes) is drawn in code. No songs, artists, lyrics or chart data are named.
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "alchemy-architect"
TITLE = "Alchemy Architect"
ACCENT = "#3A5F7D"          # this product's single accent: steel blue (008 red, 009 orange, 010 violet, 011 teal, 012 blue, 013 green, 014 magenta, 015 gold, 016 olive, 017 sienna)
ACC_LIGHT = "#CBD9E4"
PRICE = "10.00"
CLASSES = 7
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-017).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "Alchemy Synth in Logic Pro | Sound Design Synthesis Project | High School Music"
DESC_START = "Synthesizer sound design for high school music technology:"
DESC_MUST = ["Alchemy Architect", "oscillator", "no audio", "three patches"]
ZIP_DIR = "Alchemy Architect - Hudson Beat"
ZIP_DATE = (2026, 10, 16, 12, 0, 0)
TYPE = "Structured Project"
PROJ_LINE = "Digital Music Production | <i>Structured Project</i> | 7 class periods"
DECK_STRAP = "Synth sound design in Logic Pro"
BANNED_EXTRA = []

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Structured", "Synthesis"
MENU_DESC = "Design original sounds from scratch using Logic’s Alchemy synthesizer. Oscillators, filters, modulation, and patches."
OVERVIEW = ("Design your own sounds from scratch. Using Logic’s Alchemy synthesizer, you’ll explore oscillators, filters, envelopes, and "
            "modulation to create at least 3 custom patches. Then use those sounds to compose a short original piece.")
GOALS = ["Learn the foundations of sound synthesis using Alchemy",
         "Design original patches using oscillators, filters, and modulation",
         "Apply effects and automation for expressivity",
         "Compose a short track featuring your custom sounds"]
VOCAB = [("Synthesizer", "An instrument that generates sound electronically using oscillators, filters, and modulation"),
         ("Oscillator", "The sound source in a synth — generates the raw waveform (sine, saw, square, etc.)"),
         ("Filter", "Shapes the tone of a sound by cutting or boosting certain frequencies"),
         ("Envelope (ADSR)", "Controls how a sound changes over time: Attack, Decay, Sustain, Release"),
         ("Modulation", "Using one signal (like an LFO) to control another parameter for movement and variation"),
         ("Patch", "A saved set of synth settings that creates a specific sound")]
REQS = ["Design at least 3 original patches in Alchemy",
        "Use oscillators, filters, and modulation in your sound design",
        "Compose a 45–60 second track featuring all of your custom sounds",
        "Apply effects and automation for expressivity",
        "Mix and bounce your track for presentation"]
STEPS = ["<b>Explore</b> — Open Alchemy and experiment with the interface, sound sources, and presets (Explore sheet: page @EXPLORE)",
         "<b>Learn the building blocks</b> — Understand oscillators, filters, envelopes, and modulation routing (Synth guide: page @SYNTHGUIDE)",
         "<b>Design Patch 1</b> — Create your first original sound from scratch. Save it. (Patch card: page @PATCH1)",
         "<b>Design Patches 2 &amp; 3</b> — Build two more distinct sounds. Aim for variety. (Patch cards: page @PATCH23)",
         "<b>Compose</b> — Use your 3 patches to build a 45–60 second track (Track plan: page @TRACKPLAN)",
         "<b>Mix and finalize</b> — Apply effects, automation, EQ, and panning. Bounce your track. (Mix check: page @MIXCHECK)",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["Start with a simple waveform and shape it. Don’t jump into the advanced features right away.",
        "Small changes in filter and envelope settings make a huge difference. Experiment with subtle tweaks.",
        "Save your patches as you go — it’s easy to lose a sound you liked if you keep tweaking.",
        "Listen to electronic music producers for inspiration on what’s possible with synthesis."]
FILE_NAME = "“Your Name – Alchemy Architect”"
CHECK = ["Bounced .mp3 or .wav uploaded to your class page",
         "Zipped .logicx project file uploaded to your class page",
         f"Files named correctly: {FILE_NAME}",
         "At least 3 custom Alchemy patches created and used",
         "Padlet post created with your 3 feedback questions",
         "Answered at least 2 questions on classmates’ Padlet posts during presentations"]
RUBRIC_NOTE = "Each category is scored 1–5. Your final grade is the average of your self-score and your teacher’s score."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Creativity & Originality", ["Minimal creative effort; relies on defaults or clichés", "Some creative ideas but largely predictable",
                                  "Shows originality; experiments with sound or style", "Highly creative; unique approach with clear artistic intent",
                                  "Exceptional creativity; innovative, bold, and expressive"]),
    ("Technical Skill / DAW Use", ["Limited understanding of Logic Pro tools", "Basic tool use with frequent errors",
                                   "Competent workflow; uses tools correctly", "Advanced use of Logic features and shortcuts",
                                   "Expert-level command of multiple Logic systems"]),
    ("Composition & Structure", ["Disorganized; no clear form or direction", "Some structure present but underdeveloped",
                                 "Clear, cohesive form with logical sections", "Engaging structure with dynamic progression",
                                 "Professional pacing, flow, and musical arc"]),
    ("Sound Design & Mix Quality", ["Poor sound choices; unbalanced or muddy mix", "Some variety but inconsistent levels and EQ",
                                    "Good sound selection; mostly balanced mix", "Strong sound palette; clean, well-balanced mix",
                                    "Exceptional sound design; professional-quality mix"]),
    ("Documentation & Presentation", ["Missing or incomplete; no reflection", "Minimal documentation with little insight",
                                      "Satisfactory; provides basic detail and reflection", "Well-documented; clear and thoughtful reflection",
                                      "Exceptional; thorough insight and polished delivery"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = [ds[4] for _, ds in RUBRIC]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine · / 25"
# ---- Teacher Notes
TN_REINFORCES = ("Introduces sound synthesis fundamentals. Students learn that every sound in electronic music was designed by someone, "
                 "and they can be that person.")
STRUGGLES = ["Alchemy is overwhelming at first. Start with the Simple view before opening Advanced.",
             "Students tweak endlessly without saving patches. Enforce a save-as-you-go habit.",
             "Custom patches sound thin compared to presets. Show them how layering and effects can thicken a patch.",
             "Students struggle to compose with unfamiliar sounds. Encourage them to design first, compose second."]
VAR_EASY = "Provide a guided walkthrough for building one patch together as a class. Reduce to 2 custom patches."
VAR_HARD = "Require 5 patches with at least 2 using advanced modulation routing. Extend track to 90 seconds."
RESOURCES = [("Alchemy — A Short Tutorial (YouTube)",
              "Not included and not linked: videos belong to their makers. Page @SYNTHGUIDE and the demo on slides 7–11 teach the same four "
              "building blocks; add your own tutorial link if you like."),
             ("A More User-Friendly Intro to Alchemy (YouTube)",
              "Not included, for the same reason. Page @LOGICREF is a plain-language tour of where each control lives, for Class 1."),
             ("Logic’s built-in Alchemy documentation",
              "Not included: it belongs to Apple. Open it from Logic’s Help menu; page @LOGICREF says what to look up.")]
TN_NOTE = ("Consider having students name their patches creatively and share them with the class as a sound library.")
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Technical Skill: ask the student to open one patch and point to the oscillator, the filter, an envelope and one modulation "
                "(an LFO, say), and say what each one does to the sound.",
                "Sound Design &amp; Mix Quality: play each of the three patches alone, then in the track. Are they clearly different from "
                "each other, and does each have a job (bass, pad, lead) in the mix?",
                "Composition &amp; Structure: does the piece change over its 45–60 seconds, with patches entering and leaving? The Track plan "
                "(page @TRACKPLAN) shows the intended shape.",
                "Documentation &amp; Presentation: the Explore sheet (page @EXPLORE), the Patch cards (pages @PATCH1–@PATCH23) and the Mix check "
                "(page @MIXCHECK) are the evidence. My rubric mentions reflection, so you may want to ask for a sentence or two."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Introduction to Alchemy. Guided exploration of the interface.",
     "do": "Slides 1–6: the hook, what a synthesizer is, the seven classes, steps 1 and 2, and start simple. Hand out the project sheet and "
           "the Explore sheet; students explore with headphones.", "slides": (1, 6),
     "pages": ["explore", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Who designed this sound? · four building blocks · explore Alchemy"},
    {"n": 2, "owner": "<b>Class 2:</b> Sound design basics — oscillators, filters, envelopes. Begin designing Patch 1.",
     "do": "Slides 7–11: oscillators, the filter, the envelope, modulation, then a live demo building Patch 1. Students begin their first "
           "Patch card.", "slides": (7, 11), "pages": ["synthguide", "patch1"],
     "deck": "Oscillator · filter · envelope · LFO · build Patch 1"},
    {"n": 3, "owner": "<b>Classes 3–5:</b> Design remaining patches and compose your track.",
     "do": "Slide 12: Patches 2 and 3. Aim for variety. Then work time.", "slides": (12, 12), "pages": ["patch23"],
     "deck": "Working day: Patches 2 and 3"},
    {"n": 4, "owner": None, "do": "Slide 13: design first, compose second; fill in the Track plan. Then work time.", "slides": (13, 13),
     "pages": ["trackplan"], "deck": "Working day: compose with your patches"},
    {"n": 5, "owner": None, "do": "Full working day: finish the track, layer and thicken. Ask each student to play you one patch alone "
                                   "and say its job in the track.", "slides": None, "pages": [], "deck": "Working day: compose and thicken"},
    {"n": 6, "owner": "<b>Class 6:</b> Final mix, bounce. Prepare presentations.",
     "do": "Slides 14–16: effects, mix and bounce, what you turn in, the rubric. Students self-score, bounce and post their three questions.",
     "slides": (14, 16), "pages": ["mixcheck", "rubric", "present"], "deck": "Mix · bounce · checklist · rubric · 3 questions"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 17–18: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (17, 18), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:8pt;gap:14pt"><div class="box acc-b"><span class="k">The one rule for Class 1</span>'
    '<p style="margin:0;font-size:10pt">From my common struggles: start with the Simple view before opening Advanced. Let students play '
    'and listen on Class 1; the Explore sheet (page @EXPLORE) keeps them moving without turning it into a lecture.</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:10pt">Working days. Slides 12 and 13 open Classes 3 '
    'and 4; Class 5 has no new slide. Circulate and ask: what is this patch for, and have you saved it?'
    '</p></div></div>')

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (checklist items 1 and 2).",
    "Page numbers are added to steps 1 to 6 (the Explore sheet, Synth guide, Patch cards, Track plan and Mix check).",
    "My three resources are not included; each is named as I wrote it, and the kit says what it offers instead (page @TN2). No tutorial "
    "video is included or linked.",
    "My pacing guide’s “Classes 3–5” row spans the Class 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 5 shortens steps 1 and 2, slide 11 shortens step 3, "
    "slide 12 shortens step 4, slide 13 shortens step 5, and slide 14 shortens step 6.",
]
CHANGES_MUST_MENTION = ["your class page", "Page numbers", "tutorial video", "Classes 3–5", "Layout only", "intro deck shortens"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the goals, the six vocabulary terms, the five "
        "requirements, steps (apart from the page numbers), tips, checklist and file name (“Your Name – Alchemy Architect”), the "
        "rubric (five categories scored 1–5, /25, the average of the student’s and the teacher’s score), what the project reinforces, "
        "the four common struggles, the variations, my day-by-day pacing and my closing note, and the project menu entry quoted on "
        "page @OVERVIEW. No requirement or rubric row is added.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: how to use the kit, the overview and setup "
                "pages, the teacher moves and slide numbers in the pacing guide, the grading suggestions, the Alchemy quick reference, "
                "the synth guide (waveforms, harmonics, filter, envelope and LFO numbers), the worked example (three invented patches "
                "and a 26-bar track plan on paper, not audio), the Explore sheet, Patch cards, Track plan and Mix check, the "
                "vocabulary page, the presentation planner and the intro deck. None of these adds a requirement or a rubric row.")

# ================================================================ the worked example (Hudson Beat original: invented patches on paper)
TEMPO = 120                     # beats per minute, 4/4
F0 = 110                        # A2, in Hz: the pad's note and the saw-wave example
CUT = 1000                      # the filter cutoff in the picture, in Hz
NHARM = 20                      # harmonics drawn
PATCHES = [  # name, job, source, filter, envelope (A s, D s, S %, R s), motion, effects
    ("Slow Tide", "Pad", "Two saw waves, the second tuned slightly sharp", f"Low-pass, cutoff {CUT} Hz, a little resonance",
     (1.0, 0.5, 80, 1.5), "LFO 0.5 Hz on the cutoff", "Reverb, chorus"),
    ("Sub Pulse", "Bass", "One square wave at 55 Hz (A1)", "Low-pass, cutoff 400 Hz", (0.005, 0.2, 70, 0.1), "None: steady", "None, kept clean"),
    ("Glass Bell", "Melody", "Two sine waves, the second one octave up", "Open: a sine has nothing above its pitch to cut",
     (0.01, 1.2, 0, 1.5), "None: the long decay is the movement", "Reverb, quarter-note delay"),
]
SECTIONS = [("Intro", 1, 4), ("Build", 5, 12), ("Lift", 13, 20), ("Outro", 21, 26)]     # bars, inclusive
LANES = [("Slow Tide", 1, 26), ("Sub Pulse", 5, 20), ("Glass Bell", 13, 24)]
TOTAL_BARS = 26


def beat_len(bpm=TEMPO):
    return 60 / bpm


def bar_len(bpm=TEMPO):
    return 4 * 60 / bpm


def bar_start(b, bpm=TEMPO):
    return (b - 1) * bar_len(bpm)


def mmss(t):
    t = float(t)
    return f"{int(t) // 60}:{int(round(t)) % 60:02d}"


def harmonics(kind, f0=F0, cut=None, n=NHARM):
    """Frequencies (Hz) of the harmonics of a waveform that sit at or below the cutoff."""
    ns = [k for k in range(1, n + 1) if kind in ("saw",) or (kind in ("square", "triangle") and k % 2 == 1) or (kind == "sine" and k == 1)]
    return [k * f0 for k in ns if cut is None or k * f0 <= cut]


def lfo_cycles_per_bar(hz, bpm=TEMPO):
    return hz * bar_len(bpm)


def minus(v):
    return str(v).replace("-", "−")


# ================================================================ drawings (original, code-drawn: black + accent only)
def wave_y(kind, t):
    """Value -1..1 of one cycle at phase t (0..1)."""
    if kind == "sine":
        return math.sin(2 * math.pi * t)
    if kind == "triangle":
        return 2 / math.pi * math.asin(math.sin(2 * math.pi * t))
    if kind == "saw":
        return 2 * ((t + .5) % 1) - 1
    return 1.0 if (t % 1) < .5 else -1.0


def waves_body(W=1600, name="waves", fs=30, cs=22, ph=190):
    gap = 24
    pw = (W - 3 * gap) / 4
    info = [("Sine", "sine", "one pure tone"), ("Triangle", "triangle", "odd harmonics, soft"),
            ("Saw", "saw", "all harmonics, bright"), ("Square", "square", "odd harmonics, hollow")]
    out = []
    top = fs + 14
    for i, (nm, kind, cap) in enumerate(info):
        x0 = i * (pw + gap)
        out.append(D.t_(x0 + pw / 2, fs, nm.upper(), fs, 700))
        D.lab(name + " heads", nm.upper(), fs, pw - 10)
        out.append(f'<rect x="{x0:.1f}" y="{top}" width="{pw:.1f}" height="{ph}" fill="#fff" stroke="#000" stroke-width="2"/>')
        mid, amp = top + ph / 2, ph * .36
        out.append(f'<line x1="{x0 + 8:.1f}" y1="{mid:.1f}" x2="{x0 + pw - 8:.1f}" y2="{mid:.1f}" stroke="#000" stroke-width="1.2" opacity=".35"/>')
        pts = []
        N = 400
        for k in range(N + 1):
            u = k / N
            pts.append(f"{x0 + 14 + (pw - 28) * u:.1f},{mid - amp * wave_y(kind, (2 * u) % 1 if u < 1 else 1.0 - 1e-9):.1f}")
        out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{ACCENT}" stroke-width="{max(4, cs / 4):.1f}" stroke-linejoin="round"/>')
        out.append(D.t_(x0 + pw / 2, top + ph + cs + 12, cap, cs, 500))
        D.lab(name + " caps", cap, cs, pw - 10)
    return "".join(out), W, top + ph + cs + 24


def filter_body(W=1600, name="filter"):
    gx, top, ph = 70, 70, 330
    fmax = 2300
    base = top + ph

    def X(f):
        return gx + (W - gx - 20) * f / fmax

    out = [f'<line x1="{gx}" y1="{base}" x2="{W - 20}" y2="{base}" stroke="#000" stroke-width="3"/>']
    for k in range(1, NHARM + 1):
        f = k * F0
        h = ph * .94 / k
        passed = f <= CUT
        out.append(f'<rect x="{X(f) - 16:.1f}" y="{base - h:.1f}" width="32" height="{h:.1f}" rx="3" fill="{"#000" if passed else "#b9b9b9"}"/>')
    pts = " ".join(f"{X(f):.1f},{base - ph * .94 / math.sqrt(1 + (f / CUT) ** 4):.1f}" for f in range(0, fmax + 1, 25))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{ACCENT}" stroke-width="6" stroke-linejoin="round"/>')
    out.append(f'<line x1="{X(CUT):.1f}" y1="{top - 10}" x2="{X(CUT):.1f}" y2="{base}" stroke="{ACCENT}" stroke-width="4" stroke-dasharray="10 8"/>')
    out.append(D.t_(X(CUT) + 12, top - 16, f"CUTOFF {CUT} Hz", 30, 700, anchor="start", fill_=ACCENT))
    D.lab(name + " cut", f"CUTOFF {CUT} Hz", 30, 400)
    for f in (0, 500, 1000, 1500, 2000):
        out.append(f'<line x1="{X(f):.1f}" y1="{base}" x2="{X(f):.1f}" y2="{base + 10}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(f) + (4 if f == 0 else 0), base + 36, f"{f} Hz", 22, 500, anchor="start" if f == 0 else "middle"))
    kept = f"harmonics 1–{len(harmonics('saw', cut=CUT))} are kept"
    out.append(D.t_(X(270), top + 150, kept.upper(), 24, 700, anchor="start"))
    D.lab(name + " kept", kept.upper(), 24, X(CUT) - X(270) - 20)
    cutl = "the rest are turned down".upper()
    out.append(D.t_(X(1080), top + 20, cutl, 24, 700, anchor="start"))
    D.lab(name + " cutl", cutl, 24, W - 20 - X(1080))
    cap = f"A saw wave at {F0} Hz: harmonic k sits at k × {F0} Hz, and its level is 1/k"
    out.append(D.t_(gx, base + 76, cap, 26, 500, anchor="start"))
    D.lab(name + " cap", cap, 26, W - gx - 20)
    return "".join(out), W, base + 90


def adsr_rows():
    """(title, A s, D s, S level 0..1, R s, key held s)."""
    return [("Pluck", 0.01, 0.30, 0.20, 0.20, 0.50), ("Pad", 1.0, 0.5, 0.80, 1.5, 3.0)]


def adsr_body(W=1600, name="adsr"):
    gx = 24
    rh, ph = 330, 190
    hs = .84
    out = []
    for r, (nm, a, d, s, rel, held) in enumerate(adsr_rows()):
        y0 = r * rh
        total = held + rel
        base = y0 + 56 + ph

        def X(t, total=total):
            return gx + (W - 2 * gx) * t / total

        title = f"{nm.upper()}   ·   {total:g} s from key down to silence"
        out.append(D.t_(gx, y0 + 34, title, 30, 700, anchor="start"))
        D.lab(name + " titles", title, 30, W - 2 * gx)
        pts = [(0, 0), (a, 1), (a + d, s), (held, s), (held + rel, 0)]
        poly = " ".join(f"{X(t):.1f},{base - v * ph * hs:.1f}" for t, v in pts)
        out.append(f'<polygon points="{X(0):.1f},{base} {poly}" fill="{ACC_LIGHT}" stroke="none"/>')
        out.append(f'<polyline points="{poly}" fill="none" stroke="{ACCENT}" stroke-width="7" stroke-linejoin="round"/>')
        out.append(f'<line x1="{gx}" y1="{base}" x2="{W - gx}" y2="{base}" stroke="#000" stroke-width="3"/>')
        out.append(f'<line x1="{X(held):.1f}" y1="{base - ph * hs - 8}" x2="{X(held):.1f}" y2="{base}" stroke="#000" stroke-width="2.4" stroke-dasharray="8 7"/>')
        out.append(D.t_(X(held) + 10, y0 + 78, "key up", 22, 500, anchor="start"))
        D.lab(name + " keyup", "key up", 22, 120)
        leg = f"A {a:g} s     D {d:g} s     S {round(s * 100)}%     R {rel:g} s     (key held {held:g} s)"
        out.append(D.t_(gx, base + 38, leg, 26, 500, anchor="start"))
        D.lab(name + " legend", leg, 26, W - 2 * gx)
        if nm == "Pad":
            for lt, t0, t1, dx, v in (("A", 0, a, -30, .5), ("D", a, a + d, 0, .9), ("S", a + d, held, 0, .8), ("R", held, held + rel, 30, .4)):
                dy = -14 if lt in "DS" else 0
                out.append(D.t_(X((t0 + t1) / 2) + dx, base - v * ph * hs + dy, lt, 34, 700))
    return "".join(out), W, 2 * rh - 40


def lfo_body(W=1500, name="lfo"):
    gx = 130
    x0, x1 = gx, W - 20
    span = 4.0                       # seconds shown: two bars at 120 BPM
    rows = [(0.5, "LFO 0.5 Hz: one slow sweep every bar"), (4.0, "LFO 4 Hz: eight fast wobbles every bar")]
    bh = 170
    out = []

    def X(t):
        return x0 + (x1 - x0) * t / span

    for r, (hz, title) in enumerate(rows):
        top = 56 + r * (bh + 96)
        out.append(D.t_(x0, top - 18, title, 30, 700, anchor="start"))
        D.lab(name + " titles", title, 30, x1 - x0)
        out.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{bh}" fill="#fff" stroke="#000" stroke-width="2"/>')
        mid, amp = top + bh / 2, bh * .36
        pts = " ".join(f"{X(k / 400 * span):.1f},{mid - amp * math.sin(2 * math.pi * hz * k / 400 * span):.1f}" for k in range(401))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{ACCENT}" stroke-width="6" stroke-linejoin="round"/>')
        out.append(D.t_(x0 - 14, top + 34, "high", 22, 500, anchor="end"))
        out.append(D.t_(x0 - 14, top + bh - 12, "low", 22, 500, anchor="end"))
        D.lab(name + " hl", "high", 22, gx - 20)
        for b in (0, 2, 4):
            out.append(f'<line x1="{X(b):.1f}" y1="{top}" x2="{X(b):.1f}" y2="{top + bh}" stroke="#000" stroke-width="2.4" stroke-dasharray="7 7"/>')
    last = 56 + (bh + 96) + bh
    for b, lbl in ((0, "bar 1 starts"), (2, "bar 2 starts"), (4, "bar 3")):
        anc = "start" if b == 0 else ("end" if b == 4 else "middle")
        out.append(D.t_(X(b) + (4 if b == 0 else (-4 if b == 4 else 0)), last + 36, lbl, 24, 500, anchor=anc))
    cap = "Tempo 120 BPM: a bar is 2 seconds, so 0.5 Hz is one cycle per bar"
    out.append(D.t_(x0, last + 78, cap, 26, 500, anchor="start"))
    D.lab(name + " cap", cap, 26, x1 - x0)
    return "".join(out), W, last + 92


def lanes_body(W=1600, name="lanes", fs=30, ts=22):
    gx = 260
    pwid = W - gx - 14
    bw = pwid / TOTAL_BARS

    def X(b):                        # left edge of bar b (b may be TOTAL_BARS + 1)
        return gx + (b - 1) * bw

    out = []
    sh = 70
    fills = ["#000", ACCENT, "#4a4a4a", "#000"]
    for (nm, a, b), fc in zip(SECTIONS, fills):
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b + 1) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{fc}"/>')
        out.append(D.t_((X(a) + X(b + 1)) / 2, sh / 2 + fs * .36 + 2, nm.upper(), fs, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs, X(b + 1) - X(a) - 24)
    lh, lg = 74, 14
    y = sh + 24
    for i, (nm, a, b) in enumerate(LANES):
        yy = y + i * (lh + lg)
        out.append(D.t_(gx - 16, yy + lh / 2 + fs * .36, nm.upper(), fs - 2, 700, anchor="end"))
        D.lab(name + " lanes", nm.upper(), fs - 2, gx - 30)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.4"/>')
        out.append(f'<rect x="{X(a) + 2:.1f}" y="{yy + 6}" width="{X(b + 1) - X(a) - 4:.1f}" height="{lh - 12}" rx="6" fill="{ACCENT if i == 0 else ("#000" if i == 1 else "#7a7a7a")}"/>')
    ty = y + len(LANES) * (lh + lg) + 6
    for b in (1, 5, 13, 21, TOTAL_BARS + 1):
        lbl = f"bar {b}  ·  {mmss(bar_start(b))}"
        anc = "start" if b == 1 else ("end" if b == TOTAL_BARS + 1 else "middle")
        out.append(f'<line x1="{X(b):.1f}" y1="{ty - 6}" x2="{X(b):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(b) + (2 if b == 1 else (-2 if b == TOTAL_BARS + 1 else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 220)
    return "".join(out), W, ty + ts + 22


def hero_body():
    return D.stack([waves_body(1100, "hero waves", 24, 17, 120)], 40)


DRAWINGS = {"hero": hero_body, "waves": lambda: waves_body(1600, "waves pic"), "filter": lambda: filter_body(1600, "filter pic"),
            "adsr": lambda: adsr_body(1600, "adsr pic"), "lfo": lambda: lfo_body(1500, "lfo pic"),
            "lanes": lambda: lanes_body(1600, "lanes pic")}
DRAWING_PX = {"hero": 1900, "waves": 2000, "filter": 2000, "adsr": 2000, "lfo": 2000, "lanes": 2000}
SIDE = {"waves": ["Each wave has its own sound", "Saw is bright, sine is pure", "Square sounds hollow", "Start with one and shape it"],
        "filter": ["The filter turns harmonics down", "Low cutoff means a darker sound", "Open the cutoff to brighten it", "Move it while you hold a note"],
        "adsr": ["Short attack, a pluck", "Long attack, a pad", "Release is the tail after you let go", "Sustain is a level, not a time"],
        "lfo": ["An LFO is a slow wave that moves a knob", "Rate sets how fast it moves", "Amount sets how far it moves", "Match the rate to the bar"],
        "lanes": ["Design first, compose second", "Give each patch a job", "Bring patches in and out", "Plan 45–60 seconds"]}


def label_extras():
    waves_body(1250, "page waves", 26, 19, 150)
    filter_body(1250, "page filter")
    lanes_body(1250, "page lanes", 26, 19)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Alchemy Architect", "Design the sound.",
     "Class 1, the first minute. No audio is included in this deck. Before class, choose a short passage of electronic music with a bold "
     "synth sound, and find it yourself on a service your school allows; refer to it by title and artist only. Open with my overview: "
     "using Logic's Alchemy synthesizer, students design at least three custom patches from scratch, then compose a short original piece "
     "with them."),
    (1, "listen", "Listen: who designed this sound?", "Every sound was designed · Someone built that sound, knob by knob|Teacher: play a "
     "short passage you choose, one with a bold synth sound.|What does the sound make you think of?|Is it smooth or rough, bright or dark?|"
     "Does it change while the note plays?",
     "Play your passage twice. Take answers aloud about the feeling and the texture, then ask whether the sound changes from the start of "
     "the note to the end. This sets up my teacher notes' big idea: every sound in electronic music was designed by someone, and "
     "students can be that person. Do not name a song on the slide; say its title and artist aloud if you like."),
    (1, "bullets", "Four building blocks", "Oscillator: makes the raw wave|Filter: cuts or boosts frequencies|Envelope: shapes the sound over "
     "time|Modulation: makes it move",
     "A plain-English tour using the vocabulary on the project sheet. A synthesizer generates sound electronically using oscillators, "
     "filters and modulation. The oscillator is the sound source and makes the raw waveform. The filter shapes the tone by cutting or "
     "boosting frequencies. The envelope, ADSR, controls how the sound changes over time. Modulation uses one signal, like an LFO, to "
     "control another parameter. A patch is a saved set of settings. Students add their own words on the vocabulary page."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: introduction to Alchemy and guided exploration of the interface. Class 2: "
     "sound design basics, oscillators, filters and envelopes, and begin designing Patch 1. Classes 3 to 5 are working days: design the "
     "remaining patches and compose your track. Class 6: final mix and bounce, and prepare presentations. Class 7: presentations with "
     "Padlet peer feedback. Hand out the project sheet now."),
    (1, "steps", "Steps 1 and 2: explore, learn", "Open Alchemy and try the interface|Play the sound sources and presets|Learn oscillators, "
     "filters, envelopes|Learn modulation routing|Fill in the Explore sheet",
     "Steps 1 and 2 of the project sheet, shortened to fit the slide. Students open Alchemy and experiment with the interface, sound "
     "sources and presets, then work on understanding oscillators, filters, envelopes and modulation routing. The Explore sheet gives "
     "them small tasks so Class 1 is play with a purpose. Headphones on."),
    (1, "bullets", "Start simple, save often", "Simple view before Advanced|Change one thing at a time|Save your patch as you go|Design "
     "first, compose second",
     "My common struggles, as a promise for the whole project. Alchemy is overwhelming at first, so start with the Simple view before "
     "opening Advanced. Students tweak endlessly without saving, so enforce a save-as-you-go habit; a numbered name such as Tide 1, "
     "Tide 2 works well. And students struggle to compose with unfamiliar sounds, so design first and compose second."),
    (2, "pic", "The oscillator: the raw sound", "waves",
     "Class 2. Four classic waveforms, drawn on paper; nothing here is audio. A sine is one pure tone. A triangle has only odd harmonics "
     "and sounds soft. A saw has every harmonic and sounds bright. A square has odd harmonics and sounds hollow. Play each in Alchemy "
     "for the class. My tip: start with a simple waveform and shape it."),
    (2, "pic", "The filter: shaping the tone", "filter",
     "A saw wave at 110 Hz has a harmonic at every multiple of 110, each one quieter: 110, 220, 330, and so on, at 1, 1/2, 1/3 of the "
     "level. A low-pass filter with its cutoff at 1000 Hz keeps the first nine and turns the rest down; the curve shows how it fades "
     "rather than stops. Lower the cutoff and the sound gets darker. Demo it live by moving the cutoff while holding a note."),
    (2, "pic", "The envelope: shape over time", "adsr",
     "ADSR is Attack, Decay, Sustain, Release. The pluck: attack 0.01 seconds, decay 0.3, sustain 20 percent, release 0.2. The pad: attack "
     "1 second, decay 0.5, sustain 80 percent, release 1.5. Sustain is a level, not a time; the other three are times. Ask: which one "
     "would you use for a bass, a bell, a pad? Then play with the envelope in Alchemy."),
    (2, "pic", "Modulation: make it move", "lfo",
     "An LFO is a low-frequency oscillator: a slow wave that moves another knob, here the filter cutoff. At 120 BPM a bar is 2 seconds, "
     "so an LFO at 0.5 Hz makes one sweep each bar and an LFO at 4 Hz makes eight wobbles each bar. Rate is how fast, amount is how far. "
     "My advanced variation asks for advanced modulation routing; this is the gentle start."),
    (2, "steps", "Watch me: build Patch 1", "Start with one simple waveform|Open the filter: move the cutoff|Shape it with the envelope|Add "
     "one slow LFO to the cutoff|Save it: give the patch a name",
     "Step 3 of the project sheet, shortened to fit the slide: create your first original sound from scratch, and save it. Build one "
     "patch live in about ten minutes using exactly these five moves, saving after each one. Then students begin their own Patch 1 on the "
     "Patch card. My easier variation is a guided walkthrough of one patch as a class; this demo can be that."),
    (3, "bullets", "Working day: Patches 2 and 3", "Build two more sounds from scratch|Make each one different: bass, pad, lead|Change one "
     "setting at a time|Save as you go",
     "Class 3 is the first working day. Step 4 of the project sheet, shortened here: build two more distinct sounds and aim for variety. "
     "A pad, a bass and a bell make a good set. Students fill in a Patch card for each. Circulate and ask each student to play you the "
     "patch alone and tell you its job."),
    (4, "pic", "Working day: compose", "lanes",
     "Class 4. Step 5 of the project sheet, shortened here: use your three patches to build a 45 to 60 second track. The picture is an "
     "invented 26-bar plan at 120 BPM, which is 52 seconds, with three patches coming in and out. Students fill in the Track plan first. "
     "My third struggle: custom patches can sound thin, so show layering and effects to thicken them. Class 5 is a full working day."),
    (6, "bullets", "Mix, effects and bounce", "Add effects, automation, EQ and panning|Balance the levels|Bounce a .mp3 or .wav|Zip the .logicx "
     "project|Write your 3 Padlet questions",
     "Class 6. Step 6 of the project sheet, shortened to fit the slide: apply effects, automation, EQ and panning, and bounce your track. "
     "Students use the Mix check. Zip the .logicx in Finder (Control-click, Compress). Students also write their three Padlet "
     "questions today."),
    (6, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Alchemy Architect|3 custom Alchemy "
     "patches made and used|Padlet post with your 3 questions|Answer 2 questions on classmates’ posts",
     "The submission checklist from the project sheet, in short form. Show where students upload (your class page) and where the Padlet "
     "board is. Remind students that three custom patches must be created and used, so the track should feature all of them."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play your track|Show us your 3 patches|Your Padlet post: 3 questions about your project|Answer at "
     "least 2 of each classmate’s 3",
     "Class 7, presentations with Padlet Q and A. Each student plays the track and shows or describes the three patches, then explains the "
     "creative choices. During classmates' presentations, every student answers at least 2 of their 3 questions on their Padlet post. "
     "My teacher notes suggest students name their patches creatively and share them as a class sound library."),
    (7, "closer", "One last thing…", "You started with a blank patch.|You shaped the tone.|You gave it motion.|Now the sound is yours.",
     "Close with what my teacher notes say this project introduces: sound synthesis fundamentals. Every sound in electronic music was "
     "designed by someone, and now they know how to be that person. Invite students to keep saving patches and building their own sound "
     "library."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("example", "Worked example", "three patches on paper"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 7, 8, 9, 13]
SHOTS3 = [("setup", "Setup"), ("synthguide", "Synth guide"), ("example", "Worked example"), ("proj1", "Project sheet"),
          ("proj2", "Steps"), ("patch1", "Patch card"), ("trackplan", "Track plan"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "changes", "logicref", "synthguide", "example",
        "explore", "patch1", "patch23", "trackplan", "mixcheck", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "terms"]
PREVIEW_PICKS = ["pacing", "example", "proj2", "rubric"]

COVER_A = "Design the sound"
COVER_C = "DMP2 · oscillators · filters · envelopes · modulation · intro slides"
PDF_COVER = dict(a=32, b=58, c=14, art=7.3)
SQ_COVER = dict(a=50, b=140, c=27, art=700)
SQ_B_LINES = ["Alchemy", "Architect"]
SQ_SUB = "7 class periods · synth patches · sound design · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Synth guide, worked example, patch cards, track plan, project sheet", 28)}
SQ_BANDS = {1: "Explore <em>·</em> learn <em>·</em> design <em>·</em> compose <em>·</em> present",
            2: "Hook <em>·</em> oscillator <em>·</em> filter <em>·</em> envelope <em>·</em> LFO",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, video, songs or presets are included. Students make every sound themselves in Logic’s Alchemy, so everything on "
             "their tracks is original. For the hook, you choose a passage of electronic music yourself and find it on a service your "
             "school allows.")
CREDITS = ["Worked example (three invented patches and a 26-bar track plan, described on paper), the waveform, filter, envelope, LFO and "
           "track-lane drawings and layouts: original work, Hudson Beat.",
           "No audio, video, lyrics, album art, screenshots, Alchemy presets or chart data are included. YouTube is named only as the owner’s "
           "resource list names it; it is not affiliated with or endorsing this resource. Padlet is named only as an example of a tool you "
           "may already use."]
LOGIC_INTRO = ("Where each Alchemy control lives, in one table. Demonstrate the building blocks (slides 7 to 11) and then let students "
               "work. Names are from current Logic Pro versions; check the labels on yours.")
LOGIC_REF = [("Add Alchemy", "Add a Software Instrument track, click the instrument slot on the channel strip and choose Alchemy. It opens "
              "in its own window, with presets on the left."),
             ("Simple first", "Alchemy opens with a simplified set of big controls. Explore with those first, as my notes say. Open the Advanced "
              "view only when you want to build a sound from the ground up."),
             ("A basic start", "Choose a plain, basic starting patch if your version lists one, or take a simple preset and strip it back. Then "
              "change one setting at a time."),
             ("Oscillator", "In Advanced, Source A is the sound source. A Virtual Analog source gives the classic waveforms: sine, triangle, "
              "saw and square. Play a held note and switch between them."),
             ("Filter", "Each source feeds a filter. Choose a low-pass type, hold a note and move the Cutoff. A little Resonance adds a peak "
              "at the cutoff."),
             ("Envelope (ADSR)", "The amplitude envelope sets how a note's volume changes: Attack, Decay, Sustain, Release. A short attack "
              "is a pluck; a long attack is a pad."),
             ("Modulation", "Assign an LFO or an envelope to a parameter such as the filter cutoff to make it move. Start with a slow rate and "
              "a small amount."),
             ("Layer sources", "Turn on a second source and tune it a little sharp, or an octave up, to thicken a thin patch."),
             ("Effects", "Alchemy has its own effects section (reverb, delay, chorus and more). Logic’s channel-strip effects work too."),
             ("Save your patch", "Use Save As in the plug-in window header, give the patch a numbered name, and save after every change you "
              "like."),
             ("Automation", "Press A to show automation, choose a parameter such as volume or a macro, and draw changes over time."),
             ("Bounce and zip", "File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and choose "
              "Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; .mp3 or .wav and zipped .logicx uploaded", "Padlet post created with my 3 questions",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my patches:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Alchemy is overwhelming: the Explore sheet (page @EXPLORE) and the Alchemy quick reference (page @LOGICREF) keep Class 1 small.</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Not saving: slide 6 and the Patch cards (pages @PATCH1–@PATCH23), which have a version log.</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Thin patches: layering and effects on the Patch card, and the worked example on page @EXAMPLE.</li>'
    '<li style="font-size:10.8pt;margin-bottom:0">Composing with unfamiliar sounds: slide 13 and the Track plan (page @TRACKPLAN) give each patch a job.</li></ul></div>')
TN1_SIZE = 15
PROJ_SIZE = 14.2
VOCAB_GAP = 5
LOGIC_SIZE = 10.8
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example", "How to use, overview, setup, pacing, teacher notes, what changed, Alchemy "
              "quick reference, synth guide, worked example"),
             ("Student pages", "explore", "present", "Explore sheet, Patch cards, Track plan, Mix check, project sheet (3 pages), rubric, "
              "vocabulary, feedback planner"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period sound design project for high school music technology. Each '
             f'student explores Logic’s Alchemy synthesizer, designs at least three original patches from oscillators, filters, envelopes and '
             f'modulation, and composes a 45–60 second track that features them. It is a structured project from my Digital Music Production 2 '
             f'course (focus: synthesis), and the projects in that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Check that Alchemy opens on every computer (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("explore")}–{D.IX("present")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Class 5 is a working day with no new slide. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}: two patches and a class walkthrough, or five patches and a 90-second track.</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Sound library:</b> my notes suggest students name their patches and share them as a class library.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn what '
             f'a synthesizer is made of, build three sounds of their own, and compose a short piece that proves them.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro and Alchemy are trademarks or products of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:14pt;line-height:1.55">At least three original Alchemy patches, designed from scratch, and one 45–60 '
             f'second track that features all of them, with effects and automation. They hand in a bounced .mp3 or .wav, the zipped '
             f'.logicx project and a Padlet post with three feedback questions, then play the track and talk through their sounds.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:14pt;line-height:1.55">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:12pt">Supports the National Core Arts Standards for Music (Music Technology, high school): refining original '
             f'work (MU:Cr3.1), presenting it (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:13pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.6pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: explore, basics and Patch 1, three working days, mix and bounce, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro with Alchemy: sources, filter, envelopes, LFOs, effects, automation, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a feedback board, and speakers if you can</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:12pt">Students should already '
             f'know how to open a project, add software instruments, and save, bounce and zip in Logic. The quick reference (page '
             f'{D.IX("logicref")}) shows where each Alchemy control lives.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Structured", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 13.2pt; line-height: 1.5; margin-bottom: 9pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student (a current version, which includes Alchemy), and <b>headphones</b>. '
             f'Speakers help for the final listen.</li>'
             f'<li><b>Logic’s sound library downloaded</b>, so Alchemy’s presets show up.</li>'
             f'<li><b>A place to submit</b> an .mp3 or .wav and a zipped .logicx project (your class page).</li>'
             f'<li><b>A feedback board</b> for the three questions (my sheets use Padlet).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("explore")}–{D.IX("present")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:13pt;margin-bottom:11pt") for c in [
                 "Open Alchemy on a student computer. Check that presets load and that the sound plays through headphones.",
                 "Decide how students will save patches: in the project, plus a numbered name for each version.",
                 "Choose a short passage of electronic music with a bold synth sound for slide 2, and find it yourself.",
                 "Print the student pages; set up the submission spot and the feedback board."]) +
             f'</div><div class="big sb">'
             f'{D.H2("Keeping Alchemy small", True)}'
             f'<p style="font-size:13pt">My notes say Alchemy is overwhelming at first. A plan that works:</p>'
             f'<ul style="font-size:13pt;line-height:1.42">'
             f'<li><b>Class 1.</b> Simple view only. Presets, the big knobs and the Explore sheet (page {D.IX("explore")}).</li>'
             f'<li><b>Class 2.</b> Open Advanced for one sound: a source, a filter, an envelope and one LFO, built together on slide 11.</li>'
             f'<li><b>Classes 3 to 5.</b> Students build Patches 2 and 3 their own way, then compose.</li></ul>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">A save-as-you-go routine</span><ul style="margin:0">'
             f'<li style="font-size:12.4pt">Name every patch the moment it makes a sound you like.</li>'
             f'<li style="font-size:12.4pt">Use a number for each version: Tide 1, Tide 2.</li>'
             f'<li style="font-size:12.4pt">Save again before trying anything new.</li>'
             f'<li style="font-size:12.4pt">Log each version on the Patch card (pages {D.IX("patch1")}–{D.IX("patch23")}).</li></ul></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Why thin, and what to do</span><p style="margin:0;font-size:12.4pt">A single oscillator '
             f'sounds thin next to a preset, which layers many. Turn on a second source, detune it a little or put it an octave up, add a '
             f'touch of chorus or reverb, and open the filter a bit. Page {D.IX("example")} shows how.</p></div>'
             f'</div></div>')
    return D.page("Setup and keeping Alchemy small", "SETUP", "Teacher", inner, n, key="setup")


def synthguide_page(n, wm=False):
    f0 = F0
    hrows = []
    for nm, kind, desc in (("Sine", "sine", "only the 1st"), ("Triangle", "triangle", "odd: 1st, 3rd, 5th…, each much quieter (1/k²)"),
                           ("Saw", "saw", "all of them, each 1/k as loud"), ("Square", "square", "odd: 1st, 3rd, 5th…, each 1/k as loud")):
        hrows.append(f"<tr><td><b>{nm}</b></td><td>{desc}</td></tr>")
    crow = "".join(f"<tr><td>{c} Hz</td><td>{len(harmonics('saw', cut=c))}</td><td>{len(harmonics('square', cut=c))}</td></tr>" for c in (500, 1000, 2000))
    env = [("Pluck", "0.01 s", "0.3 s", "20%", "0.2 s"), ("Pad", "1 s", "0.5 s", "80%", "1.5 s"), ("Bass", "0.005 s", "0.2 s", "70%", "0.1 s"),
           ("Bell", "0.01 s", "1.2 s", "0%", "1.5 s")]
    erows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>" for a, b, c, d, e in env)
    lrows = "".join(f"<tr><td>{hz:g} Hz</td><td>{1 / hz:g} s</td><td>{lfo_cycles_per_bar(hz):g}</td></tr>" for hz in (0.25, 0.5, 1, 2, 4))
    inner = (f'<p style="margin:0 0 3pt;font-size:11.2pt">My notes say to teach oscillators, filters and envelopes first. This page is the explanation to '
             f'project or print. The numbers are for a note at {f0} Hz (the A two octaves below middle A) and a tempo of {TEMPO} BPM.</p>'
             f'<div style="width:6.6in;margin:2pt auto 3pt">{D.body_svg(waves_body(1250, "page waves", 26, 19, 150))}</div>'
             f'<div class="cols" style="gap:14pt"><div>'
             f'{D.H2("Harmonics of each wave", True)}<table class="t" style="font-size:10.2pt">{"".join(hrows)}</table>'
             f'<p class="small" style="margin:3pt 0 0">Harmonic k of a note at {f0} Hz is k × {f0} Hz. An octave up doubles the frequency: 55, 110, 220, 440 Hz.</p>'
             f'{D.H2("Where to start with an envelope")}<table class="t" style="font-size:10.2pt"><tr><th>Sound</th><th>A</th><th>D</th><th>S</th><th>R</th></tr>{erows}</table></div>'
             f'<div>{D.H2("What a low-pass filter keeps", True)}<table class="t" style="font-size:10.2pt"><tr><th>Cutoff</th><th>Saw harmonics kept</th><th>Square harmonics kept</th></tr>{crow}</table>'
             f'<p class="small" style="margin:3pt 0 0">At {f0} Hz, counting harmonics at or below the cutoff. A real filter fades gradually, so the numbers are a guide.</p>'
             f'{D.H2("LFO speed and the bar")}<table class="t" style="font-size:10.2pt"><tr><th>Rate</th><th>One cycle</th><th>Cycles per bar</th></tr>{lrows}</table>'
             f'<p class="small" style="margin:3pt 0 0">At {TEMPO} BPM a bar is {bar_len():g} s, so cycles per bar = rate × {bar_len():g}. Rules of thumb, not laws.</p></div></div>'
             f'{D.H2("A low-pass filter at work")}<div style="width:6.4in;margin:1pt auto 0">{D.body_svg(filter_body(1250, "page filter"))}</div>')
    return D.page("Synth guide · the four building blocks", "SYNTH GUIDE", "Teacher + student", inner, n, key="synthguide")


def example_page(n, wm=False):
    rows = ""
    for nm, job, src, flt, (a, d, s, r), mot, fx in PATCHES:
        rows += (f"<tr><td><b>{nm}</b><br>{job}</td><td>{src}</td><td>{flt}</td><td>A {a:g} s · D {d:g} s · S {s}% · R {r:g} s</td>"
                 f"<td>{mot}</td><td>{fx}</td></tr>")
    secs = ", ".join(f"{nm} bars {a}–{b}" for nm, a, b in SECTIONS)
    inner = (f'<p style="margin:0 0 3pt">Three <b>invented patches and a 26-bar plan, described on paper</b>: no audio is included, so the numbers '
             f'are easy to check. Students’ sounds will differ.</p>'
             f'{D.H2("1 · Three patches, three jobs", True)}'
             f'<table class="t" style="font-size:10pt;line-height:1.3"><tr><th style="width:11%">Patch</th><th style="width:18%">Source</th><th style="width:18%">Filter</th>'
             f'<th style="width:19%">Envelope</th><th style="width:16%">Motion</th><th>Effects</th></tr>{rows}</table>'
             f'{D.H2("2 · The track plan: 26 bars at 120 BPM")}<div style="width:7.2in;margin:1pt auto 3pt">{D.body_svg(lanes_body(1250, "page lanes", 26, 19))}</div>'
             f'<p class="small" style="margin:0 0 3pt">{secs}. One bar is {bar_len():g} s, so 26 bars is {TOTAL_BARS * bar_len():g} s: inside my 45–60 second requirement.</p>'
             f'<div class="cols" style="gap:12pt"><div class="box"><span class="k">3 · Checking the numbers</span>'
             f'<p style="margin:0;font-size:11.6pt;line-height:1.45">Slow Tide plays a note at {F0} Hz. With the cutoff at {CUT} Hz, '
             f'{CUT} ÷ {F0} = 9.09, so harmonics 1 to {len(harmonics("saw", cut=CUT))} pass. Its LFO at 0.5 Hz takes {1 / 0.5:g} s, which is one '
             f'bar. Sub Pulse at 55 Hz with a 400 Hz cutoff keeps the odd harmonics 1, 3, 5 and 7 (55, 165, 275, 385 Hz). Glass Bell’s '
             f'second sine is {2 * 220} Hz when the first is 220 Hz. A quarter-note delay at {TEMPO} BPM is {beat_len() * 1000:.0f} ms.</p></div>'
             f'<div class="box"><span class="k">4 · The shape of the track</span>'
             f'<p style="margin:0;font-size:11.6pt;line-height:1.45">The pad opens alone and carries the piece. The bass joins at bar 5 '
             f'({mmss(bar_start(5))}) to start the Build. The bell enters at bar 13 ({mmss(bar_start(13))}) for the Lift, the bass drops out at bar 21 '
             f'({mmss(bar_start(21))}), and the pad and bell fade in the Outro.</p></div></div>')
    return D.page("Worked example · three invented patches", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def explore_page(n, wm=False):
    tasks = [("Open Alchemy. Play three presets that sound very different.", "Names and three words each"),
             ("Find the sound source. Switch between sine, triangle, saw and square.", "Which is brightest? Which is softest?"),
             ("Find the filter. Hold a note and move the cutoff slowly.", "What happens to the sound?"),
             ("Find the envelope. Make the attack slow, then fast.", "What changes?"),
             ("Find an LFO or modulation. Make something move.", "What is moving, and how fast?"),
             ("Find the effects. Turn one on and off.", "Which one, and what does it add?"),
             ("Find Save. Save a test patch with a numbered name.", "The name I used")]
    trs = "".join(f"<tr><td style='text-align:center;height:50pt'><b>{i}</b></td><td style='font-size:10.6pt'>{a}</td>"
                  f"<td style='font-size:9.6pt;vertical-align:top'><i>{b}</i></td></tr>" for i, (a, b) in enumerate(tasks, 1))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Step 1: open Alchemy and experiment with the interface, sound sources and presets. Start with the '
             f'Simple view. Work through the tasks with headphones on, and write what you notice. Nothing here is graded.</p>'
             f'<table class="map"><tr><th style="width:6%">#</th><th style="width:44%">Try this</th><th>What I found and heard</th></tr>{trs}</table>'
             f'<div class="fl" style="margin-top:8pt"><b>The sound I liked best, and why:</b><span></span></div>'
             f'<div class="fl"><b>Something I could not find or did not understand:</b><span></span></div>'
             f'<div class="ln2" style="margin-bottom:2pt"></div>'
             f'<div class="fl"><b>The one setting I want to explore first when I start Patch 1:</b><span></span></div>')
    return D.page("Explore sheet", "STUDENT", "Class 1", inner, n, wm, name=True, key="explore")


def card_html(label, hint, compact=False):
    h = 32 if compact else 38
    env = "".join(f"<td style='height:{h}pt;text-align:center'></td>" for _ in range(4))
    ver = "".join(f"<tr><td style='height:{h - 2}pt;text-align:center'>{i}</td><td></td><td></td></tr>" for i in ((1, 2, 3) if compact else (1, 2, 3, 4)))
    ln = f"margin-bottom:{7 if compact else 11}pt"
    return (f'<div class="box" style="margin-bottom:6pt;padding:6pt 9pt"><span class="k">{label}</span>'
            f'<div class="fl" style="{ln}"><b>Patch name:</b><span></span><b>Its job in my track:</b><span></span></div>'
            f'<p class="small" style="margin:0 0 3pt">{hint}</p>'
            f'<div class="fl" style="{ln}"><b>Sound source (waveform, layers):</b><span></span></div>'
            f'<div class="fl" style="{ln}"><b>Filter (type and cutoff):</b><span></span></div>'
            f'<table class="map" style="margin-bottom:3pt"><tr><th>Attack</th><th>Decay</th><th>Sustain</th><th>Release</th></tr><tr>{env}</tr></table>'
            f'<div class="fl" style="{ln}"><b>Modulation (what moves what, how fast):</b><span></span></div>'
            f'<div class="fl" style="{ln}"><b>Effects:</b><span></span></div>'
            f'<div class="fl" style="margin-bottom:2pt"><b>It sounds:</b><span></span><b>Saved as:</b><span></span></div>'
            f'{"" if compact else "<table class=map style=margin-top:4pt><tr><th style=width:9%>Version</th><th style=width:46%>What I changed</th><th>How it sounded</th></tr>" + ver + "</table>"}'
            f'</div>')


def patch1_page(n, wm=False):
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Step 3: create your first original sound from scratch, and save it. Start with one simple '
             f'waveform and shape it. Log each saved version, so you can go back to a sound you liked.</p>'
             + card_html("Patch card 1", "Pick a job first: a bass, a pad, a lead, a bell, a texture. The job tells you where to start.")
             + f'<div class="box acc-b"><span class="k">Before you move on</span><p style="margin:0;font-size:10.8pt">Is it saved? Can you play it '
               f'for the teacher and say what the oscillator, the filter, the envelope and the modulation are each doing?</p></div>')
    return D.page("Patch card 1", "STUDENT", "Class 2", inner, n, wm, name=True, key="patch1")


def patch23_page(n, wm=False):
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Step 4: build two more distinct sounds. Aim for variety: different jobs, different '
             f'waveforms, different envelopes.</p>'
             + card_html("Patch card 2", "A different job from Patch 1.", True) + card_html("Patch card 3", "Different from Patches 1 and 2.", True))
    return D.page("Patch cards 2 and 3", "STUDENT", "Class 3", inner, n, wm, name=True, key="patch23")


def trackplan_page(n, wm=False):
    rows = "".join("<tr><td style='height:42pt'></td><td></td><td></td><td></td><td></td></tr>" for _ in range(5))
    inner = (f'<div class="fl"><b>Tempo:</b><span style="flex:0 0 0.8in"></span><b>BPM.  One bar =</b><span style="flex:0 0 0.8in"></span>'
             f'<b>seconds (4 × 60 ÷ BPM).  Total bars:</b><span style="flex:0 0 0.8in"></span><span style="border:0"></span></div>'
             f'<div class="fl"><b>Length check: bars × seconds per bar =</b><span style="flex:0 0 1in"></span><b>seconds (must be 45–60)</b>'
             f'<span style="border:0"></span></div>'
             f'<p style="margin:2pt 0 5pt;font-size:10.8pt">Step 5: use your 3 patches to build a 45–60 second track. Design first, compose second: give each '
             f'patch a job, then decide when it comes in and goes out.</p>'
             f'<table class="map"><tr><th style="width:15%">Section</th><th style="width:12%">Bars</th><th style="width:12%">Time</th>'
             f'<th style="width:26%">Which patches play</th><th>What changes here</th></tr>{rows}</table>'
             f'<div class="fl" style="margin-top:8pt"><b>The main musical idea (a melody, a rhythm or a chord pattern):</b><span></span></div>'
             f'<div class="fl"><b>The patch that carries it, and why:</b><span></span></div>'
             f'<div class="fl"><b>Where the sound gets thicker or thinner:</b><span></span></div>'
             f'<div class="fl"><b>Automation I will draw (what and where):</b><span></span></div>'
             f'<div class="ln2" style="margin-bottom:2pt"></div>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">Check before you compose</span><p style="margin:0;font-size:10.8pt">Does every patch '
             f'appear? Does the track change at least three times? Is there a quiet part and a full part?</p></div>')
    return D.page("Track plan", "STUDENT", "Class 4", inner, n, wm, name=True, key="trackplan")


def mixcheck_page(n, wm=False):
    rows = "".join("<tr><td style='height:27pt'></td><td></td><td></td><td></td><td></td></tr>" for _ in range(6))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Step 6: apply effects, automation, EQ and panning, then bounce. Fill in one row per track.</p>'
             f'<table class="map"><tr><th style="width:18%">Track</th><th style="width:20%">Patch</th><th style="width:12%">Pan (L–R)</th>'
             f'<th style="width:25%">EQ move</th><th>Effects and automation</th></tr>{rows}</table>'
             f'{D.H2("Sound check")}'
             + "".join(D.chk(c, 12, "font-size:11pt;margin-bottom:4pt") for c in [
                 "All 3 custom patches are used in the track",
                 "Each patch sounds different from the other two",
                 "At least one patch is thickened with layers or effects",
                 "I used automation at least once (volume, filter or an effect)"]) +
             f'{D.H2("Mix check")}'
             + "".join(D.chk(c, 12, "font-size:11pt;margin-bottom:4pt") for c in [
                 "I listened with headphones and again at a lower volume",
                 "No track is much louder than the rest; nothing clips",
                 "Bass and pad do not fight each other (EQ or levels)",
                 "The track is 45–60 seconds long"]) +
             f'{D.H2("Bounce")}'
             + "".join(D.chk(c, 12, "font-size:11pt;margin-bottom:4pt") for c in [
                 "Bounced as .mp3 or .wav and played back from the start",
                 "Zipped the .logicx project and named both files correctly"]))
    return D.page("Mix check", "STUDENT", "Class 6", inner, n, wm, name=True, key="mixcheck")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "synthguide": synthguide_page, "example": example_page,
         "explore": explore_page, "patch1": patch1_page, "patch23": patch23_page, "trackplan": trackplan_page, "mixcheck": mixcheck_page}


# ================================================================ content checks (synth arithmetic, owner text, no audio)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 6), reqs=(REQS, 5), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 3))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp} (the owner's count)")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is the owner's /25, levels 1-5")
    if [c for c, _ in RUBRIC] != ["Creativity & Originality", "Technical Skill / DAW Use", "Composition & Structure",
                                  "Sound Design & Mix Quality", "Documentation & Presentation"]:
        errs.append("rubric categories must be the owner's, in order")
    if FILE_NAME not in CHECK[2] or "Alchemy Architect" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    if "45–60 second" not in REQS[2] or "at least 3" not in REQS[0]:
        errs.append("requirements: 3 patches and a 45-60 second track")
    # the worked example adds up
    if bar_len() != 2.0 or beat_len() != .5:
        errs.append("bar lengths: 2.0 s at 120 BPM, a beat is 0.5 s")
    if len(harmonics("saw", cut=CUT)) != 9 or len(harmonics("saw", cut=500)) != 4 or len(harmonics("saw", cut=2000)) != 18:
        errs.append("saw at 110 Hz: 9 harmonics under 1000 Hz, 4 under 500, 18 under 2000")
    if harmonics("square", f0=55, cut=400) != [55, 165, 275, 385]:
        errs.append("square at 55 Hz under 400 Hz keeps 55, 165, 275, 385")
    if lfo_cycles_per_bar(0.5) != 1 or lfo_cycles_per_bar(4) != 8 or 1 / 0.5 != bar_len():
        errs.append("LFO 0.5 Hz = one cycle per bar, 4 Hz = eight per bar at 120 BPM")
    if TOTAL_BARS * bar_len() != 52 or not 45 <= TOTAL_BARS * bar_len() <= 60:
        errs.append("track plan: 26 bars = 52 s, inside 45-60")
    if SECTIONS[0][1] != 1 or SECTIONS[-1][2] != TOTAL_BARS or any(b + 1 != c for (_, _, b), (_, c, _) in zip(SECTIONS, SECTIONS[1:])):
        errs.append("sections must tile bars 1-26")
    if any(a < 1 or b > TOTAL_BARS or a > b for _, a, b in LANES) or len(LANES) != 3:
        errs.append("three lanes inside the plan")
    if [p[0] for p in PATCHES] != [l[0] for l in LANES]:
        errs.append("patch names must match the lanes")
    for _, _, _, _, (a, d, s, r), *_ in PATCHES:
        if min(a, d, r) <= 0 or not 0 <= s <= 100:
            errs.append("envelope values out of range")
    if mmss(bar_start(13)) != "0:24" or mmss(bar_start(21)) != "0:40" or mmss(bar_start(TOTAL_BARS + 1)) != "0:52":
        errs.append("bar 13 = 0:24, bar 21 = 0:40, end = 0:52")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    txt = " ".join(flat)
    for need in ("No audio, video, songs or presets are included", "invented patches and a 26-bar plan, described on paper",
                 "Your Name – Alchemy Architect", "Final Grade = Average of Student + Teacher", "YouTube"):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up:
        errs.append("UPLOAD.md: must say no audio is included and record the open questions")
    for i in (4, 10, 11, 12, 13):   # slides that shorten the owner's wording must say so
        if "shortened" not in notes[i].lower():
            errs.append(f"deck slide {i + 1} notes: must say the owner's wording is shortened")
    ch = flat[D.IX("changes") - 1]
    for s in ("slide 5", "slide 11", "slide 12", "slide 13", "slide 14"):
        if s not in ch:
            errs.append(f"'What changed' page must list {s}")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or any("oscillator" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in ("Billie", "Beatles", "Spotify", "Daft", "Skrillex", "Moog", "Serum", "Disney", "Minecraft", "Mario"):
        if banned in alldeck or banned in txt:
            errs.append(f"must not name songs, artists, products or services ({banned})")
    return errs


def check_summary():
    return (f"A saw at {F0} Hz keeps {len(harmonics('saw', cut=CUT))} harmonics under a {CUT} Hz cutoff; a 0.5 Hz LFO is one cycle per bar at "
            f"{TEMPO} BPM; the invented track is {TOTAL_BARS} bars = {TOTAL_BARS * bar_len():g} s; "
            f"the owner's lists counted (4 goals, 6 terms, 5 requirements, 7 steps, 4 tips, 6 checklist items, 4 struggles, 3 resources); "
            f"{len(CHANGES)} wording changes disclosed; no audio included; grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
