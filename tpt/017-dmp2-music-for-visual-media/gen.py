#!/usr/bin/env python3
"""DMP2 project: Music for Visual Media (TpT 017): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Music for Visual Media > "Music for Visual Media - Project Sheet & Rubric" (rubric 5 categories scored 1-5,
/25, final grade = average of student and teacher scores), TEACHER NOTES > "Music for Visual Media - Teacher Notes" (7 class
periods), and the project's entry on "DMP2 - Project Menu" (the June 2026 menu with Type / Focus columns).
Supporting artifact (owner rule 17 Oct 2026): the "Composing to Picture" table from DMP1 (New) > 5 - Spooky Tunes > "Project Sheet &
Rubric - Spooky Tunes" (page "picture", the owner's own text, credited as from the teacher's own materials). Searched and not found:
film scoring examples list, Logic markers tutorial, the 3-5 pre-selected clips (easier variation); the owner confirmed (17 Oct 2026)
there is no clip list and no film-scoring or markers-tutorial links to add. Left out on purpose: the older 2024/2025 outlines, student work.
VIDEOS (owner, 17 Oct 2026: include the two DMP1 Unit 5 videos in the ZIP). They are in Drive > 5 - Spooky Project (read-only):
"How to import a movie into Logic.mov" (243,604,831 bytes) and "Walking Through the Woods at Night.mp4" (209,166,623 bytes). Both are
far over the ~90 MB per-file ceiling for git and TpT, git LFS is not set up in this repo, and a 200+ MB file cannot be pulled through
the Drive connector, so they are NOT in the ZIP. Fallback: a labelled "Videos" page (key "videos") names each file, its size and where
to get it. If the owner supplies compressed copies (under 90 MB each) put them in this folder and list them in ZIP_EXTRA.

NO VIDEO AND NO AUDIO ARE INCLUDED (the two tutorial videos are only named, on the Videos page). The project has students score a video clip (their own, or one from YouTube or Vimeo). Video
clips belong to their makers, so this kit never contains, hosts or links to a specific clip: it tells teachers how to choose a
clip that students may use, and the worked example is an invented 90-second scene described on paper, with a timeline, a bars-
and-seconds ruler and a dynamics picture drawn in code. No films, games, songs, lyrics or chart data are named.
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "music-for-visual-media"
TITLE = "Music for Visual Media"
ACCENT = "#8A3B12"          # this product's single accent: sienna (008 red, 009 orange, 010 violet, 011 teal, 012 blue, 013 green, 014 magenta, 015 gold, 016 olive)
ACC_LIGHT = "#EDCDB5"
PRICE = "12.00"
CLASSES = 7
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-016).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "Film Scoring in Logic Pro | Music for Visual Media Project | High School Music"
DESC_START = "Film scoring and sync for high school music technology:"
DESC_MUST = ["Music for Visual Media", "no video", "hit point", "their own clip"]
ZIP_DIR = "Music for Visual Media - Hudson Beat"
ZIP_DATE = (2026, 10, 16, 12, 0, 0)
ZIP_EXTRA = []   # the two Unit 5 videos would go here once compressed copies under 90 MB each exist (see VIDEO_FILES / the Videos page)
VIDEO_FILES = [("How to import a movie into Logic.mov", 243604831), ("Walking Through the Woods at Night.mp4", 209166623)]
TYPE = "Open-Ended Project"
PROJ_LINE = "Digital Music Production | <i>Open-Ended Project</i> | 7 class periods"
DECK_STRAP = "Mood, timing and hit points in Logic Pro"
LIVE = True                 # already uploaded to TpT (Manager-owned uploaded file); this rebuild is for a later re-upload
BANNED_EXTRA = []

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Open-Ended", "Scoring & Sync"
MENU_DESC = "Score a video clip with an original soundtrack. Match mood, pacing, and timing to the visuals."
OVERVIEW = ("Score a video. Choose a 2–3 minute video clip and compose an original soundtrack in Logic Pro that complements the "
            "visuals. Your music should match the mood, pacing, and emotional arc of the video — and at least some elements should be "
            "timed to specific visual moments.")
GOALS = ["Compose music that serves a visual narrative",
         "Develop synchronization skills — timing music to visual cues",
         "Explore mood, atmosphere, and pacing through musical choices",
         "Optionally incorporate sound effects to enhance the audio-visual experience"]
VOCAB = [("Scoring", "Writing music designed to accompany and enhance visual media"),
         ("Synchronization (Sync)", "Aligning musical events with specific visual moments on screen"),
         ("Mood", "The emotional tone that music creates — tense, joyful, mysterious, etc."),
         ("Sound Design", "Creating or selecting sound effects that enhance the visual experience"),
         ("Hit Point", "A specific moment in a video where the music emphasizes a visual event")]
REQS = ["Choose a 2–3 minute video clip (your own or from YouTube/Vimeo)",
        "Compose a fully formed piece of music that complements the visuals",
        "At least some musical elements must be timed to the visuals",
        "Sound effects are optional but encouraged",
        "Export your composition as .mp3 or .wav and sync it to the video for presentation"]
STEPS = ["<b>Choose your video</b> — Find a 2–3 minute clip that inspires you. Import it into Logic. (Clip log: page @CLIP)",
         "<b>Study the video</b> — Watch it multiple times. Note the mood, pacing, and key visual moments. (Watch notes: page @WATCH)",
         "<b>Plan your score</b> — Decide where the music builds, drops, shifts, and hits visual cues. (Score plan: page @PLAN; "
         "cue sheet: page @CUES)",
         "<b>Compose</b> — Build your score in Logic. Start with the backbone and layer in detail.",
         "<b>Sync and refine</b> — Fine-tune timing to the visuals. Add sound effects if desired. (Sync log: page @SYNC)",
         "<b>Finalize</b> — Bounce your audio and prepare the video with your music for presentation",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["Watch the video at least 5 times before you start composing. You need to know it inside and out.",
        "Use markers in Logic to flag key visual moments you want to hit.",
        "Your music doesn’t have to fill every second. Silence and space can be powerful.",
        "Watch movie trailers and film scores for inspiration on how music and visuals interact."]
FILE_NAME = "“Your Name – Music for Visual Media”"
CHECK = ["Bounced .mp3 or .wav uploaded to your class page",
         "Zipped .logicx project file uploaded to your class page",
         f"Files named correctly: {FILE_NAME}",
         "Video with synced audio ready for presentation",
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
TN_REINFORCES = ("This connects music production to real-world application in film, TV, games, and advertising. Builds synchronization "
                 "skills, emotional storytelling through music, and arrangement for narrative purposes.")
STRUGGLES = ["Students pick clips that are too long or too complex. Encourage 1–2 minutes of actual scored content within the 2–3 minute window.",
             "Students compose music they like rather than music that fits the video. Keep redirecting to the visuals.",
             "Synchronization is hard. Show them how to use markers in Logic and count frames.",
             "Students forget about dynamic range — everything is the same volume the whole time."]
VAR_EASY = "Provide 3–5 pre-selected video clips to choose from. Shorter clips (60–90 seconds) reduce overwhelm."
VAR_HARD = "Require at least 3 specific sync points. Add a requirement for original sound effects alongside the score."
RESOURCES = [("YouTube and Vimeo for royalty-free video clips",
              "Not included: no clip is included or linked here, because clips belong to their makers. Page @SETUP shows how to choose a "
              "clip students may use, and page @CLIP is where each student records where theirs came from. Two tutorial videos of mine "
              "are named on page @VIDEOS."),
             ("Film scoring examples on YouTube",
              "Not included: search by title. My own scoring-to-picture guidance is on page @PICTURE, and slide 2 and the notes for Class 1 "
              "say how to use a scene you may show, first with the sound off and then with its score."),
             ("Logic Pro markers tutorial for sync points",
              "Not included: no tutorial is in the materials this kit is built from. Page @PICTURE (my “mark your moments” advice), page "
              "@SYNCGUIDE and page @LOGICREF cover markers, SMPTE time and frames; add your own tutorial link.")]
TN_NOTE = ("This is one of the most rewarding projects when students nail the sync. Consider showing a before/after of a clip with and "
           "without music.")
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Technical Skill: ask the student to point to three markers in the Marker track and say which moment each one marks.",
                "Composition &amp; Structure: look for a shape that follows the picture. Does the music change where the scene changes, and "
                "is there a quiet moment as well as a loud one?",
                "Sound Design &amp; Mix Quality: play the finished video once with the sound off and once on. Check that the clip’s own "
                "audio is muted and that dialogue or effects in the clip do not fight the score.",
                "Documentation &amp; Presentation: the cue sheet (page @CUES) and the Sync log (page @SYNC) are the evidence, along with the Reflection page (page @REFLECT)."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Introduction. Students select and import their video. Study the clip.",
     "do": "Slides 1–6: the hook (a scene with the sound off, then on), what a score does, the seven classes, steps 1 and 2, and choosing "
           "a clip. Hand out the project sheet, the Clip log and the Watch notes.", "slides": (1, 6),
     "pages": ["clip", "watch", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Sound off, then on · what a score does · choose a clip · study it"},
    {"n": 2, "owner": "<b>Class 2:</b> Plan the score — mark key moments, decide on mood and instrumentation.",
     "do": "Slides 7–11: the timeline, a live demo of markers in Logic, bars and seconds, the score plan, shaping the dynamics. Then "
           "students fill in the Score plan and the Cue sheet.", "slides": (7, 11), "pages": ["plan", "cues", "syncguide"],
     "deck": "Timeline · markers demo · bars and seconds · plan · dynamics"},
    {"n": 3, "owner": "<b>Classes 3–5:</b> Working days — compose, layer, and sync the score.",
     "do": "Slide 12: compose, starting with the backbone. Then work time.", "slides": (12, 12), "pages": ["sync"],
     "deck": "Working day: compose the backbone"},
    {"n": 4, "owner": None, "do": "Slide 13: sync and refine; check each hit point against the picture. Then work time.", "slides": (13, 13),
     "pages": [], "deck": "Working day: sync and refine"},
    {"n": 5, "owner": None, "do": "Full working day: layer, sync and shape the dynamics. Ask each student to play you one hit point and "
                                   "tell you where it lands.", "slides": None, "pages": [], "deck": "Working day: layer, sync, shape"},
    {"n": 6, "owner": "<b>Class 6:</b> Final mix, bounce, sync audio to video. Prepare presentations.",
     "do": "Slides 14–16: finalize and bounce, what you turn in, the rubric. Students self-score, bounce and post their three questions.",
     "slides": (14, 16), "pages": ["rubric", "present"], "deck": "Finalize · checklist · rubric · 3 questions"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 17–18: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (17, 18), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one rule for Class 1</span>'
    '<p style="margin:0;font-size:9.4pt">From my common struggles: steer students to a clip with 1–2 minutes of actual scored content. '
    'Slide 6 and the clip checks on page @SETUP are your script, and page @CLIP is where students record where their clip comes from.</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:9.4pt">Working days. Slides 12 and 13 open Classes 3 '
    'and 4; Class 5 has no new slide. Circulate and ask: where is your next hit point, and what does the music do there?'
    '</p></div></div>')

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (checklist items 1 and 2).",
    "Page numbers are added to steps 1, 2, 3 and 5 (the Clip log, Watch notes, Score plan, Cue sheet and Sync log).",
    "My three resources are not included (page @TN2): no clip list, film-scoring links or markers tutorial is added, because none exists in my materials.",
    "Page @VIDEOS is new. It names the two videos from my older DMP1 Unit 5 project (the Logic import screen recording and the “Walking Through the Woods at Night” video) with their sizes and where to get them. The files are not in the ZIP because each is over 200 MB, too big for a TpT download.",
    "Page @PICTURE is my “Composing to Picture” advice from my Spooky Tunes sheet; the last sentence (about its reverb buses) is left out.",
    "My pacing guide’s “Classes 3–5” row spans the Class 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 5 shortens steps 1 and 2, slide 10 shortens step 3, "
    "slide 12 shortens step 4, slide 13 shortens step 5, and slide 14 shortens step 6.",
]
CHANGES_MUST_MENTION = ["Composing to Picture", "your class page", "Page numbers", "not in the ZIP", "Classes 3–5", "Layout only", "intro deck shortens"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the overview, goals, the five vocabulary terms, the five "
        "requirements, steps (apart from the page numbers), tips, checklist and file name (“Your Name – Music for Visual Media”), the "
        "rubric (five categories scored 1–5, /25, the average of the student’s and the teacher’s score), what the project reinforces, "
        "the four common struggles, the variations, my day-by-day pacing and my closing note, and the project menu entry quoted on "
        "page @OVERVIEW. No rubric row is added and the requirements are unchanged.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them (page @PICTURE is from my other materials, "
                "as listed above): how to use the kit, the overview and setup "
                "pages (including how to choose a clip students may use), the teacher moves and slide numbers in the pacing guide, "
                "the grading suggestions, the Logic quick reference, the sync and timing guide, the worked example (an invented "
                "90-second scene described on paper, not a video), the Clip log, Watch notes, Score plan, Cue sheet and Sync log, the "
                "vocabulary page, the presentation planner, the Videos page and the intro deck. None of these adds a requirement or a rubric row.")

# ================================================================ the worked example (Hudson Beat original: an invented scene on paper)
TEMPO = 120                     # beats per minute, 4/4
FPS = 24                        # frames per second used in the example
CLIP_S = 90                     # the invented scene is 90 seconds long
SCENES = [("Quiet street", 0, 30), ("The chase", 30, 60), ("Sunrise", 60, 90)]
HITS = [  # time in seconds, what happens on screen, what the music does
    (8.0, "A door opens", "Low pad swells in"),
    (17.5, "She sees the balloon", "One bell note"),
    (30.0, "Cut to the chase", "Drums enter, tempo feel doubles"),
    (44.0, "Turns the corner", "Melody steps up a third"),
    (60.0, "The balloon pops", "Everything stops for two beats"),
    (76.0, "The sun comes up", "Full band returns, bright and wide"),
]
ENERGY = [(0, .15), (8, .15), (8.5, .3), (17, .3), (17.5, .4), (29.5, .4), (30, .75), (44, .75), (44.5, .9), (59.5, .95), (60, .04),
          (61, .04), (61.5, .3), (75.5, .55), (76, .9), (88, .9), (90, .4)]


def beat_len(bpm=TEMPO):
    return 60 / bpm


def bar_len(bpm=TEMPO):
    return 4 * 60 / bpm


def pos(t, bpm=TEMPO):
    """Bar and beat (1-based, 4/4) of a time in seconds."""
    beats = round(t / beat_len(bpm), 6)
    return int(beats // 4) + 1, int(beats % 4) + 1


def mmss(t):
    t = float(t)
    return f"{int(t) // 60}:{int(t) % 60:02d}" + (".5" if t % 1 else "")


def timecode(t, fps=FPS):
    """h:mm:ss:ff, as Logic's SMPTE display shows it."""
    whole = int(t)
    ff = round((t - whole) * fps)
    return f"00:{whole // 60:02d}:{whole % 60:02d}:{ff:02d}"


