#!/usr/bin/env python3
"""DMP2 project: Session Player's Studio (TpT 026): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Session Player's Studio > "Session Player's Studio - Project Sheet & Rubric" (rubric 5 categories scored 1-5,
/25, final grade = average of student and teacher scores), TEACHER NOTES > "Session Player's Studio - Teacher Notes" (7 class periods),
and the project's entry on "DMP2 - Project Menu" (the June 2026 menu; owner, 17 Oct 2026: the June entry may be quoted). These three
set the project text, steps, rubric and pacing (owner rule, 17 Oct 2026). The 2025 "Project Outline" in the older folder is not a source.

NO AUDIO IS INCLUDED. The owner's two YouTube resources are not linked or titled (they are third-party videos); his chord-progression
cheat sheet is supplied by this kit as a student page, written from music theory (Roman numerals in five major keys, no song named).
The worked example is an invented 24-bar, 96 BPM piece ("Porch Light") described on paper: three Session Players with different
settings in four sections, a chord for every bar, and an original melody of chord tones. Every picture is drawn in code.
The sheet has no reflection task (the rubric only mentions reflection), so the shared Reflection element is on.
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "session-players-studio"
TITLE = "Session Player’s Studio"
ACCENT = "#1F7A8C"          # this product's single accent: studio teal (025 orchid, 023 horizon orange, 024 magenta)
ACC_LIGHT = "#D3E8EC"
PRICE = "10.00"
CLASSES = 7
REFLECTION = True           # the sheet has no reflection task; the shared Reflection element (owner's definition) is on
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-025).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Session Players Project | Session Player's Studio | High School"
DESC_START = "Logic Pro Session Players project for high school:"
DESC_MUST = ["Session Player", "Drummer", "no audio", "Padlet", "chord progression"]
ZIP_DIR = "Session Players Studio - Hudson Beat"
ZIP_DATE = (2026, 10, 21, 12, 0, 0)
TYPE = "Structured Project"
PROJ_LINE = "Digital Music Production | <i>Structured Project</i> | 7 class periods"
DECK_STRAP = "Build a band without the band"
BANNED_EXTRA = []

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Structured", "Arrangement"
MENU_DESC = "Build a realistic band performance using Logic’s Session Players. Customize groove, complexity, and add your own melody."
OVERVIEW = ("Build a band without the band. Use Logic’s Session Players — Drummer, Bass Player, and Keyboard Player — to create a "
            "realistic live-style arrangement. Customize their style, groove, and complexity, then add your own melody on top.")
GOALS = ["Learn to use Logic’s Session Players (Drummer, Bass, Keyboard)",
         "Adjust style, groove, and complexity to create a realistic performance",
         "Arrange a short piece with an intro, groove, and ending",
         "Add an original melody and mix for a polished final product"]
VOCAB = [("Session Player", "A Logic Pro virtual musician that generates realistic performances based on your settings"),
         ("Groove", "The rhythmic feel of a performance — how tight, loose, or swinging it feels"),
         ("Complexity", "How busy or simple a session player’s part is"),
         ("Chord Progression", "A sequence of chords that provides the harmonic foundation of a piece"),
         ("Arrangement", "How different sections and instruments are organized across the timeline")]
REQS = ["Load and customize at least 3 Session Players",
        "Adjust style, groove, and complexity for each player",
        "Arrange a short piece with a clear intro, groove section, and ending",
        "Add your own original melody over the top",
        "Mix and export a 1-minute live-style production"]
STEPS = ["<b>Set up</b> — Load Drummer, Bass Player, and Keyboard Player into your project (Players sheet: page @PLAYERS)",
         "<b>Choose a chord progression</b> — Borrow one from a song you like or create your own (Chord cheat sheet: page @CHORDS)",
         "<b>Customize</b> — Adjust each session player’s style, groove, and complexity settings (Players sheet: page @PLAYERS)",
         "<b>Arrange</b> — Build an intro, main groove, and ending. Vary the energy between sections. (Arrangement plan: page @ARRANGE)",
         "<b>Add your melody</b> — Record or program an original melody over the top (Melody planner: page @MELODY)",
         "<b>Mix and finalize</b> — Balance levels, apply EQ and effects. Bounce your track. (Mix sheet: page @MIX)",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["Don’t be afraid to change the instrument a session player is using. It creates the notes — you choose the sound.",
        "Need a chord progression? Ask a search engine or an AI chatbot for the chords to a song you like.",
        "Vary the complexity between sections. The intro should feel different from the peak.",
        "The melody is what makes this yours. Spend real time on it."]
FILE_NAME = "“Your Name – Session Player’s Studio”"
CHECK = ["Bounced .mp3 or .wav uploaded to your class page",
         "Zipped .logicx project file uploaded to your class page",
         f"Files named correctly: {FILE_NAME}",
         "At least 3 Session Players used with custom settings",
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
TN_REINFORCES = ("Teaches arrangement, harmonic thinking, and how to build a full production with limited manual input. Great for students "
                 "who struggle with playing instruments.")
STRUGGLES = ["Students leave everything on default settings. Push them to customize style, groove, and complexity.",
             "The melody is an afterthought. Dedicate time specifically to melody writing.",
             "Students don’t vary sections — the whole track sounds the same. Show them how to change Drummer patterns and Bass complexity per section.",
             "Chord progressions intimidate some students. Provide a cheat sheet of common progressions."]
VAR_EASY = "Provide a chord progression and let students focus on arrangement and melody."
VAR_HARD = "Require an original chord progression, a B-section with a different groove, and at least one live-recorded element."
RESOURCES = [("A YouTube video on setting up Session Players in Logic Pro, step by step",
              "Kept as I wrote it, but not included, linked or titled: it is someone else’s video. Choose one to show on Class 1; the Players "
              "sheet (page @PLAYERS) is where students write down what they set."),
             ("A YouTube video on what Logic’s new Session Players can do",
              "Kept as I wrote it, but not included, linked or titled. Pair it with the worked example (pages @EXAMPLE–@EXAMPLE2) to "
              "show how the settings change a section."),
             ("Common chord progressions cheat sheet",
              "This kit supplies one: the Chord cheat sheet (page @CHORDS), made from music theory in five major keys with no song named.")]
TN_NOTE = "This is a great project for students who are less confident with playing but have strong arrangement ideas."
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Creativity &amp; Originality: are style, groove and complexity set on purpose, or left on default (my first struggle)? "
                "The melody is where the student’s own ideas show.",
                "Technical Skill: open the project. Are three Session Players loaded with custom settings (Players sheet, page @PLAYERS), "
                "and are EQ and effects really in use?",
                "Composition &amp; Structure: compare the piece with the Arrangement plan (page @ARRANGE). Does the intro feel different from the "
                "peak (my third struggle)?",
                "Sound Design &amp; Mix Quality: can you hear the melody over the band? Did the student change an instrument (my first tip)?",
                "Documentation &amp; Presentation: the Padlet questions, the Reflection page (page @REFLECT) and the presentation are the evidence."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Introduction. Demo Session Players. Students set up and choose chord progressions.",
     "do": "Slides 1–8: hook, what the project is, the five steps, five words to know, steps 1 and 2 and a four-bar chord loop. Hand out the "
           "project sheet, the Chord cheat sheet and the Players sheet. Demo the three players, then check that each student has a "
           "chord progression before they leave.", "slides": (1, 8),
     "pages": ["chords", "players", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Build a band · five steps · five words · set up and choose chords"},
    {"n": 2, "owner": "<b>Class 2:</b> Customize session players. Begin arranging sections.",
     "do": "Slides 9–10: step 3, customize, and the same players with different settings. Students fill in the Players sheet, then start "
           "on the Arrangement plan.", "slides": (9, 10), "pages": ["players", "arrange"],
     "deck": "Customize style, groove and complexity"},
    {"n": 3, "owner": "<b>Classes 3–5:</b> Working days — arrange, add melody, refine.",
     "do": "Slides 11–13: step 4, how the energy changes over one minute, and the worked example on paper. Then work time on the "
           "Arrangement plan.", "slides": (11, 13), "pages": ["arrange", "example", "example2"],
     "deck": "Working day: arrange, energy, worked example"},
    {"n": 4, "owner": None, "do": "Slide 14: step 5, the melody. Hand out the Melody planner. Dedicate time to melody only, then work time.",
     "slides": (14, 14), "pages": ["melody"], "deck": "Working day: add your melody"},
    {"n": 5, "owner": None, "do": "Slide 15: step 6, mix. Hand out the Mix sheet. Ask each student to play their intro and then their "
     "peak, and say what changed.", "slides": (15, 15), "pages": ["mix"], "deck": "Working day: refine and mix"},
    {"n": 6, "owner": "<b>Class 6:</b> Final mix, bounce. Prepare presentations.",
     "do": "Slides 16–17: what to turn in and the rubric. Students bounce, name their files and post their three Padlet questions.",
     "slides": (16, 17), "pages": ["rubric", "present"], "deck": "Checklist · rubric"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 18–19: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (18, 19), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:9pt">Open Logic, load all three players and press play on the same four chords. Then change one '
    'setting live and ask what changed. Students need to see that the player makes the notes and they choose the sound.</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:9.4pt">Working days; Classes 4 and 5 have one slide each. '
    'Ask: how is your intro different from your peak?</p></div></div>')
PACING_SIZE = 9.2

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (checklist items 1 and 2).",
    "Page numbers are added to steps 1 to 6 (the Players sheet, Chord cheat sheet, Arrangement plan, Melody planner and Mix sheet).",
    "Tip 2 says “Ask a search engine or an AI chatbot” where I named two products, because they are third-party names. No song, artist, "
    "site or link is named anywhere in the kit.",
    "My two YouTube resources are written as “a YouTube video on…” with no title, creator or link, because they are someone else’s videos. "
    "Neither is included.",
    "My third resource, the common chord progressions cheat sheet, is supplied by this kit (page @CHORDS). It is made from music theory, "
    "in Roman numerals and five major keys, with no song named; it is a suggestion, not one of my sheets.",
    "My Easier variation (a given chord progression) and my More Advanced variation (an original progression, a B-section with a "
    "different groove and a live-recorded element) are laid out on page @VARY. No audio is included.",
    "My pacing guide’s “Classes 3–5” row spans the Class 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 3 shortens my overview and goals, slide 6 shortens "
    "my five vocabulary definitions, slide 7 shortens steps 1 and 2, slide 9 shortens step 3 and tip 1, slide 11 shortens step 4 and "
    "my third struggle, slide 14 shortens step 5 and tip 4, slide 15 shortens step 6, slide 16 shortens the submission checklist, and "
    "slide 18 shortens step 7.",
]
CHANGES_MUST_MENTION = ["your class page", "Page numbers", "third-party", "YouTube", "cheat sheet", "Classes 3–5", "Layout only",
                        "intro deck shortens"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the overview, goals, five vocabulary terms, five requirements, "
        "steps (apart from the page numbers), tips (apart from tip 2), checklist (apart from the class page) and file name (“Your "
        "Name – Session Player’s Studio”), the /25 rubric, what the project reinforces, my four struggles, the variations, my "
        "pacing, my closing note and the project menu entry on page @OVERVIEW. No rubric row is added and the "
        "requirements are unchanged.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: the how-to, overview and setup pages, the teacher "
                "moves in the pacing guide, the grading suggestions, the Logic quick reference, the Easier and Harder planning pages, "
                "the worked example (an invented 24-bar piece for three Session Players and a melody, with its chords, settings and "
                "sections, on paper, not audio), the Chord cheat sheet, Players sheet, Arrangement plan, Melody planner and Mix sheet, "
                "the vocabulary and presentation pages and the intro deck. None adds a requirement or a rubric row.")

# ================================================================ chords (music theory, five major keys; no song named)
SCALES = {"C": ["C", "D", "E", "F", "G", "A", "B"], "G": ["G", "A", "B", "C", "D", "E", "F#"], "D": ["D", "E", "F#", "G", "A", "B", "C#"],
          "F": ["F", "G", "A", "Bb", "C", "D", "E"], "A": ["A", "B", "C#", "D", "E", "F#", "G#"]}
DEGREES = [("I", 0, ""), ("ii", 1, "m"), ("iii", 2, "m"), ("IV", 3, ""), ("V", 4, ""), ("vi", 5, "m")]
NUMERAL = {n: (i, q) for n, i, q in DEGREES}
PROGS = [("I – V – vi – IV", "bright and open"), ("vi – IV – I – V", "emotional, rising"), ("I – vi – IV – V", "classic, nostalgic"),
         ("I – IV – V – I", "simple and strong"), ("I – IV – vi – V", "steady, warm"), ("ii – V – I", "smooth, jazzy (3 chords)")]


def chord(key, numeral):
    i, q = NUMERAL[numeral]
    return SCALES[key][i] + q


def prog_chords(key, prog):
    return [chord(key, n.strip()) for n in prog.split("–")]


# the chord tones (letters) of each chord in C major, for the Melody planner
TRIADS_C = [("C", "C E G"), ("Dm", "D F A"), ("Em", "E G B"), ("F", "F A C"), ("G", "G B D"), ("Am", "A C E")]

# ================================================================ the worked example (Hudson Beat original: an invented piece on paper)
PIECE = "Porch Light"
BPM = 96
BAR_S = 240 / BPM            # one 4/4 bar in seconds: 2.5
TOTAL_BARS = 24
TOTAL_S = 60
SECTIONS = [("Intro", 1, 4), ("Groove", 5, 12), ("B-section", 13, 20), ("Ending", 21, 24)]    # inclusive bars
PLAYERS = ["Keyboard Player", "Bass Player", "Drummer"]
# complexity 1 (simple) to 5 (busy), by section; 0 = the player is out. Scale invented for this example.
CX = {"Keyboard Player": [1, 2, 3, 1], "Bass Player": [0, 2, 4, 1], "Drummer": [0, 3, 5, 2]}
PLAYER_BARS = {"Keyboard Player": (1, 24), "Bass Player": (5, 24), "Drummer": (5, 24)}
MELODY_BARS = (9, 23)
CHORD_BARS = ["C", "Am", "F", "G"] + ["C", "Am", "F", "G"] * 2 + ["F", "G", "C", "Am"] * 2 + ["F", "G", "C", "C"]
CHORD_TONES = {"C": {"C", "E", "G"}, "Am": {"A", "C", "E"}, "F": {"F", "A", "C"}, "G": {"G", "B", "D"}}
BASS_ROOT = {"C": "C2", "Am": "A1", "F": "F1", "G": "G1"}
MELODY = {"C": ["E5", "G5"], "Am": ["E5", "C5"], "F": ["C5", "A4"], "G": ["B4", "D5"]}
SETTINGS = [("Keyboard Player", "I changed the sound from piano to a soft electric piano.",
             "Style: gentle chords. Groove: straight and loose. Complexity: 1, then 2, then 3 in the B-section, then 1 again."),
            ("Bass Player", "I kept a round electric bass.",
             "Style: follows the chord roots. Groove: locked to the kick. Complexity: out for the intro, 2, then 4 in the B-section, then 1."),
            ("Drummer", "I changed the kit to a soft, roomy one.",
             "Style: a pop-rock beat. Groove: straight, slightly behind the beat. Complexity: out for the intro, 3, then 5 in the "
             "B-section with a fill at bar 12, then 2.")]
WEAK = "I will load three players and press play."
STRONG = ("My piece is 24 bars at 96 BPM, which is 60 seconds, in the key of C. The chords are C, Am, F and G, and the B-section changes "
          "to F, G, C and Am. The Keyboard Player starts alone in the intro. The Bass Player and Drummer join at bar 5 for the groove. "
          "In the B-section the Drummer and Bass get busier and the groove changes. My melody comes in at bar 9 and uses chord tones. "
          "The ending thins out to a single C.")
SECTION_NOTES = [("Intro", "bars 1–4", "Keyboard Player alone, simple (1); one chord a bar, C, Am, F, G"),
                 ("Groove", "bars 5–12", "Bass Player and Drummer join at bar 5; the same four chords twice; my melody joins at bar 9"),
                 ("B-section", "bars 13–20", "all three players busier (3, 4, 5); new chords F, G, C, Am twice; a fill at bar 12 leads in"),
                 ("Ending", "bars 21–24", "players thin out (1, 1, 2); F, G, then C for two bars; the melody ends on a held E in bar 23")]
THIN = ("My song has a drummer and a bass and keys. I made a melody and it sounds good. I like how it turned out and I think it is a good "
        "band. I used the default settings.")
USEFUL = ("I used the Drummer, Bass Player and Keyboard Player and changed all three away from default. In the intro only the keys play, "
          "simple, so it feels small. In the B-section the Drummer is at 5 and the Bass is at 4, so it feels like the peak. My melody uses "
          "chord tones on the strong beats. Next time I would try a different groove in the ending.")
QUESTIONS = ["Which player did you notice first, and when?",
             "Where did the music feel biggest, and what made it feel that way?",
             "What would you change in the melody so it stands out more?"]


def active(player, bar):
    a, b = PLAYER_BARS[player]
    return a <= bar <= b


def sec_index(bar):
    return next(i for i, (_n, a, b) in enumerate(SECTIONS) if a <= bar <= b)


def level(player, bar):
    return CX[player][sec_index(bar)] if active(player, bar) else 0


def energy(bar):
    return sum(level(p, bar) for p in PLAYERS)


ENERGY = [energy(b) for b in range(1, TOTAL_BARS + 1)]


def sec_name(bar):
    return SECTIONS[sec_index(bar)][0]


def bars_for(sec, bpm):
    return sec * bpm / 240


# ================================================================ drawings (original, code-drawn: black + accent only)
GREY = "#bdbdbd"


def stacked(x0, y_base, w, h, name, show_nums=False, cs=20):
    """Stacked bars: complexity of each Session Player in each bar. Returns svg parts."""
    cw = w / TOTAL_BARS
    top = max(ENERGY)
    unit = h / top
    fills = {"Keyboard Player": GREY, "Bass Player": "#000", "Drummer": ACCENT}
    out = []
    for bar in range(1, TOTAL_BARS + 1):
        y = y_base
        for p in PLAYERS:
            hh = level(p, bar) * unit
            if hh:
                y -= hh
                out.append(f'<rect x="{x0 + (bar - 1) * cw + 2:.1f}" y="{y:.1f}" width="{cw - 4:.1f}" height="{hh - 2:.1f}" rx="3" fill="{fills[p]}"/>')
    return "".join(out)


def hero_body():
    W, H = 1100, 470
    out = []
    pw, gap = 320, 30
    x0 = (W - 3 * pw - 2 * gap) / 2
    for i, nm in enumerate(["Drummer", "Bass Player", "Keyboard Player"]):
        x = x0 + i * (pw + gap)
        out.append(f'<rect x="{x:.1f}" y="6" width="{pw}" height="78" rx="39" fill="{ACCENT if i == 0 else "#000"}"/>')
        out.append(D.t_(x + pw / 2, 6 + 39 + 11, nm.upper(), 30, 700, fill_="#fff"))
        D.lab("hero names", nm.upper(), 30, pw - 50)
        cx = x + pw / 2
        out.append(f'<line x1="{cx:.1f}" y1="92" x2="{cx:.1f}" y2="150" stroke="#000" stroke-width="5" stroke-dasharray="3 10" stroke-linecap="round"/>')
        out.append(f'<polygon points="{cx - 16:.1f},146 {cx + 16:.1f},146 {cx:.1f},176" fill="#000"/>')
    bx, bw, by, bh = 60, 980, 190, 200
    out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="16" fill="#fff" stroke="#000" stroke-width="4"/>')
    out.append(stacked(bx + 20, by + bh - 14, bw - 40, bh - 40, "hero"))
    out.append(D.t_(bx, by + bh + 52, "0:00", 28, 500, anchor="start"))
    out.append(D.t_(bx + bw, by + bh + 52, "1:00", 28, 500, anchor="end"))
    cap = "THREE PLAYERS · ONE MINUTE · YOUR MELODY"
    out.append(D.t_(bx + bw / 2, by + bh + 52, cap, 28, 700))
    D.lab("hero cap", cap, 28, 700)
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
    return cards_body([("Set up", "3 players"), ("Choose", "the chords"), ("Customize", "style · groove"), ("Arrange", "sections"),
                       ("Melody", "your own")], "Then mix, bounce, present and get feedback", W, name, fs, cs, True)


def chords_body(W=1600, name="chords pic", cs=24):
    """The example's four-bar loop: one chord a bar, with its Roman numeral."""
    items = [("C", "I"), ("Am", "vi"), ("F", "IV"), ("G", "V")]
    gap = 74
    pw = (W - 3 * gap) / 4
    bh = 210
    out = []
    for k, (c, num) in enumerate(items):
        x0 = k * (pw + gap)
        out.append(f'<rect x="{x0:.1f}" y="4" width="{pw:.1f}" height="{bh}" rx="14" fill="{"#000" if k % 2 == 0 else ACCENT}"/>')
        out.append(D.t_(x0 + pw / 2, 4 + 112, c, 100, 700, fill_="#fff"))
        D.lab(name + " chords", c, 100, pw - 40)
        out.append(D.t_(x0 + pw / 2, 4 + 170, f"{num} · bar {k + 1}", 34, 500, fill_="#fff"))
        D.lab(name + " numerals", f"{num} · bar {k + 1}", 34, pw - 40)
        if k < 3:
            ax, ay = x0 + pw + 10, 4 + bh / 2
            out.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{ax + gap - 36:.1f}" y2="{ay:.1f}" stroke="#000" stroke-width="6" stroke-linecap="round"/>')
            out.append(f'<polygon points="{ax + gap - 16:.1f},{ay:.1f} {ax + gap - 40:.1f},{ay - 15:.1f} {ax + gap - 40:.1f},{ay + 15:.1f}" fill="#000"/>')
    cap = "Four bars, one chord each, then repeat. This is the loop under “Porch Light”."
    out.append(D.t_(W / 2, bh + 62, cap, cs + 2, 500))
    D.lab(name + " cap", cap, cs + 2, W - 20)
    return "".join(out), W, bh + 80


