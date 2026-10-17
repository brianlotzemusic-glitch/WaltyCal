#!/usr/bin/env python3
"""DMP2 project: Anti-Music Manifesto (TpT 019): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Anti-Music Manifesto > "Anti Music Manifesto - Project Sheet & Rubric" (rubric 5 categories scored 1-5, /25,
final grade = average of student and teacher scores), TEACHER NOTES > "Anti Music Manifesto - Teacher Notes" (7 class periods), and the
project's entry on "DMP2 - Project Menu" (the June 2026 menu; owner, 17 Oct 2026: the June entry may be quoted). These three set the
project text, steps, rubric and pacing (owner rule, 17 Oct 2026).
Supporting artifacts: the Teacher Notes name three suggested resources (a John Cage piece on YouTube, an introduction to experimental
music on YouTube, examples of noise music and sound art). No owner file or link for any of them exists in the other DMP2 folders (the
older Projects > Anti-Music Manifesto folder holds only the 2025 project outline, whose rubric is older and which is not a source), so
the three are printed as the owner wrote them and nothing is included: no link, audio or video.

NO AUDIO IS INCLUDED. Students record or create their own unconventional sounds and make one 45-60 second piece. The worked example is an
invented piece ("Kitchen Table", 50 seconds) described on paper, with an invented artist statement; every picture (the three conventions,
the sound chain, the timeline) is drawn in code. Songs and chart data are not named.
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "anti-music-manifesto"
TITLE = "Anti-Music Manifesto"
ACCENT = "#7A1F3D"          # this product's single accent: wine (008 red, 009 orange, 010 violet, 011 teal, 012 blue, 013 green, 014 magenta, 015 gold, 016 olive, 017 sienna, 018 steel blue)
ACC_LIGHT = "#EBC9D5"
PRICE = "10.00"
CLASSES = 7
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-018).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "Anti-Music in Logic Pro | Experimental Music Manifesto Project | High School"
DESC_START = "Experimental music project for high school music technology:"
DESC_MUST = ["Anti-Music Manifesto", "artist statement", "no audio", "Padlet"]
ZIP_DIR = "Anti-Music Manifesto - Hudson Beat"
ZIP_DATE = (2026, 10, 17, 12, 0, 0)
TYPE = "Open-Ended Project"
PROJ_LINE = "Digital Music Production | <i>Open-Ended Project</i> | 7 class periods"
DECK_STRAP = "Break the rules on purpose in Logic Pro"
BANNED_EXTRA = []

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Open-Ended", "Experimental & Conceptual"
MENU_DESC = "Break the rules on purpose. Create a deliberate piece of anti-music with a written artist statement."
OVERVIEW = ("Break the rules on purpose. Create an intentional piece of “anti-music” — a work that deliberately defies traditional "
            "structure, tonality, or rhythm while still expressing a clear artistic concept. This isn’t random noise — it’s noise with a vision.")
GOALS = ["Challenge conventional ideas of what music is and can be",
         "Use Logic Pro to create a deliberate, expressive piece that defies expectations",
         "Explore unconventional sound sources, effects, and techniques",
         "Articulate artistic intent through a written artist statement"]
VOCAB = [("Anti-Music", "Art that intentionally breaks traditional musical rules while maintaining artistic purpose"),
         ("Atonality", "Music that avoids a tonal center or key — no “home” note"),
         ("Dissonance", "Sounds that feel tense, clashing, or unresolved"),
         ("Deconstruction", "Taking apart something familiar and reassembling it in unexpected ways"),
         ("Artist Statement", "A short written explanation of your creative concept and choices")]
REQS = ["Length: 45–60 seconds",
        "Intentionally break at least one major musical convention (structure, tonality, rhythm, etc.)",
        "Use Logic’s effects and automation to distort or deconstruct sounds",
        "Record or create unconventional sound sources",
        "Write a brief artist statement (1 paragraph) explaining your approach and concept"]
STEPS = ["<b>Define your concept</b> — Brainstorm what “anti-music” means to you. What rule are you breaking and why? (Concept sheet: page @CONCEPT)",
         "<b>Gather sounds</b> — Record or create unconventional sound sources (Sound log: page @SOUNDS)",
         "<b>Build</b> — Use Logic to construct your piece. Lean into effects, automation, and distortion. (Build plan: page @BLUEPRINT)",
         "<b>Shape</b> — Even though you’re breaking rules, your piece should feel intentional, not accidental. (Build plan: page @BLUEPRINT)",
         "<b>Write your artist statement</b> — Explain what you did and why (Statement planner: page @STATEMENT)",
         "<b>Finalize</b> — Mix, bounce, and prepare to present your concept to the class",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["The difference between anti-music and random noise is intention. Know what rule you’re breaking and why.",
        "Listen to experimental artists for inspiration: John Cage, Merzbow, Aphex Twin, Death Grips.",
        "Don’t be afraid to make something uncomfortable. That might be the point.",
        "Your artist statement is just as important as the music. It tells your audience what to listen for."]
FILE_NAME = "“Your Name – Anti-Music Manifesto”"
CHECK = ["Bounced .mp3 or .wav uploaded to your class page",
         "Zipped .logicx project file uploaded to your class page",
         f"Files named correctly: {FILE_NAME}",
         "Artist statement submitted via your class page",
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
TN_REINFORCES = ("Pushes creative boundaries and critical thinking about what music is. Requires students to articulate artistic intent, "
                 "which strengthens their ability to talk about creative work.")
STRUGGLES = ["Students make random noise and call it anti-music. Push them to define their concept BEFORE they start building.",
             "Artist statements are vague. Require them to name the specific rule they’re breaking and explain their reasoning.",
             "Some students are uncomfortable making “bad” music on purpose. Frame it as artistic exploration, not failure.",
             "Students don’t use Logic’s tools — they just bang on a keyboard. Encourage effects, automation, and sound manipulation."]
VAR_EASY = ("Provide 3–5 specific rules to break (e.g., “make a track with no rhythm,” “use only dissonant chords”) and let students "
            "choose one.")
VAR_HARD = ("Require a 90-second piece with a written manifesto (not just a statement) defending their artistic philosophy. Pair with "
            "research on an experimental artist.")
RESOURCES = [("John Cage — 4’33” (YouTube)",
              "Named as I listed it. No link, audio or video is included, so find your own copy on a service your school allows. Slide 2 "
              "and page @RULES give a listening routine that works with any passage you pick."),
             ("Introduction to experimental music (YouTube)",
              "Named as I listed it; nothing is included. Choose a short introduction yourself and watch it before Class 1 if you can."),
             ("Examples of noise music and sound art",
              "Named as I listed it; no examples are included. Pick one or two short passages for the Class 1 listening, and preview them "
              "at a low volume first.")]
TN_NOTE = ("This project sparks great class discussions. Consider a brief listening session of experimental music before starting.")
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Creativity &amp; Originality and Composition &amp; Structure: ask the student to say, in one sentence, the rule they broke "
                "(the Concept sheet, page @CONCEPT, holds it). A piece that breaks no rule, or breaks one by accident, is the “random noise” "
                "my notes warn about.",
                "Technical Skill: look at the Sound log (page @SOUNDS). Which sounds were recorded or created, and which effects and "
                "automation changed them?",
                "Sound Design &amp; Mix Quality: ask whether the harsh parts are meant. A distorted or noisy sound can still be balanced "
                "against the others; levels should be a choice.",
                "Documentation &amp; Presentation: the artist statement (Statement planner, page @STATEMENT) should name the rule and give a "
                "reason. The Concept sheet, Sound log, Build plan and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Introduction. Discuss what anti-music means. Brainstorm concepts.",
     "do": "Slides 1–7: hook, what anti-music is, three rules to break, steps 1 and 2, intention over accident. Hand out the project "
           "sheet, the Rules page and the Concept sheet.", "slides": (1, 7),
     "pages": ["rules", "concept", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Is this music? · what is anti-music? · pick a rule to break"},
    {"n": 2, "owner": "<b>Class 2:</b> Gather sounds, begin building. Write initial concept notes.",
     "do": "Slides 8–10: the sound chain, where sounds come from, a live demo. Students fill in the Sound log and finish the Concept sheet.", "slides": (8, 10), "pages": ["concept", "sounds"],
     "deck": "Source · transform · effects · automation · demo"},
    {"n": 3, "owner": "<b>Classes 3–5:</b> Working days — build, shape, refine.",
     "do": "Slide 11: build, shape, refine. Then work time.", "slides": (11, 11), "pages": ["blueprint"],
     "deck": "Working day: build and shape"},
    {"n": 4, "owner": None, "do": "Slides 12–13: the worked example on paper and the “is it on purpose?” test. Then work time.", "slides": (12, 13),
     "pages": ["blueprint"], "deck": "Working day: the worked example, is it on purpose?"},
    {"n": 5, "owner": None, "do": "Full working day: refine and layer. Ask each student to play you the moment where the rule breaks.",
     "slides": None, "pages": [], "deck": "Working day: refine"},
    {"n": 6, "owner": "<b>Class 6:</b> Write artist statement. Final mix and bounce. Prepare presentations.",
     "do": "Slides 14–17: artist statement, mix and bounce, what to turn in, the rubric. Students self-score and post their three questions.", "slides": (14, 17), "pages": ["statement", "rubric", "present"],
     "deck": "Artist statement · mix · bounce · checklist · rubric"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 18–19: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (18, 19), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one rule for Class 1</span>'
    '<p style="margin:0;font-size:9.6pt">Students define the concept BEFORE they build (my first struggle). No session opens until the '
    'Concept sheet (page @CONCEPT) names a rule and a reason. Slide 2 is the listening routine my notes suggest.</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:9.6pt">Working days. Class 5 has no new slide. '
    'Circulate and ask: which rule is this breaking, and how would a listener know it was on purpose?</p></div></div>')
PACING_SIZE = 9.9

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (checklist items 1, 2 and 4).",
    "Page numbers are added to steps 1 to 5 (the Concept sheet, Sound log, Build plan and Statement planner).",
    "My three suggested resources are listed as I wrote them (page @TN2). None is included: no link, audio or video comes with the "
    "kit, and the artists’ names appear only where I wrote them (tip 2 and the resource list).",
    "My pacing guide’s “Classes 3–5” row spans the Class 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 3 shortens the definition of anti-music, slide 6 "
    "shortens steps 1 and 2, slide 7 shortens the first struggle, slide 11 shortens steps 3 and 4, slide 14 shortens step 5, slide 15 "
    "shortens step 6, and slide 16 shortens the submission checklist.",
]
CHANGES_MUST_MENTION = ["your class page", "Page numbers", "None is included", "Classes 3–5", "Layout only", "intro deck shortens"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the goals, the five vocabulary terms, the five "
        "requirements, steps (apart from the page numbers), tips, checklist and file name (“Your Name – Anti-Music Manifesto”), the "
        "rubric (five categories scored 1–5, /25, the average of the student’s and the teacher’s score), what the project reinforces, "
        "the four common struggles, the variations, my day-by-day pacing and my closing note, and the project menu entry quoted on "
        "page @OVERVIEW. No rubric row is added and the requirements are unchanged.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: how to use the kit, the overview and setup "
                "pages, the teacher moves and slide numbers in the pacing guide, the grading suggestions, the Logic quick reference, "
                "the Rules page (the three conventions drawn, plus six rule cards for your Easier variation), the worked example "
                "(an invented 50-second piece and artist statement on paper, not audio), the Concept sheet, Sound log, Build plan and "
                "Statement planner, the vocabulary page, the presentation planner and the intro deck. None of these adds a requirement "
                "or a rubric row.")

# ================================================================ the worked example (Hudson Beat original: an invented piece on paper)
PIECE = "Kitchen Table"
TOTAL_S = 50
SECTIONS = [("Promise", 0, 10), ("Break", 10, 28), ("Hush", 28, 36), ("Wrong return", 36, 50)]       # seconds
CLICKS_STEADY = [float(t) for t in range(10)]                                                         # one per second: 60 per minute
CLICKS_BREAK = [10.0, 10.9, 11.7, 12.4, 13.0, 13.5, 13.95, 14.35, 14.7, 15.0, 15.6, 16.8, 19.2, 23.0]
CLICKS_RETURN = [36.0, 37.5, 38.2, 40.9, 41.2, 45.0, 45.1, 49.0]
HISS = (6, 36)
SCRAPES = [(14, 18), (22, 27), (40, 47)]
DISTORT = [(0, 0), (10, 5), (18, 40), (28, 85), (29, 10), (36, 10), (44, 70), (50, 100)]
LANES = ["Drawer clicks", "Kettle hiss", "Chair, reversed", "Distortion"]
STATEMENT = ("“Kitchen Table” breaks the rule that a pulse should stay steady. I recorded a drawer, a kettle and a chair, and for the "
             "first ten seconds the drawer clicks once a second like a metronome. Then I sped the clicks up and stretched them out while "
             "pushing the distortion higher, until the pulse fell apart, because I wanted the listener to feel a promise being broken. The "
             "hiss in the middle is the quiet that follows. When the clicks return they are uneven, so the piece never gets back to "
             "normal. Listen for the moment the second click arrives too early.")


def mmss(t):
    return f"{int(t) // 60}:{int(round(t)) % 60:02d}"


def gaps(ts):
    return [round(b - a, 3) for a, b in zip(ts, ts[1:])]


# ================================================================ drawings (original, code-drawn: black + accent only)
def hero_body():
    W, H = 1100, 560
    out = []
    n = 25
    for i in range(n):
        x = 40 + i * 43
        if i < 10:
            out.append(f'<line x1="{x}" y1="130" x2="{x}" y2="400" stroke="#000" stroke-width="20" stroke-linecap="round"/>')
        else:
            k = i - 9
            dy = math.sin(i * 12.9898) * 17 * k
            ln = 270 - k * 11 + math.sin(i * 7.3) * 30 * (k / 4)
            ang = math.sin(i * 4.1) * 7 * k
            cx, cy = x + math.sin(i * 2.7) * 5 * k, 265 + dy
            dx, dy2 = math.sin(math.radians(ang)) * ln / 2, math.cos(math.radians(ang)) * ln / 2
            col = ACCENT if i % 3 == 1 else "#000"
            out.append(f'<line x1="{cx - dx:.1f}" y1="{cy - dy2:.1f}" x2="{cx + dx:.1f}" y2="{cy + dy2:.1f}" stroke="{col}" '
                       f'stroke-width="{20 - k * 0.8:.1f}" stroke-linecap="round"/>')
    out.append(f'<line x1="30" y1="470" x2="{40 + 9 * 43 + 18}" y2="470" stroke="#000" stroke-width="4"/>')
    return "".join(out), W, H


def rules_body(W=1600, name="rules", fs=30, cs=22, rs=20, bs=17):
    gap = 40
    W0, W = W, W - 6
    pw = (W - 2 * gap) / 3
    rowh = 100
    out = []
    names = [("Structure", "the order of the sections"), ("Tonality", "is there a home note?"), ("Rhythm", "does the pulse stay steady?")]
    top = fs + 20
    for p, (nm, cap) in enumerate(names):
        x0 = p * (pw + gap)
        out.append(D.t_(x0 + pw / 2, fs, nm.upper(), fs, 700))
        D.lab(name + " heads", nm.upper(), fs, pw - 10)
        for r in (0, 1):
            y = top + r * (rowh + rs + 22)
            lbl = "EXPECTED" if r == 0 else "BROKEN ON PURPOSE"
            out.append(D.t_(x0, y + rs, lbl, rs, 700 if r else 500, anchor="start", fill_=ACCENT if r else "#000"))
            D.lab(name + " rows", lbl, rs, pw - 10)
            by = y + rs + 8
            out.append(f'<rect x="{x0:.1f}" y="{by:.1f}" width="{pw:.1f}" height="{rowh}" fill="#fff" stroke="#000" stroke-width="2"/>')
            if p == 0:
                order = ["INTRO", "VERSE", "CHORUS", "OUTRO"] if r == 0 else ["OUTRO", "CHORUS", "VERSE", "INTRO"]
                bw = (pw - 50) / 4
                for k, s in enumerate(order):
                    bx = x0 + 10 + k * (bw + 10)
                    out.append(f'<rect x="{bx:.1f}" y="{by + 22:.1f}" width="{bw:.1f}" height="{rowh - 44}" rx="5" '
                               f'fill="{ACCENT if r else "#000"}"/>')
                    out.append(D.t_(bx + bw / 2, by + rowh / 2 + bs * .36, s, bs, 700, fill_="#fff"))
                    D.lab(name + " blocks", s, bs, bw - 8)
            elif p == 1:
                for ln in range(6):
                    ly = by + 14 + ln * (rowh - 28) / 5
                    hot = r == 0 and ln == 3
                    out.append(f'<line x1="{x0 + 10:.1f}" y1="{ly:.1f}" x2="{x0 + pw - 10:.1f}" y2="{ly:.1f}" stroke="{ACCENT if hot else "#000"}" '
                               f'stroke-width="{2.6 if hot else 1}" opacity="{1 if hot else .3}"/>')
                pts = ([3, 2, 3, 4, 3, 2, 3, 3] if r == 0 else [0.2, 4.6, 1.3, 5, 2.4, 0.8, 3.7, 1.9])
                for k, ln in enumerate(pts):
                    cx = x0 + 28 + k * (pw - 56) / 7
                    cy = by + 14 + ln * (rowh - 28) / 5
                    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8" fill="{ACCENT if r else "#000"}"/>')
            else:
                xs = ([i / 8 for i in range(9)] if r == 0 else [0, .05, .09, .25, .27, .31, .62, .86, 1.0])
                for u in xs:
                    cx = x0 + 22 + u * (pw - 44)
                    out.append(f'<line x1="{cx:.1f}" y1="{by + 20:.1f}" x2="{cx:.1f}" y2="{by + rowh - 20:.1f}" stroke="{ACCENT if r else "#000"}" '
                               f'stroke-width="7" stroke-linecap="round"/>')
        yb = top + 2 * (rowh + rs + 22)
        out.append(D.t_(x0 + pw / 2, yb + cs, cap, cs, 500))
        D.lab(name + " caps", cap, cs, pw - 10)
    H = top + 2 * (rowh + rs + 22) + cs + 12
    return f'<g transform="translate(3,0)">{"".join(out)}</g>', W0, H


def chain_body(W=1600, name="chain", fs=30, cs=22):
    gap = 74
    pw = (W - 3 * gap) / 4
    bh = 190
    items = [("Sound source", "record it or create it"), ("Transform", "reverse · stretch · pitch"),
             ("Effects", "distort · delay · filter"), ("Automation", "change it over time")]
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
    cap = "Your concept decides every step: a sound only goes down the chain if it helps break your rule"
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
    fills = ["#000", ACCENT, "#4a4a4a", "#000"]
    for (nm, a, b), fc in zip(SECTIONS, fills):
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{fc}"/>')
        out.append(D.t_((X(a) + X(b)) / 2, sh / 2 + fs * .36 + 2, nm.upper(), fs - 2, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 2, X(b) - X(a) - 24)
    lh, lg = 70, 12
    y0 = sh + 22
    for i, nm in enumerate(LANES):
        yy = y0 + i * (lh + lg)
        out.append(D.t_(gx - 16, yy + lh / 2 + 8, nm.upper(), 24, 700, anchor="end"))
        D.lab(name + " lanes", nm.upper(), 24, gx - 30)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.4"/>')
        if i == 0:
            for t in CLICKS_STEADY + CLICKS_BREAK + CLICKS_RETURN:
                col = "#000" if t < 10 else ACCENT
                out.append(f'<rect x="{X(t) - 3:.1f}" y="{yy + 12}" width="6" height="{lh - 24}" rx="2" fill="{col}"/>')
        elif i == 1:
            out.append(f'<rect x="{X(HISS[0]):.1f}" y="{yy + 14}" width="{X(HISS[1]) - X(HISS[0]):.1f}" height="{lh - 28}" rx="6" fill="#7a7a7a"/>')
        elif i == 2:
            for a, b in SCRAPES:
                out.append(f'<rect x="{X(a):.1f}" y="{yy + 10}" width="{X(b) - X(a):.1f}" height="{lh - 20}" rx="6" fill="#000"/>')
        else:
            pts = " ".join(f"{X(t):.1f},{yy + lh - 8 - (lh - 16) * v / 100:.1f}" for t, v in DISTORT)
            out.append(f'<polygon points="{X(0):.1f},{yy + lh - 8} {pts} {X(TOTAL_S):.1f},{yy + lh - 8}" fill="{ACC_LIGHT}"/>')
            out.append(f'<polyline points="{pts}" fill="none" stroke="{ACCENT}" stroke-width="5" stroke-linejoin="round"/>')
    ty = y0 + len(LANES) * (lh + lg) + 4
    for t in (0, 10, 28, 36, 50):
        lbl = mmss(t)
        anc = "start" if t == 0 else ("end" if t == TOTAL_S else "middle")
        out.append(f'<line x1="{X(t):.1f}" y1="{ty - 6}" x2="{X(t):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(t) + (2 if t == 0 else (-2 if t == TOTAL_S else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 120)
    return "".join(out), W, ty + ts + 22


DRAWINGS = {"hero": lambda: D.stack([hero_body()], 40), "rules": lambda: rules_body(1600, "rules pic"), "chain": lambda: chain_body(1600, "chain pic"),
            "plan": lambda: plan_body(1600, "plan pic")}
DRAWING_PX = {"hero": 1900, "rules": 2000, "chain": 2000, "plan": 2000}
SIDE = {"rules": ["Pick one rule, or more", "Structure, tonality or rhythm", "Know why you are breaking it", "Break it on purpose"],
        "chain": ["Record or create a sound", "Transform it until it is strange", "Distort and deconstruct with effects", "Automate so it keeps changing"],
        "plan": ["The rule is a steady pulse", "It breaks, hushes, returns wrong", "Every sound has a job", "Plan 45–60 seconds"]}


def label_extras():
    rules_body(1250, "page rules", 26, 19, 17, 15)
    plan_body(1250, "page plan", 26, 19)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Anti-Music Manifesto", "Break the rules on purpose.",
     "Class 1, the first minute. No audio is included in this deck. Open with my overview: break the rules on purpose and create an "
     "intentional piece of anti-music, a work that deliberately defies traditional structure, tonality or rhythm while still expressing a "
     "clear artistic concept. Then my line: this is not random noise, it is noise with a vision. Students make one 45 to 60 second "
     "piece in Logic and write a one-paragraph artist statement."),
    (1, "listen", "Listen: is this music?", "Is it music? · Decide, then defend your answer|Teacher: play a short passage you choose, one "
     "that breaks a rule.|What rule does it seem to break?|Does it feel planned or accidental?|Would you call it music?",
     "My teacher notes suggest a brief listening session of experimental music before starting. Choose one or two short passages "
     "yourself, preview them at a low volume, and find them on a service your school allows; say the title and the artist aloud if you "
     "like, and do not put them on the slide. Take answers aloud. The point is that the same sounds can feel planned or accidental, which "
     "sets up the idea that the difference between anti-music and random noise is intention."),
    (1, "bullets", "What is anti-music?", "Art that breaks the rules on purpose|It keeps an artistic purpose|Not random noise|Noise with a "
     "vision",
     "My vocabulary term: anti-music is art that intentionally breaks traditional musical rules while maintaining artistic purpose; the "
     "slide shortens that definition. The last line is from my overview. Students write the term in their own words on the vocabulary "
     "page. Atonality, dissonance and deconstruction, the other terms on the sheet, come up as the rules get chosen."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: introduction, what anti-music means, brainstorm concepts. Class 2: gather "
     "sounds, begin building, write initial concept notes. Classes 3 to 5 are working days: build, shape, refine. Class 6: write the "
     "artist statement, final mix and bounce, prepare presentations. Class 7: presentations with Padlet Q and A peer feedback. Hand out "
     "the project sheet now."),
    (1, "pic", "Pick a rule to break", "rules",
     "Requirement 2 is to intentionally break at least one major musical convention: structure, tonality, rhythm, and so on. The picture "
     "shows each one holding, then broken on purpose. Structure: the sections come in an expected order, and here the order is "
     "reversed. Tonality: a melody keeps returning to a home note, and here no note feels like home. Rhythm: a steady pulse, and here it "
     "falls apart. Rule cards for students who want a starting point are on the Rules page."),
    (1, "steps", "Steps 1 and 2: concept, sounds", "Define your concept|What rule are you breaking, and why?|Record or create unconventional "
     "sounds|Fill in the Concept sheet|Keep a Sound log",
     "Steps 1 and 2 of the project sheet, shortened to fit the slide. Step 1: brainstorm what anti-music means to you, and decide what rule "
     "you are breaking and why. Step 2: record or create unconventional sound sources. The Concept sheet and the Sound log hold the "
     "thinking. Nobody opens a Logic session until the Concept sheet names a rule and a reason."),
    (1, "bullets", "Intention, not accident", "Define your concept before you build|Name the specific rule you break|Know why you are breaking "
     "it|Uncomfortable is allowed",
     "My first common struggle, shortened here: students make random noise and call it anti-music, so push them to define their concept "
     "before they start building. Require the specific rule and the reason. My third struggle: some students are uncomfortable making "
     "bad music on purpose, so frame it as artistic exploration, not failure. My tip 3 says it too: that might be the point."),
    (2, "pic", "The sound chain", "chain",
     "Class 2. A sound source, here recorded or created, goes through transformation, effects and automation. Requirements 3 and 4 ask "
     "students to use Logic's effects and automation to distort or deconstruct sounds, and to record or create unconventional sound "
     "sources. My fourth struggle is students who just bang on a keyboard, so encourage effects, automation and sound manipulation."),
    (2, "bullets", "Gather unusual sounds", "Record everyday objects and spaces|Create sounds inside Logic|Keep every file, name it, log it|"
     "Keep recordings school-appropriate and kind",
     "Step 2: record or create unconventional sound sources. These are suggestions from the kit, not mine: objects and rooms around the "
     "school, sounds students make in Logic, and everything named and noted in the Sound log so nothing gets lost. Remind students to "
     "get permission before recording other people, and to keep the headphone volume moderate, because distorted and noisy sounds can be "
     "much louder than they seem."),
    (2, "steps", "Watch me: turn a sound inside out", "Record one short everyday sound|Reverse it or change its speed and pitch|Add "
     "distortion or delay|Automate one effect knob|Save it and note what you did",
     "A live demo of about ten minutes, which is also the kit's own suggestion for Class 2, not one of my steps. Record a short sound, a "
     "drawer or a pen click, then reverse it, change its speed or pitch, add distortion or delay, and draw automation on one effect "
     "knob so the change happens over time. Save after each move and write what you did in the Sound log. Menu names are on the Logic "
     "quick reference; check the labels on your version."),
    (3, "bullets", "Working days: build and shape", "Build with effects, automation and distortion|Lean into the rule you chose|Shape it: "
     "intentional, not accidental|Save versions as you go",
     "Class 3 is the first working day, and Classes 4 and 5 continue it. Steps 3 and 4 of the project sheet, shortened here: use Logic to "
     "construct your piece and lean into effects, automation and distortion; even though you are breaking rules, the piece should feel "
     "intentional, not accidental. Students use the Build plan. Circulate and ask each student to play you the moment the rule breaks."),
    (4, "pic", "Worked example: 50 seconds on paper", "plan",
     "Class 4. An invented piece, Kitchen Table, described on paper; nothing here is audio. The rule is a steady pulse. Promise: ten drawer "
     "clicks, one a second. Break: the clicks speed up, stretch out and fall apart as the distortion rises. Hush: only a kettle hiss. Wrong "
     "return: the clicks come back, uneven. It is 50 seconds, inside my 45 to 60 second requirement. The full plan and a sample artist "
     "statement are on the worked example page."),
    (4, "bullets", "Is it on purpose?", "Could a listener tell which rule you broke?|Does every sound have a job?|Does it change over its 45 "
     "to 60 seconds?|Can you explain every choice?",
     "A check students can use on each other's work. These are the kit's own questions, drawn from my line that the difference between "
     "anti-music and random noise is intention. If a student cannot answer the first question, send them back to the Concept sheet. "
     "Class 5 is a full working day with no new slide."),
    (6, "steps", "Step 5: the artist statement", "One paragraph|Name the specific rule you broke|Explain your reasoning|Say what to listen "
     "for",
     "Class 6. Step 5 of the project sheet, shortened to fit the slide: write your artist statement, explaining what you did and why. My "
     "second struggle is vague statements, so require the specific rule and the reasoning. Tip 4: the statement is just as important "
     "as the music, because it tells your audience what to listen for. Students plan it on the Statement planner."),
    (6, "bullets", "Final mix and bounce", "Mix: balance on purpose|Bounce a .mp3 or .wav|Zip the .logicx project|Write your 3 Padlet "
     "questions",
     "Step 6 of the project sheet, shortened to fit the slide: mix, bounce, and prepare to present your concept to the class. A harsh sound "
     "can still be balanced against the others; levels are a choice. Zip the .logicx in Finder (Control-click, Compress). Students also "
     "write their three Padlet questions today."),
    (6, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Anti-Music Manifesto|Artist statement "
     "submitted|Padlet post with your 3 questions|Answer 2 questions on classmates’ posts",
     "The submission checklist from the project sheet, shortened to fit the slide. Show where students upload (your class page) and where "
     "the Padlet board is. Remind students that the artist statement is submitted as well as the music."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play your piece|Say the rule you broke, and why|Your Padlet post: 3 questions about your project|"
     "Answer at least 2 of each classmate’s 3",
     "Class 7, presentations with Padlet Q and A. Each student plays the piece and presents the concept, then during classmates' "
     "presentations every student answers at least 2 of their 3 questions on their Padlet post. Read the artist statement aloud or let "
     "students do it. My notes say this project sparks great class discussions; leave time for them."),
    (7, "closer", "One last thing…", "You picked a rule.|You broke it on purpose.|You said why.|Now the noise has a vision.",
     "Close with what my teacher notes say this project does: it pushes creative boundaries and critical thinking about what music is, "
     "and it makes students articulate artistic intent, which strengthens their ability to talk about creative work."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("example", "Worked example", "an invented piece on paper"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 5, 8, 12, 17]
SHOTS3 = [("rules", "Rules"), ("example", "Worked example"), ("concept", "Concept sheet"), ("sounds", "Sound log"),
          ("blueprint", "Build plan"), ("statement", "Statement"), ("proj2", "Steps"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "changes", "logicref", "rules", "example",
        "concept", "sounds", "blueprint", "statement", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "example", "proj2", "rubric"]

COVER_A = "Break the rules on purpose"
COVER_C = "DMP2 · experimental music · artist statement · intro slides"
PDF_COVER = dict(a=32, b=50, c=14, art=7.3)
SQ_COVER = dict(a=46, b=140, c=27, art=740, gap=44)
SQ_B_LINES = ["Anti-Music", "Manifesto"]
SQ_SUB = "7 class periods · experimental music · artist statement · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Rules, worked example, concept sheet, sound log, statement planner", 28)}
SQ_BANDS = {1: "Concept <em>·</em> sounds <em>·</em> build <em>·</em> statement <em>·</em> present",
            2: "Hook <em>·</em> three rules <em>·</em> sound chain <em>·</em> demo",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, video, songs or examples are included. Students record or create every sound themselves, so everything in "
             "their pieces is original. For the listening hook, you choose a short passage yourself and find it on a service your school "
             "allows.")
CREDITS = ["Worked example (an invented 50-second piece and artist statement, described on paper), the three-conventions, sound-chain and "
           "timeline drawings and layouts: original work, Hudson Beat.",
           "No audio, video, lyrics, album art, screenshots, presets or chart data are included. The three suggested resources and the four "
           "artists in tip 2 are named exactly as the teacher listed them, with no link or content; YouTube is not affiliated with or endorsing "
           "this resource. Padlet is named only as an example of a tool you may already use."]
LOGIC_INTRO = ("Where to find the tools this project uses. Demonstrate them on Class 2 (slide 10) and then let students work. Names are from "
               "current Logic Pro versions; check the labels on yours.")
LOGIC_REF = [("Record audio", "Add an Audio track (Track › New Audio Track), choose the input, arm the track and press Record (R). Use the "
              "computer’s built-in microphone, or any microphone you have."),
             ("Make a sound in Logic", "Add a Software Instrument track and play or draw notes, or open an Apple loop, then change it. Any "
              "sound can be a starting point."),
             ("Reverse", "Select an audio region and tick Reverse in the Region inspector, or reverse it in the Audio File Editor. "
              "Reverse it again to hear the original."),
             ("Speed and pitch", "Use the Region inspector’s Transpose and Fine Tuning, or turn on Flex and drag the region’s ends to "
              "stretch it. Extreme values are welcome here."),
             ("Distortion", "Insert a distortion effect on the channel strip (Overdrive, Distortion, Bitcrusher or Clip Distortion), then "
              "raise its drive. Listen with the volume low first."),
             ("Delay and reverb", "Insert a delay (Echo or Delay Designer) and raise the feedback until it smears. Reverb: ChromaVerb "
              "or Space Designer."),
             ("Filter", "Use Channel EQ or a filter plug-in and sweep the cutoff while the sound plays. A sound that is mostly filtered "
              "away is still a sound."),
             ("Automation", "Press A to show automation, choose a parameter such as an effect knob or volume, and draw changes over time. "
              "This is how a sound breaks down gradually."),
             ("Edit and cut", "Split regions (Command-T), delete pieces and move them off the grid. Turn Snap off to place sounds "
              "anywhere on purpose."),
             ("Save versions", "Use File › Save As… with a numbered name before each big change, so a good accident is never lost."),
             ("Bounce and zip", "File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and choose "
              "Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; .mp3 or .wav, zipped .logicx and artist statement submitted", "Padlet post created with my 3 questions",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my piece:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Random noise: the Concept sheet (page @CONCEPT) asks for the rule and the reason before anything is built.</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Vague statements: the Statement planner (page @STATEMENT) and the sample statement on page @EXAMPLE.</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Uncomfortable with “bad” music: the Rules page (page @RULES) has six rule cards and says breaking a rule is a choice.</li>'
    '<li style="font-size:10.8pt;margin-bottom:0">Not using Logic’s tools: the Sound log (page @SOUNDS) and the quick reference (page @LOGICREF).</li></ul></div>')
TN1_SIZE = 15
PROJ_SIZE = 14.2
VOCAB_GAP = 9
LOGIC_SIZE = 10.8
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example", "How to use, overview, setup, pacing, teacher notes, what changed, Logic quick "
              "reference, Rules, worked example"),
             ("Student pages", "concept", "reflect", "Concept sheet, Sound log, Build plan, Statement planner, project sheet (3 pages), "
              "rubric, vocabulary, feedback planner, reflection"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period experimental music project for high school music '
             f'technology. Each student picks a musical convention (structure, tonality, rhythm or another) and breaks it on purpose, '
             f'records or creates unconventional sounds, uses Logic’s effects and automation to distort or deconstruct them, builds a '
             f'45–60 second piece, and writes a one-paragraph artist statement. It is an open-ended project from my Digital Music '
             f'Production 2 course (focus: experimental and conceptual), and the projects in that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Choose a short passage for the Class 1 listening hook (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("concept")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Class 5 is a working day with no new slide. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}: pick from 3–5 rule cards (page {D.IX("rules")}), or a 90-second piece with a written manifesto.</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Listening:</b> my notes suggest a brief listening session of experimental music first; you choose the passages.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students choose a '
             f'rule of music, break it on purpose, and prove it was on purpose with a piece and a paragraph.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:14pt;line-height:1.55">One 45–60 second piece of anti-music that intentionally breaks at least one major '
             f'convention, built from sounds they record or create and deconstructed with effects and automation, plus a one-paragraph artist '
             f'statement. They hand in a bounced .mp3 or .wav, the zipped .logicx project and the statement, plus a Padlet post with three '
             f'feedback questions, then play the piece and present the concept.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:14pt;line-height:1.55">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:12pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:13pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.6pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: concept, sounds, three working days, statement and mix, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: audio recording, effects, automation, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a way to record sound, a feedback board, and speakers if you can</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:12pt">Students should already '
             f'know how to open a project, record and edit audio, add effects and automation, and save, bounce and zip in Logic. The quick '
             f'reference (page {D.IX("logicref")}) shows where each tool lives.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Open-ended", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 13.2pt; line-height: 1.5; margin-bottom: 9pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the final listen.</li>'
             f'<li><b>A way to record sound:</b> a microphone, the computer’s built-in microphone, or another recorder students already use.</li>'
             f'<li><b>A place to submit</b> an .mp3 or .wav, a zipped .logicx project and the artist statement (your class page).</li>'
             f'<li><b>A feedback board</b> for the three questions (my sheets use Padlet).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("concept")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:13pt;margin-bottom:11pt") for c in [
                 "Choose one or two short passages of experimental music for slide 2, preview them at a low volume, and find them yourself.",
                 "Check that a student computer can record a sound and play it back through headphones.",
                 "Decide how students will record: at their desks, around the room, or on a short walk with permission.",
                 "Print the student pages; set up the submission spot and the feedback board."]) +
             f'</div><div class="big sb">'
             f'{D.H2("Making it feel safe", True)}'
             f'<p style="font-size:13pt">My notes say some students are uncomfortable making “bad” music on purpose. A plan that works:</p>'
             f'<ul style="font-size:13pt;line-height:1.42">'
             f'<li><b>Say it first.</b> This is artistic exploration, not failure. A rule broken on purpose is a skill.</li>'
             f'<li><b>Concept before sound.</b> Nobody opens a session until the Concept sheet (page {D.IX("concept")}) names a rule and a reason.</li>'
             f'<li><b>Offer a way in.</b> For students who want one, hand out the rule cards on page {D.IX("rules")}.</li></ul>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">Kit suggestions, not part of my sheets</span><ul style="margin:0">'
             f'<li style="font-size:12.4pt">Keep headphone volume moderate: distortion and noise can be much louder than they sound.</li>'
             f'<li style="font-size:12.4pt">Ask permission before recording a person, and keep recordings school-appropriate.</li>'
             f'<li style="font-size:12.4pt">Name and log every sound the moment it is recorded (Sound log, page {D.IX("sounds")}).</li>'
             f'<li style="font-size:12.4pt">Save a numbered version before every big change (page {D.IX("logicref")}).</li></ul></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Listening routine for slide 2</span><p style="margin:0;font-size:12.4pt">Play '
             f'the passage once. Ask: what rule does it seem to break, and does it feel planned or accidental? Play it again and take answers. '
             f'The same sounds can feel either way, and that gap is the lesson: intention.</p></div>'
             f'</div></div>')
    return D.page("Setup and a safe start", "SETUP", "Teacher", inner, n, key="setup")


def rules_page(n, wm=False):
    cards = [("Structure", "The ending comes first: the sections play in reverse order.", "this kit"),
             ("Structure", "Nothing repeats: no section, sound or pattern is used twice.", "this kit"),
             ("Tonality", "Use only dissonant chords.", "mine"),
             ("Tonality", "No home note: no pitch is allowed to feel like the centre.", "this kit"),
             ("Rhythm", "Make a track with no rhythm.", "mine"),
             ("Rhythm", "The pulse is steady, then speeds up and falls apart.", "this kit")]
    rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in cards)
    inner = (f'<p style="margin:0 0 3pt">Requirement 2 is to intentionally break at least one major musical convention (structure, tonality, rhythm, '
             f'etc.). Each picture shows a convention holding, then broken on purpose. Students may break any rule they can explain.</p>'
             f'<div style="width:7.4in;margin:2pt auto 3pt">{D.body_svg(rules_body(1250, "page rules", 26, 19, 17, 15))}</div>'
             f'{D.H2("Six rule cards", True)}'
             f'<table class="t" style="font-size:11.6pt;line-height:1.5"><tr><th style="width:16%">Convention</th><th>Rule card</th><th style="width:16%">From</th></tr>{rows}</table>'
             f'<div class="cols" style="gap:12pt"><div class="box acc-b"><span class="k">For my Easier variation</span>'
             f'<p style="margin:0;font-size:11.4pt;line-height:1.45">My notes say to provide 3–5 specific rules and let students choose one. '
             f'Cut these cards apart, or read them aloud. The two marked “mine” are my own examples from the variation; the other four were '
             f'added by this kit.</p></div>'
             f'<div class="box"><span class="k">Intention, not accident</span><p style="margin:0;font-size:11.4pt;line-height:1.45">A card is only '
             f'a starting point. Whatever rule a student picks, the Concept sheet asks them to say what it is and why, and the artist '
             f'statement says it again to the audience.</p></div></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Try this before Class 1 ends</span><p style="margin:0;font-size:11.4pt;line-height:1.45">'
             f'Ask students to name one convention they could break in a favorite style of music, without naming any song, and say what it '
             f'would feel like to hear it broken.</p></div>')
    return D.page("Rules to break", "RULES", "Teacher + student", inner, n, key="rules")


def example_page(n, wm=False):
    sec = ", ".join(f"{nm} {mmss(a)}–{mmss(b)}" for nm, a, b in SECTIONS)
    inner = (f'<p style="margin:0 0 3pt">An <b>invented piece, “{PIECE}”, and its artist statement, described on paper</b>: no audio is included, '
             f'so the numbers are easy to check. Students’ pieces will differ.</p>'
             f'{D.H2("1 · The concept", True)}'
             f'<table class="t" style="font-size:10pt;line-height:1.3"><tr><th style="width:17%">Rule broken</th><th style="width:30%">Concept</th>'
             f'<th style="width:28%">Sounds (recorded)</th><th>Effects and automation</th></tr>'
             f'<tr><td>Rhythm: a steady pulse</td><td>A pulse is a promise; the piece breaks it, then returns it wrong</td>'
             f'<td>A drawer click, a kettle hiss, a chair scrape played in reverse</td>'
             f'<td>Distortion automated up to 85% by 0:28; delay on the clicks; hiss filtered to a whisper in the Hush</td></tr></table>'
             f'{D.H2("2 · The plan: 50 seconds")}<div style="width:7.2in;margin:1pt auto 3pt">{D.body_svg(plan_body(1250, "page plan", 26, 19))}</div>'
             f'<p class="small" style="margin:0 0 3pt">{sec}. The plan is {TOTAL_S} seconds: inside my 45–60 second requirement.</p>'
             f'<div class="cols" style="gap:12pt"><div class="box"><span class="k">3 · Checking the numbers</span>'
             f'<p style="margin:0;font-size:11pt;line-height:1.42">Promise: {len(CLICKS_STEADY)} clicks, each {gaps(CLICKS_STEADY)[0]:g} s apart, which is '
             f'60 per minute. Break: {len(CLICKS_BREAK)} clicks whose gaps shrink from {gaps(CLICKS_BREAK)[0]:g} s to {min(gaps(CLICKS_BREAK)):g} s, then '
             f'stretch to {max(gaps(CLICKS_BREAK)):g} s. Return: {len(CLICKS_RETURN)} clicks with gaps of {min(gaps(CLICKS_RETURN)):g} s to '
             f'{max(gaps(CLICKS_RETURN)):g} s, so no pulse comes back. Sections: 10 + 18 + 8 + 14 = {TOTAL_S} s.</p></div>'
             f'<div class="box acc-b"><span class="k">4 · Why it is on purpose</span>'
             f'<p style="margin:0;font-size:11pt;line-height:1.42">A listener hears a clear pulse first, so they know what is being broken. '
             f'Every sound has a job: the drawer is the pulse, the kettle is the quiet, the reversed chair is the pull. The automation moves '
             f'with the rule instead of being random.</p></div></div>'
             f'{D.H2("5 · A sample artist statement (one paragraph)")}'
             f'<p style="font-size:11pt;line-height:1.45;margin:0">{STATEMENT}</p>')
    return D.page("Worked example · an invented piece", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def concept_page(n, wm=False):
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Step 1: brainstorm what “anti-music” means to you. What rule are you breaking and why? '
             f'Finish this page before you open a Logic session. Rules to try are on page {D.IX("rules")}.</p>'
             f'<div class="fl" style="margin-top:4pt"><b>To me, anti-music means:</b><span></span></div>'
             f'<div class="ln2" style="margin-bottom:6pt"></div>'
             f'{D.H2("The rule I will break")}'
             f'<div style="display:flex;gap:16pt;margin:0 0 6pt">'
             + "".join(f'<div style="flex:1">{D.chk(f"<b>{x}</b>", 13, "font-size:11.4pt;margin:0")}</div>' for x in ("Structure", "Tonality", "Rhythm"))
             + f'<div style="flex:1.4">{D.chk("<b>Other:</b> ____________", 13, "font-size:11.4pt;margin:0")}</div></div>'
             f'<div class="fl" style="margin-bottom:10pt"><b>The specific rule, in one sentence:</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:10pt"><b>Why I am breaking it:</b><span></span></div>'
             f'<div class="ln2" style="margin-bottom:6pt"></div>'
             f'<div class="fl" style="margin-bottom:10pt"><b>What I want a listener to feel:</b><span></span></div>'
             f'{D.H2("My concept in one line")}'
             f'<div class="box acc-b"><p style="margin:0;font-size:11.8pt;line-height:2.2">My piece breaks the rule that '
             f'<span style="display:inline-block;width:2.2in;border-bottom:1pt solid #000"></span> because '
             f'<span style="display:inline-block;width:2.2in;border-bottom:1pt solid #000"></span>.</p></div>'
             f'{D.H2("Intention check")}'
             + "".join(D.chk(c, 12, "font-size:11pt;margin-bottom:5pt") for c in [
                 "I can say the rule I am breaking in one sentence",
                 "I can say why I am breaking it",
                 "A listener could tell the rule was broken on purpose",
                 "My teacher has seen this page (initials: ______)"]) +
             f'<div class="fl" style="margin-top:6pt"><b>Early ideas for sounds:</b><span></span></div><div class="ln2"></div><div class="ln2"></div><div class="ln2" style="margin-bottom:2pt"></div>')
    return D.page("Concept sheet", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="concept")


def sounds_page(n, wm=False):
    rows = "".join("<tr><td style='height:36pt'></td><td></td><td></td><td></td></tr>" for _ in range(9))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Step 2: record or create unconventional sound sources. Write down every sound you '
             f'make, how it was made, and what you will do to it. Name each file the moment you record it.</p>'
             f'<table class="map"><tr><th style="width:24%">Sound and file name</th><th style="width:16%">Recorded or created?</th>'
             f'<th style="width:30%">How I will change it (reverse, stretch, effect)</th><th>What it does in my piece</th></tr>{rows}</table>'
             f'<div class="fl" style="margin-top:9pt"><b>The strangest sound I made, and how:</b><span></span></div>'
             f'<div class="fl"><b>A sound that did not work, and why:</b><span></span></div>'
             f'<div class="box acc-b"><span class="k">Before you move on</span><p style="margin:0;font-size:10.8pt">Do at least three sounds serve '
             f'your rule? Is every file named and saved in the project folder? Can you say what each effect does to its sound?</p></div>')
    return D.page("Sound log", "STUDENT", "Class 2", inner, n, wm, name=True, key="sounds")


def blueprint_page(n, wm=False):
    rows = "".join("<tr><td style='height:46pt'></td><td></td><td></td><td></td><td></td></tr>" for _ in range(6))
    inner = (f'<div class="fl"><b>Length check: my piece will be</b><span style="flex:0 0 0.9in"></span><b>seconds (must be 45–60).  The rule it breaks:</b>'
             f'<span></span></div>'
             f'<p style="margin:2pt 0 5pt;font-size:10.8pt">Steps 3 and 4: use Logic to construct your piece, leaning into effects, automation and '
             f'distortion. Even though you are breaking rules, it should feel intentional, not accidental. Plan the sections, then check them.</p>'
             f'<table class="map"><tr><th style="width:15%">Section</th><th style="width:13%">Time</th><th style="width:26%">Sounds playing</th>'
             f'<th style="width:25%">Effects and automation</th><th>How this breaks the rule</th></tr>{rows}</table>'
             f'<div class="fl" style="margin-top:8pt"><b>The moment the rule breaks (time):</b><span></span></div>'
             f'<div class="fl"><b>What I draw in automation, and where:</b><span></span></div>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">Is it on purpose?</span>'
             + "".join(D.chk(c, 12, "font-size:10.8pt;margin-bottom:3pt") for c in [
                 "A listener could tell which rule I broke",
                 "Every sound has a job",
                 "The piece changes over its length, not just once",
                 "I can explain every choice I made"]) + '</div>'
             f'<div class="fl" style="margin-top:6pt"><b>Something I will change after a classmate listens:</b><span></span></div>')
    return D.page("Build plan", "STUDENT", "Classes 3–5", inner, n, wm, name=True, key="blueprint")


def statement_page(n, wm=False):
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Step 5: explain what you did and why, in one paragraph. Your artist statement tells your '
             f'audience what to listen for. Plan it here, then submit the final version on your class page.</p>'
             f'<div class="fl"><b>The specific rule I broke:</b><span></span></div>'
             f'<div class="fl"><b>How I broke it (sounds, effects, automation):</b><span></span></div>'
             f'<div class="ln2" style="margin-bottom:6pt"></div>'
             f'<div class="fl"><b>Why I made that choice:</b><span></span></div>'
             f'<div class="ln2" style="margin-bottom:6pt"></div>'
             f'<div class="fl"><b>What the listener should listen for (a time and a sound):</b><span></span></div>'
             f'{D.H2("Sentence starters")}'
             f'<ul style="font-size:10.8pt"><li>My piece breaks the rule that…</li><li>I did this by recording… and then…</li>'
             f'<li>I chose this because…</li><li>Listen for the moment when…</li></ul>'
             f'{D.H2("My draft: one paragraph")}<div class="lines" style="min-height:100pt"></div>'
             f'{D.H2("Statement check")}'
             + "".join(D.chk(c, 12, "font-size:10.8pt;margin-bottom:3pt") for c in [
                 "It names the specific rule I broke",
                 "It explains my reasoning",
                 "It tells the listener what to listen for",
                 "It is one paragraph and says something only I could say"]))
    return D.page("Artist statement planner", "STUDENT", "Class 6", inner, n, wm, name=True, key="statement")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "rules": rules_page, "example": example_page,
         "concept": concept_page, "sounds": sounds_page, "blueprint": blueprint_page, "statement": statement_page}


# ================================================================ content checks (example arithmetic, owner text, no audio)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 5), reqs=(REQS, 5), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 3))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp} (the owner's count)")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is the owner's /25, levels 1-5")
    if [c for c, _ in RUBRIC] != ["Creativity & Originality", "Technical Skill / DAW Use", "Composition & Structure",
                                  "Sound Design & Mix Quality", "Documentation & Presentation"]:
        errs.append("rubric categories must be the owner's, in order")
    if FILE_NAME not in CHECK[2] or "Anti-Music Manifesto" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    if "45–60 seconds" not in REQS[0] or "at least one" not in REQS[1]:
        errs.append("requirements: 45-60 seconds and at least one convention")
    # the worked example adds up
    if SECTIONS[0][1] != 0 or SECTIONS[-1][2] != TOTAL_S or any(b != c for (_, _, b), (_, c, _) in zip(SECTIONS, SECTIONS[1:])):
        errs.append("sections must tile 0-50 seconds")
    if not 45 <= TOTAL_S <= 60 or sum(b - a for _, a, b in SECTIONS) != TOTAL_S:
        errs.append("example length must be 45-60 s and the sections must sum to it")
    if len(set(gaps(CLICKS_STEADY))) != 1 or gaps(CLICKS_STEADY)[0] != 1.0 or len(CLICKS_STEADY) != 10:
        errs.append("Promise: ten clicks, exactly one second apart")
    if len(set(gaps(CLICKS_BREAK))) < 8 or not (10 <= CLICKS_BREAK[0] and CLICKS_BREAK[-1] < 28) or gaps(CLICKS_BREAK)[0] != 0.9 \
            or min(gaps(CLICKS_BREAK)) != 0.3 or max(gaps(CLICKS_BREAK)) != 3.8:
        errs.append("Break clicks: gaps 0.9 shrinking to 0.3 then stretching to 3.8, all inside 10-28 s")
    if len(set(gaps(CLICKS_RETURN))) < 5 or not (36 <= CLICKS_RETURN[0] and CLICKS_RETURN[-1] < 50):
        errs.append("Return clicks must be uneven and inside 36-50 s")
    if gaps(CLICKS_RETURN)[0] != 1.5 or min(gaps(CLICKS_RETURN)) != 0.1 or max(gaps(CLICKS_RETURN)) != 3.9:
        errs.append("Return gaps are 0.1 to 3.9 s on the example page text")
    if not (SECTIONS[2][1] <= HISS[1] and HISS[0] < SECTIONS[1][2] and HISS[1] == SECTIONS[2][2]):
        errs.append("kettle hiss must run through the Hush")
    if any(not 0 <= a < b <= TOTAL_S for a, b in SCRAPES + [HISS]):
        errs.append("lane blocks inside the piece")
    if [t for t, _ in DISTORT] != sorted(t for t, _ in DISTORT) or any(not 0 <= v <= 100 for _, v in DISTORT) \
            or dict(DISTORT)[28] != 85:
        errs.append("distortion automation: times in order, 0-100, 85% at 0:28")
    if len(STATEMENT.split(". ")) < 4 or "\n" in STATEMENT:
        errs.append("sample statement is one paragraph")
    if len(RESOURCES) != 3:
        errs.append("three owner resources")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    txt = " ".join(flat)
    for need in ("No audio, video, songs or examples are included", "invented piece, “Kitchen Table”",
                 "Your Name – Anti-Music Manifesto", "Final Grade = Average of Student + Teacher", "John Cage"):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up:
        errs.append("UPLOAD.md: must say no audio is included and record the open questions")
    for i in (2, 5, 6, 10, 13, 14, 15):   # slides that shorten the owner's wording must say so
        if "shortened" not in notes[i].lower() and "shortens" not in notes[i].lower():
            errs.append(f"deck slide {i + 1} notes: must say the owner's wording is shortened")
    ch = flat[D.IX("changes") - 1]
    for s in ("slide 3", "slide 6", "slide 7", "slide 11", "slide 14", "slide 15", "slide 16"):
        if s not in ch:
            errs.append(f"'What changed' page must list {s}")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or any("Concept sheet" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in ("Billie", "Beatles", "Spotify", "Daft", "Skrillex", "Disney", "Minecraft", "Mario", "Taylor", "Nirvana", "Radiohead"):
        if banned in alldeck or banned in txt:
            errs.append(f"must not name songs, artists or services beyond the owner's ({banned})")
    for artist in ("Merzbow", "Aphex", "Death Grips"):     # the owner's tip 2 only: nowhere in the deck
        if artist in alldeck:
            errs.append(f"the deck must not name artists ({artist})")
    return errs


def check_summary():
    return (f"The invented piece is {TOTAL_S} s (10 + 18 + 8 + 14), its Promise clicks are 1 s apart and its Break gaps run "
            f"{min(gaps(CLICKS_BREAK)):g}-{max(gaps(CLICKS_BREAK)):g} s; "
            f"the owner's lists counted (4 goals, 5 terms, 5 requirements, 7 steps, 4 tips, 6 checklist items, 4 struggles, 3 resources); "
            f"{len(CHANGES)} wording changes disclosed; no audio included; grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