def energy_at(t):
    for (t0, e0), (t1, e1) in zip(ENERGY, ENERGY[1:]):
        if t0 <= t <= t1:
            return e0 if t1 == t0 else e0 + (e1 - e0) * (t - t0) / (t1 - t0)
    return ENERGY[-1][1]


def minus(v):
    return str(v).replace("-", "−")


# ================================================================ drawings (original, code-drawn: black + accent only)
def tl_body(W=1600, name="timeline", sh=92, fs=26, ts=22, ms=20):
    """The invented 90-second scene: three scenes, six numbered hit points, and a loudness curve under them."""
    gut = 14
    pw = W - 2 * gut

    def X(t):
        return gut + pw * t / CLIP_S

    fills = ["#000", ACCENT, "#4a4a4a"]
    out = []
    for (nm, a, b), fc in zip(SCENES, fills):
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{fc}"/>')
        head = nm.upper()
        out.append(D.t_((X(a) + X(b)) / 2, sh / 2 + fs * .36 + 2, head, fs, 700, fill_="#fff"))
        D.lab(name + " scenes", head, fs, X(b) - X(a) - 24)
    for t, lbl in ((0, "0:00  ·  bar 1"), (30, "0:30  ·  bar 16"), (60, "1:00  ·  bar 31"), (90, "1:30  ·  bar 46")):
        anc = "start" if t == 0 else ("end" if t == 90 else "middle")
        out.append(f'<line x1="{X(t):.1f}" y1="{sh + 4}" x2="{X(t):.1f}" y2="{sh + 20}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(t) + (2 if t == 0 else (-2 if t == 90 else 0)), sh + 20 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 260)
    my = sh + 20 + ts + 38
    r = ms * .95
    for i, (t, *_r) in enumerate(HITS, 1):
        out.append(f'<line x1="{X(t):.1f}" y1="{sh + 20 + ts + 10}" x2="{X(t):.1f}" y2="{my - r:.1f}" stroke="#000" stroke-width="1.6" stroke-dasharray="4 5"/>')
        out.append(f'<circle cx="{X(t):.1f}" cy="{my:.1f}" r="{r:.1f}" fill="#000"/>')
        out.append(D.t_(X(t), my + ms * .36, str(i), ms, 700, fill_="#fff"))
    cy0 = my + r + 20
    ch = 110 if W > 1300 else 84
    out.append(f'<rect x="{gut}" y="{cy0:.1f}" width="{pw}" height="{ch}" fill="#fff" stroke="#000" stroke-width="1.6"/>')
    pts = " ".join(f"{X(t):.1f},{cy0 + ch - 8 - e * (ch - 16):.1f}" for t, e in ENERGY)
    out.append(f'<polyline points="{pts}" fill="none" stroke="{ACCENT if W < 1300 else "#000"}" stroke-width="6" stroke-linejoin="round"/>')
    out.append(D.t_(gut + 10, cy0 + ts + 4, "LOUDNESS", ts - 2, 500, anchor="start"))
    D.lab(name + " loud", "LOUDNESS", ts - 2, 150)
    ptx = X(60)
    cap = "two beats of silence"
    out.append(D.t_(ptx + 14, cy0 + ts + 4, cap, ts - 4, 500, anchor="start"))
    D.lab(name + " cap", cap, ts - 4, X(76) - ptx - 20)
    return "".join(out), W, cy0 + ch + 6


def grid_body2(W=1500, name="grid"):
    """Bars and seconds: the first 18 seconds at 120 BPM and at 100 BPM, with hit points 1 and 2."""
    gut = 130
    x0, x1 = gut, W - 40
    span_s = 18.0

    def X(t):
        return x0 + (x1 - x0) * t / span_s

    out = []
    rows = [(120, 104), (100, 376)]
    for bpm, ytop in rows:
        bl = bar_len(bpm)
        out.append(D.t_(gut - 18, ytop + 78, f"{bpm}", 52, 700, anchor="end", fill_=ACCENT if bpm == 120 else "#000"))
        out.append(D.t_(gut - 18, ytop + 108, "BPM", 26, 500, anchor="end"))
        out.append(f'<rect x="{x0}" y="{ytop}" width="{x1 - x0}" height="90" fill="#fff" stroke="#000" stroke-width="2"/>')
        k, t = 0, 0.0
        while t <= span_s + 1e-9:
            out.append(f'<line x1="{X(t):.1f}" y1="{ytop}" x2="{X(t):.1f}" y2="{ytop + 90}" stroke="#000" stroke-width="3"/>')
            for b in range(1, 4):
                tb = t + b * beat_len(bpm)
                if tb < span_s:
                    out.append(f'<line x1="{X(tb):.1f}" y1="{ytop + 55}" x2="{X(tb):.1f}" y2="{ytop + 90}" stroke="#000" stroke-width="1.4" opacity=".55"/>')
            if t + bl <= span_s + 1e-9 and bl * (x1 - x0) / span_s > 70:
                out.append(D.t_(X(t) + 12, ytop + 38, str(k + 1), 30, 700, anchor="start"))
            k += 1
            t = k * bl
        for tt in (0, 6, 12, 18):
            out.append(D.t_(X(tt) if tt else X(tt) + 4, ytop + 90 + 32, f"{tt} s", 24, 500, anchor="middle" if tt not in (0, 18) else ("start" if tt == 0 else "end")))
    D.lab(name + " bpm", "BPM", 26, 100)
    for i, (t, *_r) in enumerate(HITS[:2], 1):
        for bpm, ytop in rows:
            out.append(f'<line x1="{X(t):.1f}" y1="{ytop - 26}" x2="{X(t):.1f}" y2="{ytop + 90}" stroke="{ACCENT}" stroke-width="5"/>')
        out.append(f'<circle cx="{X(t):.1f}" cy="{rows[0][1] - 40}" r="22" fill="{ACCENT}"/>')
        out.append(D.t_(X(t), rows[0][1] - 40 + 8, str(i), 24, 700, fill_="#fff"))
    # notes
    out.append(D.t_(x0, 30, "120 BPM: one bar is 2 seconds", 34, 700, anchor="start"))
    D.lab(name + " head", "120 BPM: one bar is 2 seconds", 34, 700)
    t100 = 8 / bar_len(100)
    out.append(D.t_(x0, 344, f"100 BPM: one bar is {bar_len(100):.1f} seconds", 34, 700, anchor="start"))
    D.lab(name + " head2", f"100 BPM: one bar is {bar_len(100):.1f} seconds", 34, 700)
    # callouts under each ruler
    out.append(D.t_(x0, 268, f"Hit 1 at 0:08 lands on bar {pos(8)[0]}, beat {pos(8)[1]}.   Hit 2 at 0:17.5 lands on bar {pos(17.5)[0]}, beat {pos(17.5)[1]}.", 28, 500, anchor="start"))
    D.lab(name + " call1", f"Hit 1 at 0:08 lands on bar {pos(8)[0]}, beat {pos(8)[1]}.   Hit 2 at 0:17.5 lands on bar {pos(17.5)[0]}, beat {pos(17.5)[1]}.", 28, x1 - x0 + 40)
    c2 = f"Slow to 100 BPM and hit 1 falls {t100:.2f} bars in, between beats."
    out.append(D.t_(x0, 548, c2, 28, 500, anchor="start"))
    D.lab(name + " call2", c2, 28, x1 - x0 + 40)
    return "".join(out), W, 566


def dyn_body(W=1500, name="dyn"):
    """The same scene scored two ways: one flat level for all 90 seconds, or shaped to the picture."""
    gut = 14
    n = 30
    cw = (W - 2 * gut) / n
    bh = 150
    out = []

    def row(top, title, heights, fills_, tfill="#000"):
        out.append(D.t_(gut + 2, top - 14, title, 30, 700, anchor="start", fill_=tfill))
        D.lab(name + " titles", title, 30, W - 2 * gut)
        out.append(f'<line x1="{gut}" y1="{top + bh}" x2="{W - gut}" y2="{top + bh}" stroke="#000" stroke-width="2"/>')
        for i, h in enumerate(heights):
            hh = max(5, h * bh)
            out.append(f'<rect x="{gut + i * cw + 3:.1f}" y="{top + bh - hh:.1f}" width="{cw - 6:.1f}" height="{hh:.1f}" rx="3" fill="{fills_[i]}"/>')

    flat = [.7] * n
    shaped = [energy_at(i * 3 + 1.5) for i in range(n)]
    row(56, "FLAT: the same level for all 90 seconds", flat, ["#7a7a7a"] * n)
    sil = int(60 // 3)
    row(300, "SHAPED: quiet, build, silence, release", shaped, [ACCENT if i == sil else "#000" for i in range(n)], tfill="#000")
    base = 300 + bh
    for nm, a, b in SCENES:
        xa, xb = gut + a / 3 * cw, gut + b / 3 * cw
        out.append(f'<line x1="{xa + 6:.1f}" y1="{base + 14}" x2="{xb - 6:.1f}" y2="{base + 14}" stroke="#000" stroke-width="2.4"/>')
        out.append(D.t_((xa + xb) / 2, base + 46, nm.upper(), 24, 500))
        D.lab(name + " scenes", nm.upper(), 24, xb - xa - 20)
    cap = "the silence"
    out.append(D.t_(gut + sil * cw + cw * 1.2, 300 + 52, cap, 24, 700, anchor="start", fill_=ACCENT))
    D.lab(name + " cap", cap, 24, 200)
    return "".join(out), W, base + 62


def hero_body():
    return D.stack([tl_body(1100, "hero tl", 80, 22, 18, 17)], 40)


DRAWINGS = {"hero": hero_body, "timeline": lambda: tl_body(1600, "timeline pic"), "grid": lambda: grid_body2(1500, "grid pic"),
            "dyn": lambda: dyn_body(1500, "dyn pic")}
DRAWING_PX = {"hero": 1900, "timeline": 2000, "grid": 2000, "dyn": 2000}
SIDE = {"timeline": ["Three scenes, six hit points", "The curve follows the picture", "It gets quiet before the pop", "Hit points sit on the timeline"],
        "grid": ["A bar is four beats", "Seconds divided by bar length", "Pick a tempo that lands the hits", "Hits between beats feel loose"],
        "dyn": ["Flat means the same all the way", "Shape follows the story", "Silence is a choice", "Loud means more after quiet"]}


def label_extras():
    tl_body(1250, "page tl", 88, 24, 20, 19)
    grid_body2(1250, "page grid")


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Music for Visual Media", "Score the picture.",
     "Class 1, the first minute. Before class, pick one short scene you are allowed to show (your own footage, or a clip your school may "
     "use) that has a clear mood and a few obvious moments. No video or audio is included in this deck. Open with my overview: choose "
     "a clip of 2 to 3 minutes and compose an original soundtrack in Logic Pro that matches its mood, pacing and emotional arc."),
    (1, "listen", "Watch: sound off, then sound on", "Sound off, then on · The same scene, played twice|Teacher: play the scene once with the "
     "sound off, then with a score.|What did the music tell you that the picture did not?|Where did the music change when the picture "
     "changed?|Was there a moment of silence?",
     "Play your scene with the sound off first, with no comment. Then play it with music. Take answers aloud: the feeling, the speed, "
     "the surprise. Ask where the music matched an action on screen. This sets up the whole project. If you want my before and after "
     "idea from the teacher notes, this is it: the same clip with and without music."),
    (1, "bullets", "What does a score do?", "Sets the mood: tense, joyful, mysterious|Matches the pacing of the cuts|Follows the emotional "
     "arc|Hits specific moments on screen|Knows when to be quiet",
     "A plain-English tour using the vocabulary on the project sheet. Scoring is writing music to accompany visual media. Mood is the "
     "emotional tone. Synchronization means aligning musical events with moments on screen, and a hit point is one such moment. Sound "
     "design is the effects. Students add their own words on the vocabulary page. Silence and space can be powerful."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: introduction; students select and import their video and study it. "
     "Class 2: plan the score, marking key moments and deciding on mood and instrumentation. Classes 3 to 5 are working days: compose, "
     "layer and sync. Class 6: final mix, bounce, sync the audio to the video, prepare presentations. Class 7: presentations with "
     "Padlet peer feedback. Hand out the project sheet now."),
    (1, "steps", "Steps 1 and 2: choose, study", "Find a clip of 2–3 minutes|Import it into Logic|Watch it at least 5 times|Note the mood, "
     "pacing and key moments|Fill in the Clip log and Watch notes",
     "Steps 1 and 2 of the project sheet, shortened to fit the slide. Students choose a clip of 2 to 3 minutes that inspires them and "
     "import it into Logic, then watch it multiple times, noting mood, pacing and key visual moments. My tip: watch it at least five "
     "times before composing. The Clip log is where they record where it came from."),
    (1, "bullets", "Choose a clip you can use", "1–2 minutes of real scored content|Few scenes, clear moments|Your own footage, or a clip "
     "you may use|Know where it came from|Mute the clip’s own music",
     "My first common struggle: students pick clips that are too long or too complex. Encourage 1 to 2 minutes of actual scored content "
     "inside the 2 to 3 minute window. The project sheet allows your own clip or one from YouTube or Vimeo. Clips belong to their "
     "makers, so students record the source on the Clip log and check the site's terms before anyone posts a finished video."),
    (2, "pic", "Where the music hits", "timeline",
     "Class 2. An invented 90-second scene, described on paper only; nothing here is a video. Three scenes, six numbered hit points, "
     "and a loudness curve under them. Notice that the curve follows the picture: quiet, build, a drop to silence at the pop, then a "
     "release. Ask students where the hit points would be in their own clips. Then go straight to the Logic demo."),
    (2, "steps", "Watch me: markers in Logic", "File, Movie, Open Movie: the clip appears|Play it and stop on a key moment|Add a marker "
     "there and name it|Read the time in SMPTE: minutes, seconds, frames|Mark every moment you want to hit",
     "This is the demo from my teacher notes: synchronization is hard, so show how to use markers in Logic and count frames. Open a "
     "movie you may show, show the Marker track, and add three markers. Switch the display to SMPTE time and point out the frames. "
     "Use markers to flag key visual moments you want to hit, as my tips say."),
    (2, "pic", "Worked example: bars and seconds", "grid",
     "At 120 BPM a beat is half a second and a bar of four beats is 2 seconds. A hit at 0:08 lands exactly on bar 5, beat 1. A hit at "
     "0:17.5 lands on bar 9, beat 4. Slow the tempo to 100 BPM and a bar is 2.4 seconds, so the hit at 0:08 falls between beats. This is "
     "why some students set the tempo to fit their hit points. It is a trick, not a rule."),
    (2, "steps", "Plan your score", "Where does the music build?|Where does it drop?|Where does it shift?|Where does it hit a cue?|Fill "
     "in the Score plan and Cue sheet",
     "Step 3 of the project sheet, shortened to fit the slide: decide where the music builds, drops, shifts and hits visual cues. "
     "Students use the Score plan for mood and instruments and the Cue sheet for the hit points with times. My pacing guide for Class 2 "
     "says: plan the score, mark key moments, decide on mood and instrumentation."),
    (2, "pic", "Shape the dynamics", "dyn",
     "My fourth common struggle: students forget about dynamic range, so everything is the same volume the whole time. The top row "
     "is flat; the bottom row follows the story, goes nearly silent at the pop, and then releases. Ask which one feels like it belongs to "
     "the picture. Show students volume automation as one tool and note that the music does not have to fill every second."),
    (3, "bullets", "Working day: compose", "Start with the backbone|Layer in detail|Keep looking at the picture|Music you like is not the "
     "goal: music that fits is",
     "Class 3 is the first working day. Step 4 of the project sheet, shortened here: build your score in Logic, starting with the "
     "backbone and layering in detail. My second common struggle: students compose music they like instead of music that fits the "
     "video. Keep redirecting to the visuals. Circulate and ask each student what the picture is doing right now."),
    (4, "bullets", "Working day: sync and refine", "Check every hit point against the picture|Nudge by frames, not guesses|Add sound "
     "effects if you like|Leave space: silence is a choice",
     "Class 4, a working day. Step 5 of the project sheet, shortened here: fine-tune timing to the visuals and add sound effects if "
     "desired. Students use the Sync log to check each hit point. Class 5 is a full working day with no new slide: layer, sync and shape "
     "the dynamics. Ask each student to play you one hit point and tell you where it lands."),
    (6, "bullets", "Finalize and bounce", "Final mix and levels|Bounce a .mp3 or .wav|Put your music on the video|Write your 3 Padlet "
     "questions",
     "Class 6. Step 6 of the project sheet, shortened to fit the slide: bounce the audio and prepare the video with your music for "
     "presentation. In Logic you can export the audio to the movie, or play the video and the bounce together. Zip the .logicx in Finder "
     "(Control-click, Compress). Students also write their three Padlet questions today."),
    (6, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Music for Visual Media|Video with "
     "synced audio ready|Padlet post with your 3 questions|Answer 2 questions on classmates’ posts",
     "The submission checklist from the project sheet, in short form. Show where students upload (your class page) and where the Padlet "
     "board is. Remind students to check that the finished video plays with sound before they present, and that the clip's original "
     "music is muted."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play your video with your score|Walk us through your choices|Your Padlet post: 3 questions about "
     "your project|Answer at least 2 of each classmate’s 3",
     "Class 7, presentations with Padlet Q and A. Each student plays the video with the score and explains the mood, the hit points and "
     "the creative choices. During classmates' presentations, every student answers at least 2 of their 3 questions on their Padlet "
     "post. If time allows, show one before and after: the same video with the music muted, then on."),
    (7, "closer", "One last thing…", "You started with silence.|You watched until you knew it.|You hit the moments.|Now it feels like "
     "one thing.",
     "Close with what my teacher notes say this project builds: synchronization skills, emotional storytelling through music, and "
     "arrangement for narrative purposes. It is one of the most rewarding projects when students nail the sync. Remind them that music "
     "does not have to fill every second."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("cues", "Cue sheet", "hit points with times"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 7, 9, 11, 16]
SHOTS3 = [("setup", "Choosing a clip"), ("syncguide", "Sync guide"), ("example", "Worked example"), ("proj1", "Project sheet"),
          ("proj2", "Steps"), ("plan", "Score plan"), ("sync", "Sync log"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "videos", "pacing", "tn1", "tn2", "changes", "logicref", "syncguide", "picture", "example",
        "clip", "watch", "plan", "cues", "sync", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "cues", "proj2", "rubric"]

COVER_A = "Score the picture"
COVER_C = "DMP2 · mood · timing · hit points · markers · intro slides"
PDF_COVER = dict(a=32, b=49, c=14, art=7.3)
SQ_COVER = dict(a=50, b=136, c=27, art=700)
SQ_B_LINES = ["Music for", "Visual Media"]
SQ_SUB = "7 class periods · mood · sync · hit points · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Clip guide, sync guide, worked example, cue sheet, project sheet", 28)}
SQ_BANDS = {1: "Choose <em>·</em> study <em>·</em> plan <em>·</em> compose <em>·</em> sync <em>·</em> present",
            2: "Hook <em>·</em> timeline <em>·</em> markers <em>·</em> dynamics <em>·</em> rubric",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no video included"}

SONG_NOTE = ("No video, audio, films, games or songs are included. Students use their own clip, or one they may use from a site such as "
             "YouTube or Vimeo, and choose it themselves (page @SETUP), so you know exactly where every picture came from.")
CREDITS = ["Worked example (an invented 90-second scene described on paper), the timeline, bars-and-seconds and dynamics drawings and "
           "layouts: original work, Hudson Beat.",
           "No video, audio, lyrics, album art, screenshots or chart data are included. YouTube and Vimeo are named only as the owner’s "
           "resource list names them; they are not affiliated with or endorsing this resource. Padlet is named only as an example of a "
           "tool you may already use."]
LOGIC_INTRO = ("Everything students need in Logic for this project, in one table. Demonstrate markers (slide 8) and then let students "
               "work. Names are from current Logic Pro versions.")
LOGIC_REF = [("Open the clip", "File › Movie › Open Movie, then choose the video file. The picture shows in a movie window; the clip’s "
              "own sound arrives as a track you can mute."),
             ("Frame rate", "Project Settings › Synchronization › Frame Rate. Match the video’s rate (often 24, 25 or 30) so markers and "
              "timecode line up."),
             ("Read the time", "Switch the LCD to show SMPTE time (Control-click the display for the choices): hours:minutes:seconds:frames."),
             ("Markers", "View › Show Global Tracks, then use the Marker track. Stop on a key moment, add a marker at the playhead and give it "
              "a name, such as “pop” or “cut”."),
             ("Set the tempo", "Click the tempo in the LCD and type a number, or draw changes on the Tempo global track. A bar is "
              "4 × 60 ÷ tempo seconds (page " + str(PLAN.index("syncguide") + 1) + ")."),
             ("Snap and grid", "Set Snap to Bar, Beat or Division, so regions land on the grid. Turn Snap off to nudge by smaller steps."),
             ("Software instruments", "Click an empty track, choose Software Instrument, and pick a sound in the Library. Start with one pad "
              "or bass as the backbone, then layer in detail."),
             ("Volume automation", "Press A to show automation, choose Volume and draw swells and dips. This is how a score gets quiet before a "
              "big moment."),
             ("Sound effects", "Record your own sounds, or build effects with a software instrument. Place each one at a marker."),
             ("Mute the clip’s audio", "Mute or delete the video’s own audio track, so the original soundtrack does not play under yours."),
             ("Bounce", "File › Bounce › Project or Section (Command-B), MP3 or WAV. File › Export › Audio to Movie puts the music on the "
              "video, or you can play the video and the bounce together."),
             ("Zip the project", "In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; .mp3 or .wav and zipped .logicx uploaded", "Padlet post created with my 3 questions",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my video:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Clips too long or complex: slide 6, the clip checks on page @SETUP and the Clip log (page @CLIP).</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Music they like, not music that fits: the Watch notes (page @WATCH) and the Score plan (page @PLAN) start from the picture.</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Sync is hard: the markers demo (slide 8), the sync guide (page @SYNCGUIDE) and the Cue sheet (page @CUES).</li>'
    '<li style="font-size:10.8pt;margin-bottom:0">Same volume the whole time: slide 11 and the dynamics row of the Score plan (page @PLAN).</li></ul></div>')
TN1_SIZE = 13.6
TN2_SIZE = 10.6
PACING_SIZE = 9.8
PROJ_SIZE = 14.2
VOCAB_GAP = 8
LOGIC_SIZE = 10.8
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example", "How to use, overview, choosing a clip, pacing, teacher notes, what changed, Logic "
              "reference, sync guide, composing to picture, worked example, the two tutorial videos (named, not included)"),
             ("Student pages", "clip", "reflect", "Clip log, Watch notes, Score plan, Cue sheet, Sync log, project sheet (3 pages), rubric, "
              "vocabulary, feedback planner, reflection"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period scoring project for high school music technology. Each '
             f'student chooses a 2–3 minute video clip and composes an original soundtrack for it in Logic Pro: music that matches the '
             f'mood, pacing and emotional arc of the picture, with at least some elements timed to specific visual moments, called hit '
             f'points. It is an open-ended project from my Digital Music Production 2 course (focus: scoring and sync), and the projects '
             f'in that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Decide how students will find a clip they may use (page {D.IX("setup")}): no video is included.</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("clip")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Class 5 is a working day with no new slide. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No video or audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Clips:</b> students may film their own, so the project also works with no downloads at all.</li>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}.</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students pick a '
             f'clip, study it, mark its key moments, compose a score that fits and hits them, and present the result.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a trademark of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:14pt;line-height:1.55">One Logic Pro score for a 2–3 minute video clip, with at least some musical '
             f'elements timed to the picture and, if they like, sound effects. They hand in a bounced .mp3 or .wav, the zipped .logicx '
             f'project, and a Padlet post with three feedback questions, then show the video with their music and talk through their '
             f'choices.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:14pt;line-height:1.55">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:12pt">Supports the National Core Arts Standards for Music (Music Technology, high school): refining original '
             f'work (MU:Cr3.1), presenting it (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:13pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.6pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: choose and study, plan, three working days, bounce, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: movie import, markers, SMPTE time, software instruments, tempo, volume automation, '
             f'bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Video clips (students’ own, or ones they may use), headphones, a feedback board, and '
             f'speakers if you can</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:12pt">Students should already '
             f'know how to open a project, add software instruments, and save, bounce and zip in Logic. The Logic quick reference (page '
             f'{D.IX("logicref")}) covers every tool this project uses.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Open-Ended", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<div class="cols"><div class="big">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student (a current version), and <b>headphones</b>. Speakers help for the final '
             f'check that the music and the picture feel right together.</li>'
             f'<li><b>A video clip for every student</b>: their own footage, or one they may use. Nothing is included.</li>'
             f'<li><b>A place to submit</b> an .mp3 or .wav and a zipped .logicx project (your class page).</li>'
             f'<li><b>A feedback board</b> for the three questions (my sheets use Padlet).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("clip")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:12pt;margin-bottom:8pt") for c in [
                 "Decide how clips will be chosen: your own footage, ones students find, or a short list you provide (my easier variation).",
                 "Read the terms of the site students will use, so you can tell them what they may do with a clip.",
                 "Pick one short scene you may show, for slide 2: first with the sound off, then with its score.",
                 "Print the student pages; set up the submission spot and the feedback board."]) +
             f'</div><div class="big">'
             f'{D.H2("Choosing a clip", True)}'
             f'<p style="font-size:11.4pt">My project says: your own, or from YouTube or Vimeo. Page {D.IX("clip")} is the student log for either.</p>'
             f'<ul style="font-size:11.4pt;line-height:1.42">'
             f'<li><b>Your own footage.</b> A phone video, a school project, or screen capture of a game the student plays. No source '
             f'questions, and the student already knows the story.</li>'
             f'<li><b>A clip you give them.</b> Provide 3–5 clips you may use and let students choose, as my easier variation says.</li>'
             f'<li><b>A clip they find.</b> Look for sites and licenses that allow reuse, and have the student write the source on the Clip log.</li></ul>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">Five checks for any clip</span><ul style="margin:0">'
             f'<li style="font-size:11.2pt">Does it run 2–3 minutes, with 1–2 of them worth scoring?</li>'
             f'<li style="font-size:11.2pt">Does it have a clear mood a student can name?</li>'
             f'<li style="font-size:11.2pt">Does it have a few obvious moments to hit?</li>'
             f'<li style="font-size:11.2pt">Is it simple enough (one place, a few cuts)?</li>'
             f'<li style="font-size:11.2pt">Does the student know where it came from?</li></ul></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Rights and credit</span><p style="margin:0;font-size:11.2pt">Clips belong '
             f'to their makers. Scoring a clip for a class exercise is different from posting the finished video online. Check the '
             f'clip site’s terms before anyone posts publicly, and credit the maker. This kit gives no legal advice and includes or '
             f'links to no clip.</p></div>'
             f'</div></div>')
    return D.page("Setup and choosing a clip", "SETUP", "Teacher", inner, n, key="setup")


