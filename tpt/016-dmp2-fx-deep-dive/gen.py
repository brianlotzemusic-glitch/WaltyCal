#!/usr/bin/env python3
"""DMP2 project: FX Deep Dive (TpT 016): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects them)
    python3 gen.py --check    verify content, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap,
                              overflow and dead space, banned strings, tpt.json and UPLOAD.md

The owner's own curriculum (Brian Lotze, Digital Music Production 2), in the Hudson Beat style. Source (Drive, read-only):
DMP2 > Projects (New) > FX Deep Dive > "FX Deep Dive - Project Sheet & Rubric" (rubric 5 categories scored 1-5, /25, final grade =
average of student and teacher scores), TEACHER NOTES > "FX Deep Dive - Teacher Notes" (7 class periods), and the project's entry on
"DMP2 - Project Menu". These three set the project text, steps, rubric and pacing (owner rule, 17 Oct 2026). Supporting material comes
from the older DMP2 > Projects > "FX Deep Dive" folder (read-only), which the Teacher Notes name: (a) the owner's "Audio FX - notes"
table, whose 11 rows settle the "11 FX" (the Native Instruments video title says 10; the class covers 11, and the owner's Plug-in Links
doc has the same 11 categories); (b) the owner's "Plug-in Links" doc, reproduced as page "links" (titles and URLs only, nothing
embedded); (c) the "EQ Cheatsheet.pdf", which is NOT the owner's work (its cover says "Made by Jay Dwivedi"), so it is named only and
never reproduced; the kit's own EQ guide stays original. The older "Project 4 - FX Deep Dive" doc (/20 rubric) is not used. Every change to the owner's wording is listed in CHANGES and printed on the "What changed from the original" page.

NO AUDIO IS INCLUDED. The owner's project works on a student's own earlier project or on a multitrack from the Cambridge-MT library
(third party, named only; students download it from the library). The worked example is an invented eight-track session described on
paper, with an EQ map, a pan map and a compressor curve drawn in code. No songs, lyrics or chart data are named.
The shared builder is ../_dmp2_common/dmp2.py (see its README).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

SLUG = "fx-deep-dive"
TITLE = "FX Deep Dive"
ACCENT = "#5F6F00"          # this product's single accent: olive (008 red, 009 orange, 010 violet, 011 teal, 012 blue, 013 green, 014 magenta, 015 gold)
ACC_LIGHT = "#DCE59A"
PRICE = "10.00"
CLASSES = 7
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]   # METADATA-GUIDE (a); proven slugs (008-015).
TAGS = ["Autumn"]
ANSWER_KEY = None
LISTING_TITLE = "FX Deep Dive in Logic Pro | EQ, Reverb, Delay Mixing Project | High School Music"
DESC_START = "Mixing and audio effects for high school music technology:"
DESC_MUST = ["FX Deep Dive", "EQ", "no audio", "Cambridge-MT"]
ZIP_DIR = "FX Deep Dive - Hudson Beat"
ZIP_DATE = (2026, 10, 15, 12, 0, 0)
TYPE = "Structured Project"
PROJ_LINE = "Digital Music Production | <i>Structured Project</i> | 7 class periods"
DECK_STRAP = "EQ, pan, reverb and delay in Logic Pro"
BANNED_EXTRA = []

# ================================================================ the owner's words
MENU_TYPE, MENU_FOCUS = "Structured", "Mixing & Effects"
MENU_DESC = "Enhance a track using at least 5 audio effects. EQ, pan, and mix every track for a professional result."
OVERVIEW = ("Time to level up your mixing skills. Take an existing track — either one of your own previous projects or a song from the "
            "Cambridge-MT Multitrack Library — and enhance it using at least 5 different audio effects. Your goal is to use FX "
            "creatively and intentionally to shape tone, depth, and space in a professional-sounding mix.")
GOALS = ["Learn and apply at least 5 different audio effects in a real mix",
         "Develop EQ and panning skills across all tracks in a session",
         "Understand how FX choices relate to genre and style",
         "Build a polished, balanced mix with clarity and depth"]
VOCAB = [("EQ (Equalization)", "A tool that adjusts the volume of specific frequencies to shape tone and clarity"),
         ("Compression", "Reduces the dynamic range — making quiet parts louder and loud parts quieter"),
         ("Reverb", "Simulates the natural reflections of a space, adding depth and ambience"),
         ("Delay", "Repeats a sound after a set time, creating echo or rhythmic effects"),
         ("Panning", "Placing sounds left or right in the stereo field to create width and separation"),
         ("Modulation", "Effects like chorus, phaser, and flanger that add movement by altering a sound over time")]
REQS = ["Choose your source: remix your own previous project OR pick a multitrack from Cambridge-MT",
        "Use at least 5 different FX from the 11 covered in your class notes",
        "Every track in your mix must be EQ’d and panned thoughtfully",
        "FX choices should be stylistically appropriate for the genre",
        "Your final mix should demonstrate clarity, depth, and balance"]
STEPS = ["<b>Review</b> — Revisit your notes on the 11 FX from the Native Instruments video (notes page: page @FXNOTES)",
         "<b>Choose your source</b> — Decide whether to remix your own project or download a multitrack from Cambridge-MT "
         "(log it on page @SOURCE)",
         "<b>Plan and apply FX</b> — Add at least 5 different effects across your mix. Think about genre conventions. "
         "(FX log: page @FXLOG)",
         "<b>EQ and pan every track</b> — Shape tone with EQ and place each instrument in the stereo field (Track map: page @TRACKMAP)",
         "<b>Refine your mix</b> — Adjust levels, tweak FX settings, and check on headphones and speakers",
         "<b>Finalize</b> — Bounce your final mix and prepare to walk the class through your FX choices",
         "<b>Present &amp; Get Feedback</b> — Create your own Padlet post with 3 questions you want classmates to answer about your project. "
         "Present to the class. During classmates’ presentations, answer at least 2 of their 3 questions on their Padlet post."]
TIPS = ["Less is more. A well-placed reverb or delay can transform a track. Piling on effects usually makes it worse.",
        "Always A/B test your effects — bypass the plug-in and listen with and without it.",
        "EQ is your most powerful tool. Get your EQ right before adding other effects.",
        "If using Cambridge-MT, pick a song with 8–16 tracks. Don’t pick a 40-track session."]
FILE_NAME = "“Your Name – FX Deep Dive”"
CHECK = ["Bounced .mp3 or .wav of final mix uploaded to your class page",
         "Zipped .logicx project file uploaded to your class page",
         f"Files named correctly: {FILE_NAME}",
         "At least 5 different FX used and ready to discuss",
         "All tracks EQ’d and panned",
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
TN_REINFORCES = ("This is the primary mixing skills project. It shifts focus entirely to post-production. The EQ Cheatsheet PDF and "
                 "Plug-in Links doc are key companion resources.")
STRUGGLES = ["Students apply FX randomly without purpose — push them to articulate WHY they’re using each effect.",
             "EQ feels invisible to beginners. Do a live demo early with dramatic cuts and boosts on a soloed track.",
             "Cambridge-MT tracks can be overwhelming. Pre-select 5–10 sessions with reasonable track counts.",
             "Students skip panning and leave everything center. Play a professional mix and point out the width.",
             "Some students treat this as a composition project. Redirect early."]
VAR_EASY = "Reduce the FX requirement to 3 and provide a pre-mixed reference with notes on which effects were used."
VAR_HARD = ("Require 7+ FX including at least one send/bus effect. Have them write a paragraph justifying each FX choice.")
RESOURCES = [("10 FX Every Music Producer Needs to Know — Native Instruments (YouTube)",
              "Not included: it is a video on YouTube, so search it by title (link on page @LINKS). Its title says 10; my class covers "
              "11 (page @FXNOTES lists them). Page @LOGICREF shows where each kind of effect lives in Logic."),
             ("Cambridge-MT Multitrack Library", "Not included and not mine to hand out: students download a session from the library’s "
              "own site. Page @SOURCE helps you pre-select sessions and reminds students to read the library’s terms."),
             ("EQ Cheatsheet PDF (in course materials)", "Not included: its cover credits it to Jay Dwivedi, so it is not mine to hand "
              "out. Use your own copy beside page @EQGUIDE, this kit’s own EQ guide and live-demo plan."),
             ("Plug-in Links doc with tutorials for each effect category", "Included, from the teacher’s own materials: page @LINKS "
              "lists my tutorial links (titles and web addresses only) for each of the 11 FX. Page @LOGICREF lists the Logic plug-in "
              "for each.")]
TN_NOTE = ("Great project to revisit the EQ Cheatsheet. Consider a mix critique day where you workshop student projects on the "
           "main speakers.")
GRADING = ["My rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours."]
GRADING_TIPS = ["Technical Skill: ask the student to open Channel EQ on one track and say which frequency they moved, whether they "
                "boosted or cut it, and why.",
                "Sound Design &amp; Mix Quality: have the student bypass one effect live and describe what changed (an A/B test). Listen "
                "on headphones and on the main speakers.",
                "Composition &amp; Structure: the source track brings its own form. Look at whether the mix supports it (does the chorus "
                "open up?), not whether the student wrote it.",
                "Documentation &amp; Presentation: the FX log (page @FXLOG) and the three Padlet questions are the evidence. My rubric "
                "mentions reflection, so you may want to ask for a sentence or two."]
PACING = [
    {"n": 1, "owner": "<b>Class 1:</b> Review the 11 FX from class notes. Listen to examples. Students choose their source.",
     "do": "Slides 1–6: hook (dry, then mixed), what effects do, the seven classes, steps 1 and 2, why each effect needs a reason. Hand "
           "out the project sheet, the FX notes and the Source log.", "slides": (1, 6),
     "pages": ["source", "fxnotes", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Dry and mixed · what effects do · choose a source · every effect needs a reason"},
    {"n": 2, "owner": "<b>Classes 2–5:</b> Core working days — apply FX, EQ all tracks, set panning.",
     "do": "Slides 7–11: the live EQ demo on a soloed track, pan the band, reverb and delay on a send, compression by the numbers. "
           "Then work time; circulate.", "slides": (7, 11), "pages": ["trackmap", "fxlog"],
     "deck": "EQ demo · pan the band · reverb and delay · compression numbers"},
    {"n": 3, "owner": None, "do": "Slide 12: EQ and pan every track. Then work time.", "slides": (12, 12), "pages": [],
     "deck": "Working day: EQ and pan every track"},
    {"n": 4, "owner": None, "do": "Slide 13: add effects with a reason and A/B each one. Then work time.", "slides": (13, 13), "pages": [],
     "deck": "Working day: effects with a reason"},
    {"n": 5, "owner": None, "do": "Full working day: refine the mix. Ask each student to bypass one effect and tell you what changed.",
     "slides": None, "pages": [], "deck": "Working day: refine the mix"},
    {"n": 6, "owner": "<b>Class 6:</b> Final adjustments, bounce. Prepare presentations and write 3 Padlet feedback questions.",
     "do": "Slides 14–16: refine and bounce, what you turn in, the rubric. Students self-score, bounce and post their three questions.",
     "slides": (14, 16), "pages": ["rubric", "present"], "deck": "Refine and bounce · checklist · rubric · 3 questions"},
    {"n": 7, "owner": "<b>Class 7:</b> Presentations with Padlet Q&amp;A peer feedback.",
     "do": "Slides 17–18: presentation day and the close. Every student presents and answers 2 of each classmate’s questions.",
     "slides": (17, 18), "pages": ["present"], "deck": "Presentations with Padlet Q&A"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:8pt;gap:14pt"><div class="box acc-b"><span class="k">The one rule for Class 2</span>'
    '<p style="margin:0;font-size:11pt">From my common struggles: do the EQ demo early, with dramatic cuts and boosts on a soloed track. '
    'Slide 8 is that demo, and the EQ guide (page @EQGUIDE) is your script.</p></div>'
    '<div class="box"><span class="k">Classes 3–5</span><p style="margin:0;font-size:11pt">Working days. Slides 12 and 13 open Classes 3 '
    'and 4; Class 5 has no new slide. Circulate and ask: why is that effect there, and what happens when you bypass it? For my mix '
    'critique day, use the end of Class 5 or Class 6 to play two or three volunteer mixes on the main speakers.</p></div></div>')

# ================================================================ every change to the owner's wording (printed on the changes page)
CHANGES = [
    "My LMS name is written as “your class page” (checklist items 1 and 2).",
    "Page numbers are added to steps 1 to 4 (the FX notes, the Source log, the FX log and the Track map).",
    "My four resources are named as I wrote them (page @TN2). My Plug-in Links doc is reproduced in this kit’s layout as page @LINKS "
    "(titles and web addresses only). The EQ Cheatsheet is by another author, so it is named only. The video and the library are "
    "named by title only.",
    "The 11 FX my sheets mention are listed on page @FXNOTES, from my own FX notes table (the Native Instruments video title says "
    "10; my class covers 11).",
    "My pacing guide’s “Classes 2–5” row spans the Class 2, 3, 4 and 5 rows, so each class can name its slides.",
    "Layout only: the rubric’s Name and Date lines moved to the top; its Notes box became ruled lines.",
    "The intro deck shortens my wording (full wording on pages @PROJ1–@PROJ3): slide 5 shortens steps 1 and 2, slide 12 shortens step 4, "
    "slide 13 shortens steps 3 and 5, and slide 14 shortens steps 5 and 6.",
]
CHANGES_MUST_MENTION = ["your class page", "Page numbers", "named by title only", "Classes 2–5", "Layout only", "intro deck shortens",
                        "reproduced in this kit’s layout", "my class covers 11"]
KEPT = ("Everything else from my three documents is kept as I wrote it: the overview, goals, the six vocabulary terms, the five "
        "requirements, steps (apart from the page numbers), tips, checklist and file name (“Your Name – FX Deep Dive”), the rubric (five "
        "categories scored 1–5, /25, the average of the student’s and the teacher’s score), what the project reinforces, the five common "
        "struggles, the variations, my day-by-day pacing and my closing note, and the project menu entry quoted on page @OVERVIEW. "
        "No requirement or rubric row is added.")
NEW_MATERIAL = ("Everything else is new and supports my sheets without changing them: how to use the kit, the overview and setup "
                "pages (including how to choose a source track), the teacher moves and slide numbers in the pacing guide, the grading "
                "suggestions, the Logic quick reference, the EQ guide and demo plan, the worked example (an invented eight-track "
                "session described on paper, not a recording), the Source log, the FX notes page, the Track map, the FX log, the "
                "vocabulary page, the presentation planner and the intro deck. None of these adds a requirement or a rubric row. "
                "The tutorial links page and the list of the 11 FX come from my own materials, laid out for this kit.")

# ================================================================ the worked example (Hudson Beat original: an invented session on paper)
TEMPO = 100
# The 11 FX the class covers: the rows of the owner's "Audio FX - notes" table (the Plug-in Links doc uses the same 11 categories).
FX11 = ["Panning", "Delay", "EQ", "Compression", "Distortion", "Reverb", "Chorus", "Phaser", "Pitch Correction", "Tremolo", "Filter"]
# The owner's "Plug-in Links" doc (category, [(title, url)]). External sites: titles and URLs only, nothing embedded.
LINKS = [
    ("Panning", [("Panning for a Wider Mix", "youtube.com/watch?v=xT1tQgqBWyU")]),
    ("Delay", [("Sound Basics - Reverb & Delay", "youtube.com/watch?v=-jPPJEHMepA"),
               ("How to use a Delay Effect", "youtube.com/watch?v=boCZejIYUJg")]),
    ("EQ", [("Sound Basics - EQ", "youtube.com/watch?v=I6ZF_NHvqzU"),
            ("EQ Explained in 4 minutes", "youtube.com/watch?v=34lHk6lfpkI"),
            ("How to Use EQ: 10 Amazing Tips for a Professional Mix", "musicianonamission.com/approach-equalization-two-types-eq/"),
            ("The Ultimate EQ Cheat Sheet for Every Common Instrument", "blog.sonicbids.com/the-ultimate-eq-cheat-sheet-for-every-common-instrument"),
            ("How to hear EQ", "youtu.be/U40thp61nrE")]),
    ("Compression", [("Compressors Explained", "youtube.com/watch?v=IbIC7B4BU6g"),
                     ("Beginner’s Guide to Compression, Part 1", "youtube.com/watch?v=BIVfpsoPnOo"),
                     ("Part 2", "youtube.com/watch?v=ebHGH3k7g4I"), ("Part 3", "youtube.com/watch?v=FE_8-Q6CZXE")]),
    ("Distortion", [("Distortion As An Active Production Element", "youtube.com/watch?v=KCcDBHKfp5g"),
                    ("Using Distortion Plug-ins", "youtube.com/watch?v=c9NbXzdnVB8")]),
    ("Reverb", [("Reverb and Delay Explained – Sound Basics", "youtube.com/watch?v=-jPPJEHMepA"),
                ("How to use Reverb", "youtube.com/watch?v=JxG3PQhCH0M"),
                ("What is Reverb? The Beginner's Guide to Reverb in Music Production", "blog.landr.com/what-is-reverb/")]),
    ("Chorus", [("Chorus Effect Tutorial: How To Understand & Apply A Chorus Effect For Fuller Vocals", "youtube.com/watch?v=l0BtzSXw538")]),
    ("Phaser", [("How To Use The Phaser Tool", "youtube.com/watch?v=-lpL9pv_4Eo")]),
    ("Pitch Correction", [("Pitch Correction & Mastering", "youtube.com/watch?v=E4eUe4IWM0U")]),
    ("Tremolo", [("How To Use Tremolo", "youtube.com/watch?v=ltwb3-lW-GE")]),
    ("Filter", [("Exploring the AutoFilter", "youtube.com/watch?v=CvnZTAnLyTY")]),
]
LINKS_EXTRA = [("10 FX every music producer needs to know | Native Instruments", "youtube.com/watch?v=IkiJMTa6lWo"),
               ("Multi Track Mixing Stems (Cambridge-MT)", "cambridge-mt.com/ms/mtk/")]

SESSION = [  # track, pan (-100 left .. +100 right), EQ move, FX
    ("Kick", 0, "Boost 60 Hz +3 dB; cut 300 Hz −4 dB", "Compressor"),
    ("Snare", 0, "Cut 400 Hz −3 dB; boost 4 kHz +3 dB", "Reverb (short, on a send)"),
    ("Hi-hat", 25, "High-pass at 300 Hz", "None"),
    ("Bass", 0, "Cut 250 Hz −3 dB; boost 80 Hz +2 dB", "Compressor"),
    ("Keys", -40, "High-pass at 150 Hz; cut 300 Hz −3 dB", "Chorus"),
    ("Guitar", 45, "Cut 250 Hz −3 dB; boost 3 kHz +2 dB", "Delay (1/8 note)"),
    ("Lead vocal", 0, "High-pass at 100 Hz; boost 3 kHz +3 dB", "Compressor, reverb, delay (dotted 1/8)"),
    ("Shaker", -30, "High-pass at 500 Hz", "None"),
]
THRESH, RATIO, PEAK = -18, 4, -6
CUT_HZ, BOOST_HZ = 300, 3000


def comp_out(x, th=THRESH, ratio=RATIO):
    return x if x <= th else th + (x - th) / ratio


def note_ms(frac, bpm=TEMPO):
    """Length in ms of a note of `frac` quarter notes (1 = quarter, .5 = eighth, 1.5*.5 = dotted eighth) at bpm."""
    return frac * 60000 / bpm


GAIN_RED = PEAK - comp_out(PEAK)          # 9 dB
OUT_PEAK = comp_out(PEAK)                  # -15 dB
DELAYS = [("Quarter note", 1), ("Eighth note", .5), ("Dotted eighth", .75), ("Sixteenth note", .25)]


def ms(x):
    return f"{x:.0f} ms"


def num(v):
    return f"{v:+d}".replace("-", "−") if v else "0"


def minus(v):
    return str(v).replace("-", "−")


# ================================================================ drawings (original, code-drawn: black + accent only)
BANDS = [(20, 60, "SUB", "20–60 Hz", "rumble"), (60, 250, "BASS", "60–250 Hz", "weight"), (250, 500, "LOW-MID", "250–500 Hz", "mud"),
         (500, 2000, "MID", "500 Hz–2 kHz", "body"), (2000, 6000, "PRESENCE", "2–6 kHz", "clarity"),
         (6000, 20000, "AIR", "6–20 kHz", "sparkle")]


def eq_body(W=1600, name="eqmap", h=200, bs=28, rs=21, ws=24):
    """The frequency range in six bands (log scale) with an example EQ curve: a cut near 300 Hz and a boost near 3 kHz."""
    gut = 70
    pw = W - gut - 4
    lf0, lf1 = math.log10(20), math.log10(20000)

    def fx(f):
        return gut + pw * (math.log10(f) - lf0) / (lf1 - lf0)

    top = 12
    mid = top + h / 2
    out = [f'<rect x="{gut}" y="{top}" width="{pw}" height="{h}" fill="#fff" stroke="#000" stroke-width="2"/>']
    for g in (6, 0, -6):
        y = mid - g * (h / 2 - 20) / 6
        out.append(f'<line x1="{gut}" y1="{y:.1f}" x2="{gut + pw}" y2="{y:.1f}" stroke="#000" stroke-width="{2.4 if g == 0 else 1}" '
                   f'{"" if g == 0 else "stroke-dasharray=\"6 6\" opacity=\".45\""}/>')
        out.append(D.t_(gut - 10, y + 8, num(g), 22, 500, anchor="end"))
        D.lab(name + " dB", num(g), 22, gut - 14)
    for lo, hi, *_ in BANDS[1:]:
        out.append(f'<line x1="{fx(lo):.1f}" y1="{top}" x2="{fx(lo):.1f}" y2="{top + h}" stroke="#000" stroke-width="1" opacity=".3"/>')
    pts = []
    sc = (h / 2 - 20) / 6
    for i in range(0, int(pw) + 1, 4):
        lf = lf0 + (lf1 - lf0) * i / pw
        g = -6 * math.exp(-((lf - math.log10(CUT_HZ)) / .17) ** 2 / 2) + 4 * math.exp(-((lf - math.log10(BOOST_HZ)) / .2) ** 2 / 2)
        pts.append(f"{gut + i:.1f},{mid - g * sc:.1f}")
    out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{ACCENT}" stroke-width="6" stroke-linejoin="round"/>')
    for hz, g, txt in ((CUT_HZ, -6, f"CUT {CUT_HZ} Hz"), (BOOST_HZ, 4, f"BOOST {BOOST_HZ // 1000} kHz")):
        tw = D.text_w(txt, 22) + 18
        yb_ = mid - 14 if g < 0 else mid - g * sc - 14
        out.append(f'<rect x="{fx(hz) - tw / 2:.1f}" y="{yb_ - 26:.1f}" width="{tw:.1f}" height="34" rx="6" fill="#fff"/>')
        out.append(D.t_(fx(hz), yb_, txt, 22, 700))
        D.lab(name + " tags", txt, 22, 170)
    yb = top + h + 12
    fills = ["#4a4a4a", "#000", ACCENT, "#000", ACCENT, "#4a4a4a"]
    for (lo, hi, nm, rng_, word), fc in zip(BANDS, fills):
        x0, x1 = fx(lo), fx(hi)
        out.append(f'<rect x="{x0 + 2:.1f}" y="{yb}" width="{x1 - x0 - 4:.1f}" height="54" rx="7" fill="{fc}"/>')
        out.append(D.t_((x0 + x1) / 2, yb + 37, nm, bs, 700, fill_="#fff"))
        D.lab(name + " bands", nm, bs, x1 - x0 - 16)
        out.append(D.t_((x0 + x1) / 2, yb + 54 + 28, rng_, rs, 500))
        D.lab(name + " ranges", rng_, rs, x1 - x0 - 8)
        out.append(D.t_((x0 + x1) / 2, yb + 54 + 56, word, ws, 300))
        D.lab(name + " words", word, ws, x1 - x0 - 8)
    return "".join(out), W, yb + 54 + 66


def pan_body(W=1600, name="panmap", rh=44, fs=26, gut=230):
    """Where each track of the invented session sits, left to right (one row per track)."""
    x0, x1 = gut, W - 70
    cx = (x0 + x1) / 2
    half = (x1 - x0) / 2 - 50
    out = []
    for lab_, x, anc in (("L", x0 + 6, "start"), ("C", cx, "middle"), ("R", x1 - 6, "end")):
        out.append(D.t_(x, 28, lab_, 28, 700, anchor=anc))
    top = 40
    n = len(SESSION)
    out.append(f'<line x1="{cx}" y1="{top}" x2="{cx}" y2="{top + n * rh}" stroke="#000" stroke-width="2" stroke-dasharray="7 7"/>')
    for i, (tr, pan, *_r) in enumerate(SESSION):
        y = top + i * rh + rh / 2
        out.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#000" stroke-width="1.2" opacity=".35"/>')
        out.append(D.t_(gut - 14, y + fs * .36, tr, fs, 500, anchor="end"))
        D.lab(name + " tracks", tr, fs, gut - 24)
        x = cx + pan / 100 * half
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rh * .34:.1f}" fill="{ACCENT if pan else "#000"}"/>')
        val = "C" if pan == 0 else (f"L {-pan}" if pan < 0 else f"R {pan}")
        out.append(D.t_(x + rh * .34 + 12, y + 8, val, 22, 500, anchor="start"))
        D.lab(name + " values", val, 22, 90)
    return "".join(out), W, top + n * rh + 6


def comp_body(W=1500, H=640, name="comp"):
    """Compressor transfer curve: threshold -18 dB, ratio 4:1; a -6 dB peak comes out at -15 dB (9 dB of gain reduction)."""
    px0, px1, py0, py1 = 150, 760, 54, 554      # plot box
    lo, hi = -60, 0

    def X(v):
        return px0 + (v - lo) / (hi - lo) * (px1 - px0)

    def Y(v):
        return py1 - (v - lo) / (hi - lo) * (py1 - py0)

    out = [f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="#fff" stroke="#000" stroke-width="2"/>']
    out.append(f'<line x1="{X(lo)}" y1="{Y(lo)}" x2="{X(hi)}" y2="{Y(hi)}" stroke="#000" stroke-width="2" stroke-dasharray="8 8" opacity=".45"/>')
    pts = " ".join(f"{X(v):.1f},{Y(comp_out(v)):.1f}" for v in (lo, THRESH, hi))
    out.append(f'<polyline points="{pts}" fill="none" stroke="#000" stroke-width="7" stroke-linejoin="round"/>')
    out.append(f'<line x1="{X(THRESH)}" y1="{py0}" x2="{X(THRESH)}" y2="{py1}" stroke="{ACCENT}" stroke-width="3" stroke-dasharray="5 7"/>')
    out.append(f'<line x1="{X(PEAK)}" y1="{Y(PEAK)}" x2="{X(PEAK)}" y2="{py1}" stroke="{ACCENT}" stroke-width="3"/>')
    out.append(f'<line x1="{px0}" y1="{Y(OUT_PEAK)}" x2="{X(PEAK)}" y2="{Y(OUT_PEAK)}" stroke="{ACCENT}" stroke-width="3"/>')
    out.append(f'<line x1="{X(PEAK)}" y1="{Y(PEAK)}" x2="{X(PEAK)}" y2="{Y(OUT_PEAK)}" stroke="{ACCENT}" stroke-width="3"/>')
    out.append(f'<circle cx="{X(PEAK):.1f}" cy="{Y(OUT_PEAK):.1f}" r="13" fill="{ACCENT}"/>')
    out.append(f'<circle cx="{X(PEAK):.1f}" cy="{Y(PEAK):.1f}" r="9" fill="#fff" stroke="#000" stroke-width="4"/>')
    for v in (0, -30, -60):
        out.append(D.t_(X(v), py1 + 34, minus(v), 24, 500))
        D.lab(name + " ticks", minus(v), 24, 60)
        out.append(D.t_(px0 - 12, Y(v) + 8, minus(v), 24, 500, anchor="end"))
        D.lab(name + " yticks", minus(v), 24, 60)
    out.append(D.t_(X(THRESH), py1 + 34, minus(THRESH), 24, 700, fill_=ACCENT))
    D.lab(name + " ticks", minus(THRESH), 24, 55)
    out.append(D.t_(X(PEAK), py1 + 34, minus(PEAK), 24, 700, fill_=ACCENT))
    D.lab(name + " ticks", minus(PEAK), 24, 40)
    out.append(D.t_(px0 - 12, Y(OUT_PEAK) + 8, minus(int(OUT_PEAK)), 24, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " yticks", minus(int(OUT_PEAK)), 24, 60)
    out.append(D.t_((px0 + px1) / 2, py1 + 70, "INPUT (dB)", 24, 500))
    out.append(D.t_(20, 34, "OUTPUT (dB)", 24, 500, anchor="start"))
    tx = 830
    rows = [(f"Threshold {minus(THRESH)} dB", 52, 700), (f"Ratio {RATIO} : 1", 52, 700), (f"A {minus(PEAK)} dB peak is {PEAK - THRESH} dB over", 38, 500),
            (f"It comes out {int((PEAK - THRESH) / RATIO)} dB over, at {minus(int(OUT_PEAK))} dB", 38, 500),
            (f"Gain reduction: {int(GAIN_RED)} dB", 46, 700)]
    y = 130
    for txt, sz, wt in rows:
        out.append(D.t_(tx, y, txt, sz, wt, anchor="start", fill_=ACCENT if wt == 700 and "Gain" in txt else "#000"))
        D.lab(name + " callouts", txt, sz, W - tx - 10)
        y += sz + 52
    return "".join(out), W, H


def hero_body():
    return D.stack([eq_body(1100, "hero eq", 170, 22, 17, 20), pan_body(1100, "hero pan", 46, 27, 175)], 40)


DRAWINGS = {"hero": hero_body, "eqmap": lambda: eq_body(1600, "eqmap pic", 230), "panmap": lambda: pan_body(1600, "panmap pic", 42, 26),
            "comp": lambda: comp_body(1500, 640, "comp pic")}
DRAWING_PX = {"hero": 1900, "eqmap": 2000, "panmap": 2000, "comp": 2000}
SIDE = {"eqmap": ["Cut where tracks crowd each other", "Boost to bring out what you love", "Muddy sounds often live near 300 Hz",
                  "Try a big move first, then back off"],
        "panmap": ["Kick, snare, bass, vocal: center", "Spread the rest, left and right", "Left and right weigh the same",
                   "Width comes from panning"],
        "comp": ["Quiet sounds pass through unchanged", "Only the part over the line is squeezed", "A higher ratio squeezes harder",
                 "Make-up gain brings the level back"]}


def label_extras():
    eq_body(1250, "page eq", 190)
    pan_body(1250, "page pan", 36, 22)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "FX Deep Dive", "Tone. Depth. Space.",
     "Class 1, the first minute. Before class, take a short stretch of one of your own projects (or any track you may play in class) and "
     "mix it twice in Logic Pro: once dry, once with EQ, pan and effects. No audio is included in this deck. Open with my overview: "
     "level up your mixing by using at least 5 different effects creatively and intentionally."),
    (1, "listen", "Listen: dry, then mixed", "Dry, then mixed · The same track, played twice|Teacher: play it with every effect "
     "bypassed, then with them on.|What changed between the two?|Which effect did you notice first?|Could you hear space, width or "
     "clarity?",
     "Play the dry version first with no comment, then the mixed one. Take answers aloud: louder, clearer, wider, deeper, smoother. "
     "Ask what each change might have been. This sets up the whole project: every effect should have a reason. Keep your mix simple so "
     "students can name what they hear."),
    (1, "bullets", "What do effects do?", "EQ shapes tone and clarity|Compression evens out loud and quiet|Reverb and delay add depth "
     "and space|Panning adds width and separation|Modulation adds movement",
     "A plain-English tour from the project sheet vocabulary: EQ adjusts the volume of specific frequencies; compression reduces the "
     "dynamic range; reverb simulates the reflections of a space; delay repeats a sound after a set time; panning places sounds left "
     "or right; modulation (chorus, phaser, flanger) adds movement. Students will add their own words on the vocabulary page."),
    (1, "days", "Seven classes", "",
     "The shape of the project, from my pacing guide. Class 1: review the 11 FX from class notes, listen to examples, choose a source. "
     "Classes 2 to 5 are core working days: apply FX, EQ all tracks, set panning. Class 6: final adjustments, bounce, and prepare the "
     "presentation and three Padlet questions. Class 7: presentations with Padlet peer feedback. Hand out the project sheet now."),
    (1, "steps", "Steps 1 and 2: review, choose", "Review your notes on the 11 FX|Choose: your own project or a multitrack|A multitrack "
     "from Cambridge-MT: 8–16 tracks|Not a 40-track session|Fill in the Source log",
     "Steps 1 and 2 of the project sheet, shortened to fit the slide. Students revisit their notes on the 11 FX, then decide whether to "
     "remix their own earlier project or download a multitrack from Cambridge-MT. My tip: pick a song with 8 to 16 tracks, not a "
     "40-track session. Pre-select the sessions yourself if you can (see the Source page in the resource)."),
    (1, "bullets", "Every effect needs a reason", "What problem does this effect solve?|What do I hear when it is on?|Does it fit the "
     "genre?|Bypass it: is the mix better with it?",
     "My first common struggle: students apply FX randomly, without purpose. Push them to say why they use each effect. These four "
     "questions are the habit; they come back in the FX log and in the presentation. If a student breaks genre convention, my sheet says "
     "to be ready to explain the artistic reason. Less is more: a well-placed reverb or delay can transform a track."),
    (2, "pic", "Where sounds live", "eqmap",
     "Class 2. The frequency range in six bands on a log scale, with an example EQ curve: a cut near 300 Hz and a boost near 3 kHz. The "
     "names (rumble, weight, mud, body, clarity, sparkle) are common mixing words, not rules. Ask students which band their favorite "
     "instrument lives in. Then go straight to the live demo on the next slide."),
    (2, "steps", "Watch me: EQ on a soloed track", "Solo one track, open Channel EQ|Boost a narrow band and sweep it slowly|Now cut "
     "the same band: hear it vanish|Un-solo: is the whole mix clearer?|Bypass the EQ and compare (A/B)",
     "This is the live demo from my teacher notes: EQ feels invisible to beginners, so make dramatic cuts and boosts on a soloed track. "
     "Use a drum or bass track from your own project. Boost about 12 dB, sweep, then cut. Return to normal and ask what you fixed. EQ "
     "is the most powerful tool, so get it right before adding other effects."),
    (2, "pic", "Worked example: place the band", "panmap",
     "An invented eight-track session, described on paper only; nothing here is a recording. Kick, snare, bass and lead vocal sit in the "
     "center. Hi-hat, keys, guitar and shaker are spread: keys 40 left, shaker 30 left, hi-hat 25 right, guitar 45 right, so left and "
     "right balance (70 each). My struggle: students leave everything center. Play a professional mix of your choice and point out the width."),
    (2, "steps", "Watch me: reverb and delay", "Click a Send slot, choose Bus 1 (an Aux appears)|Add one reverb to the Aux; send to "
     "taste|Delay time from tempo: 1/8 at 100 BPM = 300 ms|Turn it down until you only miss it when off",
     "A short demo of effects on a send. In the mixer, click an empty Send slot on a track and choose Bus 1; Logic makes an Aux channel. "
     "Put a reverb on the Aux and turn the send up on each track that needs it. For a delay, the time follows the tempo: at 100 BPM a "
     "quarter note is 600 ms, an eighth 300 ms and a dotted eighth 450 ms."),
    (2, "pic", "Worked example: compression", "comp",
     "Compression by the numbers, on an invented signal. Threshold is -18 dB and the ratio is 4:1. A peak at -6 dB is 12 dB over the "
     "threshold; the compressor lets only a quarter of that through, so it comes out 3 dB over, at -15 dB. The gain reduction is 9 dB. "
     "Real plug-ins add attack, release and make-up gain; students can explore those on their own."),
    (3, "bullets", "Working day: EQ and pan every track", "EQ every track, one at a time|Pan each instrument into its own place|Fill in "
     "the Track map|Judge it in the whole mix, not only solo",
     "Class 3 is the first working day. Step 4 of the project sheet, shortened here: EQ and pan every track. The requirement is that "
     "every track is EQ'd and panned thoughtfully, so check the Track map for empty boxes. Circulate and ask each student to solo a "
     "track, make one EQ move, and say what problem it fixes."),
    (4, "bullets", "Working day: effects with a reason", "Use at least 5 different FX|Write the reason in your FX log|A/B every "
     "effect: bypass, listen, decide|Check on headphones and on speakers",
     "Class 4, a working day. Steps 3 and 5 of the project sheet, shortened here: plan and apply at least 5 different effects, then "
     "check the mix on headphones and speakers. Always A/B test: bypass the plug-in and listen with and without it. Class 5 is a full "
     "working day with no new slide: refine the mix."),
    (6, "bullets", "Refine, bounce, prepare", "Final level and FX tweaks|Bounce a .mp3 or .wav|Zip the .logicx project|Write your 3 "
     "Padlet questions",
     "Class 6. Steps 5 and 6 of the project sheet, shortened to fit the slide: adjust levels and FX settings, then finalize by bouncing "
     "and preparing to walk the class through the FX choices. Bounce: File, Bounce, Project or Section. Zip: Control-click the .logicx "
     "in Finder, Compress. Students also write their three Padlet questions today."),
    (6, "check", "What you turn in", "Bounced .mp3 or .wav of the final mix|Zipped .logicx project|Named: Your Name – FX Deep "
     "Dive|At least 5 different FX, ready to discuss|All tracks EQ’d and panned|Padlet post with your 3 questions|Answer 2 questions "
     "on classmates’ posts",
     "The submission checklist from the project sheet, in short form. Show where students upload (your class page) and where the "
     "Padlet board is. Remind students that the FX log is theirs: it is what they will use to walk the class through their choices."),
    (6, "rubric", "How it’s scored", "",
     "My rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and mine. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (7, "bullets", "Presentation day", "Walk the class through your FX choices|Your Padlet post: 3 questions about your project|Answer "
     "at least 2 of each classmate’s 3|Listen like a mixer: what did they do, and why?",
     "Class 7, presentations with Padlet Q and A. Each student plays the final mix and explains the effects they chose and why. During "
     "classmates' presentations, every student answers at least 2 of their 3 questions on their Padlet post. If time allows, my mix "
     "critique idea fits here: play a volunteer mix on the main speakers."),
    (7, "closer", "One last thing…", "You started with a track.|You shaped tone and space.|Every effect had a reason.|Now it sounds like "
     "yours.",
     "Close with what my teacher notes say this project builds: the primary mixing skills, a shift in focus entirely to post-production. "
     "Every student left with a mix where each effect has a reason. Remind them that EQ, pan and a single well-placed reverb or delay "
     "already go a long way."),
]
SHOTS1 = [("pacing", "Pacing guide", "7 class periods, slide by slide"), ("trackmap", "Track map", "EQ and pan every track"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 2, 7, 9, 11, 16]
SHOTS3 = [("setup", "Choosing a source"), ("eqguide", "EQ guide"), ("example", "Worked example"), ("proj1", "Project sheet"),
          ("proj2", "Steps"), ("fxnotes", "FX notes"), ("fxlog", "FX log"), ("changes", "What changed")]

# ================================================================ page plan
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "changes", "logicref", "eqguide", "links", "example",
        "source", "fxnotes", "trackmap", "fxlog", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "terms"]
PREVIEW_PICKS = ["pacing", "trackmap", "proj2", "rubric"]

COVER_A = "Shape tone, depth and space"
COVER_C = "DMP2 · EQ · panning · reverb · delay · compression · intro slides"
PDF_COVER = dict(a=32, b=70, c=14, art=7.3)
SQ_COVER = dict(a=50, b=140, c=27, art=700)
SQ_B_LINES = ["FX Deep Dive"]
SQ_SUB = "7 class periods · EQ · pan · reverb · delay · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, student pages and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Source guide, EQ guide, tutorial links, worked example, FX log", 28)}
SQ_BANDS = {1: "Review <em>·</em> choose <em>·</em> EQ and pan <em>·</em> effects <em>·</em> present",
            2: "Hook <em>·</em> EQ demo <em>·</em> pan <em>·</em> compression <em>·</em> rubric",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, video, lyrics or songs are included. Students bring a track of their own or download a multitrack from the "
             "Cambridge-MT library themselves (page @SETUP), so you know exactly where every sound came from.")
CREDITS = ["Worked example (an invented eight-track session described on paper), the EQ map, pan map and compressor drawings and "
           "layouts: original work, Hudson Beat.",
           "No audio, video, lyrics, album art, chart data or multitrack sessions are included. Cambridge-MT and Native Instruments are "
           "named only as the owner’s resource list names them; they are not affiliated with or endorsing this resource. The list of the "
           "11 FX and the tutorial links page are from the teacher’s own materials; the linked sites and videos belong to their "
           "makers and are not included. The EQ Cheatsheet in the teacher’s course materials is by another author and is not included. Padlet and "
           "YouTube are named only as examples of tools you may already use."]
LOGIC_INTRO = ("Everything students need in Logic for this project, in one table. Demonstrate EQ (slide 8) and sends (slide 10), then let "
               "students work. Names are from current Logic Pro versions.")
LOGIC_REF = [("Import a multitrack", "File › Import › Audio File (Shift-Command-I), or drag the audio files onto the Tracks area. Set the "
              "project tempo if the session came with one."),
             ("Mixer", "Press X to show or hide the Mixer. Each track has a channel strip with an EQ display, Audio FX slots, Sends, a Pan "
              "knob and a fader."),
             ("Add an effect", "Click an empty Audio FX slot on a channel strip and choose a plug-in from the menu. Plug-ins are grouped "
              "by kind: EQ, Dynamics, Reverb, Delay, Distortion, Modulation."),
             ("EQ", "Double-click the EQ display on the channel strip to open Channel EQ. Drag a band up to boost or down to cut; the "
              "Q setting sets how wide the move is."),
             ("Compression", "Audio FX slot › Dynamics › Compressor. Lower the Threshold until the meter shows gain reduction, then set "
              "the Ratio."),
             ("Reverb and delay", "Reverb › ChromaVerb (or Space Designer). Delay › Echo or Stereo Delay. Try a delay time that matches "
              "the tempo, such as 1/8 note."),
             ("Chorus, phaser, flanger", "Modulation › Chorus, Phaser or Flanger. These move the sound over time; use a small amount."),
             ("Distortion", "Distortion › Distortion II or Overdrive. A little adds warmth; a lot is an effect on its own."),
             ("Send and bus", "Click a Send slot and choose Bus 1; an Aux channel appears. Put a reverb or delay on the Aux, then turn each "
              "track’s send knob up to taste."),
             ("Pan", "Drag the Pan knob under the fader; Option-click it to return to center."),
             ("A/B test", "Click the plug-in’s Bypass button in its window title bar to hear the track without it, then switch it back "
              "on. Use Solo (S) to hear one track alone."),
             ("Bounce and zip", "File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and "
              "choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; .mp3 or .wav and zipped .logicx uploaded", "Padlet post created with my 3 questions",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my mix:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:10.8pt;margin-bottom:2pt">FX without purpose: the FX log (page @FXLOG) asks why, and slide 6 gives students four questions.</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">EQ feels invisible: the EQ guide (page @EQGUIDE) is a demo script, and slide 8 is the demo.</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Overwhelming sessions: page @SETUP helps you pre-select, and the Source log (page @SOURCE) '
    'has students count tracks.</li>'
    '<li style="font-size:10.8pt;margin-bottom:2pt">Everything panned center: slide 9 and the Track map (page @TRACKMAP).</li>'
    '<li style="font-size:10.8pt;margin-bottom:0">Treated as composition: slide 6 and the goals on page @PROJ1 keep the focus on FX.</li></ul></div>')
TN1_SIZE = 13.6
PROJ_SIZE = 13.0
VOCAB_GAP = 5
LOGIC_SIZE = 10.8
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ custom pages
def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example", "How to use, overview, choosing a source, pacing, teacher notes, what changed, Logic "
              "reference, EQ guide, tutorial links, worked example"),
             ("Student pages", "source", "present", "Source log, FX notes, Track map, FX log, project sheet (3 pages), rubric, vocabulary, "
              "feedback planner"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12.2pt;line-height:1.45">A {CLASSES}-class-period mixing project for high school music technology. Each student '
             f'takes an existing track, either one of their own earlier projects or a multitrack from the Cambridge-MT library, and '
             f'mixes it in Logic Pro with at least five different audio effects: EQ and panning on every track, plus effects such as '
             f'compression, reverb, delay or modulation. It is a structured project from my Digital Music Production 2 course (focus: '
             f'mixing and effects), and the projects in that course can be taught in any order.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and my teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Decide where source tracks come from and pre-select sessions (page {D.IX("setup")}): no audio is included.</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("source")}–{D.IX("present")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Class 5 is a working day with no new slide. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Source tracks:</b> students may use their own earlier project, so the project also works without any download.</li>'
             f'<li><b>Easier or harder:</b> my variations on page {D.IX("tn1")}.</li>'
             f'<li><b>Feedback board:</b> my sheets use Padlet for the three questions; any class board works.</li>'
             f'<li><b>Grading:</b> my rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students take a '
             f'track, EQ and pan every part, add at least five effects with a reason for each, and present their choices.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a trademark of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">From my DMP2 project menu</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · {MENU_TYPE} · {MENU_FOCUS}<br>{MENU_DESC}</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12.8pt;line-height:1.5">One Logic Pro mix: an existing track, either a student’s own earlier project '
             f'or a multitrack, with every track EQ’d and panned and at least five different effects chosen for the genre. They hand in '
             f'a bounced .mp3 or .wav of the final mix, the zipped .logicx project, and a Padlet post with three feedback questions, '
             f'then walk the class through their FX choices.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12.8pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p>Supports the National Core Arts Standards for Music (Music Technology, high school): refining original '
             f'work (MU:Cr3.1), presenting it (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:11.8pt;line-height:1.4'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:10.4pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}: the second-year course, after a first year of Logic Pro basics</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: review and choose, four working days, bounce, present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Channel EQ, Compressor, ChromaVerb or Space Designer, Echo, Chorus and other plug-ins, '
             f'pan, sends, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Source tracks (students’ own projects, or multitracks they download), headphones, a '
             f'feedback board, and speakers if you can</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>My rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s '
             f'and the teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0">Students should already '
             f'know how to open a project, work in the Mixer, and save, bounce and zip in Logic. My project uses the 11 FX they took notes '
             f'on in class (listed on page {D.IX("fxnotes")}); the Logic quick reference (page {D.IX("logicref")}) covers every tool this project uses.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "DMP2 · Structured", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<div class="cols"><div class="big">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student (a current version), and <b>headphones</b>. Speakers help for the '
             f'headphones-and-speakers check in step 5.</li>'
             f'<li><b>A source track for every student</b>: their own earlier project, or a multitrack they download. Nothing is included.</li>'
             f'<li><b>A place to submit</b> an .mp3 or .wav and a zipped .logicx project (your class page).</li>'
             f'<li><b>A feedback board</b> for the three questions (my sheets use Padlet).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("source")}–{D.IX("present")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:12pt;margin-bottom:8pt") for c in [
                 "Pre-select 5–10 multitrack sessions with sensible track counts (8–16), as my notes suggest, or decide to let students choose.",
                 "Read the Cambridge-MT library’s terms of use so you can tell students what they may do with a download.",
                 "Mix a short stretch of your own track twice, dry and with effects, for slide 2.",
                 "Print the student pages; set up the submission spot and the feedback board."]) +
             f'</div><div class="big">'
             f'{D.H2("Choosing a source", True)}'
             f'<p style="font-size:11.4pt">My project gives two choices. Page {D.IX("source")} is the student log for either one.</p>'
             f'<ul style="font-size:11.4pt;line-height:1.42">'
             f'<li><b>Remix your own project.</b> No download is needed, and the student already knows the track. Check that it has at '
             f'least five separate tracks, so there is something to EQ and pan.</li>'
             f'<li><b>A multitrack from Cambridge-MT.</b> The library’s sessions are separate audio files for each instrument. Students '
             f'download one from the library’s own site and import it into Logic (page {D.IX("logicref")}). This kit does not include or '
             f'redistribute any of them.</li></ul>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">Pre-selecting sessions</span><ul style="margin:0">'
             f'<li style="font-size:11.4pt">Aim for 8–16 tracks; a 40-track session is a different project.</li>'
             f'<li style="font-size:11.4pt">Download each one yourself and open it in Logic before students do.</li>'
             f'<li style="font-size:11.4pt">Note the genre of each, so students can pick one whose style they can describe.</li>'
             f'<li style="font-size:11.4pt">Keep a short list on the board, with the track count beside each.</li></ul></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Terms and credit</span><p style="margin:0;font-size:11.4pt">Libraries set '
             f'their own rules for what you may do with their files, such as using them to practice mixing but not sharing them. Check '
             f'before students post a mix publicly, and credit the source if the library asks.</p></div>'
             f'</div></div>')
    return D.page("Setup and choosing a source track", "SETUP", "Teacher", inner, n, key="setup")


def eqguide_page(n, wm=False):
    probs = [("Muddy or boomy", "Cut a little around 200–400 Hz"), ("Boxy, closed in", "Cut a little around 400–800 Hz"),
             ("Harsh or sharp", "Cut a little around 2–5 kHz"), ("Thin or weak", "Boost a little around 100–250 Hz"),
             ("Dull, no sparkle", "Boost the highs, 6 kHz and up"), ("Rumble you cannot hear", "High-pass below 30–80 Hz")]
    rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a, b in probs)
    kinds = [("Bell", "Boosts or cuts around one frequency. The Q setting makes it narrow or wide."),
             ("Shelf", "Boosts or cuts everything above (high shelf) or below (low shelf) a frequency."),
             ("High-pass", "Removes everything below a frequency. Good for clearing rumble from tracks that do not need low end."),
             ("Low-pass", "Removes everything above a frequency. Good for making a sound darker.")]
    krows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a, b in kinds)
    inner = (f'<p style="margin:0 0 4pt;font-size:12pt">My notes say EQ feels invisible to beginners, so do a live demo early. This page is a '
             f'one-page guide you can project or print, and the plan for a five-minute demo (slide 8). The bands and fixes are rules of '
             f'thumb, not laws: tell students to trust their ears.</p>'
             f'<div style="width:7.5in;margin:4pt auto 6pt">{D.body_svg(eq_body(1250, "page eq", 190))}</div>'
             f'<div class="cols" style="gap:14pt"><div>'
             f'{D.H2("Common problems and a first try", True)}<table class="t" style="font-size:10.8pt"><tr><th style="width:40%">It sounds…</th>'
             f'<th>Try</th></tr>{rows}</table></div>'
             f'<div>{D.H2("The five-minute demo", True)}<ol style="font-size:11pt;line-height:1.4">'
             f'<li>Pick a drum or bass track from your own project and <b>solo</b> it.</li>'
             f'<li>Open Channel EQ. Make a narrow band and <b>boost 12 dB</b>. Sweep it slowly from low to high.</li>'
             f'<li>Stop on a spot that sounds bad. <b>Cut</b> it by 6 dB.</li>'
             f'<li>Bypass the EQ and back: that is A/B.</li>'
             f'<li>Un-solo. Ask: did the mix get clearer?</li></ol></div></div>'
             f'{D.H2("Four kinds of EQ band")}<table class="t" style="font-size:10.6pt"><tr><th style="width:16%">Band</th><th>What it does</th></tr>{krows}</table>'
             f'<div class="cols" style="gap:14pt;margin-top:6pt"><div class="box acc-b"><span class="k">EQ rules for students</span>'
             f'<p style="margin:0;font-size:11pt">Cut before you boost. Make small moves. Listen to the whole mix, not only the solo.</p></div>'
             f'<div class="box"><span class="k">Panning</span><p style="margin:0;font-size:11pt">Keep the kick, snare, bass and lead vocal near '
             f'the center. Spread other parts and balance the two sides (page {D.IX("example")}).</p></div></div>')
    return D.page("EQ guide and live demo plan", "EQ GUIDE", "Teacher + student", inner, n, key="eqguide")


def example_page(n, wm=False):
    rows = "".join(f"<tr><td><b>{t}</b></td><td>{('center' if p == 0 else ('left ' + str(-p) if p < 0 else 'right ' + str(p)))}</td><td>{e}</td><td>{f}</td></tr>"
                   for t, p, e, f in SESSION)
    drows = "".join(f"<tr><td>{a}</td><td><b>{ms(note_ms(b))}</b></td></tr>" for a, b in DELAYS)
    inner = (f'<p style="margin:0 0 3pt">An <b>invented eight-track session, described on paper</b>: no audio is included, so the numbers '
             f'are easy to check. Students’ sessions will differ.</p>'
             f'{D.H2("1 · Place the band", True)}<div style="width:6.8in;margin:1pt auto 3pt">{D.body_svg(pan_body(1250, "page pan", 36, 22))}</div>'
             f'<p class="small" style="margin:0 0 2pt">Left tracks: keys 40 + shaker 30 = 70. Right tracks: hi-hat 25 + guitar 45 = 70. The sides balance.</p>'
             f'{D.H2("2 · The plan for each track")}'
             f'<table class="t" style="font-size:9.8pt"><tr><th style="width:13%">Track</th><th style="width:13%">Pan</th><th style="width:38%">EQ</th>'
             f'<th>Effects</th></tr>{rows}</table>'
             f'<p class="small" style="margin:0 0 2pt">Five different effects are used: EQ, compressor, reverb, delay and chorus.</p>'
             f'<div class="cols" style="gap:12pt"><div class="box"><span class="k">3 · Delay times at {TEMPO} BPM</span>'
             f'<table class="t" style="font-size:10.4pt;margin:0"><tr><th>Note</th><th>Delay time</th></tr>{drows}</table>'
             f'<p class="small" style="margin:3pt 0 0">One beat = 60 000 ÷ {TEMPO} = {ms(note_ms(1))}.</p></div>'
             f'<div class="box"><span class="k">4 · Compression, by the numbers</span>'
             f'<p style="margin:0;font-size:11.4pt;line-height:1.5">Threshold {minus(THRESH)} dB, ratio {RATIO}:1. A peak at {minus(PEAK)} dB is '
             f'{PEAK - THRESH} dB over the threshold. {PEAK - THRESH} ÷ {RATIO} = {int((PEAK - THRESH) / RATIO)} dB over, so it comes out '
             f'at {minus(THRESH)} + {int((PEAK - THRESH) / RATIO)} = {minus(int(OUT_PEAK))} dB. Gain reduction = {int(GAIN_RED)} dB '
             f'(slide 11).</p></div></div>')
    return D.page("Worked example · an invented session", "EXAMPLE", "Teacher", inner, n, ak=True, key="example")


def links_page(n, wm=False):
    def one(t, u):
        return (f'<div style="margin:0 0 2.5pt;line-height:1.15"><span style="font-size:9.4pt">{t.replace("&", "&amp;")}</span><br>'
                f'<span style="font-size:8pt;color:#333;word-break:break-all">{u}</span></div>')

    def lab(c):
        return (f'<div style="font-family:Oswald;font-weight:700;text-transform:uppercase;font-size:10.4pt;margin:5pt 0 2pt;'
                f'border-bottom:1pt solid #000">{c}</div>')

    def block(c, ls):
        return lab(c) + "".join(one(t, u) for t, u in ls)
    half = 6
    left = "".join(block(c, ls) for c, ls in LINKS[:half])
    right = "".join(block(c, ls) for c, ls in LINKS[half:]) + lab("Also on my list") + "".join(one(t, u) for t, u in LINKS_EXTRA)
    inner = (f'<p style="margin:0 0 2pt;font-size:10.6pt;line-height:1.3">My own list of tutorials, one group for each of the 11 FX (page '
             f'{D.IX("fxnotes")}), from the teacher’s own materials. Each is a web address to type in, or search the title. Nothing is embedded '
             f'or included; the sites belong to their makers and addresses can change.</p>'
             f'<div class="cols" style="gap:16pt"><div>{left}</div><div>{right}</div></div>')
    return D.page("Tutorial links for each effect", "LINKS", "Teacher + student", inner, n, key="links")


def source_page(n, wm=False):
    rows = "".join(f"<tr><td style='text-align:center'><b>{i}</b></td><td></td><td></td><td></td></tr>" for i in range(1, 17))
    inner = (f'<div class="fl"><b>My source:</b><span style="flex:0 0 0.2in"></span><span style="flex:0 0 0.3in;height:15pt;border:1.2pt solid #000"></span>'
             f'<b>my own previous project</b><span style="flex:0 0 0.2in"></span><span style="flex:0 0 0.3in;height:15pt;border:1.2pt solid #000"></span>'
             f'<b>a Cambridge-MT multitrack</b><span style="border:0"></span></div>'
             f'<div class="fl"><b>Name of the project or song:</b><span></span></div>'
             f'<div class="fl"><b>Genre:</b><span></span><b>Tempo:</b><span style="flex:0 0 0.8in"></span><b>Tracks:</b><span style="flex:0 0 0.6in"></span></div>'
             f'<p style="margin:0 0 4pt;font-size:10.6pt">Count the tracks. Aim for 8–16. If there are many more, ask your teacher before you start.</p>'
             f'<table class="map"><tr><th style="width:6%">#</th><th style="width:30%">Track name</th><th style="width:22%">Kind of sound</th>'
             f'<th>What I think it needs</th></tr>{rows}</table>'
             f'<div class="fl" style="margin-top:8pt"><b>Genre conventions I should respect (reverb? width? how loud?):</b><span></span></div>'
             f'<div class="ln2" style="margin-bottom:2pt"></div>')
    return D.page("Source log", "STUDENT", "Class 1", inner, n, wm, name=True, key="source")


def fxnotes_page(n, wm=False):
    rows = "".join(f"<tr><td style='text-align:center;height:34pt'><b>{i}</b></td><td><b>{fx}</b></td><td></td><td></td></tr>" for i, fx in enumerate(FX11, 1))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">These are the 11 FX from the class notes. For each one, write in your own words what it '
             f'does to the sound and where you might use it. Then circle the ones you plan to use: you need at least 5 different effects. '
             f'Tutorial links for each are on page {D.IX("links")}.</p>'
             f'<table class="map"><tr><th style="width:6%">#</th><th style="width:22%">Effect</th><th style="width:36%">What it does to the sound</th>'
             f'<th>Where I might use it</th></tr>{rows}</table>'
             f'<div class="cols" style="gap:12pt;margin-top:8pt"><div class="box acc-b"><span class="k">Rule</span><p style="margin:0">'
             f'{REQS[1]}.</p></div><div class="box"><span class="k">Check</span><p style="margin:0">Can you say, for each circled effect, '
             f'what it does and why it fits your genre?</p></div></div>')
    return D.page("FX notes", "STUDENT", "Class 1", inner, n, wm, name=True, key="fxnotes")


def trackmap_page(n, wm=False):
    cb = D.checkbox(13)
    rows = "".join(f"<tr><td style='height:31pt'></td><td style='text-align:center'>{cb}</td><td></td><td style='text-align:center'>{cb}</td><td></td><td></td></tr>"
                   for _ in range(12))
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">One row per track. {REQS[2]}. Tick the boxes when it is done, and write down what '
             f'you did and why.</p>'
             f'<table class="map"><tr><th style="width:15%">Track</th><th style="width:7%">EQ’d</th><th style="width:27%">EQ: where, boost or cut, why</th>'
             f'<th style="width:8%">Panned</th><th style="width:16%">Pan (L / C / R)</th><th>Effects on it</th></tr>{rows}</table>'
             f'{D.H2("Mix check (step 5)")}'
             + "".join(D.chk(c, 12, "font-size:11pt;margin-bottom:5pt") for c in [
                 "Listened on headphones",
                 "Listened on speakers, or on a different pair of headphones",
                 "Left and right feel balanced",
                 "I can hear every important part",
                 "I bypassed each effect once to check it helps"]))
    return D.page("Track map", "STUDENT", "Classes 2–5", inner, n, wm, name=True, key="trackmap")


def fxlog_page(n, wm=False):
    blocks = ""
    for i in range(1, 6):
        blocks += (f'<div class="box" style="margin-bottom:5pt;padding:4pt 10pt 0"><span class="k" style="margin-bottom:2pt">FX {i}</span>'
                   f'<div class="fl" style="margin:0 0 4pt"><b>Effect and plug-in:</b><span></span><b>On track:</b><span></span></div>'
                   f'<div class="fl" style="margin:0 0 5pt"><b>The reason (what problem or feeling it solves):</b><span></span></div>'
                   f'<div class="fl" style="margin:0 0 5pt"><b>Main settings:</b><span></span></div>'
                   f'<div class="fl" style="margin:0 0 5pt"><b>Bypass test: what changed?</b><span></span></div></div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt">A planning page for step 3, and your notes for the presentation. For each effect, write '
             f'the reason before you move on. If you break the usual rules of your genre, write why.</p>{blocks}'
             f'<div class="fl"><b>My favorite change, and why:</b><span></span></div>')
    return D.page("FX log", "STUDENT", "Classes 2–7", inner, n, wm, name=True, key="fxlog")


PAGES = {"links": links_page, "howto": howto_page, "overview": overview_page, "setup": setup_page, "eqguide": eqguide_page, "example": example_page,
         "source": source_page, "fxnotes": fxnotes_page, "trackmap": trackmap_page, "fxlog": fxlog_page}


# ================================================================ content checks (music arithmetic, owner text, no audio)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 6), reqs=(REQS, 5), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 7),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 5), resources=(RESOURCES, 4))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp} (the owner's count)")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is the owner's /25, levels 1-5")
    if [c for c, _ in RUBRIC] != ["Creativity & Originality", "Technical Skill / DAW Use", "Composition & Structure",
                                  "Sound Design & Mix Quality", "Documentation & Presentation"]:
        errs.append("rubric categories must be the owner's, in order")
    if FILE_NAME not in CHECK[2] or "FX Deep Dive" not in FILE_NAME:
        errs.append("file name must stay as the owner wrote it")
    if "at least 5" not in REQS[1] or "11" not in REQS[1]:
        errs.append("requirement 2 must stay at least 5 of the 11 FX")
    # the worked example adds up
    if note_ms(1) != 600 or note_ms(.5) != 300 or note_ms(.75) != 450 or note_ms(.25) != 150:
        errs.append("delay times at 100 BPM: 600 / 300 / 450 / 150 ms")
    if (PEAK - THRESH) != 12 or comp_out(PEAK) != -15 or GAIN_RED != 9 or comp_out(-30) != -30:
        errs.append("compression example: -6 dB peak, threshold -18, 4:1 -> -15 dB out, 9 dB gain reduction")
    if not 8 <= len(SESSION) <= 16 or any(not -100 <= p <= 100 for _, p, *_ in SESSION):
        errs.append("session: 8-16 tracks, pan within -100..100")
    if sum(p for _, p, *_ in SESSION) != 0:
        errs.append("session: left and right pans must balance (sum 0)")
    center = {t for t, p, *_ in SESSION if p == 0}
    if not {"Kick", "Snare", "Bass", "Lead vocal"} <= center:
        errs.append("session: kick, snare, bass and lead vocal stay in the center")
    kinds = set()
    for _, _, e, f in SESSION:
        if e:
            kinds.add("EQ")
        for k_, w in (("Compressor", "Compressor"), ("Reverb", "Reverb"), ("Delay", "Delay"), ("Chorus", "Chorus")):
            if w.lower() in f.lower():
                kinds.add(k_)
    if len(kinds) < 5:
        errs.append(f"worked example must use at least 5 different effects, uses {sorted(kinds)}")
    if BANDS[0][0] != 20 or BANDS[-1][1] != 20000 or any(BANDS[i][1] != BANDS[i + 1][0] for i in range(len(BANDS) - 1)):
        errs.append("EQ bands must cover 20 Hz to 20 kHz without gaps")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    for need in ("No audio",):
        if need not in notes[0]:
            errs.append(f"deck slide 1 notes must say '{need}'")
    txt = " ".join(flat)
    for need in ("No audio, video, lyrics or songs are included", "invented eight-track session, described on paper",
                 "Your Name – FX Deep Dive", "Final Grade = Average of Student + Teacher", "Cambridge-MT"):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt or "10–12" in txt or "second-year course" not in txt:
        errs.append("PDF: 'Grades 9–12' and 'the second-year course' (no '10–12')")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "10-12" in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up:
        errs.append("UPLOAD.md: must say no audio is included and record the open questions")
    for i in (4, 11, 12, 13):   # slides that shorten the owner's wording must say so
        if "shortened" not in notes[i].lower():
            errs.append(f"deck slide {i + 1} notes: must say the owner's wording is shortened")
    ch = flat[D.IX("changes") - 1]
    if "slide 5" not in ch or "slide 12" not in ch or "slide 13" not in ch or "slide 14" not in ch:
        errs.append("'What changed' page must list the shortened slides")
    tn2 = flat[D.IX("tn2") - 1]
    lab = tn2.find(D.GRADING_TIPS_LABEL)
    if lab < 0 or any("Channel EQ" in g for g in GRADING):
        errs.append("page tn2: kit suggestions must sit under the label, never in the owner's rubric line")
    for banned in ("Billie", "Beatles", "Spotify"):
        if banned in alldeck or banned in txt:
            errs.append(f"must not name songs, artists or services ({banned})")
    return errs


def check_summary():
    return (f"Delay times at {TEMPO} BPM 600/300/450/150 ms; compression -6 dB peak, threshold {THRESH} dB, {RATIO}:1 -> {int(OUT_PEAK)} dB "
            f"({int(GAIN_RED)} dB gain reduction); the invented session has {len(SESSION)} tracks with balanced pans and 5 different effects; "
            f"the owner's lists counted (4 goals, 6 terms, 5 requirements, 7 steps, 4 tips, 7 checklist items, 5 struggles, 4 resources); "
            f"{len(CHANGES)} wording changes disclosed; no audio included; grades 9-12; grading tips labelled as suggestions.")


if __name__ == "__main__":
    D.main(sys.modules[__name__])