def settings_body(W=1600, name="settings pic", cs=24):
    """Same three players, different complexity in each section (the worked example)."""
    lx = 270
    gap = 20
    cw = (W - lx - 3 * gap - 4) / 4
    out = []
    for i, (nm, _a, _b) in enumerate(SECTIONS):
        x = lx + i * (cw + gap)
        out.append(f'<rect x="{x:.1f}" y="4" width="{cw:.1f}" height="64" rx="32" fill="{ACCENT if nm == "B-section" else "#000"}"/>')
        out.append(D.t_(x + cw / 2, 4 + 32 + 10, nm.upper(), 28, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), 28, cw - 30)
    rh, rg = 96, 16
    for r, p in enumerate(PLAYERS):
        y = 84 + r * (rh + rg)
        out.append(D.t_(lx - 18, y + rh / 2 + 8, p.upper(), cs, 700, anchor="end"))
        D.lab(name + " rows", p.upper(), cs, lx - 30)
        for i in range(4):
            x = lx + i * (cw + gap)
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{rh}" rx="12" fill="#fff" stroke="#000" stroke-width="3"/>')
            v = CX[p][i]
            if v == 0:
                out.append(D.t_(x + cw / 2, y + rh / 2 + 8, "OUT", cs, 700, fill_="#777"))
            else:
                for d_ in range(5):
                    cx = x + cw / 2 + (d_ - 2) * 44
                    out.append(f'<circle cx="{cx:.1f}" cy="{y + rh / 2:.1f}" r="15" fill="{ACCENT if d_ < v else "#fff"}" stroke="#000" stroke-width="3"/>')
    hh = 84 + 3 * (rh + rg)
    cap = "Complexity from 1 (simple) to 5 (busy), by section: an invented example"
    out.append(D.t_(W / 2, hh + 14, cap, cs + 2, 500))
    D.lab(name + " cap", cap, cs + 2, W - 20)
    return "".join(out), W, hh + 30