def mb(b):
    return f"{b / 1e6:.0f} MB"


def videos_page(n, wm=False):
    (f1, b1), (f2, b2) = VIDEO_FILES
    rows = (f"<tr><td style='width:29%;padding:6pt'><b>{f1}</b></td><td style='width:11%'>{mb(b1)}<br>QuickTime</td>"
            f"<td>My screen recording of importing a movie into Logic. Use it in Class 1 for step 1, “Choose your video”. The steps are "
            f"also written in the Logic quick reference (page @LOGICREF).</td></tr>"
            f"<tr><td><b>{f2}</b></td><td>{mb(b2)}<br>MP4</td>"
            f"<td>A video from my DMP1 Unit 5 project. Use it as a scene you may show on slide 2 (sound off, then on) and for the markers "
            f"demo on slide 8, if you do not have a scene of your own.</td></tr>")
    inner = (f'<div class="box acc-b"><span class="k">Not in this ZIP</span><p style="margin:0;font-size:13.4pt;line-height:1.5">Two videos from my '
             f'older DMP1 Unit 5 project go with this unit. Each file is over 200 MB, far too big for a Teachers Pay Teachers download, so '
             f'they are named here and are <b>not</b> in the ZIP.</p></div>'
             f'{D.H2("The two videos")}<table class="t" style="font-size:12.6pt;line-height:1.45"><tr><th>File</th><th>Size</th><th>What it is for</th></tr>{rows}</table>'
             f'{D.H2("Where to get them")}<p style="font-size:13.2pt;line-height:1.5">Ask for the download link in the Q&amp;A tab of the '
             f'{D.BRAND} by {D.STORE} store on Teachers Pay Teachers, and give the file names above. The files are meant for your own '
             f'students, under the terms on the last page.</p>'
             f'{D.H2("The project works without them")}<ul style="font-size:12.2pt;line-height:1.45">'
             f'<li>Class 1 and Class 2 run fine with a short scene you may show: page @SETUP shows how to choose one.</li>'
             f'<li>The Logic quick reference (page @LOGICREF) has the import steps (File › Movie › Open Movie), markers, SMPTE time and the frame rate.</li>'
             f'<li>Students use their own clip, or one they may use, as my project sheet says (page @PROJ2).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Why a page and not the files</span><p style="margin:0;font-size:12.4pt">'
             f'A TpT product file has a size limit, and a ZIP with these two videos would be about {mb(b1 + b2)}. Naming them keeps this download '
             f'small and keeps the PDF and deck as the product.</p></div>')
    return D.page("Videos · named, not included", "SETUP", "Teacher", D.fill(inner), n, key="videos")


