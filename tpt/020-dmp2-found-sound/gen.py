#!/usr/bin/env python3
"""DMP2 project: Found Sound (TpT 020): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Found Sound > "Found Sound - Project Sheet & Rubric" (rubric 5 categories scored 1-5, /25, final grade =
average of student and teacher scores), TEACHER NOTES > "Found Sound - Teacher Notes" (7 class periods), and the project's entry on
"DMP2 - Project Menu" (the June 2026 menu; owner, 17 Oct 2026: the June entry may be quoted). These three set the project text, steps,
rubric and pacing (owner rule, 17 Oct 2026).
Supporting artifacts: the Teacher Notes name three suggested resources (two Quick Sampler tutorials and an example editing session, all
on YouTube). They are third-party videos and no owner-made copy exists in the other DMP2 folders (the older Projects > Found Sound
Project folder holds the 2025 outline and a list of YouTube tutorial links, which are third-party and not a source), so the three are
printed as the owner wrote them and nothing is included: no link, audio or video.

NO AUDIO IS INCLUDED. Students record their own everyday sounds. The worked example is an invented piece ("Passing Period", 45 seconds,
96 BPM, 18 bars) described on paper; every picture (sound-to-instrument, the three Quick Sampler modes, the layer timeline) is drawn in
code. Songs and chart data are not named.
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "found-sound"
TITLE = "Found Sound"
ACCENT = "#1F6F5C"          # this product's single accent: pine green (008 red, 009 orange, 010 violet, 011 teal, 012 blue, 013 green, 014 magenta, 015 gold, 016 olive, 017 sienna, 018 steel blue, 019 wine)
ACC_LIGHT = "#CBE6DD"
PRICE = "10.00"
CLASSES = 7
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-019).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "Found Sound in Logic Pro | Quick Sampler Sound Design Project | High School"
DESC_START = "Sound design project for high school music technology:"
DESC_MUST = ["Found Sound", "Quick Sampler", "no audio", "Padlet"]
ZIP_DIR = "Found Sound - Hudson Beat"
ZIP_DATE = (2026, 10, 18, 12, 0, 0)
TYPE = "Open-Ended Project"
PROJ_LINE = "Digital Music Production | <i>Open-Ended Project</i> | 7 class periods"
DECK_STRAP = "Turn everyday sounds into instruments in Logic Pro"
BANNED_EXTRA = []

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Open-Ended", "Sound Design"
MENU_DESC = "Record everyday sounds and transform them into instruments using Quick Sampler. Compose entirely from found sounds."
OVERVIEW = ("Become a sound designer. Record everyday sounds — from your phone, the microphone at your station, or anywhere around you — "
            "and transform them into musical instruments using Logic’s Quick Sampler. Then compose a short piece built entirely from your "
            "found sounds.")
GOALS = ["Record, edit, and manipulate real-world sounds as creative tools",
         "Use Quick Sampler to build playable instruments from audio recordings",
         "Design at least three distinct sound layers (percussion, bass, texture)",
         "Apply effects, automation, and mixing to create a polished composition"]
VOCAB = [("Found Sound", "Any sound from the real world used as raw material for music"),
         ("Quick Sampler", "Logic’s tool for turning any audio into a playable instrument"),
         ("Normalize", "Adjusting the volume of a recording so its loudest point hits a target level"),
         ("Sound Design", "The process of creating, manipulating, and shaping sounds for a specific purpose"),
         ("Layering", "Stacking multiple sounds on top of each other to create depth and texture")]
REQS = ["Record or source at least 5 original audio samples",
        "Edit, trim, and normalize sounds in Logic Pro",
        "Import sounds into Quick Sampler to create playable instruments",
        "Design at least 3 distinct sound layers (e.g., percussion, bass, texture)",
        "Apply effects and automation for dynamics and interest",
        "Length: 30–60 seconds"]
STEPS = ["<b>Collect sounds</b> — Record at least 5 sounds using your phone or the microphone at your station (Sound log: page @SOUNDS)",
         "<b>Edit and prep</b> — Trim, normalize, and clean up your recordings in Logic (Logic quick reference: page @LOGICREF)",
         "<b>Build instruments</b> — Import sounds into Quick Sampler and experiment with playback modes (Quick Sampler modes: page @MODES; "
         "Instrument builder: page @INSTRUMENTS)",
         "<b>Compose</b> — Use your custom instruments to build a short piece with at least 3 layers (Layer plan: page @LAYERS)",
         "<b>Mix</b> — Apply EQ, effects, and automation. Balance levels and add polish.",
         "<b>Finalize</b> — Bounce your track and prepare your presentation",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["The weirder the source sound, the more interesting your instruments will be. Don’t just record obvious things.",
        "Spend time in Quick Sampler experimenting with Slice mode — it turns one recording into a whole kit.",
        "Layer your sounds. A single found sound as a melody is thin. Stack textures underneath it.",
        "The goal is transformation — if your audience can’t tell where the sounds came from, you’re doing it right."]
FILE_NAME = "“Your Name – Found Sound”"
CHECK = ["Bounced .mp3 or .wav uploaded to your class page",
         "Zipped .logicx project file uploaded to your class page",
         f"Files named correctly: {FILE_NAME}",
         "At least 5 source sounds recorded and used",
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
TN_REINFORCES = ("Builds recording skills, Quick Sampler proficiency, and sound design thinking. Teaches students that music can come "
                 "from anywhere, not just preset libraries.")
STRUGGLES = ["Students record low-quality audio. Show them how to get clean recordings from their phone or the condenser mic at their station.",
             "Quick Sampler setup is confusing at first. Demo all three modes (Classic, One Shot, Slice) with a real sound.",
             "Students create instruments but don’t compose with them — they just audition sounds endlessly.",
             "The 30–60 second length feels limiting. Remind them that density matters more than length."]
VAR_EASY = "Provide a set of pre-recorded found sounds that students can use alongside their own."
VAR_HARD = ("Require all source sounds to be original recordings (no pre-made sources). Extend to 90 seconds with a clear compositional "
            "arc.")
RESOURCES = [("Quick Sampler — Turn Any Sound into an Instrument (YouTube)",
              "Named as I listed it. No link, audio or video is included, so find a copy on a service your school allows. My Class 1 demo "
              "(slide 6) and the Quick Sampler modes page (page @MODES) cover the same ground."),
             ("Advanced Quick Sampler Techniques (YouTube)",
              "Named as I listed it; nothing is included. Watch it yourself before Class 2 and take what you need for the three-modes demo "
              "(slide 9)."),
             ("Example of a Found Sound editing session (YouTube)",
              "Named as I listed it; nothing is included. This kit gives a worked example on paper instead (page @EXAMPLE): an invented "
              "45-second piece, so you can show what a finished plan looks like without playing anyone else’s work.")]
TN_NOTE = ("Encourage students to record sounds during passing periods, lunch, or at home. The wider the variety, the better.")
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Creativity &amp; Originality: ask what each source sound was, then play the instrument made from it. My tip 4 is the test: "
                "if the audience can’t tell where the sounds came from, the transformation worked.",
                "Technical Skill: look at the Sound log (page @SOUNDS) and the Instrument builder (page @INSTRUMENTS). Were at least 5 sounds "
                "recorded, trimmed and normalized, and which Quick Sampler modes were used?",
                "Composition &amp; Structure: use the Layer plan (page @LAYERS). Are there at least 3 distinct layers, and does the piece "
                "change over 30–60 seconds?",
                "Sound Design &amp; Mix Quality: listen with headphones and ask which layer is leading in each section. Levels and EQ should "
                "be a choice.",
                "Documentation &amp; Presentation: the Sound log, Instrument builder, Layer plan, Padlet questions and the Reflection page "
                "(page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Introduction. Demo Quick Sampler with a live recording. Students begin collecting sounds.",
     "do": "Slides 1–7: hook, what found sound is, from sound to song, a live demo, steps 1 and 2. Record a sound in front of the class "
           "and play it in Quick Sampler. Hand out the project sheet and the Sound log.", "slides": (1, 7),
     "pages": ["sounds", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Name that sound · found sound · sound to song · live demo"},
    {"n": 2, "owner": "<b>Class 2:</b> Edit and prep recordings. Begin building instruments in Quick Sampler.",
     "do": "Slides 8–10: the three Quick Sampler modes, a live demo of all three, go weird. Students trim and normalize, then start the "
           "Instrument builder.", "slides": (8, 10), "pages": ["modes", "instruments", "logicref"],
     "deck": "Classic · One Shot · Slice · demo · go weird"},
    {"n": 3, "owner": "<b>Classes 3–5:</b> Working days — compose, layer, and mix.",
     "do": "Slides 11–12: compose with your instruments, three layers. Hand out the Layer plan. Then work time.", "slides": (11, 12),
     "pages": ["layers"], "deck": "Working day: compose and layer"},
    {"n": 4, "owner": None, "do": "Slides 13–14: the worked example on paper and the layer check. Then work time.", "slides": (13, 14),
     "pages": ["layers"], "deck": "Working day: the worked example, check your layers"},
    {"n": 5, "owner": None, "do": "Full working day: compose, layer and mix. Ask each student to play you one instrument and say what "
     "sound it came from.", "slides": None, "pages": [], "deck": "Working day: compose, layer, mix"},
    {"n": 6, "owner": "<b>Class 6:</b> Final mix, bounce. Prepare presentations.",
     "do": "Slides 15–17: mix and finalize, what to turn in, the rubric. Students self-score and post their three questions.",
     "slides": (15, 17), "pages": ["rubric", "present"], "deck": "Mix · bounce · checklist · rubric"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 18–19: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (18, 19), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one rule for Class 1</span>'
    '<p style="margin:0;font-size:9.6pt">Students record before they edit. By the end of Class 1 every student has at least one clean '
    'recording on the Sound log (page @SOUNDS), so Class 2 is spent building instruments, not hunting for sounds.</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:9.6pt">Working days. Class 5 has no new slide. '
    'Circulate and ask: which layer is this, and what sound did it come from? Instruments that never reach the Layer plan are my third '
    'struggle.</p></div></div>')
PACING_SIZE = 9.9

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (checklist items 1 and 2).",
    "Page numbers are added to steps 1 to 4 (the Sound log, Logic quick reference, Quick Sampler modes, Instrument builder and Layer plan).",
    "My three suggested resources are listed as I wrote them (page @TN2). None is included: no link, audio or video comes with the kit. "
    "The kit adds a worked example on paper (page @EXAMPLE) beside the third.",
    "My pacing guide’s “Classes 3–5” row spans the Class 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 3 shortens the definition of found sound, slide 7 "
    "shortens steps 1 and 2 and my first struggle, slide 10 shortens tips 1, 2 and 4, slide 11 shortens step 4 and my third struggle, "
    "slide 12 shortens a goal, a requirement and my fourth struggle, slide 15 shortens steps 5 and 6, slide 16 shortens the submission "
    "checklist, and slide 18 shortens step 7.",
]
CHANGES_MUST_MENTION = ["your class page", "Page numbers", "None is included", "Classes 3–5", "Layout only", "intro deck shortens"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the goals, the five vocabulary terms, the six requirements, "
        "steps (apart from the page numbers), tips, checklist and file name (“Your Name – Found Sound”), the rubric (five categories "
        "scored 1–5, /25, the average of the student’s and the teacher’s score), what the project reinforces, the four common "
        "struggles, the variations, my day-by-day pacing and my closing note, and the project menu entry quoted on page @OVERVIEW. "
        "No rubric row is added and the requirements are unchanged.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: how to use the kit, the overview and setup "
                "pages (with a list of sounds to try for my Easier variation), the teacher moves and slide numbers in the pacing guide, "
                "the grading suggestions, the Logic quick reference, the Quick Sampler modes page (three modes drawn), the worked example "
                "(an invented 45-second piece on paper, not audio), the Sound log, Instrument builder and Layer plan, the vocabulary page, "
                "the presentation planner and the intro deck. None of these adds a requirement or a rubric row.")

# ================================================================ the worked example (Hudson Beat original: an invented piece on paper)
PIECE = "Passing Period"
BPM = 96
BAR_S = 4 * 60 / BPM                  # 2.5 seconds per bar in 4/4
BARS = 18
TOTAL_S = 45
SECTIONS = [("Intro", 0, 5), ("Build", 5, 15), ("Full", 15, 35), ("Break", 35, 40), ("Outro", 40, 45)]       # seconds
SECTION_BARS = [2, 4, 8, 2, 2]
LANES = ["Percussion", "Bass", "Texture", "Filter sweep"]
SPANS = {"Percussion": [(5, 35), (40, 45)], "Bass": [(15, 35)], "Texture": [(0, 45)]}
BASS_NOTES = [0, 0, 2, 1, 0, 0, 3, 1]          # one block per bar in the Full section: height step
FILTER = [(0, 10), (5, 10), (15, 90), (35, 90), (40, 25), (45, 60)]     # texture low-pass, percent open
SOUND_ROWS = [("Locker slam", "phone, one take", "Slice (5 slices)", "Percussion", "slices on five keys: boom, rattle, click"),
              ("Pencil tap", "station microphone", "Classic, short", "Percussion", "pitched up, played as a tick"),
              ("Door thud", "phone", "Classic, pitched down", "Bass", "played as a simple bassline"),
              ("Vending-machine hum", "phone, 20 seconds", "Classic, loop on", "Texture", "held under everything, filter sweeps"),
              ("Water-bottle crinkle", "station microphone", "One Shot", "Texture", "one press at the start of the Break")]
QUESTIONS = ["Which sound did you guess first, and which one fooled you?",
             "If you took one layer out, which one would you miss most?",
             "Where does the track change the most, and how did I do it?"]


def mmss(t):
    return f"{int(t) // 60}:{int(round(t)) % 60:02d}"


# ================================================================ drawings (original, code-drawn: black + accent only)
WAVE = [.9, .5, .3, .2, .6, .95, .4, .25, .2, .5, .85, .35, .3, .45, .7, .9, .3, .2, .25, .6, .8, .3, .2, .15, .1, .05]
CUTS = [5, 10, 15, 20]


def hero_body():
    W, H = 1100, 560
    out = []
    for i, h in enumerate(WAVE[:16]):
        x = 40 + i * 28
        hh = 40 + h * 300
        out.append(f'<line x1="{x}" y1="{280 - hh / 2:.1f}" x2="{x}" y2="{280 + hh / 2:.1f}" stroke="#000" stroke-width="14" stroke-linecap="round"/>')
    out.append(f'<line x1="500" y1="280" x2="568" y2="280" stroke="#000" stroke-width="7" stroke-linecap="round"/>')
    out.append(f'<polygon points="590,280 562,262 562,298" fill="#000"/>')
    kx, ky, kw, kh = 620, 110, 62, 340
    for k in range(7):
        hot = k in (1, 3, 4)
        out.append(f'<rect x="{kx + k * kw}" y="{ky}" width="{kw - 4}" height="{kh}" rx="6" fill="{ACCENT if hot else "#fff"}" stroke="#000" stroke-width="4"/>')
    for k in (0, 1, 3, 4, 5):
        out.append(f'<rect x="{kx + (k + 1) * kw - 22}" y="{ky}" width="38" height="{kh * 0.58:.0f}" rx="4" fill="#000"/>')
    return "".join(out), W, H


def modes_body(W=1600, name="modes", fs=30, cs=22, rs=18):
    gap = 40
    W0, W = W, W - 6
    pw = (W - 2 * gap) / 3
    bh, kh = 150, 66
    out = []
    heads = [("CLASSIC", "plays across the keys, with a loop"), ("ONE SHOT", "the whole sound, every key press"),
             ("SLICE", "one recording, one slice per key")]
    top = fs + 18
    n = len(WAVE)
    bw = (pw - 24) / n
    for p, (nm, cap) in enumerate(heads):
        x0 = p * (pw + gap)
        out.append(D.t_(x0 + pw / 2, fs, nm, fs, 700))
        D.lab(name + " heads", nm, fs, pw - 10)
        out.append(f'<rect x="{x0:.1f}" y="{top}" width="{pw:.1f}" height="{bh}" fill="#fff" stroke="#000" stroke-width="2"/>')
        if p == 0:
            out.append(f'<rect x="{x0 + 12 + 8 * bw:.1f}" y="{top + 6}" width="{8 * bw:.1f}" height="{bh - 12}" fill="{ACC_LIGHT}"/>')
        for i, h in enumerate(WAVE):
            bx = x0 + 12 + i * bw + bw / 2
            hh = 8 + h * (bh - 40)
            col = ACCENT if p == 1 else "#000"
            out.append(f'<line x1="{bx:.1f}" y1="{top + bh / 2 - hh / 2:.1f}" x2="{bx:.1f}" y2="{top + bh / 2 + hh / 2:.1f}" stroke="{col}" '
                       f'stroke-width="{bw * .55:.1f}" stroke-linecap="round"/>')
        if p == 0:
            out.append(D.t_(x0 + 12 + 12 * bw, top + 22, "LOOP", rs, 700, fill_=ACCENT))
            D.lab(name + " loop", "LOOP", rs, 8 * bw)
        if p == 2:
            edges = [0] + CUTS + [n]
            for c in CUTS:
                cx = x0 + 12 + c * bw
                out.append(f'<line x1="{cx:.1f}" y1="{top + 4}" x2="{cx:.1f}" y2="{top + bh - 4}" stroke="{ACCENT}" stroke-width="4"/>')
            for k in range(5):
                mx = x0 + 12 + (edges[k] + edges[k + 1]) / 2 * bw
                out.append(D.t_(mx, top + bh - 10, str(k + 1), rs + 2, 700, fill_=ACCENT))
        ky = top + bh + 18
        kw = pw / 10
        hot = {0: (2, 4, 6), 1: (4,), 2: (2, 3, 4, 5, 6)}[p]
        for k in range(10):
            on = k in hot
            out.append(f'<rect x="{x0 + k * kw:.1f}" y="{ky}" width="{kw - 2:.1f}" height="{kh}" rx="3" fill="{ACCENT if on else "#fff"}" stroke="#000" stroke-width="2"/>')
            if p == 2 and on:
                out.append(D.t_(x0 + k * kw + kw / 2 - 1, ky + kh - 12, str(k - 1), rs, 700, fill_="#fff"))
        out.append(D.t_(x0 + pw / 2, ky + kh + cs + 12, cap, cs, 500))
        D.lab(name + " caps", cap, cs, pw - 10)
    H = top + bh + 18 + kh + cs + 28
    return f'<g transform="translate(3,0)">{"".join(out)}</g>', W0, H


def chain_body(W=1600, name="chain", fs=30, cs=22):
    gap = 74
    pw = (W - 3 * gap) / 4
    bh = 190
    items = [("Record", "phone or station mic"), ("Prep", "trim · normalize"),
             ("Instrument", "Quick Sampler"), ("Layers", "percussion · bass · texture")]
    out = []
    for k, (h, s) in enumerate(items):
        x0 = k * (pw + gap)
        out.append(f'<rect x="{x0:.1f}" y="4" width="{pw:.1f}" height="{bh}" rx="12" fill="{"#000" if k % 2 == 0 else ACCENT}"/>')
        out.append(D.t_(x0 + pw / 2, 4 + bh / 2 - 6, h.upper(), fs, 700, fill_="#fff"))
        D.lab(name + " heads", h.upper(), fs, pw - 30)
        out.append(D.t_(x0 + pw / 2, 4 + bh / 2 + 38, s, cs, 500, fill_="#fff"))
        D.lab(name + " subs", s, cs, pw - 30)
        out.append(D.t_(x0 + 24, 4 + 40, str(k + 1), 28, 700, anchor="start", fill_="#fff"))
        if k < 3:
            ax = x0 + pw + 10
            ay = 4 + bh / 2
            out.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{ax + gap - 36:.1f}" y2="{ay:.1f}" stroke="#000" stroke-width="6" stroke-linecap="round"/>')
            out.append(f'<polygon points="{ax + gap - 16:.1f},{ay:.1f} {ax + gap - 40:.1f},{ay - 15:.1f} {ax + gap - 40:.1f},{ay + 15:.1f}" fill="#000"/>')
    cap = "A sound is only raw material until you turn it into an instrument and layer it"
    out.append(D.t_(W / 2, bh + 56, cap, cs + 2, 500))
    D.lab(name + " cap", cap, cs + 2, W - 20)
    return "".join(out), W, bh + 72


def plan_body(W=1600, name="plan", fs=30, ts=22):
    gx = 262
    pwid = W - gx - 16

    def X(t):
        return gx + pwid * t / TOTAL_S

    out = []
    sh = 66
    fills = ["#4a4a4a", "#000", ACCENT, "#4a4a4a", "#000"]
    for (nm, a, b), fc in zip(SECTIONS, fills):
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{fc}"/>')
        out.append(D.t_((X(a) + X(b)) / 2, sh / 2 + fs * .36 + 2, nm.upper(), fs - 4, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 4, X(b) - X(a) - 14)
    lh, lg = 70, 12
    y0 = sh + 22
    beat = 60 / BPM
    for i, nm in enumerate(LANES):
        yy = y0 + i * (lh + lg)
        out.append(D.t_(gx - 16, yy + lh / 2 + 8, nm.upper(), 24, 700, anchor="end"))
        D.lab(name + " lanes", nm.upper(), 24, gx - 30)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.4"/>')
        if nm == "Percussion":
            for a, b in SPANS[nm]:
                k = 0
                while a + k * beat < b - 1e-9:
                    t = a + k * beat
                    tall = k % 4 in (0, 2)
                    h_ = lh - 22 if tall else lh - 42
                    out.append(f'<rect x="{X(t) - 2:.1f}" y="{yy + (lh - h_) / 2:.1f}" width="5" height="{h_}" rx="2" fill="#000"/>')
                    k += 1
        elif nm == "Bass":
            for a, b in SPANS[nm]:
                bars = int(round((b - a) / BAR_S))
                for j in range(bars):
                    t0 = a + j * BAR_S
                    st = BASS_NOTES[j % len(BASS_NOTES)]
                    out.append(f'<rect x="{X(t0) + 2:.1f}" y="{yy + 10 + (3 - st) * 12:.1f}" width="{X(t0 + BAR_S) - X(t0) - 4:.1f}" height="18" rx="4" fill="{ACCENT}"/>')
        elif nm == "Texture":
            out.append(f'<rect x="{X(0):.1f}" y="{yy + 22}" width="{X(35) - X(0):.1f}" height="{lh - 44}" rx="6" fill="#7a7a7a"/>')
            out.append(f'<rect x="{X(35):.1f}" y="{yy + 8}" width="{X(40) - X(35):.1f}" height="{lh - 16}" rx="6" fill="#4a4a4a"/>')
            out.append(f'<rect x="{X(40):.1f}" y="{yy + 22}" width="{X(45) - X(40):.1f}" height="{lh - 44}" rx="6" fill="#7a7a7a"/>')
        else:
            pts = " ".join(f"{X(t):.1f},{yy + lh - 8 - (lh - 16) * v / 100:.1f}" for t, v in FILTER)
            out.append(f'<polygon points="{X(0):.1f},{yy + lh - 8} {pts} {X(TOTAL_S):.1f},{yy + lh - 8}" fill="{ACC_LIGHT}"/>')
            out.append(f'<polyline points="{pts}" fill="none" stroke="{ACCENT}" stroke-width="5" stroke-linejoin="round"/>')
    ty = y0 + len(LANES) * (lh + lg) + 4
    for t in (0, 5, 15, 35, 40, 45):
        lbl = mmss(t)
        anc = "start" if t == 0 else ("end" if t == TOTAL_S else "middle")
        out.append(f'<line x1="{X(t):.1f}" y1="{ty - 6}" x2="{X(t):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(t) + (2 if t == 0 else (-2 if t == TOTAL_S else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 90)
    return "".join(out), W, ty + ts + 22


DRAWINGS = {"hero": lambda: D.stack([hero_body()], 40), "modes": lambda: modes_body(1600, "modes pic"), "chain": lambda: chain_body(1600, "chain pic"),
            "plan": lambda: plan_body(1600, "plan pic")}
DRAWING_PX = {"hero": 1900, "modes": 2000, "chain": 2000, "plan": 2000}
SIDE = {"modes": ["Classic: across the keys, with a loop", "One Shot: the whole sound each time", "Slice: one recording, a whole kit", "Pick the mode that fits the job"],
        "chain": ["Record clean sounds", "Trim and normalize them", "Build instruments in Quick Sampler", "Layer them into a piece"],
        "plan": ["Three layers, all playing at once", "Texture, then percussion, then bass", "A filter sweep keeps it moving", "Plan 30–60 seconds"]}


def label_extras():
    modes_body(1250, "page modes", 26, 19, 16)
    plan_body(1250, "page plan", 26, 19)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Found Sound", "Turn everyday sounds into instruments.",
     "Class 1, the first minute. No audio is included in this deck. Open with my overview: become a sound designer, record everyday "
     "sounds from your phone, the microphone at your station, or anywhere around you, and transform them into musical instruments using "
     "Logic's Quick Sampler. Then compose a short piece built entirely from your found sounds, 30 to 60 seconds long."),
    (1, "listen", "Listen: name that sound", "What was that? · Guess, then explain how you know|Teacher: make a short everyday sound out of "
     "view (a zip, a drawer, a pen click).|What do you think made it?|What does it remind you of?|Could it be a drum, a bass or a pad?",
     "Make a short sound yourself, out of the students' view: a zipper, a drawer, a stapler, a pen click. Nothing needs to be played from "
     "a speaker, and no recording from anyone else is used. Take guesses aloud. The point is that every sound can be heard two ways: what "
     "made it, and what it could become. That is the idea behind the whole project, and it sets up my line that music can come from "
     "anywhere, not just preset libraries."),
    (1, "bullets", "What is found sound?", "Any real-world sound used as raw material for music|Quick Sampler turns any audio into a playable "
     "instrument|Sound design: shaping sounds for a purpose",
     "My vocabulary terms, shortened to fit the slide. Found sound: any sound from the real world used as raw material for music. Quick "
     "Sampler: Logic's tool for turning any audio into a playable instrument. Sound design: the process of creating, manipulating and "
     "shaping sounds for a specific purpose. Students write the five terms in their own words on the vocabulary page; normalize and "
     "layering come up on later days."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: introduction, a Quick Sampler demo with a live recording, students begin "
     "collecting sounds. Class 2: edit and prep recordings, begin building instruments in Quick Sampler. Classes 3 to 5 are working "
     "days: compose, layer and mix. Class 6: final mix and bounce, prepare presentations. Class 7: presentations with Padlet Q and A peer "
     "feedback. Hand out the project sheet now."),
    (1, "pic", "From sound to song", "chain",
     "Class 1. The path of the project in four moves. Record a sound with your phone or the microphone at your station. Prep it: trim, "
     "normalize and clean it up in Logic. Build an instrument from it in Quick Sampler. Then layer your instruments into a piece with "
     "at least three distinct layers, for example percussion, bass and texture. Requirement 4 asks for exactly that; a single found sound "
     "as a melody is thin, so stack textures underneath it."),
    (1, "steps", "Watch me: sound to instrument", "Record one short everyday sound|Trim it and normalize it in Logic|Drag it into Quick "
     "Sampler|Play it on the keyboard|Name it and save the project",
     "My Class 1 plan is to demo Quick Sampler with a live recording. The five lines are the kit's own outline of that demo, not my steps. "
     "Record a sound in front of the class: a pen click, a book closing, your keys. Trim it, normalize it, drag it into Quick Sampler "
     "and play it on the keys so students hear an everyday noise become an instrument. Keep it to about ten minutes and save the project "
     "when you finish. Menu names are on the Logic quick reference; check the labels on your version."),
    (1, "steps", "Steps 1 and 2: collect, prep", "Record at least 5 sounds|Use your phone or the microphone at your station|Get clean "
     "recordings: close, quiet, no wind|Trim, normalize and clean up in Logic|Fill in the Sound log",
     "Steps 1 and 2 of the project sheet, shortened to fit the slide. Step 1: record at least 5 sounds using your phone or the microphone "
     "at your station. Step 2: trim, normalize and clean up your recordings in Logic. My first struggle, shortened here: students record "
     "low-quality audio, so show them how to get clean recordings from a phone or the condenser mic. The tips on the slide are the "
     "kit's suggestions, not mine: get close to the sound, record in a quiet spot, keep wind off the microphone."),
    (2, "pic", "Three Quick Sampler modes", "modes",
     "Class 2. Quick Sampler has three modes: Classic, One Shot and Slice. Classic plays the sound across the keys like an instrument and "
     "lets you set a loop. One Shot plays the whole sound each time a key is pressed. Slice cuts a recording at its loud moments and "
     "puts each slice on its own key, so one recording becomes a whole kit. My second struggle is that Quick Sampler is confusing at "
     "first, so demo all three modes with a real sound. Check the labels on your version."),
    (2, "steps", "Watch me: all three modes", "Take one recording with several hits|Play it in Classic, with a loop|Switch to One Shot|"
     "Switch to Slice and play the kit|Which mode fits which job?",
     "A live demo of about ten minutes; the five lines are the kit's own outline, not my steps. Use one recording with several loud "
     "moments, such as a drawer, a stapler or a locker. Play it in Classic with a loop, switch to One Shot, then Slice and play the slices "
     "across the keys. Ask students which mode suits percussion, which suits bass and which suits texture, and let them argue. My tip 2 "
     "says Slice turns one recording into a whole kit."),
    (2, "bullets", "Go weird", "The weirder the source, the better the instrument|Don't just record the obvious|Try Slice on one recording|"
     "Transformation is the goal",
     "My tips 1, 2 and 4, shortened to fit the slide. Tip 1: the weirder the source sound, the more interesting your instruments will be, "
     "so do not just record obvious things. Tip 2: experiment with Slice mode, which turns one recording into a whole kit. Tip 4: the goal "
     "is transformation; if your audience cannot tell where the sounds came from, you are doing it right. Students begin the Instrument "
     "builder today."),
    (3, "bullets", "Working days: compose", "Use your custom instruments to build the piece|Stop auditioning, start playing|Aim for at least "
     "3 layers|Save versions as you go",
     "Class 3 is the first working day, and Classes 4 and 5 continue it. Step 4 of the project sheet, shortened here: use your custom "
     "instruments to build a short piece with at least 3 layers. My third struggle, shortened: students create instruments but do not "
     "compose with them, they just audition sounds endlessly. Set a rule: an instrument that has no place on the Layer plan gets a job "
     "or goes. Students use the Layer plan."),
    (3, "bullets", "Three layers, not one", "Percussion · bass · texture|A single found sound as a melody is thin|Stack textures "
     "underneath|Density matters more than length",
     "Goal 3 and requirement 4, shortened: design at least three distinct sound layers, for example percussion, bass and texture. My tip 3 "
     "says a single found sound as a melody is thin, so stack textures underneath it. My fourth struggle, shortened: the 30 to 60 second "
     "length feels limiting, so remind students that density matters more than length. Circulate and ask each student to play you "
     "their three layers one at a time."),
    (4, "pic", "Worked example: 45 seconds on paper", "plan",
     "Class 4. An invented piece, Passing Period, described on paper; nothing here is audio. It is 96 beats per minute, 18 bars of 4/4, which "
     "is 45 seconds, inside my 30 to 60 second requirement. A vending-machine hum sets the texture from the start, a pencil tap and a "
     "locker slam sliced across the keys enter as percussion at 5 seconds, and a door thud pitched down joins as bass at 15 seconds. A "
     "filter sweep opens the texture, a short break strips back to the hum, and the outro closes. The full plan is on the worked example "
     "page."),
    (4, "bullets", "Check your layers", "Can you name the sound behind each layer?|Do you have at least 3 layers at once?|Does something "
     "change every few bars?|Would a stranger guess the source?",
     "A check students can use on each other's work. These are the kit's own questions, drawn from my goals and my fourth tip: three "
     "distinct layers, effects and automation for interest, and transformation. If a student cannot name the sound behind a layer, send "
     "them back to the Sound log. Class 5 is a full working day with no new slide."),
    (6, "steps", "Steps 5 and 6: mix, finalize", "Apply EQ, effects and automation|Balance levels and add polish|Bounce your track|Prepare "
     "your presentation",
     "Class 6. Steps 5 and 6 of the project sheet, shortened to fit the slide. Step 5: mix, applying EQ, effects and automation, balancing "
     "levels and adding polish. Step 6: finalize, bounce your track and prepare your presentation. A found sound can be harsh or boomy "
     "until it is EQed, so listen layer by layer. Zip the .logicx in Finder (Control-click, Compress). Students also write their three "
     "Padlet questions today."),
    (6, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Found Sound|At least 5 source sounds "
     "used|Padlet post with your 3 questions|Answer 2 questions on classmates’ posts",
     "The submission checklist from the project sheet, shortened to fit the slide. Show where students upload (your class page) and where "
     "the Padlet board is. Check that the Sound log shows at least five source sounds recorded and used."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play your piece|Name the sounds you started with|Your Padlet post: 3 questions about your project|"
     "Answer at least 2 of each classmate’s 3",
     "Class 7, presentations with Padlet Q and A. Step 7 of the project sheet, shortened to fit the slide: create your own Padlet post with "
     "3 questions you want classmates to answer, present to the class, and during classmates' presentations answer at least 2 of their 3 "
     "questions. Ask each student to name the sounds they started with before they play the piece, then let the class guess."),
    (7, "closer", "One last thing…", "You listened closely.|You recorded the world.|You built instruments from it.|Now it plays.",
     "Close with what my teacher notes say this project does: it builds recording skills, Quick Sampler proficiency and sound design "
     "thinking, and it teaches students that music can come from anywhere, not just preset libraries."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("example", "Worked example", "an invented piece on paper"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 5, 8, 13, 17]
SHOTS3 = [("modes", "Quick Sampler modes"), ("example", "Worked example"), ("sounds", "Sound log"), ("instruments", "Instrument builder"),
          ("layers", "Layer plan"), ("proj2", "Steps"), ("setup", "Setup"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "changes", "logicref", "modes", "example",
        "sounds", "instruments", "layers", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "example", "proj2", "rubric"]

COVER_A = "Turn sounds into instruments"
COVER_C = "DMP2 · Quick Sampler · sound design · intro slides"
PDF_COVER = dict(a=30, b=50, c=14, art=7.3)
SQ_COVER = dict(a=44, b=150, c=27, art=740, gap=44)
SQ_B_LINES = ["Found", "Sound"]
SQ_SUB = "7 class periods · Quick Sampler · sound design · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Quick Sampler modes, worked example, sound log, layer plan", 28)}
SQ_BANDS = {1: "Record <em>·</em> prep <em>·</em> instruments <em>·</em> layers <em>·</em> present",
            2: "Hook <em>·</em> sound to song <em>·</em> three modes <em>·</em> demo",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, video, songs or examples are included. Students record every sound themselves, so everything in their "
             "pieces is original. For the Class 1 hook, you make a short everyday sound yourself.")
CREDITS = ["Worked example (an invented 45-second piece described on paper), the sound-to-instrument, Quick Sampler modes and "
           "timeline drawings and layouts: original work, Hudson Beat.",
           "No audio, video, lyrics, album art, screenshots, presets or chart data are included. The three suggested resources are named "
           "exactly as the teacher listed them, with no link or content; YouTube is not affiliated with or endorsing this resource. "
           "Padlet is named only as an example of a tool you may already use."]
LOGIC_INTRO = ("Where to find the tools this project uses. Demonstrate them on Classes 1 and 2 (slides 6 and 9) and then let students work. "
               "Names are from current Logic Pro versions; check the labels on yours.")
LOGIC_REF = [("Record audio", "Add an Audio track (Track › New Audio Track), choose the input, arm the track and press Record (R). Use the "
              "microphone at your station, or bring in a phone recording."),
             ("Bring in a phone recording", "Drag the audio file from Finder into the Tracks area, or use File › Import › Audio File. Get the "
              "file from the phone to the Mac the way your school allows (AirDrop, a cable or your class page)."),
             ("Trim and clean up", "Split regions (Command-T), delete what you do not need, and trim to the first and last moments of the "
              "sound. Use fades to remove clicks."),
             ("Normalize", "Double-click the region to open the Audio File Editor and choose Functions › Normalize. Menu names vary by "
              "version; listen before and after."),
             ("Quick Sampler", "Add a Software Instrument track and choose Quick Sampler, or drag an audio region onto an empty Software "
              "Instrument track and choose Quick Sampler. Pick Classic, One Shot or Slice at the top."),
             ("Slice mode", "Choose Slice, then adjust how many slices there are and where they fall. Each slice plays from its own key."),
             ("Effects", "Insert effects on the channel strip: Channel EQ, Compressor, a delay such as Echo, and a reverb such as ChromaVerb "
              "or Space Designer."),
             ("Automation", "Press A to show automation, choose a parameter such as a filter knob or volume, and draw changes over time. "
              "A slowly opening filter keeps a loop from feeling static."),
             ("Layers", "Give each layer its own track (percussion, bass, texture) and name the tracks. Solo each one in turn to check it "
              "earns its place."),
             ("Save versions", "Use File › Save As… with a numbered name before each big change."),
             ("Bounce and zip", "File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and choose "
              "Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; .mp3 or .wav and zipped .logicx submitted", "Padlet post created with my 3 questions",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my piece:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Low-quality audio: the recording tips on the setup page (page @SETUP) and the Sound log (page @SOUNDS).</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Confusing Quick Sampler: the modes page (page @MODES), slide 9 and the Instrument builder (page @INSTRUMENTS).</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Auditioning forever: the Layer plan (page @LAYERS) gives every instrument a job.</li>'
    '<li style="font-size:10.8pt;margin-bottom:0">Length: the worked example (page @EXAMPLE) shows 45 seconds with three layers.</li></ul></div>')
TN1_SIZE = 15
PROJ_SIZE = 14.2
VOCAB_GAP = 9
LOGIC_SIZE = 10.4
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example", "How to use, overview, setup, pacing, teacher notes, what changed, Logic quick "
              "reference, Quick Sampler modes, worked example"),
             ("Student pages", "sounds", "reflect", "Sound log, Instrument builder, Layer plan, project sheet (3 pages), "
              "rubric, vocabulary, feedback planner, reflection"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period sound design project for high school music '
             f'technology. Each student records at least five everyday sounds, trims and normalizes them in Logic, turns them into playable '
             f'instruments with Quick Sampler, and composes a 30–60 second piece with at least three layers (percussion, bass, texture), '
             f'built entirely from those found sounds. It is an open-ended project from my Digital Music Production 2 course (focus: '
             f'sound design), and the projects in that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Practice the Class 1 demo: record, trim, normalize and play one sound in Quick Sampler (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("sounds")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Class 5 is a working day with no new slide. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}: a bank of sounds to use alongside their own (page {D.IX("setup")} lists ten to record), or all-original sources and a 90-second piece.</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Recording:</b> a phone or the microphone at each station; students can also record at home.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students record the '
             f'world around them, turn it into instruments and play a piece that no preset library could have made.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:14pt;line-height:1.55">One 30–60 second piece composed entirely from found sounds: at least five original '
             f'recordings, trimmed and normalized, turned into playable instruments in Quick Sampler, arranged in at least three distinct '
             f'layers, with effects and automation. They hand in a bounced .mp3 or .wav and the zipped .logicx project, plus a Padlet post '
             f'with three feedback questions, then play the piece and present it.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:14pt;line-height:1.55">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:12pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:13pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.6pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: record and demo, edit and build, three working days, mix, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: audio recording and editing, Quick Sampler, effects, automation, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a phone or microphone to record with, a feedback board, and speakers if you can</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:12pt">Students should already '
             f'know how to open a project, record and trim audio, add effects, and save, bounce and zip in Logic. Quick Sampler is taught in '
             f'this project (page {D.IX("modes")}); the quick reference (page {D.IX("logicref")}) shows where each tool lives.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Open-ended", inner, n, key="overview")


def setup_page(n, wm=False):
    ideas = ("a pen click · a zipper · a drawer · a stapler · a door closing · a water bottle · a chair scrape · keys · a book closing · "
             "a locker · a faucet · footsteps")
    inner = (f'<style>.sb p, .sb li {{ font-size: 12.4pt; line-height: 1.48; margin-bottom: 7pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the final listen.</li>'
             f'<li><b>A way to record sound:</b> the microphone at each station, a phone, or another recorder students already use.</li>'
             f'<li><b>A way to move phone recordings to the Mac</b> (AirDrop, a cable, or your class page).</li>'
             f'<li><b>A place to submit</b> an .mp3 or .wav and a zipped .logicx project (your class page).</li>'
             f'<li><b>A feedback board</b> for the three questions (my sheets use Padlet).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("sounds")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:12.4pt;margin-bottom:9pt") for c in [
                 "Practice the demo on slide 6: record, trim, normalize and play one sound in Quick Sampler.",
                 "Check that a student computer can record and play back through headphones.",
                 "Decide where students record: at their desks, around the room, on a short walk with permission, or at home.",
                 "Print the student pages; set up the submission spot and the feedback board."]) +
             f'</div><div class="big sb">'
             f'{D.H2("Clean recordings (my first struggle)", True)}'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Kit suggestions, not part of my sheets</span><ul style="margin:0">'
             f'<li style="font-size:12pt">Get close to the sound and keep the phone still.</li>'
             f'<li style="font-size:12pt">Record in a quiet spot and keep wind and breath off the microphone.</li>'
             f'<li style="font-size:12pt">Record three takes of each sound and keep the best one.</li>'
             f'<li style="font-size:12pt">Record sounds, not songs: music playing from a speaker is someone else’s work.</li>'
             f'<li style="font-size:12pt">Ask permission before recording a person, and keep recordings school-appropriate.</li></ul></div>'
             f'{D.H2("For my Easier variation")}'
             f'<p style="font-size:12pt">My variation is a set of pre-recorded found sounds students can use beside their own. No audio is in '
             f'this kit, so make a small bank in ten minutes with your own phone. Twelve sounds to try (a kit suggestion):</p>'
             f'<div class="box"><p style="margin:0;font-size:11.6pt;line-height:1.5">{ideas}</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.6pt;line-height:1.45">'
             f'Sliced and pitched-down sounds can be much louder than they look. Tell students to start with the headphones low.</p></div>'
             f'</div></div>')
    return D.page("Setup and clean recordings", "SETUP", "Teacher", inner, n, key="setup")


def modes_page(n, wm=False):
    cards = [("Classic", "Plays the sound across the keys like an instrument, and lets you set a loop.", "bass, pads, a hum held under everything"),
             ("One Shot", "Plays the whole sound each time you press a key.", "hits, accents, a crinkle or a slam"),
             ("Slice", "Cuts one recording at its loud moments and puts each slice on its own key.", "a drum kit from one recording")]
    rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in cards)
    inner = (f'<p style="margin:0 0 6pt;font-size:12pt">My second struggle is that Quick Sampler is confusing at first, so I demo all three modes (Classic, One Shot, '
             f'Slice) with a real sound. The pictures show a waveform and the keys it plays on. Names and menus can differ in your version of Logic.</p>'
             f'<div style="width:7.4in;margin:4pt auto 6pt">{D.body_svg(modes_body(1250, "page modes", 26, 19, 16))}</div>'
             f'{D.H2("Which mode for which job", True)}'
             f'<table class="t" style="font-size:12.6pt;line-height:1.55"><tr><th style="width:15%">Mode</th><th>What it does</th><th style="width:34%">Try it for</th></tr>{rows}</table>'
             f'<div class="cols" style="gap:12pt"><div class="box acc-b"><span class="k">Kit suggestions, not part of my sheets</span>'
             f'<p style="margin:0;font-size:12.4pt;line-height:1.5">Slice mode is my tip 2: one recording becomes a whole kit. Try Classic for '
             f'bass by playing a pitched-down sound low on the keyboard. If a slice sounds wrong, move its edge to the start of the sound.</p></div>'
             f'<div class="box"><span class="k">Try this in Class 2</span><p style="margin:0;font-size:12.4pt;line-height:1.5">Give each pair one '
             f'recording and ask them to play it in all three modes, then tell the class which mode they would use for percussion, bass and '
             f'texture, and why.</p></div></div>'
             f'<div class="box" style="margin-top:10pt"><span class="k">Check your version</span><p style="margin:0;font-size:12.4pt;line-height:1.5">'
             f'Quick Sampler is part of recent versions of Logic Pro. Open it with one of your own recordings before Class 1 and check that '
             f'the three modes are where this page says.</p></div>')
    return D.page("Quick Sampler modes", "MODES", "Teacher + student", inner, n, key="modes")


def example_page(n, wm=False):
    sec = ", ".join(f"{nm} {mmss(a)}–{mmss(b)}" for nm, a, b in SECTIONS)
    rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>" for a, b, c, d, e in SOUND_ROWS)
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt">An <b>invented piece, “{PIECE}”, described on paper</b>: no audio is included, '
             f'so the numbers are easy to check. Students’ pieces will differ.</p>'
             f'{D.H2("1 · The five sounds", True)}'
             f'<table class="t" style="font-size:9.8pt;line-height:1.28"><tr><th style="width:17%">Sound</th><th style="width:17%">Recorded with</th>'
             f'<th style="width:19%">Quick Sampler</th><th style="width:12%">Layer</th><th>What it does</th></tr>{rows}</table>'
             f'{D.H2("2 · The plan: 45 seconds")}<div style="width:7.2in;margin:1pt auto 3pt">{D.body_svg(plan_body(1250, "page plan", 26, 19))}</div>'
             f'<p class="small" style="margin:0 0 3pt">{sec}. The plan is {TOTAL_S} seconds: inside my 30–60 second requirement.</p>'
             f'<div class="cols" style="gap:12pt"><div class="box"><span class="k">3 · Checking the numbers</span>'
             f'<p style="margin:0;font-size:11pt;line-height:1.42">{BPM} beats per minute is {60 / BPM:g} s a beat, so a bar of 4/4 is {BAR_S:g} s. '
             f'Sections: {" + ".join(str(b) for b in SECTION_BARS)} = {BARS} bars, and {BARS} × {BAR_S:g} s = {TOTAL_S} s. From 0:15 to 0:35 all three '
             f'layers play at once. Five sounds are recorded and all five are used.</p></div>'
             f'<div class="box acc-b"><span class="k">4 · Why it works</span>'
             f'<p style="margin:0;font-size:11pt;line-height:1.42">Each layer has a job: the hum is the room, the taps and slams are the beat, the thud is '
             f'the floor. The filter sweep means the texture changes without adding anything. A listener should struggle to guess the sources.</p></div></div>'
             f'{D.H2("5 · Three Padlet questions (invented)")}'
             f'<p style="font-size:11pt;line-height:1.45;margin:0">{qs}</p>')
    return D.page("Worked example · an invented piece", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def sounds_page(n, wm=False):
    rows = "".join("<tr><td style='height:34pt'></td><td></td><td></td><td></td><td></td></tr>" for _ in range(8))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Steps 1 and 2: record at least 5 sounds using your phone or the microphone at your station, '
             f'then trim, normalize and clean them up in Logic. Name each file the moment you record it. Add the date or a take number if you '
             f'record a sound twice.</p>'
             f'<table class="map"><tr><th style="width:5%">#</th><th style="width:25%">Sound and file name</th><th style="width:20%">Recorded with (phone or mic) and where</th>'
             f'<th style="width:20%">Trimmed and normalized? (tick)</th><th>What it could become (percussion, bass or texture)</th></tr>{rows}</table>'
             f'<div class="fl" style="margin-top:9pt"><b>The strangest sound I recorded, and how:</b><span></span></div>'
             f'<div class="fl"><b>A recording that did not work, and why:</b><span></span></div>'
             f'<div class="box acc-b"><span class="k">Before you move on</span><p style="margin:0;font-size:10.8pt">Do you have at least 5 clean recordings? '
             f'Is every file named and saved in the project folder? Is there at least one sound you could use as percussion, one for bass and one for texture?</p></div>')
    return D.page("Sound log", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="sounds")


def instruments_page(n, wm=False):
    rows = "".join("<tr><td style='height:44pt'></td><td style='font-size:9.6pt'>Classic<br>One Shot<br>Slice</td><td></td><td></td><td></td></tr>"
                   for _ in range(6))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Step 3: import your sounds into Quick Sampler and experiment with playback modes. '
             f'Circle the mode you chose for each instrument. The modes are drawn on page {D.IX("modes")}.</p>'
             f'<table class="map"><tr><th style="width:21%">Sound (from the Sound log)</th><th style="width:13%">Quick Sampler mode (circle one)</th>'
             f'<th style="width:26%">Settings I changed (loop, pitch, start and end, envelope, slices)</th>'
             f'<th style="width:14%">Layer</th><th>How it sounds now</th></tr>{rows}</table>'
             f'<div class="fl" style="margin-top:9pt"><b>The instrument that surprised me most:</b><span></span></div>'
             f'<div class="fl"><b>Which mode did I use the most, and why?</b><span></span></div>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">Before you start composing</span>'
             + "".join(D.chk(c, 12, "font-size:10.8pt;margin-bottom:3pt") for c in [
                 "I have at least 3 playable instruments",
                 "I tried Slice on at least one recording",
                 "I can play each instrument on the keyboard",
                 "A stranger could not easily guess where the sounds came from"]) + '</div>')
    return D.page("Instrument builder", "STUDENT", "Class 2", inner, n, wm, name=True, key="instruments")


def layers_page(n, wm=False):
    rows = "".join("<tr><td style='height:44pt'></td><td></td><td></td><td></td><td></td></tr>" for _ in range(5))
    inner = (f'<div class="fl"><b>Length check: my piece will be</b><span style="flex:0 0 0.9in"></span><b>seconds (must be 30–60).  Tempo:</b>'
             f'<span style="flex:0 0 0.8in"></span></div>'
             f'<p style="margin:2pt 0 5pt;font-size:10.8pt">Step 4: use your custom instruments to build a short piece with at least 3 layers (for example '
             f'percussion, bass, texture). Plan the sections, then say which instrument plays each layer. Density matters more than length.</p>'
             f'<table class="map"><tr><th style="width:13%">Section and time</th><th style="width:20%">Percussion layer</th><th style="width:20%">Bass layer</th>'
             f'<th style="width:20%">Texture layer</th><th>Effects and automation</th></tr>{rows}</table>'
             f'<div class="fl" style="margin-top:8pt"><b>What I automate, and where:</b><span></span></div>'
             f'<div class="fl"><b>The moment a listener will notice the change:</b><span></span></div>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">Check your layers</span>'
             + "".join(D.chk(c, 12, "font-size:10.8pt;margin-bottom:3pt") for c in [
                 "I have at least 3 distinct layers playing together",
                 "I can name the found sound behind every layer",
                 "The piece changes every few bars, not just once",
                 "Every instrument I built has a job, or I cut it"]) + '</div>'
             f'<div class="fl" style="margin-top:6pt"><b>Something I will change after a classmate listens:</b><span></span></div>')
    return D.page("Layer plan", "STUDENT", "Classes 3–5", inner, n, wm, name=True, key="layers")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "modes": modes_page, "example": example_page,
         "sounds": sounds_page, "instruments": instruments_page, "layers": layers_page}


# ================================================================ content checks (example arithmetic, owner text, no audio)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 5), reqs=(REQS, 6), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 3))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp} (the owner's count)")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is the owner's /25, levels 1-5")
    if [c for c, _ in RUBRIC] != ["Creativity & Originality", "Technical Skill / DAW Use", "Composition & Structure",
                                  "Sound Design & Mix Quality", "Documentation & Presentation"]:
        errs.append("rubric categories must be the owner's, in order")
    if FILE_NAME not in CHECK[2] or "Found Sound" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    if "30–60 seconds" not in REQS[5] or "at least 5" not in REQS[0] or "at least 3" not in REQS[3]:
        errs.append("requirements: 5 samples, 3 layers, 30-60 seconds")
    # the worked example adds up
    if BAR_S != 2.5 or BARS * BAR_S != TOTAL_S or sum(SECTION_BARS) != BARS:
        errs.append("96 BPM: 2.5 s per bar, 18 bars, 45 s")
    if not 30 <= TOTAL_S <= 60:
        errs.append("example length must be 30-60 s")
    if SECTIONS[0][1] != 0 or SECTIONS[-1][2] != TOTAL_S or any(b != c for (_, _, b), (_, c, _) in zip(SECTIONS, SECTIONS[1:])):
        errs.append("sections must tile 0-45 seconds")
    if [round((b - a) / BAR_S) for _, a, b in SECTIONS] != SECTION_BARS:
        errs.append("section lengths must match their bars")
    full = SECTIONS[2]
    for lane in ("Percussion", "Bass", "Texture"):
        if not any(a <= full[1] and b >= full[2] for a, b in SPANS[lane]):
            errs.append(f"{lane} must play through the whole Full section (three layers at once)")
    if any(not 0 <= a < b <= TOTAL_S for sp in SPANS.values() for a, b in sp):
        errs.append("layer spans inside the piece")
    if len(SOUND_ROWS) != 5 or {r[3] for r in SOUND_ROWS} != {"Percussion", "Bass", "Texture"}:
        errs.append("five sounds covering percussion, bass and texture")
    if [t for t, _ in FILTER] != sorted(t for t, _ in FILTER) or any(not 0 <= v <= 100 for _, v in FILTER) or FILTER[-1][0] != TOTAL_S:
        errs.append("filter automation: times in order, 0-100, ending at 45 s")
    if len(QUESTIONS) != 3:
        errs.append("three Padlet questions")
    if len(BASS_NOTES) < 8:
        errs.append("a bass note for each bar of the Full section")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    txt = " ".join(flat)
    for need in ("No audio, video, songs or examples are included", "invented piece, “Passing Period”",
                 "Your Name – Found Sound", "Final Grade = Average of Student + Teacher", "Quick Sampler"):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up:
        errs.append("UPLOAD.md: must say no audio is included and record the open questions")
    for i in (2, 6, 9, 10, 11, 14, 15, 17):   # slides that shorten the owner's wording must say so
        if "shortened" not in notes[i].lower() and "shortens" not in notes[i].lower():
            errs.append(f"deck slide {i + 1} notes: must say the owner's wording is shortened")
    ch = flat[D.IX("changes") - 1]
    for s in ("slide 3", "slide 7", "slide 10", "slide 11", "slide 12", "slide 15", "slide 16", "slide 18"):
        if s not in ch:
            errs.append(f"'What changed' page must list {s}")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or any("Layer plan" in g or "Sound log" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in ("Billie", "Beatles", "Spotify", "Daft", "Skrillex", "Disney", "Minecraft", "Mario", "Taylor", "Nirvana", "Radiohead"):
        if banned in alldeck or banned in txt:
            errs.append(f"must not name songs, artists or services beyond the owner's ({banned})")
    return errs


def check_summary():
    return (f"The invented piece is {TOTAL_S} s ({BPM} BPM, {BARS} bars of {BAR_S:g} s; sections {'+'.join(map(str, SECTION_BARS))} bars) with "
            f"three layers together from 0:15 to 0:35; "
            f"the owner's lists counted (4 goals, 5 terms, 6 requirements, 7 steps, 4 tips, 6 checklist items, 4 struggles, 3 resources); "
            f"{len(CHANGES)} wording changes disclosed; no audio included; grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
