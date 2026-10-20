#!/usr/bin/env python3
"""DMP2 project: Pattern Prodigy (TpT 024): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Pattern Prodigy > "Pattern Prodigy - Project Sheet & Rubric" (rubric 5 categories scored 1-5, /25, final
grade = average of student and teacher scores), TEACHER NOTES > "Pattern Prodigy - Teacher Notes" (7 class periods), and the project's
entry on "DMP2 - Project Menu" (the June 2026 menu; owner, 17 Oct 2026: the June entry may be quoted). These three set the project
text, steps, rubric and pacing (owner rule, 17 Oct 2026). The older Projects > Pattern Prodigy folder holds a 2025 .docx outline, a
doc of YouTube tutorial links and two screen-recorded tutorial videos made by the owner (15 MB and 38 MB); the outline is not a source.

LEFT OUT ON PURPOSE: the two tutorial videos (the Teacher Notes list the tutorials as YouTube items, so the kit keeps them as listed
and includes no video or link; whether to add the owner's own videos is an open question in UPLOAD.md).
NO AUDIO IS INCLUDED. The Easier variation's pre-built drum pattern is a Logic project that the Drive does not hold, so the kit lays it
out as a 16-step chart on paper (page "starter"). The worked example is an invented 50-second piece ("Night Shift") described on
paper: four sections, five layers and four automation lanes, with every step of its patterns written out. Every picture (grid hero,
steps, pattern grid, features, arrangement map) is drawn in code.
The sheet has no reflection task (the rubric only mentions reflection), so the shared Reflection element stays ON (default).
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "pattern-prodigy"
TITLE = "Pattern Prodigy"
ACCENT = "#B3237A"          # this product's single accent: step-light magenta (008 red ... 022 lake cyan, 023 horizon orange)
ACC_LIGHT = "#F2D3E6"
PRICE = "10.00"
CLASSES = 7
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-023).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "Pattern Prodigy in Logic Pro | Step Sequencer Beat Project | High School"
DESC_START = "Step Sequencer groove project for high school:"
DESC_MUST = ["Pattern Prodigy", "probability", "no audio", "Padlet"]
ZIP_DIR = "Pattern Prodigy - Hudson Beat"
ZIP_DATE = (2026, 10, 20, 12, 0, 0)
TYPE = "Structured Project"
PROJ_LINE = "Digital Music Production | <i>Structured Project</i> | 7 class periods"
DECK_STRAP = "Program a groove that evolves"
BANNED_EXTRA = []

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Structured", "Step Sequencer"
MENU_DESC = "Master Logic’s Step Sequencer with automation, probability, and velocity to build evolving grooves."
OVERVIEW = ("Become a pattern master. Use Logic’s Step Sequencer and Pattern Regions to craft an original groove-driven composition. "
            "Create a 30–60 second piece that evolves over time through layering, automation, and creative use of sequencer features "
            "like probability and velocity.")
GOALS = ["Learn to create and manipulate Pattern Regions for drums, bass, and synths",
         "Use probability, velocity, and step automation to add organic variation",
         "Apply EQ, panning, and plug-ins for a balanced, polished sound",
         "Explore texture and form through pattern layering and evolving loops"]
VOCAB = [("Step Sequencer", "A Logic tool that lets you program rhythms and melodies by toggling steps on a grid"),
         ("Pattern Region", "A region in Logic that contains step sequencer data"),
         ("Probability", "A feature that gives each step a chance of playing or not, adding randomness"),
         ("Velocity", "How hard a note is played — higher velocity = louder and often brighter"),
         ("Automation", "Changing a parameter (volume, filter, pan, etc.) over time to create movement")]
REQS = ["Length: 30–60 seconds",
        "Use at least 3 different Step Sequencer features",
        "Include at least one drum kit, one bass or synth, and one additional element",
        "Demonstrate balance, clarity, and creative use of space in your mix"]
STEPS = ["<b>Explore</b> — Open the Step Sequencer and experiment with basic drum patterns (Pattern grids: page @GRIDS)",
         "<b>Build rhythms</b> — Create your core drum and percussion patterns",
         "<b>Add melodic layers</b> — Program bass and synth patterns that complement your groove",
         "<b>Automate and vary</b> — Use probability, velocity, and automation to make patterns evolve (Feature tracker: page @FEATURES)",
         "<b>Mix and refine</b> — Apply EQ, panning, and plug-ins. Arrange into a cohesive piece. (Arrangement plan: page @ARRANGE; Listen-back sheet: page @REFINE)",
         "<b>Finalize</b> — Bounce your track and prepare your presentation",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["Start with your drums. Once you have a groove that feels good, everything else falls into place.",
        "Probability is your friend — even a small percentage of randomness makes patterns feel more human.",
        "Don’t just stack patterns. Think about how your piece builds and evolves.",
        "Use mute/unmute in the Step Sequencer to create arrangement changes."]
FILE_NAME = "“Your Name – Pattern Prodigy”"
CHECK = ["Bounced .mp3 or .wav uploaded to your class page",
         "Zipped .logicx project file uploaded to your class page",
         f"Files named correctly: {FILE_NAME}",
         "At least 3 Step Sequencer features used",
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
TN_REINFORCES = "Introduces the Step Sequencer workflow. Builds rhythm programming, automation, and arrangement skills."
STRUGGLES = ["Students only use the Step Sequencer for drums. Demo melodic patterns early.",
             "Patterns sound static. Push automation and probability.",
             "Students don’t understand probability. Show a live example on a hi-hat.",
             "The short length makes students rush."]
VAR_EASY = "Provide a pre-built drum pattern as a starting point."
VAR_HARD = "Extend to 90 seconds. Require pattern alternates and 2 types of step automation."
RESOURCES = [("Logic Step Sequencer Getting Started (YouTube)",
              "Kept as I wrote it. No video or link is included. The Logic quick reference (page @LOGICREF) says where each Step Sequencer "
              "control lives, and the Pattern grids (page @GRIDS) give students a place to plan."),
             ("Live Pattern Recording tutorial (YouTube)",
              "Kept as I wrote it. No video is included. Recording a pattern live is one way to fill a grid; the quick reference "
              "(page @LOGICREF) mentions it."),
             ("Step Sequencer for Automation tutorial (YouTube)",
              "Kept as I wrote it. No video is included. The Feature tracker (page @FEATURES) shows what to try and the example "
              "(page @EXAMPLE2) shows the result.")]
TN_NOTE = "Works well for students drawn to electronic, lo-fi, or beat-driven music."
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Creativity &amp; Originality: ask what groove the student was after, then listen for what makes it theirs (my tip: start with "
                "your drums, then build).",
                "Technical Skill: open the project and count the Step Sequencer features against the Feature tracker (page @FEATURES). "
                "Is each one audible?",
                "Composition &amp; Structure: compare the piece with the Arrangement plan (page @ARRANGE). Does it build and evolve, or only stack?",
                "Sound Design &amp; Mix Quality: listen for balance and space (requirement 4). Can you hear each pattern?",
                "Documentation &amp; Presentation: the Feature tracker, the Arrangement plan, the Reflection page (page @REFLECT) and the "
                "Padlet questions are the evidence."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Introduction to Step Sequencer and Pattern Regions. Guided exploration.",
     "do": "Slides 1–7: hook, what the project is, the steps, five words, steps 1 and 2. Hand out the project sheet and the Pattern "
           "grids. Guide the class through a first drum pattern; no audio is included.", "slides": (1, 7),
     "pages": ["grids", "proj1", "proj2", "proj3", "vocab"],
     "deck": "A beat that changes · the steps · five words · explore and build rhythms"},
    {"n": 2, "owner": "<b>Class 2:</b> Build drum/percussion patterns. Begin adding melodic layers.",
     "do": "Slides 8–10: reading a pattern grid, not only drums, step 3. Demo a melodic pattern early (my first struggle). Check "
           "each student has a drum groove.", "slides": (8, 10), "pages": ["features"],
     "deck": "Read a grid · not only drums · add melodic layers"},
    {"n": 3, "owner": "<b>Classes 3–5:</b> Working days — explore automation, probability, variation.",
     "do": "Slides 11–13: four ways to evolve, step 4 and the worked example on paper. Hand out the Arrangement plan. Then work time.",
     "slides": (11, 13), "pages": ["arrange"], "deck": "Working day: four ways to evolve, worked example"},
    {"n": 4, "owner": None, "do": "Slides 14–15: probability is your friend, and mix and refine. Hand out the Listen-back sheet. Then work time.",
     "slides": (14, 15), "pages": ["refine"], "deck": "Working day: probability, mix, refine"},
    {"n": 5, "owner": None, "do": "Full working day: automate, vary, arrange. Ask each student to loop one bar and say which step they would "
     "change next.", "slides": None, "pages": [], "deck": "Working day: explore automation, probability, variation"},
    {"n": 6, "owner": "<b>Class 6:</b> Final mix, bounce. Prepare presentations.",
     "do": "Slides 16–18: bounce, what to turn in, the rubric. Students post their three Padlet questions.", "slides": (16, 18),
     "pages": ["rubric", "present"], "deck": "Bounce · checklist · rubric"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 19–20: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (19, 20), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to show on Class 1</span>'
    '<p style="margin:0;font-size:9.4pt">Put a hi-hat on a grid and give a step a 50% chance (my third struggle). Loop it for a few '
    'bars so the class hears it change. Do the same on a bass row so it is not only for drums.</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:9.4pt">Working days; Class 5 has no new slide. '
    'Circulate with one question: which feature changed the sound you just heard?</p></div></div>')
PACING_SIZE = 9.6

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (checklist items 1 and 2).",
    "Page numbers are added to steps 1, 4 and 5 (the Pattern grids, Feature tracker, Arrangement plan and Listen-back sheet).",
    "My Easier variation (a pre-built drum pattern) is a Logic project, which is not included. It is laid out as a 16-step chart on "
    "paper (page @STARTER) so you can enter it in a few minutes.",
    "My Harder variation (90 seconds, pattern alternates, 2 types of step automation) is laid out on page @STARTER. The sheet does not "
    "say which features count toward “at least 3”; the Feature tracker lists the ones my notes and tips name (page @FEATURES).",
    "My resources are three YouTube tutorials. They are listed as I wrote them; no tutorial, video or link is included.",
    "My pacing guide’s “Classes 3–5” row spans the Class 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 3 shortens my overview and goals, slide 6 shortens "
    "my five vocabulary definitions, slide 7 shortens steps 1 and 2, slide 9 shortens my first struggle and tip 1, slide 10 shortens "
    "step 3 and requirement 3, slide 12 shortens step 4 and requirement 2, slide 14 shortens tips 2 and 3 and my second and third "
    "struggles, slide 15 shortens step 5, tip 4 and the Harder variation, slide 16 shortens steps 6 and 7, slide 17 shortens the "
    "submission checklist, and slide 19 shortens step 7.",
]
CHANGES_MUST_MENTION = ["your class page", "Page numbers", "pre-built drum pattern", "Classes 3–5", "Layout only", "intro deck shortens"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the overview, goals, five vocabulary terms, four requirements, "
        "steps (apart from the page numbers), tips, checklist (apart from the class page) and file name (“Your Name – Pattern "
        "Prodigy”), the /25 rubric, what the project reinforces, my four struggles, the variations, my closing note and the "
        "project menu entry on page @OVERVIEW. No rubric row is added and the requirements are unchanged.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: the how-to, overview and setup pages, the teacher "
                "moves in the pacing guide, the grading suggestions, the suggested list of features that count (a kit suggestion on "
                "page @SETUP), the Logic quick reference, the pre-built pattern chart and Harder variation page, the worked example (an "
                "invented 50-second piece, its patterns, sections, layers and lanes, on paper, not audio), the Pattern grids, Feature "
                "tracker, Arrangement plan and Listen-back sheet, the vocabulary and presentation pages and the intro deck. None adds a "
                "requirement or a rubric row.")

# ================================================================ the worked example (Hudson Beat original: an invented piece on paper)
PIECE = "Night Shift"
BPM = 96
BAR_S = 240 / BPM            # one 4/4 bar in seconds: 2.5
TOTAL_BARS = 20
TOTAL_S = 50
SECTIONS = [("Intro", 0, 10), ("Groove", 10, 30), ("Build", 30, 40), ("Outro", 40, 50)]
LAYERS = [("Kick & snare", 0, 50, "a drum kit pattern region, 16 steps, looped"),
          ("Hi-hat", 5, 50, "the hat row, unmuted at bar 3, with ghost steps on probability"),
          ("Bass", 10, 45, "a bass pattern region from bar 5 to bar 18"),
          ("Synth arp", 20, 45, "a synth pattern region from bar 9 to bar 18"),
          ("Fill pattern B", 30, 40, "a second drum pattern for the Build, bars 13–16")]
AUTO = [("Synth arp", "filter cutoff", [(20, .15), (30, .4), (40, .95), (45, .5)]),
        ("Synth arp", "panning", [(20, .5), (26, .1), (34, .9), (45, .5)]),
        ("Bass", "volume", [(10, .4), (25, .6), (35, .95), (45, .4)]),
        ("Hi-hat", "reverb send", [(5, .1), (30, .2), (40, .8), (50, .15)])]
# one bar of 16 steps: step -> (velocity 1-127, probability %)
KICK = {1: (110, 100), 7: (90, 100), 11: (100, 100)}
SNARE = {5: (105, 100), 13: (105, 100)}
HAT = {**{s: (100 if s % 4 == 1 else 70, 100) for s in range(1, 17, 2)}, **{s: (45, 25) for s in range(2, 17, 2)}}
BASS = {1: ("C2", 105), 4: ("C2", 85), 7: ("Eb2", 95), 11: ("G1", 100), 14: ("Bb1", 90)}
ARP = {s: (n, 80) for s, n in zip(range(1, 17, 2), ["C4", "Eb4", "G4", "Bb4", "C5", "Bb4", "G4", "Eb4"])}
ARP_CUTOFF = [15, 20, 25, 32, 40, 48, 56, 64, 70, 76, 82, 88, 92, 95, 96, 97]   # step automation: one cutoff value per step
CHORD = {"C", "Eb", "G", "Bb"}                                                    # C minor 7: every pitch in the example is one of these
FEATURES = [("Probability", "the hi-hat’s even steps play 25% of the time; raised by hand to 60% in the Build"),
            ("Velocity", "hat accents on steps 1, 5, 9 and 13 (100) over softer ones (70); kick and snare at about 90 to 110"),
            ("Step automation", "the synth arp’s filter cutoff has its own value on every step, rising from 15 to 97"),
            ("Mute / unmute", "the hat row is unmuted at bar 3; the snare row is muted at bar 19"),
            ("Pattern alternate", "a second drum pattern, B, plays in bars 13–16 and then the first returns")]
WEAK = "I will make a beat with drums and a bass."
STRONG = ("I am making “Night Shift”, a 50-second groove at 96 BPM. It opens with kick and snare, and the hi-hat row is unmuted at bar 3. "
          "A bass pattern arrives at bar 5 and a synth arp at bar 9. I will use five Step Sequencer features: probability on the hat’s "
          "even steps, velocity accents, a cutoff on every step of the arp, mute and unmute, and an alternate drum pattern for the "
          "Build. Four automation lanes keep it moving, and in the last four bars it thins out.")
SECTION_NOTES = [("Intro", "bars 1–4", "kick and snare; the hat row is unmuted at bar 3"),
                 ("Groove", "bars 5–12", "the bass joins at bar 5 and the arp at bar 9; the arp’s cutoff begins to open"),
                 ("Build", "bars 13–16", "drum pattern B plays; hat ghost steps rise to 60%; the cutoff opens fully"),
                 ("Outro", "bars 17–20", "pattern A returns; the bass and arp leave at bar 19, the snare row is muted, the reverb falls")]
QUESTIONS = ["Which pattern did you hear change first?",
             "Where did the hi-hat sound most alive, and why?",
             "What would you take out to make the Build hit harder?"]


def mmss(t):
    return f"{int(t) // 60}:{int(round(t)) % 60:02d}"


def bars_for(sec, bpm):
    return sec * bpm / 240


# ================================================================ drawings (original, code-drawn: black + accent only)
def hero_body():
    W, H = 1100, 470
    out = []
    cw, gap, x0, y0 = 54, 8, 54, 70
    pat = ["x...x...x..x....", "....x.......x...", "x.x.x.x.x.x.x.x.", "x..x..x...x..x.."]
    for r, row in enumerate(pat):
        for c, ch in enumerate(row):
            x = x0 + c * (cw + gap)
            y = y0 + r * (cw + gap)
            if ch == "x":
                out.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{cw}" rx="9" fill="{ACCENT if (c // 4 + r) % 2 == 0 else "#000"}"/>')
            else:
                out.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{cw}" rx="9" fill="#fff" stroke="#000" stroke-width="3" opacity=".5"/>')
    px = x0 + 9 * (cw + gap) + cw / 2
    out.append(f'<polygon points="{px - 20},28 {px + 20},28 {px},60" fill="#000"/>')
    out.append(f'<line x1="{px}" y1="60" x2="{px}" y2="{y0 + 4 * (cw + gap)}" stroke="#000" stroke-width="4" stroke-dasharray="3 9" stroke-linecap="round"/>')
    base = y0 + 4 * (cw + gap) + 30
    pts = " ".join(f"{x0 + c * (cw + gap) + cw / 2:.1f},{base + 100 - (ARP_CUTOFF[c] / 100) * 90:.1f}" for c in range(16))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{ACCENT}" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/>')
    out.append(f'<line x1="{x0}" y1="{base + 104}" x2="{x0 + 16 * (cw + gap) - gap}" y2="{base + 104}" stroke="#000" stroke-width="8" stroke-linecap="round"/>')
    return "".join(out), W, base + 116


def cards_body(items, cap, W=1600, name="cards", fs=30, cs=22, arrows=True):
    n = len(items)
    gap = 74 if arrows else 40
    pw = (W - (n - 1) * gap) / n
    bh = 190
    out = []
    for k, (h, s) in enumerate(items):
        x0 = k * (pw + gap)
        out.append(f'<rect x="{x0:.1f}" y="4" width="{pw:.1f}" height="{bh}" rx="12" fill="{"#000" if k % 2 == 0 else ACCENT}"/>')
        out.append(D.t_(x0 + pw / 2, 4 + bh / 2 - 6, h.upper(), fs, 700, fill_="#fff"))
        D.lab(name + " heads", h.upper(), fs, pw - 30)
        out.append(D.t_(x0 + pw / 2, 4 + bh / 2 + 38, s, cs, 500, fill_="#fff"))
        D.lab(name + " subs", s, cs, pw - 30)
        out.append(D.t_(x0 + 24, 4 + 40, str(k + 1), 28, 700, anchor="start", fill_="#fff"))
        if arrows and k < n - 1:
            ax = x0 + pw + 10
            ay = 4 + bh / 2
            out.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{ax + gap - 36:.1f}" y2="{ay:.1f}" stroke="#000" stroke-width="6" stroke-linecap="round"/>')
            out.append(f'<polygon points="{ax + gap - 16:.1f},{ay:.1f} {ax + gap - 40:.1f},{ay - 15:.1f} {ax + gap - 40:.1f},{ay + 15:.1f}" fill="#000"/>')
    out.append(D.t_(W / 2, bh + 56, cap, cs + 2, 500))
    D.lab(name + " cap", cap, cs + 2, W - 20)
    return "".join(out), W, bh + 72


def cycle_body(W=1600, name="cycle pic", fs=30, cs=22):
    return cards_body([("Explore", "basic drums"), ("Rhythms", "drums · percussion"), ("Melody", "bass · synth"),
                       ("Evolve", "vary the loops"), ("Refine", "mix · arrange")],
                      "Then finalize: bounce, present and get feedback", W, name, fs, cs, True)


def grid_body(W=1600, name="grid pic", fs=26, cs=20):
    """The example's one-bar patterns on a 16-step grid. Fill = velocity; dashed = a step that may not play (probability)."""
    lx = 210
    cw = (W - lx - 4) / 16
    rh, gp = 64, 10
    rows = [("KICK", KICK, None), ("SNARE", SNARE, None), ("HI-HAT", HAT, None), ("BASS", None, BASS), ("SYNTH ARP", None, ARP)]
    out = []
    for c in range(16):
        out.append(D.t_(lx + c * cw + cw / 2, 26, str(c + 1), cs, 700 if c % 4 == 0 else 500, fill_=ACCENT if c % 4 == 0 else "#000"))
    for r, (lab_, drum, mel) in enumerate(rows):
        y = 40 + r * (rh + gp)
        out.append(D.t_(lx - 18, y + rh / 2 + fs * .34, lab_, fs, 700, anchor="end"))
        D.lab(name + " rows", lab_, fs, lx - 28)
        for c in range(16):
            s = c + 1
            x = lx + c * cw
            on = (drum or mel).get(s)
            if mel:
                v = on[1] if on else 0
            else:
                v = on[0] if on else 0
            ghost = bool(drum) and on and on[1] < 100
            if on and not ghost:
                shade = "#000" if v >= 100 else ACCENT
                out.append(f'<rect x="{x + 3:.1f}" y="{y}" width="{cw - 6:.1f}" height="{rh}" rx="8" fill="{shade}"/>')
                if mel:
                    out.append(D.t_(x + cw / 2, y + rh / 2 + 8, on[0], cs, 700, fill_="#fff"))
                    D.lab(name + " notes", on[0], cs, cw - 14)
            elif ghost:
                out.append(f'<rect x="{x + 3:.1f}" y="{y}" width="{cw - 6:.1f}" height="{rh}" rx="8" fill="{ACC_LIGHT}" stroke="{ACCENT}" stroke-width="3" stroke-dasharray="8 6"/>')
            else:
                out.append(f'<rect x="{x + 3:.1f}" y="{y}" width="{cw - 6:.1f}" height="{rh}" rx="8" fill="#fff" stroke="#000" stroke-width="1.6" opacity=".55"/>')
    yb = 40 + len(rows) * (rh + gp) + 6
    ky = yb + 24
    out.append(f'<rect x="{lx}" y="{ky - 18}" width="30" height="24" rx="5" fill="#000"/>')
    out.append(D.t_(lx + 42, ky + 2, "loud (velocity 100+)", cs, 500, anchor="start"))
    out.append(f'<rect x="{lx + 330}" y="{ky - 18}" width="30" height="24" rx="5" fill="{ACCENT}"/>')
    out.append(D.t_(lx + 372, ky + 2, "softer", cs, 500, anchor="start"))
    out.append(f'<rect x="{lx + 520}" y="{ky - 18}" width="30" height="24" rx="5" fill="{ACC_LIGHT}" stroke="{ACCENT}" stroke-width="3" stroke-dasharray="6 4"/>')
    out.append(D.t_(lx + 562, ky + 2, "may not play (25% chance)", cs, 500, anchor="start"))
    for t_ in ("loud (velocity 100+)", "softer", "may not play (25% chance)"):
        D.lab(name + " key", t_, cs, 300)
    return "".join(out), W, ky + 18