def syncguide_page(n, wm=False):
    t_rows = "".join(f"<tr><td>{b}</td><td>{beat_len(b) * 1000:.0f} ms</td><td><b>{bar_len(b):.2f} s</b></td><td>{60 / bar_len(b):.1f}</td></tr>"
                     for b in (80, 90, 100, 120, 140))
    fr = "".join(f"<tr><td>{f} frames per second</td><td>{1000 / f:.1f} ms</td></tr>" for f in (24, 25, 30))
    hit_types = [("On the beat", "The hit lands exactly on a beat or the start of a bar. Easiest to feel; use it for the big moments."),
                 ("Just before it", "A short run-up or pickup leads into the moment, so the music arrives as the picture does."),
                 ("A stinger", "One short sound on the exact frame, such as a bell, a hit or a rise, over a quieter bed of music."),
                 ("Silence", "The music stops, so the picture speaks alone. Often the strongest hit of all.")]
    hrows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a, b in hit_types)
    moods = [("Tense", "slow pulse, low register, sparse, notes held and unresolved"), ("Joyful", "major key, brighter register, steady and light"),
             ("Mysterious", "quiet, lots of space, unusual sounds, reverb"), ("Sad", "slow, minor key, soft, simple melody"),
             ("Excited", "fast, rhythmic, rising lines, getting louder")]
    mrows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a, b in moods)
    inner = (f'<p style="margin:0 0 3pt;font-size:11.4pt">My notes say sync is hard: show students how to use markers and count frames. This page '
             f'is the explanation to project or print. The numbers use an invented scene at {TEMPO} BPM in 4/4.</p>'
             f'<div style="width:6.2in;margin:2pt auto 3pt">{D.body_svg(grid_body2(1250, "page grid"))}</div>'
             f'<div class="cols" style="gap:14pt"><div>'
             f'{D.H2("Seconds and bars", True)}<table class="t" style="font-size:10.4pt"><tr><th>BPM</th><th>One beat</th><th>One bar</th><th>Bars/min</th></tr>{t_rows}</table>'
             f'<p class="small" style="margin:3pt 0 0">One bar in 4/4 = 4 × 60 ÷ BPM seconds. A hit at time t is in bar t ÷ (bar length) + 1.</p></div>'
             f'<div>{D.H2("Counting frames", True)}<table class="t" style="font-size:10.4pt"><tr><th>Video</th><th>One frame</th></tr>{fr}</table>'
             f'<p class="small" style="margin:3pt 0 0">Timecode is hours:minutes:seconds:frames. At 24 fps, 0:17.5 is 00:00:17:12, or '
             f'frame {17 * 24 + 12}. Match the project’s frame rate to the video’s.</p></div></div>'
             f'<div class="cols" style="gap:14pt"><div>{D.H2("Four ways to hit a moment")}<table class="t" style="font-size:10.2pt">{hrows}</table></div>'
             f'<div>{D.H2("Mood: first ideas")}<table class="t" style="font-size:10.2pt">{mrows}</table>'
             f'<p class="small" style="margin:3pt 0 0">Rules of thumb, not laws. Trust your ears and the picture.</p></div></div>')
    return D.page("Sync and timing guide", "SYNC GUIDE", "Teacher + student", inner, n, key="syncguide")


