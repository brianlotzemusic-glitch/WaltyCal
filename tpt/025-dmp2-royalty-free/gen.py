#!/usr/bin/env python3
"""DMP2 project: Royalty Free (TpT 025): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Royalty Free > "Royalty Free - Project Sheet & Rubric" (rubric 5 categories scored 1-5, /25, final
grade = average of student and teacher scores), TEACHER NOTES > "Royalty Free - Teacher Notes" (7 class periods), and the project's
entry on "DMP2 - Project Menu" (the June 2026 menu; owner, 17 Oct 2026: the June entry may be quoted). These three set the project
text, steps, rubric and pacing (owner rule, 17 Oct 2026).
Supporting artifacts (owner rule, 17 Oct 2026: may be taken from the other DMP2 folders): the 160-word "Royalty Free - Groups of Words"
sheet from the older Projects > Royalty Free folder is the "provided list" of descriptive words (printed A to Z as a student page, no
word added or removed); the older "Royalty-Free Music Sources & What to Dissect" doc is NOT included, because it names real tracks,
artists and links, but its six "What to Dissect" lenses are the headings of the Listening log. The 2025 Project Outline and the owner's
older folders of student mp3s and zips are not sources (student work is never used).

NO AUDIO IS INCLUDED. The Easier variation's "structural template" and the Harder variation's "real video clip" are laid out on paper
(page "vary"); no video is included. The worked example is an invented one-minute piece ("Open Doors", 120 BPM, 30 bars, three words
Bright / Steady / Uplifting from the owner's list) for an invented video, described on paper: four sections, seven layers, two of them
Apple Loops that the student rearranges, a chord for every bar, and four automation lanes. Every picture (word-to-sound hero, cards,
brief map, build-peak-resolve arc, arrangement map) is drawn in code.
The sheet already asks for a reflection paragraph (requirement 6, step 5, checklist), so the shared Reflection element is switched off
(REFLECTION = False) and the kit's own "reflect" page is the planner the owner's fourth struggle asks for (as in tpt/022).
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "royalty-free"
TITLE = "Royalty Free"
ACCENT = "#9B4DA6"          # this product's single accent: orchid (008 red ... 023 horizon orange, 024 step-light magenta)
ACC_LIGHT = "#EBD6EF"
PRICE = "10.00"
CLASSES = 7
REFLECTION = False          # the owner's sheet already requires a reflection paragraph; this kit adds only a planner page (key "reflect")
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-024).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "Royalty Free in Logic Pro | Compose to a Creative Brief | High School"
DESC_START = "Functional composition project for high school:"
DESC_MUST = ["Royalty Free", "descriptive words", "no audio", "Padlet"]
ZIP_DIR = "Royalty Free - Hudson Beat"
ZIP_DATE = (2026, 10, 20, 12, 0, 0)
TYPE = "Structured Project"
PROJ_LINE = "Digital Music Production | <i>Structured Project</i> | 7 class periods"
DECK_STRAP = "Music with a job to do"
BANNED_EXTRA = []

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Structured", "Functional Composition"
MENU_DESC = "Create a 1-minute piece for media use, guided by 3 descriptive words. Compose for a purpose, not just yourself."
OVERVIEW = ("You’re composing music for the real world. Create a 1-minute piece of royalty-free music that could score a video for the "
            "school district — anything from sports highlights to facilities tours. Your sound and mood will be guided by 3 descriptive "
            "words you choose from a provided list.")
GOALS = ["Compose music driven by descriptive keywords rather than personal preference",
         "Understand what makes music functional for media use",
         "Practice efficient composition within a defined length and mood",
         "Develop skills in matching musical choices to a visual or emotional context"]
VOCAB = [("Royalty-Free", "Music that can be used without paying ongoing fees — no copyrighted samples"),
         ("Descriptive Words", "Adjectives that define the mood and character of a piece (e.g., “upbeat,” “cinematic”)"),
         ("Scoring", "Writing music specifically designed to accompany visual media"),
         ("Apple Loops", "Pre-made loops in Logic — allowed here, but arrangement must be your own")]
REQS = ["Length: 1 minute (give or take a few seconds)",
        "Choose 3 descriptive words from the provided list",
        "Your music must be royalty-free — no copyrighted samples. Apple Loops allowed but arrangement must be original.",
        "Use layers appropriate to the style",
        "Apply EQ and plug-ins to shape your mix",
        "Write a short paragraph explaining how your song reflects your 3 chosen words"]
STEPS = ["<b>Choose your words</b> — Review the word list and pick 3 that define your track’s mood (Word list: page @WORDS)",
         "<b>Plan</b> — Brainstorm how instruments, rhythm, and melody bring those words to life (Creative brief: page @BRIEF; Listening log: page @LISTEN)",
         "<b>Compose</b> — Build your 1-minute piece in Logic (Arrangement plan: page @ARRANGE)",
         "<b>Mix</b> — EQ, pan, and balance your tracks (Layers and mix sheet: page @MIX)",
         "Write your reflection paragraph explaining your creative choices (Reflection page: page @REFLECT)",
         "<b>Finalize</b> — Bounce your track with the correct file name format",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["Think about where this music would actually be used. Keep that context in mind.",
        "1 minute goes fast. Don’t cram too many ideas in — pick a vibe and commit.",
        "Your 3 words are your creative brief. Every choice should connect back to them.",
        "Listen to royalty-free music on YouTube or a free music library for inspiration."]
FILE_NAME = "“Your Name – Royalty Free – Word, Word, Word”"
CHECK = ["Bounced .mp3 or .wav uploaded to your class page",
         "Zipped .logicx project file uploaded to your class page",
         f"Files named correctly: {FILE_NAME}",
         "Reflection paragraph submitted via your class page",
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
TN_REINFORCES = ("Teaches functional composition — making music for a purpose beyond personal expression. Students learn to work from a "
                 "creative brief.")
STRUGGLES = ["Students ignore their 3 words and just make what they want.",
             "Tracks feel incomplete at 1 minute. Encourage a simple arc: build, peak, resolve.",
             "Over-reliance on Apple Loops with minimal original arrangement.",
             "Reflection paragraph is an afterthought."]
VAR_EASY = "Reduce to 2 descriptive words and provide a structural template."
VAR_HARD = "Require students to score their track to an actual video clip."
RESOURCES = [("Descriptive word list (on your class page)",
              "Kept as your own list, which is yours to post. The kit prints the same words as a student page, the Word list "
              "(page @WORDS), so students can circle theirs on paper."),
             ("Royalty-Free Music Sources doc",
              "Kept as I wrote it, but it is not included: it names real tracks, artists and links. The Listening log (page @LISTEN) "
              "uses its six “What to Dissect” lenses with no track named, so students study a piece they choose."),
             ("Examples of royalty-free music in real corporate/school videos",
              "Kept as I wrote it. Nothing is included: the examples are yours to choose and play. The Listening log (page @LISTEN) "
              "is where students write what they hear in them.")]
TN_NOTE = "Pairs well with real district videos. Students love knowing their music might actually get used."
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Creativity &amp; Originality: ask how the three words shaped the choices, then listen for what is the student’s own. "
                "Apple Loops are allowed; a loop left untouched is the default in the 1 column.",
                "Technical Skill: open the project. Which layers are the student’s own and which are loops (Layers and mix, page @MIX)? "
                "Are EQ and plug-ins really in use?",
                "Composition &amp; Structure: compare the piece with the Arrangement plan (page @ARRANGE). Is there a build, a peak and "
                "a resolve (my second struggle), or one long loop?",
                "Sound Design &amp; Mix Quality: close your eyes and listen for each of the three words. Is every layer audible, and "
                "does the mix still carry the words?",
                "Documentation &amp; Presentation: the Creative brief (page @BRIEF), the reflection paragraph (page @REFLECT) and the "
                "Padlet questions are the evidence."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Introduction and word list. Choose 3 words, brainstorm, begin composing.",
     "do": "Slides 1–7: hook, what the project is, the five steps, four words to know, steps 1 and 2. Hand out the project sheet, the Word "
           "list and the Creative brief. Check that each student has 3 words before they leave.", "slides": (1, 7),
     "pages": ["words", "brief", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Music with a job · five steps · four words · choose and plan"},
    {"n": 2, "owner": "<b>Classes 2–4:</b> Working days — compose and refine your 1-minute piece.",
     "do": "Slides 8–9: words become sound, and your 3 words are your brief. Hand out the Listening log. Then work time.",
     "slides": (8, 9), "pages": ["listen"], "deck": "Working day: words become sound, the brief"},
    {"n": 3, "owner": None, "do": "Slides 10–12: step 3, build-peak-resolve and the worked example on paper. Hand out the Arrangement plan "
     "and the Layers and mix sheet. Then work time.", "slides": (10, 12), "pages": ["arrange", "mix"],
     "deck": "Working day: compose, build-peak-resolve, worked example"},
    {"n": 4, "owner": None, "do": "Slide 13: one minute goes fast. Then work time. Ask each student to play their first 20 seconds and say "
     "which word they hear.", "slides": (13, 13), "pages": [], "deck": "Working day: pick a vibe and commit"},
    {"n": 5, "owner": "<b>Class 5:</b> Mix and finalize. Write reflection paragraph.",
     "do": "Slides 14–15: step 4, mix, and steps 5 and 6, the reflection paragraph and the bounce. Students plan their paragraph on "
           "the Reflection page (page @REFLECT).", "slides": (14, 15), "pages": ["reflect"],
     "deck": "Mix · reflection paragraph · bounce"},
    {"n": 6, "owner": "<b>Class 6:</b> Final bounce. Prepare presentations.",
     "do": "Slides 16–17: what to turn in and the rubric. Students bounce, name their files and post their three Padlet questions.",
     "slides": (16, 17), "pages": ["rubric", "present"], "deck": "Checklist · rubric"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 18–19: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (18, 19), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:9.4pt">Ask each student to name where their music could be used (my first tip) and to write three '
    'words on the Creative brief before they leave. If a word is only what they like, ask: how would you play that word to someone who had never heard it?</p></div>'
    '<div class="box"><span class="k">Classes 2–4</span><p style="margin:0;font-size:9.4pt">Working days; Class 4 has one slide. '
    'Circulate with one question: which of your three words is this layer for?</p></div></div>')
PACING_SIZE = 9.6

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (the word list resource and checklist items 1, 2 and 4).",
    "Page numbers are added to steps 1 to 5 (the Word list, Creative brief, Listening log, Arrangement plan, Layers and mix sheet and "
    "Reflection page).",
    "Tip 4 is written “on YouTube or a free music library” where I named a website, because that site is a third-party name. No site, "
    "track, artist or link is included anywhere in the kit.",
    "The Word list (page @WORDS) is my “Groups of Words” sheet from the older Royalty Free folder, printed A to Z with a circle by each "
    "of its 160 words. No word is added or removed, and spellings are kept (both Mesmerizing and Mesmerising).",
    "My Royalty-Free Music Sources doc is not included, because it names real tracks, artists and links. The Listening log (page @LISTEN) "
    "uses its six “What to Dissect” lenses. My third resource, examples of royalty-free music in real videos, is yours to choose.",
    "My Easier variation (2 words and a structural template) is laid out on page @VARY with a structural template that is the kit’s "
    "own (intro, build, peak, resolve). My Harder variation (score to an actual video clip) is laid out as a hit-point sheet on the same "
    "page; no video is included.",
    "My pacing guide’s “Classes 2–4” row spans the Class 2, 3 and 4 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "<b>Reflection page, not a new task (page @REFLECT).</b> My sheet already asks for a reflection paragraph (requirement 6, step 5, "
    "checklist), so this kit adds no extra task. It adds a planner only, because my fourth struggle says the paragraph is an "
    "afterthought, plus two looking-back prompts that follow my definition (a written or oral conversation about how the student did "
    "and what they would do differently), so you may take those orally. No points, no rubric row.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 3 shortens my overview and goals, slide 6 shortens "
    "my four vocabulary definitions, slide 7 shortens steps 1 and 2, slide 9 shortens tip 3 and my first struggle, slide 10 shortens "
    "step 3 and requirements 3 and 4, slide 13 shortens tip 2 and my second struggle, slide 14 shortens step 4 and requirement 5, "
    "slide 15 shortens steps 5 and 6, slide 16 shortens the submission checklist, and slide 18 shortens step 7.",
]
CHANGES_MUST_MENTION = ["your class page", "Page numbers", "third-party", "A to Z", "not included", "Classes 2–4", "Layout only",
                        "Reflection page", "intro deck shortens"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the overview, goals, four vocabulary terms, six requirements, "
        "steps (apart from the page numbers), tips (apart from tip 4), checklist (apart from the class page) and file name (“Your "
        "Name – Royalty Free – Word, Word, Word”), the /25 rubric, what the project reinforces, my four struggles, the variations, my "
        "three resources, my pacing, my closing note and the project menu entry on page @OVERVIEW. No rubric row is added and the "
        "requirements are unchanged.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: the how-to, overview and setup pages, the teacher "
                "moves in the pacing guide, the grading suggestions, the Logic quick reference, the structural template and hit-point "
                "sheet, the worked example (an invented one-minute piece for an invented video, with its chords, sections, layers and "
                "lanes, on paper, not audio), the Creative brief, Listening log, Arrangement plan, Layers and mix sheet and Reflection "
                "planner, the vocabulary and presentation pages and the intro deck. None adds a requirement or a rubric row.")

# ================================================================ the Word list (the owner's "Groups of Words" sheet: 16 columns x 10 words)
_COLS = [
    "Grandiose Classical Light Computerised Exciting Moody Rhythmic Groundbreaking Life-changing Talented",
    "Rich Ethereal Restoring Eclectic Uplifting Dramatic Powerful Symphonic Saturated Sad",
    "Passionate Pop Visionary Biphonic New_Age Progressive_Rock Melodious Sonic Heterophonic Beautiful",
    "Mesmerizing Haunting Natural Warm Sublime Loud Sentimental Simple Exhilarating Melancholic",
    "Enchanting Synthetic Lyrical Jazz Happy Complex Romantic Choral Melancholy Tempo",
    "Riveting Soothing Epic Harmonic Contemporary Harmonious Indulgent Hip-Hop Inciting Cultural",
    "Vibrant Rejuvenating Melodic Soft Latin Expressive Breathy Indie Emotional Magical",
    "Distinct Extravagant Enthusiastic Orchestral Relaxing Vocal Soulful Fluid Gradual Calming",
    "Feel-good Thrilling Mythical Ceremonial Bright Ballad Country Stylized Fresh Hypnotic",
    "Heartfelt Breathtaking Mesmerising Poignant Alternative Refined Mellow Flat Joyful Motivational",
    "Dainty Staccato Motivating Stratospheric Musical Catchy Harmonised Blues Nostalgic Groovy",
    "Fortissimo Frantic Radical Energetic Hardcore Rap Intense Polyphonic Bluesy Folk",
    "Electric Bluegrass Opera Invigorating Funky Tranquil Glorious Diminishing Faint Jazzy",
    "Sophisticated Empowering Slow Electronic Inspirational Baroque Drab Upbeat Healing Enigmatic",
    "Dynamic Soaring Inspiring Poetic Monophonic Shrill Ambient Acoustic Depressing Instrumental",
    "Gentle Classic Majestic Sombre Steady Transcendent Smooth Bittersweet Wonderous Adventure",
]
# two entries of the sheet are two words ("New Age", "Progressive Rock"); they are written with "_" in the lines above
WORDS = [[w.replace("_", " ") for w in c.split()] for c in _COLS]       # 16 groups of 10, as on the owner's sheet
WORDS_ALPHA = sorted((w for c in WORDS for w in c), key=lambda s: s.lower())


# ================================================================ the worked example (Hudson Beat original: an invented piece on paper)
PIECE = "Open Doors"
VIDEO = "a one-minute tour of a renovated school library (an invented video)"
WORDS3 = ["Bright", "Steady", "Uplifting"]
BPM = 120
BAR_S = 240 / BPM            # one 4/4 bar in seconds: 2
TOTAL_BARS = 30
TOTAL_S = 60
SECTIONS = [("Intro", 0, 8), ("Build", 8, 24), ("Peak", 24, 44), ("Resolve", 44, 60)]
# layer, start s, end s, how it is made, source ("own" / "loop")
LAYERS = [("Pad", 0, 60, "a soft synth pad I play and shape myself", "own"),
          ("Plucked keys", 0, 56, "a plucked keyboard I play, one chord per two bars", "own"),
          ("Drums", 8, 52, "an Apple Loop drum groove; I cut it, drop the hi-hat in the Build and write my own fill at bar 12", "loop"),
          ("Bass", 8, 56, "root notes I write on a bass instrument", "own"),
          ("Riser", 20, 24, "a filter sweep I automate on a synth, bars 11–12", "own"),
          ("Shaker", 24, 44, "an Apple Loop shaker, chopped so it only plays in the Peak", "loop"),
          ("Bell melody", 24, 48, "a bell melody I write, four notes a bar, all chord tones", "own")]
AUTO = [("Pad", "filter cutoff", [(0, .2), (24, .5), (44, .9), (56, .25)]),
        ("Plucked keys", "pan", [(0, .5), (12, .25), (32, .8), (56, .5)]),
        ("Drums", "volume", [(8, .3), (24, .9), (44, .9), (52, .2)]),
        ("Bell melody", "reverb send", [(24, .2), (36, .45), (48, .9)])]
# chords: name, first bar, last bar (every bar has one); the pitch letters each chord holds
CHORD_NOTES = {"C": {"C", "E", "G"}, "G": {"G", "B", "D"}, "Am": {"A", "C", "E"}, "F": {"F", "A", "C"}}
CHORDS = [("C", 1, 2), ("G", 3, 4), ("Am", 5, 6), ("F", 7, 8), ("C", 9, 10), ("G", 11, 12), ("C", 13, 14), ("G", 15, 16), ("Am", 17, 18),
          ("F", 19, 20), ("G", 21, 22), ("F", 23, 24), ("G", 25, 26), ("C", 27, 30)]
BASS_ROOT = {"C": "C2", "G": "G1", "Am": "A1", "F": "F1"}
BELL = {"C": ["E5", "G5", "C6", "G5"], "G": ["D5", "G5", "B5", "G5"], "Am": ["C5", "E5", "A5", "E5"], "F": ["C5", "F5", "A5", "F5"]}
BRIEF_ROWS = ["Sounds", "Rhythm", "Harmony", "Mix"]
BRIEF = {"Bright": ["bells · plucked keys", "light, clear hits", "major key (C)", "highs lifted"],
         "Steady": ["soft pad · bass", "kick on every beat", "one chord per 2 bars", "nothing jumps out"],
         "Uplifting": ["bell melody climbs", "drums enter in the Build", "ends on home chord C", "opens up in the Peak"]}
WEAK = "I will make a happy song with a nice beat."
STRONG = (f"My video is {VIDEO}. My three words are Bright, Steady and Uplifting. Bright: bells and plucked keys in a major key, with "
          "the highs lifted a little. Steady: 120 BPM that never changes, a kick on every beat and one chord for every two bars. "
          "Uplifting: a bell melody that climbs, a new layer every few bars, and an ending that lands on the home chord. It is 30 bars, "
          "60 seconds, in four sections: intro, build, peak and resolve. Two layers are Apple Loops that I cut and rearrange.")
SECTION_NOTES = [("Intro", "bars 1–4", "pad and plucked keys alone; C then G, two bars each"),
                 ("Build", "bars 5–12", "bass and drums enter at bar 5; a riser sweeps up in bars 11–12"),
                 ("Peak", "bars 13–22", "shaker and bell melody join at bar 13; the drums and pad are at their loudest"),
                 ("Resolve", "bars 23–30", "layers leave one by one; the last four bars are C, with the pad alone at the end")]
THIN = ("My song is bright and steady and uplifting. I used bells and drums and it is happy. I think it sounds good and fits my words. "
        "I liked making it.")
USEFUL = ("Bright is the bell melody and the plucked keys in C major, with the highs lifted in the mix. Steady is the 120 BPM pulse "
          "with the kick on every beat; I did not change tempo once. Uplifting is the climb: a new layer arrives about every four bars, "
          "the bell melody rises to its highest note in the Peak, and the last chord settles on C. Next time I would try a quieter intro.")
QUESTIONS = ["Which of the three words did you hear first?",
             "Where did the music feel like it was building, and where did it peak?",
             "What would you change so it fits the video even better?"]


def mmss(t):
    return f"{int(t) // 60}:{int(round(t)) % 60:02d}"


def bars_for(sec, bpm):
    return sec * bpm / 240


def density(bar):
    """How many layers play at the start of this bar."""
    t = (bar - 1) * BAR_S
    return sum(1 for _n, a, b, _d, _s in LAYERS if a <= t < b)


DENS = [density(b) for b in range(1, TOTAL_BARS + 1)]


# ================================================================ drawings (original, code-drawn: black + accent only)
def hero_body():
    W, H = 1100, 470
    out = []
    pw, gap, x0 = 300, 40, 60
    for i, w in enumerate(WORDS3):
        x = x0 + i * (pw + gap)
        out.append(f'<rect x="{x}" y="6" width="{pw}" height="78" rx="39" fill="{ACCENT if i != 1 else "#000"}"/>')
        out.append(D.t_(x + pw / 2, 6 + 39 + 14, w.upper(), 40, 700, fill_="#fff"))
        D.lab("hero words", w.upper(), 40, pw - 50)
        cx = x + pw / 2
        out.append(f'<line x1="{cx}" y1="92" x2="{cx}" y2="150" stroke="#000" stroke-width="5" stroke-dasharray="3 10" stroke-linecap="round"/>')
        out.append(f'<polygon points="{cx - 16},146 {cx + 16},146 {cx},176" fill="#000"/>')
    bx, bw = 60, 980
    by, bh = 190, 200
    out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="16" fill="#fff" stroke="#000" stroke-width="4"/>')
    cw = (bw - 40) / TOTAL_BARS
    top = max(DENS)
    for i, d in enumerate(DENS):
        peak = d == top
        h_ = d / top * (bh - 50)
        out.append(f'<rect x="{bx + 20 + i * cw + 2:.1f}" y="{by + bh - 16 - h_:.1f}" width="{cw - 4:.1f}" height="{h_:.1f}" rx="4" fill="{ACCENT if peak else "#000"}"/>')
    out.append(D.t_(bx, by + bh + 52, "0:00", 28, 500, anchor="start"))
    out.append(D.t_(bx + bw, by + bh + 52, "1:00", 28, 500, anchor="end"))
    out.append(D.t_(bx + bw / 2, by + bh + 52, "ONE MINUTE · BUILD · PEAK · RESOLVE", 28, 700))
    D.lab("hero cap", "ONE MINUTE · BUILD · PEAK · RESOLVE", 28, 600)
    return "".join(out), W, by + bh + 66


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
    return cards_body([("Choose", "3 words"), ("Plan", "the brief"), ("Compose", "1 minute"), ("Mix", "EQ · pan · balance"),
                       ("Reflect", "a paragraph")],
                      "Then finalize: bounce, present and get feedback", W, name, fs, cs, True)


def brief_body(W=1600, name="brief pic", fs=34, cs=24):
    """Three words -> four kinds of musical choice (the worked example's brief)."""
    lx = 190
    gap = 22
    cw = (W - lx - 2 * gap - 4) / 3
    out = []
    for i, w in enumerate(WORDS3):
        x = lx + i * (cw + gap)
        out.append(f'<rect x="{x:.1f}" y="4" width="{cw:.1f}" height="70" rx="35" fill="{ACCENT if i != 1 else "#000"}"/>')
        out.append(D.t_(x + cw / 2, 4 + 35 + fs * .34, w.upper(), fs, 700, fill_="#fff"))
        D.lab(name + " words", w.upper(), fs, cw - 40)
    rh, rg = 84, 14
    for r, row in enumerate(BRIEF_ROWS):
        y = 92 + r * (rh + rg)
        out.append(D.t_(lx - 16, y + rh / 2 + cs * .34, row.upper(), cs, 700, anchor="end"))
        D.lab(name + " rows", row.upper(), cs, lx - 26)
        for i, w in enumerate(WORDS3):
            x = lx + i * (cw + gap)
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{rh}" rx="12" fill="{ACC_LIGHT if i != 1 else "#fff"}" stroke="#000" stroke-width="3"/>')
            txt = BRIEF[w][r]
            out.append(D.t_(x + cw / 2, y + rh / 2 + cs * .34, txt, cs, 500))
            D.lab(name + " cells", txt, cs, cw - 30)
    hh = 92 + len(BRIEF_ROWS) * (rh + rg)
    cap = "Every choice connects back to a word"
    out.append(D.t_(W / 2, hh + 20, cap, cs + 2, 500))
    D.lab(name + " cap", cap, cs + 2, W - 20)
    return "".join(out), W, hh + 36


def arc_body(W=1600, name="arc pic", fs=26, cs=22):
    """Layers playing in each of the example's 30 bars: build, peak, resolve."""
    lx = 8
    pw = W - 2 * lx
    cw = pw / TOTAL_BARS
    top = max(DENS)
    bh = 300
    y0 = 78
    out = []
    shade = {"Intro": "#4a4a4a", "Build": "#000", "Peak": ACCENT, "Resolve": "#4a4a4a"}
    for nm, a, b in SECTIONS:
        xa, xb = lx + a / BAR_S * cw, lx + b / BAR_S * cw
        out.append(f'<rect x="{xa + 2:.1f}" y="2" width="{xb - xa - 4:.1f}" height="52" rx="8" fill="{shade[nm]}"/>')
        out.append(D.t_((xa + xb) / 2, 2 + 26 + fs * .32, nm.upper(), fs, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs, xb - xa - 12)
    out.append(f'<line x1="{lx}" y1="{y0 + bh}" x2="{lx + pw}" y2="{y0 + bh}" stroke="#000" stroke-width="5" stroke-linecap="round"/>')
    for i, d in enumerate(DENS):
        sec = next(nm for nm, a, b in SECTIONS if a <= i * BAR_S < b)
        h_ = d / top * (bh - 20)
        out.append(f'<rect x="{lx + i * cw + 3:.1f}" y="{y0 + bh - h_:.1f}" width="{cw - 6:.1f}" height="{h_:.1f}" rx="5" fill="{shade[sec] if sec != "Intro" else "#7a7a7a"}"/>')
        if i % 4 == 0 or i == TOTAL_BARS - 1:
            out.append(D.t_(lx + i * cw + cw / 2, y0 + bh + 30, str(i + 1), cs - 2, 500))
    cap = "Layers playing in each of the 30 bars"
    out.append(D.t_(W / 2, y0 + bh + 66, cap, cs + 2, 500))
    D.lab(name + " cap", cap, cs + 2, W - 20)
    return "".join(out), W, y0 + bh + 82


def map_body(W=1600, name="map", fs=24, ts=20):
    gx = 250
    pwid = W - gx - 16

    def X(t):
        return gx + pwid * t / TOTAL_S

    out = []
    sh = 54
    shade = {"Intro": "#4a4a4a", "Build": "#000", "Peak": ACCENT, "Resolve": "#4a4a4a"}
    for nm, a, b in SECTIONS:
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{shade[nm]}"/>')
        out.append(D.t_((X(a) + X(b)) / 2, sh / 2 + fs * .3 + 2, nm.upper(), fs - 4, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 4, X(b) - X(a) - 10)
    lh, lg = 30, 6
    y0 = sh + 14
    out.append(D.t_(gx - 14, y0 + 6, "LAYERS", fs - 6, 700, anchor="end", fill_=ACCENT))
    for i, (nm, a, b, _d, src) in enumerate(LAYERS):
        yy = y0 + 16 + i * (lh + lg)
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, nm.upper(), 20, 700, anchor="end"))
        D.lab(name + " lanes", nm.upper(), 20, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        fill_ = ACC_LIGHT if src == "loop" else "#bdbdbd"
        edge = ACCENT if src == "loop" else "#000"
        out.append(f'<rect x="{X(a):.1f}" y="{yy + 4}" width="{X(b) - X(a):.1f}" height="{lh - 8}" rx="6" fill="{fill_}" stroke="{edge}" stroke-width="2"/>')
    ay0 = y0 + 16 + len(LAYERS) * (lh + lg) + 8
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
    ky = ty + 52
    out.append(f'<rect x="{gx}" y="{ky - 17}" width="30" height="22" rx="5" fill="#bdbdbd" stroke="#000" stroke-width="2"/>')
    out.append(D.t_(gx + 42, ky + 1, "layer I made", ts, 500, anchor="start"))
    out.append(f'<rect x="{gx + 250}" y="{ky - 17}" width="30" height="22" rx="5" fill="{ACC_LIGHT}" stroke="{ACCENT}" stroke-width="2"/>')
    out.append(D.t_(gx + 292, ky + 1, "Apple Loop I rearranged", ts, 500, anchor="start"))
    for t_ in ("layer I made", "Apple Loop I rearranged"):
        D.lab(name + " key", t_, ts, 260)
    for t in (0, 8, 24, 44, 60):
        lbl = mmss(t)
        anc = "start" if t == 0 else ("end" if t == TOTAL_S else "middle")
        out.append(f'<line x1="{X(t):.1f}" y1="{ty - 6}" x2="{X(t):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(t) + (2 if t == 0 else (-2 if t == TOTAL_S else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 80)
    return "".join(out), W, ky + 18


DRAWINGS = {"hero": lambda: D.stack([hero_body()], 40), "cycle": lambda: cycle_body(1600), "brief": lambda: brief_body(1600),
            "arc": lambda: arc_body(1600), "arrange": lambda: map_body(1600, "arrange pic")}
DRAWING_PX = {"hero": 1900, "cycle": 2000, "brief": 2000, "arc": 2000, "arrange": 2000}
SIDE = {"cycle": ["Choose 3 descriptive words", "Plan how sound shows each word", "Compose and mix one minute",
                  "Reflect, bounce and present"],
        "brief": ["An invented brief on paper", "Three words, four kinds of choice", "Every choice points back to a word",
                  "Your words are your creative brief"],
        "arc": ["An invented piece, on paper", "Fewer layers, then more, then fewer", "The peak has the most layers",
                "Build, peak, resolve"],
        "arrange": ["An invented 60-second piece", "Four sections you can name", "Seven layers, two are loops",
                    "Four automation lanes, none flat"]}


def label_extras():
    map_body(1250, "page arrange", 24, 20)
    cycle_body(1250, "page cycle", 28, 20)
    brief_body(1250, "page brief", 34, 24)
    arc_body(1250, "page arc", 26, 22)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Royalty Free", "Music with a job to do.",
     "Class 1, the first minute. No audio is included in this deck. Open with my overview: you are composing music for the real world. "
     "Create a 1-minute piece of royalty-free music that could score a video for the school district, anything from sports "
     "highlights to facilities tours, guided by 3 descriptive words you choose from a provided list."),
    (1, "listen", "Think: music with a job", "Think, then share|Teacher: describe a 30-second video of a school sports highlight, first with no music and then "
     "with music. No audio is needed.|What does the music need to do for that video?|What changes if a calm piece plays under it instead?|"
     "Who must give permission to use a song?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker; describe a short video and let students "
     "imagine two kinds of music under it. No one else's music is included in this kit. This sets up my teacher note that students love "
     "knowing their music might actually get used, and my goal of understanding what makes music functional for media use."),
    (1, "bullets", "What is Royalty Free?", "Compose a 1-minute piece for media use|Guided by 3 descriptive words|No copyrighted samples; "
     "the arrangement is yours|Compose for a purpose, not just yourself",
     "My overview and goals, shortened to fit the slide. You are composing music for the real world: a 1-minute piece of royalty-free "
     "music that could score a video for the school district. Your sound and mood are guided by 3 descriptive words you choose from a "
     "provided list. My goals are to compose from keywords rather than personal preference, understand what makes music functional, "
     "practice efficient composition within a defined length and mood, and match musical choices to a visual or emotional context."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: introduction and word list; choose 3 words, brainstorm and begin "
     "composing. Classes 2 to 4 are working days: compose and refine your 1-minute piece. Class 5: mix and finalize, and write the "
     "reflection paragraph. Class 6: final bounce and prepare presentations. Class 7: presentations with Padlet Q and A peer "
     "feedback. Hand out the project sheet and the Word list now."),
    (1, "pic", "Five steps, then finish", "cycle",
     "Class 1. The first five steps of my project sheet, in order: choose your words, plan, compose, mix, and write the reflection "
     "paragraph. Then students finalize with a bounce and present with Padlet feedback. Point to each box and say roughly when it "
     "happens: choosing and planning today, composing on the working days, mixing and the paragraph in Class 5. The step names are "
     "mine; the picture and its short labels are the kit's own."),
    (1, "bullets", "Four words to know", "Royalty-Free: no ongoing fees, no copyrighted samples|Descriptive words: the mood of a "
     "piece|Scoring: music written to go with visuals|Apple Loops: allowed, but the arrangement is yours",
     "My four vocabulary terms, shortened to fit the slide. Royalty-Free: music that can be used without paying ongoing fees, with no "
     "copyrighted samples. Descriptive Words: adjectives that define the mood and character of a piece, for example upbeat or "
     "cinematic. Scoring: writing music specifically designed to accompany visual media. Apple Loops: pre-made loops in Logic, "
     "allowed here, but the arrangement must be your own. The full definitions are on the vocabulary page."),
    (1, "steps", "Steps 1 and 2: choose, plan", "Review the word list and pick 3 that define your mood|Brainstorm how instruments, rhythm "
     "and melody bring them to life|Write your 3 words at the top of your Creative brief|Name where your music would be used",
     "Steps 1 and 2 of the project sheet, shortened to fit the slide. Step 1, choose your words: review the word list and pick 3 "
     "that define your track's mood. Step 2, plan: brainstorm how instruments, rhythm and melody bring those words to life. The last "
     "two lines are the kit's own suggestions, not my steps: write the words at the top of the Creative brief, and name where the music "
     "would be used, which is my first tip. Hand out the Word list and the Creative brief."),
    (2, "pic", "Words become sound", "brief",
     "Class 2. A kit picture, not from my sheets: an invented brief on paper. Three words from the list, Bright, Steady and "
     "Uplifting, each turned into choices about sounds, rhythm, harmony and the mix. Ask students to pick one cell and say what they "
     "would hear. The Creative brief page lets them do the same for their own three words. Nothing here is audio."),
    (2, "bullets", "Your 3 words are your brief", "Every choice should connect back to them|Stuck? Ask which word a layer is for|Listen to "
     "a royalty-free piece and name its words|Keep the place it would be used in mind",
     "My third tip and my first struggle, shortened to fit the slide. Your 3 words are your creative brief, and every choice should "
     "connect back to them. Students sometimes ignore their words and just make what they want, so keep asking which word a layer is "
     "for. The second and third lines are the kit's own suggestions: the Listening log is a place to study a royalty-free piece the "
     "student chooses, and my first tip, keep the real use in mind, is the fourth line."),
    (3, "steps", "Step 3: compose", "Build your 1-minute piece in Logic|Use layers that suit the style|Apple Loops are fine; the "
     "arrangement must be original|Log each layer as your own, a loop or both",
     "Step 3 of the project sheet and requirements 3 and 4, shortened to fit the slide. Step 3, compose: build your 1-minute piece in "
     "Logic. Requirement 3: your music must be royalty-free, with no copyrighted samples; Apple Loops are allowed but the arrangement "
     "must be original. Requirement 4: use layers appropriate to the style. The last line is the kit's own suggestion, not my step: "
     "the Layers and mix sheet asks students to say which layers they made, which are loops and what they changed, which answers my "
     "third struggle, over-reliance on Apple Loops."),
    (3, "pic", "Build, peak, resolve", "arc",
     "Class 3, the first working day after the brief. A kit picture of an invented piece: how many layers play in each of 30 bars. "
     "It starts with two, grows through the build, has its most layers in the peak and thins out to a single pad at the end. My "
     "second struggle is that tracks feel incomplete at 1 minute, and my fix is a simple arc: build, peak, resolve. Students can "
     "plan their own on the Arrangement plan."),
    (3, "pic", "Worked example: 60 seconds", "arrange",
     "Class 3. An invented piece, Open Doors, described on paper for an invented video; nothing here is audio. It is 60 seconds, 30 "
     "bars at 120 BPM, in four sections: intro, build, peak and resolve. Seven layers join and leave, and two are Apple Loops that "
     "the student cut and rearranged. Below them are four automation lanes, and none is flat. The chords, the numbers and the "
     "weak and clear plans are on the worked example pages."),
    (4, "bullets", "One minute goes fast", "Pick a vibe and commit|Don’t cram too many ideas in|Give it a simple arc: build, peak, "
     "resolve|Check the length: 60 seconds, give or take",
     "My second tip and my second struggle, shortened to fit the slide. One minute goes fast, so do not cram too many ideas in; pick a "
     "vibe and commit. Tracks can feel incomplete at 1 minute, so encourage a simple arc: build, peak, resolve. The last line is the "
     "kit's own reminder: the length is 1 minute, give or take a few seconds, and bars times 240 divided by tempo gives seconds. Ask "
     "each student to play their first 20 seconds and say which of their words they hear."),
    (5, "bullets", "Step 4: mix", "EQ, pan and balance your tracks|Apply EQ and plug-ins to shape your mix|Can you hear every "
     "layer?|Do your 3 words still come through?",
     "Step 4 and requirement 5, shortened to fit the slide. Mix: EQ, pan and balance your tracks, and apply EQ and plug-ins to shape "
     "your mix. The last two lines are the kit's own questions for the Layers and mix sheet: close your eyes and listen for each layer, "
     "then for each of the three words. Students fix the one thing that hides a word."),
    (5, "steps", "Steps 5 and 6: reflect, bounce", "Write your reflection paragraph|Explain how the song reflects your 3 words|Bounce your "
     "track with the correct file name|Zip the .logicx project",
     "Class 5. Steps 5 and 6 of the project sheet, shortened to fit the slide. Write your reflection paragraph explaining your "
     "creative choices, and requirement 6, explain how your song reflects your 3 chosen words. Finalize: bounce your track with the "
     "correct file name format. My fourth struggle is that the paragraph is an afterthought, so students plan it on the Reflection "
     "page first. A reflection is a written or oral conversation about how they did and what they would do differently next time. "
     "The last line is the kit's own reminder to zip the project."),
    (6, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Royalty Free – Word, Word, Word|"
     "Reflection paragraph|Padlet post with 3 questions|Answer 2 questions on classmates’ posts",
     "The submission checklist from the project sheet, shortened to fit the slide. Show where students upload (your class page) and "
     "where the Padlet board is. The file name is Your Name, Royalty Free, then the three words, in that order. Check that every "
     "track is about 1 minute before students bounce."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play your track; say your 3 words|Say where each word shows up|Your Padlet post: 3 questions "
     "about your project|Answer at least 2 of each classmate’s 3",
     "Class 7, presentations with Padlet Q and A. Step 7 of the project sheet, shortened to fit the slide: create your own Padlet post "
     "with 3 questions you want classmates to answer, present to the class, and during classmates' presentations answer at least 2 of "
     "their 3 questions. The first two lines are the kit's own suggestions. Ask the class to name the three words before the "
     "presenter does."),
    (7, "closer", "One last thing…", "You got a brief.|You made your choices.|You kept it to a minute.|Now press play.",
     "Close with my teacher notes: this project pairs well with real district videos, and students love knowing their music might "
     "actually get used. Ask a few students which word they heard most in a classmate's track. Tell them the next project starts from "
     "the menu."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("example", "Worked example", "an invented piece on paper"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 8, 11, 12, 17]
SHOTS3 = [("example", "Worked example"), ("words", "Word list"), ("brief", "Creative brief"), ("arrange", "Arrangement plan"),
          ("mix", "Layers and mix"), ("reflect", "Reflection"), ("setup", "Setup"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "changes", "logicref", "vary", "example", "example2",
        "words", "brief", "listen", "arrange", "mix", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "example", "words", "rubric"]

COVER_A = "Music with a job to do"
COVER_C = "DMP2 · functional composition · intro slides"
PDF_COVER = dict(a=30, b=50, c=14, art=7.3)
SQ_COVER = dict(a=44, b=140, c=27, art=740, gap=44)
SQ_B_LINES = ["Royalty", "Free"]
SQ_SUB = "7 class periods · 3 words · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "160-word list, creative brief, arrangement plan, worked example", 28)}
SQ_BANDS = {1: "Choose <em>·</em> plan <em>·</em> compose <em>·</em> mix <em>·</em> reflect",
            2: "Hook <em>·</em> words become sound <em>·</em> build, peak, resolve <em>·</em> mix",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, video, songs, artists or albums are named or included. Students make every sound in their tracks themselves, "
             "from the instruments, kits and Apple Loops in Logic.")
CREDITS = ["Worked example (an invented one-minute piece for an invented video, with its chords, sections, layers and automation lanes, "
           "described on paper), the hero, card, brief, arc and arrangement drawings and layouts: original work, Hudson Beat.",
           "The Word list is the owner’s “Groups of Words” sheet. No audio, video, lyrics, album art, screenshots, presets, templates, "
           "links or chart data are included. No student work is included. Padlet is named only as the owner’s own materials name it."]
LOGIC_INTRO = ("Where to find the tools a Royalty Free project is likely to use. Demonstrate what your class needs on Classes 1 and 2 "
               "and then let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add tracks with Track › New Tracks…: Software Instrument tracks for pads, keys, "
              "bass and bells, and Drummer or Apple Loops for drums."),
             ("Apple Loops", "Open the Loop Browser (O) and drag a loop into a track. Apple Loops are allowed here, but the arrangement "
              "must be your own: cut loops, repeat them, drop layers in and out, and add your own parts (my third struggle)."),
             ("Tempo and length", "Set the tempo in the control bar. Bars × 240 ÷ tempo = seconds; at 120 BPM, 30 bars is 60 seconds. "
              "The Arrangement plan has a length helper."),
             ("Sections", "Show Global Tracks (G) and add arrangement markers named Intro, Build, Peak and Resolve, so the form is visible "
              "in the project."),
             ("Layers", "Add one layer at a time. Mute and unmute tracks, or cut regions, to bring layers in and out of the sections."),
             ("Automation", "Press A to show track automation. Pick a parameter, such as filter cutoff, volume, pan or reverb send, and draw "
              "points so the sound moves."),
             ("EQ, pan, plug-ins", "Add Channel EQ for balance, use each track's Pan knob, and add plug-ins such as a reverb or filter. "
              "Press X for the Mixer."),
             ("Endings", "A resolve usually means layers leave and the last chord settles. Use volume automation or a fade, and check "
              "that nothing is cut off at the end."),
             ("Scoring to video (Harder)", "Choose Open Movie from the File menu or the Window menu in your version, and open a clip you "
              "have the right to use. Add markers at the moments the music should hit (see the Easier and Harder variations page)."),
             ("Bounce and zip", "File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and "
              "choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and zipped .logicx submitted",
                 "Reflection paragraph submitted (page @REFLECT)", "Padlet post created with my 3 questions",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my track:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12.2pt;margin-bottom:3pt">Ignoring the words: the Creative brief (page @BRIEF), slide 8 and the word check on the Layers and mix sheet (page @MIX).</li>'
    '<li style="font-size:12.2pt;margin-bottom:3pt">Incomplete at 1 minute: slide 11 and the Arrangement plan (page @ARRANGE) show a build, a peak and a resolve.</li>'
    '<li style="font-size:12.2pt;margin-bottom:3pt">Too many Apple Loops: the layer log on the Layers and mix sheet (page @MIX) and the worked example (page @EXAMPLE2).</li>'
    '<li style="font-size:12.2pt;margin-bottom:0">An afterthought paragraph: the Reflection planner (page @REFLECT), with a thin and a useful example.</li></ul></div>'
    '<div class="box" style="margin-top:6pt"><span class="k">Where this kit helps with the variations (kit suggestion)</span><ul style="margin:0">'
    '<li style="font-size:12.2pt;margin-bottom:3pt">Easier: a blank structural template and a 2-word brief (page @VARY).</li>'
    '<li style="font-size:12.2pt;margin-bottom:0">More advanced: a hit-point sheet for scoring to a clip you choose (page @VARY).</li></ul></div>')
TN1_SIZE = 15.0
PROJ_SIZE = 14.2
VOCAB_GAP = 34
CHANGES_SIZE = 9.4
LOGIC_SIZE = 11.2
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ small page helpers
CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; } table.sg td, table.sg th { border: 1pt solid #000; text-align: center; "
          "padding: 0; font-size: 8pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.2in; font-size: 9pt; } "
          "table.sg td.b { border-left: 2.2pt solid #000; } table.sg td.on { background: " + ACCENT + "; } </style>")


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, what changed, Logic quick "
              "reference, Easier and Harder variations, worked example (2 pages)"),
             ("Student pages", "words", "reflect", "Word list, Creative brief, Listening log, Arrangement plan, Layers and mix sheet, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection planner"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period structured project for high school music '
             f'technology. Each student composes a one-minute piece of royalty-free music in Logic, as if for a school video, guided by '
             f'three descriptive words they choose from a list. They plan it as a creative brief, give it a build, a peak and a resolve, '
             f'mix it, write a paragraph on how it reflects their words, and present it with Padlet questions for feedback. It is the '
             f'project from my Digital Music Production 2 course (type: structured; focus: functional composition), and the projects in '
             f'that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Set up the Presentation Padlet and decide how you will treat Apple Loops (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("words")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}: 2 words and a structural template, or scoring to a real video clip (both laid out on page {D.IX("vary")}).</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Word choice:</b> students choose their three words from the list; you could also assign them with a wheel, as a kit suggestion.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'music can have a job to do, and that three well-chosen words are a creative brief.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro and Apple Loops are products of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13.4pt;line-height:1.5">One original piece of royalty-free music, about one minute long, built from '
             f'layers that suit its style and shaped by three descriptive words from the list. It is mixed with EQ and plug-ins and may '
             f'use Apple Loops as long as the arrangement is the student’s own. They hand in a bounced .mp3 or .wav, the zipped .logicx '
             f'project and a paragraph explaining how the song reflects their three words, plus a Padlet post with three feedback '
             f'questions, then play the piece and present it.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:13pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:12pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:13pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.6pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: choose words and plan, three working days, mix and reflect, bounce, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: instruments, Apple Loops, arrangement, automation, EQ and plug-ins, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a feedback board and a place to submit files</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:12pt">Students should already '
             f'know how to open a project, add software instruments and loops, use the Mixer, and save, bounce and zip in Logic. Nobody '
             f'needs to read music.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Structured", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 12.2pt; line-height: 1.46; margin-bottom: 6pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the final listen.</li>'
             f'<li><b>A place to submit</b> the .mp3 or .wav, the zipped .logicx and the reflection paragraph (your class page).</li>'
             f'<li><b>The Presentation Padlet</b>, set up before Class 1 (yours to set up; none is included).</li>'
             f'<li><b>The Word list</b>, printed (page {D.IX("words")}), or your own copy of the list on your class page.</li>'
             f'<li><b>A rule for Apple Loops</b> (requirement 3): loops are allowed but the arrangement must be original. Decide what that '
             f'means (for example, no loop used untouched for the whole piece) and write it on the board.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("words")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:12.2pt;margin-bottom:8pt") for c in [
                 "Set up the Presentation Padlet in your class page.",
                 "Decide your Apple Loops rule and how you will check it (page @MIX).".replace("@MIX", str(D.IX("mix"))),
                 "Choose the video you might use for the Harder variation, if any (page @VARY).".replace("@VARY", str(D.IX("vary"))),
                 "Check that a student computer opens Logic and plays back through headphones."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch (my struggles)", True)}'
             f'<p style="font-size:12pt">Students ignore their three words, tracks feel incomplete at one minute, students lean on Apple '
             f'Loops, and the reflection paragraph is an afterthought. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Kit suggestions, not part of my sheets</span><ul style="margin:0">'
             f'<li style="font-size:11.6pt">Ways to use the word list: students pick their own three, or you spin a wheel and let them swap one.</li>'
             f'<li style="font-size:11.6pt">Real uses to name on Class 1: a sports highlight, a facilities tour, an announcement, a club promo. Ask what each one needs.</li>'
             f'<li style="font-size:11.6pt">Ask while students work: which of your words is this layer for? Where does the peak happen?</li></ul></div>'
             f'{D.H2("Sounds they did not make")}'
             f'<div class="box"><span class="k">A kit suggestion</span><p style="margin:0;font-size:11.4pt;line-height:1.42">'
             f'Remind students that “royalty-free” means no copyrighted samples: they use their own sounds, instruments and Apple Loops '
             f'from Logic, and they hand in only their own track.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.4pt;line-height:1.42">'
             f'Bright sounds and loud peaks are tiring in headphones. Tell students to start low and to check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


def vary_page(n, wm=False):
    rows = "".join(f"<tr><td style='width:20%;height:30pt'><b>{a}</b></td><td>{b}</td></tr>" for a, b in
                   [("Intro", "bars 1–4 · 4 bars"), ("Build", "bars 5–12 · 8 bars"), ("Peak", "bars 13–22 · 10 bars"),
                    ("Resolve", "bars 23–30 · 8 bars")])
    hit = "".join("<tr><td style='height:26pt'></td><td></td><td></td><td></td></tr>" for _ in range(6))
    inner = (f'<style>.sb2 li {{ font-size: 11.4pt; line-height: 1.38; margin-bottom: 4pt; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:11.4pt;line-height:1.4">My Easier variation: reduce to 2 descriptive words and provide a '
             f'structural template. The words are your choice, and the template below is the kit’s own (it is not one of my sheets). '
             f'Copy it onto the board or hand it out.</p>'
             f'{D.H2("Easier: a structural template for one minute", True)}'
             f'<div class="cols" style="gap:12pt"><div><table class="t" style="font-size:11pt"><tr><th>Section</th><th>Bars</th></tr>{rows}</table>'
             f'<p style="margin:3pt 0 0;font-size:10pt">30 bars at 120 BPM = 60 seconds. At another tempo, use the length helper on page {D.IX("arrange")}.</p></div>'
             f'<div class="box acc-b"><span class="k">How to use it</span><ol class="sb2" style="margin:0"><li>Two words instead of three; the brief on page {D.IX("brief")} has room for a third.</li>'
             f'<li>Fill the sections: the intro has the fewest layers, the peak the most, the resolve thins out.</li>'
             f'<li>Students may change the bar counts as long as the piece is about a minute.</li></ol></div></div>'
             f'{D.H2("Harder: score your track to a real video clip")}'
             f'<p style="margin:0 0 3pt;font-size:11.4pt;line-height:1.4">My More Advanced variation. No video is included: choose a clip you have the '
             f'right to use (a district video, or one your students shot). Students watch it first, write down where something happens '
             f'on screen, and decide what the music does at that moment.</p>'
             f'<table class="map"><tr><th style="width:14%">Time</th><th style="width:34%">What happens on screen</th><th style="width:30%">What the music does</th>'
             f'<th>Which word</th></tr>{hit}</table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Check</span>'
             + D.chk("The first section starts where the video starts, and the resolve ends with it.", 12, "font-size:11pt;margin-bottom:3pt")
             + D.chk("The peak lands on the most important moment of the clip.", 12, "font-size:11pt;margin-bottom:3pt")
             + D.chk("The music does not cover any speech in the clip.", 12, "font-size:11pt;margin-bottom:0") + '</div>')
    return D.page("Easier and Harder variations", "TEACHER", "Easier + Harder", inner, n, key="vary")


def example_page(n, wm=False):
    br = "".join(f"<tr><td style='width:14%'><b>{w}</b></td>" + "".join(f"<td>{BRIEF[w][r]}</td>" for r in range(4)) + "</tr>" for w in WORDS3)
    inner = (f'<p style="margin:0 0 5pt;font-size:10.4pt">An <b>invented piece, “{PIECE}”, described on paper</b>, for {VIDEO}: no audio '
             f'is included. Students’ projects will differ. {TOTAL_BARS} bars at {BPM} BPM, three words, four sections, seven layers (page 1 of 2).</p>'
             f'<div class="cols" style="gap:10pt"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.4pt">{WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.4pt">It names no words and nothing says why any choice was made.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:9pt;line-height:1.28">{STRONG}</p></div></div>'
             f'{D.H2("3 · Three words, four kinds of choice")}'
             f'<div style="width:5.6in;margin:2pt auto 3pt">{D.body_svg(brief_body(1250, "page brief", 34, 24))}</div>'
             f'<table class="t" style="font-size:9pt;line-height:1.25"><tr><th>Word</th>' + "".join(f"<th>{r}</th>" for r in BRIEF_ROWS) + f'</tr>{br}</table>'
             f'{D.H2("4 · Build, peak, resolve: layers in each bar")}'
             f'<div style="width:5.2in;margin:2pt auto 0">{D.body_svg(arc_body(1250, "page arc", 26, 22))}</div>')
    return D.page("Worked example · an invented piece", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    lay = "".join(f"<tr><td style='width:17%'><b>{a}</b></td><td>{d}</td><td style='white-space:nowrap'>{mmss(s)}–{mmss(e)}</td></tr>"
                  for a, s, e, d, _src in LAYERS)
    aut = "".join(f"<tr><td><b>{ly} · {par}</b></td><td>{mmss(pts[0][0])}–{mmss(pts[-1][0])}</td></tr>" for ly, par, pts in AUTO)
    ph = "".join(f"<tr><td style='width:16%'><b>{a}</b></td><td style='width:17%;white-space:nowrap'>{b}</td><td>{c}</td></tr>"
                 for a, b, c in SECTION_NOTES)
    chs = "".join(f"<td>{c}<br><span style='font-size:7.4pt'>{a if a == b else str(a) + '–' + str(b)}</span></td>" for c, a, b in CHORDS)
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">“{PIECE}”, page 2 of 2: the map of the whole piece, then the numbers.</p>'
             f'{D.H2("5 · The map: 1:00, four sections, seven layers, four lanes")}'
             f'<div style="width:6.4in;margin:1pt auto 3pt">{D.body_svg(map_body(1250, "page arrange", 24, 20))}</div>'
             f'<div class="cols" style="gap:10pt"><div><span class="k" style="font-size:9.4pt">6 · Sections</span>'
             f'<table class="t" style="font-size:8.4pt;line-height:1.2;margin-top:2pt">{ph}</table></div>'
             f'<div><span class="k" style="font-size:9.4pt">7 · Layers (in to out)</span>'
             f'<table class="t" style="font-size:8.4pt;line-height:1.2;margin-top:2pt">{lay}</table></div></div>'
             f'<span class="k" style="font-size:9.4pt;display:block;margin-top:3pt">8 · The chords, bar by bar (the bass plays each root: C2, G1, A1, F1; the bell melody uses only chord tones)</span>'
             f'<table class="t" style="font-size:8.8pt;line-height:1.1;margin-top:2pt;text-align:center"><tr>{chs}</tr></table>'
             f'<div class="cols" style="gap:10pt;margin-top:4pt"><div><span class="k" style="font-size:9.4pt">9 · Automation lanes</span>'
             f'<table class="t" style="font-size:8.4pt;line-height:1.2;margin-top:2pt">{aut}</table></div>'
             f'<div class="box acc-b"><span class="k">10 · Checking the numbers</span><p style="margin:0;font-size:8.4pt;line-height:1.26">'
             f'One bar of 4/4 at {BPM} BPM lasts 240 ÷ {BPM} = {BAR_S:g} seconds, so {TOTAL_BARS} bars = {TOTAL_BARS * BAR_S:g} seconds, my "1 minute". '
             f'The sections are {" + ".join(str(int((b - a) / BAR_S)) for _, a, b in SECTIONS)} bars = {TOTAL_BARS}. Two of seven layers are Apple Loops, and both '
             f'are cut and rearranged. <b>Three Padlet questions (invented):</b> {qs}</p></div></div>')
    return D.page("Worked example · the map", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


def words_page(n, wm=False):
    cb = ("<span style='display:inline-block;width:7.6pt;height:7.6pt;border:1pt solid #000;border-radius:50%;margin-right:5pt;"
          "vertical-align:-0.5pt'></span>")
    lst = "".join(f"<div style='break-inside:avoid;white-space:nowrap'>{cb}{w}</div>" for w in WORDS_ALPHA)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.38">Step 1: review the word list and pick 3 that define your track’s mood. '
             f'Requirement 2: choose 3 descriptive words from the provided list. Descriptive words are adjectives that define the mood and character '
             f'of a piece (e.g., “upbeat,” “cinematic”). Circle three, then copy them onto your Creative brief. The words are listed A to Z.</p>'
             f'<div style="column-count:5;column-gap:8pt;font-size:10pt;line-height:1.5;margin-top:2pt">{lst}</div>'
             f'<div class="box acc-b" style="margin-top:7pt"><span class="k">My three words</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Word 1:</b><span></span><b>Word 2:</b><span></span><b>Word 3:</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>Why they go together:</b><span></span></div></div>')
    return D.page("Word list", "STUDENT", "Class 1", inner, n, wm, name=True, key="words")


def brief_page(n, wm=False):
    trs = "".join("<tr><td style='height:74pt'></td><td></td><td></td><td></td><td></td></tr>" for _ in range(3))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt">Step 2: brainstorm how instruments, rhythm, and melody bring those words to life. '
             f'Your 3 words are your creative brief. Every choice should connect back to them. Think about where this music would actually be used.</p>'
             f'<div class="box acc-b" style="margin:0 0 5pt"><span class="k">The brief</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Where my music would be used (the kind of video):</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>What the person watching should feel:</b><span></span></div></div>'
             f'<table class="map"><tr><th style="width:12%">My word</th><th style="width:22%">Sounds and instruments</th>'
             f'<th style="width:22%">Rhythm and tempo</th><th style="width:22%">Melody and harmony</th><th>How the mix feels</th></tr>{trs}</table>'
             f'<div class="box" style="margin-top:7pt"><span class="k">Check the brief</span>'
             + D.chk("Every word has at least one sound, one rhythm choice and one harmony choice behind it.", 12, "font-size:10.8pt;margin-bottom:3pt")
             + D.chk("I can say which word each layer is for.", 12, "font-size:10.8pt;margin-bottom:3pt")
             + D.chk("My words fit the video, not only what I like.", 12, "font-size:10.8pt;margin-bottom:0") + '</div>'
             f'<div class="fl" style="margin-top:7pt"><b>My tempo:</b><span style="flex:0 0 0.9in"></span><b>My key or mood:</b><span></span></div>'
             f'<div class="fl"><b>If a stranger heard my track with no title, the three words they would pick:</b><span></span></div>'
             f'<div class="fl"><b>The word I think will be hardest to hear, and my plan for it:</b><span></span></div>')
    return D.page("Creative brief", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="brief")


LENSES = [("Song structure", "How are the sections laid out? Where does it build or change?"),
          ("Instrumentation", "Which instruments or sounds are used, and what does each add to the feel?"),
          ("Loops and repetition", "What repeats? How does the producer keep it interesting?"),
          ("Emotional impact", "What mood does it give, and which instrument or choice creates it?"),
          ("Transitions", "How does it get from one section to the next? Smooth or abrupt?"),
          ("Application to visuals", "Where could it be used (sports, tours, announcements)? What would not fit?")]


def listen_page(n, wm=False):
    trs = "".join(f"<tr><td style='height:50pt'><b>{a}</b><br><span style='font-size:8.6pt'>{b}</span></td><td></td><td></td></tr>" for a, b in LENSES)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt;line-height:1.4">Step 2: plan. Listen to royalty-free music and study how it is built. '
             f'Choose a piece yourself, from YouTube or a free music library (no music is included in this kit). Take ideas about how it works, not '
             f'its notes: your arrangement must be your own.</p>'
             f'<div class="box acc-b" style="margin:0 0 5pt"><span class="k">The piece</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Title and where I found it:</b><span></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>Three descriptive words I would give it:</b><span></span></div></div>'
             f'<table class="map"><tr><th style="width:36%">What to dissect</th><th style="width:34%">What I hear</th><th>An idea I can use</th></tr>{trs}</table>'
             f'<div class="fl" style="margin-top:7pt"><b>Something I will not do, because it does not fit my words:</b><span></span></div>'
             f'<div class="fl"><b>One thing in this piece I will try in my own way:</b><span></span></div>')
    return D.page("Listening log", "STUDENT", "Classes 2–3", inner, n, wm, name=True, key="listen")


def arrange_page(n, wm=False):
    nb = 36
    head = "<tr><th style='width:1.25in'>Layer</th>" + "".join(f"<th>{i + 1}</th>" for i in range(nb)) + "</tr>"
    body = "".join("<tr><td class='l' style='height:30pt'></td>" + "".join(f"<td class='{'b' if i % 4 == 0 else ''}'></td>" for i in range(nb)) + "</tr>"
                   for _ in range(8))
    help_rows = [(80, 20), (96, 24), (100, 25), (120, 30), (128, 32), (144, 36)]
    hr = "".join(f"<tr><td><b>{b}</b></td><td>{bars}</td><td>{240 / b:.2f} s</td></tr>" for b, bars in help_rows)
    inner = (f'{CSS_SG}<style>table.sg th {{ font-size: 6pt; }} table.sg td.l {{ width: 1.25in; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.6pt">Step 3: build your 1-minute piece in Logic. Tracks feel incomplete at 1 minute, so give it a simple arc: '
             f'build, peak, resolve. Shade the bars where each layer plays and write the layer’s name at the left. Mark where each section starts. '
             f'Use layers appropriate to the style.</p>'
             f'<table class="sg">{head}{body}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:6pt"><div class="box acc-b"><span class="k">My sections (intro · build · peak · resolve)</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Intro:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Build:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Peak:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>Resolve:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div></div>'
             f'<div><span class="k">Length helper (1 minute)</span><table class="t" style="font-size:9.6pt;margin-top:2pt"><tr><th>BPM</th><th>Bars for 60 s</th><th>One bar</th></tr>{hr}</table></div></div>'
             f'<div class="fl" style="margin-top:6pt"><b>My tempo:</b><span style="flex:0 0 0.8in"></span><b>Bars:</b><span style="flex:0 0 0.8in"></span>'
             f'<b>Length: bars × 240 ÷ tempo =</b><span style="flex:0 0 0.8in"></span><b>seconds</b></div>'
             f'<div class="fl"><b>The peak is in bars</b><span style="flex:0 0 1in"></span><b>because</b><span></span></div>')
    return D.page("Arrangement plan", "STUDENT", "Classes 2–4", inner, n, wm, name=True, key="arrange")


def mix_page(n, wm=False):
    trs = "".join("<tr><td style='height:27pt'></td><td></td><td></td><td></td></tr>" for _ in range(8))
    wr = "".join("<tr><td style='height:24pt'></td><td></td><td></td></tr>" for _ in range(3))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.4pt">Step 4: EQ, pan, and balance your tracks. Requirement 5: apply EQ and plug-ins to shape your mix. '
             f'Apple Loops are allowed, but the arrangement must be your own: say below what you made and what you changed.</p>'
             f'<table class="map"><tr><th style="width:17%">Layer</th><th style="width:21%">Source (my own · Apple Loop · both)</th>'
             f'<th style="width:32%">What I wrote or changed myself</th><th>EQ · pan · plug-in</th></tr>{trs}</table>'
             f'<span class="k" style="display:block;margin-top:6pt">Word check: close your eyes and listen</span>'
             f'<table class="map" style="margin-top:2pt"><tr><th style="width:16%">My word</th><th style="width:34%">Where I hear it (bar or time)</th><th>If I do not hear it, what I will fix</th></tr>{wr}</table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Checks before I bounce</span>'
             + "".join(D.chk(c, 12, "font-size:10.4pt;margin-bottom:2pt") for c in [
                 "There are no copyrighted samples. Every sound is mine or from Logic.",
                 "No Apple Loop plays untouched for the whole piece; I cut, repeat or rebuild each one.",
                 "I can hear every layer, and none is buried or too loud.",
                 "EQ and at least one plug-in are in use.",
                 "The piece is about 1 minute (give or take a few seconds)."]) + '</div>')
    return D.page("Layers and mix sheet", "STUDENT", "Classes 3–5", inner, n, wm, name=True, key="mix")


