#!/usr/bin/env python3
"""DMP2 project: Billboard Top 10 (TpT 014): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Billboard Top 10 > "Billboard Top 10 - Project Sheet & Rubric" (rubric 5 categories scored 1-5, /25,
final grade = average of student and teacher scores), TEACHER NOTES > "Billboard Top 10 - Teacher Notes" (7 class periods),
and the project's entry on "DMP2 - Project Menu". Every change to the owner's wording is listed in CHANGES and printed on the
"What changed from the original" page. No songs, audio, lyrics or chart data are included: students use the current chart.
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "billboard-top-10"
TITLE = "Billboard Top 10"
ACCENT = "#B0127A"          # this product's single accent: magenta (008 red, 009 orange, 010 violet, 011 teal, 012 blue, 013 green)
ACC_LIGHT = "#F6C3E4"
PRICE = "12.00"
CLASSES = 7
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-013).
#   DMP2 is the second-year course (page 3 says so); some schools take it in 9th grade.
TAGS = ["Autumn"]                                           # the only proven tag that fits a fall-semester course; extras in UPLOAD.md
ANSWER_KEY = None            # no answer key in this kit; "Included" is the only proven option text
LISTING_TITLE = "Song Form in Logic Pro | Billboard Top 10 Remake | High School Music Technology"
DESC_START = "Song form and drum programming for high school music technology:"
DESC_MUST = ["Billboard Top 10", "YouTube or Spotify", "no songs", "not affiliated with Billboard"]
ZIP_DIR = "Billboard Top 10 - Hudson Beat"
ZIP_DATE = (2026, 10, 15, 12, 0, 0)
TYPE = "Structured Project"
PROJ_LINE = "Digital Music Production | <i>Structured Project</i> | 7 class periods"
DECK_STRAP = "Song form and drums in Logic Pro"
LIVE = True                 # already live on TpT (uploaded/release files belong to the Manager); this rebuild is for the later re-upload
BANNED_EXTRA = ["Bieber" + " example spreadsheet"]

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Structured", "Song Form & Drums"
MENU_DESC = "Analyze and recreate a current Billboard hit. Study song form, production techniques, and drum programming."
OVERVIEW = ("Your job is to study the current Billboard Top 10, pick one song, and recreate it in Logic Pro. You’re not just copying — "
            "you’re reverse-engineering what makes a hit song work. You’ll analyze song form, drum patterns, instrumentation, and production "
            "techniques, then build your own version from scratch.")
GOALS = ["Analyze song form, structure, and arrangement in commercial music",
         "Develop drum programming skills by recreating real-world patterns",
         "Practice matching tempo, key, and instrumentation to a reference track",
         "Strengthen mixing and production techniques through style emulation"]
VOCAB = [("Song Form", "The structure of a song — how sections like intro, verse, chorus, and bridge are organized"),
         ("Tempo", "The speed of a song, measured in BPM (beats per minute)"),
         ("Drum Pattern", "A repeating rhythmic figure played by the kick, snare, and hi-hat that defines the groove"),
         ("Emulation", "Recreating the style and sound of an existing track as closely as possible"),
         ("Arrangement Markers", "Logic’s tool for labeling and organizing song sections on the timeline")]
REQS = ["Choose one song from the current Billboard Top 10",
        "Match the tempo of your chosen song exactly",
        "Recreate the exact song form (intro, verse, chorus, bridge, etc.)",
        "Drum patterns must be self-created — percussion loops are okay as accents",
        "Use appropriate instruments and layers for the genre",
        "Apply EQ and plug-ins to shape your sounds authentically"]
STEPS = ["<b>Explore the Billboard Top 10</b> — listen to all 10 songs and complete the Top 10 analysis (page @ANALYSIS)",
         "<b>Study song form</b> — map out the exact structure of your chosen song using the Song Form map (page @FORMMAP)",
         "<b>Analyze and program drum patterns</b> — break down the kick, snare, and hi-hat and build them in Logic (page @DRUMS). "
         "Set up Arrangement Markers.",
         "<b>Build your foundation</b> — lay down bass, chords, and core instrumentation to match the original’s energy",
         "<b>Add layers</b> — fill in melodies, pads, FX, and transitions to match the fullness of the original",
         "<b>Mix and refine</b> — EQ every track, pan for width, adjust levels, and add plug-ins for authenticity",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["Listen to your reference track with headphones and really pay attention to what’s happening in each section. Count the bars.",
        "Don’t try to perfectly match every single sound — focus on capturing the vibe, structure, and energy.",
        "Your drums are the backbone. If the beat doesn’t feel right, the whole track will feel off.",
        "Use Logic’s Arrangement Markers early to block out your form — it keeps you organized and saves time."]
FILE_NAME = "“Your Name – Billboard Top 10”"
CHECK = ["Top 10 analysis completed",
         "Song form mapped out and input into Logic using Arrangement Markers",
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
RUBRIC_TOTAL = 25            # checked in Drive: "Grading Rubric /25", Student / Teacher / Final "/ 25"
RUBRIC_SHORT = [ds[4] for _, ds in RUBRIC]    # the owner's own level-5 descriptors, for the deck
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine · / 25"
# ---- Teacher Notes
TN_REINFORCES = ("This builds directly on song form, drum programming, and arrangement skills. The emulation approach forces precision with "
                 "tempo, form, and instrumentation while still requiring creative production choices. It teaches students to listen "
                 "analytically rather than passively.")
STRUGGLES = ["Students pick songs that are too complex (heavily layered pop or hip-hop with 50+ tracks). Guide them toward songs with clear, "
             "identifiable sections.",
             "Song form analysis is rushed or inaccurate — students skip counting bars. Require the Song Form map (page @FORMMAP) before they "
             "open Logic.",
             "Drum programming feels robotic. Encourage velocity variation and subtle timing adjustments to add human feel.",
             "Students copy the arrangement but ignore the mix — the EQ and panning step often gets skipped."]
VAR_EASY = "Allow students to recreate only the first 1–2 minutes of the song, or provide a pre-built drum pattern they can modify."
VAR_HARD = "Require students to add an original 8-bar section (bridge, outro, or remix) that fits the style but is entirely their own."
RESOURCES = [("Google Form for Billboard analysis (link on your class page)", "The Top 10 analysis, page @ANALYSIS (a printed version; my "
              "Google Form is not included)."),
             ("Song Form spreadsheet — <i>Sorry</i> by Justin Bieber example", "The Song Form map, page @FORMMAP, and the worked example on "
              "page @EXAMPLE. My spreadsheet is not included; you can map the song with the class from your own YouTube or Spotify access."),
             ("Drum Pattern analysis spreadsheet for reference", "Drum pattern analysis, page @DRUMS, with worked grids on page @EXAMPLE."),
             ("Billboard Hot 100 website for current chart", "billboard.com (the Hot 100 chart). Check the current Top 10 before Class 1 (page "
              "@SETUP).")]
TN_NOTE = ("This project works well early when students need structure. The Top 10 analysis and the song form and drum pattern pages "
           "front-load the analytical work.")
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
# kit suggestions, NOT the owner's rubric: printed under a "Suggestions from this kit" label (dmp2.GRADING_TIPS_LABEL)
GRADING_TIPS = ["Composition &amp; Structure: hold the student’s Song Form map next to their Arrangement Markers. Do the sections, bar counts and "
           "tempo match the original?",
           "Technical Skill: are the drums programmed by the student (percussion loops only as accents), with some velocity variation?",
           "Sound Design &amp; Mix: solo a few tracks. Is there EQ on every track, panning for width, and nothing clipping on the loudest "
           "section?"]
# ---- pacing: the owner's day-by-day guide, as written ("owner"; None = shares the row above, the owner's "Classes 3–5")
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Explore Billboard Top 10, complete the Top 10 analysis. Begin song form analysis.",
     "do": "Slides 1–6: hook, listen to the No. 1, what emulation is, the seven classes, the Top 10 and song form. Hand out the project "
           "sheet and the Top 10 analysis.", "slides": (1, 6), "pages": ["analysis", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Explore the Top 10 · Top 10 analysis · begin song form"},
    {"n": 2, "owner": "<b>Class 2:</b> Finish song form mapping. Analyze drum patterns and begin programming in Logic.",
     "do": "Slides 7–10: a mapped song, tempo and markers demo, the drums broken down, drum demo. Check every Song Form map before "
           "students open Logic.", "slides": (7, 10), "pages": ["formmap", "drums"],
     "deck": "Finish the Song Form map · tempo and markers · drums"},
    {"n": 3, "owner": "<b>Classes 3–5:</b> Working days — build tracks, layer instruments, refine arrangement.",
     "do": "Slide 11: build your foundation (bass, chords, core instruments). Then work time; circulate.", "slides": (11, 11),
     "pages": [], "deck": "Working day: build your foundation"},
    {"n": 4, "owner": None, "do": "Slide 12: add layers (melodies, pads, FX, transitions). Then work time.", "slides": (12, 12),
     "pages": [], "deck": "Working day: add layers"},
    {"n": 5, "owner": None, "do": "Full working day: refine the arrangement against the original, section by section.", "slides": None,
     "pages": [], "deck": "Working day: refine the arrangement"},
    {"n": 6, "owner": "<b>Class 6:</b> Final mix and bounce. Prepare presentations and write 3 Padlet feedback questions.",
     "do": "Slides 13–15: mix and refine, what you turn in, the rubric. Students self-score, bounce and post their questions.",
     "slides": (13, 15), "pages": ["rubric", "present"], "deck": "Mix and bounce · checklist · rubric · 3 questions"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 16–17: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (16, 17), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:8pt;gap:14pt"><div class="box acc-b"><span class="k">The one rule for Class 2</span>'
    '<p style="margin:0;font-size:11pt">From my common struggles: students skip counting bars. Require the Song Form map (page @FORMMAP) '
    'before they open Logic. Slides 7 and 8 model it.</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:11pt">Working days. Slides 11 and 12 open Classes 3 '
    'and 4; Class 5 has no new slide. Circulate with each student’s Song Form map and ask: which section are you building, and does it '
    'match the original’s energy?</p></div></div>')

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (checklist items 3 and 4, and the Google Form link in my resource list).",
    "My Google Form analysis is not included, so step 1, the first checklist item and my Class 1 plan say “the Top 10 analysis” "
    "(a printed page, page @ANALYSIS) instead of “the Google Form analysis” / “complete Google Form”.",
    "My Song Form spreadsheet is not included, so step 2 and the second common struggle say “the Song Form map” (page @FORMMAP) "
    "instead of “the Song Form spreadsheet”.",
    "Page numbers are added to steps 1–3 (step 3 points to the drum pattern page, page @DRUMS).",
    "My closing note says “The Top 10 analysis and the song form and drum pattern pages front-load the analytical work” instead of "
    "“The Google Form and spreadsheets front-load the analytical work”.",
    "My pacing guide’s “Classes 3–5” row spans the Class 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): step 6 becomes four short lines on slide 13 (“EQ "
    "every track · Pan for width · Adjust levels · Add plug-ins for authenticity”); slides 3, 5, 11, 12 and 14 condense the emulation "
    "definition, steps 1, 4 and 5 and the checklist.",
]
CHANGES_MUST_MENTION = ["your class page", "Google Form", "Song Form spreadsheet", "Page numbers", "front-load", "Classes 3–5", "Layout only", "intro deck shortens", "step 6 becomes four short lines on slide 13"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the overview, goals, vocabulary, requirements, steps, tips, "
        "checklist and file name (“Your Name – Billboard Top 10”), the rubric (five categories scored 1–5, /25, the average of the "
        "student’s and the teacher’s score), what the project reinforces, the four common struggles, the variations, my resource list "
        "and my day-by-day pacing, and the project menu entry quoted on page @OVERVIEW. No rubric row is added and the requirements are unchanged.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: how to use the kit, the overview and setup "
                "pages, the teacher moves and slide numbers in the pacing guide, the grading suggestions, the Logic quick reference, the worked "
                "example (an original practice map, not a real song), the Top 10 analysis, the Song Form map and the drum pattern pages, "
                "the vocabulary page, the presentation planner and the intro deck. None of these adds a requirement or a rubric row.")

# ================================================================ the worked example (Hudson Beat original: a practice map, not a real song)
TEMPO = 100
BEATS_15S = 25                                  # counting tip: beats in 15 seconds x 4 = BPM
FORM = [("Intro", 4), ("Verse 1", 16), ("Chorus", 8), ("Verse 2", 16), ("Chorus", 8), ("Bridge", 8), ("Chorus", 8), ("Outro", 4)]
WHAT = {"Intro": ("Chords and a pad, no drums", 1), "Verse": ("Drums (verse groove), bass, chords; vocal melody", 2),
        "Chorus": ("Full drums (chorus groove), bass, chords, pad, lead synth", 4), "Bridge": ("Drums drop to kick only; pad and bass", 2),
        "Outro": ("Chords ring out; no drums", 1)}
LANES = ["Open hi-hat", "Closed hi-hat", "Clap", "Snare", "Kick"]
VERSE = {"Closed hi-hat": "x.x.x.x.x.x.x.x.", "Snare": "....x.......x...", "Kick": "x.......x.x....."}
CHORUS = {"Open hi-hat": "..x...x...x...x.", "Closed hi-hat": "x...x...x...x...", "Clap": "....x.......x...", "Snare": "....x.......x...",
          "Kick": "x...x...x...x..."}
VERSE_HAT_VEL = [(100 if i % 4 == 0 else 72) if VERSE["Closed hi-hat"][i] == "x" else None for i in range(16)]


def bar_secs(bpm=TEMPO):
    return 4 * 60 / bpm


def mmss(s):
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


def bar_time(bar):
    return mmss((bar - 1) * bar_secs())


def starts():
    out, b = [], 1
    for _, n in FORM:
        out.append(b)
        b += n
    return out


TOTAL_BARS = sum(n for _, n in FORM)
FILLS = {"Intro": "#6e6e6e", "Outro": "#6e6e6e", "Verse": "#000", "Chorus": ACCENT, "Bridge": "#4a4a4a"}


# ================================================================ drawings (original, code-drawn: black + accent only)
def form_drawing(W=1600, h=110, times=True, name="form"):
    return D.form_body(f"{name} {W}", FORM, W=W, h=h, fills=FILLS, times=bar_time if times else None,
                       energy={k: v[1] for k, v in WHAT.items()})


def drums_drawing(cw=30, ch=34, name="drums"):
    lanes = [ln for ln in LANES if ln in VERSE or ln in CHORUS]
    return D.grid_body(f"{name} {cw}", [VERSE, CHORUS], ["Verse groove", "Chorus groove"], lanes, cw=cw, ch=ch, gut=170, ls=20,
                       vel={0: VERSE_HAT_VEL})


def ladder_body(W=1600, rh=70):
    """The chart: ranks 1-10 in two columns, each with a blank title bar (no songs are named); No. 1 in the accent."""
    out, colw = [], (W - 60) / 2
    for k in range(10):
        col, row = k // 5, k % 5
        x, y = col * (colw + 60), row * rh
        acc = k == 0
        bx = rh * 1.2
        out.append(f'<rect x="{x:.1f}" y="{y + 4}" width="{bx:.0f}" height="{rh - 10}" rx="8" fill="{ACCENT if acc else "#000"}"/>')
        out.append(D.t_(x + bx / 2, y + rh * 0.7, str(k + 1), rh * 0.55, 700, fill_="#fff"))
        D.lab("ladder", str(k + 1), rh * 0.55, bx - 8)
        bw = colw - bx - 30 - (k % 3) * 70
        out.append(f'<rect x="{x + bx + 16:.1f}" y="{y + rh * 0.22:.1f}" width="{bw:.1f}" height="{rh * 0.24:.1f}" rx="{rh * 0.12:.1f}" '
                   f'fill="{ACCENT if acc else "#1a1a1a"}"/>')
        out.append(f'<rect x="{x + bx + 16:.1f}" y="{y + rh * 0.56:.1f}" width="{bw * 0.55:.1f}" height="{rh * 0.15:.1f}" rx="{rh * 0.075:.1f}" '
                   f'fill="#9a9a9a"/>')
    return "".join(out), W, 5 * rh


def hero_body():
    lanes = [ln for ln in LANES if ln in VERSE or ln in CHORUS]
    grid = D.grid_body("hero grid", [VERSE, CHORUS], ["Verse groove", "Chorus groove"], lanes, cw=40, ch=38, gut=180, ls=22)
    return D.stack([ladder_body(1600, 96), form_drawing(1600, 130, times=False, name="hero"), grid], 40)


DRAWINGS = {"hero": hero_body, "form": lambda: form_drawing(1600, 210), "drums": lambda: drums_drawing()}
DRAWING_PX = {"hero": 1900, "form": 2000, "drums": 2000}
SIDE = {"form": [f"{TOTAL_BARS} bars at {TEMPO} BPM: {mmss(TOTAL_BARS * bar_secs())}", "Count bars, not seconds",
                 "One Arrangement Marker per section", "Verses 16 bars, choruses 8"],
        "drums": ["Verse: hi-hat eighths, snare on 2 and 4", "Chorus: kick on every beat, open hi-hats",
                  "A clap doubles the snare in the chorus", "Velocity: louder on the beat, softer between"]}


def label_extras():
    form_drawing(1250, 96)          # the example page's size
    drums_drawing(17, 21, "page")   # the example page's size


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Billboard Top 10", "Feat. this week’s Hot 100",
     "Class 1, the first minute. Have this week’s Billboard Hot 100 open on billboard.com, and the No. 1 song cued up on YouTube or Spotify "
     "from your own account; no audio, video or chart data are included in this deck. Open with my overview: your job is to pick one hit "
     "and recreate it in Logic Pro."),
    (1, "listen", "Listen: this week’s No. 1", "This week’s Billboard Hot 100 · the No. 1 song|Teacher: open the chart; play the No. 1 "
     "from YouTube or Spotify.|How long until the first chorus?|What instruments can you hear?|Clap the beat: fast, medium or slow?",
     "Play the first minute or so of the current No. 1 (preview it first: choose a clean version). The Hot 100 is published every week "
     "and has been since 1958; it ranks songs by streaming, sales and radio airplay. Take answers aloud. The point is my teacher note: "
     "listen analytically rather than passively."),
    (1, "bullets", "What the heck is emulation?", "Recreating a track’s style and sound as closely as you can|Not just copying: "
     "reverse-engineering a hit|Same tempo, same form, your own drums|Then build your own version from scratch",
     "Plain-English definition, from the project sheet vocabulary: emulation is recreating the style and sound of an existing track as "
     "closely as possible. From my overview: you are not just copying, you are reverse-engineering what makes a hit song work. The drum "
     "patterns must be self-created; percussion loops are okay as accents."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: explore the Top 10 and start the song form. Class 2: finish the map, then "
     "drums. Classes 3 to 5 are working days. Class 6: final mix and bounce, presentations prepared. Class 7: presentations with Padlet "
     "feedback. Hand out the project sheet now."),
    (1, "steps", "Step 1: explore the Top 10", "Listen to all 10 songs|Fill in the Top 10 analysis|Pick one song with clear, "
     "easy-to-hear sections|Start counting bars: where does each section begin?",
     "Students listen to all 10 songs with headphones and fill in the Top 10 analysis page. Steer them, as my notes say, away from heavily "
     "layered songs with 50 or more tracks and toward songs with clear, identifiable sections. Check song choices for school-appropriate "
     "content before they commit."),
    (1, "bullets", "Song form: what to listen for", "Intro, verse, chorus, bridge, outro|Count the bars in every section|Write down when "
     "each section starts|Finish the Song Form map before Logic",
     "Song form is the structure of a song: how sections like intro, verse, chorus and bridge are organized. Model counting bars aloud on "
     "the No. 1 from slide 2: count 1, 2, 3, 4 and say the bar number on each 1. Students begin their Song Form map today and finish it "
     "in Class 2, before they open Logic."),
    (2, "pic", "Worked example: a mapped song", "form",
     "Class 2. This is an original practice map, not a real song, so the numbers are easy to check: 72 bars at 100 BPM. One bar of 4/4 "
     "at 100 BPM lasts 2.4 seconds, so the second verse starts at bar 29, 67.2 seconds in (1:07), and the whole map runs 2:53. Students' maps come "
     "from their own song; check each one before they open Logic."),
    (2, "steps", "Watch me: tempo and markers", "Count the beats for 15 seconds, then × 4 = BPM|Set the project tempo to match|Metronome "
     "on (K): play the song alongside it|Global Tracks (G): one Arrangement Marker per section|Save as: Your Name – Billboard Top 10",
     "A three-minute demo. Count beats for 15 seconds: 25 beats times 4 is 100 BPM. Set the project tempo, turn on the metronome and "
     "play the song next to it; if the click drifts, nudge the tempo by one. Then Global Tracks, Arrangement track: add one marker per "
     "section, sized to its bars, named as on the Song Form map. The requirement is to match the tempo exactly."),
    (2, "pic", "Worked example: break down the drums", "drums",
     "Break the beat into kick, snare and hi-hat, one sound at a time: listen for the hi-hat first, then the snare, then the kick. "
     "In this practice example the verse is laid back and the chorus pushes, with a kick on every beat. The velocity lane shows my tip "
     "against robotic drums: accents on the beat, softer hits between."),
    (2, "steps", "Watch me: program the drums", "New track: an Electronic Drum Kit (Drum Machine Designer)|Pattern region at the first "
     "verse marker|Kick, snare, hi-hat first: copy what you hear|Vary the velocity so it doesn’t sound robotic|Copy it into every section "
     "that uses it",
     "A short demo. An Electronic Drum Kit loads Drum Machine Designer. Control-click at the first verse marker, Create Pattern Region, "
     "double-click for the Step Sequencer. Program what you hear, then vary velocity and nudge a few notes for human feel. Drum patterns "
     "must be self-created; percussion loops only as accents."),
    (3, "bullets", "Build your foundation", "Bass, chords and core instruments|Match the original’s energy, section by section|Pick "
     "sounds that fit the genre|Your drums are the backbone",
     "Class 3 is the first working day. Step 4 of the project sheet: lay down bass, chords and core instrumentation to match the original’s "
     "energy. Circulate with the song form maps in hand. My tip to repeat: your drums are the backbone; if the beat doesn’t feel right, "
     "the whole track will feel off."),
    (4, "bullets", "Add layers", "Melodies, pads, FX and transitions|Match the fullness of the original|Capture the vibe, structure and "
     "energy|You don’t need every single sound",
     "Class 4, a working day. Step 5: fill in melodies, pads, FX and transitions to match the fullness of the original. From my tips: "
     "don’t try to perfectly match every single sound; focus on capturing the vibe, structure and energy. Class 5 is a full working day "
     "with no new slide: refine the arrangement."),
    (6, "bullets", "Mix and refine", "EQ every track|Pan for width|Adjust levels|Add plug-ins for authenticity",
     "Class 6, final mix and bounce. The four parts of step 6 of the sheet, shortened to fit the slide; the full step is on the "
     "project sheet. My notes warn that students copy the arrangement but "
     "ignore the mix, and the EQ and panning step often gets skipped, so make it visible: ask every student to show you one EQ and one pan "
     "change before they bounce."),
    (6, "check", "What you turn in", "Top 10 analysis completed|Song form as Arrangement Markers in Logic|Bounced .mp3 or .wav uploaded|"
     "Zipped .logicx project uploaded|Named: Your Name – Billboard Top 10|Padlet post with your 3 questions|Answer 2 questions on "
     "classmates’ posts",
     "The submission checklist from the project sheet, condensed. Export: File, Bounce, Project or Section, MP3 or WAV. Compress: in "
     "Finder, Control-click the .logicx project and choose Compress. Show where students upload (your class page) and where the Padlet "
     "board is."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play your track for the class|Your Padlet post: 3 questions about your project|Answer at least 2 "
     "of each classmate’s 3|Listen like a producer: what made it work?",
     "Class 7, presentations with Padlet Q and A. Each student plays their track and says which song they recreated. During classmates’ "
     "presentations, every student answers at least 2 of their 3 questions on their Padlet post. Keep the original song available in "
     "case the class wants to compare a section."),
    (7, "closer", "One last thing…", "You studied a hit.|You matched its tempo and form.|You built the drums yourself.|You listened like a "
     "producer.",
     "Close with what my teacher notes say this project does: it teaches students to listen analytically rather than passively. They "
     "matched a real hit’s tempo, form and instrumentation with precision, and still made creative production choices of their own. "
     "That is how producers learn."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("formmap", "Song Form map", "count the bars first"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 7, 9, 8, 15]
SHOTS3 = [("analysis", "Top 10 analysis"), ("drums", "Drum patterns"), ("example", "Worked example"), ("proj1", "Project sheet"),
          ("proj2", "Steps"), ("vocab", "Vocabulary"), ("present", "Feedback planner"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "changes", "logicref", "example",
        "analysis", "formmap", "drums", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "formmap", "proj2", "rubric"]

COVER_A = "Recreate a hit in Logic Pro"
COVER_C = "DMP2 · song form · tempo · drum programming · mixing · intro slides"
PDF_COVER = dict(a=32, b=67, c=15, art=7.3)
SQ_COVER = dict(a=50, b=134, c=28, art=700)
SQ_B_LINES = ["Billboard", "Top 10"]
SQ_SUB = "7 class periods · song form · drums · mix · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Analysis, song form map, drums, project sheet, vocabulary, feedback", 28)}
SQ_BANDS = {1: "Listen <em>·</em> map <em>·</em> program <em>·</em> mix <em>·</em> present",
            2: "Hook <em>·</em> listen <em>·</em> worked example <em>·</em> steps <em>·</em> rubric",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no songs included"}

SONG_NOTE = ("No songs, audio, video, lyrics or chart data are included. Students choose from the current chart on billboard.com and "
             "listen on YouTube or Spotify through your school’s own access.")
TM_NOTE = ("Billboard and Hot 100 are trademarks of their owner, named only to describe the chart students listen to; this resource is not "
           "affiliated with or endorsed by Billboard.")
CREDITS = ["Practice map, drum grids, chart drawing and layouts: original work, Hudson Beat.",
           "No songs, audio, video, lyrics, album art or chart data are included. Songs are named for reference only (title and artist); "
           "play them from your own YouTube or Spotify access. Song titles belong to their owners; this resource is not affiliated with or "
           "endorsed by the artists or their labels.",
           TM_NOTE + " Padlet, YouTube and Spotify are named only as examples of tools you may already use."]
LOGIC_INTRO = ("Everything students need in Logic for this project, in one table. Demonstrate the tempo and markers (slide 8) and the "
               "drums (slide 10), then let students work.")
LOGIC_REF = [("Tempo", "Count the song’s beats for 15 seconds and multiply by 4. Double-click the tempo in the control bar and type it in. "
              "Turn on the metronome (K) and play the song alongside it: if the click drifts, adjust by 1 BPM."),
             ("Arrangement Markers", "Turn on Global Tracks (G). In the Arrangement track, click + to add a marker, drag its edges to fit "
              "the section’s bars, and rename it (Intro, Verse 1, Chorus…)."),
             ("Drum track", "Track › New Software Instrument Track; in the Library (Y) choose a kit under Electronic Drum Kit. This loads "
              "Drum Machine Designer."),
             ("Pattern region", "Control-click in the drum track at a marker and choose Create Pattern Region. Double-click it to open the "
              "Step Sequencer; click steps to turn hits on."),
             ("Velocity", "In the Step Sequencer, switch the edit mode to Velocity and drag hits up or down; in the Piano Roll, select notes "
              "and use the Velocity slider."),
             ("Copy a section", "Option-drag a region to copy it, or select it and press Command-R to repeat it."),
             ("EQ and pan", "Open the Mixer (X). Double-click the EQ display at the top of a channel strip to open Channel EQ; turn the Pan "
              "knob to place the track left or right."),
             ("Percussion accents", "Loop Browser (O): percussion Apple Loops are allowed as accents only; the main drum patterns are "
              "programmed by the student."),
             ("Bounce and zip", "File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx project "
              "and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; .mp3 or .wav and zipped .logicx uploaded", "Padlet post created with my 3 questions",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my project:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:11.4pt;margin-bottom:3pt">Songs that are too complex: “Songs that work well” on page @SETUP, and the “Clear sections?” '
    'column of the Top 10 analysis (page @ANALYSIS).</li>'
    '<li style="font-size:11.4pt;margin-bottom:3pt">Skipped bar counts: the Song Form map (page @FORMMAP) has a bar column and a length check.</li>'
    '<li style="font-size:11.4pt;margin-bottom:3pt">Robotic drums: the velocity lane in the worked example (page @EXAMPLE) and slide 9.</li>'
    '<li style="font-size:11.4pt;margin-bottom:0">A skipped mix: slide 13 puts EQ, pan, levels and plug-ins on the screen in Class 6.</li></ul></div>')
TN1_SIZE = 13.4
PROJ_SIZE = 13
VOCAB_GAP = 14
LOGIC_SIZE = 13
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example", "How to use, overview, setup, pacing, teacher notes, what changed, Logic reference, "
              "worked example"),
             ("Student pages", "analysis", "reflect", "Top 10 analysis, Song Form map, drum patterns, project sheet (3 pages), rubric, "
              "vocabulary, feedback planner, reflection"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:11pt">A {CLASSES}-class-period project for high school music technology. Students study the current Billboard '
             f'Top 10, pick one song and recreate it in Logic Pro: the same tempo, the exact song form, drums they program themselves, '
             f'instruments that fit the genre, and a mix with EQ and plug-ins. It is a structured project from my Digital Music Production 2 '
             f'course (focus: song form and drums), and the projects in that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li>Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li>Check this week’s Top 10 on billboard.com and preview the songs (page {D.IX("setup")}).</li>'
             f'<li>Print the student pages (pages {D.IX("analysis")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Class 5 is a working day with no new slide. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No songs included</span><p style="margin:0">{SONG_NOTE}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>The chart changes every week.</b> Use the Top 10 of the week you start; students keep their song even if it drops.</li>'
             f'<li><b>Song choice:</b> preview the ten songs and point students to clean versions, or offer an approved list.</li>'
             f'<li><b>Shorter or harder:</b> my variations on page {D.IX("tn1")}.</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<p class="small">{TM_NOTE}</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12pt;line-height:1.42">One Logic Pro project: their own version of a song from the current Billboard Top 10, at the original '
             f'tempo and in the original song form, with Arrangement Markers for every section, drum patterns they programmed themselves, '
             f'instruments and layers that fit the genre, and EQ, panning and plug-ins. They hand in a bounced .mp3 or .wav, the zipped '
             f'.logicx project, the Top 10 analysis, and a Padlet post with three feedback questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12pt;line-height:1.42">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p>Supports the National Core Arts Standards for Music (Music Technology, high school): analyzing how '
             f'musical works are structured (MU:Re7.2), developing and refining work (MU:Cr2.1, MU:Cr3.1) and presenting it (MU:Pr6.1).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:11.8pt;line-height:1.4'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:10.4pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: explore and map, drums, three working days, mix, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: tempo and metronome, Arrangement Markers, Drum Machine Designer and the Step '
             f'Sequencer, Channel EQ, pan, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Access to the current chart and the songs (YouTube or Spotify), headphones, a feedback '
             f'board</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0">Students should already '
             f'know how to make a drum pattern, play in parts and save, bounce and zip a project in Logic. The Logic quick reference '
             f'(page {D.IX("logicref")}) covers every tool this project uses.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Structured", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<div class="cols"><div class="big">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student (a current version: the Step Sequencer and pattern regions came in Logic '
             f'Pro X 10.5), and <b>headphones</b>.</li>'
             f'<li><b>The current chart</b>: the Billboard Hot 100 on billboard.com, top 10 songs.</li>'
             f'<li><b>A way to play the songs</b>: YouTube or Spotify through your school’s own access. Nothing is included.</li>'
             f'<li><b>A place to submit</b> an .mp3 or .wav and a zipped .logicx project (your class page).</li>'
             f'<li><b>A feedback board</b> for the three questions (my sheets use Padlet).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("analysis")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("A MIDI keyboard?")}<p>Helpful for bass, chords and melodies, not required: notes can be drawn in the Piano Roll.</p>'
             f'</div><div class="big">'
             f'{D.H2("Before Class 1", True)}'
             + "".join(D.chk(c, 13, "font-size:12pt;margin-bottom:8pt") for c in [
                 "Open this week’s Hot 100 and list the top 10 songs.",
                 "Preview all ten. Note clean versions, or make an approved list for your school.",
                 "Note which songs have clear, easy-to-hear sections (my first common struggle).",
                 "Test the class speakers; cue up the No. 1 for slide 2.",
                 "Print the student pages; set up the submission spot and the feedback board."]) +
             f'{D.H2("Before Class 2")}'
             + "".join(D.chk(c, 13, "font-size:12pt;margin-bottom:8pt") for c in [
                 "Skim every Song Form map: sections, bar counts, start times.",
                 "Have the worked example (page " + str(D.IX("example")) + ") ready for the tempo and drums demos."]) +
             f'</div></div>'
             f'<div class="cols" style="margin-top:8pt;gap:14pt"><div class="box acc-b"><span class="k">Songs that work well</span><ul style="margin:0">'
             f'<li style="font-size:11.4pt">Clear, identifiable sections: you can hear where the chorus starts</li>'
             f'<li style="font-size:11.4pt">A steady beat you can count, and drums you can pick out</li>'
             f'<li style="font-size:11.4pt">A clean version your school is comfortable with</li></ul></div>'
             f'<div class="box"><span class="k">Songs that will be hard</span><ul style="margin:0">'
             f'<li style="font-size:11.4pt">Heavily layered pop or hip-hop with 50+ tracks (my teacher notes)</li>'
             f'<li style="font-size:11.4pt">Tempo changes, or long sections with no beat</li>'
             f'<li style="font-size:11.4pt">If a student insists: the easier variation, the first 1–2 minutes</li></ul></div></div>')
    return D.page("Setup and requirements", "SETUP", "Teacher", inner, n, key="setup")


def example_page(n, wm=False):
    st = starts()
    rows = "".join(f"<tr><td><b>{sec}</b></td><td>{s}–{s + nb - 1}</td><td>{nb}</td><td>{bar_time(s)}</td>"
                   f"<td>{WHAT[sec.split()[0]][0]}</td></tr>" for (sec, nb), s in zip(FORM, st))
    lanes = [ln for ln in LANES if ln in VERSE or ln in CHORUS]
    steps = "".join(f"<tr><td><b>{ln}</b></td><td class='stp'>{VERSE.get(ln, '—')}</td><td class='stp'>{CHORUS.get(ln, '—')}</td></tr>"
                    for ln in lanes)
    inner = (f'<p style="margin:0 0 4pt">An <b>original practice map, not a real song</b>, so you can model each step with numbers that are '
             f'easy to check. Students’ maps come from their own song.</p>'
             f'<div class="box" style="margin-bottom:2pt"><span class="k">1 · Tempo</span><p style="margin:0">Count the beats for 15 seconds: '
             f'{BEATS_15S} beats × 4 = <b>{BEATS_15S * 4} BPM</b>. One bar of 4/4 lasts 240 ÷ {TEMPO} = {bar_secs():.1f} seconds.</p></div>'
             f'{D.H2("2 · Song form")}<div style="width:6.7in;margin:2pt auto 3pt">{D.body_svg(form_drawing(1250, 96))}</div>'
             f'<table class="t" style="font-size:9.6pt"><tr><th style="width:13%">Section</th><th style="width:11%">Bars</th><th style="width:9%">Length'
             f'</th><th style="width:10%">Starts</th><th>What’s happening</th></tr>{rows}</table>'
             f'<p class="small" style="margin:0 0 4pt">{" + ".join(str(nb) for _, nb in FORM)} = {TOTAL_BARS} bars × {bar_secs():.1f} s = '
             f'{TOTAL_BARS * bar_secs():.1f} s ({mmss(TOTAL_BARS * bar_secs())}). Start time = (bar − 1) × {bar_secs():.1f} s, rounded. '
             f'Bars in the white meter on each block: how full the section is (1–4).</p>'
             f'{D.H2("3 · Drums (x = a hit, . = a rest, 16 steps per bar)")}'
             f'<div style="width:5.5in;margin:1pt auto 2pt">{D.body_svg(drums_drawing(17, 21, "page"))}</div>'
             f'<table class="t" style="font-size:9.4pt"><tr><th style="width:20%">Sound</th><th>Verse groove</th><th>Chorus groove</th></tr>{steps}</table>'
             f'<p class="small" style="margin:0">Velocity: verse hi-hats {VERSE_HAT_VEL[0]} on the beat, {VERSE_HAT_VEL[2]} between (of 127). '
             f'The bridge keeps only the verse kick; the intro and outro have no drums.</p>')
    return D.page("Worked example · a practice map", "EXAMPLE", "Teacher", inner, n, ak=True, key="example")


def analysis_page(n, wm=False):
    rows = "".join(f"<tr><td style='text-align:center'><b>{i}</b></td><td></td><td></td><td></td><td></td><td></td></tr>" for i in range(1, 11))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Listen to all 10 songs from this week’s Billboard Top 10 with headphones. Fill in a row '
             f'for each one, then choose the song you will recreate.</p>'
             f'<div class="fl"><b>Chart week of:</b><span style="flex:0 0 1.6in"></span><b>Where I listened:</b><span></span></div>'
             f'<table class="map"><tr><th style="width:5%">#</th><th style="width:22%">Song</th><th style="width:18%">Artist</th>'
             f'<th style="width:14%">Tempo (slow / med / fast)</th><th style="width:15%">Genre / style</th><th>Clear sections? Instruments I hear</th></tr>'
             f'{rows}</table>'
             f'{D.H2("My song")}'
             f'<div class="fl"><b>Song:</b><span></span><b>Artist:</b><span></span><b>Rank:</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Why this one?</b><span></span></div><div class="ln2" style="margin-bottom:8pt"></div>'
             f'<div class="fl"><b>Can I hear where each section starts? Which sections does it have?</b><span></span></div>'
             f'<div class="fl"><b>About how many layers (instruments and sounds) does it have?</b><span style="flex:0 0 1in"></span></div>'
             f'<div class="fl"><b>What do the drums do in the chorus?</b><span></span></div>')
    return D.page("Top 10 analysis", "STUDENT", "Class 1", inner, n, wm, name=True, key="analysis")


def formmap_page(n, wm=False):
    rows = "".join(f"<tr><td style='text-align:center'>{i}</td><td></td><td></td><td></td><td></td><td style='text-align:center'>{D.checkbox(12)}</td></tr>"
                   for i in range(1, 13))
    inner = (f'<div class="fl"><b>Song:</b><span></span><b>Artist:</b><span></span></div>'
             f'<div class="fl"><b>Beats in 15 seconds:</b><span style="flex:0 0 0.7in"></span><b>× 4 = Tempo (BPM):</b>'
             f'<span style="flex:0 0 0.8in"></span><b>Checked with the metronome?</b><span style="flex:0 0 0.6in"></span></div>'
             f'<p style="margin:0 0 5pt">Listen with headphones and count the bars: 1, 2, 3, 4, then say the bar number on every 1. '
             f'Write each section in order (intro, verse, pre-chorus, chorus, bridge, outro…).</p>'
             f'<table class="map"><tr><th style="width:5%">#</th><th style="width:17%">Section</th><th style="width:13%">Starts at (m:ss)</th>'
             f'<th style="width:10%">Bars</th><th>What’s happening (instruments, energy, drums)</th><th style="width:11%">Marker in Logic</th></tr>'
             f'{rows}</table>'
             f'<div class="fl" style="margin-top:9pt"><b>Total bars:</b><span style="flex:0 0 0.8in"></span><b>× (240 ÷ BPM) =</b>'
             f'<span style="flex:0 0 0.8in"></span><b>seconds. The song is</b><span style="flex:0 0 0.8in"></span><b>long. Close?</b>'
             f'<span style="flex:0 0 0.5in"></span></div>'
             f'<div class="box acc-b"><span class="k">Finish this before you open Logic</span><p style="margin:0">Your teacher checks this '
             f'map in Class 2. Then each row becomes an Arrangement Marker, sized to its bars.</p></div>')
    return D.page("Song Form map", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="formmap")


def drums_page(n, wm=False):
    lanes = ["Open hi-hat", "Closed hi-hat", "Snare / clap", "Kick", "Other:"]
    cells = ""
    for i in range(3):
        g = D.grid_body(f"blank {i}", [{}], [], lanes, cw=34, ch=27, gut=160, ls=17, blank=True)
        cells += (f'<div style="margin:0 0 7pt"><div class="fl" style="margin:0 0 3pt"><b>Section:</b><span style="flex:0 0 1.6in"></span>'
                  f'<b>Bars:</b><span style="flex:0 0 0.6in"></span><b>What I hear:</b><span></span></div>'
                  f'<div style="width:6.6in;margin:0 auto">{D.body_svg(g)}</div></div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Pick the sections with different drums (usually verse and chorus). Listen for one '
             f'sound at a time: hi-hat first, then snare or clap, then kick. Fill a square for each hit. Each square is a sixteenth note; '
             f'grey columns are the beats.</p>{cells}'
             f'<div class="cols" style="gap:12pt"><div class="box"><span class="k">Make it human</span><p style="margin:0">Mark the loudest hits '
             f'with a dot. Vary velocity and nudge a few notes so it doesn’t sound robotic.</p></div>'
             f'<div class="box"><span class="k">Rule</span><p style="margin:0">{REQS[3]}.</p></div></div>')
    return D.page("Drum pattern analysis", "STUDENT", "Class 2", inner, n, wm, name=True, key="drums")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "analysis": analysis_page,
         "formmap": formmap_page, "drums": drums_page}


# ================================================================ content checks (music arithmetic, owner text, songs)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 5), reqs=(REQS, 6), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 7),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 4))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp} (the owner's count)")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is the owner's /25, levels 1-5")
    if [c for c, _ in RUBRIC] != ["Creativity & Originality", "Technical Skill / DAW Use", "Composition & Structure",
                                  "Sound Design & Mix Quality", "Documentation & Presentation"]:
        errs.append("rubric categories must be the owner's, in order")
    if FILE_NAME not in CHECK[4] or "Billboard Top 10" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    # the worked example adds up
    st = starts()
    if TOTAL_BARS != 72 or st[-1] + FORM[-1][1] - 1 != TOTAL_BARS or BEATS_15S * 4 != TEMPO:
        errs.append("practice map arithmetic")
    if abs(bar_secs() - 2.4) > 1e-9 or mmss(TOTAL_BARS * bar_secs()) != "2:53" or bar_time(29) != "1:07":
        errs.append("practice map times")
    for nm, p in (("verse", VERSE), ("chorus", CHORUS)):
        if p["Snare"][4] != "x" or p["Snare"][12] != "x" or p["Kick"][0] != "x" or any(len(s) != 16 for s in p.values()):
            errs.append(f"{nm} groove: snare on 2 and 4, kick on 1, 16 steps")
        if len([ln for ln in p if "x" in p[ln]]) < 3:
            errs.append(f"{nm} groove: kick, snare and hi-hat at minimum")
    if CHORUS["Kick"] != "x...x...x...x..." or CHORUS["Clap"] != CHORUS["Snare"] or set(CHORUS["Open hi-hat"][i] for i in (2, 6, 10, 14)) != {"x"}:
        errs.append("chorus groove must match its description (kick every beat, clap doubles snare, open hats off the beat)")
    if [i for i, v in enumerate(VERSE_HAT_VEL) if v] != [i for i, c in enumerate(VERSE["Closed hi-hat"]) if c == "x"]:
        errs.append("velocity lane must match the verse hi-hats")
    if any(not (1 <= v <= 127) for v in VERSE_HAT_VEL if v):
        errs.append("velocities must be 1-127")
    # no songs beyond the owner's one example; songs by title and artist only
    alltxt = " ".join(str(x) for x in (SLIDES, RESOURCES, STEPS, REQS, CHECK, SONG_NOTE))
    if alltxt.count("Bieber") != 1:
        errs.append("the only song named is the owner's example (Sorry, Justin Bieber), once, in the resource list")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    if "YouTube or Spotify" not in notes[0] or "no audio" not in notes[0]:
        errs.append("deck slide 1 notes: YouTube or Spotify, no audio included")
    if "YouTube or Spotify" not in stext[1]:
        errs.append("deck slide 2 (song): must say YouTube or Spotify on the slide")
    if "Bieber" in alldeck:
        errs.append("deck must not name songs")
    txt = " ".join(flat)
    for need in ("No songs, audio, video, lyrics or chart data are included", "not affiliated with or endorsed by Billboard",
                 "original practice map, not a real song", "Your Name – Billboard Top 10", "Final Grade = Average of Student + Teacher"):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    # QA round 1 fixes: grades 9-12 (METADATA-GUIDE), slide 13 note truthful about the shortened step 6, grading tips labelled
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "shortened" not in notes[12] or "word by word" in notes[12] or SLIDES[12][2] != "Mix and refine":
        errs.append("deck slide 13 notes: must say step 6 is shortened, never 'word by word'")
    ch = flat[D.IX("changes") - 1]
    if "slide 13" not in ch or "EQ every track · Pan for width · Adjust levels · Add plug-ins for authenticity" not in ch:
        errs.append("'What changed' page must list the shortened step 6 on slide 13")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or tn2.find("nothing clipping") < lab or any("clipping" in g for g in GRADING):
        errs.append("page tn2: 'nothing clipping' must sit under the kit-suggestions label, never in the owner's rubric line")
    for gone in ("Google Form analysis", "Song Form spreadsheet before", "complete Google Form"):
        if gone in txt and gone not in flat[D.IX("changes") - 1]:
            errs.append(f"old wording '{gone}' outside the changes page")
    return errs


def check_summary():
    return (f"Practice map {TOTAL_BARS} bars at {TEMPO} BPM = {mmss(TOTAL_BARS * bar_secs())} ({BEATS_15S} beats in 15 s x 4); verse and "
            f"chorus grooves checked (kick on 1, snare on 2 and 4, chorus kick every beat, clap = snare), velocity lane matches the "
            f"hi-hats; the owner's lists counted (4 goals, 5 terms, 6 requirements, 7 steps, 4 tips, 7 checklist items, 4 struggles); "
            f"{len(CHANGES)} wording changes disclosed (incl. the deck's shortened step 6); grades 9-12; grading tips labelled as "
            f"suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