def features_body(W=1600, name="features pic", fs=30, cs=22):
    rows = [("Probability", "a chance a step plays"), ("Velocity", "how hard each step hits"),
            ("Step automation", "a value for every step"), ("Mute / unmute", "take a row out, bring it back")]
    gx, rh, gp = 360, 110, 18
    out = []
    for i, (h, s) in enumerate(rows):
        y = 4 + i * (rh + gp)
        out.append(D.t_(gx - 24, y + rh / 2 + fs * .36 - 14, h.upper(), fs, 700, anchor="end"))
        D.lab(name + " heads", h.upper(), fs, gx - 34)
        out.append(D.t_(gx - 24, y + rh / 2 + fs * .36 + 20, s, cs - 2, 500, anchor="end"))
        D.lab(name + " subs", s, cs - 2, gx - 34)
        out.append(f'<rect x="{gx}" y="{y}" width="{W - gx - 4}" height="{rh}" rx="10" fill="#fff" stroke="#000" stroke-width="3"/>')
        n, cw = 16, (W - gx - 4 - 60) / 16
        for c in range(n):
            x = gx + 30 + c * cw
            if i == 0:
                solid = c % 4 in (0, 2)
                out.append(f'<rect x="{x + 3:.1f}" y="{y + 20}" width="{cw - 6:.1f}" height="{rh - 40}" rx="7" fill="{"#000" if solid else ACC_LIGHT}"'
                           f'{"" if solid else f" stroke=\"{ACCENT}\" stroke-width=\"3\" stroke-dasharray=\"7 5\""}/>')
            elif i == 1:
                v = [1, .45, .7, .45][c % 4]
                hh = v * (rh - 30)
                out.append(f'<rect x="{x + 6:.1f}" y="{y + rh - 12 - hh:.1f}" width="{cw - 12:.1f}" height="{hh:.1f}" rx="4" fill="{ACCENT if v == 1 else "#000"}"/>')
            elif i == 2:
                pass
            else:
                on = (c // 4) % 2 == 0
                out.append(f'<rect x="{x + 3:.1f}" y="{y + 20}" width="{cw - 6:.1f}" height="{rh - 40}" rx="7" fill="{ACCENT if on else "#fff"}"'
                           f'{"" if on else " stroke=\"#000\" stroke-width=\"2\" opacity=\".55\""}/>')
        if i == 2:
            pts = [(gx + 30 + c * cw + cw / 2, y + rh - 16 - (ARP_CUTOFF[c] / 100) * (rh - 32)) for c in range(16)]
            out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{ACCENT}" stroke-width="8" stroke-linejoin="round"/>')
            for a, b in pts:
                out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="7" fill="#000"/>')
    hh = 4 + 4 * (rh + gp)
    out.append(D.t_(W / 2, hh + 24, "Each one is a setting on the steps you already have", cs + 2, 500))
    D.lab(name + " cap", "Each one is a setting on the steps you already have", cs + 2, W - 20)
    return "".join(out), W, hh + 40


def map_body(W=1600, name="map", fs=24, ts=20):
    gx = 250
    pwid = W - gx - 16

    def X(t):
        return gx + pwid * t / TOTAL_S

    out = []
    sh = 54
    shade = {"Intro": "#4a4a4a", "Groove": "#000", "Build": ACCENT, "Outro": "#4a4a4a"}
    for nm, a, b in SECTIONS:
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{shade[nm]}"/>')
        out.append(D.t_((X(a) + X(b)) / 2, sh / 2 + fs * .3 + 2, nm.upper(), fs - 4, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 4, X(b) - X(a) - 10)
    lh, lg = 34, 7
    y0 = sh + 14
    out.append(D.t_(gx - 14, y0 + 6, "LAYERS", fs - 6, 700, anchor="end", fill_=ACCENT))
    fills = {"Kick & snare": "#4a4a4a", "Hi-hat": "#7a7a7a", "Bass": ACC_LIGHT, "Synth arp": "#bdbdbd", "Fill pattern B": ACC_LIGHT}
    for i, (nm, a, b, _d) in enumerate(LAYERS):
        yy = y0 + 16 + i * (lh + lg)
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, nm.upper(), 20, 700, anchor="end"))
        D.lab(name + " lanes", nm.upper(), 20, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        edge = ACCENT if nm in ("Bass", "Fill pattern B") else "#000"
        out.append(f'<rect x="{X(a):.1f}" y="{yy + 5}" width="{X(b) - X(a):.1f}" height="{lh - 10}" rx="6" fill="{fills[nm]}" stroke="{edge}" stroke-width="2"/>')
    ay0 = y0 + 16 + len(LAYERS) * (lh + lg) + 10
    out.append(D.t_(gx - 14, ay0 + 6, "AUTOMATION", fs - 6, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " lanes", "AUTOMATION", fs - 6, gx - 24)
    for i, (ly, par, pts) in enumerate(AUTO):
        yy = ay0 + 16 + i * (lh + lg + 6)
        lbl = f"{ly} · {par}".upper()
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, lbl, 18, 700, anchor="end"))
        D.lab(name + " lanes", lbl, 18, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh + 6}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        xy = [(X(t), yy + lh + 2 - v * (lh - 2)) for t, v in pts]
        out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in xy)}" fill="none" stroke="{ACCENT}" stroke-width="4" stroke-linejoin="round"/>')
        for a, b in xy:
            out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="4.5" fill="#000"/>')
    ty = ay0 + 16 + len(AUTO) * (lh + lg + 6) + 2
    for t in (0, 10, 30, 40, 50):
        lbl = mmss(t)
        anc = "start" if t == 0 else ("end" if t == TOTAL_S else "middle")
        out.append(f'<line x1="{X(t):.1f}" y1="{ty - 6}" x2="{X(t):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(t) + (2 if t == 0 else (-2 if t == TOTAL_S else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 80)
    return "".join(out), W, ty + ts + 22


DRAWINGS = {"hero": lambda: D.stack([hero_body()], 40), "cycle": lambda: cycle_body(1600), "grid": lambda: grid_body(1600),
            "features": lambda: features_body(1600), "arrange": lambda: map_body(1600, "arrange pic")}
DRAWING_PX = {"hero": 1900, "cycle": 2000, "grid": 2000, "features": 2000, "arrange": 2000}
SIDE = {"cycle": ["Explore basic drum patterns", "Build drum and percussion patterns", "Add bass and synth patterns",
                  "Evolve them, then mix and refine"],
        "grid": ["One bar, 16 steps", "Darker means louder", "Dashed steps may not play", "Drums, bass and a synth arp"],
        "features": ["Probability: a chance to play", "Velocity: how hard", "Step automation: a value per step",
                     "Mute / unmute: arrangement changes"],
        "arrange": ["An invented 50-second piece, on paper", "Four sections you can name", "Five layers that join and leave",
                    "Four automation lanes, none flat"]}


def label_extras():
    map_body(1250, "page arrange", 24, 20)
    cycle_body(1250, "page cycle", 28, 20)
    grid_body(1250, "page grid", 26, 20)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Pattern Prodigy", "Program a groove that evolves.",
     "Class 1, the first minute. No audio is included in this deck. Open with my overview: become a pattern master. Use Logic's Step "
     "Sequencer and Pattern Regions to craft an original groove-driven composition, a 30 to 60 second piece that evolves over time "
     "through layering, automation and creative use of sequencer features like probability and velocity."),
    (1, "listen", "Think: a beat that changes", "Tap it out · Think, then share|Teacher: tap a simple beat on a desk, then change one "
     "tap each time round. No audio is needed.|What makes a groove feel like a groove?|What happens if a machine plays the exact same "
     "bar forever?|How could a machine sound as if a person is playing?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker; tap a beat on a desk and change one tap "
     "each time round, so students hear that small changes keep a loop alive. No one else's music is included in this kit. This sets up "
     "my tips: probability is your friend, and do not just stack patterns."),
    (1, "bullets", "What is Pattern Prodigy?", "Build an original loop-based groove|Step Sequencer and Pattern Regions|Probability, "
     "velocity and automation|30–60 seconds that evolves over time",
     "My overview and goals, shortened to fit the slide. Become a pattern master: use Logic's Step Sequencer and Pattern Regions to "
     "craft an original groove-driven composition of 30 to 60 seconds that evolves over time through layering, automation and creative "
     "use of sequencer features like probability and velocity. My goals add EQ, panning and plug-ins for a polished sound, and texture "
     "and form through pattern layering. Slide 6 introduces the five vocabulary terms."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: introduction to the Step Sequencer and Pattern Regions, with guided "
     "exploration. Class 2: build drum and percussion patterns and begin adding melodic layers. Classes 3 to 5 are working days: "
     "explore automation, probability and variation. Class 6: final mix and bounce, and prepare presentations. Class 7: presentations "
     "with Padlet Q and A peer feedback. Hand out the project sheet now."),
    (1, "pic", "Five steps, then finish", "cycle",
     "Class 1. The first five steps of my project sheet, in order: explore, build rhythms, add melodic layers, automate and vary, mix "
     "and refine. Then students finalize with a bounce and present with Padlet feedback. Point to each box and say roughly when it "
     "happens: exploring and rhythms now, melodic layers in Class 2, variation and refining on the working days. The step names are "
     "mine; the picture and its short labels are the kit's own."),
    (1, "bullets", "Five words to know", "Step Sequencer: toggle steps on a grid|Pattern Region: holds sequencer data|Probability: a "
     "chance a step plays|Velocity: how hard a note is played|Automation: a parameter changing over time",
     "My five vocabulary terms, shortened to fit the slide. Step Sequencer: a Logic tool that lets you program rhythms and melodies by "
     "toggling steps on a grid. Pattern Region: a region in Logic that contains step sequencer data. Probability: a feature that gives "
     "each step a chance of playing or not, adding randomness. Velocity: how hard a note is played; higher velocity is louder and often "
     "brighter. Automation: changing a parameter, such as volume, filter or pan, over time to create movement. The full definitions "
     "are on the vocabulary page."),
    (1, "steps", "Steps 1 and 2: explore, build", "Open the Step Sequencer; try basic drum patterns|Click steps on and off, listen, "
     "change one thing at a time|Create your core drum and percussion patterns|Make a groove that feels good first",
     "Steps 1 and 2 of the project sheet, shortened to fit the slide. Step 1, explore: open the Step Sequencer and experiment with "
     "basic drum patterns. Step 2, build rhythms: create your core drum and percussion patterns. The second and fourth lines are the "
     "kit's own suggestions, not my steps: change one thing at a time so students hear what each change does, and get a groove that "
     "feels good before adding anything, which is my first tip. Guide the class through a first pattern; none is included as audio."),
    (2, "pic", "Reading a pattern grid", "grid",
     "Class 2. A kit picture, not from my sheets: one bar of an invented groove on a 16-step grid, with kick, snare, hi-hat, bass and a "
     "synth arp. Darker steps are louder, which is velocity; a dashed step may not play, which is probability. Ask students to find "
     "where the kick and snare fall and which steps are the hi-hat's ghost steps. The Pattern grids page lets them plan their own."),
    (2, "bullets", "Not only drums", "The Step Sequencer works for bass and synths too|Demo a melodic pattern early|Start with your "
     "drums; the rest follows|Ask: what else could be a row?",
     "My first struggle and first tip, shortened to fit the slide. Students only use the Step Sequencer for drums, so demo melodic "
     "patterns early. Start with your drums: once you have a groove that feels good, everything else falls into place. The last line is "
     "the kit's own question: a bass line, a chord arp or a small effect can each be a row."),
    (2, "steps", "Step 3: add melodic layers", "Program bass and synth patterns that complement your groove|Include a drum kit, a bass "
     "or synth, and one more element|Let the bass follow the kick|Add one pattern at a time, and listen",
     "Step 3 of the project sheet and requirement 3, shortened to fit the slide. Step 3, add melodic layers: program bass and synth "
     "patterns that complement your groove. Requirement 3: include at least one drum kit, one bass or synth, and one additional "
     "element. The last two lines are the kit's own suggestions, not my steps: let the bass follow the kick, and add one pattern at a "
     "time and listen before adding the next. Hand out the Feature tracker."),
    (3, "pic", "Four ways to evolve", "features",
     "Class 3, the first working day. A kit picture of four Step Sequencer settings on the steps students already have. Probability "
     "gives a step a chance of playing. Velocity changes how hard each step hits. Step automation gives every step its own value, for "
     "example a filter cutoff. Mute and unmute takes a row out and brings it back, which my fourth tip uses for arrangement changes. "
     "Students use at least three of these or others they find; the sheet says at least 3 different Step Sequencer features."),
    (3, "bullets", "Step 4: automate and vary", "Use probability, velocity and automation|Patterns should evolve, not repeat exactly|"
     "Use at least 3 Step Sequencer features|Count your features on the tracker",
     "Step 4 and requirement 2, shortened to fit the slide. Step 4, automate and vary: use probability, velocity and automation to make "
     "patterns evolve. Requirement 2: use at least 3 different Step Sequencer features. My second struggle is that patterns sound "
     "static, so push automation and probability. The last line is the kit's own: students list their features on the Feature tracker."),
    (3, "pic", "Worked example: 50 seconds", "arrange",
     "Class 3. An invented piece, Night Shift, described on paper; nothing here is audio. It is 50 seconds long, 20 bars at 96 BPM, in "
     "four sections: intro, groove, build and outro. Five layers join and leave: kick and snare, hi-hat, bass, a synth arp and a second "
     "drum pattern. Below them are four automation lanes, and none is flat. The patterns, the five features and the arithmetic are on "
     "the worked example pages."),
    (4, "bullets", "Probability is your friend", "Even a small chance makes patterns feel human|Do not just stack patterns: build and "
     "evolve|Static? Push automation and probability|Try it live on a hi-hat",
     "My tips 2 and 3 and my second and third struggles, shortened to fit the slide. Probability is your friend: even a small "
     "percentage of randomness makes patterns feel more human. Do not just stack patterns; think about how your piece builds and "
     "evolves. Patterns that sound static need automation and probability. Students do not always understand probability, so show a "
     "live example on a hi-hat: give a few steps a 25 percent chance and loop it. Ask students to try it now."),
    (4, "bullets", "Step 5: mix and refine", "Apply EQ, panning and plug-ins|Arrange into a cohesive piece|Use mute/unmute to change "
     "the arrangement|Harder option: 90 seconds, alternates, 2 step automations",
     "Step 5, tip 4 and my Harder variation, shortened to fit the slide. Mix and refine: apply EQ, panning and plug-ins, and arrange "
     "into a cohesive piece. Use mute and unmute in the Step Sequencer to create arrangement changes. My Harder variation extends the "
     "piece to 90 seconds and requires pattern alternates and two types of step automation; offer it to students who are ready. "
     "Hand out the Listen-back sheet."),
    (6, "steps", "Steps 6 and 7: bounce, present", "Bounce your track|Zip the .logicx project|Create your Padlet post with 3 questions|"
     "Prepare to present",
     "Class 6. Steps 6 and 7 of the project sheet, shortened to fit the slide. Finalize: bounce your track and prepare your "
     "presentation. Present and get feedback: create your own Padlet post with three questions you want classmates to answer. The "
     "second line is the kit's own reminder about the submission: zip the .logicx in Finder (Control-click, Compress). Check that "
     "every track is between 30 and 60 seconds before students bounce, because the short length makes students rush."),
    (6, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Pattern Prodigy|At least 3 Step "
     "Sequencer features|Padlet post with 3 questions|Answer 2 questions on classmates’ posts",
     "The submission checklist from the project sheet, shortened to fit the slide. Show where students upload (your class page) and "
     "where the Padlet board is. Remind students that the checklist includes using at least three Step Sequencer features: they can "
     "show them from their Feature tracker. A bounced file of the wrong length is the quickest thing to fix: check it is 30 to 60 seconds."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play your track|Say which features you used and where|Your Padlet post: 3 questions about your "
     "project|Answer at least 2 of each classmate’s 3",
     "Class 7, presentations with Padlet Q and A. Step 7 of the project sheet, shortened to fit the slide: create your own Padlet post "
     "with 3 questions you want classmates to answer, present to the class, and during classmates' presentations answer at least 2 of "
     "their 3 questions. The second line is the kit's own suggestion. Ask the class to listen for one thing that changes in each piece."),
    (7, "closer", "One last thing…", "You built the pattern.|You made it breathe.|You let it evolve.|Now press play.",
     "Close with my teacher notes: this project works well for students drawn to electronic, lo-fi or beat-driven music. Ask a few "
     "students what they noticed changing in a classmate's groove. Tell them the next project starts from the menu."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("example", "Worked example", "an invented groove on paper"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 8, 11, 13, 18]
SHOTS3 = [("example", "Worked example"), ("grids", "Pattern grids"), ("features", "Feature tracker"), ("arrange", "Arrangement plan"),
          ("starter", "Starter + Harder"), ("proj2", "Steps"), ("setup", "Setup"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "changes", "logicref", "starter", "example", "example2",
        "grids", "features", "arrange", "refine", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "example", "proj2", "rubric"]

COVER_A = "Program a groove that evolves"
COVER_C = "DMP2 · step sequencer · intro slides"
PDF_COVER = dict(a=30, b=50, c=14, art=7.3)
SQ_COVER = dict(a=44, b=140, c=27, art=740, gap=44)
SQ_B_LINES = ["Pattern", "Prodigy"]
SQ_SUB = "7 class periods · step sequencer · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Pattern grids, feature tracker, arrangement plan, worked example", 28)}
SQ_BANDS = {1: "Explore <em>·</em> rhythms <em>·</em> melody <em>·</em> evolve <em>·</em> bounce",
            2: "Hook <em>·</em> read a grid <em>·</em> four ways to evolve <em>·</em> mix",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, video, songs, artists or albums are named or included. Students make every sound in their tracks themselves, "
             "from the instruments and kits in Logic.")
