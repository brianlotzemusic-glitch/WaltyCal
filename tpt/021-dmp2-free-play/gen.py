#!/usr/bin/env python3
"""DMP2 project: Free Play (TpT 021): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Free Play > "Free Play - Project Sheet & Rubric" (rubric 5 categories scored 1-5, /25, final grade =
average of student and teacher scores), TEACHER NOTES > "Free Play - Teacher Notes" (7 class periods), and the project's entry on
"DMP2 - Project Menu" (the June 2026 menu; owner, 17 Oct 2026: the June entry may be quoted). These three set the project text, steps,
rubric and pacing (owner rule, 17 Oct 2026).
Supporting artifacts: the Teacher Notes name no tutorial ("No specific tutorials needed"), suggest playing 2-3 examples of past student
work (student work is never used here, so nothing is included and the kit gives an invented example on paper instead) and ask the
teacher to set up the Presentation Padlet. The older Projects > Free Play folder holds only a 2024 outline, which is not a source.

NO AUDIO IS INCLUDED. Students make their own music. The worked example is an invented piece ("Late Bus Home", 2 minutes 30 seconds,
96 BPM, 60 bars) described on paper; every picture (production cycle, proposal parts, the arrangement map) is drawn in code.
Songs and chart data are not named.
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "free-play"
TITLE = "Free Play"
ACCENT = "#4B4FA8"          # this product's single accent: indigo (008 red, 009 orange, 010 violet, 011 teal, 012 blue, 013 green, 014 magenta, 015 gold, 016 olive, 017 sienna, 018 steel blue, 019 wine, 020 pine)
ACC_LIGHT = "#D5D6F0"
PRICE = "9.00"
CLASSES = 7
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-020).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "Free Play Project in Logic Pro | Open-Ended Music Production | High School"
DESC_START = "Open-ended music production project for high school:"
DESC_MUST = ["Free Play", "proposal", "no audio", "Padlet"]
ZIP_DIR = "Free Play - Hudson Beat"
ZIP_DATE = (2026, 10, 18, 12, 0, 0)
TYPE = "Open-Ended Project"
PROJ_LINE = "Digital Music Production | <i>Open-Ended Project</i> | 7 class periods"
DECK_STRAP = "Make whatever you want in Logic Pro"
BANNED_EXTRA = []

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Open-Ended", "Creative Freedom"
MENU_DESC = "Explore any style or technique of your choice. Find your artistic voice and set goals for the semester."
OVERVIEW = ("This is your chance to make whatever you want. Use Logic Pro to explore any style, technique, or idea that excites you. "
            "The only rule: have a plan and follow through. This project is about finding your creative voice and showing that you can "
            "manage a project from start to finish.")
ARROW = ('<svg width="1em" height=".62em" viewBox="0 0 20 12" style="vertical-align:baseline;margin:0 1pt">'
         '<path d="M1 6h16M12 1.5l6 4.5-6 4.5" stroke="#000" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')
GOALS = ["Explore Logic Pro creatively with full artistic freedom",
         "Develop project management skills through proposals and documentation",
         "Practice the full production cycle: idea " + ARROW + " composition " + ARROW + " mix " + ARROW + " presentation",
         "Build confidence in making creative decisions independently"]
VOCAB = [("DAW", "Digital Audio Workstation — the software you use to make music (Logic Pro)"),
         ("Bounce / Export", "Rendering your project into a playable audio file (.mp3 or .wav)"),
         ("Arrangement", "How you organize different sections and instruments across time in your project"),
         ("Project Proposal", "A written plan describing what you intend to create and how")]
REQS = ["Length is up to you — but your track should feel complete, not unfinished",
        "Use a variety of tracks and instruments appropriate to your chosen style",
        "Apply basic mixing: EQ, panning, and volume balancing on all tracks",
        "Write a project proposal paragraph (submitted via your class page)"]
STEPS = ["<b>Explore</b> — Open Logic, experiment with sounds, and brainstorm ideas (Idea sketchpad: page @SKETCH)",
         "<b>Propose</b> — Write a paragraph describing your concept, tools, and what the final product will sound like. Submit via your class page "
         "(Proposal planner: page @PROPOSAL)",
         "<b>Build</b> — Lay down your foundation (drums, chords, bass) and begin shaping your arrangement (Work plan: page @WORKPLAN)",
         "<b>Develop</b> — Add layers, melodies, FX, and transitions. Refine your sound and structure",
         "<b>Mix</b> — Balance your levels, apply EQ and panning, and clean up your project",
         "<b>Finalize</b> — Bounce your final track and prepare your presentation",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["Start with a clear idea, but don’t be afraid to let it evolve. Some of the best projects shift direction during the process.",
        "Don’t spend 3 days picking sounds. Get something down early and refine as you go.",
        "If you get stuck, listen to music that inspires you. Pay attention to what they did and try something similar in your own project.",
        "Listen to your track on headphones AND speakers before you call it done."]
FILE_NAME = "“Your Name – Free Play”"
CHECK = ["Project proposal paragraph submitted via your class page",
         "Bounced .mp3 or .wav uploaded to your class page",
         "Zipped .logicx project file uploaded to your class page",
         f"Files named correctly: {FILE_NAME}",
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
TN_REINFORCES = ("This is a diagnostic project as much as a creative one. It lets you see where each student is — their comfort with Logic, "
                 "their creative instincts, and their ability to manage time independently. It also establishes the proposal and Padlet "
                 "Q&amp;A workflow they’ll use all semester.")
STRUGGLES = ["Analysis paralysis — students freeze because they have too many choices. Encourage them to commit to an idea early and iterate.",
             "Weak proposals — some students write one vague sentence. Push them to describe what their track will sound like and which tools they’ll use.",
             "Poor time management — students underestimate how long mixing takes. Remind them to leave at least one full class for final mixing and bounce.",
             "Students treat the presentation Q&amp;A as an afterthought — remind them that thoughtful questions lead to better feedback."]
VAR_EASY = ("Provide a list of 3–5 project prompts they can choose from (e.g., “make a 30-second intro for a podcast,” “recreate a song you "
            "like”) to reduce overwhelm.")
VAR_HARD = ("Require a minimum track length (2+ minutes), a specific number of original MIDI tracks (no Apple Loops), or a written artist "
            "statement explaining their creative choices.")
RESOURCES = [("No specific tutorials needed — this is about student exploration",
              "Kept as I wrote it. The kit adds no tutorial and no video: the Logic quick reference (page @LOGICREF) only says where each tool "
              "lives."),
             ("Consider playing 2–3 examples of past student work to set expectations",
              "No student work is included, so there is nothing to play. This kit gives an invented example on paper instead (page @EXAMPLE): "
              "a proposal, an arrangement map and a mix plan for a piece that does not exist, so you can show what a finished plan looks "
              "like without using anyone’s work."),
             ("Set up the Presentation Padlet in your class page before Day 1",
              "Kept, and added to the setup checklist (page @SETUP). The Padlet is yours to set up: no board or link is included.")]
TN_NOTE = ("Use this project to calibrate your expectations for the group. Take note of who manages time well, who needs more structure, "
           "and who might be ready for bigger challenges.")
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Creativity &amp; Originality: ask what the student was going for in the proposal, then listen for it. Defaults and clichés "
                "are fine as a start; the question is what they changed.",
                "Technical Skill: open the project. Which Logic tools did they use, and are EQ, panning and volume set on every track "
                "(my third requirement)?",
                "Composition &amp; Structure: compare the arrangement with the Work plan (page @WORKPLAN). Does the piece feel complete, "
                "with sections that change?",
                "Sound Design &amp; Mix Quality: listen on headphones and on speakers (my fourth tip). Ask which part leads in each section.",
                "Documentation &amp; Presentation: the proposal, the Work plan, the three Padlet questions and the Reflection page "
                "(page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Introduction, project overview, explore Logic, brainstorm ideas.",
     "do": "Slides 1–7: hook, what Free Play is, the production cycle, step 1, commit early. Hand out the project sheet and the Idea "
           "sketchpad. Students open Logic and try sounds.", "slides": (1, 7),
     "pages": ["sketch", "proj1", "proj2", "proj3", "vocab"],
     "deck": "What would you make? · production cycle · explore · commit early"},
    {"n": 2, "owner": "<b>Class 2:</b> Write and submit project proposals via your class page.",
     "do": "Slides 8–10: the three parts of a proposal, vague or clear, before you submit. Hand out the Proposal planner. Read each "
           "proposal before the student builds.", "slides": (8, 10), "pages": ["proposal"],
     "deck": "Three parts of a proposal · vague or clear · before you submit"},
    {"n": 3, "owner": "<b>Classes 3–5:</b> Working days — compose, build, refine.",
     "do": "Slides 11–12: steps 3 and 4, and the worked example on paper. Hand out the Work plan. Then work time.", "slides": (11, 12),
     "pages": ["workplan"], "deck": "Working day: build, develop, worked example"},
    {"n": 4, "owner": None, "do": "Slides 13–14: keep building, and mix time is not optional. Then work time.", "slides": (13, 14),
     "pages": ["workplan"], "deck": "Working day: keep building, protect your mix time"},
    {"n": 5, "owner": None, "do": "Full working day: compose, build, refine. Ask each student to play you the track so far and say what "
     "is next.", "slides": None, "pages": [], "deck": "Working day: compose, build, refine"},
    {"n": 6, "owner": "<b>Class 6:</b> Final mix, bounce, and prepare presentations. Students write their 3 Padlet feedback questions.",
     "do": "Slides 15–17: mix and finalize, what to turn in, the rubric. Students self-score and post their three questions.",
     "slides": (15, 17), "pages": ["rubric", "present"], "deck": "Mix · bounce · checklist · rubric"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 18–19: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (18, 19), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one rule for Class 2</span>'
    '<p style="margin:0;font-size:9.6pt">Read every proposal before the student starts building. A one-sentence proposal goes back '
    'with a question (what will it sound like? which tools?), not a grade. The Proposal planner (page @PROPOSAL) has the frame.</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:9.6pt">Working days. Class 5 has no new slide. '
    'Circulate and use this project as a diagnostic: note who manages time, who needs structure and who is ready for more '
    '(my closing note).</p></div></div>')
PACING_SIZE = 9.9

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (requirement 4, step 2, checklist items 1 to 3, my Class 2 pacing line and the "
    "Presentation Padlet resource).",
    "In that resource, “Day 1” is written “Class 1” on the setup page; on page @TN2 it stays as I wrote it.",
    "Page numbers are added to steps 1 to 3 (the Idea sketchpad, Proposal planner and Work plan).",
    "My resource “Consider playing 2–3 examples of past student work” is listed as I wrote it. No student work is included; the kit "
    "adds an invented worked example on paper beside it (page @EXAMPLE).",
    "My pacing guide’s “Classes 3–5” row spans the Class 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines; the arrows in goal 3 are drawn.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 3 shortens my overview and a goal, slide 6 shortens "
    "step 1, slide 7 shortens tips 1, 2 and 3, slides 8 and 10 shorten step 2 and my second struggle, slide 11 shortens steps 3 and 4, "
    "slide 14 shortens requirement 3, my third struggle and tip 4, slide 15 shortens steps 5 and 6, slide 16 shortens the submission "
    "checklist, and slide 18 shortens step 7.",
]
CHANGES_MUST_MENTION = ["your class page", "Page numbers", "No student work", "Classes 3–5", "Layout only", "intro deck shortens"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the overview, the four goals, the four vocabulary terms, the four "
        "requirements (apart from the class page), steps (apart from the page numbers), tips, checklist and file name (“Your Name – Free "
        "Play”), the rubric (five categories scored 1–5, /25, the average of the student’s and the teacher’s score), what the project "
        "reinforces, the four common struggles, the variations, my three resources, my day-by-day pacing and my closing note, and the "
        "project menu entry quoted on page @OVERVIEW. No rubric row is added and the requirements are unchanged.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: how to use the kit, the overview and setup "
                "pages, the teacher moves and slide numbers in the pacing guide, the grading suggestions, the Logic quick reference, the "
                "Idea starters page (prompts for my Easier variation, and my Harder variation laid out), the worked example (an invented "
                "2-minute-30 piece on paper, not audio), the Idea sketchpad, Proposal planner and Work plan, the vocabulary page, the "
                "presentation planner and the intro deck. None of these adds a requirement or a rubric row.")

# ================================================================ the worked example (Hudson Beat original: an invented piece on paper)
PIECE = "Late Bus Home"
BPM = 96
BAR_S = 4 * 60 / BPM                  # 2.5 seconds per bar in 4/4
BARS = 60
TOTAL_S = 150
SECTIONS = [("Intro", 0, 10), ("Verse", 10, 40), ("Chorus", 40, 60), ("Verse", 60, 90), ("Chorus", 90, 110), ("Break", 110, 120),
            ("Chorus", 120, 140), ("Outro", 140, 150)]       # seconds
SECTION_BARS = [4, 12, 8, 12, 8, 4, 8, 4]
LANES = ["Drums", "Bass", "Chords", "Melody", "FX"]
SPANS = {"Drums": [(10, 110), (120, 150)], "Bass": [(10, 110), (120, 140)], "Chords": [(0, 110), (120, 150)],
         "Melody": [(40, 60), (90, 120), (120, 140)], "FX": []}
RISERS = [(36, 40), (86, 90), (116, 120)]
BASS_NOTES = [0, 0, 2, 1, 0, 0, 3, 1]
WEAK = "I will make a chill beat."
STRONG = ("I am making “Late Bus Home”, a mellow instrumental about the ride home after a long day, about two and a half minutes long. "
          "I will start with a slow drum groove and a soft bass, add warm chords on a keyboard sound, and write a simple melody for "
          "the choruses. In Logic I will use drum sounds and software instruments, EQ to keep the bass from covering the chords, and "
          "panning to spread the parts out. It will sound relaxed and a little sleepy at 96 beats per minute, and it should get fuller "
          "each time the chorus comes back.")
MIX_ROWS = [("Drums", "steady, under the melody in the choruses", "center", "cut a little of the muddy low-mids"),
            ("Bass", "just under the drums", "center", "roll off the highs so it stays out of the chords’ way"),
            ("Chords", "softer than the melody", "a little left and right", "cut the lows so the bass has room"),
            ("Melody", "the loudest part in the choruses", "center", "lift the upper mids so it cuts through"),
            ("FX", "very quiet", "wide", "cut the lows so the risers stay light")]
QUESTIONS = ["Where did you first hear the track get fuller?",
             "Which part would you turn up or down, and why?",
             "Does the title match the way the track feels?"]
STARTERS = [("Make something for something",
             ["a 30-second intro for a podcast (my example)", "a theme for a board game that does not exist yet",
              "a background loop for a study session"]),
            ("Make something in a style",
             ["a track in a style you rarely make", "a slow beat with a simple melody on top", "a build that grows for a minute, then drops out"]),
            ("Make something with a rule",
             ["only three instruments", "every section is different from the one before", "a track that could not exist without its first sound"]),
            ("Make something from something you like",
             ["recreate a song you like (my example): make your own version", "take what you notice in music you like and use it in a new piece",
              "change one choice (tempo, instrument or mood) and see what happens"])]


def mmss(t):
    return f"{int(t) // 60}:{int(round(t)) % 60:02d}"


# ================================================================ drawings (original, code-drawn: black + accent only)
WAVE = [.9, .5, .3, .2, .6, .95, .4, .25, .2, .5, .85, .35]


def hero_body():
    W, H = 1100, 560
    out = []
    for i, h in enumerate(WAVE):
        x = 40 + i * 28
        hh = 40 + h * 300
        out.append(f'<line x1="{x}" y1="{280 - hh / 2:.1f}" x2="{x}" y2="{280 + hh / 2:.1f}" stroke="#000" stroke-width="14" stroke-linecap="round"/>')
    out.append(f'<circle cx="560" cy="280" r="130" fill="{ACCENT}" stroke="#000" stroke-width="6"/>')
    out.append('<polygon points="520,215 520,345 615,280" fill="#fff"/>')
    gx, gy, cell, gap = 735, 130, 100, 20
    hot = {(0, 1), (1, 0), (1, 2), (2, 1), (2, 2)}
    for r in range(3):
        for c in range(3):
            on = (r, c) in hot
            out.append(f'<rect x="{gx + c * (cell + gap)}" y="{gy + r * (cell + gap)}" width="{cell}" height="{cell}" rx="14" '
                       f'fill="{ACCENT if on else "#fff"}" stroke="#000" stroke-width="4"/>')
    return "".join(out), W, H


def cards_body(items, cap, W=1600, name="cards", fs=30, cs=22, arrows=True, n_cols=None):
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
    return cards_body([("Idea", "explore · brainstorm"), ("Composition", "build · layer · refine"), ("Mix", "levels · EQ · panning"),
                       ("Presentation", "bounce · present")],
                      "Idea, composition, mix, presentation: the whole cycle, start to finish", W, name, fs, cs, True)


def proposal_body(W=1600, name="proposal pic", fs=30, cs=22):
    return cards_body([("Concept", "what you are making"), ("Tools", "what you will use in Logic"),
                       ("Sound", "what it will sound like")],
                      "One paragraph that answers all three, submitted on your class page", W, name, fs, cs, False)


def plan_body(W=1600, name="plan", fs=24, ts=20):
    gx = 200
    pwid = W - gx - 16

    def X(t):
        return gx + pwid * t / TOTAL_S

    out = []
    sh = 58
    shade = {"Intro": "#4a4a4a", "Verse": "#000", "Chorus": ACCENT, "Break": "#4a4a4a", "Outro": "#4a4a4a"}
    for nm, a, b in SECTIONS:
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{shade[nm]}"/>')
        out.append(D.t_((X(a) + X(b)) / 2, sh / 2 + fs * .36 + 2, nm.upper(), fs - 4, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 4, X(b) - X(a) - 10)
    lh, lg = 56, 10
    y0 = sh + 18
    for i, nm in enumerate(LANES):
        yy = y0 + i * (lh + lg)
        out.append(D.t_(gx - 14, yy + lh / 2 + 8, nm.upper(), 22, 700, anchor="end"))
        D.lab(name + " lanes", nm.upper(), 22, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.4"/>')
        if nm == "Drums":
            for a, b in SPANS[nm]:
                k = 0
                while a + k * 2 * 60 / BPM < b - 1e-9:
                    t = a + k * 2 * 60 / BPM
                    tall = k % 2 == 0
                    h_ = lh - 18 if tall else lh - 34
                    out.append(f'<rect x="{X(t) - 1.5:.1f}" y="{yy + (lh - h_) / 2:.1f}" width="4" height="{h_}" rx="2" fill="#000"/>')
                    k += 1
        elif nm == "Bass":
            for a, b in SPANS[nm]:
                bars = int(round((b - a) / BAR_S))
                for j in range(bars):
                    t0 = a + j * BAR_S
                    st = BASS_NOTES[j % len(BASS_NOTES)]
                    out.append(f'<rect x="{X(t0) + 1:.1f}" y="{yy + 8 + (3 - st) * 9:.1f}" width="{X(t0 + BAR_S) - X(t0) - 2:.1f}" height="15" rx="3" fill="{ACCENT}"/>')
        elif nm == "Chords":
            for a, b in SPANS[nm]:
                j = 0
                t0 = a
                while t0 < b - 1e-9:
                    t1 = min(b, t0 + 4 * BAR_S)
                    out.append(f'<rect x="{X(t0) + 1:.1f}" y="{yy + 14}" width="{X(t1) - X(t0) - 2:.1f}" height="{lh - 28}" rx="5" fill="{"#7a7a7a" if j % 2 == 0 else "#4a4a4a"}"/>')
                    t0 = t1
                    j += 1
        elif nm == "Melody":
            for a, b in SPANS[nm]:
                bars = int(round((b - a) / BAR_S))
                for j in range(bars):
                    t0 = a + j * BAR_S
                    st = (0, 2, 1, 3, 2, 1, 0, 2)[j % 8]
                    out.append(f'<rect x="{X(t0) + 3:.1f}" y="{yy + 6 + (3 - st) * 9:.1f}" width="{X(t0 + BAR_S) - X(t0) - 6:.1f}" height="12" rx="6" fill="#000"/>')
        else:
            for a, b in RISERS:
                out.append(f'<polygon points="{X(a):.1f},{yy + lh - 8} {X(b):.1f},{yy + 8} {X(b):.1f},{yy + lh - 8}" fill="{ACC_LIGHT}" stroke="{ACCENT}" stroke-width="3"/>')
    ty = y0 + len(LANES) * (lh + lg) + 4
    for t in (0, 10, 40, 60, 90, 110, 120, 140, 150):
        lbl = mmss(t)
        anc = "start" if t == 0 else ("end" if t == TOTAL_S else "middle")
        out.append(f'<line x1="{X(t):.1f}" y1="{ty - 6}" x2="{X(t):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(t) + (2 if t == 0 else (-2 if t == TOTAL_S else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 80)
    return "".join(out), W, ty + ts + 22


DRAWINGS = {"hero": lambda: D.stack([hero_body()], 40), "cycle": lambda: cycle_body(1600), "proposal": lambda: proposal_body(1600),
            "arrange": lambda: plan_body(1600, "arrange pic")}
DRAWING_PX = {"hero": 1900, "cycle": 2000, "proposal": 2000, "arrange": 2000}
SIDE = {"cycle": ["Idea: explore and brainstorm", "Composition: build and refine", "Mix: balance every track", "Present and get feedback"],
        "proposal": ["Concept: what it is", "Tools: what you will use", "Sound: what it will be like", "More than one sentence"],
        "arrange": ["An invented 2:30 piece on paper", "Sections you can name", "Layers that come and go", "Plan it, then follow through"]}


def label_extras():
    plan_body(1250, "page arrange", 24, 20)
    cycle_body(1250, "page cycle", 28, 20)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Free Play", "Make whatever you want. Finish it.",
     "Class 1, the first minute. No audio is included in this deck. Open with my overview: this is your chance to make whatever you want. "
     "Use Logic Pro to explore any style, technique or idea that excites you. The only rule is to have a plan and follow through. Say that "
     "the project is about finding a creative voice and showing you can manage a project from start to finish."),
    (1, "listen", "Think: what would you make?", "If anything were allowed · Think, then share|Teacher: no audio is needed. Ask the questions "
     "aloud and take a few answers.|If nobody could say no, what would you make?|What style or sound do you keep coming back to?|"
     "What is one thing you want to try in Logic?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker and no one else's music is used. The point is "
     "that Free Play only works if students pick something they care about, and that is harder than it sounds: the freedom is the "
     "challenge. This sets up my first struggle, analysis paralysis, which comes up on slide 7."),
    (1, "bullets", "What is Free Play?", "Any style, technique or idea that excites you|One rule: have a plan and follow through|Show you can "
     "manage a project from start to finish|Goal: build confidence in your own creative decisions",
     "My overview and fourth goal, shortened to fit the slide. Use Logic Pro to explore any style, technique or idea that excites you. The "
     "only rule: have a plan and follow through. The project is about finding your creative voice and showing that you can manage a "
     "project from start to finish. Goal four: build confidence in making creative decisions independently. Students write the four "
     "vocabulary terms in their own words on the vocabulary page: DAW, bounce or export, arrangement and project proposal."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: introduction, project overview, explore Logic, brainstorm ideas. Class 2: "
     "write and submit project proposals on your class page. Classes 3 to 5 are working days: compose, build, refine. Class 6: final mix, "
     "bounce, and prepare presentations, and students write their three Padlet feedback questions. Class 7: presentations with Padlet Q "
     "and A peer feedback. Hand out the project sheet now."),
    (1, "pic", "The production cycle", "cycle",
     "Class 1. My third goal is to practice the full production cycle: idea, composition, mix, presentation. Every project in this course "
     "follows it, and this is the first time students run it with no rules about what to make. Point to each box and say when it "
     "happens: the idea today and Class 2, composition on the working days, the mix and bounce in Class 6, the presentation in Class 7."),
    (1, "steps", "Step 1: explore", "Open Logic and experiment with sounds|Brainstorm ideas|Write down two or three, not just one|"
     "Pick one before the end of class|Fill in the Idea sketchpad",
     "Step 1 of the project sheet, shortened to fit the slide: explore. Open Logic, experiment with sounds and brainstorm ideas. The last "
     "three lines on the slide are the kit's own suggestions, not my steps: write down two or three ideas, pick one before the end of "
     "class, and use the Idea sketchpad. If a student cannot pick, offer the Idea starters page; my Easier variation is a short list of "
     "prompts to choose from."),
    (1, "bullets", "Commit early", "Get something down early, then refine as you go|Don't spend 3 days picking sounds|Ideas can shift "
     "while you work|Stuck? Listen to music that inspires you",
     "My tips 1, 2 and 3, shortened to fit the slide. Tip 1: start with a clear idea, but let it evolve; some of the best projects shift "
     "direction. Tip 2: do not spend three days picking sounds; get something down early and refine as you go. Tip 3: if you get stuck, "
     "listen to music that inspires you and notice what they did. This answers my first struggle, analysis paralysis: encourage students "
     "to commit to an idea early and iterate."),
    (2, "pic", "A proposal has three parts", "proposal",
     "Class 2. Step 2 of the project sheet, shortened here: write a paragraph describing your concept, your tools, and what the final "
     "product will sound like, and submit it on your class page. Those are the three boxes. My second struggle is weak proposals: some "
     "students write one vague sentence, so push them to describe what the track will sound like and which tools they will use. The "
     "Proposal planner has a sentence frame for each part."),
    (2, "bullets", "Vague or clear?", "Vague: “I will make a chill beat.”|Clear: what it is, which tools, what it sounds like|Say the "
     "tempo, the mood and the instruments|Name the Logic tools you will use",
     "A quick contrast; the vague example is the kit's own, not mine. Read it aloud, then ask what it would sound like: nobody can say. "
     "Then read the clear version from the worked example page, an invented piece on paper. A clear proposal gives the concept, the "
     "tools and the sound. My second struggle, shortened: a one-sentence proposal needs to be pushed to say what the track will sound like "
     "and which tools it will use."),
    (2, "check", "Before you submit", "A concept: what you are making|Tools: what you will use in Logic|What it will sound like|A "
     "paragraph, not one sentence|Submitted on your class page",
     "The checklist is the kit's own, built from step 2 and my second struggle; step 2 is shortened here. Students tick each line on the "
     "Proposal planner before they submit. Read every proposal before the student starts building, and send a vague one back with a "
     "question rather than a grade. The proposal also becomes evidence for the Documentation and Presentation row of my rubric."),
    (3, "bullets", "Steps 3 and 4: build, develop", "Lay down the foundation: drums, chords, bass|Begin shaping the arrangement|Add layers, "
     "melodies, FX and transitions|Refine your sound and structure",
     "Class 3 is the first working day, and Classes 4 and 5 continue it. Steps 3 and 4 of the project sheet, shortened to fit the slide. "
     "Step 3, build: lay down your foundation of drums, chords and bass and begin shaping your arrangement. Step 4, develop: add layers, "
     "melodies, FX and transitions, and refine your sound and structure. Hand out the Work plan so students can say what they will finish "
     "each class."),
    (3, "pic", "Worked example: 2:30 on paper", "arrange",
     "Class 3. An invented piece, Late Bus Home, described on paper; nothing here is audio. It is 96 beats per minute and 60 bars of 4/4, "
     "which is two minutes thirty. Read the sections across the top: intro, verse, chorus, verse, chorus, a short break, a last chorus and "
     "an outro. The lanes show drums, bass and chords entering after the intro, the melody in the choruses and the break, and short risers "
     "before each chorus. The full proposal, the arrangement numbers and a mix plan are on the worked example page."),
    (4, "bullets", "Keep building", "Check your track against your proposal|Add one new thing every class|Try a transition between "
     "sections|Save a new version before big changes",
     "Class 4, a working day. These four lines are the kit's own suggestions for the middle of the project, not my steps. Ask each student "
     "to read their proposal and say whether the track still matches it; it can change, but they should know it has. A transition between "
     "sections, a riser or a drop out, is a quick way to make a loop feel like a piece. Saving a new version first means a bad experiment "
     "costs nothing."),
    (4, "bullets", "Mix time is not optional", "Leave at least one full class for the final mix|Balance levels, EQ and panning on all "
     "tracks|Listen on headphones AND speakers|Mixing takes longer than you think",
     "My third struggle, shortened: students underestimate how long mixing takes, so remind them to leave at least one full class for "
     "final mixing and bounce. Requirement 3, shortened: apply basic mixing (EQ, panning and volume balancing) on all tracks. Tip 4, "
     "shortened: listen to your track on headphones and speakers before you call it done. Ask students to say which class they will "
     "start mixing on and write it on the Work plan."),
    (6, "steps", "Steps 5 and 6: mix, finalize", "Balance levels, apply EQ and panning|Clean up your project|Bounce your final track|Prepare "
     "your presentation|Write your 3 Padlet questions",
     "Class 6. Steps 5 and 6 of the project sheet, shortened to fit the slide. Step 5: mix, balancing your levels, applying EQ and panning "
     "and cleaning up your project. Step 6: finalize, bouncing your final track and preparing your presentation. The last line is from "
     "my pacing guide: students write their three Padlet feedback questions today. Zip the .logicx in Finder (Control-click, Compress)."),
    (6, "check", "What you turn in", "Proposal paragraph on your class page|Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – "
     "Free Play|Padlet post with your 3 questions|Answer 2 questions on classmates’ posts",
     "The submission checklist from the project sheet, shortened to fit the slide. Show where students upload (your class page) and where "
     "the Padlet board is. The proposal should already be in from Class 2; if it is not, this is the last chance."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play your track|Say what you set out to make, and what changed|Your Padlet post: 3 questions about "
     "your project|Answer at least 2 of each classmate’s 3",
     "Class 7, presentations with Padlet Q and A. Step 7 of the project sheet, shortened to fit the slide: create your own Padlet post "
     "with 3 questions you want classmates to answer, present to the class, and during classmates' presentations answer at least 2 of "
     "their 3 questions. Remind the class that thoughtful questions lead to better feedback, my fourth struggle. Ask each student to "
     "say what they set out to make before they play it."),
    (7, "closer", "One last thing…", "You had a plan.|You followed through.|You made it your way.|Now play it.",
     "Close with what my teacher notes say this project does: it is a diagnostic project as much as a creative one, and it sets up the "
     "proposal and Padlet Q and A workflow students will use all semester. Tell them the next project starts from a menu, and they will "
     "write another proposal."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("example", "Worked example", "an invented piece on paper"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 5, 8, 12, 17]
SHOTS3 = [("example", "Worked example"), ("proposal", "Proposal planner"), ("sketch", "Idea sketchpad"), ("workplan", "Work plan"),
          ("ideas", "Idea starters"), ("proj2", "Steps"), ("setup", "Setup"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "changes", "logicref", "ideas", "example",
        "sketch", "proposal", "workplan", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "example", "proj2", "rubric"]

COVER_A = "Make music your way"
COVER_C = "DMP2 · open-ended project · proposal · intro slides"
PDF_COVER = dict(a=30, b=50, c=14, art=7.3)
SQ_COVER = dict(a=44, b=150, c=27, art=740, gap=44)
SQ_B_LINES = ["Free", "Play"]
SQ_SUB = "7 class periods · open-ended · proposal · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Proposal planner, worked example, work plan, idea starters", 28)}
SQ_BANDS = {1: "Explore <em>·</em> propose <em>·</em> build <em>·</em> mix <em>·</em> present",
            2: "Hook <em>·</em> production cycle <em>·</em> proposal <em>·</em> mix time",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, video, songs or examples are included. Students make every sound in their tracks themselves, so everything in "
             "their projects is their own. For the Class 1 hook, you only ask questions aloud.")
CREDITS = ["Worked example (an invented 2-minute-30 piece described on paper), the production cycle, proposal and arrangement-map "
           "drawings and layouts: original work, Hudson Beat.",
           "No audio, video, lyrics, album art, screenshots, presets or chart data are included. No student work is included. Padlet is "
           "named only as an example of a tool you may already use."]
LOGIC_INTRO = ("Where to find the tools a Free Play project is likely to use. Demonstrate what your class needs on Classes 1 and 3 and then "
               "let students work. Names are from current Logic Pro versions; check the labels on yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add tracks with Track › New Tracks…: a Software Instrument track for MIDI "
              "sounds, an Audio track for recordings, a drum track for beats."),
             ("Play and record MIDI", "Use a MIDI keyboard, or turn on Musical Typing (Command-K) to play from the computer keyboard. "
              "Arm the track and press Record (R)."),
             ("Apple Loops", "Open the Loop Browser (O) to find ready-made loops. My Harder variation asks for original MIDI tracks and no "
              "Apple Loops, so decide your rule before Class 1."),
             ("Arrangement", "Copy and paste regions to build sections, and name and color them so every section is easy to see. "
              "Sketch the whole form first, then fill it in."),
             ("Mixer: volume and panning", "Press X to open the Mixer. Move each track’s fader for volume and its Pan knob to place it "
              "left or right."),
             ("EQ", "Add Channel EQ to the channel strip. Cut what you do not need before you boost anything, and check the result "
              "with the track soloed and in the full mix."),
             ("Effects", "Insert effects on the channel strip, for example a reverb or a delay, and keep them subtle until the rest of the "
              "mix is balanced."),
             ("Transitions", "A reverse sound, a riser, a drop out or a filter sweep can join two sections. Draw it with automation or "
              "build it from a sound."),
             ("Automation", "Press A to show automation, choose a parameter such as volume or a filter, and draw changes over time."),
             ("Save versions", "Use File › Save As… with a numbered name before each big change."),
             ("Bounce and zip", "File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and "
              "choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; proposal, .mp3 or .wav and zipped .logicx submitted", "Padlet post created with my 3 questions",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my project:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Analysis paralysis: the Idea starters (page @IDEAS) and the Idea sketchpad (page @SKETCH).</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Weak proposals: the Proposal planner (page @PROPOSAL) and the worked example (page @EXAMPLE).</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Time management: the Work plan (page @WORKPLAN) and slide 14, which protects mix time.</li>'
    '<li style="font-size:10.8pt;margin-bottom:0">Q&amp;A as an afterthought: the presentation planner (page @PRESENT) has students write the three questions early.</li></ul></div>')
TN1_SIZE = 15
PROJ_SIZE = 14.2
VOCAB_GAP = 40
LOGIC_SIZE = 10.4
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example", "How to use, overview, setup, pacing, teacher notes, what changed, Logic quick "
              "reference, idea starters, worked example"),
             ("Student pages", "sketch", "reflect", "Idea sketchpad, Proposal planner, Work plan, project sheet (3 pages), "
              "rubric, vocabulary, feedback planner, reflection"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period open-ended project for high school music '
             f'technology. Each student picks any style, technique or idea, writes a proposal paragraph, builds the track in Logic, '
             f'mixes it, bounces it and presents it, with Padlet questions for feedback. It is the project from my Digital Music '
             f'Production 2 course (focus: creative freedom), and the projects in that course can be taught in any order. '
             f'My teacher notes call it a diagnostic project as much as a creative one.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Set up the Presentation Padlet and the submission spot (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("sketch")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Class 5 is a working day with no new slide. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}: a short list of prompts to choose from (page {D.IX("ideas")} has twelve), or a minimum length, original MIDI tracks only, or an artist statement.</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Any style:</b> the project is open, so the pages never name a genre; students fill in their own.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students pick '
             f'something they care about, write a plan, follow it through the whole production cycle and play the result for the class.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:14pt;line-height:1.55">One finished track in a style of the student’s choosing, as long as it feels '
             f'complete and uses a variety of tracks and instruments, with EQ, panning and volume balanced on every track. They hand in a '
             f'proposal paragraph, a bounced .mp3 or .wav and the zipped .logicx project, plus a Padlet post with three feedback questions, '
             f'then play the track and present it.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:13pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:12pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:13pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.6pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: explore, propose, three working days, mix and bounce, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: instruments, arrangement, mixing with EQ and panning, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a feedback board, a place to submit files, and speakers if you can</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:12pt">Students should already '
             f'know how to open a project, add and play instruments, build a beat or chords, and save, bounce and zip in Logic. Nothing new '
             f'is taught: the quick reference (page {D.IX("logicref")}) shows where each tool lives.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Open-ended", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 12.4pt; line-height: 1.48; margin-bottom: 7pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the final listen.</li>'
             f'<li><b>A place to submit</b> the proposal paragraph, an .mp3 or .wav and a zipped .logicx project (your class page).</li>'
             f'<li><b>The Presentation Padlet</b>, set up before Class 1 (my resource: this is yours to set up; none is included).</li>'
             f'<li><b>A rule about Apple Loops.</b> My sheets do not forbid them, and my Harder variation asks for none. Decide before Class 1.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("sketch")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:12.4pt;margin-bottom:9pt") for c in [
                 "Set up the Presentation Padlet in your class page before Class 1.",
                 "Check that a student computer opens Logic and plays back through headphones.",
                 "Decide how students will choose: free choice, or a short list from page @IDEAS (my Easier variation).",
                 "Print the student pages; set up the submission spot for the proposal."]).replace("@IDEAS", str(D.IX("ideas"))) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch (my closing note)", True)}'
             f'<p style="font-size:12pt">This is a diagnostic project. Use it to calibrate your expectations for the group: note who manages '
             f'time well, who needs more structure, and who might be ready for bigger challenges.</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Kit suggestions, not part of my sheets</span><ul style="margin:0">'
             f'<li style="font-size:12pt">While students work, ask three questions: What does it sound like so far? What is the next '
             f'thing you will add? What would you cut if you ran out of time?</li>'
             f'<li style="font-size:12pt">The Work plan (page {D.IX("workplan")}) shows time management in the students’ own words.</li>'
             f'<li style="font-size:12pt">Keep a running list of who needed a nudge and when.</li></ul></div>'
             f'{D.H2("Music they did not make")}'
             f'<div class="box"><span class="k">A kit suggestion</span><p style="margin:0;font-size:11.6pt;line-height:1.45">'
             f'If a student recreates a song they like (my Easier variation), they build their own version in Logic. No one else’s audio goes '
             f'into the project, and only the student’s own track is bounced and submitted.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.6pt;line-height:1.45">'
             f'Tell students to start with the headphones low and to check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


def ideas_page(n, wm=False):
    cols = "".join(f'<div class="box{" acc-b" if i % 2 == 0 else ""}"><span class="k">{h}</span><ul style="margin:0">'
                   + "".join(f'<li style="font-size:11.4pt;margin-bottom:3pt">{x}</li>' for x in xs) + '</ul></div>'
                   for i, (h, xs) in enumerate(STARTERS))
    inner = (f'<p style="margin:0 0 6pt;font-size:12pt">My Easier variation is a list of 3–5 prompts students can choose from, to '
             f'reduce overwhelm. Twelve prompts you can cut down to a short list. Two are my own examples; the rest are kit suggestions. '
             f'None is a requirement.</p>'
             f'{D.H2("Twelve starter prompts (kit suggestions)", True)}'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8pt">{cols}</div>'
             f'{D.H2("My Harder variation, laid out")}'
             f'<table class="t" style="font-size:12pt;line-height:1.5"><tr><th style="width:30%">My option</th><th>How to use it</th></tr>'
             f'<tr><td><b>Minimum track length</b></td><td>2+ minutes. The worked example (page {D.IX("example")}) is 2:30, so you can show what that '
             f'looks like in sections.</td></tr>'
             f'<tr><td><b>Original MIDI tracks</b></td><td>A set number, with no Apple Loops. Tell students the number on Class 1.</td></tr>'
             f'<tr><td><b>Artist statement</b></td><td>A written statement explaining their creative choices. It adds to the Reflection page '
             f'(page {D.IX("reflect")}); it does not add a rubric row.</td></tr></table>'
             f'<div class="box acc-b" style="margin-top:8pt"><span class="k">How to use this page</span><p style="margin:0;font-size:12pt;line-height:1.5">'
             f'Pick 3–5 prompts, put them on the board on Class 1 and let students choose one or write their own. Free Play stays free: '
             f'a student may ignore the list. The Idea sketchpad (page {D.IX("sketch")}) is where they write down what they pick.</p></div>')
    return D.page("Idea starters and my Harder variation", "TEACHER", "Easier + Harder", inner, n, key="ideas")


def example_page(n, wm=False):
    rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in MIX_ROWS)
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt">An <b>invented piece, “{PIECE}”, described on paper</b>: no audio is included, '
             f'so the numbers are easy to check. Students’ projects will differ.</p>'
             f'<div class="cols" style="gap:10pt"><div class="box"><span class="k">1 · A vague proposal</span><p style="margin:0;font-size:11pt">{WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:10pt">Nobody can say what it sounds like or which tools it needs.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear proposal (concept, tools, sound)</span><p style="margin:0;font-size:9.8pt;line-height:1.36">{STRONG}</p></div></div>'
             f'{D.H2("3 · The arrangement map: 2:30")}<div style="width:6.2in;margin:1pt auto 3pt">{D.body_svg(plan_body(1250, "page arrange", 24, 20))}</div>'
             f'<div class="box acc-b"><span class="k">4 · Checking the numbers, and why it works</span>'
             f'<p style="margin:0;font-size:10.4pt;line-height:1.38">{BPM} beats per minute is {60 / BPM:g} s a beat, so a bar of 4/4 is {BAR_S:g} s. '
             f'Sections: {" + ".join(str(b) for b in SECTION_BARS)} = {BARS} bars, and {BARS} × {BAR_S:g} s = {TOTAL_S} s = 2:30, as the proposal says. '
             f'Every section has a job and something changes each time: layers enter, the melody arrives in the choruses, a riser leads into each '
             f'chorus and the break strips the track back.</p></div>'
             f'{D.H2("5 · A mix plan: EQ, panning and volume on every track")}'
             f'<table class="t" style="font-size:9.8pt;line-height:1.28"><tr><th style="width:11%">Track</th><th style="width:30%">Volume</th>'
             f'<th style="width:19%">Panning</th><th>EQ</th></tr>{rows}</table>'
             f'<p style="font-size:10pt;line-height:1.35;margin:3pt 0 0"><b>6 · Three Padlet questions (invented):</b> {qs}</p>')
    return D.page("Worked example · an invented piece", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def sketch_page(n, wm=False):
    rows = "".join("<tr><td style='height:40pt'></td><td></td><td></td></tr>" for _ in range(3))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Step 1: open Logic, experiment with sounds, and brainstorm ideas. Write down two or '
             f'three ideas, not just one, then pick one before the end of class. You can change it later; you cannot start without one.</p>'
             f'<div class="fl"><b>Styles or sounds I keep coming back to:</b><span></span></div>'
             f'<div class="fl"><b>Three words for the mood I want:</b><span></span></div>'
             f'<div class="fl"><b>Something I want to try in Logic:</b><span></span></div>'
             f'<table class="map" style="margin-top:4pt"><tr><th style="width:8%">Idea</th><th style="width:50%">What it is, in one or two lines</th>'
             f'<th>Can I finish it in 7 classes? Why?</th></tr>'
             + "".join(f"<tr><td style='height:58pt'><b>{c}</b></td><td></td><td></td></tr>" for c in "ABC") + '</table>'
             f'<div class="box acc-b" style="margin-top:9pt"><span class="k">Commit</span>'
             f'<div class="fl" style="margin-top:4pt"><b>I am making:</b><span></span></div>'
             f'<div class="fl"><b>I will start with (a sound, a beat, a chord):</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>One thing that could go wrong, and my plan for it:</b><span></span></div></div>'
             f'<div class="box" style="margin-top:9pt"><span class="k">Stuck? (tips 2 and 3 from my project sheet)</span><p style="margin:0;font-size:11pt">'
             f'Do not spend three days picking sounds: get something down early and refine as you go. If you are stuck, listen to music '
             f'that inspires you, notice what they did and try something similar in your own project.</p></div>')
    return D.page("Idea sketchpad", "STUDENT", "Class 1", inner, n, wm, name=True, key="sketch")


def proposal_page(n, wm=False):
    inner = (f'<p style="margin:0 0 4pt;font-size:11pt">Step 2: write a paragraph describing your concept, tools, and what the final product '
             f'will sound like. Submit it on your class page. Use the frames to start; change them to sound like you.</p>'
             f'<table class="map"><tr><th style="width:17%">Part</th><th style="width:34%">Start with</th><th>My answer</th></tr>'
             f'<tr><td style="height:46pt"><b>Concept</b></td><td>I am making…, about… long, in a style that…</td><td></td></tr>'
             f'<tr><td style="height:46pt"><b>Tools</b></td><td>In Logic I will use… (instruments, drums, EQ, panning, FX)</td><td></td></tr>'
             f'<tr><td style="height:46pt"><b>Sound</b></td><td>It will sound… at about… beats per minute, and it will…</td><td></td></tr></table>'
             f'{D.H2("My proposal paragraph")}{D.lines(8, 25)}'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">Before you submit</span>'
             + "".join(D.chk(c, 12, "font-size:10.8pt;margin-bottom:3pt") for c in [
                 "It says what I am making (the concept)",
                 "It names the Logic tools I will use",
                 "It says what the final product will sound like",
                 "It is a paragraph, not one sentence",
                 "I submitted it on our class page"]) + '</div>')
    return D.page("Proposal planner", "STUDENT", "Class 2", inner, n, wm, name=True, key="proposal")


def workplan_page(n, wm=False):
    rows = [("Class 1", "Explore and brainstorm; pick an idea"), ("Class 2", "Proposal submitted"), ("Class 3", ""), ("Class 4", ""),
            ("Class 5", ""), ("Class 6", "Final mix, bounce; write 3 Padlet questions"), ("Class 7", "Present; answer 2 questions")]
    trs = "".join(f"<tr><td style='height:52pt'><b>{a}</b></td><td style='font-size:9.4pt'>{b}</td><td></td><td></td></tr>" for a, b in rows)
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Steps 3 and 4: lay down your foundation and shape your arrangement, then add layers, '
             f'melodies, FX and transitions. Before each class write what you plan to finish; after it, what you actually did.</p>'
             f'<table class="map"><tr><th style="width:11%">Class</th><th style="width:22%">Fixed by the schedule</th>'
             f'<th style="width:34%">What I plan to finish</th><th>What I actually finished</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:9pt"><span class="k">Protect your mix time</span>'
             f'<p style="margin:0 0 4pt;font-size:10.8pt">Students underestimate how long mixing takes. Leave at least one full class for final mixing and bounce.</p>'
             f'<div class="fl" style="margin:0"><b>I will start mixing in Class</b><span style="flex:0 0 0.7in"></span><b>because</b><span></span></div></div>'
             f'<div class="fl" style="margin-top:8pt"><b>The part of my track I am proudest of so far:</b><span></span></div>'
             f'<div class="fl"><b>The part that is not working yet:</b><span></span></div>')
    return D.page("Work plan", "STUDENT", "Classes 3–5", inner, n, wm, name=True, key="workplan")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "ideas": ideas_page, "example": example_page,
         "sketch": sketch_page, "proposal": proposal_page, "workplan": workplan_page}


# ================================================================ content checks (example arithmetic, owner text, no audio)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 4), reqs=(REQS, 4), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 3))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp} (the owner's count)")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is the owner's /25, levels 1-5")
    if [c for c, _ in RUBRIC] != ["Creativity & Originality", "Technical Skill / DAW Use", "Composition & Structure",
                                  "Sound Design & Mix Quality", "Documentation & Presentation"]:
        errs.append("rubric categories must be the owner's, in order")
    if FILE_NAME not in CHECK[3] or "Free Play" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    if "EQ, panning, and volume" not in REQS[2]:
        errs.append("requirement 3: basic mixing")
    # the worked example adds up
    if BAR_S != 2.5 or BARS * BAR_S != TOTAL_S or sum(SECTION_BARS) != BARS:
        errs.append("96 BPM: 2.5 s per bar, 60 bars, 150 s")
    if TOTAL_S < 120:
        errs.append("example is 2+ minutes (my Harder variation's minimum)")
    if SECTIONS[0][1] != 0 or SECTIONS[-1][2] != TOTAL_S or any(b != c for (_, _, b), (_, c, _) in zip(SECTIONS, SECTIONS[1:])):
        errs.append("sections must tile the piece")
    if [round((b - a) / BAR_S) for _, a, b in SECTIONS] != SECTION_BARS:
        errs.append("section lengths must match their bars")
    if any(not 0 <= a < b <= TOTAL_S for sp in SPANS.values() for a, b in sp) or any(not 0 <= a < b <= TOTAL_S for a, b in RISERS):
        errs.append("layer spans and risers inside the piece")
    for lane in ("Drums", "Bass", "Chords"):
        if not any(a <= 40 and b >= 60 for a, b in SPANS[lane]):
            errs.append(f"{lane} must play through the first chorus")
    if len(MIX_ROWS) != 5 or [r[0] for r in MIX_ROWS] != [l for l in LANES]:
        errs.append("a mix row (volume, panning, EQ) for every lane")
    if len(QUESTIONS) != 3:
        errs.append("three Padlet questions")
    if sum(len(x) for _, x in STARTERS) != 12:
        errs.append("twelve starter prompts")
    for need in ("I am making", "In Logic I will use", "It will sound"):
        if need not in STRONG:
            errs.append(f"the clear proposal must cover concept, tools and sound ({need})")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    txt = " ".join(flat)
    for need in ("No audio, video, songs or examples are included", "invented piece, “Late Bus Home”",
                 "Your Name – Free Play", "Final Grade = Average of Student + Teacher", "No student work is included"):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up:
        errs.append("UPLOAD.md: must say no audio is included and record the open questions")
    for i in (2, 5, 6, 7, 9, 10, 13, 14, 15, 17):   # slides that shorten the owner's wording must say so
        if "shortened" not in notes[i].lower() and "shortens" not in notes[i].lower():
            errs.append(f"deck slide {i + 1} notes: must say the owner's wording is shortened")
    ch = flat[D.IX("changes") - 1]
    for s in ("slide 3", "slide 6", "slide 7", "slides 8 and 10", "slide 11", "slide 14", "slide 15", "slide 16", "slide 18"):
        if s not in ch:
            errs.append(f"'What changed' page must list {s}")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or any("Work plan" in g or "Reflection" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in ("Billie", "Beatles", "Spotify", "Daft", "Skrillex", "Disney", "Minecraft", "Mario", "Taylor", "Nirvana", "Radiohead"):
        if banned in alldeck or banned in txt:
            errs.append(f"must not name songs, artists or services beyond the owner's ({banned})")
    return errs


def check_summary():
    return (f"The invented piece is {TOTAL_S} s ({BPM} BPM, {BARS} bars of {BAR_S:g} s; sections {'+'.join(map(str, SECTION_BARS))} bars) with "
            f"a mix row for every layer; "
            f"the owner's lists counted (4 goals, 4 terms, 4 requirements, 7 steps, 4 tips, 6 checklist items, 4 struggles, 3 resources); "
            f"{len(CHANGES)} wording changes disclosed; no audio or student work included; grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
