#!/usr/bin/env python3
"""DMP2 project: Sample Flipping (TpT 015): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > Sample Flipping > "Sample Flipping - Project Sheet & Rubric" (rubric 5 categories scored 1-5, /25,
final grade = average of student and teacher scores), TEACHER NOTES > "Sample Flipping - Teacher Notes" (7 class periods),
and the project's entry on "DMP2 - Project Menu". Every change to the owner's wording is listed in CHANGES and printed on the
"What changed from the original" page.

NO SAMPLES ARE INCLUDED. The owner's class sample set (in Drive) is not clearly his own work or licensed for
resale (inventory open question 7), so the kit describes how a teacher supplies their own cleared sample set instead.
The worked example is an original practice sample described on paper only. No audio, lyrics or chart data; no songs named.
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "sample-flipping"
TITLE = "Sample Flipping"
ACCENT = "#B07D00"          # this product's single accent: gold (008 red, 009 orange, 010 violet, 011 teal, 012 blue, 013 green, 014 magenta)
ACC_LIGHT = "#F3DF9C"
PRICE = "12.00"
CLASSES = 7
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-013).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "Sample Flipping in Logic Pro | Quick Sampler Project | High School Music Tech"
DESC_START = "Sampling and Quick Sampler for high school music technology:"
DESC_MUST = ["Sample Flipping", "Quick Sampler", "no samples", "your own cleared"]
ZIP_DIR = "Sample Flipping - Hudson Beat"
ZIP_DATE = (2026, 10, 15, 12, 0, 0)
TYPE = "Open-Ended Project"
PROJ_LINE = "Digital Music Production | <i>Open-Ended Project</i> | 7 class periods"
DECK_STRAP = "Chop, pitch and flip in Logic Pro"
LIVE = True                 # already live on TpT (uploaded/release files belong to the Manager); this rebuild is for the later re-upload
BANNED_EXTRA = ["50 Vocal" + " Samples", "Rivals" + " 01", "COY" + "_", "Vocal Chop" + " Loop"]

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Open-Ended", "Sampling & Quick Sampler"
MENU_DESC = "Transform a provided sample into an original track using Logic’s Quick Sampler. Chop, pitch, flip, and build."
OVERVIEW = ("Take one of the provided samples and flip it into something entirely your own. Using Logic’s Quick Sampler, you’ll chop, "
            "stretch, pitch, and manipulate the sample to build an original track around it. This is how some of the biggest producers "
            "in hip-hop, R&amp;B, and electronic music work.")
GOALS = ["Learn to use Quick Sampler for creative sample manipulation",
         "Understand the art and ethics of sample-based production",
         "Develop drum programming skills with self-created patterns",
         "Build a complete, original track from a single source sample"]
VOCAB = [("Sample", "A recorded piece of audio used as raw material in a new composition"),
         ("Quick Sampler", "A Logic Pro instrument that lets you import, slice, and play back audio samples"),
         ("Flipping", "Transforming a sample into something new through chopping, pitching, or reversing"),
         ("Chopping", "Cutting a sample into smaller pieces to rearrange and replay")]
REQS = ["Choose one sample from the provided options (my class set has 50; page @SETUP shows how to build yours)",
        "Use Quick Sampler to manipulate and transform the sample",
        "Key and tempo are up to you — make sure they fit the sample",
        "Drum patterns must be self-created",
        "Use layers appropriate to the style",
        "Apply EQ and plug-ins to polish your mix"]
STEPS = ["<b>Listen and choose</b> — Browse the provided samples and select one (log your choices on page @PICK)",
         "<b>Learn Quick Sampler</b> — Import your sample and experiment with slicing, pitching, and playback modes (reference: page @LOGICREF)",
         "<b>Build your beat</b> — Program your own drum pattern that fits the style (page @DRUMS)",
         "<b>Layer and arrange</b> — Add bass, chords, melodies, and additional elements",
         "<b>Mix</b> — EQ, pan, and balance everything",
         "<b>Finalize</b> — Bounce your track and prepare your presentation",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["Spend real time experimenting in Quick Sampler before building the full track.",
        "Try reversing, pitching down, or isolating just one small section of the sample.",
        "Your drums set the tone. Match the drum style to whatever genre your flip is heading toward.",
        "Listen to classic sample-based producers (J Dilla, Kanye, Madlib) for inspiration."]
FILE_NAME = "“Your Name – Sample Flipping”"
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
TN_REINFORCES = ("Builds Quick Sampler proficiency, drum programming, and creative transformation skills. Natural entry point for "
                 "discussing sampling ethics and copyright.")
STRUGGLES = ["Students use the sample without transforming it — push them to actually chop, pitch, or manipulate.",
             "Quick Sampler modes are confusing. Demo Classic, One Shot, and Slice modes early.",
             "Drums feel generic or disconnected from the sample.",
             "Students give up quickly if the sample doesn’t immediately sound cool."]
VAR_EASY = "Pre-slice a few samples and provide them as ready-to-play Quick Sampler instruments."
VAR_HARD = "Require 2 samples in the same track, or multiple Quick Sampler instruments from a single source."
RESOURCES = [("Quick Sampler — Turn Any Sound into an Instrument (YouTube)",
              "Not included: it is a video on YouTube, so search it by title. Slides 8 and 9 and the Logic reference (page @LOGICREF) cover "
              "the same ground."),
             ("Advanced Quick Sampler Techniques (YouTube)", "Not included: search it by title. The worked example (page @EXAMPLE) shows "
              "the chop, reverse and pitch moves on paper."),
             ("50 provided samples (on your class page)", "Not included. Page @SETUP shows how to build a set of your own cleared samples, "
              "and page @ETHICS helps you talk about where they came from.")]
TN_NOTE = "Usually one of the most popular projects."
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Technical Skill: ask the student to open Quick Sampler and show the mode they used and one thing they did to the sample "
                "(a chop, a reverse, a pitch change).",
                "Creativity: play the raw sample, then the track. Can you hear what changed, and did the student make something new "
                "around it?",
                "Documentation &amp; Presentation: the Sample log (page @PICK) and the three Padlet questions are the evidence, along with the Reflection page (page @REFLECT)."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Introduction to sample flipping and Quick Sampler demo. Select sample.",
     "do": "Slides 1–6: hook (before and after), what flipping is, sampling ethics, the seven classes, step 1. Hand out the project "
           "sheet and the Sample log.", "slides": (1, 6), "pages": ["pick", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Before and after · what flipping is · ethics · choose a sample"},
    {"n": 2, "owner": "<b>Class 2:</b> Deep dive into Quick Sampler manipulation. Begin building.",
     "do": "Slides 7–10: slice a sample, the three Quick Sampler modes, a flip, drums that fit. Demo Classic, One Shot and Slice "
           "before students start.", "slides": (7, 10), "pages": ["chops", "drums"],
     "deck": "Slice it · the three modes · flip it · drums that fit"},
    {"n": 3, "owner": "<b>Classes 3–5:</b> Working days — build track, layer instruments, refine.",
     "do": "Slide 11: build the beat and the chops. Then work time; circulate.", "slides": (11, 11), "pages": [],
     "deck": "Working day: build your beat"},
    {"n": 4, "owner": None, "do": "Slide 12: layer and arrange (bass, chords, melodies). Then work time.", "slides": (12, 12),
     "pages": [], "deck": "Working day: layer and arrange"},
    {"n": 5, "owner": None, "do": "Full working day: refine the track. Ask each student to play the raw sample, then the track.",
     "slides": None, "pages": [], "deck": "Working day: refine"},
    {"n": 6, "owner": "<b>Class 6:</b> Final mix, bounce. Prepare presentations.",
     "do": "Slides 13–15: mix and bounce, what you turn in, the rubric. Students self-score, bounce and post their three questions.",
     "slides": (13, 15), "pages": ["rubric", "present"], "deck": "Mix and bounce · checklist · rubric · 3 questions"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 16–17: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (16, 17), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:8pt;gap:14pt"><div class="box acc-b"><span class="k">The one rule for Class 2</span>'
    '<p style="margin:0;font-size:11pt">From my common struggles: demo Classic, One Shot and Slice early. Slide 8 is that demo, and the '
    'Logic reference (page @LOGICREF) is the handout.</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:11pt">Working days. Slides 11 and 12 open Classes 3 '
    'and 4; Class 5 has no new slide. Circulate and ask: what did you do to the sample, and could I hear the original in your track?</p></div></div>')

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (checklist items 1 and 2, and the sample-set line in my resource list).",
    "This kit includes no samples. Requirement 1 reads “from the provided options (my class set has 50; page @SETUP shows how to "
    "build yours)” instead of “from the 50 provided options”, and my resource “50 provided samples” points to page @SETUP.",
    "Page numbers are added to steps 1–3 (the Sample log, the Logic reference and the drum plan).",
    "My two YouTube resources are named by title only; the videos are not included.",
    "My pacing guide’s “Classes 3–5” row spans the Class 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 8 shortens the three Quick Sampler modes from "
    "my struggle list, and slides 11, 12 and 13 shorten steps 3 to 6 into short lines.",
]
CHANGES_MUST_MENTION = ["your class page", "includes no samples", "Page numbers", "title only", "Classes 3–5", "Layout only",
                        "intro deck shortens"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the overview, goals, vocabulary, requirements 2 to 6, steps, "
        "tips, checklist and file name (“Your Name – Sample Flipping”), the rubric (five categories scored 1–5, /25, the average of "
        "the student’s and the teacher’s score), what the project reinforces, the four common struggles, the variations, my day-by-day "
        "pacing and my closing note, and the project menu entry quoted on page @OVERVIEW. No rubric row is added and the requirements are unchanged.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: how to use the kit, the overview and setup "
                "pages (including how to build a cleared sample set), the sampling ethics page, the teacher moves and slide numbers in the "
                "pacing guide, the grading suggestions, the Logic quick reference, the worked example (an original practice sample "
                "described on paper, not a recording), the Sample log, the Chop map, the drum plan, the vocabulary page, the "
                "presentation planner and the intro deck. None of these adds a requirement or a rubric row.")

# ================================================================ the worked example (Hudson Beat original: a practice sample on paper)
TEMPO = 100
NSLICE = 8
BEATS_PER_SLICE = 2
SLICE_WHAT = ["Long soft “ah” that swells", "A breath", "Short bright “hey”", "Low hummed note", "Two quick syllables", "Held high note",
              "Rising slide", "Short low stab"]
FLIP = [(1, ""), (1, ""), (4, ""), (2, "rev"), (6, ""), (3, "rev"), (5, ""), (8, "−12")]   # 8 slots of 2 beats: slice, treatment
TREAT = {"": "as recorded", "rev": "reversed", "−12": "down an octave"}
DRUM = {"Closed hi-hat": "x.x.x.x.x.x.x.x.", "Snare": "....x.......x...", "Kick": "x.....x.x......."}
DRUM_LANES = ["Closed hi-hat", "Snare", "Kick"]


def beat_secs(bpm=TEMPO):
    return 60 / bpm


def bar_secs(bpm=TEMPO):
    return 4 * beat_secs(bpm)


SLICE_SECS = BEATS_PER_SLICE * beat_secs()           # 1.2 s
TOTAL_SECS = NSLICE * SLICE_SECS                     # 9.6 s = 4 bars


def sec(x):
    return f"{x:.1f} s"


# ================================================================ drawings (original, code-drawn: black + accent only)
def wave_body(W=1600, h=190, name="wave", numbers=True):
    """A made-up waveform cut into 8 slices: one burst per slice, slice lines in the accent, start times under the slices."""
    out, n = [], 160
    bw = (W - 4) / n
    top = 46 if numbers else 6
    mid = top + h / 2
    for i in range(n):
        f = (i + .5) / n * NSLICE
        k = int(f)
        local = f - k
        env = (math.sin(math.pi * min(1, local * 1.15)) ** 0.7) * (0.45 + 0.55 * abs(math.sin(2.3 * k + 1.1)))
        a = max(0.07, env) * (0.88 + 0.12 * math.sin(i * 1.9))
        hh = a * h * 0.5
        out.append(f'<rect x="{2 + i * bw + 0.8:.1f}" y="{mid - hh:.1f}" width="{bw - 1.6:.1f}" height="{2 * hh:.1f}" rx="1.2" fill="#000"/>')
    sw = (W - 4) / NSLICE
    for k in range(NSLICE + 1):
        x = 2 + k * sw
        out.append(f'<line x1="{x:.1f}" y1="{top - 4}" x2="{x:.1f}" y2="{top + h + 4}" stroke="{ACCENT}" stroke-width="4"/>')
    for k in range(NSLICE):
        x = 2 + k * sw
        if numbers:
            out.append(f'<rect x="{x + sw / 2 - 24:.1f}" y="4" width="48" height="36" rx="9" fill="{ACCENT}"/>')
            out.append(D.t_(x + sw / 2, 31, str(k + 1), 28, 700, fill_="#fff"))
            D.lab(name, str(k + 1), 28, 40)
        out.append(D.t_(x + 8, top + h + 34, sec(k * SLICE_SECS), 24, 500, anchor="start"))
        D.lab(f"{name} times", sec(k * SLICE_SECS), 24, sw - 12)
    return "".join(out), W, top + h + 44


def flip_body(W=1600, name="flip", bh=96):
    """Row 1: the original slices in order. Row 2: the flip, 8 slots of 2 beats (reversed = accent, pitched = grey) with bar numbers."""
    out = []
    sw = (W - 4) / NSLICE
    out.append(D.t_(2, 26, "ORIGINAL ORDER", 24, 500, anchor="start"))
    D.lab(name, "ORIGINAL ORDER", 24, 400)
    for k in range(NSLICE):
        x = 2 + k * sw
        out.append(f'<rect x="{x + 3:.1f}" y="38" width="{sw - 6:.1f}" height="{bh * .62:.0f}" rx="8" fill="#9a9a9a"/>')
        out.append(D.t_(x + sw / 2, 38 + bh * .62 * .72, str(k + 1), 34, 700, fill_="#fff"))
        D.lab(name, str(k + 1), 34, sw - 20)
    y2 = 38 + bh * .62 + 40
    out.append(D.t_(2, y2 - 10, "THE FLIP", 24, 500, anchor="start", fill_=ACCENT))
    D.lab(name, "THE FLIP", 24, 400)
    for k, (sl, tr) in enumerate(FLIP):
        x = 2 + k * sw
        fill_ = ACCENT if tr == "rev" else ("#4a4a4a" if tr else "#000")
        out.append(f'<rect x="{x + 3:.1f}" y="{y2:.0f}" width="{sw - 6:.1f}" height="{bh}" rx="9" fill="{fill_}"/>')
        ns = round(min(52, bh * .5))
        out.append(D.t_(x + sw / 2, y2 + bh * (.5 if tr else .64), str(sl), ns, 700, fill_="#fff"))
        D.lab(name, str(sl), ns, sw - 20)
        if tr:
            tag = {"rev": "REVERSE", "−12": "DOWN 12"}[tr]
            ts = round(min(21, bh * .24))
            out.append(D.t_(x + sw / 2, y2 + bh * .88, tag, ts, 500, fill_="#fff"))
            D.lab(name, tag, ts, sw - 20)
    yb = y2 + bh + 14
    for b in range(4):
        x0, x1 = 2 + b * 2 * sw, 2 + (b + 1) * 2 * sw
        out.append(f'<line x1="{x0 + 3:.1f}" y1="{yb}" x2="{x1 - 3:.1f}" y2="{yb}" stroke="#000" stroke-width="3"/>')
        out.append(D.t_((x0 + x1) / 2, yb + 30, f"bar {b + 1}  ·  {sec(b * bar_secs())}", 24, 500))
        D.lab(f"{name} bars", f"bar {b + 1}  ·  {sec(b * bar_secs())}", 24, 2 * sw - 16)
    return "".join(out), W, yb + 40


def drums_drawing(cw=30, ch=34, name="drums"):
    return D.grid_body(f"{name} {cw}", [DRUM], [f"Self-made drums · {TEMPO} BPM"], DRUM_LANES, cw=cw, ch=ch, gut=170, ls=20)


def hero_body():
    return D.stack([wave_body(1600, 170, "hero wave"), flip_body(1600, "hero flip", 110),
                    D.grid_body("hero grid", [DRUM], [f"Self-made drums · {TEMPO} BPM"], DRUM_LANES, cw=58, ch=50, gut=230, ls=30)], 44)


DRAWINGS = {"hero": hero_body, "slices": lambda: wave_body(1600, 230, "slices pic"), "flip": lambda: flip_body(1600, "flip pic", 110)}
DRAWING_PX = {"hero": 1900, "slices": 2000, "flip": 2000}
SIDE = {"slices": [f"{NSLICE} slices of {sec(SLICE_SECS)}", f"{TOTAL_SECS:.1f} s = 4 bars at {TEMPO} BPM", "Each slice = 2 beats",
                   "Cut at the start of a sound"],
        "flip": ["8 slots of 2 beats, 4 bars", "Reverse slices 2 and 3", "Slice 8 down an octave", "Same slices, new order"]}


def label_extras():
    flip_body(1250, "page flip", 80)
    wave_body(1250, 110, "page wave")
    drums_drawing(30, 24, "page")


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Sample Flipping", "Chop. Pitch. Flip.",
     "Class 1, the first minute. Before class, pick one cleared sample from your own set (page 4 of the resource shows how to build "
     "one) and make a 30-second flip of it in Logic Pro. No audio is included in this deck. Open with my overview: take one sample and "
     "flip it into something entirely your own."),
    (1, "listen", "Listen: before and after", "Your own cleared sample, played twice|Teacher: play the raw sample, then your 30-second "
     "flip.|What did I do to it?|Which tiny piece did I use again and again?|Could you hear the original inside the new track?",
     "Play the raw sample first with no comment, then your flip. Take answers aloud: chopped, reversed, pitched, repeated, drums added. "
     "The point of the project is in my notes: students must actually chop, pitch or manipulate the sample, not just loop it. Keep your "
     "flip short and a bit rough on purpose."),
    (1, "bullets", "What the heck is flipping?", "Taking a sample and making something new from it|Chop it into pieces|Pitch it, "
     "reverse it, stretch it|Rearrange the pieces and build around them",
     "Plain-English definition from the project sheet vocabulary: a sample is a recorded piece of audio used as raw material; flipping "
     "is transforming it through chopping, pitching or reversing; chopping is cutting it into smaller pieces to rearrange and replay. "
     "From my overview: this is how some of the biggest producers in hip-hop, R&B and electronic music work."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: introduction and Quick Sampler demo, select a sample. Class 2: deep dive "
     "into Quick Sampler, begin building. Classes 3 to 5 are working days. Class 6: final mix and bounce, presentations prepared. "
     "Class 7: presentations with Padlet feedback. Hand out the project sheet and the Sample log now."),
    (1, "bullets", "Sampling: art and ethics", "Producers have always built new music from old sounds|Whose sound is it?|Is it "
     "cleared, public domain, or yours?|Our samples are cleared for this class|Write down where your sample came from",
     "My teacher notes call this project a natural entry point for discussing sampling ethics and copyright. Use two or three of the "
     "discussion questions from the ethics page of the resource (page 5). Keep it short and honest: using someone else's recording "
     "generally needs their permission, which is why this class uses samples you have cleared. This is not legal advice."),
    (1, "steps", "Step 1: listen and choose", "Browse the provided samples|Listen with headphones, more than once|Note the key and "
     "tempo from the file name|Pick one you can hear a use for|Fill in the Sample log",
     "Students listen to the set with headphones and fill in the Sample log (page 12). File names that carry the key and tempo help, "
     "as in my guidelines: make sure the key fits the sample. My struggles list warns that students give up quickly if the sample "
     "does not sound cool at once, so tell them a plain sample can still become a great flip."),
    (2, "pic", "Worked example: slice a sample", "slices",
     "Class 2. This is an original practice sample, described on paper only; nothing here is a recording. It runs 9.6 seconds, which "
     "is 4 bars at 100 BPM (one bar is 2.4 seconds). Cut into 8 slices of 1.2 seconds, each slice is 2 beats and slice 4 starts at "
     "3.6 seconds. Students' samples will differ; the arithmetic is the habit to teach."),
    (2, "steps", "Watch me: the three modes", "Classic: the sample plays across the keys, pitch follows the key|One Shot: a key plays "
     "the whole sample|Slice: the sample is cut up, one slice per key|Drop in a sample, try all three|Reverse, pitch, then play it",
     "A three-minute demo, using your own cleared sample. Here the three modes are shortened from the longer descriptions on the "
     "reference page; the project sheet says to demo Classic, One Shot and Slice early because the modes confuse students. Drop in "
     "the sample, switch modes, and play each. Show Reverse and the pitch control. Menu names vary a little by Logic version."),
    (2, "pic", "Worked example: flip it", "flip",
     "The same 8 slices, rearranged into 8 slots of 2 beats: 4 bars, 9.6 seconds. Slice 1 repeats, slices 2 and 3 are reversed, and "
     "slice 8 drops an octave. In Classic mode, down 12 semitones doubles the length of a slice: 1.2 seconds becomes 2.4, exactly one "
     "bar. Ask students which move they would try first."),
    (2, "steps", "Watch me: drums that fit", "New track: an Electronic Drum Kit (Drum Machine Designer)|Pattern region, Step "
     "Sequencer|Kick, snare, hi-hat: leave space for the chops|Match the style the flip is heading toward|Vary the velocity",
     "A short demo. An Electronic Drum Kit loads Drum Machine Designer. Control-click in the drum track, Create Pattern Region, "
     "double-click for the Step Sequencer. My tip: your drums set the tone, so match the style. Drum patterns must be self-created. "
     "Leave a gap where a chop lands so the two do not fight."),
    (3, "bullets", "Build your beat", "Program your own drum pattern|Match the style of your flip|Play the chops on the keys, "
     "record them|Keep the best take",
     "Class 3 is the first working day. Step 3 of the project sheet, shortened here: build the beat. Students also record their "
     "chops by playing Quick Sampler from the keyboard or by drawing notes in the Piano Roll. Circulate and ask each student to play "
     "you the raw sample and then their loop; push anyone who is only looping the sample to chop or pitch it."),
    (4, "bullets", "Layer and arrange", "Bass, chords, melodies and extras|Keep it appropriate to the style|Give the track a "
     "beginning, a middle and an end|Put each sound on its own track",
     "Class 4, a working day. Step 4, shortened here: add bass, chords, melodies and additional elements. From my guidelines, keep "
     "the layers appropriate to the style and put effects on different tracks so each can have its own volume and plug-ins. Class 5 "
     "is a full working day with no new slide: refine the track."),
    (6, "bullets", "Mix and bounce", "EQ every track|Pan and balance everything|Bounce a .mp3 or .wav|Zip the .logicx project",
     "Class 6, final mix and bounce. Steps 5 and 6 of the project sheet, shortened to fit the slide: mix with EQ, pan and balance, "
     "then finalize by bouncing and preparing the presentation. Ask every student to show you one EQ move and one pan move before "
     "they bounce. Bounce: File, Bounce, Project or Section. Zip: Control-click the .logicx in Finder, Compress."),
    (6, "check", "What you turn in", "Bounced .mp3 or .wav uploaded|Zipped .logicx project uploaded|Named: Your Name – Sample "
     "Flipping|Padlet post with your 3 questions|Answer 2 questions on classmates’ posts",
     "The submission checklist from the project sheet, in short form. Show where students upload (your class page) and where the "
     "Padlet board is. Remind students that the Sample log (page 12) is theirs to keep: it records where the sample came from."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Play the raw sample, then your track|Your Padlet post: 3 questions about your project|Answer "
     "at least 2 of each classmate’s 3|Listen like a producer: what did they do to it?",
     "Class 7, presentations with Padlet Q and A. Each student plays the raw sample and then the flip, so the class can hear the "
     "transformation. During classmates' presentations, every student answers at least 2 of their 3 questions on their Padlet post. "
     "Two minutes per student keeps the day moving."),
    (7, "closer", "One last thing…", "You started with one sample.|You chopped it and flipped it.|You built the drums "
     "yourself.|Now it’s yours.",
     "Close with what my teacher notes say this project builds: Quick Sampler proficiency, drum programming and creative "
     "transformation, plus a first look at sampling ethics. Every student made a complete track from a single source. That is how "
     "producers work."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("chops", "Chop map", "slice, then plan the flip"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 7, 9, 8, 15]
SHOTS3 = [("setup", "Cleared sample set"), ("ethics", "Sampling ethics"), ("example", "Worked example"), ("proj1", "Project sheet"),
          ("proj2", "Steps"), ("pick", "Sample log"), ("drums", "Drum plan"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "ethics", "pacing", "tn1", "tn2", "changes", "logicref", "example",
        "pick", "chops", "drums", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "chops", "proj2", "rubric"]

COVER_A = "Chop, pitch and flip a sample"
COVER_C = "DMP2 · Quick Sampler · chopping · drum programming · mixing · intro slides"
PDF_COVER = dict(a=32, b=67, c=14, art=7.3)
SQ_COVER = dict(a=50, b=134, c=27, art=700)
SQ_B_LINES = ["Sample", "Flipping"]
SQ_SUB = "7 class periods · Quick Sampler · drums · mix · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Sample set guide, ethics page, chop map, drum plan, project sheet", 28)}
SQ_BANDS = {1: "Choose <em>·</em> slice <em>·</em> flip <em>·</em> build <em>·</em> present",
            2: "Hook <em>·</em> slice <em>·</em> three modes <em>·</em> flip <em>·</em> rubric",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no samples included"}

SONG_NOTE = ("No samples, audio, video, lyrics or songs are included. You supply your own cleared sample set (page @SETUP), "
             "so you know exactly where every sound came from.")
CREDITS = ["Worked example (a practice sample described on paper), waveform and flip drawings, drum grid and layouts: original work, "
           "Hudson Beat.",
           "No samples, audio, video, lyrics, album art or chart data are included. Producers are named only as the owner's tip lists "
           "them (artists, no songs); they are not affiliated with or endorsing this resource. Padlet and YouTube are named only as "
           "examples of tools you may already use."]
LOGIC_INTRO = ("Everything students need in Logic for this project, in one table. Demonstrate the three modes (slide 8) and the drums "
               "(slide 10), then let students work. Names are from current Logic Pro versions.")
LOGIC_REF = [("Make a Quick Sampler", "Track › New Software Instrument Track. In the Library (Y), click the instrument slot and choose "
              "Quick Sampler (under Sampler)."),
             ("Load a sample", "Drag the audio file from Finder onto the Quick Sampler’s waveform area. The sample appears as a "
              "waveform; play the keys to hear it."),
             ("Classic mode", "The sample plays across the keyboard like a sampler: the key you play changes the pitch, and the pitch "
              "changes the speed. Good for melodies and bass."),
             ("One Shot mode", "A key plays the whole sample from start to end, however long you hold it. Good for hits, stabs and "
              "single sounds."),
             ("Slice mode", "The sample is cut into slices and each slice goes to its own key. Move or add slice markers on the "
              "waveform so each cut starts at the beginning of a sound."),
             ("Reverse and pitch", "Use the Reverse button for the sample or a slice, and the pitch control to move it up or down in "
              "semitones (12 = one octave)."),
             ("Record the chops", "Record-enable the track and play the slices from a keyboard, or draw notes in the Piano Roll. "
              "Quantize if you want them tight."),
             ("Drums", "New Software Instrument Track, Electronic Drum Kit (Drum Machine Designer). Control-click in the track, Create "
              "Pattern Region, double-click to open the Step Sequencer."),
             ("EQ, pan, bounce", "Mixer (X): double-click the EQ display for Channel EQ; turn the Pan knob. File › Bounce › Project or "
              "Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; .mp3 or .wav and zipped .logicx uploaded", "Padlet post created with my 3 questions",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my project:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:11.4pt;margin-bottom:3pt">Using the sample without transforming it: the Chop map (page @CHOPS) makes students plan '
    'their cuts and their flip, and the worked example (page @EXAMPLE) shows chop, reverse and pitch.</li>'
    '<li style="font-size:11.4pt;margin-bottom:3pt">Confusing modes: slide 8 and the Logic reference (page @LOGICREF).</li>'
    '<li style="font-size:11.4pt;margin-bottom:3pt">Generic drums: slide 10 and the drum plan (page @DRUMS), which asks where the chop '
    'lands.</li>'
    '<li style="font-size:11.4pt;margin-bottom:0">Giving up early: the Sample log (page @PICK) has students try several samples first.</li></ul></div>')
TN1_SIZE = 15.2
PROJ_SIZE = 13.8
VOCAB_GAP = 40
LOGIC_SIZE = 12.6
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example", "How to use, overview, sample set, ethics, pacing, teacher notes, what changed, Logic "
              "reference, worked example"),
             ("Student pages", "pick", "reflect", "Sample log, Chop map, drum plan, project sheet (3 pages), rubric, vocabulary, "
              "feedback planner, reflection"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period project for high school music technology. Each student takes one '
             f'sample and flips it into an original track in Logic Pro: they chop, pitch, reverse and rearrange it in Quick Sampler, '
             f'program their own drums, layer instruments and mix. It is an open-ended project from my Digital Music Production 2 '
             f'course (focus: sampling and Quick Sampler), and the projects in that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Build your cleared sample set (page {D.IX("setup")}): no samples are included.</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("pick")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Class 5 is a working day with no new slide. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'<div class="box" style="margin-top:8pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students pick a cleared '
             f'sample, chop and pitch it in Quick Sampler, build their own drums around it, layer, mix and present.</p></div>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No samples included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Your sample set:</b> 10 to 50 short sounds you have cleared. I use 50; a smaller set works, and so does one sound per pair of students.</li>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}.</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<p class="small">Logic Pro is a trademark of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12.8pt;line-height:1.5">One Logic Pro project: an original track built around one sample. The sample is '
             f'chopped, pitched, reversed or stretched in Quick Sampler, set against drum patterns the student programmed, layered with '
             f'instruments that fit the style, and mixed with EQ and plug-ins. They hand in a bounced .mp3 or .wav, the zipped .logicx '
             f'project, and a Padlet post with three feedback questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12.8pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p>Supports the National Core Arts Standards for Music (Music Technology, high school): developing and '
             f'refining original work (MU:Cr2.1, MU:Cr3.1), presenting it (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:11.8pt;line-height:1.4'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:10.4pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: choose and demo, build, three working days, mix, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Quick Sampler (Classic, One Shot, Slice), Drum Machine Designer and the Step '
             f'Sequencer, Channel EQ, pan, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>A set of cleared samples, headphones, a feedback board</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0">Students should already '
             f'know how to make a drum pattern, play in parts and save, bounce and zip a project in Logic. The Logic quick reference '
             f'(page {D.IX("logicref")}) covers every tool this project uses.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Open-Ended", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<div class="cols"><div class="big">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student (a current version; Quick Sampler and the Step Sequencer need Logic '
             f'Pro 10.5 or later), and <b>headphones</b>.</li>'
             f'<li><b>A set of cleared samples</b>: short audio files (a few seconds each) your students may use. Nothing is included. '
             f'Build it from the options on the right.</li>'
             f'<li><b>A place to share the set</b> with your students and to submit an .mp3 or .wav and a zipped .logicx project (your class page).</li>'
             f'<li><b>A feedback board</b> for the three questions (my sheets use Padlet).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("pick")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:12pt;margin-bottom:8pt") for c in [
                 "Build and test the sample set; write each sample’s source and license in a list for yourself.",
                 "Name each file with its key and tempo where you know them (for example Warm Pad_keyAmin_90bpm).",
                 "Make a 30-second flip of one sample for slide 2.",
                 "Print the student pages; set up the submission spot and the feedback board."]) +
             f'</div><div class="big">'
             f'{D.H2("Record your own.", True)}'
             f'<p style="font-size:11.4pt">My class set is 50 short vocal loops and phrases, and it is not part of this kit. A sample is '
             f'someone’s recording, so use sounds you have the right to hand to students:</p>'
             f'<ul style="font-size:11.4pt;line-height:1.42">'
             f'<li><b>Record your own.</b> You, your colleagues or willing students sing, play or tap short phrases into Logic. The '
             f'performers agree to class use.</li>'
             f'<li><b>Public domain and CC0 sounds.</b> Sound libraries label these. Save the page that shows the license.</li>'
             f'<li><b>Licensed libraries.</b> If your school or department owns a sample library, read its license: does it allow '
             f'classroom use and student remixes?</li>'
             f'<li><b>Logic’s own sounds.</b> Apple Loops that come with Logic are meant for making music; read Apple’s license before '
             f'you hand a set out.</li></ul>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">A cleared sample is…</span><ul style="margin:0">'
             f'<li style="font-size:11.4pt">One whose source and license you can name</li>'
             f'<li style="font-size:11.4pt">Short (2 to 12 seconds) and clean, with one clear idea to chop</li>'
             f'<li style="font-size:11.4pt">Free of any famous recording or song</li></ul></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Posting online?</span><p style="margin:0;font-size:11.4pt">A class '
             f'assignment kept on your class page is one thing; posting a flip publicly is another. Check each license first, and credit '
             f'the source if it asks.</p></div>'
             f'</div></div>')
    return D.page("Setup and your cleared sample set", "SETUP", "Teacher", inner, n, key="setup")


def ethics_page(n, wm=False):
    inner = (f'<p style="margin:0 0 4pt;font-size:11.4pt">My teacher notes call this project “a natural entry point for discussing '
             f'sampling ethics and copyright.” This page gives you the facts to start with and questions for Class 1. It is a '
             f'discussion starter, <b>not legal advice</b>.</p>'
             f'<div class="cols"><div class="big">'
             f'{D.H2("Four ideas for students", True)}'
             f'<ul style="font-size:11.4pt;line-height:1.42">'
             f'<li><b>Two kinds of ownership.</b> A recorded song generally carries two sets of rights: the recording itself and the '
             f'music and words underneath it. Using a piece of someone’s record in a new track usually means asking about both.</li>'
             f'<li><b>Clearing a sample</b> means getting permission, often for a fee or a share of the earnings.</li>'
             f'<li><b>Some sounds are free to use.</b> Recordings you make yourself, public-domain sounds and CC0 sounds need no '
             f'permission. Some licenses ask you to credit the source.</li>'
             f'<li><b>Transforming is not the same as clearing.</b> Chopping and pitching a sample makes it sound different; it does not '
             f'make it yours.</li></ul>'
             f'{D.H2("Why this class uses cleared samples")}<p style="font-size:11.4pt">Every student can flip freely because the set '
             f'was chosen so that nobody has to ask permission. The Sample log (page {D.IX("pick")}) asks where the sample came from, so '
             f'the habit sticks.</p>'
             f'</div><div class="big">'
             f'{D.H2("Discussion questions", True)}<ol style="font-size:11.4pt;line-height:1.42">'
             f'<li>Why would a producer build a track from someone else’s sound instead of recording a new one?</li>'
             f'<li>The artist made the original recording. What does the producer owe them?</li>'
             f'<li>When does a flip become a new work, and when is it still the original?</li>'
             f'<li>Would you feel differently if the sample was a stranger’s voice, a friend’s, or yours?</li>'
             f'<li>A producer flips a sample so much that nobody could recognize it. Do they still need permission?</li>'
             f'<li>What would you want if someone sampled your music?</li></ol>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">Class 1 in two minutes</span><p style="margin:0;font-size:11.4pt">'
             f'Pick two questions, take answers aloud, then tell students: our samples are cleared, and I would like you to write down '
             f'where yours came from.</p></div>'
                      f'</div></div>'
             f'{D.H2("Is it cleared? A five-minute sort")}'
             f'<p style="margin:0 0 4pt;font-size:11pt">Read each source aloud and have students vote: use it, or ask first?</p>'
             f'<table class="t" style="font-size:10.6pt"><tr><th style="width:36%">The sound comes from…</th><th style="width:20%">Use it?</th><th>Why</th></tr>'
             f'<tr><td>A phrase you recorded yourself</td><td><b>Yes</b></td><td>You own it. Check that anyone performing agrees.</td></tr>'
             f'<tr><td>A sound labelled public domain or CC0</td><td><b>Yes</b></td><td>The owner has given up the rights; keep the license page.</td></tr>'
             f'<tr><td>A sound whose license asks for credit</td><td><b>Yes, with credit</b></td><td>Follow the license and name the source.</td></tr>'
             f'<tr><td>A few seconds of a song from a streaming service</td><td><b>Ask first</b></td><td>It is someone’s recording and someone’s song.</td></tr>'
             f'<tr><td>A clip pulled from a video or a game</td><td><b>Ask first</b></td><td>Same rules; it may have several owners.</td></tr></table>')
    return D.page("Sampling, ethics and copyright", "TEACHER", "Class 1", inner, n, key="ethics")


def example_page(n, wm=False):
    rows = "".join(f"<tr><td><b>{k + 1}</b></td><td>{sec(k * SLICE_SECS)} – {sec((k + 1) * SLICE_SECS)}</td><td>{SLICE_WHAT[k]}</td></tr>"
                   for k in range(NSLICE))
    frows = "".join(f"<tr><td><b>{k + 1}</b></td><td>{sl}</td><td>{TREAT[tr]}</td><td>{sec(k * SLICE_SECS)}</td></tr>"
                    for k, (sl, tr) in enumerate(FLIP))
    inner = (f'<p style="margin:0 0 3pt">An <b>original practice sample, described on paper</b>: no audio is included, so these numbers are '
             f'easy to check. Students’ samples will differ.</p>'
             f'<div class="box" style="margin-bottom:2pt"><span class="k">1 · Time</span><p style="margin:0">At {TEMPO} BPM one beat is '
             f'{beat_secs():.1f} s and one bar is {bar_secs():.1f} s. The sample lasts {TOTAL_SECS:.1f} s = {TOTAL_SECS / bar_secs():.0f} bars '
             f'= {NSLICE} slices of {BEATS_PER_SLICE} beats ({sec(SLICE_SECS)}).</p></div>'
             f'{D.H2("2 · Slice it")}<div style="width:6.7in;margin:2pt auto 3pt">{D.body_svg(wave_body(1250, 110, "page wave"))}</div>'
             f'{D.H2("3 · Flip it")}<div style="width:6.7in;margin:2pt auto 3pt">{D.body_svg(flip_body(1250, "page flip", 80))}</div>'
             f'<div class="cols" style="gap:10pt"><table class="t" style="font-size:9pt"><tr><th style="width:11%">Slice</th><th style="width:34%">Plays</th><th>Sounds like (imagined)</th></tr>{rows}</table>'
             f'<table class="t" style="font-size:9pt"><tr><th style="width:10%">Slot</th><th style="width:11%">Slice</th><th>What happens</th><th style="width:22%">Starts</th></tr>{frows}</table></div>'
             f'<p class="small" style="margin:2pt 0 3pt">In Classic mode, pitching down 12 semitones plays at half speed, so slice 8 '
             f'({sec(SLICE_SECS)}) lasts {sec(2 * SLICE_SECS)}: exactly one bar.</p>'
             f'{D.H2("4 · Drums (x = a hit, . = a rest, 16 steps per bar)")}'
             f'<div style="width:5.3in;margin:1pt auto 2pt">{D.body_svg(drums_drawing(30, 24, "page"))}</div>')
    return D.page("Worked example · a practice sample", "EXAMPLE", "Teacher", inner, n, ak=True, key="example")


def pick_page(n, wm=False):
    rows = "".join(f"<tr><td style='text-align:center'><b>{i}</b></td><td></td><td></td><td></td><td></td><td></td></tr>" for i in range(1, 9))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">Listen to the samples with headphones, more than once. Fill in a row for each one you '
             f'try, then choose the sample you will flip.</p>'
             f'<table class="map"><tr><th style="width:5%">#</th><th style="width:25%">Sample (file name)</th><th style="width:11%">Key</th>'
             f'<th style="width:11%">Tempo</th><th style="width:24%">What I hear</th><th>An idea: chop, pitch, reverse…</th></tr>'
             f'{rows}</table>'
             f'{D.H2("My sample")}'
             f'<div class="fl"><b>File name:</b><span></span></div>'
             f'<div class="fl"><b>Where it came from (my teacher tells me):</b><span></span></div>'
             f'<div class="fl"><b>Why this one?</b><span></span></div><div class="ln2" style="margin-bottom:8pt"></div>'
             f'<div class="fl"><b>Key:</b><span style="flex:0 0 1in"></span><b>Tempo:</b><span style="flex:0 0 1in"></span>'
             f'<b>Length (seconds):</b><span style="flex:0 0 0.8in"></span></div>'
             f'<div class="fl"><b>The one small piece I want to use again and again:</b><span></span></div>'
             f'<div class="fl"><b>The style my track is heading toward:</b><span></span></div>')
    return D.page("Sample log", "STUDENT", "Class 1", inner, n, wm, name=True, key="pick")


def chops_page(n, wm=False):
    rows = "".join(f"<tr><td style='text-align:center'>{i}</td><td></td><td></td><td></td><td></td></tr>" for i in range(1, 9))
    flip_rows = "".join(f"<tr><td style='height:20pt'><b>{lab}</b></td>" + "<td></td>" * 8 + "</tr>" for lab in ("Slice #", "Reverse / pitch?", "Notes"))
    inner = (f'<div class="fl"><b>Sample:</b><span></span><b>Tempo (BPM):</b><span style="flex:0 0 0.8in"></span>'
             f'<b>Length (s):</b><span style="flex:0 0 0.7in"></span></div>'
             f'<p style="margin:0 0 5pt">Slice it first. Play the sample and note where each sound begins, then cut so every slice starts '
             f'at the beginning of a sound.</p>'
             f'<table class="map"><tr><th style="width:6%">Slice</th><th style="width:15%">Starts (s)</th><th style="width:15%">Length (s)</th>'
             f'<th>What it sounds like</th><th style="width:26%">I could use it as…</th></tr>{rows}</table>'
             f'{D.H2("My flip: the slices in a new order")}'
             f'<p style="margin:0 0 5pt;font-size:11pt">One box per slot. Write the slice number you will play there, and whether it is '
             f'reversed or pitched. Repeat a slice, skip a slice, leave a slot empty.</p>'
             f'<table class="map"><tr><th style="width:16%"></th>' + "".join(f"<th>{i}</th>" for i in range(1, 9)) + f'</tr>{flip_rows}</table>'
             f'<div class="cols" style="gap:12pt;margin-top:8pt"><div class="box acc-b"><span class="k">Check your time</span><p style="margin:0">'
             f'Slice length = sample length ÷ number of slices. At your tempo, how many beats is one slice? (One beat = 60 ÷ BPM seconds.)</p></div>'
             f'<div class="box"><span class="k">Rule</span><p style="margin:0">{REQS[1]}. Do more than loop it: chop, pitch or reverse.</p></div></div>')
    return D.page("Chop map", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="chops")


def drums_page(n, wm=False):
    lanes = ["Open hi-hat", "Closed hi-hat", "Snare / clap", "Kick", "Other:"]
    cells = ""
    for i in range(3):
        g = D.grid_body(f"blank {i}", [{}], [], lanes, cw=34, ch=27, gut=160, ls=17, blank=True)
        cells += (f'<div style="margin:0 0 7pt"><div class="fl" style="margin:0 0 3pt"><b>Section:</b><span style="flex:0 0 1.4in"></span>'
                  f'<b>Bars:</b><span style="flex:0 0 0.5in"></span><b>Where the chop lands:</b><span></span></div>'
                  f'<div style="width:6.6in;margin:0 auto">{D.body_svg(g)}</div></div>')
    inner = (f'<div class="fl"><b>Style my flip is heading toward:</b><span></span><b>Tempo:</b><span style="flex:0 0 0.8in"></span></div>'
             f'<p style="margin:0 0 5pt;font-size:11pt">Design your own drum patterns to fit the style and the sample. Fill a square for each '
             f'hit; each square is a sixteenth note and grey columns are the beats. Mark the steps where a chop lands so your drums leave it room.</p>'
             f'{cells}'
             f'<div class="cols" style="gap:12pt"><div class="box"><span class="k">Make it human</span><p style="margin:0">Mark the loudest hits '
             f'with a dot. Vary velocity and nudge a few notes so it doesn’t sound robotic.</p></div>'
             f'<div class="box"><span class="k">Rule</span><p style="margin:0">{REQS[3]}.</p></div></div>')
    return D.page("Drum plan", "STUDENT", "Class 2", inner, n, wm, name=True, key="drums")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "ethics": ethics_page, "example": example_page,
         "pick": pick_page, "chops": chops_page, "drums": drums_page}


# ================================================================ content checks (music arithmetic, owner text, no samples)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 4), reqs=(REQS, 6), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 5),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 3))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp} (the owner's count)")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is the owner's /25, levels 1-5")
    if [c for c, _ in RUBRIC] != ["Creativity & Originality", "Technical Skill / DAW Use", "Composition & Structure",
                                  "Sound Design & Mix Quality", "Documentation & Presentation"]:
        errs.append("rubric categories must be the owner's, in order")
    if FILE_NAME not in CHECK[2] or "Sample Flipping" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    # the practice sample adds up
    if abs(beat_secs() - 0.6) > 1e-9 or abs(bar_secs() - 2.4) > 1e-9 or abs(SLICE_SECS - 1.2) > 1e-9 or abs(TOTAL_SECS - 9.6) > 1e-9:
        errs.append("practice sample times")
    if abs(TOTAL_SECS / bar_secs() - 4) > 1e-9 or len(FLIP) != NSLICE or len(SLICE_WHAT) != NSLICE:
        errs.append("practice sample: 8 slices = 4 bars, 8 flip slots")
    if not all(1 <= s <= NSLICE and t in TREAT for s, t in FLIP) or set(s for s, _ in FLIP) - set(range(1, NSLICE + 1)):
        errs.append("flip slots must use slices 1-8 and known treatments")
    if sec(2 * SLICE_SECS) != "2.4 s" or abs(2 * SLICE_SECS - bar_secs()) > 1e-9:
        errs.append("octave-down slice must last one bar")
    if DRUM["Snare"][4] != "x" or DRUM["Snare"][12] != "x" or DRUM["Kick"][0] != "x" or any(len(s) != 16 for s in DRUM.values()):
        errs.append("drum groove: snare on 2 and 4, kick on 1, 16 steps")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    for need in ("cleared sample", "No audio"):
        if need not in notes[0]:
            errs.append(f"deck slide 1 notes must say '{need}'")
    txt = " ".join(flat)
    for need in ("No samples, audio, video, lyrics or songs are included", "original practice sample, described on paper",
                 "Your Name – Sample Flipping", "Final Grade = Average of Student + Teacher", "not legal advice",
                 "Record your own."):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no samples" not in up.lower() or "Open question" not in up:
        errs.append("UPLOAD.md: must say no samples are included and record the sample-license open question")
    for i in (7, 10, 11, 12):   # slides that shorten the owner's wording must say so
        if "shortened" not in notes[i].lower() and "short form" not in notes[i].lower():
            errs.append(f"deck slide {i + 1} notes: must say the owner's wording is shortened")
    ch = flat[D.IX("changes") - 1]
    if "slide 8" not in ch or "slides 11, 12 and 13" not in ch or "includes no samples" not in ch:
        errs.append("'What changed' page must list the shortened slides and the no-samples change")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or any("mode they used" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in ("J Dilla", "Madlib", "Kanye"):
        if banned in alldeck:
            errs.append(f"deck must not name producers ({banned}); only the owner's tip page does")
    return errs


def check_summary():
    return (f"Practice sample {TOTAL_SECS:.1f} s = 4 bars at {TEMPO} BPM = {NSLICE} slices of {sec(SLICE_SECS)} (2 beats); the octave-down "
            f"slice lasts one bar; the 8 flip slots use slices 1-8; drum groove checked; the owner's lists counted (4 goals, 4 terms, "
            f"6 requirements, 7 steps, 4 tips, 5 checklist items, 4 struggles, 3 resources); {len(CHANGES)} wording changes disclosed; "
            f"no samples included; grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
