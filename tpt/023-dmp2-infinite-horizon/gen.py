#!/usr/bin/env python3
"""DMP2 project: Infinite Horizon (TpT 023): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Infinite Horizon > "Infinite Horizon - Project Sheet & Rubric" (rubric 5 categories scored 1-5, /25, final
grade = average of student and teacher scores), TEACHER NOTES > "Infinite Horizon - Teacher Notes" (7 class periods), and the project's
entry on "DMP2 - Project Menu" (the June 2026 menu; owner, 17 Oct 2026: the June entry may be quoted). These three set the project
text, steps, rubric and pacing (owner rule, 17 Oct 2026). The older Projects > Infinite Horizon (Soundscape project) folder holds only
a 2025 .docx outline, which is not a source; Drive holds no template, example or other artifact for this project.

LEFT OUT ON PURPOSE: the Teacher Notes name an ambient album and three artists (individual third-party authors) for reference
listening. The kit names none of them and includes no audio; the teacher chooses what to play. The Easier variation's starter template
is a Logic project that the Drive does not hold, so the kit lays it out as a recipe on paper (page "starter").
NO AUDIO IS INCLUDED. The worked example is an invented 75-second piece ("Slow Tide") described on paper: four phases, five layers and
five automation lanes. Every picture (horizon hero, steps, phases, automation lanes, automation map) is drawn in code.
The sheet has no reflection task (the rubric only mentions reflection), so the shared Reflection element stays ON (default).
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "infinite-horizon"
TITLE = "Infinite Horizon"
ACCENT = "#C2571A"          # this product's single accent: horizon orange (008 red ... 021 indigo, 022 lake cyan)
ACC_LIGHT = "#F4DCCB"
PRICE = "10.00"
CLASSES = 7
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-022).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "Infinite Horizon in Logic Pro | Ambient Soundscape Project | High School"
DESC_START = "Ambient soundscape and automation project for high school:"
DESC_MUST = ["Infinite Horizon", "automation", "no audio", "Padlet"]
ZIP_DIR = "Infinite Horizon - Hudson Beat"
ZIP_DATE = (2026, 10, 19, 12, 0, 0)
TYPE = "Open-Ended Project"
PROJ_LINE = "Digital Music Production | <i>Open-Ended Project</i> | 7 class periods"
DECK_STRAP = "Make a soundscape that never sits still"
BANNED_EXTRA = ["Brian " + "Eno", "Tim " + "Hecker", "Stars of the " + "Lid", "Music for " + "Airports"]   # third-party names the Teacher Notes use

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Open-Ended", "Automation & Texture"
MENU_DESC = "Create an evolving ambient soundscape through automation and modulation. Focus on motion, texture, and space."
OVERVIEW = ("Create a soundscape that never sits still. Design an evolving ambient piece that continuously transforms through automation, "
            "modulation, and layering. No traditional rhythm or song structure — this is about motion, texture, and space.")
GOALS = ["Use automation and modulation to create evolving, non-repeating textures",
         "Layer ambient sounds, drones, synths, and effects for depth",
         "Explore how sound can create mood and atmosphere without traditional structure",
         "Build a 60–90 second soundscape that sustains listener interest"]
VOCAB = [("Soundscape", "An ambient composition focused on texture and atmosphere rather than melody or rhythm"),
         ("Drone", "A sustained tone or chord that creates a foundation for ambient music"),
         ("Automation", "Changing a parameter over time to create movement and evolution"),
         ("Modulation", "Using one signal to control another, adding variation and life to a sound"),
         ("Ambient", "Music focused on tone, atmosphere, and texture rather than traditional song structure")]
REQS = ["Length: 60–90 seconds",
        "Layer ambient textures and drones using synths, samples, and FX",
        "Use automation to change parameters over time (filters, reverb, volume)",
        "Incorporate gradual transitions and evolving movement",
        "Avoid traditional rhythm or song structure — focus on motion and space"]
STEPS = ["<b>Listen</b> — Study examples of ambient and soundscape music for inspiration (Listening log: page @LISTEN)",
         "<b>Build your foundation</b> — Create a drone or pad layer as your base texture (Phase plan: page @PHASES)",
         "<b>Layer</b> — Add additional textures, sounds, and atmospheric elements",
         "<b>Automate</b> — Draw automation on filters, reverb, volume, and panning to create evolution (Automation plan: page @AUTOMATION)",
         "<b>Refine</b> — Listen for flow and pacing. Remove anything that feels static or repetitive. (Listen-back sheet: page @REFINE)",
         "<b>Finalize</b> — Mix for depth and space. Bounce your soundscape.",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["This project is about patience. Let sounds evolve slowly — don’t rush changes.",
        "Reverb and delay are your best friends here. Use them to create a sense of space.",
        "Automate everything. If a parameter stays the same the whole time, your soundscape will feel flat.",
        "Close your eyes while listening to your piece. Does it take you somewhere? That’s the goal."]
FILE_NAME = "“Your Name – Infinite Horizon”"
CHECK = ["Bounced .mp3 or .wav uploaded to your class page",
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
TN_REINFORCES = ("Deep dive into automation, modulation, and effects processing. Challenges students to think about music as atmosphere "
                 "rather than structure.")
STRUGGLES = ["Students default to adding beats. Remind them this is about texture and motion, not rhythm.",
             "Soundscapes feel static because students don’t automate enough parameters. Require a minimum number of automation lanes.",
             "Students struggle without traditional structure to guide them. Suggest thinking in phases: opening, evolution, climax, fade.",
             "Some students find ambient music boring. Play compelling examples."]
VAR_EASY = "Provide a starter template with one drone layer and basic automation. Students add layers on top."
VAR_HARD = "Extend to 2+ minutes. Require at least 5 automation lanes and use of Alchemy for custom ambient patches."
RESOURCES = [("An ambient album for reference listening (named in my notes)",
              "Not named here, and no audio is included: choose your own listening for Class 1 and your compelling examples (my fourth "
              "struggle). The Listening log (page @LISTEN) is where students write what they hear."),
             ("Ambient music production tutorials on YouTube",
              "Kept as I wrote it. No tutorial, video or link is included. The Logic quick reference (page @LOGICREF) says where each "
              "tool lives."),
             ("Logic Pro automation tutorial",
              "Kept as I wrote it. No video is included. The Automation plan (page @AUTOMATION) and the quick reference show what to "
              "draw and where.")]
TN_NOTE = ("This project stretches students’ definition of what music can be. Pair with a brief discussion of ambient and experimental "
           "music history.")
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Creativity &amp; Originality: ask what mood or place the student was after, then listen for it with your eyes closed (my "
                "fourth tip).",
                "Technical Skill: open the project and show the automation lanes (page @AUTOMATION). Count them against the minimum you set.",
                "Composition &amp; Structure: compare the piece with the Phase plan (page @PHASES). Is there a clear opening, evolution, "
                "climax and fade, with no beat?",
                "Sound Design &amp; Mix Quality: listen for depth and space (step 6). Which layers sit far away, which close?",
                "Documentation &amp; Presentation: the Listening log, the Automation plan, the Reflection page (page @REFLECT) and the "
                "Padlet questions are the evidence."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Introduction. Listen to ambient examples. Begin building a drone/pad foundation.",
     "do": "Slides 1–7: hook, what the project is, the steps, five words, steps 1 and 2. Hand out the project sheet and the Listening "
           "log. You choose and play the examples; none is included.", "slides": (1, 7),
     "pages": ["listen", "proj1", "proj2", "proj3", "vocab"],
     "deck": "A sound with no beat · the steps · five words · listen, then build a drone"},
    {"n": 2, "owner": "<b>Class 2:</b> Layer additional textures and atmospheric elements.",
     "do": "Slides 8–10: four phases, texture not rhythm, step 3. Hand out the Phase plan. Check each drone layer is in place.",
     "slides": (8, 10), "pages": ["phases"], "deck": "Opening, evolution, climax, fade · texture, not rhythm · layer"},
    {"n": 3, "owner": "<b>Classes 3–5:</b> Working days — automate, refine, evolve the soundscape.",
     "do": "Slides 11–13: automate everything, step 4 and the worked example on paper. Hand out the Automation plan. Then work time.",
     "slides": (11, 13), "pages": ["automation"], "deck": "Working day: automate, worked example"},
    {"n": 4, "owner": None, "do": "Slides 14–15: patience, and refine. Hand out the Listen-back sheet. Then work time.", "slides": (14, 15),
     "pages": ["refine"], "deck": "Working day: patience, refine, eyes closed"},
    {"n": 5, "owner": None, "do": "Full working day: automate, refine, evolve. Ask each student to play the first 20 seconds and say what "
     "changes in it.", "slides": None, "pages": [], "deck": "Working day: automate, refine, evolve"},
    {"n": 6, "owner": "<b>Class 6:</b> Final mix, bounce. Prepare presentations.",
     "do": "Slides 16–18: mix and bounce, what to turn in, the rubric. Students post their three Padlet questions.", "slides": (16, 18),
     "pages": ["rubric", "present"], "deck": "Mix for depth · bounce · checklist · rubric"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 19–20: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (19, 20), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one rule for Class 1</span>'
    '<p style="margin:0;font-size:9.4pt">Say it twice: this is texture and motion, not rhythm (my first struggle). If a student adds a '
    'beat, ask what they would hear if the beat were taken out.</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:9.4pt">Working days; Class 5 has no new slide. '
    'Circulate with one question: what is moving in your piece right now?</p></div></div>')
PACING_SIZE = 9.6

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (checklist items 1 and 2).",
    "Page numbers are added to steps 1, 2, 4 and 5 (the Listening log, Phase plan, Automation plan and Listen-back sheet).",
    "<b>No artist or album is named.</b> My fourth struggle names three artists and my first resource names an album and its artist, "
    "for reference listening. This kit names no artist and includes no audio, so my fourth struggle reads “Play compelling examples.” "
    "and my first resource is listed as “An ambient album for reference listening (named in my notes)”. You choose what to play.",
    "My Easier variation (a starter template with one drone layer and basic automation) is a Logic project, which is not included. "
    "It is laid out as a recipe on paper (page @STARTER) so you can build it in a few minutes.",
    "My Harder variation (2+ minutes, at least 5 automation lanes, Alchemy for custom ambient patches) is laid out on page @STARTER. "
    "My second struggle asks you to require a minimum number of automation lanes; the number is yours to set.",
    "My resources about YouTube tutorials and a Logic Pro automation tutorial are listed as I wrote them. No tutorial or link is included.",
    "My pacing guide’s “Classes 3–5” row spans the Class 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 3 shortens my overview and a goal, slide 6 shortens "
    "my five vocabulary definitions, slide 7 shortens steps 1 and 2, slide 9 shortens my first struggle and requirement 5, slide 10 "
    "shortens step 3 and requirement 2, slide 12 shortens step 4 and requirements 3 and 4, slide 14 shortens tips 1 to 3, slide 15 "
    "shortens step 5, tip 4 and the Harder variation, slide 16 shortens steps 6 and 7, slide 17 shortens the submission checklist, and "
    "slide 19 shortens step 7.",
]
CHANGES_MUST_MENTION = ["your class page", "Page numbers", "No artist or album", "starter template", "Classes 3–5", "Layout only",
                        "intro deck shortens"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the overview, goals, five vocabulary terms, five requirements, "
        "steps (apart from the page numbers), tips, checklist (apart from the class page) and file name (“Your Name – Infinite "
        "Horizon”), the /25 rubric, what the project reinforces, my first three struggles, the variations, my closing note and the "
        "project menu entry on page @OVERVIEW. No rubric row is added and the requirements are unchanged.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: the how-to, overview and setup pages, the teacher "
                "moves in the pacing guide, the grading suggestions, the suggested minimum of three automation lanes (a kit suggestion on "
                "page @SETUP), the Logic quick reference, the starter-template recipe and Harder variation page, the worked example (an "
                "invented 75-second piece, its phases, layers and automation lanes, on paper, not audio), the Listening log, Phase plan, "
                "Automation plan and Listen-back sheet, the vocabulary and presentation pages and the intro deck. None adds a requirement "
                "or a rubric row.")

# ================================================================ the worked example (Hudson Beat original: an invented piece on paper)
PIECE = "Slow Tide"
TOTAL_S = 75
PHASES = [("Opening", 0, 12), ("Evolution", 12, 45), ("Climax", 45, 63), ("Fade", 63, 75)]
LAYERS = [("Drone", 0, 75, "one low, sustained synth chord that never stops"),
          ("Pad", 8, 70, "a soft, wide synth pad that slowly joins"),
          ("Texture", 16, 63, "filtered noise, like wind far away"),
          ("Chimes", 28, 66, "a few soft bell notes, no pulse, long reverb"),
          ("Sweep", 42, 63, "a noise swell that rises into the climax")]
CHIME_T = [30, 34, 41, 47, 52, 55, 61]
# automation lanes: (layer, parameter, [(time s, value 0-1)])
AUTO = [("Drone", "filter cutoff", [(0, .15), (12, .2), (45, .8), (63, .85), (75, .1)]),
        ("Pad", "reverb send", [(8, .2), (30, .5), (50, .9), (70, .4)]),
        ("Texture", "volume", [(16, 0), (30, .5), (50, .9), (63, 0)]),
        ("Texture", "panning", [(16, .2), (30, .8), (40, .2), (52, .8), (63, .5)]),
        ("Chimes", "delay feedback", [(28, .1), (45, .4), (56, .8), (66, .2)])]
WEAK = "I will make a calm ambient track with a soft beat."
STRONG = ("I am making “Slow Tide”, a 75-second soundscape about the sea coming in. It has no beat. It opens with a low drone, a pad joins "
          "at 8 seconds, and noise and bell notes arrive in the evolution. I will automate the drone’s filter, the pad’s reverb, the "
          "texture’s volume and panning and the chimes’ delay: five lanes, so nothing stays the same. It climbs to a swell at 45 seconds "
          "and fades to the drone alone.")
PHASE_NOTES = [("Opening", "0:00–0:12", "the drone alone, filter nearly closed; the pad joins at 0:08"),
               ("Evolution", "0:12–0:45", "texture and chimes arrive; the filter and reverb open slowly; the texture pans left and right"),
               ("Climax", "0:45–1:03", "the sweep rises, everything is at its fullest and widest, the chimes echo the most"),
               ("Fade", "1:03–1:15", "texture and sweep leave, the pad fades, the filter closes on the drone")]
QUESTIONS = ["Where did you first notice something change?",
             "Which layer could you hear moving, and which was still?",
             "Did your eyes-closed picture match the title?"]
THIN = "I made a calm sound. It was relaxing and I liked it."
USEFUL = ("I thought ambient music would be boring, but watching the filter open made me want to keep listening. My hardest part was "
          "patience: my first version changed too fast. I slowed every automation lane and the climax felt earned. Next time I would "
          "draw the Phase plan first and add the fourth lane sooner. My strongest rubric category is Sound Design; my weakest is "
          "Documentation.")


def mmss(t):
    return f"{int(t) // 60}:{int(round(t)) % 60:02d}"


# ================================================================ drawings (original, code-drawn: black + accent only)
def hero_body():
    W, H = 1100, 560
    out = []
    cx, hy = 550, 330
    for r in (235, 275, 315):
        out.append(f'<path d="M {cx - r} {hy} A {r} {r} 0 0 1 {cx + r} {hy}" fill="none" stroke="#000" stroke-width="3" opacity=".45"/>')
    out.append(f'<path d="M {cx - 190} {hy} A 190 190 0 0 1 {cx + 190} {hy} Z" fill="{ACCENT}" stroke="#000" stroke-width="6"/>')
    out.append(f'<line x1="50" y1="{hy}" x2="1050" y2="{hy}" stroke="#000" stroke-width="10" stroke-linecap="round"/>')
    for i in range(6):
        w = 330 - i * 48
        y = hy + 28 + i * 30
        out.append(f'<rect x="{cx - w / 2}" y="{y}" width="{w}" height="{16 - i}" rx="6" fill="{"#000" if i % 2 == 0 else ACCENT}"/>')
    for k, x in enumerate((120, 200, 880, 970)):
        out.append(f'<line x1="{x}" y1="{hy - 20 - 14 * (k % 2)}" x2="{x}" y2="{hy - 60 - 30 * (k % 2)}" stroke="#000" stroke-width="6" stroke-linecap="round"/>')
    return "".join(out), W, H


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
    return cards_body([("Listen", "ambient examples"), ("Foundation", "a drone or pad"), ("Layer", "textures · sounds"),
                       ("Automate", "filters · reverb"), ("Refine", "cut what is static")],
                      "Then finalize: mix for depth, bounce, present and get feedback", W, name, fs, cs, True)


def phases_body(W=1600, name="phases pic", fs=30, cs=22):
    items = [("Opening", "start quiet"), ("Evolution", "layers join, sounds shift"), ("Climax", "the fullest moment"), ("Fade", "let it go")]
    n = len(items)
    gap = 30
    pw = (W - (n - 1) * gap) / n
    bh = 150
    out = []
    for k, (h, s) in enumerate(items):
        x0 = k * (pw + gap)
        out.append(f'<rect x="{x0:.1f}" y="4" width="{pw:.1f}" height="{bh}" rx="12" fill="{"#000" if k % 2 == 0 else ACCENT}"/>')
        out.append(D.t_(x0 + pw / 2, 4 + bh / 2 - 4, h.upper(), fs, 700, fill_="#fff"))
        D.lab(name + " heads", h.upper(), fs, pw - 30)
        out.append(D.t_(x0 + pw / 2, 4 + bh / 2 + 36, s, cs, 500, fill_="#fff"))
        D.lab(name + " subs", s, cs, pw - 30)
    # one energy curve across the four phases
    base, top = bh + 270, bh + 60
    xs = [0, .13, .35, .6, .75, .88, 1.0]
    ys = [.12, .2, .55, .95, .9, .45, .05]
    pts = " ".join(f"{x * W:.1f},{base - y * (base - top):.1f}" for x, y in zip(xs, ys))
    out.append(f'<line x1="0" y1="{base}" x2="{W}" y2="{base}" stroke="#000" stroke-width="3"/>')
    out.append(f'<polyline points="{pts}" fill="none" stroke="{ACCENT}" stroke-width="10" stroke-linejoin="round" stroke-linecap="round"/>')
    out.append(D.t_(W / 2, base + 46, "How full the sound is, over time", cs + 2, 500))
    D.lab(name + " cap", "How full the sound is, over time", cs + 2, W - 20)
    return "".join(out), W, base + 62


def lanes_body(W=1600, name="lanes pic", fs=30, cs=22):
    rows = [("Filter", "cutoff opens", [(0, .1), (.35, .2), (.7, .8), (1, .95)]),
            ("Reverb", "more space", [(0, .2), (.3, .2), (.5, .6), (1, .9)]),
            ("Volume", "swells in, fades out", [(0, 0), (.3, .5), (.6, .9), (.85, .5), (1, 0)]),
            ("Panning", "drifts left, then right", [(0, .5), (.2, .1), (.45, .9), (.7, .2), (1, .5)])]
    gx, rh, gp = 300, 96, 18
    out = []
    for i, (h, s, pts) in enumerate(rows):
        y = 4 + i * (rh + gp)
        out.append(D.t_(gx - 24, y + rh / 2 + fs * .36, h.upper(), fs, 700, anchor="end"))
        D.lab(name + " heads", h.upper(), fs, gx - 34)
        out.append(f'<rect x="{gx}" y="{y}" width="{W - gx - 4}" height="{rh}" rx="10" fill="#fff" stroke="#000" stroke-width="3"/>')
        pw_ = W - gx - 4 - 60
        xy = [(gx + 30 + t * pw_, y + rh - 14 - v * (rh - 28)) for t, v in pts]
        out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in xy)}" fill="none" stroke="{ACCENT}" stroke-width="8" stroke-linejoin="round"/>')
        for a, b in xy:
            out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="9" fill="#000"/>')
        out.append(D.t_(gx + 40, y + 28, s, cs - 2, 500, anchor="start"))
        D.lab(name + " subs", s, cs - 2, 460)
    hh = 4 + 4 * (rh + gp)
    out.append(D.t_(W / 2, hh + 28, "Every dot is a point you draw; Logic joins them", cs + 2, 500))
    D.lab(name + " cap", "Every dot is a point you draw; Logic joins them", cs + 2, W - 20)
    return "".join(out), W, hh + 44


def map_body(W=1600, name="map", fs=24, ts=20):
    gx = 250
    pwid = W - gx - 16

    def X(t):
        return gx + pwid * t / TOTAL_S

    out = []
    sh = 54
    shade = {"Opening": "#4a4a4a", "Evolution": "#000", "Climax": ACCENT, "Fade": "#4a4a4a"}
    for nm, a, b in PHASES:
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{shade[nm]}"/>')
        out.append(D.t_((X(a) + X(b)) / 2, sh / 2 + fs * .3 + 2, nm.upper(), fs - 4, 700, fill_="#fff"))
        D.lab(name + " phases", nm.upper(), fs - 4, X(b) - X(a) - 10)
    lh, lg = 34, 7
    y0 = sh + 14
    out.append(D.t_(gx - 14, y0 + 6, "LAYERS", fs - 6, 700, anchor="end", fill_=ACCENT))
    for i, (nm, a, b, _d) in enumerate(LAYERS):
        yy = y0 + 16 + i * (lh + lg)
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, nm.upper(), 20, 700, anchor="end"))
        D.lab(name + " lanes", nm.upper(), 20, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        if nm == "Chimes":
            for t in CHIME_T:
                out.append(f'<circle cx="{X(t):.1f}" cy="{yy + lh / 2:.1f}" r="7" fill="#000"/>')
        elif nm == "Sweep":
            out.append(f'<polygon points="{X(a):.1f},{yy + lh - 5} {X(b):.1f},{yy + 5} {X(b):.1f},{yy + lh - 5}" fill="{ACC_LIGHT}" stroke="{ACCENT}" stroke-width="3"/>')
        else:
            fillc = {"Drone": "#4a4a4a", "Pad": "#7a7a7a", "Texture": ACC_LIGHT}[nm]
            out.append(f'<rect x="{X(a):.1f}" y="{yy + 5}" width="{X(b) - X(a):.1f}" height="{lh - 10}" rx="6" fill="{fillc}" stroke="{ACCENT if nm == "Texture" else "#000"}" stroke-width="2"/>')
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
    for t in (0, 12, 45, 63, 75):
        lbl = mmss(t)
        anc = "start" if t == 0 else ("end" if t == TOTAL_S else "middle")
        out.append(f'<line x1="{X(t):.1f}" y1="{ty - 6}" x2="{X(t):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(t) + (2 if t == 0 else (-2 if t == TOTAL_S else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 80)
    return "".join(out), W, ty + ts + 22


DRAWINGS = {"hero": lambda: D.stack([hero_body()], 40), "cycle": lambda: cycle_body(1600), "phases": lambda: phases_body(1600),
            "lanes": lambda: lanes_body(1600), "arrange": lambda: map_body(1600, "arrange pic")}
DRAWING_PX = {"hero": 1900, "cycle": 2000, "phases": 2000, "lanes": 2000, "arrange": 2000}
SIDE = {"cycle": ["Listen to ambient examples", "Build a drone or pad base", "Layer, then automate", "Refine: cut what is static"],
        "phases": ["Opening: start quiet", "Evolution: layers join and shift", "Climax: the fullest moment", "Fade: let it go"],
        "arrange": ["An invented 75-second piece, on paper", "Four phases you can name", "Five layers that join and leave",
                    "Five automation lanes, none flat"]}


def label_extras():
    map_body(1250, "page arrange", 24, 20)
    cycle_body(1250, "page cycle", 28, 20)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Infinite Horizon", "Make a sound that never sits still.",
     "Class 1, the first minute. No audio is included in this deck. Open with my overview: create a soundscape that never sits still. "
     "Design an evolving ambient piece that continuously transforms through automation, modulation and layering. Say that there is no "
     "traditional rhythm or song structure: this project is about motion, texture and space."),
    (1, "listen", "Think: music with no beat", "Close your eyes · Think, then share|Teacher: no audio is needed. You may play a short ambient "
     "piece you choose; none is included.|Can music have no beat and still go somewhere?|What is a sound that slowly changes, "
     "like wind or a hum?|How would you make a sound feel like it is moving?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker unless you choose to, and no one else's "
     "music is included in this kit. If you do play a short ambient piece of your own choosing, ask students to close their eyes and say "
     "what changed. This sets up my first struggle: students default to adding beats, so say early that this project is about texture "
     "and motion, not rhythm."),
    (1, "bullets", "What is Infinite Horizon?", "A soundscape that never sits still|An evolving ambient piece|Automation, modulation and "
     "layering|No traditional rhythm or song structure",
     "My overview and goals, shortened to fit the slide. Create a soundscape that never sits still: an evolving ambient piece that "
     "continuously transforms through automation, modulation and layering. No traditional rhythm or song structure; this is about motion, "
     "texture and space. Goal four is a 60 to 90 second soundscape that sustains listener interest. Students write the five vocabulary "
     "terms in their own words on the vocabulary page; slide 6 introduces them."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: introduction, listen to ambient examples and begin building a drone or pad "
     "foundation. Class 2: layer additional textures and atmospheric elements. Classes 3 to 5 are working days: automate, refine and "
     "evolve the soundscape. Class 6: final mix and bounce, and prepare presentations. Class 7: presentations with Padlet Q and A peer "
     "feedback. Hand out the project sheet now."),
    (1, "pic", "Five steps, then finish", "cycle",
     "Class 1. The first five steps of my project sheet, in order: listen, build your foundation, layer, automate, refine. Then students "
     "finalize with a mix and a bounce, and present with Padlet feedback. Point to each box and say roughly when it happens: listening "
     "and the foundation today, layers in Class 2, automation and refining on the working days. The step names are mine; the picture and "
     "its short labels are the kit's own."),
    (1, "bullets", "Five words to know", "Soundscape: texture and atmosphere, not melody or rhythm|Drone: a sustained tone or chord|"
     "Automation: changing a parameter over time|Modulation: one signal controlling another|Ambient: tone, atmosphere and texture",
     "My five vocabulary terms, shortened to fit the slide. Soundscape: an ambient composition focused on texture and atmosphere rather "
     "than melody or rhythm. Drone: a sustained tone or chord that creates a foundation for ambient music. Automation: changing a "
     "parameter over time to create movement and evolution. Modulation: using one signal to control another, adding variation and life "
     "to a sound. Ambient: music focused on tone, atmosphere and texture rather than traditional song structure. The full definitions "
     "are on the vocabulary page."),
    (1, "steps", "Steps 1 and 2: listen, build", "Study examples of ambient and soundscape music|Write what you hear on the Listening log|"
     "Create a drone or pad as your base texture|Make it long and steady, so layers can sit on it",
     "Steps 1 and 2 of the project sheet, shortened to fit the slide. Step 1, listen: study examples of ambient and soundscape music for "
     "inspiration. Step 2, build your foundation: create a drone or pad layer as your base texture. The second and fourth lines are the "
     "kit's own suggestions, not my steps: students write what they hear on the Listening log, and the drone should be steady enough for "
     "layers to sit on. You choose the listening examples; none is included."),
    (2, "pic", "Think in four phases", "phases",
     "Class 2. A kit picture, not from my sheets, built from my third struggle: students struggle without traditional structure to guide "
     "them, so suggest thinking in phases: opening, evolution, climax, fade. The curve shows how full the sound is over time. Ask "
     "students to place their own piece on it: where does it start, where does it peak, how does it end? The Phase plan has room for the "
     "layers in each phase."),
    (2, "bullets", "Texture, not rhythm", "Avoid traditional rhythm and song structure|Focus on motion and space|Students often add a "
     "beat: take it out|Ask: what changes while it plays?",
     "My fifth requirement and first struggle, shortened to fit the slide. Avoid traditional rhythm or song structure and focus on motion "
     "and space. Students default to adding beats; remind them this is about texture and motion, not rhythm. The last line is the kit's "
     "own question for the working days: if nothing changes, there is nothing to hear yet."),
    (2, "steps", "Step 3: layer", "Add textures, sounds and atmospheric elements|Use synths, samples and FX|Keep the drone underneath|"
     "Add one layer at a time, and listen",
     "Step 3 of the project sheet and requirement 2, shortened to fit the slide. Step 3, layer: add additional textures, sounds and "
     "atmospheric elements. Requirement 2: layer ambient textures and drones using synths, samples and FX. The last line is the kit's own "
     "suggestion, not my step: add one layer at a time and listen before adding the next. Hand out the Phase plan so students can say "
     "which layers belong in which phase."),
    (3, "pic", "Automate everything", "lanes",
     "Class 3, the first working day. A kit picture of what automation looks like: a line drawn on a lane, one lane for each parameter. "
     "From my third tip: automate everything, because if a parameter stays the same the whole time the soundscape will feel flat. The "
     "four lanes are the ones my step 4 names: filters, reverb, volume and panning. In Logic, press A to show automation and choose the "
     "parameter to draw."),
    (3, "bullets", "Step 4: automate", "Draw automation on filters, reverb, volume and panning|Change parameters over time|Make every "
     "transition gradual|Count your lanes on the Automation plan",
     "Step 4 and requirements 3 and 4, shortened to fit the slide. Step 4, automate: draw automation on filters, reverb, volume and "
     "panning to create evolution. Use automation to change parameters over time, and incorporate gradual transitions and evolving "
     "movement. My second struggle is that soundscapes feel static because students do not automate enough parameters; require a minimum "
     "number of automation lanes. The last line is the kit's own: students list their lanes on the Automation plan."),
    (3, "pic", "Worked example: 75 seconds", "arrange",
     "Class 3. An invented piece, Slow Tide, described on paper; nothing here is audio. It is 75 seconds long, in four phases: opening, "
     "evolution, climax and fade. Five layers join and leave: a drone, a pad, a texture, a few chimes and a sweep. Below them are five "
     "automation lanes, and none of them is flat: the drone's filter, the pad's reverb, the texture's volume and panning, and the chimes' "
     "delay. The numbers are on the worked example page."),
    (4, "bullets", "Be patient", "Let sounds evolve slowly|Do not rush changes|Reverb and delay create a sense of space|If a parameter "
     "never moves, it sounds flat",
     "My tips 1 to 3, shortened to fit the slide. This project is about patience: let sounds evolve slowly and do not rush changes. Reverb "
     "and delay are your best friends here; use them to create a sense of space. Automate everything: if a parameter stays the same the "
     "whole time, your soundscape will feel flat. Ask students to stretch the slowest change in their piece, then listen again."),
    (4, "bullets", "Step 5: refine", "Listen for flow and pacing|Remove anything that feels static or repetitive|Close your eyes: does "
     "it take you somewhere?|Harder option: 5+ automation lanes and Alchemy",
     "Step 5, tip 4 and my Harder variation, shortened to fit the slide. Refine: listen for flow and pacing, and remove anything that "
     "feels static or repetitive. Close your eyes while listening to your piece: does it take you somewhere? That is the goal. My Harder "
     "variation extends the piece to two minutes or more, requires at least five automation lanes and use of Alchemy for custom ambient "
     "patches; offer it to students who are ready. Hand out the Listen-back sheet."),
    (6, "steps", "Steps 6 and 7: mix, bounce", "Mix for depth and space|Bounce your soundscape|Zip the .logicx project|Create your Padlet "
     "post with 3 questions|Prepare to present",
     "Class 6. Steps 6 and 7 of the project sheet, shortened to fit the slide. Finalize: mix for depth and space and bounce your "
     "soundscape. Present and get feedback: create your own Padlet post with three questions you want classmates to answer. The third "
     "line is the kit's own reminder about the submission: zip the .logicx in Finder (Control-click, Compress). Check that every "
     "soundscape is between 60 and 90 seconds before students bounce."),
    (6, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Infinite Horizon|Padlet post with "
     "your 3 questions|Answer 2 questions on classmates’ posts",
     "The submission checklist from the project sheet, shortened to fit the slide. Show where students upload (your class page) and where "
     "the Padlet board is. Remind students that a bounced file with the wrong length is the quickest thing to fix: check it is 60 to 90 "
     "seconds."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play your soundscape|Say what you wanted it to feel like|Your Padlet post: 3 questions about your "
     "project|Answer at least 2 of each classmate’s 3",
     "Class 7, presentations with Padlet Q and A. Step 7 of the project sheet, shortened to fit the slide: create your own Padlet post "
     "with 3 questions you want classmates to answer, present to the class, and during classmates' presentations answer at least 2 of "
     "their 3 questions. The second line is the kit's own suggestion. Ask the class to close their eyes during each piece."),
    (7, "closer", "One last thing…", "You made it move.|You gave it space.|You let it evolve.|Now listen.",
     "Close with my teacher notes: this project stretches students' definition of what music can be. Ask a few students what they "
     "noticed in a classmate's piece with their eyes closed. My notes suggest pairing the project with a brief discussion of ambient and "
     "experimental music history; the kit leaves that to you. Tell them the next project starts from the menu."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("example", "Worked example", "an invented piece on paper"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 8, 11, 13, 18]
SHOTS3 = [("example", "Worked example"), ("listen", "Listening log"), ("phases", "Phase plan"), ("automation", "Automation plan"),
          ("starter", "Starter + Harder"), ("proj2", "Steps"), ("setup", "Setup"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "changes", "logicref", "starter", "example",
        "listen", "phases", "automation", "refine", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "example", "proj2", "rubric"]

COVER_A = "Make music that never sits still"
COVER_C = "DMP2 · ambient · automation · intro slides"
PDF_COVER = dict(a=30, b=50, c=14, art=7.3)
SQ_COVER = dict(a=44, b=140, c=27, art=740, gap=44)
SQ_B_LINES = ["Infinite", "Horizon"]
SQ_SUB = "7 class periods · ambient · automation · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Listening log, phase plan, automation plan, worked example", 28)}
SQ_BANDS = {1: "Listen <em>·</em> layer <em>·</em> automate <em>·</em> refine <em>·</em> bounce",
            2: "Hook <em>·</em> four phases <em>·</em> automate everything <em>·</em> refine",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, video, songs, artists or albums are named or included. You choose what to play for the listening on Class 1, and "
             "students make every sound in their soundscapes themselves.")
CREDITS = ["Worked example (an invented 75-second piece with its phases, layers and automation lanes, described on paper), the horizon, "
           "step, phase and automation drawings and layouts: original work, Hudson Beat.",
           "No audio, video, lyrics, album art, screenshots, presets, templates, links or chart data are included. No student work is "
           "included. Padlet and Alchemy are named only as the owner’s own materials name them."]
LOGIC_INTRO = ("Where to find the tools an Infinite Horizon project is likely to use. Demonstrate what your class needs on Classes 1 and 3 "
               "and then let students work. Names are from current Logic Pro versions; check the labels on yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add tracks with Track › New Tracks…: a Software Instrument track for synths "
              "and pads, an Audio track for samples and recordings."),
             ("A drone or pad", "On a Software Instrument track open the Library (Y) and browse the pad and synth sounds. Draw one long "
              "region with a held note or chord and loop it, so the sound never stops."),
             ("Synths and samples", "Alchemy (my Harder variation) and the other software instruments make drones and textures. Drop "
              "audio you own onto an Audio track, or load it in Quick Sampler, to build a texture."),
             ("Automation", "Press A to show automation, choose a parameter such as a filter cutoff, volume, pan or a reverb send, and click "
              "to add points on the lane. Drag points to shape the curve."),
             ("Modulation", "Many synth sounds have LFOs and envelopes that move a parameter for you. In Alchemy, look at the modulation "
              "section. Automation is you drawing the change; modulation is a signal doing it."),
             ("Filters and EQ", "Add Channel EQ or use a synth’s own filter. Automating a filter cutoff slowly opens or closes the sound."),
             ("Reverb and delay", "Insert Space Designer or ChromaVerb, or send tracks to a bus with a reverb or delay on it. Automate the "
              "send level to change how much space a sound has."),
             ("Mixer: volume and panning", "Press X to open the Mixer. Move each track’s fader for volume and its Pan knob to place it, "
              "then automate both."),
             ("Save versions", "Use File › Save As… with a numbered name before each big change."),
             ("Length check", "Look at the position display: a 60–90 second piece ends between 1:00 and 1:30 at the project’s tempo."),
             ("Bounce and zip", "File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and "
              "choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and zipped .logicx submitted",
                 "Padlet post created with my 3 questions", "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my soundscape:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12.4pt;margin-bottom:3pt">Adding beats: slide 9 and the Listen-back sheet’s “no beat crept in” check (page @REFINE).</li>'
    '<li style="font-size:12.4pt;margin-bottom:3pt">Too little automation: the Automation plan (page @AUTOMATION), with a box for the minimum you set.</li>'
    '<li style="font-size:12.4pt;margin-bottom:3pt">No structure to guide them: the four phases on slide 8 and the Phase plan (page @PHASES).</li>'
    '<li style="font-size:12.4pt;margin-bottom:0">Ambient seems boring: the Listening log (page @LISTEN) asks what changes, which gives listening a job.</li></ul></div>'
    '<div class="box" style="margin-top:7pt"><span class="k">Where this kit helps with the variations (kit suggestion)</span><ul style="margin:0">'
    '<li style="font-size:12.4pt;margin-bottom:3pt">Easier: the starter-template recipe, to build on paper’s instructions in a few minutes (page @STARTER).</li>'
    '<li style="font-size:12.4pt;margin-bottom:0">More advanced: the worked example has five lanes (page @EXAMPLE); page @STARTER lays out 2+ minutes, 5+ lanes and Alchemy.</li></ul></div>')
TN1_SIZE = 15.2
PROJ_SIZE = 14.6
VOCAB_GAP = 14
CHANGES_SIZE = 9.8
LOGIC_SIZE = 10.2
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example", "How to use, overview, setup, pacing, teacher notes, what changed, Logic quick "
              "reference, starter template and Harder variation, worked example"),
             ("Student pages", "listen", "reflect", "Listening log, Phase plan, Automation plan, Listen-back sheet, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period open-ended project for high school music '
             f'technology. Each student builds a 60–90 second ambient soundscape in Logic: a drone or pad, more layers, and automation '
             f'on filters, reverb, volume and panning so the sound is always moving. There is no beat and no song form. They bounce it, '
             f'reflect and present it with Padlet questions for feedback. It is the project from my Digital Music Production 2 course '
             f'(type: open-ended; focus: automation and texture), and the projects in that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Choose your listening examples, set up the Presentation Padlet and decide your minimum number of automation lanes (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("listen")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Class 5 is a working day with no new slide. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}: a starter template with one drone layer and basic automation (a recipe for it is on page {D.IX("starter")}), or 2+ minutes, at least 5 automation lanes and Alchemy.</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Any sound:</b> the pages name no instrument or sound source beyond the owner’s, so students fill in their own.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students build a '
             f'soundscape that never sits still, and learn that automation is how a sound moves.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13.4pt;line-height:1.5">One evolving ambient soundscape, 60–90 seconds long, with no traditional rhythm '
             f'or song structure. It is built from layered textures and drones using synths, samples and FX, with automation of '
             f'parameters such as filters, reverb and volume, and with gradual transitions. They hand in a bounced .mp3 or .wav and the '
             f'zipped .logicx project, plus a Padlet post with three feedback questions, then play the piece and present it.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:13pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:12pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:13pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.6pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: listen and build a drone, layer, three working days, mix and bounce, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: synths, effects, automation, mixing, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, ambient examples of your choice to play, a feedback board and a place to submit files</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:12pt">Students should already '
             f'know how to open a project, add and play software instruments, use the Mixer, and save, bounce and zip in Logic. Nothing new '
             f'is taught: the quick reference (page {D.IX("logicref")}) shows where each tool lives, including automation.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Open-ended", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 12.2pt; line-height: 1.46; margin-bottom: 6pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the final listen.</li>'
             f'<li><b>Ambient examples of your choice</b> to play on Class 1 and as your “compelling examples” (my fourth struggle). None is included.</li>'
             f'<li><b>A place to submit</b> the .mp3 or .wav and the zipped .logicx (your class page).</li>'
             f'<li><b>The Presentation Padlet</b>, set up before Class 1 (yours to set up; none is included).</li>'
             f'<li><b>A minimum number of automation lanes</b> (my second struggle). Write it on the board and on page {D.IX("automation")}.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("listen")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:12.2pt;margin-bottom:8pt") for c in [
                 "Choose two or three ambient examples to play, and decide what students listen for.",
                 "Set up the Presentation Padlet in your class page.",
                 "Decide your minimum number of automation lanes and your rule for the starter template (page @STARTER).",
                 "Check that a student computer opens Logic and plays back through headphones."]).replace("@STARTER", str(D.IX("starter"))) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch (my fourth struggle and closing note)", True)}'
             f'<p style="font-size:12pt">Some students find ambient music boring, and many add a beat. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Kit suggestions, not part of my sheets</span><ul style="margin:0">'
             f'<li style="font-size:11.6pt">A minimum of three automation lanes works for most classes; use five for my Harder variation. The number is yours to set.</li>'
             f'<li style="font-size:11.6pt">While students work, ask: what is moving in your piece right now? What was the last change you could hear?</li>'
             f'<li style="font-size:11.6pt">Short, quiet listening works best with eyes closed and the lights low. Keep it to a minute or two.</li></ul></div>'
             f'{D.H2("Music they did not make")}'
             f'<div class="box"><span class="k">A kit suggestion</span><p style="margin:0;font-size:11.4pt;line-height:1.42">'
             f'The sheet allows samples. Tell students to use only audio they made or have the right to use, and to hand in only their own '
             f'soundscape. Examples you play for listening stay out of their projects.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.4pt;line-height:1.42">'
             f'Slow, low drones can hide how loud a piece is. Tell students to start with the headphones low and to check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


def starter_page(n, wm=False):
    steps = ["New Software Instrument track; open the Library (Y) and pick a pad or drone sound.",
             "Draw one long region (8 to 16 bars) with a held note or chord, and cycle it so the sound never stops.",
             "Add a filter: the synth’s own cutoff or Channel EQ. Press A and choose its cutoff on the lane.",
             "Draw a slow curve: closed at the start, open by the middle, partly closed at the end. This is the “basic automation”.",
             "Add a reverb send, set it moderate, and automate nothing else yet. Save as “Starter”.",
             "Open it for each student (or share it on your class page). They add layers on top, as my Easier variation says."]
    li = "".join(f"<li style='font-size:12.6pt;line-height:1.4;margin-bottom:6pt'>{s}</li>" for s in steps)
    inner = (f'<p style="margin:0 0 6pt;font-size:12.6pt;line-height:1.42">My Easier variation: provide a starter template with one drone layer and basic '
             f'automation; students add layers on top. A Logic project is not included in this kit, so here is a recipe for it. Build it '
             f'yourself in a few minutes, with sounds you have the right to use.</p>'
             f'{D.H2("Starter template: one drone layer, basic automation", True)}<ol style="margin:0">{li}</ol>'
             f'{D.H2("My Harder variation, laid out")}'
             f'<table class="t" style="font-size:12.4pt;line-height:1.45"><tr><th style="width:30%">My option</th><th>How to use it</th></tr>'
             f'<tr><td><b>Extend to 2+ minutes</b></td><td>The worked example (page {D.IX("example")}) is 75 seconds, so at 2 minutes each '
             f'phase is about a third longer. Students replan the four phases on page {D.IX("phases")} for 120 seconds or more.</td></tr>'
             f'<tr><td><b>At least 5 automation lanes</b></td><td>The worked example has five lanes. Students list them on page '
             f'{D.IX("automation")} and you count them.</td></tr>'
             f'<tr><td><b>Alchemy for custom ambient patches</b></td><td>Students build or edit a drone or pad patch in Alchemy rather than '
             f'picking one from the Library. Show the source and filter sections and the modulation section (page {D.IX("logicref")}).</td></tr></table>'
             f'<div class="box acc-b" style="margin-top:8pt"><span class="k">How to use this page</span><p style="margin:0;font-size:12.4pt;line-height:1.5">'
             f'Offer the starter to students who freeze at the empty project; nobody has to take it. Offer the Harder variation to students '
             f'who finish early. Both are your choice, as in my notes. The 60–90 second length is the rule for everyone else (requirement 1).</p></div>')
    return D.page("Starter template and my Harder variation", "TEACHER", "Easier + Harder", inner, n, key="starter")


def example_page(n, wm=False):
    lay = "".join(f"<tr><td style='width:16%'><b>{a}</b></td><td>{d}</td><td style='white-space:nowrap'>{mmss(s)}–{mmss(e)}</td></tr>"
                  for a, s, e, d in LAYERS)
    aut = "".join(f"<tr><td><b>{ly} · {par}</b></td><td>{mmss(pts[0][0])}–{mmss(pts[-1][0])}</td></tr>" for ly, par, pts in AUTO)
    ph = "".join(f"<tr><td style='width:17%'><b>{a}</b></td><td style='width:19%;white-space:nowrap'>{b}</td><td>{c}</td></tr>"
                 for a, b, c in PHASE_NOTES)
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">An <b>invented piece, “{PIECE}”, described on paper</b>: no audio is included. Students’ projects will differ.</p>'
             f'<div class="cols" style="gap:10pt"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10pt">{WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9pt">It has a beat, and nothing says what will change.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:9pt;line-height:1.3">{STRONG}</p></div></div>'
             f'{D.H2("3 · The map: 1:15, four phases, five layers, five lanes")}'
             f'<div style="width:6.1in;margin:1pt auto 2pt">{D.body_svg(map_body(1250, "page arrange", 24, 20))}</div>'
             f'<div class="cols" style="gap:10pt"><div><span class="k" style="font-size:9.4pt">4 · Phases</span>'
             f'<table class="t" style="font-size:8.4pt;line-height:1.2;margin-top:2pt">{ph}</table></div>'
             f'<div><span class="k" style="font-size:9.4pt">5 · Layers (in to out)</span>'
             f'<table class="t" style="font-size:8.4pt;line-height:1.2;margin-top:2pt">{lay}</table></div></div>'
             f'<div class="cols" style="gap:10pt;margin-top:3pt"><div><span class="k" style="font-size:9.4pt">6 · Automation lanes</span>'
             f'<table class="t" style="font-size:8.4pt;line-height:1.2;margin-top:2pt">{aut}</table></div>'
             f'<div class="box acc-b"><span class="k">7 · Checking the numbers</span><p style="margin:0;font-size:8.6pt;line-height:1.25">'
             f'{" + ".join(str(b - a) for _, a, b in PHASES)} = {TOTAL_S} s = 1:15, inside my 60–90 second range. Five lanes, my Harder '
             f'variation’s minimum, and every one moves a lot. '
             f'<b>Three Padlet questions (invented):</b> {qs}</p></div></div>')
    return D.page("Worked example · an invented piece", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def listen_page(n, wm=False):
    rows = [("What I hear (sounds, in order)", 62), ("What stays the same", 40), ("What changes over time", 62),
            ("How it makes me feel", 40), ("What is NOT there (a beat? a melody?)", 40)]
    trs = "".join(f"<tr><td style='height:{h}pt'><b>{a}</b></td><td></td><td></td><td></td></tr>" for a, h in rows)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Step 1: study examples of ambient and soundscape music for inspiration. '
             f'Your teacher chooses and plays the examples. Close your eyes, listen for a minute, then write what you notice. Soundscape: '
             f'an ambient composition focused on texture and atmosphere rather than melody or rhythm.</p>'
             f'<table class="map"><tr><th style="width:24%">What I notice</th><th>Example 1</th><th>Example 2</th><th>Example 3</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:7pt"><span class="k">What the examples share</span>'
             f'<div class="fl" style="margin-top:3pt"><b>The longest sound I heard lasted about:</b><span></span></div>'
             f'<div class="fl"><b>Something that changed so slowly I almost missed it:</b><span></span></div>'
             f'<div class="fl"><b>A change I could hear in space (reverb, echo, near or far):</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>One thing I will try in my own soundscape:</b><span></span></div></div>'
             f'<div class="box" style="margin-top:7pt"><span class="k">Check</span>'
             + D.chk("I wrote down what changed, not only what I liked.", 12, "font-size:10.8pt;margin-bottom:2pt")
             + D.chk("I listened with my eyes closed at least once.", 12, "font-size:10.8pt;margin-bottom:0") + '</div>')
    return D.page("Listening log", "STUDENT", "Class 1", inner, n, wm, name=True, key="listen")


def phases_page(n, wm=False):
    cols = "".join(
        f'<div class="box{" acc-b" if k % 2 == 0 else ""}" style="margin-bottom:5pt"><span class="k">{nm} · from ____ to ____ seconds</span>'
        f'<div class="fl" style="margin:3pt 0 0"><b>Layers I hear:</b><span></span></div>'
        f'<div class="fl" style="margin:2pt 0 0"><b>What moves or changes:</b><span></span></div>'
        f'<div class="fl" style="margin:2pt 0 0"><b>How it should feel:</b><span></span></div></div>'
        for k, nm in enumerate(["Opening", "Evolution", "Climax", "Fade"]))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Steps 2 and 3: create a drone or pad layer as your base texture, then add '
             f'additional textures, sounds, and atmospheric elements. Plan the piece in four phases: opening, evolution, climax, fade '
             f'(from my teacher notes). A drone is a sustained tone or chord that creates a foundation for ambient music.</p>'
             f'<div class="box"><span class="k">My foundation (step 2)</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>My drone or pad sound is:</b><span></span></div>'
             f'<div class="fl"><b>It plays the note or chord:</b><span style="flex:0 0 1.5in"></span><b>Made with (synth, sample, FX):</b><span></span></div></div>'
             f'<div style="margin-top:6pt">{cols}</div>'
             f'<div class="fl" style="margin-top:4pt"><b>Total length (60–90 seconds):</b><span style="flex:0 0 1in"></span><b>Layers in all:</b><span style="flex:0 0 0.7in"></span><b>No beat?</b><span style="flex:0 0 0.5in"></span></div>')
    return D.page("Phase plan", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="phases")


def automation_page(n, wm=False):
    trs = "".join(f"<tr><td style='height:32pt'><b>{i}</b></td><td></td><td></td><td></td><td></td></tr>" for i in range(1, 9))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Step 4: draw automation on filters, reverb, volume, and panning to create '
             f'evolution. Automation is changing a parameter over time to create movement and evolution. Each lane is one parameter on one '
             f'track. Automate everything: if a parameter stays the same the whole time, your soundscape will feel flat.</p>'
             f'<div class="box acc-b" style="margin:0 0 5pt"><div class="fl" style="margin:0"><b>My teacher’s minimum number of lanes:</b>'
             f'<span style="flex:0 0 0.8in"></span><b>My lanes so far:</b><span style="flex:0 0 0.8in"></span></div></div>'
             f'<table class="map"><tr><th style="width:6%">#</th><th style="width:24%">Track and parameter</th><th style="width:26%">Starts at to</th>'
             f'<th style="width:20%">From time to time</th><th>Does it move slowly? Done?</th></tr>{trs}</table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Parameters to try (from my sheet and the quick reference)</span>'
             f'<p style="margin:0;font-size:10.6pt;line-height:1.4">Filter cutoff · reverb send · delay send or feedback · volume · '
             f'panning · a synth’s modulation depth. Modulation is using one signal to control another, adding variation and life to a sound.</p></div>'
             f'<div class="fl" style="margin-top:6pt"><b>The lane that changes the most:</b><span></span></div>'
             f'<div class="fl"><b>The lane I will slow down:</b><span></span></div>')
    return D.page("Automation plan", "STUDENT", "Classes 3–5", inner, n, wm, name=True, key="automation")


def refine_page(n, wm=False):
    trs = "".join("<tr><td style='height:36pt'></td><td></td><td></td></tr>" for _ in range(5))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Step 5: listen for flow and pacing. Remove anything that feels static or '
             f'repetitive. Close your eyes while listening to your piece. Does it take you somewhere? That’s the goal.</p>'
             f'<div class="box acc-b"><span class="k">Eyes-closed listen</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Where it took me:</b><span></span></div>'
             f'<div class="fl"><b>The first moment I noticed a change (time):</b><span style="flex:0 0 1in"></span><b>The last:</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>Where my attention drifted (time):</b><span></span></div></div>'
             f'{D.H2("Static or repetitive spots")}'
             f'<table class="map"><tr><th style="width:16%">Time</th><th style="width:42%">What feels static or repetitive</th><th>What I changed</th></tr>{trs}</table>'
             f'<div class="box" style="margin-top:7pt"><span class="k">Checks before I bounce</span>'
             + "".join(D.chk(c, 12, "font-size:10.8pt;margin-bottom:3pt") for c in [
                 "Every layer changes at least once (an automation lane or a sound that moves).",
                 "Nothing repeats exactly, and no beat crept in.",
                 "The transitions between phases are gradual.",
                 "The piece is between 60 and 90 seconds.",
                 "Reverb or delay gives it a sense of space.",
                 "I mixed for depth and space (step 6)."]) + '</div>'
             f'<div class="fl" style="margin-top:6pt"><b>The one change that improved my piece most:</b><span></span></div>')
    return D.page("Listen-back sheet", "STUDENT", "Classes 4–6", inner, n, wm, name=True, key="refine")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "starter": starter_page, "example": example_page,
         "listen": listen_page, "phases": phases_page, "automation": automation_page, "refine": refine_page}


# ================================================================ content checks (example arithmetic, owner text, no audio)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 5), reqs=(REQS, 5), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 5),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 3))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp} (the owner's count)")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is the owner's /25, levels 1-5")
    if [c for c, _ in RUBRIC] != ["Creativity & Originality", "Technical Skill / DAW Use", "Composition & Structure",
                                  "Sound Design & Mix Quality", "Documentation & Presentation"]:
        errs.append("rubric categories must be the owner's, in order")
    if FILE_NAME not in CHECK[2] or "Infinite Horizon" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    if "60–90 seconds" not in REQS[0] or "60–90 second" not in GOALS[3]:
        errs.append("length 60-90 seconds as the owner wrote it")
    if not getattr(D, "reflect_on", lambda: True)() or getattr(sys.modules[__name__], "REFLECTION", True) is False:
        errs.append("REFLECTION must stay on: the owner's sheet has no reflection task")
    # the worked example adds up
    if [b - a for _, a, b in PHASES] != [12, 33, 18, 12] or sum(b - a for _, a, b in PHASES) != TOTAL_S:
        errs.append("phases 12 + 33 + 18 + 12 = 75 s")
    if not 60 <= TOTAL_S <= 90:
        errs.append("example inside the owner's 60-90 seconds")
    if PHASES[0][1] != 0 or PHASES[-1][2] != TOTAL_S or any(b != c for (_, _, b), (_, c, _) in zip(PHASES, PHASES[1:])):
        errs.append("phases must tile the piece")
    if any(not 0 <= a < b <= TOTAL_S for _, a, b, _ in LAYERS):
        errs.append("layer spans inside the piece")
    if len(AUTO) != 5:
        errs.append("five automation lanes (the Harder variation's minimum)")
    spans = {nm: (a, b) for nm, a, b, _ in LAYERS}
    for ly, par, pts in AUTO:
        a, b = spans[ly]
        ts = [t for t, _ in pts]
        vs = [v for _, v in pts]
        if ts != sorted(ts) or len(pts) < 3 or ts[0] < a or ts[-1] > b:
            errs.append(f"lane {ly}/{par}: points in order, 3+, inside its layer")
        if max(vs) - min(vs) < .5:
            errs.append(f"lane {ly}/{par}: a lane that barely moves is the static soundscape the project warns about")
    if any(not a <= t <= b for t in CHIME_T for a, b in [spans["Chimes"]]):
        errs.append("chime notes inside the chimes layer")
    if len(QUESTIONS) != 3:
        errs.append("three Padlet questions")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    txt = " ".join(flat)
    for need in ("No audio, video, songs, artists or albums", "invented piece, “Slow Tide”",
                 "Your Name – Infinite Horizon", "Final Grade = Average of Student + Teacher", "No student work is included",
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
    if lab < 0 or any("Phase plan" in g or "Reflection" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in BANNED_EXTRA + ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Spotify",
                   "Radiohead", "Billboard"]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs or services ({banned})")
    return errs


def check_summary():
    return (f"The invented piece is {TOTAL_S} s (phases {'+'.join(str(b - a) for _, a, b in PHASES)}; {len(LAYERS)} layers, "
            f"{len(AUTO)} automation lanes, none flat); "
            f"the owner's lists counted (4 goals, 5 terms, 5 requirements, 7 steps, 4 tips, 5 checklist items, 4 struggles, 3 resources); "
            f"{len(CHANGES)} wording changes disclosed; no audio, artist names or student work included; grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