def arc_body(W=1600, name="arc pic", fs=26, cs=22):
    """Stacked complexity of the three players in each of the example's 24 bars."""
    lx = 8
    pw = W - 2 * lx
    cw = pw / TOTAL_BARS
    bh = 300
    y0 = 78
    out = []
    shade = {"Intro": "#4a4a4a", "Groove": "#000", "B-section": ACCENT, "Ending": "#4a4a4a"}
    for nm, a, b in SECTIONS:
        xa, xb = lx + (a - 1) * cw, lx + b * cw
        out.append(f'<rect x="{xa + 2:.1f}" y="2" width="{xb - xa - 4:.1f}" height="52" rx="8" fill="{shade[nm]}"/>')
        out.append(D.t_((xa + xb) / 2, 2 + 26 + fs * .32, nm.upper(), fs, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs, xb - xa - 12)
    out.append(f'<line x1="{lx}" y1="{y0 + bh}" x2="{lx + pw}" y2="{y0 + bh}" stroke="#000" stroke-width="5" stroke-linecap="round"/>')
    out.append(stacked(lx, y0 + bh, pw, bh - 20, name))
    for i in range(TOTAL_BARS):
        if i % 4 == 0 or i == TOTAL_BARS - 1:
            out.append(D.t_(lx + i * cw + cw / 2, y0 + bh + 30, str(i + 1), cs - 2, 500))
    ky = y0 + bh + 74
    kx = 8
    for p, f_ in (("Keyboard Player", GREY), ("Bass Player", "#000"), ("Drummer", ACCENT)):
        out.append(f'<rect x="{kx}" y="{ky - 17}" width="30" height="22" rx="5" fill="{f_}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(kx + 42, ky + 1, p, cs, 500, anchor="start"))
        D.lab(name + " key", p, cs, 260)
        kx += 330
    cap = "How busy the three players are in each of the 24 bars"
    out.append(D.t_(W / 2, ky + 44, cap, cs + 2, 500))
    D.lab(name + " cap", cap, cs + 2, W - 20)
    return "".join(out), W, ky + 62


def map_body(W=1600, name="map", fs=24, ts=20):
    gx = 250
    pwid = W - gx - 16
    cw = pwid / TOTAL_BARS
    out = []
    sh = 54
    shade = {"Intro": "#4a4a4a", "Groove": "#000", "B-section": ACCENT, "Ending": "#4a4a4a"}
    for nm, a, b in SECTIONS:
        xa, xb = gx + (a - 1) * cw, gx + b * cw
        out.append(f'<rect x="{xa + 2:.1f}" y="2" width="{xb - xa - 4:.1f}" height="{sh}" rx="8" fill="{shade[nm]}"/>')
        out.append(D.t_((xa + xb) / 2, sh / 2 + fs * .3 + 2, nm.upper(), fs - 4, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 4, xb - xa - 10)
    y = sh + 12
    out.append(D.t_(gx - 14, y + 25, "CHORDS", 20, 700, anchor="end"))
    for i, c in enumerate(CHORD_BARS):
        out.append(f'<rect x="{gx + i * cw:.1f}" y="{y}" width="{cw:.1f}" height="34" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        out.append(D.t_(gx + i * cw + cw / 2, y + 25, c, 20, 700))
        D.lab(name + " chords", c, 20, cw - 6)
    lh, lg = 46, 8
    y0 = y + 34 + 14
    rows = PLAYERS + ["Melody"]
    for r, nm in enumerate(rows):
        yy = y0 + r * (lh + lg)
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, nm.upper(), 20, 700, anchor="end"))
        D.lab(name + " lanes", nm.upper(), 20, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        if nm == "Melody":
            a, b = MELODY_BARS
            out.append(f'<rect x="{gx + (a - 1) * cw + 2:.1f}" y="{yy + 5}" width="{(b - a + 1) * cw - 4:.1f}" height="{lh - 10}" rx="6" fill="{ACC_LIGHT}" stroke="{ACCENT}" stroke-width="2.5"/>')
            out.append(D.t_(gx + (a - 1) * cw + (b - a + 1) * cw / 2, yy + lh / 2 + 7, "I wrote this", 20, 500))
            D.lab(name + " lane words", "I wrote this", 20, (b - a + 1) * cw - 12)
        else:
            for i, (sn, a, b) in enumerate(SECTIONS):
                v = CX[nm][i]
                if not v:
                    continue
                out.append(f'<rect x="{gx + (a - 1) * cw + 2:.1f}" y="{yy + 5}" width="{(b - a + 1) * cw - 4:.1f}" height="{lh - 10}" rx="6" fill="#bdbdbd" stroke="#000" stroke-width="2"/>')
                out.append(D.t_(gx + (a - 1) * cw + (b - a + 1) * cw / 2, yy + lh / 2 + 8, str(v), 24, 700))
    ty = y0 + len(rows) * (lh + lg) + 4
    for bar in (1, 5, 9, 13, 17, 21, 24):
        xx = gx + (bar - 1) * cw + cw / 2
        out.append(D.t_(xx, ty + 24, str(bar), ts, 500))
    out.append(D.t_(gx - 14, ty + 24, "BAR", 18, 700, anchor="end"))
    ky = ty + 62
    out.append(f'<rect x="{gx}" y="{ky - 17}" width="30" height="22" rx="5" fill="#bdbdbd" stroke="#000" stroke-width="2"/>')
    out.append(D.t_(gx + 42, ky + 1, "Session Player (number = complexity)", ts, 500, anchor="start"))
    D.lab(name + " key", "Session Player (number = complexity)", ts, 420)
    out.append(f'<rect x="{gx + 480}" y="{ky - 17}" width="30" height="22" rx="5" fill="{ACC_LIGHT}" stroke="{ACCENT}" stroke-width="2"/>')
    out.append(D.t_(gx + 522, ky + 1, "my own melody", ts, 500, anchor="start"))
    D.lab(name + " key", "my own melody", ts, 260)
    return "".join(out), W, ky + 18


DRAWINGS = {"hero": lambda: D.stack([hero_body()], 40), "cycle": lambda: cycle_body(1600), "chords": lambda: chords_body(1600),
            "settings": lambda: settings_body(1600), "arc": lambda: arc_body(1600), "arrange": lambda: map_body(1600, "arrange pic")}
DRAWING_PX = {"hero": 1900, "cycle": 2000, "chords": 2000, "settings": 2000, "arc": 2000, "arrange": 2000}
SIDE = {"cycle": ["Load three Session Players", "Choose a chord progression", "Customize, then arrange", "Add your melody, mix, present"],
        "chords": ["An invented loop, on paper", "One chord for each bar", "Repeat it under every section", "Change it in the B-section"],
        "settings": ["Same players in every section", "The settings are what change", "Keys are simple in the intro", "The B-section is the busiest"],
        "arc": ["An invented piece, on paper", "Small intro, bigger groove", "The B-section is the peak", "The ending thins out"],
        "arrange": ["An invented 60-second piece", "Four sections you can name", "A chord for every bar", "Your melody sits on top"]}


def label_extras():
    map_body(1250, "page arrange", 24, 20)
    cycle_body(1250, "page cycle", 28, 20)
    chords_body(1250, "page chords", 24)
    settings_body(1250, "page settings", 24)
    arc_body(1250, "page arc", 26, 22)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Session Player’s Studio", "Build a band without the band.",
     "Class 1, the first minute. No audio is included in this deck. Open with my overview: build a band without the band. Use Logic’s "
     "Session Players, Drummer, Bass Player, and Keyboard Player, to create a realistic live-style arrangement. Customize their style, "
     "groove, and complexity, then add your own melody on top."),
    (1, "listen", "Think: what does a band do?", "Think, then share|Teacher: describe a band playing the same slow song twice, first quietly and simply, then "
     "loud and busy. No audio is needed.|What did the drummer change?|What stayed the same?|Who wrote the melody?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker; describe one band and one song in two "
     "ways and let students imagine them. This sets up my goal that students adjust style, groove and complexity to create a realistic "
     "performance, and my teacher note that this project suits students who are less confident playing but have strong arrangement ideas."),
    (1, "bullets", "What is Session Player’s Studio?", "Build a band without the band|Drummer, Bass Player and Keyboard Player|Customize style, "
     "groove and complexity|Add your own melody on top",
     "My overview and goals, shortened to fit the slide. Build a band without the band: use Logic's Session Players, Drummer, Bass Player "
     "and Keyboard Player, to create a realistic live-style arrangement, customize their style, groove and complexity, then add your own "
     "melody on top. My goals are to learn to use the Session Players, adjust style, groove and complexity to create a realistic "
     "performance, arrange a short piece with an intro, groove and ending, and add an original melody and mix for a polished final product."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: introduction, demo Session Players, and students set up and choose chord "
     "progressions. Class 2: customize the session players and begin arranging sections. Classes 3 to 5 are working days: arrange, add "
     "melody, refine. Class 6: final mix, bounce and prepare presentations. Class 7: presentations with Padlet Q and A peer feedback."),
    (1, "pic", "Five steps, then finish", "cycle",
     "Class 1. The first five steps of my project sheet, in order: set up, choose a chord progression, customize, arrange and add your "
     "melody. Then students mix and finalize, and present with Padlet feedback. Point to each box and say roughly when it happens: set "
     "up and chords today, customizing tomorrow, arranging and the melody on the working days. The step names are mine; the picture "
     "and its short labels are the kit's own."),
    (1, "bullets", "Five words to know", "Session Player: a virtual musician that plays for you|Groove: how tight, loose or swinging it "
     "feels|Complexity: how busy or simple a part is|Chord progression: the chords under a piece|Arrangement: how sections and "
     "instruments are laid out",
     "My five vocabulary terms, shortened to fit the slide. Session Player: a Logic Pro virtual musician that generates realistic "
     "performances based on your settings. Groove: the rhythmic feel of a performance, how tight, loose or swinging it feels. Complexity: how "
     "busy or simple a session player's part is. Chord progression: a sequence of chords that provides the harmonic foundation of a "
     "piece. Arrangement: how different sections and instruments are organized across the timeline. The full definitions are on the "
     "vocabulary page."),
    (1, "steps", "Steps 1 and 2: set up, choose chords", "Load Drummer, Bass Player and Keyboard Player|Borrow a chord progression or "
     "make your own|Stuck? Start from the Chord cheat sheet|Write your chords on the Arrangement plan",
     "Steps 1 and 2 of the project sheet, shortened to fit the slide. Step 1, set up: load Drummer, Bass Player, and Keyboard Player "
     "into your project. Step 2: choose a chord progression, borrow one from a song you like or create your own. The last two lines "
     "are the kit's own suggestions, not my steps: the Chord cheat sheet answers my fourth struggle, that chord progressions intimidate "
     "some students, and the Arrangement plan has a row for the chords. Demo loading all three players live."),
    (1, "pic", "A four-bar chord loop", "chords",
     "Class 1. A kit picture, not from my sheets: the four chords under the invented worked example, C, A minor, F and G, one chord for each "
     "bar, then repeat. The Roman numerals I, vi, IV and V are on the Chord cheat sheet in five keys. Ask students to say the chords "
     "aloud with you, one a bar, and then show them how to type the chords into the project. Nothing here is audio."),
    (2, "steps", "Step 3: customize", "Adjust each player’s style, groove and complexity|You can change the instrument a player uses|The "
     "player makes the notes; you choose the sound|Write your settings on the Players sheet",
     "Step 3 of the project sheet and tip 1, shortened to fit the slide. Customize: adjust each session player's style, groove, and "
     "complexity settings. My first tip: don't be afraid to change the instrument a session player is using, because it creates the notes "
     "and you choose the sound. My first struggle is students who leave everything on default, so push them to customize. The last line "
     "is the kit's own suggestion: the Players sheet is where they record what they set."),
    (2, "pic", "Same players, different settings", "settings",
     "Class 2. A kit picture of an invented piece: the same three Session Players in four sections, each with a different complexity from "
     "1, simple, to 5, busy. The Keyboard Player is alone and simple in the intro, and the Drummer is at 5 in the B-section. Ask students "
     "which section would feel biggest and why. The scale from 1 to 5 is the kit's own, so that settings can be talked about; Logic "
     "shows them with its own controls. Nothing here is audio."),
    (3, "steps", "Step 4: arrange", "Build an intro, main groove and ending|Vary the energy between sections|Change Drummer patterns "
     "and Bass complexity per section|Plan it on the Arrangement plan",
     "Step 4 of the project sheet and my third struggle, shortened to fit the slide. Arrange: build an intro, main groove, and ending, and "
     "vary the energy between sections. My third struggle is students who don't vary sections, so the whole track sounds the same; show "
     "them how to change Drummer patterns and Bass complexity per section. The last line is the kit's own suggestion: the Arrangement plan "
     "is where they decide it on paper first."),
    (3, "pic", "Energy over one minute", "arc",
     "Class 3, the first working day after the settings. A kit picture of an invented piece: how busy the three players are in each of 24 "
     "bars. The intro is small, the groove is bigger, the B-section is the peak and the ending thins out. My tip 3 is to vary the "
     "complexity between sections so the intro feels different from the peak. Students can plan their own on the Arrangement plan."),
    (3, "pic", "Worked example: 60 seconds", "arrange",
     "Class 3. An invented piece, Porch Light, described on paper; nothing here is audio. It is 24 bars at 96 BPM, which is 60 seconds, in "
     "four sections. Three Session Players come in and out with different complexity, there is a chord for every bar, and an "
     "original melody comes in at bar 9. The numbers, the settings and the weak and clear plans are on the worked example pages."),
    (4, "bullets", "Step 5: add your melody", "Record or program an original melody|The melody is what makes this yours|Spend real time "
     "on it|Use chord tones on the strong beats",
     "Step 5 and tip 4, shortened to fit the slide. Add your melody: record or program an original melody over the top. My fourth tip: the "
     "melody is what makes this yours, so spend real time on it. My second struggle is that the melody is an afterthought, so dedicate "
     "this class to melody writing. The last line is the kit's own suggestion; the Melody planner lists the chord tones."),
    (5, "bullets", "Step 6: mix and finalize", "Balance levels|Apply EQ and effects|Bounce your track|Can you hear your melody over the band?",
     "Step 6, shortened to fit the slide: mix and finalize. Balance levels, apply EQ and effects, and bounce your track. The last line is "
     "the kit's own question for the Mix sheet: close your eyes and listen for the melody. Ask each student to play their intro and then "
     "their peak, and say what changed."),
    (6, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Session Player’s Studio|At least 3 "
     "Session Players with custom settings|Padlet post with 3 questions|Answer 2 questions on classmates’ posts",
     "The submission checklist from the project sheet, shortened to fit the slide. Show where students upload (your class page) and "
     "where the Padlet board is. The file name is Your Name, then Session Player's Studio. Check that every student has at least three "
     "Session Players with custom settings before they bounce."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play your track; name your three players|Say what you changed in the intro and the peak|Your Padlet "
     "post: 3 questions about your project|Answer at least 2 of each classmate’s 3",
     "Class 7, presentations with Padlet Q and A. Step 7 of the project sheet, shortened to fit the slide: create your own Padlet post "
     "with 3 questions you want classmates to answer, present to the class, and during classmates' presentations answer at least 2 of "
     "their 3 questions. The first two lines are the kit's own suggestions. Ask the class to name the chord progression before the "
     "presenter does."),
    (7, "closer", "One last thing…", "You built a band.|You shaped every part.|You wrote the melody.|Now press play.",
     "Close with my teacher note: this is a great project for students who are less confident with playing but have strong arrangement "
     "ideas. Ask a few students which player they changed the most. Tell them the next project starts from the menu."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("example", "Worked example", "an invented piece on paper"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 8, 10, 12, 17]
SHOTS3 = [("example", "Worked example"), ("chords", "Chord cheat sheet"), ("players", "Players sheet"), ("arrange", "Arrangement plan"),
          ("melody", "Melody planner"), ("mix", "Mix sheet"), ("setup", "Setup"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "changes", "logicref", "vary", "example", "example2",
        "chords", "players", "arrange", "melody", "mix", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "example", "chords", "rubric"]

COVER_A = "Build a band without the band"
COVER_C = "DMP2 · arrangement · intro slides"
PDF_COVER = dict(a=30, b=44, c=14, art=7.0)
SQ_COVER = dict(a=44, b=134, c=27, art=520, gap=30)
SQ_B_LINES = ["Session", "Player’s", "Studio"]
SQ_SUB = "7 class periods · 3 session players · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "chord cheat sheet, players sheet, arrangement plan, melody planner", 28)}
SQ_BANDS = {1: "Set up <em>·</em> customize <em>·</em> arrange <em>·</em> melody <em>·</em> mix",
            2: "Hook <em>·</em> chords <em>·</em> settings <em>·</em> energy <em>·</em> melody",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, video, songs, artists or albums are named or included. Students make every sound in their tracks themselves, "
             "from the Session Players, instruments and sounds in Logic.")
CREDITS = ["Worked example (an invented 24-bar piece for three Session Players and a melody, with its chords, settings and sections, "
           "described on paper), the Chord cheat sheet (written from music theory), the hero, card, chord, settings, energy and "
           "arrangement drawings and layouts: original work, Hudson Beat.",
           "No audio, video, lyrics, album art, screenshots, presets, templates, links or chart data are included. No student work is "
           "included. Padlet is named only as the owner’s own materials name it."]
LOGIC_INTRO = ("Where to find the tools a Session Player’s Studio project is likely to use. Demonstrate what your class needs on Classes 1 and 2 "
               "and then let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add tracks with Track › New Tracks…. Choose Drummer, then add a Bass Player "
              "and a Keyboard Player from the same menu."),
             ("Session Players", "Each player has its own editor: choose a style, then set how loud or soft and how simple or complex it plays. "
              "Drummer also has groove and fill controls. The player creates the notes; you choose the sound."),
             ("Change the sound", "In the Library, choose a different instrument or kit for a player (my first tip). The part stays; the "
              "sound changes."),
             ("Chords", "Show Global Tracks (G) and use the Chord track to type in the chords, one a bar, so Bass Player and Keyboard "
              "Player follow them. Or let the Keyboard Player play from the chords you give it."),
             ("Tempo and length", "Set the tempo in the control bar. Bars × 240 ÷ tempo = seconds; at 96 BPM, 24 bars is 60 seconds. "
              "The Arrangement plan has a length helper."),
             ("Sections", "Add arrangement markers named Intro, Groove, B-section and Ending. In each section, change a player’s "
              "complexity or mute it to vary the energy (my third struggle)."),
             ("Your melody", "Record a Software Instrument with a MIDI keyboard or the on-screen keyboard, or program notes in the Piano "
              "Roll. Keep to the chord tones on the strong beats (Melody planner)."),
             ("Live-recorded element (Harder)", "Add an Audio track and record a voice or an instrument through a microphone. Wear "
              "headphones so the band does not leak into the recording."),
             ("EQ, pan, plug-ins", "Add Channel EQ for balance, use each track's Pan knob, and add effects such as a reverb. Press X for "
              "the Mixer."),
             ("Bounce and zip", "File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and "
              "choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and zipped .logicx submitted",
                 "At least 3 Session Players with custom settings (Players sheet, page @PLAYERS)", "Padlet post created with my 3 questions",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my track:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12.2pt;margin-bottom:3pt">Default settings: the Players sheet (page @PLAYERS) asks for a style, groove and complexity for every player.</li>'
    '<li style="font-size:12.2pt;margin-bottom:3pt">An afterthought melody: Class 4 and the Melody planner (page @MELODY) give it a class of its own.</li>'
    '<li style="font-size:12.2pt;margin-bottom:3pt">Sections that sound the same: slide 12 and the Arrangement plan (page @ARRANGE), with the worked example (page @EXAMPLE2).</li>'
    '<li style="font-size:12.2pt;margin-bottom:0">Chords that intimidate: the Chord cheat sheet (page @CHORDS), in five keys.</li></ul></div>'
    '<div class="box" style="margin-top:6pt"><span class="k">Where this kit helps with the variations (kit suggestion)</span><ul style="margin:0">'
    '<li style="font-size:12.2pt;margin-bottom:3pt">Easier: a given progression and a section plan to fill in (page @VARY).</li>'
    '<li style="font-size:12.2pt;margin-bottom:0">More advanced: planning pages for an original progression, a B-section and a live-recorded element (page @VARY).</li></ul></div>')
TN1_SIZE = 14.4
PROJ_SIZE = 13.2
VOCAB_GAP = 14
CHANGES_SIZE = 9.8
LOGIC_SIZE = 10.4
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""

CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; } table.sg td, table.sg th { border: 1pt solid #000; text-align: center; "
          "padding: 0; font-size: 8pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.2in; font-size: 9pt; } "
          "table.sg td.b { border-left: 2.2pt solid #000; } table.sg td.on { background: " + ACCENT + "; } </style>")


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, what changed, Logic quick "
              "reference, Easier and Harder variations, worked example (2 pages)"),
             ("Student pages", "chords", "reflect", "Chord cheat sheet, Players sheet, Arrangement plan, Melody planner, Mix sheet, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period structured project for high school music '
             f'technology. Each student builds a one-minute, live-style band arrangement in Logic with three Session Players: Drummer, '
             f'Bass Player and Keyboard Player. They choose a chord progression, customize each player’s style, groove and complexity, '
             f'arrange an intro, groove section and ending, add an original melody, mix it, and present it with Padlet questions for '
             f'feedback. It is the project from my Digital Music Production 2 course (type: structured; focus: arrangement), and the '
             f'projects in that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Set up the Presentation Padlet and open Logic to try the three players (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("chords")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}: a given chord progression, or an original progression, a B-section and a live-recorded element (both laid out on page {D.IX("vary")}).</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Chords:</b> students choose their own progression; the cheat sheet (page {D.IX("chords")}) is there when they are stuck.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'a band is a set of choices, and that the player makes the notes while they choose the sound.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13.4pt;line-height:1.5">One original, live-style production about one minute long. Three Session '
             f'Players (Drummer, Bass Player and Keyboard Player) play a chord progression the student chooses, each with its own style, '
             f'groove and complexity. The piece has a clear intro, groove section and ending, with the energy varied between sections, '
             f'and the student’s own melody on top. It is mixed with EQ and effects. They hand in a bounced .mp3 or .wav and the zipped '
             f'.logicx project, plus a Padlet post with three feedback questions, then present the piece.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:13pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:12pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:13pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.6pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: set up and chords, customize, three working days, mix and bounce, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Session Players (Drummer, Bass Player, Keyboard Player), arrangement, EQ and effects, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with a current Logic Pro, headphones, a feedback board and a place to submit files</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:12pt">Students should already '
             f'know how to open a project, add software instruments, use the Mixer, and save, bounce and zip in Logic. Nobody '
             f'needs to read music or play an instrument.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Structured", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 13.2pt; line-height: 1.5; margin-bottom: 9pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with a current Logic Pro</b> for each student, and <b>headphones</b>. Session Players are part of recent versions of Logic Pro, so check yours before Class 1.</li>'
             f'<li><b>A place to submit</b> the .mp3 or .wav and the zipped .logicx (your class page).</li>'
             f'<li><b>The Presentation Padlet</b>, set up before Class 1 (yours to set up; none is included).</li>'
             f'<li><b>The Chord cheat sheet</b>, printed (page {D.IX("chords")}).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("chords")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:13pt;margin-bottom:11pt") for c in [
                 "Set up the Presentation Padlet in your class page.",
                 "Open Logic on a student computer and load Drummer, Bass Player and Keyboard Player.",
                 "Choose the two YouTube videos you might show (my resources, page @TN2).".replace("@TN2", str(D.IX("tn2"))),
                 "Decide how you will treat the live-recorded element in the Harder variation (page @VARY).".replace("@VARY", str(D.IX("vary")))]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch (my struggles)", True)}'
             f'<p style="font-size:12pt">Students leave everything on default, the melody is an afterthought, sections sound the same, and chord '
             f'progressions intimidate some students. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Kit suggestions, not part of my sheets</span><ul style="margin:0">'
             f'<li style="font-size:11.6pt">Ask while students work: what did you change on this player? How is your intro different from your peak?</li>'
             f'<li style="font-size:11.6pt">Have students play the same four chords with three different drum settings and say which feels like which section.</li>'
             f'<li style="font-size:11.6pt">Give the melody a class of its own (Class 4), as my second struggle suggests.</li></ul></div>'
             f'{D.H2("Original work")}'
             f'<div class="box"><span class="k">A kit suggestion</span><p style="margin:0;font-size:11.4pt;line-height:1.42">'
             f'Students may borrow a chord progression (step 2) but not a melody or a recording. They write their own melody and hand '
             f'in only their own track.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.4pt;line-height:1.42">'
             f'A full band in headphones can get loud. Tell students to start low and to check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


def vary_page(n, wm=False):
    prog = ["C", "Am", "F", "G"]
    cells = "".join(f"<td style='height:30pt;font-size:13pt'><b>{c}</b></td>" for c in prog)
    secrows = "".join(f"<tr><td style='height:26pt'><b>{a}</b></td><td></td><td></td></tr>"
                      for a in ("Intro", "Groove", "B-section", "Ending"))
    inner = (f'<style>.sb2 li {{ font-size: 11.2pt; line-height: 1.36; margin-bottom: 4pt; }}</style>'
             f'<p style="margin:0 0 3pt;font-size:11.2pt;line-height:1.4">My Easier variation: provide a chord progression and let students '
             f'focus on arrangement and melody. The progression below is the kit’s own (it is not one of my sheets). Hand it out as is, or '
             f'choose one from the Chord cheat sheet (page {D.IX("chords")}).</p>'
             f'{D.H2("Easier: a given chord progression and a plan to fill in", True)}'
             f'<div class="cols" style="gap:12pt"><div><table class="t" style="text-align:center"><tr><th colspan="4">Given: key of C, one chord a bar, repeat</th></tr>'
             f'<tr>{cells}</tr><tr><td>bar 1</td><td>bar 2</td><td>bar 3</td><td>bar 4</td></tr></table>'
             f'<p style="margin:3pt 0 0;font-size:9.6pt">At 96 BPM, 24 bars = 60 seconds (length helper, page {D.IX("arrange")}).</p></div>'
             f'<div class="box acc-b"><span class="k">How to use it</span><ol class="sb2" style="margin:0"><li>Load the three players and type the chords in.</li>'
             f'<li>Fill in the plan below: the bars, and which players play in each section.</li>'
             f'<li>Spend the saved time on the arrangement and the melody.</li></ol></div></div>'
             f'<table class="map" style="margin-top:5pt"><tr><th style="width:18%">Section</th><th style="width:22%">Bars</th><th>Which players, and how busy</th></tr>{secrows}</table>'
             f'{D.H2("More advanced: original chords, a B-section and a live-recorded element")}'
             f'<p style="margin:0 0 3pt;font-size:11.2pt;line-height:1.4">My More Advanced variation. Plan it here, then build it in Logic. No audio is included.</p>'
             f'<div class="fl" style="margin:3pt 0"><b>My original progression (the chords, one a bar):</b><span></span></div>'
             f'<div class="fl" style="margin:3pt 0"><b>My B-section groove (what changes on the Drummer and Bass):</b><span></span></div>'
             f'<div class="fl" style="margin:3pt 0"><b>My live-recorded element (what, where it plays, how I record it):</b><span></span></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">Check</span>'
             + D.chk("The B-section sounds different from the groove: I can name two things that changed.", 12, "font-size:10.8pt;margin-bottom:3pt")
             + D.chk("The live-recorded element is clear and does not fight the melody.", 12, "font-size:10.8pt;margin-bottom:3pt")
             + D.chk("I wrote the chords myself and can name each one.", 12, "font-size:10.8pt;margin-bottom:0") + '</div>')
    return D.page("Easier and Harder variations", "TEACHER", "Easier + Harder", inner, n, key="vary")


def example_page(n, wm=False):
    tbl = "".join(f"<tr><td style='width:21%'><b>{a}</b></td><td style='width:15%'>{b}</td><td>{c}</td></tr>" for a, b, c in SECTION_NOTES)
    inner = (f'<p style="margin:0 0 5pt;font-size:10.4pt">An <b>invented piece, “{PIECE}”, described on paper</b>: no audio is included. '
             f'Students’ projects will differ. {TOTAL_BARS} bars at {BPM} BPM, three Session Players, four sections (page 1 of 2).</p>'
             f'<div class="cols" style="gap:10pt"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.4pt">{WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.4pt">It names no chords, no settings and no sections.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:9pt;line-height:1.28">{STRONG}</p></div></div>'
             f'{D.H2("3 · The chords: a loop under every section")}'
             f'<div style="width:5.8in;margin:2pt auto 3pt">{D.body_svg(chords_body(1250, "page chords", 24))}</div>'
             f'{D.H2("4 · The settings: the same players, different complexity")}'
             f'<div style="width:5.6in;margin:2pt auto 3pt">{D.body_svg(settings_body(1250, "page settings", 24))}</div>'
             f'<table class="t" style="font-size:8.8pt;line-height:1.25"><tr><th>Section</th><th>Bars</th><th>What happens</th></tr>{tbl}</table>')
    return D.page("Worked example · an invented piece", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    st = "".join(f"<tr><td style='width:20%'><b>{a}</b></td><td style='width:28%'>{b}</td><td>{c}</td></tr>" for a, b, c in SETTINGS)
    chs = "".join(f"<td>{c}<br><span style='font-size:7pt'>{i + 1}</span></td>" for i, c in enumerate(CHORD_BARS[:12]))
    chs2 = "".join(f"<td>{c}<br><span style='font-size:7pt'>{i + 13}</span></td>" for i, c in enumerate(CHORD_BARS[12:]))
    mel = "".join(f"<td><b>{c}</b></td><td>{' · '.join(MELODY[c])}</td>" for c in ("C", "Am", "F", "G"))
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">“{PIECE}”, page 2 of 2: the energy, the map of the whole piece, then the numbers.</p>'
             f'{D.H2("5 · The energy: how busy the players are in each bar", True)}'
             f'<div style="width:5.2in;margin:1pt auto 3pt">{D.body_svg(arc_body(1250, "page arc", 26, 22))}</div>'
             f'{D.H2("6 · The map: four sections, three players, a melody")}'
             f'<div style="width:5.6in;margin:1pt auto 3pt">{D.body_svg(map_body(1250, "page arrange", 24, 20))}</div>'
             f'<span class="k" style="font-size:9.4pt;display:block">7 · What I set on each player</span>'
             f'<table class="t" style="font-size:8.4pt;line-height:1.2;margin-top:2pt">{st}</table>'
             f'<span class="k" style="font-size:9.4pt;display:block;margin-top:3pt">8 · The chords, bar by bar</span>'
             f'<table class="t" style="font-size:8.6pt;line-height:1.1;margin-top:2pt;text-align:center"><tr>{chs}</tr><tr>{chs2}</tr></table>'
             f'<div class="cols" style="gap:10pt;margin-top:4pt"><div><span class="k" style="font-size:9.4pt">9 · The melody, two notes a bar (bar 9 on)</span>'
             f'<table class="t" style="font-size:8.4pt;line-height:1.2;margin-top:2pt;text-align:center"><tr>{mel}</tr></table></div>'
             f'<div class="box acc-b"><span class="k">10 · Checking the numbers</span><p style="margin:0;font-size:8.2pt;line-height:1.24">'
             f'One bar of 4/4 at {BPM} BPM lasts 240 ÷ {BPM} = {BAR_S:g} seconds, so {TOTAL_BARS} bars = {TOTAL_BARS * BAR_S:g} seconds, my "1 minute". '
             f'The sections are {" + ".join(str(b - a + 1) for _, a, b in SECTIONS)} bars = {TOTAL_BARS}. Bass notes are the chord roots (C2, A1, F1, G1). '
             f'<b>Three Padlet questions (invented):</b> {qs}</p></div></div>')
    return D.page("Worked example · the map", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


def chords_page(n, wm=False):
    keys = list(SCALES)
    head = "<tr><th>Key</th>" + "".join(f"<th>{nm}</th>" for nm, _, _ in DEGREES) + "</tr>"
    rows = "".join(f"<tr><td><b>{k}</b></td>" + "".join(f"<td>{chord(k, nm)}</td>" for nm, _, _ in DEGREES) + "</tr>" for k in keys)
    ph = "<tr><th>Progression</th><th>Feel</th>" + "".join(f"<th>{k}</th>" for k in keys) + "</tr>"
    pr = "".join(f"<tr><td style='white-space:nowrap'><b>{p}</b></td><td>{f}</td>"
                 + "".join(f"<td>{' '.join(prog_chords(k, p))}</td>" for k in keys) + "</tr>" for p, f in PROGS)
    boxes = "".join("<td style='height:30pt'></td>" for _ in range(8))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.38">Step 2: choose a chord progression. Borrow one from a song you like or '
             f'create your own. If chords intimidate you, start here. Each chord below is a major or minor chord that belongs to the key. '
             f'Play one chord a bar, or two, and repeat. (This cheat sheet is the kit’s own; it names no song.)</p>'
             f'{D.H2("The chords in five major keys", True)}'
             f'<table class="t" style="font-size:10.6pt;text-align:center">{head}{rows}</table>'
             f'<p style="margin:2pt 0 0;font-size:9.4pt">Capital numerals are major chords; small numerals are minor. The same numeral is the same job in every key.</p>'
             f'{D.H2("Six common progressions, in every key")}'
             f'<table class="t" style="font-size:9.6pt;line-height:1.3;text-align:center">{ph}{pr}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:6pt"><div class="box acc-b"><span class="k">Tips</span><ul style="margin:0">'
             f'<li style="font-size:10.4pt;margin-bottom:2pt">A key you like is the one your melody sits in comfortably. Try two keys.</li>'
             f'<li style="font-size:10.4pt;margin-bottom:2pt">Change the progression in your B-section for a lift.</li>'
             f'<li style="font-size:10.4pt;margin-bottom:0">Want more? Ask a search engine or an AI chatbot for the chords to a song you like (tip 2).</li></ul></div>'
             f'<div class="box"><span class="k">Check</span>'
             + D.chk("I know the key and can name each chord.", 12, "font-size:10.4pt;margin-bottom:3pt")
             + D.chk("The chords are typed into my project, one a bar.", 12, "font-size:10.4pt;margin-bottom:0") + '</div></div>'
             f'<span class="k" style="display:block;margin-top:6pt">My chords (one a bar)</span>'
             f'<table class="map" style="margin-top:2pt"><tr>{boxes}</tr></table>'
             f'<div class="fl" style="margin-top:5pt"><b>My key:</b><span style="flex:0 0 0.8in"></span><b>My progression is:</b><span></span></div>')
    return D.page("Chord cheat sheet", "STUDENT", "Class 1", inner, n, wm, name=True, key="chords")


def players_page(n, wm=False):
    def block(nm, extra):
        return (f'<div class="box" style="margin-bottom:9pt"><span class="k">{nm}</span>'
                f'<div class="fl" style="margin:8pt 0 0"><b>Sound I chose (did I change the instrument?):</b><span></span></div>'
                f'<div class="fl" style="margin:8pt 0 0"><b>Style:</b><span></span><b>{extra}:</b><span></span></div>'
                f'<div class="fl" style="margin:8pt 0 0"><b>Complexity (1 simple to 5 busy):</b><b>Intro</b><span style="flex:0 0 0.5in"></span>'
                f'<b>Groove</b><span style="flex:0 0 0.5in"></span><b>B-section</b><span style="flex:0 0 0.5in"></span><b>Ending</b><span style="flex:0 0 0.5in"></span></div>'
                f'<div class="fl" style="margin:8pt 0 4pt"><b>What I changed from the default, and why:</b><span></span></div></div>')
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.38">Steps 1 and 3: load Drummer, Bass Player, and Keyboard Player, then adjust '
             f'each session player’s style, groove, and complexity settings. Don’t be afraid to change the instrument a session player is using. '
             f'It creates the notes, you choose the sound. Write what you set. Use 0 or “out” where a player is not playing.</p>'
             + block("Drummer", "Groove (tight, loose, swinging)")
             + block("Bass Player", "Groove (how it sits with the drums)")
             + block("Keyboard Player", "Groove (how it plays the chords)")
             + f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Check</span>'
             + D.chk("At least 3 Session Players are loaded and none is left on its default settings.", 12, "font-size:10.4pt;margin-bottom:3pt")
             + D.chk("Complexity is different in at least two sections for every player.", 12, "font-size:10.4pt;margin-bottom:3pt")
             + D.chk("I changed at least one instrument sound.", 12, "font-size:10.4pt;margin-bottom:0") + '</div>')
    return D.page("Players sheet", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="players")


def arrange_page(n, wm=False):
    nb = 36
    head = "<tr><th style='width:1.25in'>Layer</th>" + "".join(f"<th>{i + 1}</th>" for i in range(nb)) + "</tr>"
    labels = ["Chords", "Keyboard Player", "Bass Player", "Drummer", "My melody", "", ""]
    body = "".join(f"<tr><td class='l' style='height:38pt'>{lb}</td>" + "".join(f"<td class='{'b' if i % 4 == 0 else ''}'></td>" for i in range(nb)) + "</tr>"
                   for lb in labels)
    help_rows = [(80, 20), (96, 24), (100, 25), (120, 30), (128, 32), (144, 36)]
    hr = "".join(f"<tr><td><b>{b}</b></td><td>{bars}</td><td>{240 / b:.2f} s</td></tr>" for b, bars in help_rows)
    inner = (f'{CSS_SG}<style>table.sg th {{ font-size: 6pt; }} table.sg td.l {{ width: 1.25in; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.6pt">Step 4: build an intro, main groove, and ending. Vary the energy between sections. Write the chord for each bar '
             f'in the top row. Shade the bars where each player plays and write its complexity (1 to 5) in the shaded bars. Mark where each '
             f'section starts. The intro should feel different from the peak.</p>'
             f'<table class="sg">{head}{body}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:6pt"><div class="box acc-b"><span class="k">My sections (intro · groove · peak · ending)</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Intro:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Groove:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>B-section or peak:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>Ending:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div></div>'
             f'<div><span class="k">Length helper (1 minute)</span><table class="t" style="font-size:9.6pt;margin-top:2pt"><tr><th>BPM</th><th>Bars for 60 s</th><th>One bar</th></tr>{hr}</table></div></div>'
             f'<div class="fl" style="margin-top:6pt"><b>My tempo:</b><span style="flex:0 0 0.8in"></span><b>Bars:</b><span style="flex:0 0 0.8in"></span>'
             f'<b>Length: bars × 240 ÷ tempo =</b><span style="flex:0 0 0.8in"></span><b>seconds</b></div>'
             f'<div class="fl"><b>The peak is in bars</b><span style="flex:0 0 1in"></span><b>because</b><span></span></div>')
    return D.page("Arrangement plan", "STUDENT", "Classes 2–5", inner, n, wm, name=True, key="arrange")


def melody_page(n, wm=False):
    tri = "".join(f"<td><b>{c}</b><br>{t}</td>" for c, t in TRIADS_C)
    trs = "".join("<tr><td style='height:40pt'></td><td></td><td></td><td></td></tr>" for _ in range(8))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.38">Step 5: record or program an original melody over the top. '
             f'The melody is what makes this yours. Spend real time on it. Plan a few bars here, then build them in Logic and keep changing them.</p>'
             f'<span class="k" style="display:block">Chord tones in C major (a note from the chord sounds good on a strong beat)</span>'
             f'<table class="t" style="font-size:10pt;text-align:center;margin-top:2pt"><tr>{tri}</tr></table>'
             f'<div class="cols" style="gap:10pt;margin:6pt 0 4pt"><div class="box acc-b"><span class="k">Ideas that work</span><ul style="margin:0">'
             f'<li style="font-size:10.2pt;margin-bottom:2pt">Start with a short idea of 3 or 4 notes and repeat it with a small change.</li>'
             f'<li style="font-size:10.2pt;margin-bottom:2pt">Leave space. Rests make the melody easier to hear over the band.</li>'
             f'<li style="font-size:10.2pt;margin-bottom:0">Change the melody in the B-section: higher, busier, or new notes.</li></ul></div>'
             f'<div class="box"><span class="k">Check</span>'
             + D.chk("My melody is my own: I wrote or played every note.", 12, "font-size:10.2pt;margin-bottom:3pt")
             + D.chk("The melody lands on a chord tone at the end.", 12, "font-size:10.2pt;margin-bottom:3pt")
             + D.chk("I can hear it over all three players.", 12, "font-size:10.2pt;margin-bottom:0") + '</div></div>'
             f'<table class="map"><tr><th style="width:10%">Bar</th><th style="width:16%">Chord</th><th style="width:34%">Notes or rhythm I play</th><th>How it feels</th></tr>{trs}</table>'
             f'<div class="fl" style="margin-top:7pt"><b>My melody starts in bar</b><span style="flex:0 0 0.8in"></span><b>and plays on:</b><span></span></div>'
             f'<div class="fl"><b>The instrument sound I chose for it, and why:</b><span></span></div>')
    return D.page("Melody planner", "STUDENT", "Class 4", inner, n, wm, name=True, key="melody")