CREDITS = ["Worked example (an invented 50-second piece with its patterns, sections, layers and automation lanes, described on paper), "
           "the grid, step, feature and arrangement drawings and layouts: original work, Hudson Beat.",
           "No audio, video, lyrics, album art, screenshots, presets, templates, links or chart data are included. No student work is "
           "included. Padlet is named only as the owner’s own materials name it."]
LOGIC_INTRO = ("Where to find the tools a Pattern Prodigy project is likely to use. Demonstrate what your class needs on Classes 1 and 2 "
               "and then let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add tracks with Track › New Tracks…: a Software Instrument track for drum kits, "
              "bass and synths."),
             ("Drum kit and sounds", "Choose a drum kit from the Library (Y) on a Software Instrument track. Kits that show a grid of "
              "pads, such as Drum Machine Designer, are the easiest to read in a sequencer."),
             ("Pattern Region and Step Sequencer", "Create a Pattern Region on the track (look for the Pattern Region option when you "
              "make or draw a region) and double-click it to open the Step Sequencer in the editor area. Click a step to turn it on; "
              "click again to turn it off."),
             ("Bass and synth rows", "A melodic track can use the Step Sequencer too: each row is a pitch, so the steps you click make a "
              "bass line or a synth arp. This answers my first struggle."),
             ("Velocity and probability", "Use the controls along the bottom or side of the Step Sequencer to choose which value you edit "
              "for each step. Velocity is how hard a step hits; probability is its chance of playing. Try it on a hi-hat."),
             ("Step automation", "Pick a parameter, such as a filter cutoff, and set a value for each step. The values repeat every "
              "time the pattern loops."),
             ("Mute and unmute", "Each row has a mute control. Muting and unmuting rows as the piece plays is the simplest way to change "
              "the arrangement (my fourth tip)."),
             ("Alternates", "For my Harder variation, put a second Pattern Region with a different pattern after the first. Check "
              "whether your version also offers pattern sets inside one region."),
             ("Live recording", "You can also play a pattern in live and let Logic fill the steps. Quantize or edit the steps afterwards."),
             ("Automation, EQ, pan, plug-ins", "Press A to show track automation. Add Channel EQ for balance, use each track's Pan "
              "knob, and add plug-ins such as a reverb or filter. Press X for the Mixer."),
             ("Length check and bounce", "Bars × 240 ÷ tempo = seconds. File › Bounce › Project or Section (Command-B), MP3 or WAV. "
              "In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and zipped .logicx submitted",
                 "Padlet post created with my 3 questions", "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my track:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12.4pt;margin-bottom:3pt">Only drums: slide 9 and the bass and synth rows on the Pattern grids (page @GRIDS).</li>'
    '<li style="font-size:12.4pt;margin-bottom:3pt">Static patterns: the Feature tracker (page @FEATURES) and slide 11 show four ways to make a pattern change.</li>'
    '<li style="font-size:12.4pt;margin-bottom:3pt">Probability: the hi-hat demo on page @SETUP and slide 14, with the dashed steps on the worked example (page @EXAMPLE).</li>'
    '<li style="font-size:12.4pt;margin-bottom:0">Rushing: the Arrangement plan (page @ARRANGE) has a length helper, so students plan their bars first.</li></ul></div>'
    '<div class="box" style="margin-top:7pt"><span class="k">Where this kit helps with the variations (kit suggestion)</span><ul style="margin:0">'
    '<li style="font-size:12.4pt;margin-bottom:3pt">Easier: a 16-step chart of a drum pattern to enter, standing in for the pre-built pattern (page @STARTER).</li>'
    '<li style="font-size:12.4pt;margin-bottom:0">More advanced: the worked example has an alternate pattern and step automation (page @EXAMPLE2); page @STARTER lays out 90 seconds.</li></ul></div>')