def example_page(n, wm=False):
    rows = "".join(f"<tr><td style='text-align:center'><b>{i}</b></td><td>{mmss(t)}</td><td>{timecode(t)}</td>"
                   f"<td>{pos(t)[0]}.{pos(t)[1]}</td><td>{w}</td><td>{m}</td></tr>" for i, (t, w, m) in enumerate(HITS, 1))
    inner = (f'<p style="margin:0 0 3pt">An <b>invented 90-second scene, described on paper</b>: no video or audio is included, so the numbers '
             f'are easy to check. Students’ clips will differ.</p>'
             f'{D.H2("1 · The scene and its hit points", True)}<div style="width:7.3in;margin:1pt auto 3pt">{D.body_svg(tl_body(1250, "page tl", 88, 24, 20, 19))}</div>'
             f'<p class="small" style="margin:0 0 2pt">Three scenes of 30 seconds each. At {TEMPO} BPM one bar is {bar_len():.0f} seconds, so the scene is 45 bars '
             f'long and each scene is 15 bars.</p>'
             f'{D.H2("2 · The cue sheet")}'
             f'<table class="t" style="font-size:11pt"><tr><th style="width:4%">#</th><th style="width:8%">Time</th><th style="width:15%">Timecode ({FPS} fps)</th>'
             f'<th style="width:8%">Bar.beat</th><th style="width:25%">On screen</th><th>The music</th></tr>{rows}</table>'
             f'<div class="cols" style="gap:12pt"><div class="box"><span class="k">3 · Reading a row</span>'
             f'<p style="margin:0;font-size:12.4pt;line-height:1.5">Hit 2 is at 17.5 s. 17.5 ÷ {beat_len():.1f} = 35 beats. 35 ÷ 4 = 8 bars and 3 beats, '
             f'so it is bar 9, beat 4. In timecode it is 17 s and 12 frames at {FPS} fps.</p></div>'
             f'<div class="box"><span class="k">4 · The shape of the score</span>'
             f'<p style="margin:0;font-size:12.4pt;line-height:1.5">Scene 1 is quiet and sparse. Scene 2 is loud and driving until the pop at '
             f'1:00, then two beats of silence. Scene 3 returns bright. The loudness curve on this page is the plan (slide 11).</p></div></div>')
    return D.page("Worked example · an invented scene", "EXAMPLE", "Teacher", inner, n, ak=True, key="example")