def mix_page(n, wm=False):
    trs = "".join(f"<tr><td style='height:40pt'><b>{a}</b></td><td></td><td></td><td></td></tr>"
                  for a in ("Keyboard Player", "Bass Player", "Drummer", "My melody", "", ""))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt">Step 6: balance levels, apply EQ and effects. Bounce your track. Write what you did on each track. '
             f'Listen to the whole piece, then fix the one thing that bothers you most.</p>'
             f'<table class="map"><tr><th style="width:20%">Track</th><th style="width:18%">Level (loud · soft)</th>'
             f'<th style="width:28%">EQ and effects I used</th><th>What I fixed</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:7pt"><span class="k">Checks before I bounce</span>'
             + "".join(D.chk(c, 12, "font-size:11.6pt;margin-bottom:6pt") for c in [
                 "I can hear my melody over the band, and the band still sounds like a band.",
                 "No player is too loud, and the drums and bass sit together.",
                 "EQ and at least one effect are in use.",
                 "The intro, the groove and the peak all sound different.",
                 "The piece is about 1 minute (give or take a few seconds).",
                 "The bounce is named correctly and the project is zipped."]) + '</div>'
             f'<div class="fl" style="margin-top:7pt"><b>Close my eyes: the first thing I hear is</b><span></span></div>'
             f'<div class="fl"><b>The part of my mix I am proudest of:</b><span></span></div>'
             f'<div class="fl"><b>What I would fix with more time:</b><span></span></div>')
    return D.page("Mix sheet", "STUDENT", "Classes 5–6", inner, n, wm, name=True, key="mix")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "vary": vary_page, "example": example_page,
         "example2": example2_page, "chords": chords_page, "players": players_page, "arrange": arrange_page, "melody": melody_page,
         "mix": mix_page}


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
    if FILE_NAME not in CHECK[2] or "Your Name – Session Player’s Studio" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    if "1-minute" not in REQS[4] or "at least 3 Session Players" not in REQS[0]:
        errs.append("requirements 1 and 5 as the owner wrote them")
    if not REFLECTION:
        errs.append("REFLECTION must be True: the owner's sheet has no reflection task")
    # chord cheat sheet: music theory
    if sorted(SCALES) != ["A", "C", "D", "F", "G"] or any(len(set(s)) != 7 for s in SCALES.values()):
        errs.append("five major keys, seven distinct notes each")
    for k, s in SCALES.items():
        if chord(k, "I") != k or chord(k, "V") != s[4] or chord(k, "vi") != s[5] + "m" or chord(k, "ii") != s[1] + "m":
            errs.append(f"chords in {k}")
    if prog_chords("C", "I – V – vi – IV") != ["C", "G", "Am", "F"] or prog_chords("G", "I – V – vi – IV") != ["G", "D", "Em", "C"]:
        errs.append("I-V-vi-IV in C and G")
    if prog_chords("F", "I – IV – V – I") != ["F", "Bb", "C", "F"] or prog_chords("C", "ii – V – I") != ["Dm", "G", "C"]:
        errs.append("progressions in F and C")
    if [c for c, _ in TRIADS_C] != [chord("C", n) for n, _, _ in DEGREES]:
        errs.append("chord-tone table must list the six chords of C major in order")
    # the worked example adds up
    if BAR_S != 2.5 or TOTAL_BARS * BAR_S != TOTAL_S or TOTAL_S != 60:
        errs.append("24 bars x 2.5 s = 60 s (the owner's 1 minute)")
    if [b - a + 1 for _, a, b in SECTIONS] != [4, 8, 8, 4] or sum(b - a + 1 for _, a, b in SECTIONS) != TOTAL_BARS:
        errs.append("sections 4 + 8 + 8 + 4 = 24 bars")
    if SECTIONS[0][1] != 1 or SECTIONS[-1][2] != TOTAL_BARS or any(b + 1 != c for (_, _, b), (_, c, _) in zip(SECTIONS, SECTIONS[1:])):
        errs.append("sections must tile the piece")
    if [nm for nm, _, _ in SECTIONS] != ["Intro", "Groove", "B-section", "Ending"]:
        errs.append("the owner's intro, groove section and ending, plus a B-section")
    if len(PLAYERS) != 3 or sorted(CX) != sorted(PLAYERS) or [p for p in PLAYERS] != ["Keyboard Player", "Bass Player", "Drummer"]:
        errs.append("three Session Players: Keyboard Player, Bass Player, Drummer")
    for p, vals in CX.items():
        a, b = PLAYER_BARS[p]
        if len(vals) != 4 or any(not 0 <= v <= 5 for v in vals):
            errs.append(f"{p}: complexity 0-5 in four sections")
        if len(set(v for v in vals if v)) < 2:
            errs.append(f"{p}: complexity must change between sections (the owner's third struggle)")
        for i, (nm, sa, sb) in enumerate(SECTIONS):
            if (vals[i] == 0) != (sb < a or sa > b):
                errs.append(f"{p}: complexity {vals[i]} in {nm} does not match the bars it plays")
    # build, peak, resolve: the energy arc
    top = max(ENERGY)
    peak_bars = [i + 1 for i, e in enumerate(ENERGY) if e == top]
    pk = next((a, b) for nm, a, b in SECTIONS if nm == "B-section")
    if not all(pk[0] <= b <= pk[1] for b in peak_bars):
        errs.append("the busiest bars must be inside the B-section")
    if not (ENERGY[0] < ENERGY[4] < top and ENERGY[-1] < ENERGY[4] and ENERGY[-1] > ENERGY[0]):
        errs.append("intro < groove < peak, and the ending thins out")
    if len(ENERGY) != 24:
        errs.append("24 bars")
    # chords: every bar has one chord; the melody and bass use chord tones; the piece starts and ends on C
    if len(CHORD_BARS) != TOTAL_BARS or CHORD_BARS[0] != "C" or CHORD_BARS[-1] != "C" or CHORD_BARS[-2] != "C":
        errs.append("a chord for each of the 24 bars, starting and ending on C")
    for c in set(CHORD_BARS):
        if c not in CHORD_TONES or c not in MELODY or c not in BASS_ROOT:
            errs.append(f"chord {c} needs tones, bass root and melody")
            continue
        if BASS_ROOT[c].rstrip("0123456789") != c.rstrip("m"):
            errs.append(f"bass root for {c}")
        for nt in MELODY[c]:
            if nt.rstrip("0123456789") not in CHORD_TONES[c]:
                errs.append(f"melody note {nt} is not a tone of {c}")
        if len(MELODY[c]) != 2:
            errs.append("two melody notes a bar")
    for nm, a, b in SECTIONS:
        if a > 1 and CHORD_BARS[a - 1] == CHORD_BARS[a - 2] and nm != "Ending":
            pass
    if not 1 < MELODY_BARS[0] < MELODY_BARS[1] <= TOTAL_BARS or MELODY_BARS[0] != 9:
        errs.append("the melody joins at bar 9 and ends inside the piece")
    if CHORD_BARS[12:20] == CHORD_BARS[4:12]:
        errs.append("the B-section must have different chords from the groove")
    if len(QUESTIONS) != 3:
        errs.append("three Padlet questions")
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
    for need in ("No audio, video, songs, artists or albums", "invented piece, “Porch Light”",
                 "Your Name – Session Player’s Studio", "Final Grade = Average of Student + Teacher", "No student work is included",
                 "Chord cheat sheet", "I – V – vi – IV", "Dm"):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "Grades 10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up:
        errs.append("UPLOAD.md: must say no audio is included and record the open questions")
    for i in (2, 5, 6, 8, 10, 13, 14, 15, 17):   # slides that shorten the owner's wording must say so
        if "shortened" not in notes[i].lower() and "shortens" not in notes[i].lower():
            errs.append(f"deck slide {i + 1} notes: must say the owner's wording is shortened")
    ch = flat[D.IX("changes") - 1]
    for s in ("slide 3", "slide 6", "slide 7", "slide 9", "slide 11", "slide 14", "slide 15", "slide 16", "slide 18"):
        if s not in ch:
            errs.append(f"'What changed' page must list {s}")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or any("Arrangement plan" in g or "Reflection" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Spotify", "Radiohead", "Billboard", "Roland", "TR-808", "Ableton",
                   "Bensound", "BenSound", "Ben Sound", "ChatGPT", "OpenAI", "Gemini", "Apple Music", "GarageBand "]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
    return errs


def check_summary():
    return (f"The invented piece is {TOTAL_BARS} bars at {BPM} BPM = {TOTAL_S} s (sections {'+'.join(str(b - a + 1) for _, a, b in SECTIONS)} bars; "
            f"3 Session Players whose complexity changes by section; peak = the B-section; a chord for every bar, starting and ending on C; "
            f"melody notes and bass roots are chord tones); chords in five keys computed from the scales; "
            f"the owner's lists counted (4 goals, 5 terms, 5 requirements, 7 steps, 4 tips, 6 checklist items, 4 struggles, 3 resources); "
            f"{len(CHANGES)} wording changes disclosed; no audio, artist names or student work included; grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