TN1_SIZE = 15.2
PROJ_SIZE = 14.6
VOCAB_GAP = 14
CHANGES_SIZE = 9.8
LOGIC_SIZE = 10.2
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ small page helpers
CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; } table.sg td, table.sg th { border: 1pt solid #000; text-align: center; "
          "padding: 0; font-size: 8pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.2in; font-size: 9pt; } "
          "table.sg td.b { border-left: 2.2pt solid #000; } table.sg td.on { background: " + ACCENT + "; } </style>")


def blank_grid(rows, h=24, hdr="Step"):
    head = "<tr><th style='width:1.2in'>" + hdr + "</th>" + "".join(
        f"<th{' style=\"border-left:2.2pt solid #fff\"' if i % 4 == 0 else ''}>{i + 1}</th>" for i in range(16)) + "</tr>"
    body = "".join("<tr><td class='l' style='height:%dpt'>%s</td>%s</tr>" % (h, r, "".join(
        f"<td class='{'b' if i % 4 == 0 else ''}'></td>" for i in range(16))) for r in rows)
    return f"<table class='sg'>{head}{body}</table>"


def chart_grid(rows, h=20):
    """A filled 16-step chart: rows = [(label, set of steps)]."""
    head = "<tr><th style='width:1.2in'>Step</th>" + "".join(
        f"<th{' style=\"border-left:2.2pt solid #fff\"' if i % 4 == 0 else ''}>{i + 1}</th>" for i in range(16)) + "</tr>"
    body = "".join("<tr><td class='l' style='height:%dpt'>%s</td>%s</tr>" % (h, lab_, "".join(
        f"<td class='{'b' if i % 4 == 0 else ''}{' on' if (i + 1) in on else ''}'></td>" for i in range(16))) for lab_, on in rows)
    return f"<table class='sg'>{head}{body}</table>"


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, what changed, Logic quick "
              "reference, pre-built pattern and Harder variation, worked example (2 pages)"),
             ("Student pages", "grids", "reflect", "Pattern grids, Feature tracker, Arrangement plan, Listen-back sheet, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period structured project for high school music '
             f'technology. Each student builds a 30–60 second groove in Logic with the Step Sequencer and Pattern Regions: drums, a bass '
             f'or synth and one more element, with probability, velocity and automation so the patterns evolve. They bounce it, '
             f'reflect and present it with Padlet questions for feedback. It is the project from my Digital Music Production 2 course '
             f'(type: structured; focus: Step Sequencer), and the projects in that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Set up the Presentation Padlet, practise the hi-hat demo and decide which features count (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("grids")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Class 5 is a working day with no new slide. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}: a pre-built drum pattern (a chart to enter is on page {D.IX("starter")}), or 90 seconds with pattern alternates and 2 types of step automation.</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Any sounds:</b> the pages name no kit or instrument beyond Logic’s own, so students fill in their own.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students program '
             f'a groove on a grid, then learn that probability, velocity and automation are how a loop evolves.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13.4pt;line-height:1.5">One original loop-based groove, 30–60 seconds long, built from Pattern Regions '
             f'in the Step Sequencer: at least one drum kit, one bass or synth and one additional element. It uses at least three '
             f'different Step Sequencer features, such as probability, velocity and step automation, and a mix with balance, clarity '
             f'and space. They hand in a bounced .mp3 or .wav and the zipped .logicx project, plus a Padlet post with three feedback '
             f'questions, then play the piece and present it.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:13pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:12pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:13pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.6pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: explore and build drums, add melody, three working days, mix and bounce, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Step Sequencer, Pattern Regions, automation, mixing, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a feedback board and a place to submit files</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:12pt">Students should already '
             f'know how to open a project, add and play software instruments, use the Mixer, and save, bounce and zip in Logic. The '
             f'Step Sequencer is new: the quick reference (page {D.IX("logicref")}) shows where its controls live.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Structured", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 12.2pt; line-height: 1.46; margin-bottom: 6pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the final listen.</li>'
             f'<li><b>A place to submit</b> the .mp3 or .wav and the zipped .logicx (your class page).</li>'
             f'<li><b>The Presentation Padlet</b>, set up before Class 1 (yours to set up; none is included).</li>'
             f'<li><b>A hi-hat demo</b> ready for Class 1 or 2 (my third struggle): a hi-hat row with a few steps at 25–50% probability, looped.</li>'
             f'<li><b>A rule for “at least 3 features”</b> (requirement 2): which features count. Write it on the board and on page {D.IX("features")}.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("grids")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:12.2pt;margin-bottom:8pt") for c in [
                 "Practise opening a Pattern Region and the Step Sequencer on a classroom Mac.",
                 "Set up the Presentation Padlet in your class page.",
                 "Decide which features count, and whether to offer the pre-built pattern (page @STARTER).",
                 "Check that a student computer opens Logic and plays back through headphones."]).replace("@STARTER", str(D.IX("starter"))) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch (my struggles)", True)}'
             f'<p style="font-size:12pt">Students use the Step Sequencer only for drums, patterns sound static, probability is hard to see, and the '
             f'short length makes students rush. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Kit suggestions, not part of my sheets</span><ul style="margin:0">'
             f'<li style="font-size:11.6pt">Features that count: probability, velocity, step automation, mute and unmute, and pattern alternates are the ones my notes and tips name. Add others if you like.</li>'
             f'<li style="font-size:11.6pt">Ask while students work: which feature changed what you just heard? Which step would you change next?</li>'
             f'<li style="font-size:11.6pt">Plan the bars first. Thirty seconds is only about 15 bars at 120 BPM, so a short piece goes fast.</li></ul></div>'
             f'{D.H2("Sounds they did not make")}'
             f'<div class="box"><span class="k">A kit suggestion</span><p style="margin:0;font-size:11.4pt;line-height:1.42">'
             f'Tell students to build their grooves from the instruments and kits in Logic, and to hand in only their own track.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.4pt;line-height:1.42">'
             f'Loud kicks and bass are easy to overdo in headphones. Tell students to start low and to check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