def clip_page(n, wm=False):
    cb = D.checkbox(13)
    inner = (f'<div class="fl"><b>Clip title or description:</b><span></span></div>'
             f'<div class="fl"><b>Where it came from (my own footage, or the site and link):</b><span></span></div>'
             f'<div class="fl"><b>Who made it:</b><span></span><b>Length:</b><span style="flex:0 0 0.9in"></span><b>Frame rate:</b><span style="flex:0 0 0.7in"></span></div>'
             f'<div class="fl"><b>I will score from</b><span style="flex:0 0 0.8in"></span><b>to</b><span style="flex:0 0 0.8in"></span>'
             f'<b>(1–2 minutes of real scored content)</b><span style="border:0"></span></div>'
             f'{D.H2("Is this clip a good choice?")}'
             + "".join(D.chk(c, 13, "font-size:13pt;margin-bottom:9pt") for c in [
                 "It runs 2–3 minutes, and 1–2 minutes of it are worth scoring",
                 "I can name its mood in a word or two",
                 "It has a few clear moments I can hit",
                 "It is simple enough: one place, a few cuts, not too many characters",
                 "I know where it came from, and I may use it for this class project",
                 "I muted the clip’s own music, so only my score plays"]) +
             f'{D.H2("Why I chose it")}<div class="ln2" style="margin-bottom:10pt"></div><div class="ln2" style="margin-bottom:10pt"></div>'
             f'<div class="ln2" style="margin-bottom:10pt"></div>'
             f'{D.H2("Credit and rights note")}<p style="margin:0 0 4pt;font-size:10.8pt">If I share my finished video outside class, I will check the '
             f'terms of the site the clip came from, and I will credit the person who made it.</p>'
             f'<div class="fl"><b>Credit line:</b><span></span></div>')
    return D.page("Clip log", "STUDENT", "Class 1", inner, n, wm, name=True, key="clip")