def reflect_page(n, wm=False):
    prompts = [("Word 1:", "Name it, say what you did to show it, and where we can hear it."),
               ("Word 2:", "Name it, say what you did to show it, and where we can hear it."),
               ("Word 3:", "Name it, say what you did to show it, and where we can hear it."),
               ("What would you do differently next time?", "Be specific: a step, a choice, a sound or a tool."),
               ("Look at the rubric (page @RUBRIC).", "Which category are you proudest of, and which would you work on first next time?")]
    pr = "".join(
        f'<div style="flex:1;display:flex;flex-direction:column;min-height:0;margin-bottom:3pt"><p style="margin:0 0 1pt;font-size:10.4pt">'
        f'<b style="font-family:Oswald;font-size:12pt;color:{ACCENT}">{i}</b>&nbsp; <b>{D.fill(a)}</b> {D.fill(b)}</p>'
        f'<div class="lines" style="min-height:28pt"></div></div>' for i, (a, b) in enumerate(prompts, start=1))
    inner = (f'<div class="box acc-b"><span class="k">What this page is</span><p style="margin:0;font-size:10.4pt;line-height:1.36">My sheet asks '
             f'for a short paragraph explaining how your song reflects your 3 chosen words. Fill in prompts 1 to 3, then write your paragraph on '
             f'your class page. Prompts 4 and 5 follow my definition: a reflection is {D.REFLECT_DEFINITION}; you may talk them through with your teacher instead.</p></div>'
             f'<div class="cols" style="gap:10pt;margin:5pt 0 4pt"><div class="box"><span class="k">Thin (an invented example)</span>'
             f'<p style="margin:0;font-size:9.4pt;line-height:1.3">{THIN}</p></div>'
             f'<div class="box"><span class="k">Useful (an invented example)</span><p style="margin:0;font-size:8.6pt;line-height:1.26">{USEFUL}</p></div></div>'
             f'{pr}')
    return D.page("Reflection · how does it reflect my words?", "STUDENT", "Class 5", inner, n, wm, name=True, key="reflect")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "vary": vary_page, "example": example_page,
         "example2": example2_page, "words": words_page, "brief": brief_page, "listen": listen_page, "arrange": arrange_page,
         "mix": mix_page, "reflect": reflect_page}