def starter_page(n, wm=False):
    chart = chart_grid([("Kick", {1, 9}), ("Snare", {5, 13}), ("Closed hi-hat", set(range(1, 17, 2))), ("Percussion", {4, 12})], 20)
    inner = (f'<style>.sb2 li {{ font-size: 11.6pt; line-height: 1.4; margin-bottom: 4pt; }}</style>'
             f'<p style="margin:0 0 5pt;font-size:12pt;line-height:1.42">My Easier variation: provide a pre-built drum pattern as a starting '
             f'point. A Logic project is not included in this kit, so here is the pattern as a chart. Enter it in a Pattern Region in a few '
             f'minutes, or have students enter it, with a kit you have the right to use.</p>'
             f'{D.H2("Pre-built drum pattern: one bar, 16 steps", True)}{CSS_SG}{chart}'
             f'<ol class="sb2" style="margin:5pt 0 0"><li>New Software Instrument track with a drum kit; create a Pattern Region and open the Step Sequencer.</li>'
             f'<li>Turn on the steps shown in the chart. Kick on 1 and 9, snare on 5 and 13, the hi-hat on every odd step, and percussion on 4 and 12.</li>'
             f'<li>Loop it for a few bars and save it as “Starter”. Students add bass, synth and variation on top.</li></ol>'
             f'{D.H2("My Harder variation, laid out")}'
             f'<table class="t" style="font-size:11.6pt;line-height:1.4"><tr><th style="width:30%">My option</th><th>How to use it</th></tr>'
             f'<tr><td><b>Extend to 90 seconds</b></td><td>That is 36 bars at 96 BPM or 45 bars at 120 BPM (page {D.IX("arrange")} has the length helper). '
             f'The worked example (page {D.IX("example")}) is 50 seconds, so each section is about twice as long.</td></tr>'
             f'<tr><td><b>Pattern alternates</b></td><td>Students make a second pattern (an A and a B) and switch between them, as the worked example does in its Build.</td></tr>'
             f'<tr><td><b>2 types of step automation</b></td><td>Two different parameters set per step, for example a filter cutoff on a synth and a velocity or gate pattern on a drum row. '
             f'The worked example uses one (page {D.IX("example2")}).</td></tr></table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">How to use this page</span><p style="margin:0;font-size:11.6pt;line-height:1.45">'
             f'Offer the chart to students who freeze at the empty grid; nobody has to take it. Offer the Harder variation to students '
             f'who finish early. Both are your choice, as in my notes. The 30–60 second length is the rule for everyone else (requirement 1).</p></div>')
    return D.page("Pre-built pattern and my Harder variation", "TEACHER", "Easier + Harder", inner, n, key="starter")