def watch_page(n, wm=False):
    rows = [("1", "Just watch. What happens? What is the story?"), ("2", "Mood: what is the feeling? Colors, light, faces."),
            ("3", "Pacing: how fast are the cuts? Where does it speed up or slow down?"),
            ("4", "Key moments: write the time of each big change or action."),
            ("5", "Sound: what do you hear in the clip itself? What is missing?")]
    trs = "".join(f"<tr><td style='text-align:center;height:78pt'><b>{a}</b></td><td style='font-size:10.4pt'>{b}</td><td></td></tr>" for a, b in rows)
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">My tip: watch the video at least 5 times before you start composing. Use a different job '
             f'for each viewing and write what you notice.</p>'
             f'<table class="map"><tr><th style="width:9%">Watch</th><th style="width:34%">What to look for</th><th>What I noticed</th></tr>{trs}</table>'
             f'<div class="fl" style="margin-top:8pt"><b>The mood in three words:</b><span></span></div>'
             f'<div class="fl"><b>The pacing in one sentence:</b><span></span></div>'
             f'<div class="fl"><b>The emotional arc (how the feeling changes from start to end):</b><span></span></div>'
             f'<div class="ln2" style="margin-bottom:2pt"></div>'
             f'<div class="fl"><b>Where I might use silence:</b><span></span></div>')
    return D.page("Watch notes", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="watch")


def plan_page(n, wm=False):
    rows = "".join("<tr><td style='height:44pt'></td><td></td><td></td><td></td><td></td></tr>" for _ in range(5))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Step 3: decide where the music builds, drops, shifts and hits visual cues. One row per '
             f'scene or section of your clip. Start from what the picture does, not from the music you like.</p>'
             f'<table class="map"><tr><th style="width:15%">Scene and time</th><th style="width:16%">Mood</th><th style="width:25%">Instruments and sounds</th>'
             f'<th style="width:16%">Tempo and key</th><th>Loudness: quiet, medium, loud, and how it changes</th></tr>{rows}</table>'
             f'<div class="fl" style="margin-top:8pt"><b>The backbone I will build first:</b><span></span></div>'
             f'<div class="fl"><b>My main musical idea (a melody, a rhythm or a sound):</b><span></span></div>'
             f'<div class="fl"><b>Where the music is silent or very quiet, and why:</b><span></span></div>'
             f'<div class="fl"><b>Sound effects I might add (optional):</b><span></span></div>'
             f'<div class="ln2" style="margin-bottom:2pt"></div>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">Check before you compose</span><p style="margin:0;font-size:10.8pt">Does my '
             f'plan change at the places the picture changes? Does it have a quiet part and a loud part?</p></div>')
    return D.page("Score plan", "STUDENT", "Class 2", inner, n, wm, name=True, key="plan")


def cues_page(n, wm=False):
    rows = "".join("<tr><td style='height:29pt;text-align:center'></td><td></td><td></td><td></td><td></td><td></td></tr>" for _ in range(11))
    inner = (f'<div class="fl"><b>Tempo:</b><span style="flex:0 0 0.8in"></span><b>BPM.  One bar =</b><span style="flex:0 0 0.8in"></span>'
             f'<b>seconds  (4 × 60 ÷ BPM).  Frame rate:</b><span style="flex:0 0 0.7in"></span><span style="border:0"></span></div>'
             f'<p style="margin:0 0 5pt;font-size:10.6pt">Mark every hit point on the video with a marker in Logic, then list it here. Use the markers to '
             f'read the time. Bar.beat = the bar and beat where the music should hit.</p>'
             f'<table class="map"><tr><th style="width:5%">#</th><th style="width:10%">Time (m:ss)</th><th style="width:17%">Timecode</th>'
             f'<th style="width:9%">Bar.beat</th><th style="width:26%">What happens on screen</th><th>What the music does</th></tr>{rows}</table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Tip</span><p style="margin:0;font-size:10.8pt">Start with at least three hit points. '
             f'If a hit does not land on a beat, try a different tempo, or hit the moment with a stinger instead (page {D.IX("syncguide")}).</p></div>')
    return D.page("Cue sheet", "STUDENT", "Class 2", inner, n, wm, name=True, key="cues")


def sync_page(n, wm=False):
    cb = D.checkbox(13)
    rows = "".join(f"<tr><td style='text-align:center;height:30pt'><b>{i}</b></td><td></td><td style='text-align:center'>{cb}</td><td></td>"
                   f"<td style='text-align:center'>{cb}</td></tr>" for i in range(1, 9))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Step 5: for each hit point on your cue sheet, play it with the picture. Does the music arrive '
             f'with the moment? Write how many frames early or late, then fix it.</p>'
             f'<table class="map"><tr><th style="width:7%">Hit #</th><th style="width:20%">Planned bar.beat</th><th style="width:14%">On the moment?</th>'
             f'<th style="width:30%">Early (−) or late (+), in frames</th><th>Fixed?</th></tr>{rows}</table>'
             f'{D.H2("Dynamics check")}'
             + "".join(D.chk(c, 12, "font-size:11pt;margin-bottom:5pt") for c in [
                 "There is a quiet part and a loud part",
                 "The loud parts are loud because of the picture",
                 "I used silence or space at least once",
                 "My music is not the same level the whole time"]) +
             f'{D.H2("Mix check")}'
             + "".join(D.chk(c, 12, "font-size:11pt;margin-bottom:5pt") for c in [
                 "I listened with headphones and with the clip on",
                 "The clip’s own music is muted",
                 "Any sound effects sit at their markers",
                 "The video plays from the start with my music"]))
    return D.page("Sync log", "STUDENT", "Classes 3–6", inner, n, wm, name=True, key="sync")


