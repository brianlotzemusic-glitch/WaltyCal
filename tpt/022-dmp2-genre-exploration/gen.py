#!/usr/bin/env python3
"""DMP2 project: Genre Exploration (TpT 022): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Genre Exploration > "Genre Exploration - Project Sheet & Rubric" (rubric 5 categories scored 1-5, /25, final
grade = average of student and teacher scores), TEACHER NOTES > "Genre Exploration - Teacher Notes" (7 class periods), and the project's
entry on "DMP2 - Project Menu" (the June 2026 menu; owner, 17 Oct 2026: the June entry may be quoted). These three set the project
text, steps, rubric and pacing (owner rule, 17 Oct 2026).
Supporting artifacts the Teacher Notes name: the Genre Research Google Form (the owner's own form, in Drive under the older Genre
Exploration folder; Drive's connector cannot read a Form's questions, so it is NOT included and the kit prints a paper research sheet
as a planning copy beside it), streaming services for reference tracks (named as the owner wrote them; no track, link or playlist is
included) and a shared class playlist (the teacher's to make). The older "Genre Exploration Project" doc (2025) is not a source.

NO AUDIO IS INCLUDED and no real genre, artist or song is named (the owner's sheets name none). The worked example is an invented
genre ("Harbor Drift", 80 BPM, 52 bars, 2 minutes 36 seconds) with three invented reference tracks, all on paper; every picture
(vinyl hero, steps, genre fingerprint, arrangement map) is drawn in code.
The sheet already asks for a written reflection (requirement 6, step 6, checklist), so the shared Reflection element is switched off
(REFLECTION = False) and the kit's own "reflect" page is the prompt page the owner's fourth struggle asks for.
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "genre-exploration"
TITLE = "Genre Exploration"
ACCENT = "#0A7EA4"          # this product's single accent: lake cyan (008 red, 009 orange, 010 violet, 011 teal, 012 blue, 013 green, 014 magenta, 015 gold, 016 olive, 017 sienna, 018 steel blue, 019 wine, 020 pine, 021 indigo)
ACC_LIGHT = "#CDE6F0"
PRICE = "11.00"
CLASSES = 7
REFLECTION = False          # the owner's sheet already requires a written reflection; this kit adds only a prompt page (key "reflect")
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-021).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "Genre Exploration in Logic Pro | Production Research Project | High School"
DESC_START = "Genre research and music production project for high school:"
DESC_MUST = ["Genre Exploration", "reference track", "no audio", "Padlet"]
ZIP_DIR = "Genre Exploration - Hudson Beat"
ZIP_DATE = (2026, 10, 19, 12, 0, 0)
TYPE = "Structured Project"
PROJ_LINE = "Digital Music Production | <i>Structured Project</i> | 7 class periods"
DECK_STRAP = "Make a track in a genre you do not know"
BANNED_EXTRA = []

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Structured", "Research & Style"
MENU_DESC = "Step outside your comfort zone and produce a track in an unfamiliar genre. Research, compose, and reflect."
OVERVIEW = ("Step outside your comfort zone. Pick a musical genre you’re unfamiliar with, research what defines it, and produce a track "
            "that captures its signature sound. This project pushes you to listen deeper, experiment with new sounds, and grow as a "
            "producer.")
GOALS = ["Research and identify the defining characteristics of an unfamiliar genre",
         "Compose a track that authentically reflects the genre’s conventions",
         "Apply genre-appropriate instrumentation, production techniques, and mixing",
         "Reflect on the creative process and what you learned"]
VOCAB = [("Genre", "A category of music defined by shared characteristics like rhythm, instrumentation, and structure"),
         ("Reference Track", "A professionally produced song you study and use as a guide for your own production"),
         ("Instrumentation", "The specific instruments and sounds used in a piece of music"),
         ("Song Form", "How a song is structured — verse, chorus, bridge, etc.")]
REQS = ["Choose a genre you are NOT already comfortable producing in",
        "Complete the Genre Research Google Form before composing",
        "Your track should follow typical song forms and conventions of the genre",
        "Use instruments, synths, or samples authentic to the genre",
        "Apply genre-appropriate mixing and production techniques",
        "Write a short reflection (1 paragraph minimum) on what you learned"]
STEPS = ["<b>Research</b> — Select your genre and complete the Google Form analyzing its key characteristics "
         "(Genre research sheet: page @RESEARCH)",
         "<b>Listen</b> — Study 2–3 reference tracks and break down their elements (Reference track log: page @LISTEN)",
         "<b>Sketch</b> — Build an 8–16 bar loop that captures the genre’s essence (Loop and form sketch: page @SKETCH)",
         "<b>Compose</b> — Develop the full song structure. Layer instrumentation and refine. (Work plan: page @WORKPLAN)",
         "<b>Mix</b> — Apply genre-appropriate mixing techniques. Polish the track.",
         "Write your reflection and finalize your bounce (Reflection: page @REFLECT)",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["Commit to the genre fully. Don’t just add one instrument that “sounds kinda like it.”",
        "Use reference tracks constantly. Pull them into Logic and compare your mix.",
        "Don’t be afraid to sound weird to yourself — that’s the point.",
        "Your Google Form research will save you time later."]
FILE_NAME = "“Your Name – Genre Exploration”"
CHECK = ["Genre Research Google Form completed",
         "Bounced .mp3 or .wav uploaded to your class page",
         "Zipped .logicx project file uploaded to your class page",
         f"Files named correctly: {FILE_NAME}",
         "Written reflection submitted via your class page",
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
TN_REINFORCES = ("Builds analytical listening, research skills, and genre awareness. Forces students out of their default sound palette.")
STRUGGLES = ["Students pick genres too close to what they already make.",
             "Shallow research — require specific reference tracks and concrete elements.",
             "Students nail the instruments but miss the production style.",
             "Reflections are thin. Give specific prompts."]
VAR_EASY = "Provide a curated list of 5–8 genres with starter reference tracks and cheat sheets."
VAR_HARD = "Require 2+ minutes with a full arrangement. Add a requirement for 2 genre-specific mixing techniques."
RESOURCES = [("Genre Research Google Form (link on your class page)",
              "Kept as your own form: it is yours to share, and it is not included, because the Drive connector this kit was built with "
              "cannot read a Form’s questions. The kit adds a paper Genre research sheet beside it (page @RESEARCH) as a planning copy "
              "for the same job: the characteristics of the genre. Requirement 2 stays: students still complete your form."),
             ("Encourage Spotify, YouTube, or Apple Music for reference tracks",
              "Kept as I wrote it. No track, link or playlist is included, so every reference track is one the student chooses. The "
              "Reference track log (page @LISTEN) is where students write what they hear."),
             ("Consider a shared class playlist of genre examples",
              "Kept. The playlist is yours to make: nothing is included. The Genre shortlist (page @SHORTLIST) gives you a place to "
              "write the genres and starter tracks you pick.")]
TN_NOTE = "Students often surprise themselves by enjoying genres they thought they’d hate."
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Creativity &amp; Originality: ask what the student changed from the genre’s usual sound, then listen for it. Copying "
                "the genre well is the assignment; adding something of their own is what lifts the score.",
                "Technical Skill: open the project. Which Logic tools did they use to get the genre’s sounds and its production style?",
                "Composition &amp; Structure: compare the form with the Loop and form sketch (page @SKETCH) and with the typical song forms "
                "in the Reference track log (page @LISTEN).",
                "Sound Design &amp; Mix Quality: put a reference track next to theirs, as my second tip says, and ask where the mix "
                "differs. Instruments right but production wrong is my third struggle.",
                "Documentation &amp; Presentation: the research sheet, the reference log, the reflection paragraph (page @REFLECT) and "
                "the Padlet questions are the evidence."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Introduction. Select genre and begin Google Form research.",
     "do": "Slides 1–7: hook, what the project is, the five steps, four words to know, steps 1 and 2. Hand out the project sheet and "
           "the Genre research sheet. Approve each student’s genre before they leave.", "slides": (1, 7),
     "pages": ["research", "proj1", "proj2", "proj3", "vocab"],
     "deck": "What genre would you skip? · five steps · four words · research"},
    {"n": 2, "owner": "<b>Class 2:</b> Finish research. Begin sketching an 8–16 bar loop.",
     "do": "Slides 8–10: a genre’s fingerprint, instruments are not enough, before you compose. Hand out the Reference track log and "
           "the Loop and form sketch. Check each research sheet for concrete elements.", "slides": (8, 10),
     "pages": ["listen", "sketch"], "deck": "Genre fingerprint · production, not just instruments · before you compose"},
    {"n": 3, "owner": "<b>Classes 3–5:</b> Working days — expand composition, refine arrangement and mix.",
     "do": "Slides 11–12: steps 3 and 4, and the worked example on paper. Hand out the Work plan. Then work time.", "slides": (11, 12),
     "pages": ["workplan"], "deck": "Working day: sketch, compose, worked example"},
    {"n": 4, "owner": None, "do": "Slides 13–14: use your references constantly, and mix like the genre. Then work time.", "slides": (13, 14),
     "pages": ["workplan"], "deck": "Working day: compare to references, mix like the genre"},
    {"n": 5, "owner": None, "do": "Full working day: expand, refine, mix. Ask each student to play a reference and then their own track, "
     "and say what is different.", "slides": None, "pages": [], "deck": "Working day: expand, refine, mix"},
    {"n": 6, "owner": "<b>Class 6:</b> Final mix, bounce, write reflection. Prepare presentations.",
     "do": "Slides 15–17: mix, reflect and bounce, what to turn in, the rubric. Students write the reflection paragraph (page "
           "@REFLECT) and post their three Padlet questions.", "slides": (15, 17), "pages": ["reflect", "rubric", "present"],
     "deck": "Mix · reflect · bounce · checklist · rubric"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 18–19: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (18, 19), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one rule for Class 1</span>'
    '<p style="margin:0;font-size:9.2pt">Approve every genre before the student leaves. If it is close to what they already make '
    '(my first struggle), ask: what would you not normally reach for?</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:9.2pt">Working days; Class 5 has no new slide. '
    'Circulate with one question: is that the instrument, or the production style?</p></div></div>')
PACING_SIZE = 9.4

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (checklist items 2, 3 and 5, and in the Genre Research Google Form resource).",
    "Page numbers are added to steps 1 to 4 and step 6 (the Genre research sheet, Reference track log, Loop and form sketch, Work plan "
    "and Reflection page).",
    "My Genre Research Google Form is yours and is not included. The kit adds a paper Genre research sheet beside it as a planning "
    "copy (page @RESEARCH); requirement 2 is unchanged.",
    "My resources about streaming services and a shared class playlist are listed as I wrote them. No track, link or playlist is "
    "included.",
    "My Easier variation (a curated list of 5–8 genres with starter reference tracks and cheat sheets) is laid out as a blank "
    "Genre shortlist for you to fill in (page @SHORTLIST). The kit names no genre, because my sheets name none.",
    "My pacing guide’s “Classes 3–5” row spans the Class 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "<b>Reflection page, not a new task (page @REFLECT).</b> My sheet already asks for a written reflection (requirement 6, step 6, "
    "checklist), so this kit adds no extra task. It adds prompts only, because my fourth struggle says to give specific prompts, and "
    "follows my definition (a written or oral conversation about how the student did and what they would do differently), so you may "
    "take it orally. No points, no rubric row.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 3 shortens my overview and a goal, slide 6 shortens "
    "my four vocabulary definitions, slides 7 and 10 shorten steps 1 and 2, slide 9 shortens requirements 4 and 5, my third struggle "
    "and tip 1, slide 11 shortens steps 3 and 4, slide 13 shortens tips 2 to 4, slide 14 shortens step 5 and the Harder variation, "
    "slide 15 shortens steps 5 to 7, slide 16 shortens the submission checklist, and slide 18 shortens step 7.",
]
CHANGES_MUST_MENTION = ["your class page", "Page numbers", "not included", "Genre shortlist", "Classes 3–5", "Layout only",
                        "Reflection page", "intro deck shortens"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the overview, goals, vocabulary, six requirements, steps (apart "
        "from the page numbers), tips, checklist and file name (“Your Name – Genre Exploration”), the /25 rubric, what the project "
        "reinforces, the four struggles, the variations, my three resources, my pacing and my closing note, and the project menu entry "
        "on page @OVERVIEW. No rubric row is added and the requirements are unchanged.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: the how-to, overview and setup pages, the teacher "
                "moves in the pacing guide, the grading suggestions, the Logic quick reference, the Genre shortlist (my Easier variation "
                "as a blank, my Harder variation laid out), the worked example (an invented genre, three invented reference tracks and a "
                "2:36 arrangement, on paper, not audio), the research sheet, reference log, loop sketch and Work plan, the vocabulary "
                "and presentation pages, the Reflection prompts and the intro deck. None adds a requirement or a rubric row.")

# ================================================================ the worked example (Hudson Beat original: an invented genre on paper)
GENRE = "Harbor Drift"
BPM = 80
BAR_S = 4 * 60 / BPM                  # 3 seconds per bar in 4/4
BARS = 52
TOTAL_S = 156
SECTIONS = [("Intro", 0, 12), ("Verse", 12, 36), ("Chorus", 36, 60), ("Verse", 60, 84), ("Chorus", 84, 108), ("Bridge", 108, 120),
            ("Chorus", 120, 144), ("Outro", 144, 156)]       # seconds
SECTION_BARS = [4, 8, 8, 8, 8, 4, 8, 4]
LANES = ["Drums", "Bass", "Pads", "Lead", "FX"]
SPANS = {"Drums": [(12, 108), (120, 144)], "Bass": [(12, 108), (120, 144)], "Pads": [(0, 156)],
         "Lead": [(36, 60), (84, 108), (120, 144)], "FX": []}
RISERS = [(32, 36), (80, 84), (116, 120)]
BASS_NOTES = [0, 0, 2, 1, 0, 0, 3, 1]
REFS = [("Reference A", "about 80 BPM", [4, 8, 8, 8, 8, 4], "starts with the pads alone"),
        ("Reference B", "about 84 BPM", [4, 8, 8, 8, 8, 8, 4], "drums wait until the first verse"),
        ("Reference C", "about 76 BPM", [4, 8, 8, 4, 8, 8, 4], "a short bridge before the last chorus")]
GENRE_ROWS = [("Tempo", "about 76–84 beats per minute"),
              ("Rhythm", "soft kick on beats 1 and 3, light brushed hi-hat in eighth notes, no heavy snare"),
              ("Instruments and sounds", "wide warm pads, a plucked bass, a bell-like lead; no distorted guitars"),
              ("Song form", "intro, verse, chorus, verse, chorus, a short bridge, chorus, outro"),
              ("Production style", "lots of space: reverb on the pads, the drums’ highs rolled off, the bass quiet and centered")]
WEAK = "I used pads, a bass and a bell. It is Harbor Drift."
STRONG = ("The instruments are only half of Harbor Drift. The drums’ highs are rolled off so they stay soft, the pads sit in a wide "
          "reverb while the bass stays dry and in the center, and the whole track is quiet and spacious like Reference A, B and C. "
          "I checked this by playing Reference A next to my track in Logic and matching the space.")
TECHNIQUES = [("Roll off the drums’ highs", "A gentle low-pass filter on the drums keeps the hi-hat soft, as in all three references."),
              ("Wide reverb on the pads only", "A long reverb on the pads gives the space; the bass stays dry and centered so it is not washed out.")]
QUESTIONS = ["Where did you first hear the track open up?",
             "Which part would you turn up or down, and why?",
             "Does it sound like the genre I described?"]
THIN = "I learned a lot. It was fun and I liked the genre more than I thought."
USEFUL = ("I thought I would hate slow, spacious music, but I liked it. The hard part was the mix: my first bounce had every part loud and "
          "dry, so it sounded like a different genre even with the right instruments. Comparing to Reference A showed me the drums "
          "needed their highs rolled off. Next time I would start with the pads and the space first, and I would check my references "
          "in the first class instead of the fourth. My strongest rubric category is Composition and Structure; my weakest is Mix.")


def mmss(t):
    return f"{int(t) // 60}:{int(round(t)) % 60:02d}"


# ================================================================ drawings (original, code-drawn: black + accent only)
def hero_body():
    W, H = 1100, 560
    out = []
    cx, cy = 360, 290
    out.append(f'<circle cx="{cx}" cy="{cy}" r="250" fill="#000"/>')
    for r in (220, 190, 160, 130):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#fff" stroke-width="2.5" opacity=".55"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="92" fill="{ACCENT}" stroke="#fff" stroke-width="5"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="12" fill="#fff"/>')
    out.append('<line x1="1010" y1="60" x2="640" y2="250" stroke="#000" stroke-width="16" stroke-linecap="round"/>')
    out.append('<circle cx="1010" cy="60" r="34" fill="#fff" stroke="#000" stroke-width="8"/>')
    out.append('<rect x="560" y="236" width="100" height="46" rx="10" fill="#000" transform="rotate(-27 610 259)"/>')
    for k, (txt_w, on) in enumerate([(300, True), (220, False), (260, False)]):
        y = 330 + k * 72
        out.append(f'<rect x="700" y="{y}" width="{txt_w}" height="52" rx="12" fill="{ACCENT if on else "#fff"}" stroke="#000" stroke-width="5"/>')
        out.append(f'<circle cx="730" cy="{y + 26}" r="9" fill="{"#fff" if on else "#000"}"/>')
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
    return cards_body([("Research", "pick a genre"), ("Listen", "2–3 references"), ("Sketch", "8–16 bar loop"),
                       ("Compose", "full song form"), ("Mix", "genre sound")],
                      "Then write your reflection, bounce, present and get feedback", W, name, fs, cs, True)


def finger_body(W=1600, name="fingerprint pic", fs=30, cs=22):
    return cards_body([("Rhythm", "drums · groove"), ("Sound", "instruments · synths"), ("Form", "sections · length"),
                       ("Production", "mix · space · FX")],
                      "Four things to find in a genre before you compose", W, name, fs, cs, False)


def plan_body(W=1600, name="plan", fs=24, ts=20):
    gx = 200
    pwid = W - gx - 16

    def X(t):
        return gx + pwid * t / TOTAL_S

    out = []
    sh = 58
    shade = {"Intro": "#4a4a4a", "Verse": "#000", "Chorus": ACCENT, "Bridge": "#4a4a4a", "Outro": "#4a4a4a"}
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
        elif nm == "Pads":
            for a, b in SPANS[nm]:
                j = 0
                t0 = a
                while t0 < b - 1e-9:
                    t1 = min(b, t0 + 4 * BAR_S)
                    out.append(f'<rect x="{X(t0) + 1:.1f}" y="{yy + 14}" width="{X(t1) - X(t0) - 2:.1f}" height="{lh - 28}" rx="5" fill="{"#7a7a7a" if j % 2 == 0 else "#4a4a4a"}"/>')
                    t0 = t1
                    j += 1
        elif nm == "Lead":
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
    for t in (0, 12, 36, 60, 84, 108, 120, 144, 156):
        lbl = mmss(t)
        anc = "start" if t == 0 else ("end" if t == TOTAL_S else "middle")
        out.append(f'<line x1="{X(t):.1f}" y1="{ty - 6}" x2="{X(t):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(t) + (2 if t == 0 else (-2 if t == TOTAL_S else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 80)
    return "".join(out), W, ty + ts + 22


DRAWINGS = {"hero": lambda: D.stack([hero_body()], 40), "cycle": lambda: cycle_body(1600), "fingerprint": lambda: finger_body(1600),
            "arrange": lambda: plan_body(1600, "arrange pic")}
DRAWING_PX = {"hero": 1900, "cycle": 2000, "fingerprint": 2000, "arrange": 2000}
SIDE = {"cycle": ["Research: pick and analyze a genre", "Listen: study 2–3 references", "Sketch, then compose the full form",
                  "Mix to match the genre’s sound"],
        "fingerprint": ["Rhythm: the groove", "Sound: instruments and synths", "Form: how the song is built",
                        "Production: how it is mixed"],
        "arrange": ["An invented genre, on paper", "Sections you can name", "Layers that come and go", "Space is part of the genre"]}


def label_extras():
    plan_body(1250, "page arrange", 24, 20)
    cycle_body(1250, "page cycle", 28, 20)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Genre Exploration", "Step outside your comfort zone.",
     "Class 1, the first minute. No audio is included in this deck. Open with my overview: step outside your comfort zone. Pick a "
     "musical genre you are unfamiliar with, research what defines it, and produce a track that captures its signature sound. Say that "
     "the project pushes students to listen deeper, experiment with new sounds, and grow as producers."),
    (1, "listen", "Think: a genre you would skip", "Think, then share|Teacher: no audio is needed. Ask the questions aloud and take "
     "a few answers.|Which genre would you never choose to listen to?|What do you think it sounds like, and how do you know?|"
     "What would you need to find out to make it?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker and no one else's music is used. The point "
     "is my closing note: students often surprise themselves by enjoying genres they thought they would hate. Do not name a genre for "
     "them; let them say what they would skip. It sets up my first struggle, picking a genre too close to what they already make."),
    (1, "bullets", "What is Genre Exploration?", "Pick a genre you are unfamiliar with|Research what defines it|Produce a track that "
     "captures its signature sound|Goal: listen deeper and grow as a producer",
     "My overview and first goals, shortened to fit the slide. Pick a musical genre you are unfamiliar with, research what defines it, "
     "and produce a track that captures its signature sound. The project pushes you to listen deeper, experiment with new sounds, and "
     "grow as a producer. Students write the four vocabulary terms in their own words on the vocabulary page; slide 6 introduces them."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: introduction, select a genre and begin the Google Form research. "
     "Class 2: finish research and begin sketching an 8 to 16 bar loop. Classes 3 to 5 are working days: expand the composition, "
     "refine the arrangement and mix. Class 6: final mix, bounce, write the reflection, and prepare presentations. Class 7: "
     "presentations with Padlet Q and A peer feedback. Hand out the project sheet now."),
    (1, "pic", "Five steps, research to mix", "cycle",
     "Class 1. The first five steps of my project sheet, in order: research, listen, sketch, compose, mix. Then students write their "
     "reflection, finalize the bounce, and present with Padlet feedback. Point to each box and say roughly when it happens: research "
     "today and in Class 2, the sketch in Class 2, composing on the working days, the mix in Classes 4 to 6. The step names are mine; "
     "the picture and its short labels are the kit's own."),
    (1, "bullets", "Four words to know", "Genre: a category defined by shared traits|Reference track: a song you study as your guide|"
     "Instrumentation: the instruments and sounds used|Song form: how a song is structured",
     "My four vocabulary terms, shortened to fit the slide. Genre: a category of music defined by shared characteristics like rhythm, "
     "instrumentation and structure. Reference track: a professionally produced song you study and use as a guide for your own "
     "production. Instrumentation: the specific instruments and sounds used in a piece of music. Song form: how a song is structured, "
     "verse, chorus, bridge and so on. The full definitions are on the vocabulary page."),
    (1, "steps", "Steps 1 and 2: research, listen", "Select a genre you do not already make|Complete the Google Form on its key "
     "characteristics|Study 2–3 reference tracks|Break down their elements|Write what you hear on the log",
     "Steps 1 and 2 of the project sheet, shortened to fit the slide. Step 1, research: select your genre and complete the Google Form "
     "analyzing its key characteristics. Step 2, listen: study 2 to 3 reference tracks and break down their elements. The last line is "
     "the kit's own suggestion, not my step: students write what they hear on the Reference track log. My resources encourage "
     "Spotify, YouTube or Apple Music for reference tracks; students choose their own tracks. Approve each genre before they leave."),
    (2, "pic", "A genre has a fingerprint", "fingerprint",
     "Class 2. A kit picture, not from my sheets, built from my definition of a genre: shared characteristics like rhythm, "
     "instrumentation and structure, plus the production techniques my requirement 5 names. Ask students to find all four in their "
     "reference tracks: the rhythm, the sound, the form and the production. My second struggle is shallow research, so require specific "
     "reference tracks and concrete elements, not a vague impression."),
    (2, "bullets", "Instruments are not enough", "Commit fully, not just one instrument|Use sounds that belong to the genre|Apply "
     "genre-appropriate mixing and production|Compare your mix to your references",
     "Requirements 4 and 5 and my first tip, shortened to fit the slide. Commit to the genre fully; do not just add one instrument that "
     "sounds kind of like it. Use instruments, synths or samples authentic to the genre. Apply genre-appropriate mixing and production "
     "techniques. This answers my third struggle, students who nail the instruments but miss the production style. The fourth line comes "
     "from my second tip: pull your references into Logic and compare your mix."),
    (2, "check", "Before you compose", "A genre I am not comfortable producing in|Google Form research completed|2–3 reference "
     "tracks studied|Rhythm, sound, form and production noted|My teacher has seen my genre",
     "The checklist is the kit's own, built from requirements 1 and 2, step 2 (shortened here) and my first two struggles. Students "
     "tick each line on the Genre research sheet and the Reference track log before they start composing. Send a student back who has "
     "picked a genre close to what they already make, with a question, and send back research that names no concrete elements."),
    (3, "steps", "Steps 3 and 4: sketch, compose", "Build an 8–16 bar loop that captures the genre’s essence|Develop the full song "
     "structure|Layer instrumentation and refine|Follow typical song forms of the genre",
     "Class 3 is the first working day, and Classes 4 and 5 continue it. Steps 3 and 4 of the project sheet, shortened to fit the "
     "slide. Step 3, sketch: build an 8 to 16 bar loop that captures the genre's essence. Step 4, compose: develop the full song "
     "structure, layer instrumentation and refine. The last line comes from requirement 3. Hand out the Work plan."),
    (3, "pic", "Worked example: invented genre", "arrange",
     "Class 3. An invented genre, Harbor Drift, described on paper; nothing here is audio and no real genre is named. It is 80 beats "
     "per minute and 52 bars of 4/4, which is two minutes thirty-six. Read the sections across the top: intro, verse, chorus, verse, "
     "chorus, a short bridge, a last chorus and an outro. The lanes show drums and bass entering after the intro, pads all the way "
     "through, the lead in the choruses, and risers before each chorus. The genre card, three invented reference tracks and the numbers "
     "are on the worked example page."),
    (4, "bullets", "Use your references constantly", "Pull a reference into Logic and compare your mix|Listen: does yours feel the "
     "same?|Don’t be afraid to sound weird to yourself|Your Google Form research will save you time",
     "My tips 2, 3 and 4, shortened to fit the slide. Use reference tracks constantly: pull them into Logic and compare your mix. Do not "
     "be afraid to sound weird to yourself; that is the point. Your Google Form research will save you time later. The kit suggests "
     "that a reference sits on its own muted track and is removed before bouncing, so only the student's own track is handed in."),
    (4, "bullets", "Mix like the genre", "Step 5: apply genre-appropriate mixing techniques|Polish the track|Harder option: name 2 "
     "genre-specific mixing techniques|Leave a full class for the final mix",
     "Step 5 of the project sheet and my Harder variation, shortened to fit the slide. Mix: apply genre-appropriate mixing techniques "
     "and polish the track. My Harder variation adds a requirement for two genre-specific mixing techniques; offer it to students who "
     "are ready. The last line is the kit's own suggestion, not my step: protect one full class for the final mix. The worked example "
     "page shows two techniques for the invented genre."),
    (6, "steps", "Mix, reflect, bounce", "Mix: apply genre-appropriate techniques, polish|Write your reflection, 1 paragraph "
     "minimum|Finalize your bounce|Create your Padlet post with 3 questions|Prepare to present",
     "Class 6. Steps 5, 6 and 7 of the project sheet, shortened to fit the slide. Mix and polish. Write your reflection and finalize "
     "your bounce. Create your own Padlet post with three questions for classmates and prepare to present. Remind students that my "
     "fourth struggle is thin reflections, so they use the prompts on the Reflection page. A reflection is a written or oral "
     "conversation about how they did and what they would do differently next time; my sheet asks for the written paragraph."),
    (6, "check", "What you turn in", "Genre Research Google Form|Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Genre "
     "Exploration|Written reflection on your class page|Padlet post with your 3 questions|Answer 2 questions on classmates’ posts",
     "The submission checklist from the project sheet, shortened to fit the slide. Show where students upload (your class page) and "
     "where the Padlet board is. Zip the .logicx in Finder (Control-click, Compress). The Google Form should already be complete from "
     "Classes 1 and 2; if it is not, this is the last chance."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play your track|Say which genre you chose and what defines it|Your Padlet post: 3 questions "
     "about your project|Answer at least 2 of each classmate’s 3",
     "Class 7, presentations with Padlet Q and A. Step 7 of the project sheet, shortened to fit the slide: create your own Padlet post "
     "with 3 questions you want classmates to answer, present to the class, and during classmates' presentations answer at least 2 of "
     "their 3 questions. The second line is the kit's own suggestion. No one plays a reference track; the project is the student's own."),
    (7, "closer", "One last thing…", "You left your comfort zone.|You studied the genre.|You made it sound right.|Now play it.",
     "Close with my closing note: students often surprise themselves by enjoying genres they thought they would hate. Ask a few "
     "students whether that happened to them. Reflection: point students to the Reflection page for the prompts; it follows my "
     "definition, a written or oral conversation about how they did and what they would do differently next time, and my sheet asks "
     "for the written paragraph. Tell them the next project starts from the menu."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("example", "Worked example", "an invented genre on paper"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 5, 8, 12, 17]
SHOTS3 = [("example", "Worked example"), ("research", "Research sheet"), ("listen", "Reference log"), ("sketch", "Loop sketch"),
          ("shortlist", "Genre shortlist"), ("proj2", "Steps"), ("setup", "Setup"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "changes", "logicref", "shortlist", "example",
        "research", "listen", "sketch", "workplan", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "example", "proj2", "rubric"]

COVER_A = "Try a genre you don't know"
COVER_C = "DMP2 · research · reference tracks · intro slides"
PDF_COVER = dict(a=30, b=50, c=14, art=7.3)
SQ_COVER = dict(a=44, b=140, c=27, art=740, gap=44)
SQ_B_LINES = ["Genre", "Exploration"]
SQ_SUB = "7 class periods · research · reference tracks · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Research sheet, reference log, loop sketch, worked example", 28)}
SQ_BANDS = {1: "Research <em>·</em> listen <em>·</em> sketch <em>·</em> compose <em>·</em> mix",
            2: "Hook <em>·</em> five steps <em>·</em> genre fingerprint <em>·</em> mix",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, video, songs, artists or genres are named or included. Students choose their own genre and their own reference "
             "tracks, and make every sound in their projects themselves. For the Class 1 hook, you only ask questions aloud.")
CREDITS = ["Worked example (an invented genre, three invented reference tracks and an arrangement described on paper), the vinyl, step, "
           "genre-fingerprint and arrangement-map drawings and layouts: original work, Hudson Beat.",
           "No audio, video, lyrics, album art, screenshots, presets, playlists, links or chart data are included. No student work is "
           "included. Padlet and the streaming services are named only as the owner’s own materials name them."]
LOGIC_INTRO = ("Where to find the tools a Genre Exploration project is likely to use. Demonstrate what your class needs on Classes 1 and 3 and "
               "then let students work. Names are from current Logic Pro versions; check the labels on yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add tracks with Track › New Tracks…: a Software Instrument track for MIDI "
              "sounds, an Audio track for recordings, a drum track for beats."),
             ("Set the tempo", "Click the tempo in the control bar and type the BPM you measured from your references. Tap Tempo "
              "(the tempo display’s menu) helps if you are not sure."),
             ("Bring in a reference", "Drag an audio file you own or have the right to use onto its own Audio track, name it “REF” and "
              "mute it when you are not comparing. Delete it before you bounce. Only your own track is handed in."),
             ("Loop and arrangement", "Build the 8–16 bar loop, then copy and paste regions to build sections. Name and color each "
              "section so the form is easy to see."),
             ("Software instruments", "Open the Library (Y) to browse sounds by category and try instruments until the sound fits "
              "the genre. Drum Kit Designer and Drum Machine Designer give genre-specific drum kits."),
             ("Mixer: volume and panning", "Press X to open the Mixer. Move each track’s fader for volume and its Pan knob to place it."),
             ("EQ and filters", "Add Channel EQ to a channel strip. A high-cut or low-cut filter changes how bright or heavy a part "
              "sounds; cut what you do not need before you boost anything."),
             ("Reverb and effects", "Insert Space Designer or ChromaVerb to give a part space; Delay and Compressor are also on the "
              "channel strip. Keep effects subtle until the rest of the mix is balanced."),
             ("Automation", "Press A to show automation, choose a parameter such as volume or a filter, and draw changes over time."),
             ("Save versions", "Use File › Save As… with a numbered name before each big change."),
             ("Bounce and zip", "File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and "
              "choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the Google Form, reflection, .mp3 or .wav and zipped .logicx submitted",
                 "Padlet post created with my 3 questions", "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my genre:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12.4pt;margin-bottom:3pt">Genres too close to home: the genre check on the Genre research sheet (page @RESEARCH) and your approval on Class 1.</li>'
    '<li style="font-size:12.4pt;margin-bottom:3pt">Shallow research: the Reference track log (page @LISTEN) asks for tempo, form in bars, instruments and production.</li>'
    '<li style="font-size:12.4pt;margin-bottom:3pt">Instruments right, production wrong: slides 8 and 9, and the Work plan’s mix-technique lines (page @WORKPLAN).</li>'
    '<li style="font-size:12.4pt;margin-bottom:0">Thin reflections: the Reflection prompts (page @REFLECT), with a thin and a useful example.</li></ul></div>'
    '<div class="box" style="margin-top:7pt"><span class="k">Where this kit helps with the variations (kit suggestion)</span><ul style="margin:0">'
    '<li style="font-size:12.4pt;margin-bottom:3pt">Easier: a blank Genre shortlist for your 5–8 genres, starter tracks and cheat sheets (page @SHORTLIST).</li>'
    '<li style="font-size:12.4pt;margin-bottom:0">More advanced: the worked example runs 2:36 in sections (page @EXAMPLE), and the Work plan has two lines for the mixing techniques.</li></ul></div>')
TN1_SIZE = 16.2
PROJ_SIZE = 14.9
VOCAB_GAP = 40
CHANGES_SIZE = 10.1
LOGIC_SIZE = 10.8
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example", "How to use, overview, setup, pacing, teacher notes, what changed, Logic quick "
              "reference, genre shortlist, worked example"),
             ("Student pages", "research", "reflect", "Genre research sheet, Reference track log, Loop and form sketch, Work plan, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection prompts"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period structured project for high school music '
             f'technology. Each student picks a genre they do not already make, researches what defines it, studies 2–3 reference '
             f'tracks, sketches a loop, composes a full track in that genre, mixes it to fit, reflects, and presents it with Padlet '
             f'questions for feedback. It is the project from my Digital Music Production 2 course (type: structured; focus: research '
             f'and style), and the projects in that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Set up your Genre Research Google Form, the Presentation Padlet and the submission spot (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("research")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Class 5 is a working day with no new slide. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}: a curated list of 5–8 genres (a blank for it is on page {D.IX("shortlist")}), or 2+ minutes with a full arrangement and 2 genre-specific mixing techniques.</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Any genre:</b> the pages never name one, so students and you fill in your own.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students study a '
             f'genre they do not know until they can make a track that sounds like it, and then say what they learned.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13.4pt;line-height:1.5">One finished track in a genre the student does not already make, following the '
             f'genre’s typical song form and conventions, with instruments, synths or samples that belong to it and genre-appropriate mixing '
             f'and production. They complete the Genre Research Google Form first, and hand in a bounced .mp3 or .wav, the zipped .logicx '
             f'project and a written reflection (one paragraph minimum), plus a Padlet post with three feedback questions, then present.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:13pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:12pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:13pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.6pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: research, sketch, three working days, mix and bounce, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: instruments, arrangement, mixing, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, the Genre Research Google Form, a way to stream reference tracks, a feedback board and a place to submit files</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:12pt">Students should already '
             f'know how to open a project, add and play instruments, build a loop, and save, bounce and zip in Logic. Nothing new '
             f'is taught: the quick reference (page {D.IX("logicref")}) shows where each tool lives.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Structured", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 12.2pt; line-height: 1.46; margin-bottom: 6pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the final listen.</li>'
             f'<li><b>The Genre Research Google Form.</b> It is your own form: share the link on your class page. It is not included.</li>'
             f'<li><b>A way to stream reference tracks</b> on student devices (my resource names Spotify, YouTube and Apple Music). The kit includes no track or link.</li>'
             f'<li><b>A place to submit</b> the bounce, the zipped .logicx and the written reflection (your class page).</li>'
             f'<li><b>The Presentation Padlet</b>, set up before Class 1 (yours to set up; none is included).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("research")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:12.2pt;margin-bottom:8pt") for c in [
                 "Share the Genre Research Google Form on your class page.",
                 "Set up the Presentation Padlet and, if you like, a shared class playlist (my resource).",
                 "Decide how students choose: free choice, or a short list from page @SHORTLIST (my Easier variation).",
                 "Check that a student computer opens Logic and plays back through headphones."]).replace("@SHORTLIST", str(D.IX("shortlist"))) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch (my closing note)", True)}'
             f'<p style="font-size:12pt">{TN_NOTE} Check in with students who expected to dislike their genre.</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Kit suggestions, not part of my sheets</span><ul style="margin:0">'
             f'<li style="font-size:11.6pt">Approve each genre on Class 1. If it is close to what the student already makes, ask what they would not normally reach for.</li>'
             f'<li style="font-size:11.6pt">While students work, ask: is that the instrument, or the production style? Which reference sounds most like yours?</li>'
             f'<li style="font-size:11.6pt">The Work plan (page {D.IX("workplan")}) shows time management in the students’ own words.</li></ul></div>'
             f'{D.H2("Music they did not make")}'
             f'<div class="box"><span class="k">A kit suggestion</span><p style="margin:0;font-size:11.4pt;line-height:1.42">'
             f'Reference tracks are for studying and comparing. Tell students to keep each reference on its own muted track in Logic, '
             f'delete it before they bounce, and hand in only their own track. No one else’s audio goes into the project they submit.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.4pt;line-height:1.42">'
             f'Tell students to start with the headphones low and to check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


def shortlist_page(n, wm=False):
    trs = "".join("<tr><td style='height:34pt'></td><td></td><td></td></tr>" for _ in range(8))
    inner = (f'<p style="margin:0 0 5pt;font-size:11.6pt">My Easier variation: provide a curated list of 5–8 genres with starter reference '
             f'tracks and cheat sheets. This page is a <b>blank for you to fill in</b>: this kit names no genre, artist or song, because my '
             f'sheets name none. Choose genres your students are unlikely to make already (my first struggle). Fill in 5–8 rows.</p>'
             f'{D.H2("Genre shortlist (kit template)", True)}'
             f'<table class="map"><tr><th style="width:24%">Genre</th><th style="width:38%">Starter reference tracks (title and artist)</th>'
             f'<th>Cheat sheet in a line (tempo, rhythm, sound, form, production)</th></tr>{trs}</table>'
             f'<div class="cols" style="margin-top:7pt;gap:12pt"><div class="box acc-b"><span class="k">A one-genre cheat sheet has five lines</span>'
             f'<ul style="margin:0"><li style="font-size:11pt;margin-bottom:2pt"><b>Tempo:</b> a range in beats per minute</li>'
             f'<li style="font-size:11pt;margin-bottom:2pt"><b>Rhythm:</b> the drum pattern and groove</li>'
             f'<li style="font-size:11pt;margin-bottom:2pt"><b>Sound:</b> instruments, synths and samples</li>'
             f'<li style="font-size:11pt;margin-bottom:2pt"><b>Form:</b> the usual sections and lengths in bars</li>'
             f'<li style="font-size:11pt;margin-bottom:0"><b>Production:</b> space, filters, loudness, what is quiet or bright</li></ul></div>'
             f'<div class="box"><span class="k">My Harder variation, laid out</span>'
             f'<ul style="margin:0"><li style="font-size:11pt;margin-bottom:2pt"><b>2+ minutes, full arrangement.</b> The worked example '
             f'(page {D.IX("example")}) is 2:36 in sections.</li>'
             f'<li style="font-size:11pt;margin-bottom:0"><b>2 genre-specific mixing techniques.</b> Students write them on the Work plan '
             f'(page {D.IX("workplan")}); the worked example shows two.</li></ul></div></div>'
             f'<div class="box acc-b" style="margin-top:7pt"><span class="k">How to use this page</span><p style="margin:0;font-size:11.4pt;line-height:1.45">'
             f'Write the list on the board or share it on your class page on Class 1, with starter tracks you have chosen. Genre Exploration '
             f'stays open: a student may pick a genre off the list if you approve it. The list and the tracks are yours; nothing here is '
             f'audio, and the kit does not suggest any.</p></div>')
    return D.page("Genre shortlist and my Harder variation", "TEACHER", "Easier + Harder", inner, n, key="shortlist")


def example_page(n, wm=False):
    gr = "".join(f"<tr><td style='width:25%'><b>{a}</b></td><td>{b}</td></tr>" for a, b in GENRE_ROWS)
    refs = "".join(f"<tr><td><b>{a}</b></td><td>{t}</td><td>{' + '.join(map(str, b))} = {sum(b)} bars</td><td>{c}</td></tr>" for a, t, b, c in REFS)
    tec = "".join(f"<tr><td style='width:27%'><b>{a}</b></td><td>{b}</td></tr>" for a, b in TECHNIQUES)
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10.6pt">An <b>invented genre, “{GENRE}”, with three invented reference tracks, described on '
             f'paper</b>: no audio is included and no real genre is named. Students’ projects will differ.</p>'
             f'<div class="cols" style="gap:10pt"><div>{D.H2("1 · A genre card", True)}<table class="t" style="font-size:9.4pt;line-height:1.25">{gr}</table></div>'
             f'<div>{D.H2("2 · Three reference tracks, broken down", True)}<table class="t" style="font-size:9pt;line-height:1.25">'
             f'<tr><th>Track</th><th>Tempo</th><th>Form</th><th>Notes</th></tr>{refs}</table>'
             f'<p style="font-size:9.4pt;line-height:1.3;margin:3pt 0 0">What they share: slow, spacious, the same section order, a short intro and a short bridge.</p></div></div>'
             f'{D.H2("3 · The arrangement map: 2:36")}<div style="width:6.1in;margin:1pt auto 3pt">{D.body_svg(plan_body(1250, "page arrange", 24, 20))}</div>'
             f'<div class="box acc-b"><span class="k">4 · Checking the numbers</span>'
             f'<p style="margin:0;font-size:9.8pt;line-height:1.32">{BPM} beats per minute is {60 / BPM:g} s a beat, so a bar of 4/4 is {BAR_S:g} s. '
             f'Sections: {" + ".join(str(b) for b in SECTION_BARS)} = {BARS} bars, and {BARS} × {BAR_S:g} s = {TOTAL_S} s = 2:36. '
             f'It follows the form the three references share, and each chorus brings back the lead.</p></div>'
             f'<div class="cols" style="gap:10pt;margin-top:3pt"><div class="box"><span class="k">5 · Instruments right, production wrong?</span>'
             f'<p style="margin:0 0 2pt;font-size:9.2pt;line-height:1.28"><b>Weak:</b> {WEAK}</p>'
             f'<p style="margin:0;font-size:9.2pt;line-height:1.28"><b>Strong:</b> {STRONG}</p></div>'
             f'<div><span class="k" style="font-size:9.4pt">6 · Two genre-specific mixing techniques (my Harder variation)</span>'
             f'<table class="t" style="font-size:9pt;line-height:1.25;margin-top:2pt">{tec}</table>'
             f'<p style="font-size:9pt;line-height:1.28;margin:3pt 0 0"><b>Three Padlet questions (invented):</b> {qs}</p></div></div>')
    return D.page("Worked example · an invented genre", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def research_page(n, wm=False):
    rows = [("Tempo", "range in BPM"), ("Rhythm", "drum pattern, groove, feel"), ("Instruments and sounds", "what plays, what is missing"),
            ("Song form", "sections and how long each lasts"), ("Production style", "space, filters, loudness, bright or dark")]
    trs = "".join(f"<tr><td style='height:41pt'><b>{a}</b><br><span style='font-size:8.6pt'>{b}</span></td><td></td><td></td></tr>"
                  for a, b in rows)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Step 1: select your genre and complete the Google Form analyzing its key '
             f'characteristics. This sheet is a <b>paper planning copy</b> for the same job. Your teacher’s Google Form is separate, and '
             f'you still complete it before composing.</p>'
             f'<div class="fl"><b>My genre:</b><span></span></div>'
             f'<div class="fl"><b>What I usually make:</b><span></span></div>'
             f'<div class="box acc-b" style="margin:3pt 0 4pt"><span class="k">Genre check (requirement 1)</span>'
             + D.chk("This genre is NOT one I am already comfortable producing in.", 12, "font-size:10.8pt;margin-bottom:2pt")
             + D.chk("My teacher has seen my genre.", 12, "font-size:10.8pt;margin-bottom:0") +
             f'</div>'
             f'<table class="map"><tr><th style="width:21%">What defines it</th><th style="width:40%">What I found (be specific)</th>'
             f'<th>Where I heard it (Reference A, B or C)</th></tr>{trs}</table>'
             f'<div class="fl" style="margin-top:6pt"><b>The sound I would miss most if it were gone:</b><span></span></div>'
             f'<div class="fl"><b>What I think will be hardest to copy:</b><span></span></div>'
             f'<div class="fl"><b>My Google Form is done:</b><span style="flex:0 0 0.9in"></span><b>Date:</b><span></span></div>')
    return D.page("Genre research sheet", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="research")


def listen_page(n, wm=False):
    rows = [("Title and artist", 33), ("Tempo (BPM) and feel", 33), ("Sections, each in bars", 48), ("Instruments and sounds I hear", 48),
            ("Production: space, filters, loudness", 48), ("One thing I will borrow", 38)]
    trs = "".join(f"<tr><td style='height:{h}pt'><b>{a}</b></td><td></td><td></td><td></td></tr>" for a, h in rows)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Step 2: study 2–3 reference tracks and break down their elements. A reference '
             f'track is a professionally produced song you study and use as a guide. Pick your own tracks and write what you hear. '
             f'Reference C is optional.</p>'
             f'<table class="map"><tr><th style="width:21%">What I notice</th><th>Reference A</th><th>Reference B</th><th>Reference C</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:7pt"><span class="k">What my references share</span>'
             f'<div class="fl" style="margin-top:3pt"><b>Tempo range:</b><span></span></div>'
             f'<div class="fl"><b>Form (sections in order):</b><span></span></div>'
             f'<div class="fl"><b>The sounds in all of them:</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>What is true of the production in all of them:</b><span></span></div></div>'
             f'<div class="box" style="margin-top:7pt"><span class="k">Compare in Logic (my second tip)</span>'
             + D.chk("I put a reference on its own track in Logic and compared it with my mix.", 12, "font-size:10.8pt;margin-bottom:2pt")
             + D.chk("I deleted the reference track before I bounced.", 12, "font-size:10.8pt;margin-bottom:0") + '</div>')
    return D.page("Reference track log", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="listen")


def sketch_page(n, wm=False):
    lanes = ["Drums", "Bass", "Chords / pads", "Lead", "FX / other"]
    head = "".join(f"<th style='font-size:8pt;padding:2pt'>{i}</th>" for i in range(1, 17))
    grid = "".join(f"<tr><td style='height:34pt;font-size:9.4pt'><b>{a}</b></td>" + "<td></td>" * 16 + "</tr>" for a in lanes)
    form = "".join("<td style='height:68pt;vertical-align:top;font-size:8.6pt'>Section:<br><br>Bars:</td>" for _ in range(8))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Step 3: build an 8–16 bar loop that captures the genre’s essence. Mark which '
             f'layers play in which bars. Step 4: develop the full song structure and follow the typical song form of your genre.</p>'
             f'{D.H2("The loop: one box per bar", True)}'
             f'<table class="map"><tr><th style="width:15%">Layer</th>{head}</tr>{grid}</table>'
             f'<div class="fl" style="margin-top:5pt"><b>Tempo (BPM):</b><span style="flex:0 0 0.9in"></span><b>Why this loop sounds like my genre:</b><span></span></div>'
             f'{D.H2("The full song form")}'
             f'<table class="map"><tr>{form}</tr></table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">How long will it be?</span>'
             f'<p style="margin:0 0 3pt;font-size:10.4pt">A bar of 4/4 lasts 240 ÷ BPM seconds. My Harder variation asks for 2+ minutes.</p>'
             f'<div class="fl" style="margin:0"><b>Total bars</b><span style="flex:0 0 0.6in"></span><b>× seconds per bar</b><span style="flex:0 0 0.6in"></span>'
             f'<b>= seconds</b><span style="flex:0 0 0.7in"></span><b>= minutes</b><span></span></div></div>'
             f'<div class="fl" style="margin-top:6pt"><b>My form matches the references because:</b><span></span></div>'
             f'{D.H2("Notes to myself")}{D.lines(4, 25)}')
    return D.page("Loop and form sketch", "STUDENT", "Classes 2–3", inner, n, wm, name=True, key="sketch")


def workplan_page(n, wm=False):
    rows = [("Class 1", "Genre selected; Google Form begun"), ("Class 2", "Research done; loop started"), ("Class 3", ""), ("Class 4", ""),
            ("Class 5", ""), ("Class 6", "Final mix, bounce, reflection"), ("Class 7", "Present; answer 2 questions")]
    trs = "".join(f"<tr><td style='height:42pt'><b>{a}</b></td><td style='font-size:8.8pt'>{b}</td><td></td><td></td></tr>" for a, b in rows)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Steps 4 and 5: develop the full song structure, layer instrumentation and refine, '
             f'then apply genre-appropriate mixing. Before each class write what you plan to finish; after it, what you actually did.</p>'
             f'<table class="map"><tr><th style="width:11%">Class</th><th style="width:22%">Fixed by the schedule</th>'
             f'<th style="width:34%">What I plan to finish</th><th>What I actually finished</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:7pt"><span class="k">Instruments are not enough: production check</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Instruments and sounds I used that belong to the genre:</b><span></span></div>'
             f'<div class="fl"><b>How my references are mixed (space, filters, loudness):</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>Where my mix is different from them:</b><span></span></div></div>'
             f'<div class="box" style="margin-top:7pt"><span class="k">Two genre-specific mixing techniques (my Harder variation)</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>1.</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>2.</b><span></span></div></div>'
             f'<div class="fl" style="margin-top:7pt"><b>I will start my final mix in Class</b><span style="flex:0 0 0.6in"></span><b>because</b><span></span></div>'
             f'<div class="fl"><b>The part of my track I am proudest of so far:</b><span></span></div>'
             f'<div class="fl"><b>The part that is not working yet:</b><span></span></div>')
    return D.page("Work plan", "STUDENT", "Classes 3–5", inner, n, wm, name=True, key="workplan")


def reflect_page(n, wm=False):
    prompts = D.REFLECT_PROMPTS + [("What did you learn about the genre?", "Say what surprised you, and whether your opinion of it changed.")]
    pr = "".join(
        f'<div style="flex:1;display:flex;flex-direction:column;min-height:0;margin-bottom:4pt"><p style="margin:0 0 1pt;font-size:10.8pt">'
        f'<b style="font-family:Oswald;font-size:12pt;color:{ACCENT}">{i}</b>&nbsp; <b>{D.fill(a)}</b> {D.fill(b)}</p>'
        f'<div class="lines" style="min-height:34pt"></div></div>' for i, (a, b) in enumerate(prompts, start=1))
    inner = (f'<div class="box acc-b"><span class="k">What this page is</span><p style="margin:0;font-size:10.8pt;line-height:1.38">My sheet asks '
             f'for a short written reflection, 1 paragraph minimum, on what you learned. A reflection is {D.REFLECT_DEFINITION}. '
             f'Answer the prompts below, then write your paragraph on your class page. Your teacher may take it orally instead.</p></div>'
             f'<div class="cols" style="gap:10pt;margin:5pt 0 4pt"><div class="box"><span class="k">Thin (an invented example)</span>'
             f'<p style="margin:0;font-size:9.4pt;line-height:1.3">{THIN}</p></div>'
             f'<div class="box"><span class="k">Useful (an invented example)</span><p style="margin:0;font-size:8.8pt;line-height:1.28">{USEFUL}</p></div></div>'
             f'{pr}')
    return D.page("Reflection · what did you learn?", "STUDENT", "Class 6", inner, n, wm, name=True, key="reflect")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "shortlist": shortlist_page, "example": example_page,
         "research": research_page, "listen": listen_page, "sketch": sketch_page, "workplan": workplan_page, "reflect": reflect_page}


# ================================================================ content checks (example arithmetic, owner text, no audio)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 4), reqs=(REQS, 6), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 7),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 3))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp} (the owner's count)")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is the owner's /25, levels 1-5")
    if [c for c, _ in RUBRIC] != ["Creativity & Originality", "Technical Skill / DAW Use", "Composition & Structure",
                                  "Sound Design & Mix Quality", "Documentation & Presentation"]:
        errs.append("rubric categories must be the owner's, in order")
    if FILE_NAME not in CHECK[3] or "Genre Exploration" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    if "NOT already comfortable" not in REQS[0] or "1 paragraph minimum" not in REQS[5]:
        errs.append("requirements 1 and 6 as the owner wrote them")
    if REFLECTION:
        errs.append("REFLECTION must be False: the owner's sheet already asks for a written reflection")
    # the worked example adds up
    if BAR_S != 3 or BARS * BAR_S != TOTAL_S or sum(SECTION_BARS) != BARS:
        errs.append("80 BPM: 3 s per bar, 52 bars, 156 s")
    if TOTAL_S < 120:
        errs.append("example is 2+ minutes (my Harder variation's minimum)")
    if SECTIONS[0][1] != 0 or SECTIONS[-1][2] != TOTAL_S or any(b != c for (_, _, b), (_, c, _) in zip(SECTIONS, SECTIONS[1:])):
        errs.append("sections must tile the piece")
    if [round((b - a) / BAR_S) for _, a, b in SECTIONS] != SECTION_BARS:
        errs.append("section lengths must match their bars")
    if any(not 0 <= a < b <= TOTAL_S for sp in SPANS.values() for a, b in sp) or any(not 0 <= a < b <= TOTAL_S for a, b in RISERS):
        errs.append("layer spans and risers inside the piece")
    for lane in ("Drums", "Bass", "Pads"):
        if not any(a <= 36 and b >= 60 for a, b in SPANS[lane]):
            errs.append(f"{lane} must play through the first chorus")
    if len(REFS) != 3 or any(not 3 <= len(b) for _, _, b, _ in REFS):
        errs.append("three reference tracks, each with sections in bars")
    if len(TECHNIQUES) != 2:
        errs.append("two genre-specific mixing techniques")
    if len(QUESTIONS) != 3:
        errs.append("three Padlet questions")
    if len(GENRE_ROWS) != 5:
        errs.append("genre card: five lines")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    txt = " ".join(flat)
    for need in ("No audio, video, songs,", "invented genre, “Harbor Drift”",
                 "Your Name – Genre Exploration", "Final Grade = Average of Student + Teacher", "No student work is included",
                 "paper planning copy"):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up:
        errs.append("UPLOAD.md: must say no audio is included and record the open questions")
    for i in (2, 5, 6, 8, 9, 10, 12, 13, 14, 15, 17):   # slides that shorten the owner's wording must say so
        if "shortened" not in notes[i].lower() and "shortens" not in notes[i].lower():
            errs.append(f"deck slide {i + 1} notes: must say the owner's wording is shortened")
    ch = flat[D.IX("changes") - 1]
    for s in ("slide 3", "slide 6", "slides 7 and 10", "slide 9", "slide 11", "slide 13", "slide 14", "slide 15", "slide 16", "slide 18"):
        if s not in ch:
            errs.append(f"'What changed' page must list {s}")
    if "Reflection page, not a new task" not in ch:
        errs.append("'What changed' page must explain the Reflection page")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or any("Work plan" in g or "Reflection" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in ("Billie", "Beatles", "Daft", "Skrillex", "Disney", "Minecraft", "Mario", "Taylor", "Nirvana", "Radiohead",
                   "hip-hop", "hip hop", "jazz", "house music", "EDM", "lo-fi", "Lo-fi",
                   "Cage", "Billboard"):
        if banned in alldeck or banned in txt:
            errs.append(f"must not name genres, songs, artists or services beyond the owner's ({banned})")
    return errs


def check_summary():
    return (f"The invented genre piece is {TOTAL_S} s ({BPM} BPM, {BARS} bars of {BAR_S:g} s; sections {'+'.join(map(str, SECTION_BARS))} bars) "
            f"with three invented references; "
            f"the owner's lists counted (4 goals, 4 terms, 6 requirements, 7 steps, 4 tips, 7 checklist items, 4 struggles, 3 resources); "
            f"{len(CHANGES)} wording changes disclosed; no audio, genre names or student work included; grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