def example_page(n, wm=False):
    feats = "".join(f"<tr><td style='width:22%'><b>{a}</b></td><td>{b}</td></tr>" for a, b in FEATURES)
    inner = (f'<p style="margin:0 0 5pt;font-size:10.4pt">An <b>invented piece, “{PIECE}”, described on paper</b>: no audio is included. '
             f'Students’ projects will differ. {TOTAL_BARS} bars at {BPM} BPM, four sections, five layers, five Step Sequencer features (page 1 of 2).</p>'
             f'<div class="cols" style="gap:10pt"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.4pt">{WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.4pt">It names no features and nothing says what will change.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:9.4pt;line-height:1.3">{STRONG}</p></div></div>'
             f'{D.H2("3 · One bar of the groove: 16 steps")}{CSS_SG}'
             f'<div style="width:7.2in;margin:2pt auto 3pt">{D.body_svg(grid_body(1250, "page grid", 26, 20))}</div>'
             f'<p style="margin:0 0 3pt;font-size:9pt;line-height:1.3">The bass plays C, Eb, G and Bb (C minor 7) on steps 1, 4, 7, 11 and 14, '
             f'and the synth arp climbs C, Eb, G, Bb, C and comes back down on the odd steps. Every pitch is a chord tone, so the layers '
             f'agree. Hat velocity: 100 on steps 1, 5, 9, 13 and 70 on the other odd steps; the even steps are ghosts at 25% probability.</p>'
             f'{D.H2("4 · The five features it uses")}<table class="t" style="font-size:9.4pt;line-height:1.28">{feats}</table>')
    return D.page("Worked example · an invented groove", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    lay = "".join(f"<tr><td style='width:16%'><b>{a}</b></td><td>{d}</td><td style='white-space:nowrap'>{mmss(s)}–{mmss(e)}</td></tr>"
                  for a, s, e, d in LAYERS)
    aut = "".join(f"<tr><td><b>{ly} · {par}</b></td><td>{mmss(pts[0][0])}–{mmss(pts[-1][0])}</td></tr>" for ly, par, pts in AUTO)
    ph = "".join(f"<tr><td style='width:17%'><b>{a}</b></td><td style='width:19%;white-space:nowrap'>{b}</td><td>{c}</td></tr>"
                 for a, b, c in SECTION_NOTES)
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">“{PIECE}”, page 2 of 2: the map of the whole piece, then the numbers.</p>'
             f'{D.H2("5 · The map: 0:50, four sections, five layers, four lanes")}'
             f'<div style="width:6.5in;margin:1pt auto 3pt">{D.body_svg(map_body(1250, "page arrange", 24, 20))}</div>'
             f'<div class="cols" style="gap:10pt"><div><span class="k" style="font-size:9.4pt">6 · Sections</span>'
             f'<table class="t" style="font-size:8.6pt;line-height:1.22;margin-top:2pt">{ph}</table></div>'
             f'<div><span class="k" style="font-size:9.4pt">7 · Layers (in to out)</span>'
             f'<table class="t" style="font-size:8.6pt;line-height:1.22;margin-top:2pt">{lay}</table></div></div>'
             f'<div class="cols" style="gap:10pt;margin-top:4pt"><div><span class="k" style="font-size:9.4pt">8 · Automation lanes</span>'
             f'<table class="t" style="font-size:8.6pt;line-height:1.22;margin-top:2pt">{aut}</table></div>'
             f'<div class="box acc-b"><span class="k">9 · Checking the numbers</span><p style="margin:0;font-size:8.8pt;line-height:1.28">'
             f'One bar of 4/4 at {BPM} BPM lasts 240 ÷ {BPM} = {BAR_S:g} seconds, so {TOTAL_BARS} bars = {TOTAL_BARS * BAR_S:g} seconds, inside my '
             f'30–60 second range. The sections are {" + ".join(str(int((b - a) / BAR_S)) for _, a, b in SECTIONS)} bars = {TOTAL_BARS}. '
             f'Five features, more than my minimum of three. '
             f'<b>Three Padlet questions (invented):</b> {qs}</p></div></div>')
    return D.page("Worked example · the map", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


def grids_page(n, wm=False):
    inner = (f'{CSS_SG}<p style="margin:0 0 4pt;font-size:10.6pt">Steps 1 to 3: open the Step Sequencer and experiment with basic drum patterns, '
             f'create your core drum and percussion patterns, then program bass and synth patterns that complement your groove. '
             f'Colour or mark the steps you turn on. The Step Sequencer is a tool that lets you program rhythms and melodies by toggling steps on a grid. '
             f'Each grid is one bar of 16 steps; beats start at 1, 5, 9 and 13.</p>'
             f'<span class="k">Pattern A · drums and percussion</span><div style="margin-top:2pt">{blank_grid(["Kick", "Snare", "Hi-hat", "", ""], 25)}</div>'
             f'<div class="fl" style="margin:3pt 0 5pt"><b>Steps with lower velocity or probability:</b><span></span></div>'
             f'<span class="k">Pattern B · bass (write the note under each step)</span><div style="margin-top:2pt">{blank_grid(["Bass note", "Note name"], 25)}</div>'
             f'<span class="k" style="display:block;margin-top:6pt">Pattern C · synth or another element</span><div style="margin-top:2pt">{blank_grid(["Synth note", "Note name"], 25)}</div>'
             f'<div class="box acc-b" style="margin-top:7pt"><span class="k">My groove</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Tempo (BPM):</b><span style="flex:0 0 0.9in"></span><b>The feel I want:</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>The row I will use for something other than drums:</b><span></span></div></div>')
    return D.page("Pattern grids", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="grids")


def features_page(n, wm=False):
    rows = [("Probability", ""), ("Velocity", ""), ("Step automation", ""), ("Mute / unmute", ""), ("Pattern alternate", ""), ("Another feature: ", "")]
    trs = "".join(f"<tr><td style='height:40pt'><b>{a}</b></td><td></td><td></td><td></td><td></td></tr>" for a, _ in rows)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Step 4: use probability, velocity, and automation to make patterns evolve. Requirement 2: use at '
             f'least 3 different Step Sequencer features. Probability is a feature that gives each step a chance of playing or not, adding randomness. '
             f'Velocity is how hard a note is played. Fill in the row each time you use a feature.</p>'
             f'<div class="box acc-b" style="margin:0 0 5pt"><div class="fl" style="margin:0"><b>The features my teacher says count:</b>'
             f'<span></span></div></div>'
             f'<table class="map"><tr><th style="width:17%">Feature</th><th style="width:25%">Where I used it (track, pattern, bars)</th>'
             f'<th style="width:22%">The setting I chose</th><th style="width:26%">What I hear change</th><th>Done?</th></tr>{trs}</table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Check</span>'
             + D.chk("I used at least 3 different Step Sequencer features (requirement 2).", 12, "font-size:10.8pt;margin-bottom:3pt")
             + D.chk("I can point to each one and play the moment it changes.", 12, "font-size:10.8pt;margin-bottom:3pt")
             + D.chk("I used the Step Sequencer for more than drums (a bass or synth row).", 12, "font-size:10.8pt;margin-bottom:0") + '</div>'
             f'<div class="fl" style="margin-top:6pt"><b>The feature that changed my groove most:</b><span></span></div>'
             f'<div class="fl"><b>A feature I want to try next:</b><span></span></div>')
    return D.page("Feature tracker", "STUDENT", "Classes 2–5", inner, n, wm, name=True, key="features")