PICTURE_MOVES = [
    ("Watch before you build", "Play the clip twice without touching Logic. What moments stand out? Where does the energy change? What "
     "would a sound do to that moment? Write notes before you open a single plug-in."),
    ("Mark your moments", "Add markers in Logic at the timestamps where you want something to happen. A footstep. A sudden silence. "
     "A swell. Having the map in advance stops you from improvising past the moments that matter."),
    ("Silence is a tool", "If nothing is playing for a moment and then a sound enters, the entry feels enormous. Silence is not dead "
     "air; it is tension. Use it deliberately."),
    ("Let the picture breathe", "You do not need to fill every second with sound. Sparse music over a quiet visual can be more "
     "unsettling than a wall of noise. Less is often more here."),
    ("Match the energy", "If the picture gets more intense, your music should respond. Build toward moments of tension and release "
     "from them."),
]


def picture_page(n, wm=False):
    rows = "".join(f"<tr><td style='width:27%;font-size:13.4pt'><b>{a}</b></td><td style='font-size:13pt;line-height:1.5'>{b}</td></tr>"
                   for a, b in PICTURE_MOVES)
    inner = (f'<p style="margin:0 0 6pt;font-size:11.8pt">From the teacher’s own materials: the advice I give my own students when they '
             f'score a picture for the first time. Project it, or hand it out on Class 1 or 2, next to the Watch notes (page {D.IX("watch")}) '
             f'and the Cue sheet (page {D.IX("cues")}).</p>'
             f'{D.H2("Composing to picture", True)}<table class="t">{rows}</table>'
             f'<div class="cols" style="gap:14pt;margin-top:10pt"><div class="box acc-b"><span class="k">Try this in Class 1</span>'
             f'<p style="margin:0;font-size:11.6pt">Play a scene you may show to the class with no comment. Then ask: what would you '
             f'expect to hear if this were a film? Take answers aloud before anyone opens Logic.</p></div>'
             f'<div class="box"><span class="k">Where it connects</span><ul style="margin:0;font-size:11.4pt">'
             f'<li>Markers: demo on slide 8, then the Sync log (page {D.IX("sync")}).</li>'
             f'<li>Silence and space: the dynamics picture on slide 11.</li>'
             f'<li>Hit points: the Sync guide (page {D.IX("syncguide")}).</li></ul></div></div>'
             f'<div class="box" style="margin-top:10pt"><span class="k">Ask your students</span><ul style="margin:0;font-size:12pt;line-height:1.5">'
             f'<li>Which moment in your clip would feel biggest if the music stopped?</li>'
             f'<li>Where are you filling space that the picture does not need filled?</li>'
             f'<li>Does your music follow the picture, or just play alongside it?</li></ul></div>'
             f'<p class="small" style="margin-top:8pt">Film scoring examples are not included. Search by title for a scene you may show.</p>')
    return D.page("Composing to picture", "TEACHER + STUDENT", "Classes 1-2", inner, n, wm, key="picture")


PAGES = {"videos": videos_page, "howto": howto_page, "overview": overview_page, "setup": setup_page, "syncguide": syncguide_page, "picture": picture_page, "example": example_page,
         "clip": clip_page, "watch": watch_page, "plan": plan_page, "cues": cues_page, "sync": sync_page}


# ================================================================ content checks (music arithmetic, owner text, no video)
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
    if FILE_NAME not in CHECK[2] or "Music for Visual Media" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    if "2–3 minute" not in REQS[0]:
        errs.append("requirement 1 must stay a 2-3 minute clip")
    # the worked example adds up
    if bar_len() != 2.0 or beat_len() != .5 or bar_len(100) != 2.4:
        errs.append("bar lengths: 2.0 s at 120 BPM, 2.4 s at 100 BPM")
    expect = {8.0: (5, 1), 17.5: (9, 4), 30.0: (16, 1), 44.0: (23, 1), 60.0: (31, 1), 76.0: (39, 1)}
    for t, bb in expect.items():
        if pos(t) != bb:
            errs.append(f"hit at {t}s should be bar.beat {bb}, got {pos(t)}")
    if timecode(17.5) != "00:00:17:12" or 17 * 24 + 12 != 420:
        errs.append("timecode of 17.5 s at 24 fps is 00:00:17:12 (frame 420)")
    if CLIP_S / bar_len() != 45 or any(b - a != 30 for _, a, b in SCENES) or SCENES[-1][2] != CLIP_S:
        errs.append("scene: 45 bars, three 30-second scenes")
    if len(HITS) < 3 or [h[0] for h in HITS] != sorted(h[0] for h in HITS):
        errs.append("at least three hit points, in time order")
    if not 8 / bar_len(100) > 3.3 or 8 % bar_len(100) == 0:
        errs.append("at 100 BPM hit 1 must fall off the grid")
    if min(e for _, e in ENERGY) > .1 or max(e for _, e in ENERGY) < .8:
        errs.append("loudness curve needs a real quiet and a real loud part")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    vp = flat[D.IX("videos") - 1]
    for f_, b_ in VIDEO_FILES:
        if not all(w in vp for w in f_.split()) or mb(b_) not in vp:
            errs.append(f"Videos page must name {f_} and its size {mb(b_)}")
    if "Not in this ZIP" not in vp.replace("NOT IN THIS ZIP", "Not in this ZIP") or ZIP_EXTRA:
        errs.append("Videos page: must say the files are not in the ZIP (fallback) while ZIP_EXTRA is empty")
    for f_, _ in VIDEO_FILES:
        if os.path.exists(os.path.join(HERE, f_)):
            errs.append(f"{f_} must not be committed (over 90 MB)")
    for need in ("No video",):
        if need not in notes[0]:
            errs.append(f"deck slide 1 notes must say '{need}'")
    txt = " ".join(flat)
    for need in ("No video, audio, films, games or songs are included", "invented 90-second scene, described on paper",
                 "Your Name – Music for Visual Media", "Final Grade = Average of Student + Teacher", "YouTube"):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no video" not in up.lower() or "Open question" not in up or "Videos page" not in up:
        errs.append("UPLOAD.md: must say no video is included, explain the Videos page and record the open questions")
    for i in (4, 9, 11, 12, 13):   # slides that shorten the owner's wording must say so
        if "shortened" not in notes[i].lower():
            errs.append(f"deck slide {i + 1} notes: must say the owner's wording is shortened")
    ch = flat[D.IX("changes") - 1]
    for s in ("slide 5", "slide 10", "slide 12", "slide 13", "slide 14"):
        if s not in ch:
            errs.append(f"'What changed' page must list {s}")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or any("markers" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in ("Billie", "Beatles", "Spotify", "Star Wars", "Disney", "Pixar", "Minecraft", "Mario"):
        if banned in alldeck or banned in txt:
            errs.append(f"must not name films, games, songs, artists or services ({banned})")
    return errs


def check_summary():
    return (f"At {TEMPO} BPM one bar is {bar_len():.0f} s (100 BPM: {bar_len(100):.1f} s); the six hit points land on bars "
            f"{', '.join(str(pos(t)[0]) for t, *_ in HITS)}; 0:17.5 is 00:00:17:12 at {FPS} fps; the invented scene is {CLIP_S} s, 45 bars; "
            f"the owner's lists counted (4 goals, 5 terms, 5 requirements, 7 steps, 4 tips, 6 checklist items, 4 struggles, 3 resources); "
            f"{len(CHANGES)} wording changes disclosed; no video or audio included (the two Unit 5 videos are named on the Videos page, over 90 MB each, not in the ZIP); grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