# ================================================================ content checks (example arithmetic, owner text, no audio)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 4), reqs=(REQS, 6), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 3))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp} (the owner's count)")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is the owner's /25, levels 1-5")
    if [c for c, _ in RUBRIC] != ["Creativity & Originality", "Technical Skill / DAW Use", "Composition & Structure",
                                  "Sound Design & Mix Quality", "Documentation & Presentation"]:
        errs.append("rubric categories must be the owner's, in order")
    if FILE_NAME not in CHECK[2] or "Royalty Free – Word, Word, Word" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    if "1 minute" not in REQS[0] or "1-minute" not in OVERVIEW:
        errs.append("length 1 minute as the owner wrote it")
    if "3 descriptive words" not in REQS[1] or "3 chosen words" not in REQS[5]:
        errs.append("requirements 2 and 6 as the owner wrote them")
    if REFLECTION:
        errs.append("REFLECTION must be False: the owner's sheet already asks for a reflection paragraph")
    # the word list: the owner's 16 groups of 10 = 160 words, none lost in the A-Z page
    if len(WORDS) != 16 or any(len(g) != 10 for g in WORDS):
        errs.append("word list: 16 groups of 10 words, as on the owner's sheet")
    flat = [w for g in WORDS for w in g]
    if len(WORDS_ALPHA) != 160 or sorted(flat) != sorted(WORDS_ALPHA) or len(set(flat)) != 160:
        errs.append("word list: 160 distinct words, none added or removed")
    if not all(w in flat for w in WORDS3):
        errs.append("the example's three words must come from the owner's list")
    # the worked example adds up
    if BAR_S != 2 or TOTAL_BARS * BAR_S != TOTAL_S or TOTAL_S != 60:
        errs.append("30 bars x 2 s = 60 s (the owner's 1 minute)")
    if [round((b - a) / BAR_S) for _, a, b in SECTIONS] != [4, 8, 10, 8] or sum(round((b - a) / BAR_S) for _, a, b in SECTIONS) != TOTAL_BARS:
        errs.append("sections 4 + 8 + 10 + 8 = 30 bars")
    if SECTIONS[0][1] != 0 or SECTIONS[-1][2] != TOTAL_S or any(b != c for (_, _, b), (_, c, _) in zip(SECTIONS, SECTIONS[1:])):
        errs.append("sections must tile the piece")
    for nm, a, b, _d, src in LAYERS:
        if not 0 <= a < b <= TOTAL_S or a % BAR_S or b % BAR_S or src not in ("own", "loop"):
            errs.append(f"layer {nm}: starts and ends on a bar line, inside the piece; source own or loop")
    loops = [nm for nm, _a, _b, d, s in LAYERS if s == "loop"]
    if len(LAYERS) != 7 or len(loops) != 2 or any(not any(w in d for w in ("cut", "chopped")) for nm, _a, _b, d, s in LAYERS if s == "loop"):
        errs.append("seven layers; two Apple Loops, each cut or chopped (the arrangement must be original)")
    spans = {nm: (a, b) for nm, a, b, _d, _s in LAYERS}
    if len(AUTO) != 4:
        errs.append("four automation lanes")
    for ly, par, pts in AUTO:
        a, b = spans[ly]
        ts = [t for t, _ in pts]
        vs = [v for _, v in pts]
        if ts != sorted(ts) or len(pts) < 3 or ts[0] < a or ts[-1] > b or any(t % BAR_S for t in ts):
            errs.append(f"lane {ly}/{par}: points in order, 3+, on bar lines, inside its layer")
        if max(vs) - min(vs) < .5:
            errs.append(f"lane {ly}/{par}: a lane that barely moves is the static sound the project warns about")
    # build, peak, resolve: the density arc
    top = max(DENS)
    peak_bars = [i for i, d in enumerate(DENS) if d == top]
    pk = next((a, b) for nm, a, b in SECTIONS if nm == "Peak")
    if not all(pk[0] <= i * BAR_S < pk[1] for i in peak_bars):
        errs.append("the most layers must play inside the Peak section")
    if not (DENS[0] < top and DENS[-1] < DENS[0] + 1 and DENS[-1] < top):
        errs.append("the piece must start smaller than its peak and resolve down")
    if sorted(DENS[:16]) != DENS[:16] and DENS[0] >= DENS[15]:
        errs.append("the build must grow")
    # chords: every bar has one chord; pitches are chord tones
    bars = []
    for c, a, b in CHORDS:
        if c not in CHORD_NOTES:
            errs.append(f"chord {c} unknown")
        bars += list(range(a, b + 1))
    if bars != list(range(1, TOTAL_BARS + 1)):
        errs.append("chords must cover bars 1-30 exactly once")
    if CHORDS[-1][0] != "C" or CHORDS[0][0] != "C":
        errs.append("the piece starts and ends on the home chord C")
    for c in CHORD_NOTES:
        if BASS_ROOT[c].rstrip("0123456789") != c.rstrip("m"):
            errs.append(f"bass root for {c}")
        for nt in BELL[c]:
            if nt.rstrip("0123456789") not in CHORD_NOTES[c]:
                errs.append(f"bell note {nt} is not a tone of {c}")
        if len(BELL[c]) != 4:
            errs.append("four bell notes a bar")
    for nm, a, b in SECTIONS:
        ca = [c for c, x, y in CHORDS if x == int(a / BAR_S) + 1]
        if not ca:
            errs.append(f"a chord must start where {nm} starts")
    if len(QUESTIONS) != 3 or len(WORDS3) != 3:
        errs.append("three Padlet questions and three words")
    for bpm, bars_ in [(80, 20), (96, 24), (100, 25), (120, 30), (128, 32), (144, 36)]:
        if bars_for(60, bpm) != bars_:
            errs.append(f"length helper wrong at {bpm} BPM")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    txt = " ".join(flat)
    for need in ("No audio, video, songs, artists or albums", "invented piece, “Open Doors”",
                 "Your Name – Royalty Free – Word, Word, Word", "Final Grade = Average of Student + Teacher", "No student work is included",
                 "Mesmerising", "Wonderous"):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "Grades 10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up:
        errs.append("UPLOAD.md: must say no audio is included and record the open questions")
    for i in (2, 5, 6, 8, 9, 12, 13, 14, 15, 17):   # slides that shorten the owner's wording must say so
        if "shortened" not in notes[i].lower() and "shortens" not in notes[i].lower():
            errs.append(f"deck slide {i + 1} notes: must say the owner's wording is shortened")
    ch = flat[D.IX("changes") - 1]
    for s in ("slide 3", "slide 6", "slide 7", "slide 9", "slide 10", "slide 13", "slide 14", "slide 15", "slide 16", "slide 18"):
        if s not in ch:
            errs.append(f"'What changed' page must list {s}")
    if "Reflection page, not a new task" not in ch:
        errs.append("'What changed' page must explain the Reflection page")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or any("Arrangement plan" in g or "Reflection" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Spotify", "Radiohead", "Billboard", "Roland", "TR-808", "Ableton",
                   "Bensound", "BenSound", "Ben Sound", "Silent Partner", "Kai Engel", "Free Music Archive", "Audio Library"]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
    return errs


def check_summary():
    return (f"The invented piece is {TOTAL_BARS} bars at {BPM} BPM = {TOTAL_S} s (sections {'+'.join(str(round((b - a) / BAR_S)) for _, a, b in SECTIONS)} bars; "
            f"{len(LAYERS)} layers, 2 of them cut Apple Loops, {len(AUTO)} automation lanes, none flat; peak = {max(DENS)} layers inside the Peak; "
            f"a chord for every bar, ending on C; bell notes and bass roots are chord tones); the word list has {len(WORDS_ALPHA)} words, none added or removed; "
            f"the owner's lists counted (4 goals, 4 terms, 6 requirements, 7 steps, 4 tips, 6 checklist items, 4 struggles, 3 resources); "
            f"{len(CHANGES)} wording changes disclosed; no audio, artist names or student work included; grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