def arrange_page(n, wm=False):
    nb = 32
    head = "<tr><th style='width:1.25in'>Layer</th>" + "".join(f"<th>{i + 1}</th>" for i in range(nb)) + "</tr>"
    body = "".join("<tr><td class='l' style='height:34pt'></td>" + "".join(f"<td class='{'b' if i % 4 == 0 else ''}'></td>" for i in range(nb)) + "</tr>"
                   for _ in range(8))
    help_rows = [(80, 10, 20), (96, 12, 24), (120, 15, 30), (128, 16, 32), (144, 18, 36)]
    hr = "".join(f"<tr><td><b>{b}</b></td><td>{lo}</td><td>{hi}</td></tr>" for b, lo, hi in help_rows)
    inner = (f'{CSS_SG}<style>table.sg th {{ font-size: 6.4pt; }} table.sg td.l {{ width: 1.25in; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.6pt">Step 5: arrange into a cohesive piece. Use mute/unmute in the Step Sequencer to create '
             f'arrangement changes. Shade the bars where each pattern plays, and write the layer’s name at the left. Don’t just stack patterns: '
             f'think about how your piece builds and evolves.</p>'
             f'<table class="sg">{head}{body}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:6pt"><div class="box acc-b"><span class="k">My sections</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Section 1:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Section 2:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Section 3:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>Section 4:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div></div>'
             f'<div><span class="k">Length helper (bars needed)</span><table class="t" style="font-size:9.6pt;margin-top:2pt"><tr><th>BPM</th><th>30 s</th><th>60 s</th></tr>{hr}</table></div></div>'
             f'<div class="fl" style="margin-top:6pt"><b>My tempo:</b><span style="flex:0 0 0.8in"></span><b>Bars:</b><span style="flex:0 0 0.8in"></span>'
             f'<b>Length: bars × 240 ÷ tempo =</b><span style="flex:0 0 0.8in"></span><b>seconds</b></div>')
    return D.page("Arrangement plan", "STUDENT", "Classes 3–5", inner, n, wm, name=True, key="arrange")


def refine_page(n, wm=False):
    trs = "".join("<tr><td style='height:36pt'></td><td></td><td></td></tr>" for _ in range(5))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Step 5: apply EQ, panning, and plug-ins. Arrange into a cohesive piece. '
             f'Requirement 4: demonstrate balance, clarity, and creative use of space in your mix. Loop one section and listen for each pattern.</p>'
             f'<div class="box acc-b"><span class="k">Listen-back</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>The pattern I hear clearly:</b><span></span></div>'
             f'<div class="fl"><b>The pattern that gets buried:</b><span style="flex:0 0 2.2in"></span><b>What fixes it (EQ, pan, level):</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>A bar that sounds exactly like the one before it:</b><span></span></div></div>'
             f'{D.H2("Static or crowded spots")}'
             f'<table class="map"><tr><th style="width:16%">Bar or time</th><th style="width:42%">What feels static, crowded or muddy</th><th>What I changed</th></tr>{trs}</table>'
             f'<div class="box" style="margin-top:7pt"><span class="k">Checks before I bounce</span>'
             + "".join(D.chk(c, 12, "font-size:10.8pt;margin-bottom:3pt") for c in [
                 "I have a drum kit, a bass or synth, and one more element.",
                 "At least 3 different Step Sequencer features are used and I can hear them.",
                 "The piece builds and evolves; it does not only stack patterns.",
                 "Mute and unmute change the arrangement at least once.",
                 "The mix is balanced and clear, with room between sounds.",
                 "The piece is between 30 and 60 seconds."]) + '</div>'
             f'<div class="fl" style="margin-top:6pt"><b>The one change that improved my groove most:</b><span></span></div>')
    return D.page("Listen-back sheet", "STUDENT", "Classes 4–6", inner, n, wm, name=True, key="refine")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "starter": starter_page, "example": example_page,
         "example2": example2_page, "grids": grids_page, "features": features_page, "arrange": arrange_page, "refine": refine_page}


# ================================================================ content checks (example arithmetic, owner text, no audio)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 5), reqs=(REQS, 4), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 3))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp} (the owner's count)")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is the owner's /25, levels 1-5")
    if [c for c, _ in RUBRIC] != ["Creativity & Originality", "Technical Skill / DAW Use", "Composition & Structure",
                                  "Sound Design & Mix Quality", "Documentation & Presentation"]:
        errs.append("rubric categories must be the owner's, in order")
    if FILE_NAME not in CHECK[2] or "Pattern Prodigy" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    if "30–60 seconds" not in REQS[0] or "30–60 second" not in OVERVIEW:
        errs.append("length 30-60 seconds as the owner wrote it")
    if "at least 3" not in REQS[1] or "at least 3" not in CHECK[3].lower():
        errs.append("'at least 3' Step Sequencer features as the owner wrote it")
    if not getattr(D, "reflect_on", lambda: True)() or getattr(sys.modules[__name__], "REFLECTION", True) is False:
        errs.append("REFLECTION must stay on: the owner's sheet has no reflection task")
    # the worked example adds up
    if BAR_S != 2.5 or TOTAL_BARS * BAR_S != TOTAL_S:
        errs.append("20 bars x 2.5 s = 50 s")
    if not 30 <= TOTAL_S <= 60:
        errs.append("example inside the owner's 30-60 seconds")
    if [round((b - a) / BAR_S) for _, a, b in SECTIONS] != [4, 8, 4, 4] or sum(round((b - a) / BAR_S) for _, a, b in SECTIONS) != TOTAL_BARS:
        errs.append("sections 4 + 8 + 4 + 4 = 20 bars")
    if SECTIONS[0][1] != 0 or SECTIONS[-1][2] != TOTAL_S or any(b != c for (_, _, b), (_, c, _) in zip(SECTIONS, SECTIONS[1:])):
        errs.append("sections must tile the piece")
    for nm, a, b, _d in LAYERS:
        if not 0 <= a < b <= TOTAL_S or a % BAR_S or b % BAR_S:
            errs.append(f"layer {nm}: starts and ends on a bar line, inside the piece")
    spans = {nm: (a, b) for nm, a, b, _ in LAYERS}
    if len(AUTO) != 4:
        errs.append("four automation lanes")
    for ly, par, pts in AUTO:
        a, b = spans[ly]
        ts = [t for t, _ in pts]
        vs = [v for _, v in pts]
        if ts != sorted(ts) or len(pts) < 3 or ts[0] < a or ts[-1] > b:
            errs.append(f"lane {ly}/{par}: points in order, 3+, inside its layer")
        if max(vs) - min(vs) < .5:
            errs.append(f"lane {ly}/{par}: a lane that barely moves is the static pattern the project warns about")
    if len(FEATURES) < 3:
        errs.append("the example uses at least 3 Step Sequencer features")
    # patterns: steps 1-16, velocity 1-127, probability 1-100, pitches are chord tones of Cm7
    for nm, pat in (("kick", KICK), ("snare", SNARE), ("hat", HAT)):
        if any(not 1 <= s <= 16 or not 1 <= v <= 127 or not 1 <= p <= 100 for s, (v, p) in pat.items()):
            errs.append(f"{nm}: steps 1-16, velocity 1-127, probability 1-100")
    if set(KICK) & set(SNARE):
        errs.append("kick and snare never share a step")
    if len(HAT) != 16 or sum(1 for v in HAT.values() if v[1] < 100) != 8:
        errs.append("hat: 8 sure steps and 8 ghost steps")
    for nm, pat in (("bass", BASS), ("arp", ARP)):
        for s, (note, vel) in pat.items():
            if not 1 <= s <= 16 or not 1 <= vel <= 127 or note.rstrip("0123456789") not in CHORD:
                errs.append(f"{nm}: step {s} {note} is not a C minor 7 chord tone")
    if len(ARP_CUTOFF) != 16 or ARP_CUTOFF != sorted(ARP_CUTOFF) or ARP_CUTOFF[0] != 15 or ARP_CUTOFF[-1] != 97:
        errs.append("arp cutoff: 16 rising values from 15 to 97")
    if len(QUESTIONS) != 3:
        errs.append("three Padlet questions")
    # the length helper
    for bpm, lo, hi in [(80, 10, 20), (96, 12, 24), (120, 15, 30), (128, 16, 32), (144, 18, 36)]:
        if bars_for(30, bpm) != lo or bars_for(60, bpm) != hi:
            errs.append(f"length helper wrong at {bpm} BPM")
    if bars_for(90, 96) != 36 or bars_for(90, 120) != 45:
        errs.append("90 seconds = 36 bars at 96 BPM, 45 bars at 120 BPM")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    txt = " ".join(flat)
    for need in ("No audio, video, songs, artists or albums", "invented piece, “Night Shift”",
                 "Your Name – Pattern Prodigy", "Final Grade = Average of Student + Teacher", "No student work is included",
                 "Reflection"):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up:
        errs.append("UPLOAD.md: must say no audio is included and record the open questions")
    for i in (2, 5, 6, 8, 9, 11, 13, 14, 15, 16, 18):   # slides that shorten the owner's wording must say so
        if "shortened" not in notes[i].lower() and "shortens" not in notes[i].lower():
            errs.append(f"deck slide {i + 1} notes: must say the owner's wording is shortened")
    ch = flat[D.IX("changes") - 1]
    for s in ("slide 3", "slide 6", "slide 7", "slide 9", "slide 10", "slide 12", "slide 14", "slide 15", "slide 16", "slide 17", "slide 19"):
        if s not in ch:
            errs.append(f"'What changed' page must list {s}")
    if "Reflection added" not in ch:
        errs.append("'What changed' page must explain the added Reflection page")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or any("Feature tracker" in g or "Reflection" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Spotify", "Radiohead", "Billboard", "Roland", "TR-808", "Ableton"]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, services or other brands ({banned})")
    return errs


def check_summary():
    return (f"The invented piece is {TOTAL_BARS} bars at {BPM} BPM = {TOTAL_S} s (sections {'+'.join(str(round((b - a) / BAR_S)) for _, a, b in SECTIONS)} bars; "
            f"{len(LAYERS)} layers, {len(AUTO)} automation lanes, none flat, {len(FEATURES)} Step Sequencer features; bass and arp pitches are chord tones); "
            f"the owner's lists counted (4 goals, 5 terms, 4 requirements, 7 steps, 4 tips, 6 checklist items, 4 struggles, 3 resources); "
            f"{len(CHANGES)} wording changes disclosed; no audio, artist names or student work included; grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
