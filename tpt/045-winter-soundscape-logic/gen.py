#!/usr/bin/env python3
"""Logic Pro project kit: Winter Soundscape (TpT 045): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content, the storm arc and its arithmetic, the worked example, frequency map, automation lanes,
                              drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap, overflow and dead space,
                              truncated slide bullets, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 031, 036 and 040). Students design a snowstorm soundscape from scratch in
Logic Pro: wind, ice and pads from Alchemy, Quick Sampler and Retro Synth, layered and shaped with automation (filter cutoff, volume,
pan, reverb send), reverb, EQ and stereo width, over a build / peak / fade arc of 60 to 90 seconds. There is no melody to chart and no
audio ships: the kit gives a scene brief, sound-palette cards, Alchemy recipes in words, automation diagrams, a layer map, a storm-arc
timeline planner and a worked example (60 s at 120 BPM = 30 bars), and every number is computed here and verified by --check.
No music notation is drawn anywhere in this kit.

Shared builder: ../_dmp2_common/dmp2.py (see its README).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402
D.DISCLOSURE_NEW = "Created with the help of digital and AI tools."   # fix: this kit has no notation or answer keys to verify

# fix: the shared reflection page ran its teacher box into the footer rule; add bottom clearance in this kit only.
_reflect_orig = D.reflect_page
def _reflect_tight(n, watermark=False):
    return _reflect_orig(n, watermark).replace('<div class="box" style="margin-top:2pt">', '<div class="box" style="margin-top:2pt;margin-bottom:12pt">')
D.reflect_page = _reflect_tight
D.STD_PAGES["reflect"] = _reflect_tight

# fix: the closing slide's reflection box sat ~0.1 in above the footer rule; lift it before the deck PDF is made.
_deck_pdf_orig = D.deck_pdf
def _deck_pdf_lifted():
    from pptx import Presentation
    from pptx.util import Inches
    p = os.path.join(HERE, "winter-soundscape-intro-deck.pptx")
    prs = Presentation(p)
    sl = prs.slides[len(prs.slides) - 1]
    for sh in sl.shapes:
        if Inches(5.8) <= sh.top < Inches(7.0) and sh.left < Inches(7.0):
            sh.top = sh.top - Inches(0.2)
    prs.save(p)
    _deck_pdf_orig()
D.deck_pdf = _deck_pdf_lifted

ORIGINAL = True
SLUG = "winter-soundscape"
TITLE = "Winter Soundscape"
ACCENT = "#1F6FA8"          # this product's single accent: icy blue
ACC_LIGHT = "#DCEBF6"
PRICE = "8.00"
CLASSES = 4
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Project-based Learning", "Projects", "Rubrics"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Sound Design in Logic Pro | Alchemy Soundscape Project | High School Music Tech"
DESC_START = "Sound design and automation for high school music technology:"
DESC_MUST = ["Winter Soundscape", "Alchemy", "automation", "no audio", "no melody", "reverb", "Quick Sampler", "snowstorm"]
ZIP_DIR = "Winter Soundscape - Hudson Beat"
ZIP_DATE = (2026, 11, 15, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Sound Design Project</i> | 4 class periods"
DECK_STRAP = "A snowstorm from scratch"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Ro" + "land", "Sle" + "igh Ride"]

PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2", "brief", "palette1", "palette2",
        "alchemy", "auto1", "auto2", "space", "timeline", "layers", "autoplan", "proj1", "proj2", "proj3", "rubric", "vocab", "present",
        "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the project text (original; students read these pages)
OVERVIEW = ("Design a snowstorm from scratch. You are the sound designer for a scene, and you have 60 to 90 seconds to make a storm that "
            "arrives, builds, peaks and fades away, using no melody at all. In Logic Pro you will build six or more layers (wind, ice, "
            "rumble, pads, noise textures) with Alchemy, Quick Sampler and Retro Synth, then shape them with automation of filter "
            "cutoff, volume, pan and reverb send, and place them with reverb, EQ and stereo width.")
GOALS = ["Design six or more layers of sound for a storm, each with its own job, from noise, pads and short samples",
         "Plan a 60 to 90 second storm arc (hush, build, peak, fade) whose bars and seconds add up",
         "Automate at least four parameters (filter cutoff, volume, pan, reverb send) so the storm moves and breathes",
         "Place every layer in the mix with reverb, EQ and stereo width, and explain each choice"]
VOCAB = [("Soundscape", "A piece of sound design that paints a place or scene from layers of texture, with no tune required"),
         ("Layer", "One sound in a stack, such as wind or ice, with its own job, range of pitch and place in the mix"),
         ("Automation", "A drawn or recorded curve that changes a control, such as volume, pan or filter cutoff, over time"),
         ("Filter cutoff", "Where a filter starts to cut: a lower cutoff makes a sound darker and muffled, a higher one opens it up"),
         ("Reverb", "The sound of a space: fast echoes that blend into a tail; more reverb makes a sound seem farther away"),
         ("Stereo width", "How far a sound spreads between the speakers; pan places it, width widens or narrows it")]
REQS = ["Choose a scene from the brief (page @BRIEF) or invent one your teacher approves, and write your scene card",
        "Build at least six layers, each with its own job; make at least two in Alchemy and use a noise-based texture in at least one",
        "Plan and build a 60 to 90 second arc with a hush, a build, a peak and a fade, and make the bars and seconds add up (page @TIMELINE)",
        "Automate at least four parameters, including filter cutoff, volume, pan and reverb send (pages @AUTO1–@AUTO2)",
        "Use reverb, Channel EQ and stereo width on your layers (page @SPACE) and keep the peak free of clipping",
        "Reflect on how the soundscape went, in writing or out loud (page @REFLECT)"]
FILE_NAME = "“Your Name – Winter Soundscape – Scene”"
STEPS = ["<b>Choose</b> — Pick a scene and write your scene card (page @BRIEF)",
         "<b>Plan the arc</b> — Decide your hush, build, peak and fade, and make the bars and seconds add up (page @TIMELINE)",
         "<b>Make the layers</b> — Build six or more layers from the sound palette (pages @PALETTE1–@PALETTE2) and the Alchemy "
         "recipes (page @ALCHEMY), and fill in your layer map (page @LAYERS)",
         "<b>Automate</b> — Plan four automation lanes (page @AUTOPLAN) and draw them in Logic (pages @AUTO1–@AUTO2)",
         "<b>Space and mix</b> — Give each layer its place with reverb, EQ, pan and width (page @SPACE), then listen for clipping at the peak",
         "<b>Bounce</b> — Check that the length is 60 to 90 seconds, bounce your soundscape and name your files like this: " + FILE_NAME,
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your soundscape. Play it, name "
         "each layer and say what each automation lane does, and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["A storm is not loud all the way through. Start quiet so the peak feels huge.",
        "Give every layer its own range of pitch: low rumble, mid wind, high ice. Layers that overlap hide each other.",
        "Add one layer at a time and listen before you add the next. Move the controls slowly: real wind rarely jumps.",
        "Save a new version of your project before each big experiment, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav handed in where your teacher says",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Scene card, layer map, timeline and automation plan handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can name every layer and what each automation lane does"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; your final grade is the average of your self-score and your teacher’s score."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Layers & Sound Design", ["Fewer than three layers, or every layer is the same sound",
                               "Three or four layers; they sound alike or have no clear job",
                               "Five layers with different jobs; Alchemy used for one of them",
                               "Six layers with clear jobs; Alchemy used for at least two",
                               "Seven or more distinct layers, each with its own job, zone and texture, all built by the student"]),
    ("Automation", ["No automation", "One parameter automated, with very few points",
                    "Three parameters automated; the changes can be heard",
                    "Four parameters (cutoff, volume, pan, reverb send) with smooth, planned curves",
                    "Five or more lanes that match the plan, with the biggest change at the peak and no clicks or jumps"]),
    ("Storm Arc & Timing", ["No clear arc, or the length is outside 60 to 90 seconds",
                            "The length is in range, but the storm barely changes",
                            "A build, a peak and a fade can be heard; the timings roughly match the plan",
                            "A clear build, peak and fade; the bars and seconds add up to the plan",
                            "A convincing arc: a gradual build, a peak that lands on its planned bar and a fade timed exactly to the plan"]),
    ("Space & Mix", ["Layers cover each other; no reverb or EQ", "Some reverb or EQ, but the mix is muddy or too loud",
                     "Reverb and EQ used; most layers can be heard; the peak does not clip",
                     "Each layer has a place: EQ, pan, width and reverb; no clipping",
                     "A clean, wide, balanced mix with depth, headroom and a bounce at a safe level"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plans; little to say about choices",
                           "Plans and reflection complete, with basic detail", "Clear plans; thoughtful reflection and good answers to questions",
                           "Insightful reflection and a polished, confident presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = [ds[4] for _, ds in RUBRIC]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.84
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches sound design as a way of making music without a melody. Students learn that texture, movement and space, not only "
                 "notes, hold a listener’s attention, and they practice building layers, drawing automation, and using reverb, EQ and stereo "
                 "width in Logic Pro.")
STRUGGLES = ["Every layer sounds like one grey blur: give each layer its own range of pitch (page @SPACE), cut the lows of every layer except "
             "the rumble with Channel EQ, and spread the layers with pan.",
             "The storm never builds because every layer plays from start to finish: use the layer map (page @LAYERS) so layers enter and "
             "leave on purpose, and compare it with the worked example (pages @EXAMPLE–@EXAMPLE2).",
             "The automation clicks or zig-zags: use fewer points and smooth curves (page @AUTO1), and move the control slowly. Wind rarely "
             "jumps from one level to another.",
             "The peak is distorted, or the reverb washes everything out: lower the faders so the loudest moment keeps headroom, and use "
             "less reverb on the layers at the peak (page @SPACE)."]
VAR_EASY = ("Offer scene A, build only six layers from the palette cards, automate only filter cutoff and volume first, and add pan and reverb "
            "send afterwards. Students can start from a Library preset in Alchemy and change only its filter and effects.")
VAR_HARD = ("Ask for a second scene change halfway, such as a storm that clears to a still, starry night, with a different set of layers "
            "in each half. Students can record their own sounds for Quick Sampler (rubbing paper, a zipper, a fingertip on a desk), "
            "automate Alchemy macro controls and plan a stereo width that grows toward the peak.")
RESOURCES = [("Scene brief and sound palette cards (pages @BRIEF–@PALETTE2)",
              "Hand out the brief first and let students choose. The eight palette cards say what each layer does, so nobody starts with a blank screen."),
             ("Alchemy, Quick Sampler and Retro Synth recipes (page @ALCHEMY)",
              "Settings are described in words, not as presets, so they work in any current Logic Pro. Students adapt them."),
             ("Automation guide, reverb, EQ and width (pages @AUTO1–@SPACE)",
              "Five curve shapes, four lanes drawn on one storm and a frequency map. Demonstrate one lane on the projector, then work time."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "An invented 60-second storm at 120 BPM, planned on paper with its bar and time table. Use it as a model, not a template.")]
TN_NOTE = ("Pairs well with a listening day: play the finished soundscapes without saying the scene and let the class decide where the "
           "storm builds, peaks and fades. A storm the class can follow without a tune is a soundscape that works.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Layers & Sound Design (rubric row 1): open the project and count the tracks. Does each layer have its own job and its own "
           "range of pitch, and were at least two built in Alchemy?",
           "Automation (rubric row 2): show the automation lanes on each track (press A) and compare them with the automation plan "
           "(page @AUTOPLAN). Listen for clicks or jumps.",
           "Storm Arc & Timing and Space & Mix (rubric rows 3 and 4): check the length is 60 to 90 seconds, that the bars and seconds on the "
           "timeline (page @TIMELINE) add up, that the peak does not clip, and that layers are not covering each other.",
           "Plan & Reflection (rubric row 5): the scene card, layer map, timeline and automation plan, the questions on the feedback planner "
           "and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Choose a scene, plan the storm arc and start the first layers.",
     "do": "Slides 1–6: the hook, what the project is, the four classes, the five steps and the storm arc. Hand out the project sheet, the "
           "scene brief, the sound palette cards and the timeline planner. Check that each student has a scene and a tempo before they leave.",
     "slides": (1, 6), "pages": ["brief", "palette1", "palette2", "timeline", "layers", "proj1", "proj2", "proj3", "vocab"],
     "deck": "A snowstorm from scratch · five steps · the storm arc"},
    {"n": 2, "owner": "Build the layers in Alchemy, Quick Sampler and Retro Synth.",
     "do": "Slides 7–8: build the layers and the frequency map. Demonstrate the wind bed from page @ALCHEMY on the projector, then work time. "
           "Walk the room with one question: what is this layer’s job, and where does it sit in pitch?",
     "slides": (7, 8), "pages": ["alchemy"], "deck": "Build the layers · a place in frequency for every layer"},
    {"n": 3, "owner": "Automate, add space, and finish the arrangement and mix.",
     "do": "Slides 9–11: automation curves, the worked example and space, width and mix. Demonstrate one automation lane, then hand out the "
           "automation plan. Ask each student to play their build and say where the peak starts.",
     "slides": (9, 11), "pages": ["auto1", "auto2", "space", "autoplan"], "deck": "Automation curves · worked example, 60 seconds · space and mix"},
    {"n": 4, "owner": "Bounce, hand in, present and reflect.",
     "do": "Slides 12–15: what to turn in, the rubric, presentation day and the close. Students bounce, name their files and write their "
           "three feedback questions, then present.",
     "slides": (12, 15), "pages": ["rubric", "present", "reflect"], "deck": "Checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:9.6pt">Make sure every student leaves with a scene, a tempo and a storm arc on the timeline planner (page @TIMELINE) '
    'whose bars add up to 60 to 90 seconds. If the sums are wrong now, the whole plan is wrong later: use seconds = bars × 240 ÷ BPM.</p></div>'
    '<div class="box"><span class="k">If you only have three classes</span><p style="margin:0;font-size:9.6pt">Combine Classes 3 and 4: '
    'build the layers and draw the automation on Class 2, then do space, mix, bouncing, presentations and reflection together in Class 3. Plan on a longer Class 3.</p></div></div>')
PACING_SIZE = 9.6

# ================================================================ the worked example: an invented 60-second storm at 120 BPM
EX_BPM = 120
EX_BAR_S = 240 / EX_BPM         # 2 s
EX_BARS = 30
EX_SECTIONS = [("Hush", 1, 4), ("Build", 5, 14), ("Peak", 15, 22), ("Fade", 23, 30)]
EX_JOBS = {"Hush": "Almost silence: a faint wind and a pad, with sparse chimes. The listener leans in.",
           "Build": "Gusts, ice and a rumble join one by one, the wind opens up and pans widen.",
           "Peak": "Everything at once: whiteout hiss and shimmer join; the filter is wide open; the pad is driest.",
           "Fade": "Layers drop out, the cutoff closes and the reverb returns until only the wind, the pad and a few quiet chimes are left."}
# layer, [(first bar, last bar), ...], how it is made
EX_LAYERS = [("Wind bed", [(1, 30)], "pink noise in Alchemy through a band-pass filter, with a slow LFO on the cutoff; the constant body of the storm"),
             ("Frozen pad", [(1, 30)], "two detuned oscillators on one low note and its fifth, slow attack, long release; no melody, just a cold tone"),
             ("Glass chimes", [(1, 4), (23, 30)], "a few high, soft plucks at random, with a long reverb; they only sound when the storm is quiet"),
             ("Gust swells", [(5, 22)], "the wind noise again, with its volume and cutoff swelling over two to four seconds, then falling"),
             ("Ice crackle", [(5, 22)], "tiny clicks from a short sample in Quick Sampler, played with random velocities and panned left and right"),
             ("Low rumble", [(9, 26)], "a sine at about 45 Hz with a little noise in Retro Synth, kept in the centre"),
             ("Whiteout hiss", [(15, 22)], "white noise through a high-pass filter at 3 kHz; the sound of the storm at its worst"),
             ("Shimmer", [(15, 22)], "the pad an octave higher with a long, bright reverb; a glassy halo around the peak")]
# the storm's overall intensity, 0 (silence) to 10 (the loudest moment): (bar, level); the last point is held to the end
EX_INTENSITY = [(1, 1), (4, 2), (9, 5), (14, 8), (15, 10), (22, 10), (26, 4), (30, 1)]
# lane: (layer, parameter, unit, lowest value, highest value, [(bar, value)])
EX_AUTO = [("Wind bed", "low-pass cutoff", "Hz", 200, 8000, [(1, 500), (5, 600), (14, 3500), (15, 4500), (22, 4500), (30, 300)]),
           ("Wind bed", "volume", "dB", -40, 0, [(1, -30), (5, -24), (14, -10), (15, -6), (22, -6), (30, -40)]),
           ("Ice crackle", "pan", "L–R", -100, 100, [(5, -50), (9, 60), (13, -70), (17, 80), (21, -80)]),
           ("Frozen pad", "reverb send", "dB", -30, 0, [(1, -4), (5, -10), (15, -18), (22, -18), (30, -3)])]
EX_MOMENTS = [(5, "first gust and the ice begin"), (9, "the rumble enters"), (15, "the peak: whiteout hiss and shimmer join"),
              (23, "the chimes return"), (27, "the rumble ends; wind and pad fade")]
EX_SCENE = ("Scene: a mountain hut at night. A snowstorm arrives over the ridge, hits the hut and passes on. The listener is inside, "
            "close to the window.")
EX_WEAK = "I will make a storm sound with some wind and some bells."
EX_STRONG = ("My scene is a mountain hut at night. My soundscape is 60 seconds at 120 BPM, so 30 bars of 2 seconds each. It has four "
             "sections: a hush of 4 bars, a build of 10 bars, a peak of 8 bars and a fade of 8 bars. I use eight layers: wind bed, frozen "
             "pad, glass chimes, gust swells, ice crackle, low rumble, whiteout hiss and shimmer. I automate four lanes: the wind’s "
             "cutoff and volume, the ice’s pan and the pad’s reverb send.")
EX_QUESTIONS = ["Where did the storm start to build, and what told you?",
                "Which layer did you notice first, and which did you notice last?",
                "How did the storm end: did it stop, or did it fade?"]
EX_NOTE = "Invented, on paper: no audio is included, and a student’s numbers will differ."


def mmss(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


def bar_time(bar):
    return (bar - 1) * EX_BAR_S


def ex_density(bar):
    return sum(1 for _n, spans, _d in EX_LAYERS if any(a <= bar <= b for a, b in spans))


EX_DENS = [ex_density(b) for b in range(1, EX_BARS + 1)]


def length_s(bars, bpm):
    return bars * 240 / bpm


LEN_BARS = (20, 24, 30, 36, 40)
LEN_BPMS = (80, 90, 100, 110, 120)
LEN_EXPECT = [60.0, 72.0, 90.0, 108.0, 120.0, 53.3, 64.0, 80.0, 96.0, 106.7, 48.0, 57.6, 72.0, 86.4, 96.0,
              43.6, 52.4, 65.5, 78.5, 87.3, 40.0, 48.0, 60.0, 72.0, 80.0]

# the frequency map: layer, lowest and highest Hz it needs, and the Channel EQ high-pass setting (Hz) to use on it
FREQ = [("Low rumble", 30, 120, 25), ("Frozen pad", 120, 3000, 100), ("Wind bed", 200, 4000, 120), ("Gust swells", 300, 3000, 120),
        ("Glass chimes", 1000, 8000, 600), ("Shimmer", 2000, 12000, 1500), ("Ice crackle", 3000, 12000, 2000), ("Whiteout hiss", 4000, 16000, 3000)]

# the five automation curve shapes: name, what it is for, [(x 0..1, y 0..1)]
CURVES = [("Ramp", "a build: the cutoff opens", [(0, .08), (1, .92)]),
          ("Swell", "a gust: up, then back down", [(0, .1), (.5, .92), (1, .1)]),
          ("Step", "a hold, then a jump", [(0, .2), (.45, .2), (.5, .85), (1, .85)]),
          ("Wave", "wind that breathes", [(0, .5), (.125, .9), (.375, .1), (.625, .9), (.875, .1), (1, .5)]),
          ("Fade", "an ending: the level falls", [(0, .92), (1, .06)])]

# ---- the palette cards: layer, job, how to make it (in words), zone, one automation idea
PALETTE = [
    ("Wind bed", "The constant body of the storm and the glue of the mix.",
     "Alchemy with a noise source (pink or white noise). Low-pass or band-pass filter with the cutoff near 800 Hz and little resonance. "
     "A slow LFO on the cutoff, about one cycle every 6 to 10 seconds, so the wind breathes.",
     "200 Hz–4 kHz", "Open the cutoff from the hush to the peak; close it again in the fade."),
    ("Gust swells", "Gusts that come and go, so the wind is never flat.",
     "The same noise as the wind bed on its own track, or one more Alchemy source. Draw volume and cutoff swells of 2 to 4 seconds, "
     "each followed by a fall. A longer, softer attack makes a gust sound like it arrives from far away.",
     "300 Hz–3 kHz", "Draw a Swell curve (page @AUTO1) every few bars; make the gusts bigger toward the peak."),
    ("Low rumble", "Weight under the storm; you feel it more than you hear it.",
     "Retro Synth or Alchemy: a sine or the sub oscillator on one low note (about 45 Hz) with a trace of noise and a low-pass filter. "
     "A slow volume wobble helps. Keep it in the centre of the stereo picture.",
     "30–120 Hz", "Bring it in at the middle of the build; take it out in the fade."),
    ("Frozen pad", "A cold, held tone that gives the storm a pitch to sit on. It is a drone, not a tune.",
     "Alchemy, two or three oscillators slightly detuned, on one low note and its fifth. Attack 3 s or more, release 6 s or more, "
     "a gentle low-pass filter. A slow chorus or Step FX filter movement keeps it alive.",
     "120 Hz–3 kHz", "Automate reverb send: wetter in the hush and fade, drier at the peak."),
    ("Ice crackle", "Tiny, bright, irregular ticks, like frozen branches and blown snow on a window.",
     "Quick Sampler with a very short sound (a click or a fingernail on a desk, recorded yourself) played with short notes of "
     "different velocities. Raise the pitch, shorten the end, add a high-pass filter. Alchemy’s granular source is another route.",
     "3–12 kHz", "Automate pan so the ticks sweep from left to right."),
    ("Whiteout hiss", "A wall of bright noise that only appears when the storm is at its worst.",
     "White noise in Alchemy or Retro Synth through a high-pass filter near 3 kHz. A long attack so it swells in rather than starting.",
     "4–16 kHz", "Bring it in at the start of the peak, swelling up over its first bar; remove it all at once at the start of the fade."),
    ("Glass chimes", "A few soft, high sounds that show how quiet the hush is.",
     "A bell or pluck sound in Alchemy, played by hand in a handful of random notes from one scale, short and soft, "
     "with a long reverb. Leave them out at the peak. They are not a melody: no tune, no pattern.",
     "1–8 kHz", "Send more to the reverb in the hush and the fade."),
    ("Shimmer", "A glassy halo that makes the peak feel wide and open.",
     "The pad, or a copy of it, an octave higher, with a long, bright reverb and the high-pass filter at about 1.5 kHz. "
     "Play it only through the peak.",
     "2–12 kHz", "Raise reverb send and volume together as the peak begins; lower both in the fade."),
]

# ---- the recipes: instrument, title, [(label, text)] (settings in words; menu paths are avoided where unsure)
RECIPES = [
    ("Alchemy", "The wind bed",
     [("Source", "Choose a noise sound: a noise waveform from one of Alchemy’s sources, or a Library wind or noise preset to start from."),
      ("Filter", "Low-pass or band-pass. Cutoff low (around 800 Hz), resonance low, so it sounds like air and not a whistle."),
      ("Motion", "Add an LFO and route it to the cutoff, very slow (one cycle every 6 to 10 seconds) and shallow, so the wind breathes."),
      ("Effects", "A little reverb and a gentle high-pass. Leave the volume low; the peak is made by automation, not by turning it up first.")]),
    ("Alchemy", "The frozen pad",
     [("Source", "Two sources of a simple, soft wave, detuned a few cents apart for a slow, cold beating."),
      ("Envelope", "Attack 3 seconds or more, a long release (6 seconds or more), so notes swell in and melt away."),
      ("Filter", "A low-pass filter with a gentle slope and the cutoff around 2 kHz, to take the edge off."),
      ("Play", "Hold one low note and its fifth for the whole piece. No melody, and no change of note, is needed.")]),
    ("Quick Sampler", "The ice crackle",
     [("Sound", "Record a very short sound yourself (a fingernail on a desk, a pen click, crumpled paper). "
                "Nothing is supplied with this kit."),
      ("Shape", "Shorten the end of the sample, raise the pitch, and add a high-pass filter so only the highest part remains."),
      ("Play", "Play short, soft notes with different velocities and gaps, or draw them with the mouse. Irregular is better than steady."),
      ("Space", "Pan the track and send it to a reverb. Automate the pan over the build (page @AUTO2).")]),
    ("Retro Synth", "The low rumble",
     [("Source", "A sine wave, or the sub oscillator if your version has one, with a trace of noise."),
      ("Pitch", "One note around 45 Hz. Keep it mono."),
      ("Filter", "Low-pass with the cutoff low; a slow tremolo or volume wobble is enough movement."),
      ("Mix", "Keep it in the centre, and do not boost it: it takes up a great deal of room. Check it on small speakers too.")]),
]


# ================================================================ drawings (waveforms, snowflakes, automation curves; no notation)
def snowflake(cx, cy, r, sw=7, col="#000", tip=None):
    """A six-armed snowflake: each arm has a stem and two pairs of side branches, all drawn as lines."""
    tip = tip or ACCENT
    out = []
    for k in range(6):
        a = math.radians(90 + 60 * k)
        ux, uy = math.cos(a), -math.sin(a)
        ex, ey = cx + r * ux, cy + r * uy
        out.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>')
        for frac, ln in ((0.55, 0.30), (0.8, 0.2)):
            bx, by = cx + r * frac * ux, cy + r * frac * uy
            for sgn in (-1, 1):
                b = a + sgn * math.radians(55)
                out.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx + r * ln * math.cos(b):.1f}" y2="{by - r * ln * math.sin(b):.1f}" '
                           f'stroke="{col}" stroke-width="{sw * .8:.1f}" stroke-linecap="round"/>')
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{sw * 1.15:.1f}" fill="{tip}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{sw * 1.5:.1f}" fill="{tip}"/>')
    return "".join(out)


def noise01(i):
    """A fixed pseudo-random value 0..1 for bar i (no random module: the artwork is the same on every build)."""
    v = math.sin(i * 12.9898 + 78.233) * 43758.5453
    return v - math.floor(v)


def env_at(u):
    """The storm's loudness 0..1 at position u (0..1) along a drawing: hush, build, peak, fade."""
    if u < .12:
        return .10 + .1 * u / .12
    if u < .42:
        return .2 + .8 * ((u - .12) / .30) ** 1.5
    if u < .66:
        return 1.0
    return max(.06, 1.0 - .94 * ((u - .66) / .34) ** 1.2)


def hero_body():
    W = 1100
    out = [snowflake(W / 2, 150, 125, 8)]
    n = 120
    y0, hh = 450, 120
    bw = (W - 100) / n
    for i in range(n):
        u = i / (n - 1)
        a = env_at(u) * (.55 + .45 * noise01(i))
        h = max(6, a * hh)
        col = ACCENT if .42 <= u < .66 else "#000"
        out.append(f'<rect x="{50 + i * bw + 1:.1f}" y="{y0 - h:.1f}" width="{max(2, bw - 2):.1f}" height="{2 * h:.1f}" rx="2" fill="{col}"/>')
    out.append(f'<line x1="50" y1="{y0}" x2="{W - 50}" y2="{y0}" stroke="#000" stroke-width="2"/>')
    ty = y0 + hh + 34
    for nm, a, b in (("HUSH", .0, .12), ("BUILD", .12, .42), ("PEAK", .42, .66), ("FADE", .66, 1.0)):
        x0, x1 = 50 + a * (W - 100), 50 + b * (W - 100)
        out.append(f'<line x1="{x0 + 10:.1f}" y1="{ty - 22}" x2="{x1 - 10:.1f}" y2="{ty - 22}" stroke="{ACCENT if nm == "PEAK" else "#000"}" stroke-width="5" stroke-linecap="round"/>')
        out.append(D.t_((x0 + x1) / 2, ty + 20, nm, 36, 700, fill_=ACCENT if nm == "PEAK" else "#000"))
        D.lab("hero", nm, 36, x1 - x0 - 16)
    return "".join(out), W, ty + 34


def cards_body(items, cap, W=1600, name="cards", fs=30, cs=22):
    n = len(items)
    gap = 74
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
        if k < n - 1:
            ax, ay = x0 + pw + 10, 4 + bh / 2
            out.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{ax + gap - 36:.1f}" y2="{ay:.1f}" stroke="#000" stroke-width="6" stroke-linecap="round"/>')
            out.append(f'<polygon points="{ax + gap - 16:.1f},{ay:.1f} {ax + gap - 40:.1f},{ay - 15:.1f} {ax + gap - 40:.1f},{ay + 15:.1f}" fill="#000"/>')
    out.append(D.t_(W / 2, bh + 56, cap, cs + 2, 500))
    D.lab(name + " cap", cap, cs + 2, W - 20)
    return "".join(out), W, bh + 72


def cycle_body(W=1600, name="cycle pic", fs=30, cs=22):
    return cards_body([("Scene", "brief + sounds"), ("Arc", "build · peak · fade"), ("Layers", "wind, ice, pads"),
                       ("Automate", "cutoff, volume, pan"), ("Space", "reverb · EQ · width")],
                      "Then mix, bounce, present and reflect", W, name, fs, cs)


def X_of(bar, gx, pw, nbars):
    return gx + pw * (bar - 1) / nbars


def arc_body(W=1600, name="arc pic", fs=26, ts=20):
    """The worked example's storm arc: sections with their bars and seconds, the intensity curve, and a time ruler."""
    gx, pw = 120, W - 120 - 16
    X = lambda bar: X_of(bar, gx, pw, EX_BARS)
    shade = {"Hush": "#4a4a4a", "Build": "#000", "Peak": ACCENT, "Fade": "#4a4a4a"}
    out = []
    sh = 52
    for nm, a, b in EX_SECTIONS:
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b + 1) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{shade[nm]}"/>')
        out.append(D.t_((X(a) + X(b + 1)) / 2, sh / 2 + fs * .3 + 2, nm.upper(), fs - 2, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 2, X(b + 1) - X(a) - 10)
        sub = f"bars {a}–{b} · {(b - a + 1) * EX_BAR_S:g} s"
        out.append(D.t_((X(a) + X(b + 1)) / 2, sh + ts + 6, sub, ts - 2, 500))
        D.lab(name + " subs", sub, ts - 2, X(b + 1) - X(a) - 8)
    top, ch = sh + ts + 26, 250
    for lv, lbl in ((10, "PEAK"), (5, "MID"), (0, "QUIET")):
        y = top + ch - lv / 10 * ch
        out.append(f'<line x1="{gx}" y1="{y:.1f}" x2="{gx + pw:.1f}" y2="{y:.1f}" stroke="{"#000" if lv == 0 else "#bdbdbd"}" stroke-width="{2 if lv == 0 else 1}"/>')
        out.append(D.t_(gx - 12, y + 7, lbl, 20, 700, anchor="end"))
        D.lab(name + " levels", lbl, 20, gx - 20)
    pts = [(X(b), top + ch - v / 10 * ch) for b, v in EX_INTENSITY] + [(X(EX_BARS + 1), top + ch - EX_INTENSITY[-1][1] / 10 * ch)]
    poly = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    out.append(f'<polygon points="{gx:.1f},{top + ch} {poly} {X(EX_BARS + 1):.1f},{top + ch}" fill="{ACC_LIGHT}" opacity=".9"/>')
    out.append(f'<polyline points="{poly}" fill="none" stroke="{ACCENT}" stroke-width="6" stroke-linejoin="round"/>')
    for a, b in pts[:-1]:
        out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="7" fill="#000"/>')
    for nm, a, b in EX_SECTIONS[1:]:
        out.append(f'<line x1="{X(a):.1f}" y1="{top}" x2="{X(a):.1f}" y2="{top + ch}" stroke="#000" stroke-width="2" stroke-dasharray="6 6"/>')
    ty = top + ch + 6
    for bar in (1, 6, 11, 16, 21, 26, 31):
        lbl = mmss(bar_time(bar))
        anc = "start" if bar == 1 else ("end" if bar == 31 else "middle")
        out.append(f'<line x1="{X(bar):.1f}" y1="{ty}" x2="{X(bar):.1f}" y2="{ty + 12}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(bar), ty + 12 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 70)
    cap = f"{EX_BARS} bars × {EX_BAR_S:g} seconds = {EX_BARS * EX_BAR_S:g} seconds at {EX_BPM} BPM"
    out.append(D.t_(gx + pw / 2, ty + 12 + ts + 34, cap, ts + 2, 500))
    D.lab(name + " cap", cap, ts + 2, pw)
    return "".join(out), W, ty + 12 + ts + 48


def map_body(W=1600, name="map", fs=24, ts=20):
    """The worked example's whole 30-bar arrangement: sections, eight layers and four automation lanes with their values."""
    gx = 300
    pwid = W - gx - 16
    X = lambda bar: X_of(bar, gx, pwid, EX_BARS)
    shade = {"Hush": "#4a4a4a", "Build": "#000", "Peak": ACCENT, "Fade": "#4a4a4a"}
    out = []
    sh = 54
    for nm, a, b in EX_SECTIONS:
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b + 1) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{shade[nm]}"/>')
        out.append(D.t_((X(a) + X(b + 1)) / 2, sh / 2 + fs * .3 + 2, nm.upper(), fs - 4, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 4, X(b + 1) - X(a) - 10)
    lh, lg = 28, 6
    y0 = sh + 14
    out.append(D.t_(gx - 14, y0 + 6, "LAYERS", fs - 6, 700, anchor="end", fill_=ACCENT))
    for i, (nm, spans, _d) in enumerate(EX_LAYERS):
        yy = y0 + 16 + i * (lh + lg)
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, nm.upper(), 20, 700, anchor="end"))
        D.lab(name + " lanes", nm.upper(), 20, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        for a, b in spans:
            out.append(f'<rect x="{X(a):.1f}" y="{yy + 4}" width="{X(b + 1) - X(a):.1f}" height="{lh - 8}" rx="6" fill="#bdbdbd" stroke="#000" stroke-width="2"/>')
    ay0 = y0 + 16 + len(EX_LAYERS) * (lh + lg) + 8
    out.append(D.t_(gx - 14, ay0 + 6, "AUTOMATION", fs - 6, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " lanes", "AUTOMATION", fs - 6, gx - 24)
    for i, (ly, par, _u, lo, hi, pts) in enumerate(EX_AUTO):
        yy = ay0 + 16 + i * (lh + lg + 6)
        lbl = f"{ly} · {par}".upper()
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, lbl, 18, 700, anchor="end"))
        D.lab(name + " lanes", lbl, 18, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh + 6}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        xy = [(X(t), yy + lh + 2 - (v - lo) / (hi - lo) * (lh - 2)) for t, v in pts]
        out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in xy)}" fill="none" stroke="{ACCENT}" stroke-width="4" stroke-linejoin="round"/>')
        for a, b in xy:
            out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="4.5" fill="#000"/>')
    ty = ay0 + 16 + len(EX_AUTO) * (lh + lg + 6) + 4
    for bar in (1, 6, 11, 16, 21, 26, 31):
        lbl = mmss(bar_time(bar))
        anc = "start" if bar == 1 else ("end" if bar == 31 else "middle")
        out.append(f'<line x1="{X(bar):.1f}" y1="{ty - 6}" x2="{X(bar):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(bar) + (2 if bar == 1 else (-2 if bar == 31 else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 70)
    cap = f"Bar 1 to bar 30 at {EX_BPM} BPM: {EX_BARS} bars × {EX_BAR_S:g} seconds = {EX_BARS * EX_BAR_S:g} seconds"
    out.append(D.t_(gx + pwid / 2, ty + 8 + ts + 34, cap, ts + 2, 500))
    D.lab(name + " cap", cap, ts + 2, pwid)
    return "".join(out), W, ty + 8 + ts + 48


def curves_body(W=1600, name="curves pic", fs=26, cs=19):
    """The five automation curve shapes, each a small lane with its points (computed from CURVES)."""
    n = len(CURVES)
    gap = 26
    pw = (W - (n - 1) * gap) / n
    lh = 150
    out = []
    for k, (nm, use, pts) in enumerate(CURVES):
        x0 = k * (pw + gap)
        out.append(f'<rect x="{x0:.1f}" y="0" width="{pw:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="2"/>')
        for q in (.25, .5, .75):
            out.append(f'<line x1="{x0:.1f}" y1="{lh * q:.1f}" x2="{x0 + pw:.1f}" y2="{lh * q:.1f}" stroke="#d6d6d6" stroke-width="1"/>')
        xy = [(x0 + 14 + u * (pw - 28), lh - 14 - v * (lh - 28)) for u, v in pts]
        out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in xy)}" fill="none" stroke="{ACCENT}" stroke-width="6" stroke-linejoin="round"/>')
        for a, b in xy:
            out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="7" fill="#000"/>')
        out.append(D.t_(x0 + pw / 2, lh + 36, nm.upper(), fs, 700, fill_=ACCENT))
        D.lab(name + " names", nm.upper(), fs, pw - 10)
        out.append(D.t_(x0 + pw / 2, lh + 36 + cs + 8, use, cs, 500))
        D.lab(name + " uses", use, cs, pw - 8)
    cap = "Time runs left to right; higher means more (louder, brighter, wider)"
    out.append(D.t_(W / 2, lh + 36 + cs + 8 + 38, cap, cs + 3, 500))
    D.lab(name + " cap", cap, cs + 3, W - 20)
    return "".join(out), W, lh + 36 + cs + 8 + 54


def freq_x(f, gx, pw):
    return gx + pw * (math.log10(f) - math.log10(20)) / 3.0


def freq_body(W=1600, name="freq pic", fs=22, ts=19):
    """The frequency map: each layer's range on a log axis from 20 Hz to 20 kHz, with the Channel EQ high-pass marked."""
    gx = 260
    pw = W - gx - 24
    rh = 40
    out = []
    top = 8
    rows = sorted(FREQ, key=lambda r: r[1])
    for f, lbl in ((20, "20"), (100, "100"), (1000, "1k"), (10000, "10k"), (20000, "20k")):
        x = freq_x(f, gx, pw)
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + rows.__len__() * rh}" stroke="#bdbdbd" stroke-width="1.5"/>')
        anc = "start" if f == 20 else ("end" if f == 20000 else "middle")
        out.append(D.t_(x, top + len(rows) * rh + 28, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 60)
    for i, (nm, lo, hi, hp) in enumerate(rows):
        y = top + i * rh
        out.append(D.t_(gx - 14, y + rh / 2 + 7, nm.upper(), fs, 700, anchor="end"))
        D.lab(name + " names", nm.upper(), fs, gx - 24)
        x0, x1 = freq_x(lo, gx, pw), freq_x(hi, gx, pw)
        out.append(f'<rect x="{x0:.1f}" y="{y + 7}" width="{x1 - x0:.1f}" height="{rh - 14}" rx="9" fill="{ACCENT if i % 2 else "#000"}"/>')
        xh = freq_x(hp, gx, pw)
        out.append(f'<line x1="{xh:.1f}" y1="{y + 3}" x2="{xh:.1f}" y2="{y + rh - 3}" stroke="#000" stroke-width="4"/>')
        out.append(f'<polygon points="{xh:.1f},{y + rh - 3} {xh - 7:.1f},{y + rh - 14} {xh + 7:.1f},{y + rh - 14}" fill="#000"/>')
    cap = "Each bar is the range a layer needs; the colours only tell the rows apart."
    cap3 = "The black arrow marks the Channel EQ high-pass: everything below it is cut."
    ey = top + len(rows) * rh + 28 + ts + 14
    out.append(D.t_(gx + pw / 2, ey, "Frequency in Hz, a log scale: each step to the right is ten times higher", ts, 500))
    D.lab(name + " cap", "Frequency in Hz, a log scale: each step to the right is ten times higher", ts, pw)
    out.append(D.t_(gx + pw / 2, ey + ts + 12, cap, ts, 500))
    D.lab(name + " cap2", cap, ts, pw)
    out.append(D.t_(gx + pw / 2, ey + 2 * (ts + 12), cap3, ts, 500))
    D.lab(name + " cap3", cap3, ts, pw)
    ey += ts + 12
    return "".join(out), W, ey + ts + 24


def lane_blank(W=1100, nb=48, step=4, name="lane blank", h=96, first=True):
    """A blank automation lane for students: bar ruler every `step` bars, quarter lines, a box to draw in."""
    gx, pw = 30, W - 46
    out = [f'<rect x="{gx}" y="22" width="{pw}" height="{h}" fill="#fff" stroke="#000" stroke-width="2"/>']
    for q in (.25, .5, .75):
        out.append(f'<line x1="{gx}" y1="{22 + h * q:.1f}" x2="{gx + pw}" y2="{22 + h * q:.1f}" stroke="#d6d6d6" stroke-width="1.2"/>')
    for b in range(1, nb + 2, step):
        x = gx + pw * (b - 1) / nb
        out.append(f'<line x1="{x:.1f}" y1="22" x2="{x:.1f}" y2="{22 + h}" stroke="{"#000" if (b - 1) % (step * 2) == 0 else "#9a9a9a"}" stroke-width="{2.2 if (b - 1) % (step * 2) == 0 else 1}"/>')
        if b <= nb and first:
            out.append(D.t_(x + 4, 16, str(b), 15, 500, anchor="start"))
            D.lab(name + " bars", str(b), 15, 30)
    return "".join(out), W, 22 + h + 4


def arc_blank(W=1100, name="arc blank"):
    """Blank axes for the student's storm arc: quiet to peak, 0 to 90 seconds."""
    gx, pw, top, ch = 90, W - 90 - 16, 8, 190
    out = [f'<rect x="{gx}" y="{top}" width="{pw}" height="{ch}" fill="#fff" stroke="#000" stroke-width="2"/>']
    for q in (.25, .5, .75):
        out.append(f'<line x1="{gx}" y1="{top + ch * q:.1f}" x2="{gx + pw}" y2="{top + ch * q:.1f}" stroke="#d6d6d6" stroke-width="1.2"/>')
    for s in range(0, 91, 15):
        x = gx + pw * s / 90
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + ch}" stroke="{"#000" if s in (0, 60, 90) else "#9a9a9a"}" stroke-width="{2 if s in (0, 60, 90) else 1}"/>')
        lbl = mmss(s)
        out.append(D.t_(x, top + ch + 24, lbl, 18, 500, anchor="start" if s == 0 else ("end" if s == 90 else "middle")))
        D.lab(name + " ticks", lbl, 18, 60)
    for yy, lbl in ((top + 18, "PEAK"), (top + ch - 4, "QUIET")):
        out.append(D.t_(gx - 10, yy, lbl, 17, 700, anchor="end"))
        D.lab(name + " levels", lbl, 17, gx - 14)
    out.append(D.t_(gx + pw / 2, top + ch + 52, "Draw your storm’s intensity: shade 60 to 90 seconds only", 18, 500))
    D.lab(name + " cap", "Draw your storm’s intensity: shade 60 to 90 seconds only", 18, pw)
    return "".join(out), W, top + ch + 62


DRAWINGS = {"hero": hero_body, "cycle": lambda: cycle_body(1600), "arc": lambda: arc_body(1600, "arc deck"),
            "curves": lambda: curves_body(1600, "curves deck"), "freq": lambda: freq_body(1600, "freq deck", 27, 25),
            "map": lambda: map_body(1600, "map pic")}
DRAWING_PX = {"hero": 1900, "cycle": 2000, "arc": 2000, "curves": 2000, "freq": 2000, "map": 2000}
SIDE = {"cycle": ["Choose a scene and a tempo", "Plan the storm arc on paper", "Build layers, then automate", "Space and mix last"],
        "arc": ["Four sections: hush, build, peak, fade", "The peak is the only loudest part", "Bars × 2 seconds at 120 BPM", "30 bars = 60 seconds"],
        "curves": ["Ramp: a build", "Swell: a gust", "Step: a sudden change", "Wave and Fade: breath and ending"],
        "freq": ["Low layers sit at the left", "High layers sit at the right", "High-pass every layer; the rumble gets a very low one", "Layers that overlap hide each other"],
        "map": ["An invented 60-second storm", "Four sections: 4, 10, 8, 8 bars", "Eight layers, four automation lanes", "The peak has the most layers"]}


def label_extras():
    arc_body(1250, "page arc", 24, 20)
    map_body(1250, "page map", 24, 20)
    curves_body(1100, "page curves", 22, 16)
    freq_body(1100, "page freq", 20, 17)
    cycle_body(1250, "page cycle", 28, 20)
    lane_blank(1100, 48, 4, "lane page")
    arc_blank(1100)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Winter Soundscape", "A snowstorm from scratch.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you are going to design a snowstorm from nothing, "
     "in Logic Pro, with no melody at all. Students will build wind, ice and pads, draw how they change over time, and place them in a "
     "space. Hand out the project sheet and the scene brief at the end of this class."),
    (1, "listen", "Think: what does a storm do over time?", "Think, then share · Teacher: describe a storm out loud|First a hush, then wind "
     "in the trees, then a roar, then it thins out.|What changes as it gets closer?|Which sounds would you stack?|What would you leave out?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker: you describe a storm yourself, first a hush, "
     "then the wind finding the trees, then a roar, then it thinning out. Students will say louder, brighter, wider and more layers. Write "
     "their words on the board; the project turns each one into a tool."),
    (1, "bullets", "What is Winter Soundscape?", "Design a 60 to 90 second snowstorm|Build it from layers: wind, ice, pads, noise|Shape it "
     "with automation and space|No melody needed, no audio supplied",
     "The project in four lines. Students choose a scene from the brief, build six or more layers, draw automation so the storm builds, peaks "
     "and fades, and place it with reverb, EQ and stereo width. The finished soundscape is 60 to 90 seconds. There is no melody and no audio "
     "in this kit; every sound is made by the students in Logic Pro."),
    (1, "days", "Four classes", "",
     "The shape of the project. Class 1: hook, choose a scene, plan the arc and start the first layers. Class 2: build the layers in Alchemy, "
     "Quick Sampler and Retro Synth. Class 3: automate, then add space and mix. Class 4: bounce, hand in, present and reflect. Hand out the "
     "project sheet, the scene brief and the timeline planner now."),
    (1, "pic", "Five steps, then finish", "cycle",
     "Class 1. The five steps in order: scene, arc, layers, automate and space. After that students mix, bounce, present and reflect. Point to "
     "each box and say roughly when it happens: the scene and arc today, the layers on Class 2, automation and space on Class 3. The picture "
     "and its short labels are drawn for this kit."),
    (1, "pic", "The storm arc", "arc",
     f"Class 1. This is the worked example's arc: a hush of 4 bars, a build of 10, a peak of 8 and a fade of 8, 30 bars in all. At 120 BPM a "
     f"bar lasts 2 seconds, so the soundscape is 60 seconds. The line is how loud and full the storm feels. Notice the peak is the only "
     f"loudest part: a storm that is always loud has no peak. Students draw their own on page {pg('timeline')}."),
    (2, "steps", "Build the layers", "Choose a layer from the palette cards|Make it in Alchemy, Quick Sampler or Retro Synth|Give it one "
     "job and one range of pitch|Name the track and fill in the layer map|Add the next layer only after you listen",
     f"Class 2. Demonstrate on the projector: make a Software Instrument track, choose Alchemy, pick a noise sound, set a low-pass filter with a "
     f"low cutoff and add a slow LFO on the cutoff. That is the wind bed from page {pg('alchemy')}. Then show one short sample in Quick Sampler. "
     f"Menu names move between Logic versions, so describe the action, not the path."),
    (2, "pic", "A place in frequency", "freq",
     f"Class 2. Each bar is the range of pitch a layer needs, on a scale where every step to the right is ten times higher. The black tick is "
     f"where Channel EQ's high-pass filter goes. Only the rumble needs the lowest notes; every other layer is cut below its tick, which "
     f"keeps the mix clear. Students check their own layers against it on page {pg('space')}."),
    (3, "pic", "Automation: draw the change", "curves",
     f"Class 3. Five shapes cover almost everything: a ramp for a build, a swell for a gust, a step for a sudden change, a wave for wind that "
     f"breathes and a fade for an ending. Show one lane on the projector: press A, pick Volume or a filter cutoff in the track's automation "
     f"menu, click the line to add points and drag them. See page {pg('auto1')}. Fewer points make smoother curves."),
    (3, "pic", "Worked example: 60 seconds", "map",
     "Class 3. An invented soundscape described on paper, nothing here is audio: a mountain hut in a storm at 120 BPM. Thirty bars at 2 seconds "
     "a bar is 60 seconds, in four sections of 4, 10, 8 and 8 bars. Eight layers join and leave, and the peak has the most. Four automation "
     "lanes keep the sound moving. Students plan their own on the layer map and the automation plan."),
    (3, "bullets", "Space, width and mix", "Reverb: wetter when calm, drier at the peak|EQ: high-pass every layer, the rumble very low|Pan the "
     "ice, keep the rumble in the centre|Check it quietly, then at normal level",
     f"Class 3. Space in four ideas. Reverb makes a sound seem far away: use more in the hush and fade and less at the peak. Channel EQ's "
     f"high-pass filter clears the lows. Pan the ice and widen the pad, but keep the rumble in the centre so it stays strong on any speaker. "
     f"Check the mix quietly first, then at a normal level; the page is {pg('space')}."),
    (4, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Winter Soundscape – Scene|Scene card, "
     "layer map, timeline, automation plan|Rubric self-score|Three questions for classmates",
     "Class 4. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, Winter "
     "Soundscape, then the scene, in that order. Check that every soundscape is between 60 and 90 seconds before students bounce."),
    (4, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and yours. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (4, "bullets", "Presentation day", "Play your soundscape, then name each layer|Say what each automation lane does|Your three questions "
     "for classmates|Answer at least 2 of each classmate’s questions",
     "Class 4, presentations. Each student plays their soundscape, names the layers they built and says what each automation lane does, then "
     "takes questions. Students write three questions they want classmates to answer, and answer at least two of each classmate's. "
     "Ask the class where the build starts and where the peak is before the presenter says."),
    (4, "closer", "One last thing…", "You built the wind.|You drew the change.|You shaped the space.|Now press play.",
     "Close with the listening day: play the finished soundscapes without saying the scene and let the class say where each storm builds, "
     "peaks and fades. Ask a few students which automation lane changed the mood most. No audio is included in this kit; the sounds are "
     "the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "4 class periods, slide by slide"), ("palette1", "Sound palette", "what each layer does"),
          ("auto2", "Automation guide", "four lanes on one storm")]
SHOTS2 = [1, 6, 8, 9, 10, 13]
SHOTS3 = [("brief", "Scene brief"), ("alchemy", "Alchemy recipes"), ("auto1", "Automation"), ("space", "Reverb, EQ, width"),
          ("timeline", "Storm arc planner"), ("layers", "Layer map"), ("example", "Worked example"), ("rubric", "Rubric / 25")]
PREVIEW_PICKS = ["pacing", "palette1", "auto2", "rubric"]

COVER_A = "Design a snowstorm from scratch"
COVER_C = "Logic Pro · Alchemy · automation · intro slides"
PDF_COVER = dict(a=26, b=58, c=14, art=7.3)
SQ_COVER = dict(a=40, b=150, c=27, art=740, gap=40)
SQ_B_LINES = ["Winter", "Soundscape"]
SQ_SUB = "4 class periods · no melody needed · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, palette cards, automation and a /25 rubric", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Scene brief, recipes, automation, layer map, arc planner, worked example", 28)}
SQ_BANDS = {1: "Layers <em>·</em> automation <em>·</em> reverb <em>·</em> EQ <em>·</em> width",
            2: "Storm arc <em>·</em> frequency map <em>·</em> automation curves <em>·</em> worked example",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, recordings, loops, lyrics, artists or albums are named or included, and there is no melody to chart. Students make every "
             "sound in their soundscapes themselves, from the instruments, samplers and plug-ins in Logic Pro.")
CREDITS = ["The scene brief, sound palette cards, Alchemy and sampler recipes, automation guide, frequency map, storm-arc timeline, layer map, "
           "worked example, the hero, card, curve, arc and map drawings and all layouts: original work, Hudson Beat. No recordings, loops, "
           "presets or published material are included.",
           "No audio, video, album art, screenshots, presets, templates, links or chart data are included. No student work is included."]
LOGIC_INTRO = ("Where to find the tools a Winter Soundscape is likely to use. Demonstrate what your class needs on Classes 1 to 3 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add a Software Instrument track with Track › New Tracks… for each layer you play or draw. "
              "Name every track so your layer map matches."),
             ("Tempo as a ruler", "Type the tempo in the control bar (60 to 120 BPM) and keep 4/4. A soundscape has no beat, but the tempo turns bars "
              "into seconds: seconds = bars × 240 ÷ BPM (page " + str(pg("timeline")) + "). The playhead position in the control bar can also be shown as time."),
             ("Alchemy", "Click the instrument slot on a channel strip and choose Alchemy. Browse the Library (Y) for noise, wind or pad sounds as a "
              "starting point, then change the source, the filter and the effects (recipes on page " + str(pg("alchemy")) + ")."),
             ("Quick Sampler", "Choose Quick Sampler as the instrument and record a short sound yourself, or use a short sound you recorded. "
              "Shorten it, raise its pitch, add its filter and play it from the keyboard or draw notes in the Piano Roll."),
             ("Retro Synth and Step FX", "Retro Synth makes simple low tones (a sine for the rumble). The Step FX plug-in, if your version has it, "
              "can make a pad stutter or sweep its filter in steps. If you are unsure, skip it."),
             ("Auto Filter", "Insert Auto Filter on a track. Choose a low-pass filter and set the cutoff and resonance; its LFO moves the cutoff in time. "
              "The same cutoff can also be automated (next row)."),
             ("Automation", "Press A to show automation. In the track header, pick a parameter such as Volume, Pan or a plug-in control, click the line to "
              "add a point and drag it. Or choose Touch, Latch or Write, play, and move the control by hand; Read plays it back."),
             ("Reverb: ChromaVerb and Space Designer", "Insert ChromaVerb or Space Designer on a track, or on an aux channel strip that several tracks "
              "send to (the Send knob). Set the size and decay to taste and put more on layers that should sound far away."),
             ("Channel EQ", "Insert Channel EQ. Turn on the lowest band as a high-pass filter and set its frequency (page " + str(pg("space")) + "); lower or raise a "
              "band to cut mud or add air."),
             ("Pan and stereo width", "Each channel strip has a Pan knob (and can automate it). The Stereo Spread plug-in, if your version has it, "
              "widens a sound; keep very low sounds in the centre."),
             ("Mix and bounce", "Press X for the Mixer and keep the loudest moment below the red clipping mark. Then File › Bounce › Project or Section "
              "(Command-B), MP3 or WAV. In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my soundscape:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:11.4pt;margin-bottom:3pt">A grey blur: the palette cards (pages @PALETTE1–@PALETTE2) and the frequency map (page @SPACE) give each layer its own range.</li>'
    '<li style="font-size:11.4pt;margin-bottom:3pt">No build: the timeline planner (page @TIMELINE), the layer map (page @LAYERS) and slide 7 show layers entering and leaving.</li>'
    '<li style="font-size:11.4pt;margin-bottom:3pt">Clicky automation: the five curve shapes (page @AUTO1) and the worked example (page @EXAMPLE2).</li>'
    '<li style="font-size:11.4pt;margin-bottom:0">A distorted peak or wash: the space page (page @SPACE) and slide 11.</li></ul></div>')
TN1_SIZE = 11.8
PROJ_SIZE = 11.8
VOCAB_GAP = 7
LOGIC_SIZE = 8.9
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


def zone_text(lo, hi):
    if hi < 1000:
        return f"{lo}–{hi} Hz"
    if lo >= 1000:
        return f"{lo / 1000:g}–{hi / 1000:g} kHz"
    return f"{lo} Hz–{hi / 1000:g} kHz"


def freq_of(layer):
    return next(r for r in FREQ if r[0] == layer)


def lanes_body(W=1250, name="lanes pic", fs=22):
    """The four automation lanes of the worked example, drawn from EX_AUTO under the four sections."""
    gx = 290
    pwid = W - gx - 16
    X = lambda bar: X_of(bar, gx, pwid, EX_BARS)
    shade = {"Hush": "#4a4a4a", "Build": "#000", "Peak": ACCENT, "Fade": "#4a4a4a"}
    out = []
    sh = 44
    for nm, a, b in EX_SECTIONS:
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b + 1) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{shade[nm]}"/>')
        out.append(D.t_((X(a) + X(b + 1)) / 2, sh / 2 + fs * .3 + 2, nm.upper(), fs - 2, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 2, X(b + 1) - X(a) - 10)
    lh, lg = 74, 12
    for i, (ly, par, unit, lo, hi, pts) in enumerate(EX_AUTO):
        yy = sh + 14 + i * (lh + lg)
        lbl = f"{ly} · {par}".upper()
        out.append(D.t_(gx - 14, yy + lh / 2 - 2, lbl, 17, 700, anchor="end"))
        D.lab(name + " lanes", lbl, 17, gx - 24)
        rng_ = f"{lo:g} to {hi:g} {unit}" if unit != "L–R" else "left to right"
        out.append(D.t_(gx - 14, yy + lh / 2 + 20, rng_, 16, 500, anchor="end"))
        D.lab(name + " ranges", rng_, 16, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.6"/>')
        for nm, a, b in EX_SECTIONS[1:]:
            out.append(f'<line x1="{X(a):.1f}" y1="{yy}" x2="{X(a):.1f}" y2="{yy + lh}" stroke="#9a9a9a" stroke-width="1.4" stroke-dasharray="5 5"/>')
        xy = [(X(t), yy + lh - 8 - (v - lo) / (hi - lo) * (lh - 16)) for t, v in pts]
        out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in xy)}" fill="none" stroke="{ACCENT}" stroke-width="5" stroke-linejoin="round"/>')
        for a, b in xy:
            out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="5.5" fill="#000"/>')
    ty = sh + 14 + len(EX_AUTO) * (lh + lg) - 4
    for bar in (1, 6, 11, 16, 21, 26, 31):
        lbl = mmss(bar_time(bar))
        anc = "start" if bar == 1 else ("end" if bar == 31 else "middle")
        out.append(f'<line x1="{X(bar):.1f}" y1="{ty}" x2="{X(bar):.1f}" y2="{ty + 10}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(bar), ty + 10 + 19, lbl, 19, 500, anchor=anc))
        D.lab(name + " ticks", lbl, 19, 70)
    return "".join(out), W, ty + 36


# ================================================================ small page helpers
CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; table-layout: fixed; } table.sg td, table.sg th { border: 1.25pt solid #000; text-align: center; "
          "padding: 0; font-size: 8pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.2in; font-size: 9pt; } "
          "table.sg td.b { border-left: 2.5pt solid #000; } </style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, "
              "worked example (2 pages)"),
             ("Student pages", "brief", "reflect", "Scene brief, sound palette cards (2 pages), Alchemy and sampler recipes, automation guide (2 pages), "
              "reverb, EQ and width, storm-arc timeline, layer map, automation plan, project sheet (3 pages), rubric, vocabulary, "
              "feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period sound design project for high school music technology. Each '
             f'student designs a snowstorm soundscape from scratch in Logic Pro: no melody, no drums and no loops, only layers of wind, ice, '
             f'noise and pads made with Alchemy, Quick Sampler and Retro Synth, shaped with automation of filter cutoff, volume, pan and reverb '
             f'send, and placed with reverb, EQ and stereo width. The piece is 60 to 90 seconds and follows a hush, build, peak and fade. Students '
             f'plan it, build and mix it, present it and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look through the scene brief (page {D.IX("brief")}) and the worked example (pages {D.IX("example")}–{D.IX("example2")}), and check the setup (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("brief")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> see the variations on page {D.IX("tn1")}.</li>'
             f'<li><b>No melody needed:</b> students who want a tune can add one, but the rubric scores layers, automation, the arc, space and the plan.</li>'
             f'<li><b>Feedback:</b> students write three questions and answer classmates’ on a class board or on paper.</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'texture, movement and space can hold a listener’s attention without a melody: layers, automation and reverb turn noise into a storm.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Sound design · Logic Pro<br>Design a snowstorm from scratch, with no melody.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13pt;line-height:1.5">One original soundscape, 60 to 90 seconds long, of a snowstorm that builds, peaks and fades. '
             f'It has at least six layers (at least two built in Alchemy and one from noise), at least four automated parameters (filter cutoff, '
             f'volume, pan and reverb send), reverb, EQ and stereo width, and a mix that does not clip. Students hand in a bounced .mp3 or .wav and the '
             f'zipped .logicx project, plus their plans and a reflection, then play it and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12.6pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.6pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12.6pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.4pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}, music technology, music production or sound design</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods (3 or 4 classes work: see page {D.IX("pacing")}): choose and plan, build the layers, automate and mix, present and reflect</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Alchemy, Quick Sampler, Retro Synth, Auto Filter, automation lanes, ChromaVerb or Space Designer, Channel EQ, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a place to hand in files and a class board or paper for feedback</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>Rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s and the '
             f'teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:11.6pt">Students should know how '
             f'to open a project, add a software instrument and use the mixer in Logic. Nobody needs to read music or play an instrument: the '
             f'palette cards and recipes describe every sound in words.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Sound design project", inner, n, key="overview")


def setup_page(n, wm=False):
    chk_items = ["Decide which scenes you will offer (page @BRIEF).",
                 "Open Logic Pro on a student computer: can you add an Alchemy track, hear it through headphones and draw automation (press A)?",
                 "Check that the tools on pages @ALCHEMY and @SPACE are there (Alchemy, Quick Sampler, Retro Synth, Auto Filter, ChromaVerb or Space Designer, Channel EQ).",
                 "Read the worked example (pages @EXAMPLE–@EXAMPLE2)."]
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.8pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the final listen, because a rumble needs good low end.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav, the zipped .logicx and the reflection.</li>'
             f'<li><b>The scene brief and palette cards</b>, printed (pages {D.IX("brief")}–{D.IX("palette2")}), or shown on the projector.</li>'
             f'<li><b>The recipes, automation guide and space page</b>, printed (pages {D.IX("alchemy")}–{D.IX("space")}).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("brief")}–{D.IX("reflect")}).</li>'
             f'<li><b>A microphone</b> is optional: students can record a short sound for Quick Sampler, such as paper or a fingernail on a desk. A MIDI keyboard is optional too.</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(D.fill(c) if "@" in c else c, 13, "font-size:11.8pt;margin-bottom:7pt") for c in chk_items) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.6pt">Students build layers that blur together, never build to a peak, click when they automate, or crush the peak. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.4pt">Ask while students work: what is this layer’s job? Where does the storm peak? What is moving here?</li>'
             f'<li style="font-size:11.4pt">On Class 1, ask students to close their eyes while you describe a storm and raise a hand when it starts to build, peaks and fades. Compare the hands.</li>'
             f'<li style="font-size:11.4pt">A student who is stuck on sound design can start from a Library noise or pad preset in Alchemy and change its filter and effects.</li></ul></div>'
             f'{D.H2("Choosing scenes")}'
             f'<div class="box"><span class="k">A secular, seasonal theme</span><p style="margin:0;font-size:11.2pt;line-height:1.4">'
             f'The project is about winter weather and place, not a holiday. Nothing is sung, no carol is used and there is no sleigh, '
             f'no character and no brand. Students who prefer another weather or place (a desert wind, a rainstorm) can use the same plan; approve their scene on Class 1.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.2pt;line-height:1.4">'
             f'Noise, bass and loud peaks are tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


SCENES = [("A", "Mountain hut at night", "The listener is inside, close to a window. The storm arrives over the ridge, hits the hut and moves on. "
                                        "Wind is the main character."),
          ("B", "Town square after midnight", "The listener stands in an empty square. Snow muffles everything. The storm is wide and soft, with "
                                              "hiss and a deep rumble, and the streetlights hum."),
          ("C", "Research station on an ice field", "The listener is in a metal hut. The storm is harsh and high, with ice ticking on the walls, "
                                                    "and the loudest moment feels like a whiteout.")]


def brief_page(n, wm=False):
    sc = "".join(f'<tr><td style="width:6%;text-align:center"><b>{a}</b></td><td style="width:24%"><b>{b}</b></td><td>{c}</td></tr>' for a, b, c in SCENES)
    inner = (f'<p style="margin:0 0 4pt;font-size:11pt;line-height:1.4">A studio needs <b>60 to 90 seconds of a snowstorm</b> for a scene. '
             f'It arrives, builds, peaks and fades away. There is <b>no melody</b>: you make the storm from layers of wind, ice, noise and pads, and '
             f'you draw how it changes. The listener should know where they are without a word of dialogue.</p>'
             f'<span class="k">Choose a scene (or invent one your teacher approves)</span>'
             f'<table class="t" style="font-size:10.2pt"><tr><th>#</th><th>Scene</th><th>What the listener hears</th></tr>{sc}</table>'
             f'<div class="box acc-b" style="margin:4pt 0 4pt"><span class="k">My scene card</span>'
             f'<div class="fl" style="margin:3pt 0 7pt"><b>My scene:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 7pt"><b>Where the listener is:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 7pt"><b>The mood in three words:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 7pt"><b>How the storm starts:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 7pt"><b>What the peak feels like:</b><span></span></div>'
             f'<div class="fl" style="margin:0"><b>How it ends:</b><span></span></div></div>'
             f'<div class="cols" style="gap:12pt"><div class="box"><span class="k">Rules of the brief</span><ul style="margin:0;font-size:10pt">'
             f'<li style="font-size:10pt">60 to 90 seconds, set by the timeline (page {D.IX("timeline")}).</li>'
             f'<li style="font-size:10pt">Six or more layers, each with its own job (pages {D.IX("palette1")}–{D.IX("palette2")}).</li>'
             f'<li style="font-size:10pt">Four or more automated parameters.</li>'
             f'<li style="font-size:10pt">No melody, no drums, and no recordings you did not make or have the right to use.</li></ul></div>'
             f'<div class="box"><span class="k">Listen first, with your eyes closed</span><p style="margin:0;font-size:10pt;line-height:1.35">'
             f'Think of the worst weather you have been out in. What was the first sound? What happened to it as it got closer? What did you hear '
             f'underneath it? What stopped it from being silent at the end? Write one sound for each question on the lines below.</p></div></div>'
             f'<span class="k" style="margin-top:6pt">Sounds I heard in my head (one per question)</span>'
             f'<div class="ln2" style="height:20pt"></div><div class="ln2" style="height:20pt"></div><div class="ln2" style="height:20pt"></div><div class="ln2" style="height:20pt"></div>')
    return D.page("Scene brief", "STUDENT", "Class 1", inner, n, wm, name=True, key="brief")


def pal_card(i, p, fs=12.6, mb=9):
    nm, job, make, aut = p[0], p[1], p[2], p[4]
    lo, hi, _hp = freq_of(nm)[1:]
    zone = zone_text(lo, hi)
    return (f'<div class="box" style="margin-bottom:{mb}pt;padding:8pt 12pt"><div style="display:flex;justify-content:space-between;align-items:baseline">'
            f'<span class="k" style="font-size:13pt;margin:0;color:#000">{i} · {nm}</span><span class="k" style="margin:0">Zone {zone}</span></div>'
            f'<p style="margin:2pt 0 1.5pt;font-size:{fs}pt;line-height:1.3"><b>Its job.</b> {job}</p>'
            f'<p style="margin:0 0 1.5pt;font-size:{fs}pt;line-height:1.3"><b>Make it.</b> {D.fill(make) if "@" in make else make}</p>'
            f'<p style="margin:0;font-size:{fs}pt;line-height:1.3"><b>Automate it.</b> {D.fill(aut) if "@" in aut else aut}</p></div>')


def palette1_page(n, wm=False):
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.36">Every layer in a storm has a <b>job</b> and a <b>zone</b>, the range of pitch it needs '
             f'(page {D.IX("space")}). These cards describe the sounds in words, not presets: use them as recipes and make them your own. Cards 1 to 4 are the body '
             f'of the storm. Use at least six cards across the two pages; at least two must be made in Alchemy.</p>'
             + "".join(pal_card(i + 1, p) for i, p in enumerate(PALETTE[:4])))
    return D.page("Sound palette · 1 of 2", "STUDENT", "Class 1", inner, n, wm, name=False, key="palette1")


def palette2_page(n, wm=False):
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.36">Cards 5 to 8 are the details: the bright, high sounds that appear '
             f'at the peak, and the sparse ones that show how quiet the hush is. Some layers should come and go: a layer that plays all the time cannot '
             f'make the storm build. Tick the cards you will use and write the track name you give each.</p>'
             + "".join(pal_card(i + 5, p, mb=6) for i, p in enumerate(PALETTE[4:]))
             + f'<div class="box" style="padding:4pt 10pt;margin-bottom:10pt"><span class="k">My layers from the palette (tick, then name the track)</span><div class="cols" style="gap:12pt">'
             f'<div>' + "".join(D.chk(f"<b>{p[0]}</b> = <span style='display:inline-block;width:1.4in;border-bottom:1pt solid #000'>&nbsp;</span>", 11, "font-size:9.6pt;margin-bottom:1pt") for p in PALETTE[:4]) +
             f'</div><div>' + "".join(D.chk(f"<b>{p[0]}</b> = <span style='display:inline-block;width:1.4in;border-bottom:1pt solid #000'>&nbsp;</span>", 11, "font-size:9.6pt;margin-bottom:1pt") for p in PALETTE[4:]) +
             f'</div></div></div>')
    return D.page("Sound palette · 2 of 2", "STUDENT", "Class 1", inner, n, wm, name=False, key="palette2")


def alchemy_page(n, wm=False):
    boxes = ""
    for inst, ttl, rows in RECIPES:
        body = "".join(f'<p style="margin:0 0 2pt;font-size:10.9pt;line-height:1.32"><b>{a}.</b> {D.fill(b) if "@" in b else b}</p>' for a, b in rows)
        boxes += (f'<div class="box" style="margin-bottom:6pt;padding:6pt 10pt"><span class="k" style="font-size:12.5pt;margin:0 0 2pt;color:#000">'
                  f'{inst} · {ttl}</span>{body}</div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:11pt;line-height:1.38">Four recipes, in words. Settings are starting points: change them by ear. '
             f'The same ideas work in other synths, but the names here are from Logic Pro. Nothing is supplied: you make every sound. '
             f'Build at least two layers in Alchemy.</p>{boxes}'
             f'<div class="box acc-b" style="padding:5pt 10pt"><span class="k">Three habits of a good sound designer</span><p style="margin:0;font-size:10.8pt;line-height:1.3">'
             f'<b>Slow:</b> real wind moves slowly, so use slow LFOs and long envelopes. <b>Small:</b> a little modulation is enough. '
             f'<b>Different:</b> two layers made the same way sound like one. Change the source, the filter or the speed.</p></div>')
    return D.page("Alchemy, Quick Sampler and Retro Synth recipes", "STUDENT", "Class 2", inner, n, wm, name=False, key="alchemy")


def auto1_page(n, wm=False):
    modes = [("Read", "plays the automation you drew back"), ("Touch", "records while you hold a control, then returns to the drawn line"),
             ("Latch", "records while you hold a control and stays at the last value"), ("Write", "records from the start of playback, over everything")]
    mrows = "".join(f"<tr><td style='width:16%'><b>{a}</b></td><td>{b}</td></tr>" for a, b in modes)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.38"><b>Automation</b> is a curve that moves a control over time. It is how a storm builds: '
             f'the wind’s cutoff opens, a gust swells, the ice moves from left to right, and the reverb falls away at the peak. Everything you can turn in Logic can be automated.</p>'
             f'<div style="margin:2pt 0 4pt">{D.body_svg(curves_body(1100, "page curves", 22, 16))}</div>'
             f'<div class="cols" style="gap:12pt"><div class="box acc-b" style="padding:5pt 10pt"><span class="k">How to draw it in Logic</span><ol style="margin:0;padding-left:14pt">'
             f'<li style="font-size:10.8pt;margin-bottom:2pt">Press <b>A</b> to show automation on the track.</li>'
             f'<li style="font-size:10.8pt;margin-bottom:2pt">In the track header, choose a parameter: Volume, Pan, a plug-in control such as a filter cutoff, or a send.</li>'
             f'<li style="font-size:10.8pt;margin-bottom:2pt">Click the line to add a point; drag it up or down, or left or right. Use few points.</li>'
             f'<li style="font-size:10.8pt;margin-bottom:0">Press play and listen. Move the points until the change is smooth.</li></ol></div>'
             f'<div class="box" style="padding:5pt 10pt"><span class="k">Or record it by hand</span><table class="t" style="font-size:9.4pt;margin:2pt 0 0">{mrows}</table></div></div>'
             f'<span class="k" style="margin-top:5pt">Try it: draw a gust (a Swell over 2 bars) and a build (a Ramp over 10 bars)</span>'
             f'<div style="margin:2pt 0 2pt">{D.body_svg(lane_blank(1100, 12, 1, "lane try 1", 84, first=True))}</div>'
             f'<div style="margin:0 0 2pt">{D.body_svg(lane_blank(1100, 12, 1, "lane try 2", 84, first=False))}</div>'
             f'<div class="cols" style="gap:12pt;margin-top:5pt"><div class="box" style="padding:5pt 10pt"><span class="k">Rules for smooth automation</span><ul style="margin:0">'
             f'<li style="font-size:10.8pt;margin-bottom:2pt">Fewer points make smoother curves. A gust needs three, not thirty.</li>'
             f'<li style="font-size:10.8pt;margin-bottom:2pt">Move slowly: 2 to 4 seconds for a gust, 20 seconds or more for a build.</li>'
             f'<li style="font-size:10.8pt;margin-bottom:0">Never jump a volume or a cutoff in one step unless you want a click.</li></ul></div>'
             f'<div class="box" style="padding:5pt 10pt"><span class="k">Tempo turns bars into seconds</span><p style="margin:0;font-size:10.8pt;line-height:1.32">'
             f'At 120 BPM one bar lasts 240 ÷ 120 = 2 seconds. A gust of 2 bars is 4 seconds; a build of 10 bars is 20 seconds. '
             f'Use the timeline (page {D.IX("timeline")}) to plan where each curve starts and ends.</p></div></div>')
    return D.page("Automation guide · 1 of 2", "STUDENT", "Class 3", inner, n, wm, name=False, key="auto1")


PARAM_ROWS = [("Filter cutoff", "How bright a sound is", "Alchemy or Auto Filter: the cutoff", "Wind: low in the hush, wide open at the peak"),
              ("Volume", "How loud a layer is", "The channel fader or a Gain plug-in", "Wind: from very quiet to the loudest moment"),
              ("Pan", "Where a sound sits, left to right", "The Pan knob on the channel strip", "Ice: tick from left to right and back"),
              ("Reverb send", "How far away it sounds", "The Send knob to a reverb on an aux", "Pad: wet in the hush and fade, dry at the peak")]


def auto2_page(n, wm=False):
    prow = "".join(f"<tr><td style='width:16%'><b>{a}</b></td><td style='width:22%'>{b}</td><td style='width:26%'>{c}</td><td>{d}</td></tr>" for a, b, c, d in PARAM_ROWS)
    pts = "".join(f"<tr><td><b>{ly}</b> · {par}</td><td>" + " · ".join(f"bar {b} ({mmss(bar_time(b))}): {v:g}" for b, v in pts_) + "</td></tr>"
                  for ly, par, _u, _lo, _hi, pts_ in EX_AUTO)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.38">Four lanes are enough to make a storm move. Here are the four lanes of the worked example '
             f'(pages {D.IX("example")}–{D.IX("example2")}) under its four sections. The sections’ bars decide when each curve turns; the values are in the table below.</p>'
             f'<div style="margin:2pt 0 4pt">{D.body_svg(lanes_body(1250, "page lanes"))}</div>'
             f'{D.H2("The four parameters")}'
             f'<table class="t" style="font-size:9.6pt"><tr><th>Parameter</th><th>It changes</th><th>Where it is</th><th>A storm idea</th></tr>{prow}</table>'
             f'{D.H2("The points on each lane (from the worked example)")}'
             f'<table class="t" style="font-size:9pt;line-height:1.22"><tr><th style="width:26%">Lane</th><th>Points: bar (time): value</th></tr>{pts}</table>'
             f'<div class="box acc-b" style="margin-top:5pt;padding:5pt 10pt"><span class="k">Reading the picture</span><p style="margin:0;font-size:10.8pt;line-height:1.32">'
             f'The cutoff and the volume of the wind both rise through the build and are highest in the peak. The pad’s reverb send does the opposite: it is lowest at the peak and highest at the '
             f'ends. The ice’s pan swings wider each time. Three curves that move together make the peak feel big; one that moves the other way gives it depth.</p></div>')
    return D.page("Automation guide · 2 of 2", "STUDENT", "Class 3", inner, n, wm, name=False, key="auto2")


def space_page(n, wm=False):
    rows = "".join(f"<tr><td><b>{nm}</b></td><td>{zone_text(lo, hi)}</td><td>{hp:g} Hz</td></tr>"
                   for nm, lo, hi, hp in sorted(FREQ, key=lambda r: r[1]))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.4pt;line-height:1.36">A good soundscape gives every layer its own <b>place</b>: a range of pitch, a distance and a position '
             f'between the speakers. Use the frequency map to place each layer, then reverb, EQ and width to keep them apart.</p>'
             f'<div style="margin:2pt 0 3pt">{D.body_svg(freq_body(1100, "page freq", 20, 17))}</div>'
             f'<div class="cols" style="gap:10pt"><div><span class="k">Channel EQ high-pass for each layer</span>'
             f'<table class="t" style="font-size:9pt;margin:2pt 0 0"><tr><th>Layer</th><th>Zone</th><th>High-pass</th></tr>{rows}</table>'
             f'<p style="margin:2pt 0 0;font-size:9pt;line-height:1.25">Turn on the lowest band of Channel EQ as a high-pass filter and set its frequency. Everything below it is cut.</p></div>'
             f'<div><div class="box acc-b" style="padding:4pt 9pt;margin-bottom:5pt"><span class="k">Reverb · distance</span><p style="margin:0;font-size:9.4pt;line-height:1.28">'
             f'ChromaVerb or Space Designer on an aux that layers send to. More send, a bigger size and a longer decay mean farther away; less send means close and dry. '
             f'Use more in the hush and fade and less at the peak.</p></div>'
             f'<div class="box" style="padding:4pt 9pt;margin-bottom:5pt"><span class="k">Pan and stereo width</span><p style="margin:0;font-size:9.4pt;line-height:1.28">'
             f'Pan puts a sound on one side; the Stereo Spread plug-in, if you have it, widens a layer. Pan the ice, widen the pad and shimmer, and keep the rumble in the centre.</p></div>'
             f'<div class="box" style="padding:4pt 9pt"><span class="k">Auto Filter · movement</span><p style="margin:0;font-size:9.4pt;line-height:1.28">'
             f'A low-pass cutoff that opens makes a sound seem to come closer. Use its LFO for slow breathing, and automate the cutoff for the big build.</p></div></div></div>'
             f'<div class="box" style="margin-top:5pt;padding:4pt 10pt"><span class="k">Check before I bounce</span>'
             + "".join(D.chk(c, 10.5, "font-size:9.6pt;margin-bottom:1.5pt") for c in [
                 "Every layer has a high-pass at or below the bottom of its zone (the rumble’s is very low, 25 Hz).",
                 "The rumble is in the centre. The ice and the pad are spread; the loudest moment does not clip.",
                 "I listened quietly first, then at a normal level, and the layers are all still audible."]) + '</div>')
    return D.page("Reverb, EQ and stereo width", "STUDENT", "Class 3", inner, n, wm, name=False, key="space")


def timeline_page(n, wm=False):
    secs = "".join("<tr>" + f"<td style='height:30pt'><b>{nm}</b></td>" + "<td></td>" * 5 + "</tr>" for nm in ("Hush", "Build", "Peak", "Fade"))
    hr = "".join(f"<tr><td><b>{b}</b></td><td>{240 / b:.2f} s</td>" + "".join(
        f"<td{' style=\"font-weight:700;background:#ececec\"' if 60 <= length_s(bars, b) <= 90 else ''}>{length_s(bars, b):.1f} s</td>" for bars in LEN_BARS)
        + "</tr>" for b in LEN_BPMS)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 1: plan the arc. Choose a tempo (60 to 120 BPM) and decide how many bars each section lasts. '
             f'One bar of 4/4 lasts <b>240 ÷ BPM</b> seconds, so seconds = bars × 240 ÷ BPM. The sections’ bars must add up to a total of 60 to 90 seconds. '
             f'Compare your plan with the worked example (page {D.IX("example")}).</p>'
             f'<div class="fl" style="margin:0 0 4pt"><b>My tempo (BPM):</b><span style="flex:0 0 0.8in"></span><b>One bar lasts 240 ÷ tempo =</b><span style="flex:0 0 0.8in"></span><b>seconds</b></div>'
             f'<table class="map" style="margin-bottom:3pt"><tr><th style="width:11%">Section</th><th style="width:33%">What the listener should feel</th><th style="width:10%">First bar</th>'
             f'<th style="width:10%">Bars</th><th style="width:16%">Seconds</th><th>Time (from–to)</th></tr>{secs}'
             f'<tr><td><b>Total</b></td><td></td><td style="background:#ececec"></td><td></td><td></td><td style="background:#ececec"></td></tr></table>'
             f'<div class="fl" style="margin:3pt 0 5pt"><b>Do my bars add up?</b><span></span><b>Total bars × 240 ÷ tempo =</b><span style="flex:0 0 0.8in"></span><b>s (60 to 90)</b></div>'
             f'<span class="k">My storm arc: draw how intense it is, from quiet to peak</span>'
             f'<div style="margin:2pt 0 3pt">{D.body_svg(arc_blank(1100))}</div>'
             f'<div class="cols" style="gap:10pt"><div><span class="k">Length helper (4/4)</span><table class="t" style="font-size:9pt;margin-top:2pt"><tr><th>BPM</th><th>One bar</th>'
             + "".join(f"<th>{b} bars</th>" for b in LEN_BARS) +
             f'</tr>{hr}</table><p class="small" style="margin:1pt 0 0">Shaded and bold: 60 to 90 seconds.</p></div>'
             f'<div class="box acc-b" style="flex:0 0 2.1in;padding:4pt 9pt"><span class="k">Moments I plan</span><p style="margin:0;font-size:9pt;line-height:1.3">'
             f'Write the bar where each new layer enters, and the bar where the peak begins. Time = (bar − 1) × seconds per bar.</p>'
             + '<div class="ln2" style="height:19pt"></div>' * 4 + '</div></div>')
    return D.page("Storm arc and timeline planner", "STUDENT", "Class 1", inner, n, wm, name=True, key="timeline")


ARR_COLS = 24         # each column is two bars: 48 bars


def layers_page(n, wm=False):
    cg = "<colgroup><col style='width:1.1in'>" + "<col>" * ARR_COLS + "</colgroup>"
    head = "<tr><th>Layer</th>" + "".join(f"<th>{2 * i + 1}</th>" for i in range(ARR_COLS)) + "</tr>"
    body = "".join("<tr><td class='l' style='height:25pt'></td>" + "".join(f"<td class='{'b' if i % 2 == 0 else ''}'></td>" for i in range(ARR_COLS))
                   + "</tr>" for _ in range(9))
    inner = (f'{CSS_SG}<style>table.sg th {{ font-size: 6.4pt; }} table.sg td.l {{ width: 1.1in; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.4pt">Step 2: the layer map. Each column is 2 bars (the number is its first bar). Write each layer’s name at the left, shade the columns where it plays '
             f'and draw a heavy line where each section starts (every thick line is 4 bars). A storm builds when layers enter, so not every layer should play the whole time.</p>'
             f'<table class="sg">{cg}{head}{body}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:6pt"><div class="box acc-b"><span class="k">My sections</span>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Hush:</b><span style="flex:0 0 0.6in"></span><b>bars</b><span></span></div>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Build:</b><span style="flex:0 0 0.6in"></span><b>bars</b><span></span></div>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Peak:</b><span style="flex:0 0 0.6in"></span><b>bars</b><span></span></div>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Fade:</b><span style="flex:0 0 0.6in"></span><b>bars</b><span></span></div></div>'
             f'<div class="box"><span class="k">Count my layers</span>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Layers in the hush:</b><span></span></div>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Layers at the peak:</b><span></span></div>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Layers in the last 4 bars:</b><span></span></div>'
             f'<p class="small" style="margin:3pt 0 0">The peak should have the most layers.</p></div></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Checks before I bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:2pt") for c in [
                 "I can name the scene in the first ten seconds, and the peak is clearly the loudest moment.",
                 "At least six layers, each with its own job, and at least two made in Alchemy.",
                 "At least four parameters are automated, each audible, and EQ and reverb are in use.",
                 "The soundscape is between 60 and 90 seconds."]) + '</div>')
    return D.page("Layer map", "STUDENT", "Classes 1–3", inner, n, wm, name=True, key="layers")


def autoplan_page(n, wm=False):
    blocks = ""
    for i in range(4):
        blocks += (f'<div style="margin-bottom:3pt"><div class="fl" style="margin:0 0 1pt"><b>Lane {i + 1}.</b> <b>Layer:</b><span></span><b>Parameter:</b><span></span>'
                   f'<b>From:</b><span style="flex:0 0 0.55in"></span><b>to:</b><span style="flex:0 0 0.55in"></span></div>'
                   f'{D.body_svg(lane_blank(1100, 48, 4, f"lane page {i}", 170, first=True))}</div>')
    inner = (f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 3: plan four automation lanes. Choose a layer and a parameter for each (cutoff, volume, pan and reverb send are the four to use), '
             f'draw the curve you want across the bars with the shapes on page {D.IX("auto1")}, and write the lowest and highest value. Then draw it in Logic. The numbers above each lane are bars.</p>'
             f'{blocks}'
             f'<div class="box acc-b" style="padding:4pt 10pt;margin-top:6pt"><span class="k">Check my lanes</span>'
             + "".join(D.chk(c, 10.5, "font-size:9.6pt;margin-bottom:1.5pt") for c in [
                 "Each lane has at least three points and changes by a lot, not a little.",
                 "Each curve moves clearly: its biggest change happens around the peak, and it settles in the fade.",
                 "I have a lane for cutoff, volume, pan and reverb send."]) + '</div>')
    return D.page("Automation plan", "STUDENT", "Class 3", inner, n, wm, name=True, key="autoplan")


def example_page(n, wm=False):
    secs = "".join(f"<tr><td style='width:12%'><b>{nm}</b></td><td style='white-space:nowrap'>bars {a}–{b}</td><td style='white-space:nowrap'>{b - a + 1} × {EX_BAR_S:g} = {(b - a + 1) * EX_BAR_S:g} s</td>"
                   f"<td style='white-space:nowrap'>{mmss(bar_time(a))}–{mmss(b * EX_BAR_S)}</td><td>{EX_JOBS[nm]}</td></tr>" for nm, a, b in EX_SECTIONS)
    mom = "".join(f"<tr><td style='width:14%'>bar {b}</td><td style='width:12%'>{mmss(bar_time(b))}</td><td>{t}</td></tr>" for b, t in EX_MOMENTS)
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">An <b>invented plan on paper</b>: a snowstorm at 120 BPM. {EX_NOTE} Page 1 of 2: the plan, the arc and the numbers.</p>'
             f'<div class="cols" style="gap:10pt"><div class="box" style="align-self:flex-start"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10pt">{EX_WEAK}</p>'
             f'<p style="margin:2pt 0 0;font-size:9pt">It names no scene, no tempo, no sections and no automation.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The storm arc: 30 bars, four sections")}'
             f'<div style="width:6.7in;margin:1pt auto 2pt">{D.body_svg(arc_body(1250, "page arc", 24, 20))}</div>'
             f'{D.H2("4 · Sections, bars and seconds")}'
             f'<table class="t" style="font-size:8.8pt;line-height:1.2"><tr><th>Section</th><th>Bars</th><th>Length</th><th>Time</th><th>What the listener hears</th></tr>{secs}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:3pt"><div><span class="k" style="font-size:9.4pt">5 · Moments</span>'
             f'<table class="t" style="font-size:8.6pt;line-height:1.18;margin-top:2pt">{mom}</table></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;align-self:flex-start"><span class="k">6 · Checking the numbers</span><p style="margin:0;font-size:8.8pt;line-height:1.3">'
             f'One bar of 4/4 at {EX_BPM} BPM lasts 240 ÷ {EX_BPM} = {EX_BAR_S:g} seconds, so {EX_BARS} bars = {EX_BARS * EX_BAR_S:g} seconds, inside 60 to 90. '
             f'The sections are {" + ".join(str(b - a + 1) for _, a, b in EX_SECTIONS)} bars = {EX_BARS}. '
             f'Time at a bar = (bar − 1) × {EX_BAR_S:g}, so bar 15 starts at {mmss(bar_time(15))}.</p></div></div>')
    return D.page("Worked example · an invented storm", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    lay = "".join(f"<tr><td style='width:15%'><b>{nm}</b></td><td style='width:12%;white-space:nowrap'>"
                  + ", ".join(f"{a}–{b}" for a, b in spans) + f"</td><td>{d}</td></tr>" for nm, spans, d in EX_LAYERS)
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    top = max(EX_DENS)
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same storm, page 2 of 2: the map of the whole piece, then the layers and the numbers.</p>'
             f'{D.H2("7 · The map: 1:00, four sections, eight layers, four lanes")}'
             f'<div style="width:6.5in;margin:1pt auto 3pt">{D.body_svg(map_body(1250, "page map", 24, 20))}</div>'
             f'<span class="k" style="font-size:9.4pt;display:block">8 · Layers (bars they play, and how each is made)</span>'
             f'<table class="t" style="font-size:8.4pt;line-height:1.16;margin-top:2pt"><tr><th>Layer</th><th>Bars</th><th>How it is made</th></tr>{lay}</table>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">9 · Checking the numbers</span><p style="margin:0;font-size:8.8pt;line-height:1.3">'
             f'The peak (bars 15–22) has {top} layers, the most; the hush has {EX_DENS[0]} and the last four bars have {EX_DENS[-1]}. '
             f'Every automation lane sits inside its layer’s bars, and its highest or lowest point falls in the peak (bar 15 = {mmss(bar_time(15))}). '
             f'<b>Three feedback questions (invented):</b> {qs}</p></div>')
    return D.page("Worked example · the map", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


def vocab_page(n, wm=False):
    """Kit version of the vocabulary page: a real gap between the boxes and clearance from the footer rule."""
    cells = "".join(
        f'<div class="box" style="margin-bottom:8pt;padding:6pt 10pt 3pt"><p style="margin:0 0 1pt;font-size:11.6pt"><b style="font-family:Oswald;'
        f'font-size:13pt;text-transform:uppercase;letter-spacing:.02em">{a}</b> — {b}</p>'
        f'<div class="fl" style="margin:6pt 0 6pt"><b>In my own words:</b><span></span></div>'
        f'<div class="fl" style="margin:0 0 3pt"><b>{VOCAB_PROMPT}</b><span></span></div></div>' for a, b in VOCAB)
    inner = (f'<p style="font-size:11.4pt;margin:0 0 6pt">The six words from your project sheet, with definitions. Rewrite each in your '
             f'own words, then show where it happens in your own project.</p>{cells}')
    return D.page("Key vocabulary", "STUDENT", "Vocabulary", inner, n, wm, name=True, key="vocab")


def present_page(n, wm=False):
    """Kit version of the feedback page: the three question lines are evenly spaced (every rule 24pt below the last)."""
    qs = "".join(f'<div class="fl" style="margin:0;height:24pt"><b>Question {i}:</b><span style="height:24pt"></span></div>'
                 f'<div class="ln2" style="margin:0"></div>' for i in (1, 2, 3))
    rows = "".join("<tr><td style='height:40pt'></td><td></td><td></td></tr>" for _ in range(4))
    inner = (f'<div class="box acc-b"><span class="k">From your project sheet, step {len(STEPS)}</span><p style="margin:0;font-size:11.4pt">'
             f'{D.fill(STEPS[-1])}</p></div>'
             f'{D.H2("My three feedback questions")}<p style="margin:0 0 6pt">Ask about things you really want to know, not yes-or-no questions.</p>{qs}'
             f'{D.H2("Classmates’ questions I answered (at least 2)")}'
             f'<table class="map"><tr><th style="width:24%">Classmate</th><th style="width:38%">Their question</th><th>My answer</th></tr>{rows}</table>'
             f'{D.H2("Before I present")}'
             + "".join(D.chk(D.fill(c), 12, "font-size:11.4pt;margin-bottom:6pt") for c in PRESENT_CHECK))
    return D.page("Present and get feedback", "STUDENT", f"Classes {CLASSES - 1}–{CLASSES}", inner, n, wm, name=True, key="present")


def reflect_page(n, wm=False):
    """Kit version of the reflection page: clearance between the teacher box and the footer rule."""
    pr = "".join(
        f'<div style="flex:1;display:flex;flex-direction:column;min-height:0;margin-bottom:5pt"><p style="margin:0 0 1pt;font-size:11.4pt">'
        f'<b style="font-family:Oswald;font-size:13pt;color:{ACCENT}">{i}</b>&nbsp; <b>{D.fill(a)}</b> {D.fill(b)}</p><div class="lines" style="min-height:44pt"></div></div>'
        for i, (a, b) in enumerate(D.REFLECT_PROMPTS, start=1))
    inner = (f'<div class="box acc-b"><span class="k">What a reflection is</span><p style="margin:0;font-size:11.6pt">A reflection is '
             f'{D.REFLECT_DEFINITION}. Answer all four prompts in your own words. You choose how.</p></div>'
             f'<div style="display:flex;gap:18pt;margin:8pt 0 4pt">'
             f'<div style="flex:1">{D.chk("<b>Written.</b> I will write my answers on this page.", 13, "font-size:11.4pt;margin:0")}</div>'
             f'<div style="flex:1">{D.chk("<b>Oral.</b> I will talk my answers through with my teacher. My teacher fills in the box at the bottom.", 13, "font-size:11.4pt;margin:0")}</div></div>'
             f'{pr}'
             f'<div class="box" style="margin:2pt 0 15pt"><span class="k">Oral reflection · teacher</span><div class="fl" style="margin:0"><b>Date:</b>'
             f'<span style="flex:0 0 1.4in"></span><b>Prompts covered (1-4):</b><span></span></div>'
             f'<div class="fl" style="margin:6pt 0 0"><b>Key points I heard:</b><span></span></div></div>')
    return D.page("Reflection · how did it go?", "STUDENT", "After presenting", inner, n, wm, name=True, key="reflect")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "brief": brief_page, "palette1": palette1_page,
         "palette2": palette2_page, "alchemy": alchemy_page, "auto1": auto1_page, "auto2": auto2_page, "space": space_page,
         "timeline": timeline_page, "layers": layers_page, "autoplan": autoplan_page, "example": example_page, "example2": example2_page,
         "vocab": vocab_page, "present": present_page, "reflect": reflect_page}


# ================================================================ content checks (the storm's arithmetic, layers, lanes, frequency map, curves, slides)
def verify_content():
    import re
    from fractions import Fraction
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 6), reqs=(REQS, 6), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 4), palette=(PALETTE, 8), recipes=(RECIPES, 4),
                  freq=(FREQ, 8), curves=(CURVES, 5))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    if set(TAGS) & {"Holiday", "Student Practice", "Theme", "Seasonal"} or "Performing Arts" in SUBJECTS:
        errs.append("tags and subjects must not be headings")
    if re.search(r"winter|holiday|christmas|snow", LISTING_TITLE, re.I):
        errs.append("the listing title must not contain a seasonal word (Winter, Holiday, Christmas, Snow)")
    # ---- the worked example adds up, computed from first principles
    if EX_BAR_S != 2 or Fraction(240, EX_BPM) != 2 or EX_BARS * EX_BAR_S != 60 or not 60 <= EX_BARS * EX_BAR_S <= 90:
        errs.append("30 bars x 2 s = 60 s at 120 BPM, inside 60 to 90")
    if not 60 <= EX_BPM <= 120:
        errs.append("the example tempo must sit in 60 to 120 BPM")
    if EX_SECTIONS[0][1] != 1 or EX_SECTIONS[-1][2] != EX_BARS or any(b_ + 1 != c_ for (_, _, b_), (_, c_, _) in zip(EX_SECTIONS, EX_SECTIONS[1:])):
        errs.append("sections must tile bars 1-30")
    if [b_ - a_ + 1 for _, a_, b_ in EX_SECTIONS] != [4, 10, 8, 8] or sum(b_ - a_ + 1 for _, a_, b_ in EX_SECTIONS) != EX_BARS:
        errs.append("sections 4 + 10 + 8 + 8 = 30")
    if [nm for nm, _, _ in EX_SECTIONS] != ["Hush", "Build", "Peak", "Fade"] or set(EX_JOBS) != {"Hush", "Build", "Peak", "Fade"}:
        errs.append("the four sections are Hush, Build, Peak and Fade")
    secs = {nm: (a_, b_) for nm, a_, b_ in EX_SECTIONS}
    sec_s = [(b_ - a_ + 1) * EX_BAR_S for _, a_, b_ in EX_SECTIONS]
    if sec_s != [8, 20, 16, 16] or sum(sec_s) != 60:
        errs.append("section lengths 8 + 20 + 16 + 16 = 60 seconds")
    if [mmss(bar_time(a_)) for _, a_, _ in EX_SECTIONS] != ["0:00", "0:08", "0:28", "0:44"] or mmss(EX_BARS * EX_BAR_S) != "1:00":
        errs.append("section start times 0:00, 0:08, 0:28, 0:44 and the end at 1:00")
    for b_, _t in EX_MOMENTS:
        if not 1 <= b_ <= EX_BARS:
            errs.append(f"moment at bar {b_} outside the piece")
    if [mmss(bar_time(b_)) for b_, _ in EX_MOMENTS] != ["0:08", "0:16", "0:28", "0:44", "0:52"]:
        errs.append("moments at 0:08, 0:16, 0:28, 0:44, 0:52")
    if EX_MOMENTS[2][0] != secs["Peak"][0] or EX_MOMENTS[3][0] != secs["Fade"][0] or EX_MOMENTS[0][0] != secs["Build"][0]:
        errs.append("the first gust at the start of the Build, the peak's hiss at the start of the Peak, the chimes at the start of the Fade")
    if len(EX_LAYERS) != 8 or len(EX_AUTO) != 4 or len(EX_MOMENTS) != 5:
        errs.append("eight layers, four automation lanes, five moments")
    for nm, spans, _d in EX_LAYERS:
        for a_, b_ in spans:
            if not 1 <= a_ <= b_ <= EX_BARS:
                errs.append(f"layer {nm}: span {a_}-{b_} outside the piece")
    names = [n_ for n_, _, _ in EX_LAYERS]
    if sorted(names) != sorted(r[0] for r in FREQ) or sorted(names) != sorted(p[0] for p in PALETTE):
        errs.append("the worked example, the frequency map and the palette cards must name the same eight layers")
    top = max(EX_DENS)
    pk = secs["Peak"]
    if [i + 1 for i, dd in enumerate(EX_DENS) if dd == top] != list(range(pk[0], pk[1] + 1)):
        errs.append("the most layers must play in exactly the Peak")
    if EX_DENS[0] >= top or EX_DENS[-1] >= top or EX_DENS[-1] > EX_DENS[0] or min(EX_DENS[secs["Build"][0] - 1:secs["Build"][1]]) <= EX_DENS[0]:
        errs.append("the piece starts smaller than its peak, builds above the hush and resolves to no more than the hush")
    # the intensity curve: rises to the Peak, is highest only there, then falls
    iv = EX_INTENSITY
    ib = [b_ for b_, _ in iv]
    vs = [v for _, v in iv]
    if ib != sorted(ib) or ib[0] != 1 or ib[-1] != EX_BARS or max(vs) != 10 or min(vs) < 0:
        errs.append("intensity points in order from bar 1 to bar 30, 0 to 10")
    if [b_ for b_, v in iv if v == 10] != [pk[0], pk[1]]:
        errs.append("intensity 10 only at the start and end of the Peak")
    up = [v for b_, v in iv if b_ <= pk[0]]
    dn = [v for b_, v in iv if b_ >= pk[1]]
    if up != sorted(up) or dn != sorted(dn, reverse=True) or vs[0] >= 3 or vs[-1] >= 3:
        errs.append("intensity rises to the Peak, falls after it, and starts and ends quiet")
    # automation lanes
    spans = {nm: (min(a_ for a_, _ in sp), max(b_ for _, b_ in sp)) for nm, sp, _ in EX_LAYERS}
    for ly, par, unit, lo, hi, pts in EX_AUTO:
        a_, b_ = spans[ly]
        ts_ = [t_ for t_, _ in pts]
        vs_ = [v for _, v in pts]
        if ts_ != sorted(ts_) or len(set(ts_)) != len(ts_) or len(pts) < 3 or ts_[0] < a_ or ts_[-1] > b_:
            errs.append(f"lane {ly}/{par}: points in order, 3+, inside its layer")
        if any(not lo <= v <= hi for v in vs_):
            errs.append(f"lane {ly}/{par}: a value outside {lo}..{hi}")
        if (max(vs_) - min(vs_)) / (hi - lo) < .45:
            errs.append(f"lane {ly}/{par}: a lane that barely moves")
    cut, vol, pan, rev = (a[5] for a in EX_AUTO)
    hi_bars = lambda pts: [b_ for b_, v in pts if v == max(x for _, x in pts)]
    if not (pk[0] <= min(hi_bars(cut)) and max(hi_bars(cut)) <= pk[1]) or not (pk[0] <= min(hi_bars(vol)) and max(hi_bars(vol)) <= pk[1]):
        errs.append("the wind's cutoff and volume must be highest within the Peak")
    lo_rev = [b_ for b_, v in rev if v == min(x for _, x in rev)]
    if not (pk[0] <= min(lo_rev) and max(lo_rev) <= pk[1]) or rev[0][1] <= min(v for _, v in rev) or rev[-1][1] <= min(v for _, v in rev):
        errs.append("the pad's reverb send must be lowest within the Peak and higher at both ends")
    if [v for _, v in pan] != [-50, 60, -70, 80, -80] or any(a_ * b_ >= 0 for (_, a_), (_, b_) in zip(pan, pan[1:])) or \
            any(abs(b_) < abs(a_) for (_, a_), (_, b_) in zip(pan, pan[1:])):
        errs.append("the ice's pan swings left and right, a little wider each time")
    if cut[0][1] >= cut[2][1] or vol[0][1] >= vol[2][1] or cut[-1][1] >= cut[3][1] or vol[-1][1] >= vol[3][1]:
        errs.append("cutoff and volume rise through the Build and fall in the Fade")
    # ---- length helper (computed twice: with fractions, and against the printed list)
    got = [round(float(Fraction(bars * 240, bpm)), 1) for bpm in LEN_BPMS for bars in LEN_BARS]
    if got != LEN_EXPECT or [round(length_s(bars, bpm), 1) for bpm in LEN_BPMS for bars in LEN_BARS] != LEN_EXPECT:
        errs.append("length helper numbers")
    if not any(60 <= v <= 90 for v in LEN_EXPECT) or sum(60 <= v <= 90 for v in LEN_EXPECT) != 13:
        errs.append("thirteen cells of the length helper sit inside 60 to 90 seconds")
    # ---- the frequency map
    for nm, lo, hi, hp in FREQ:
        if not 20 <= lo < hi <= 20000:
            errs.append(f"frequency map: {nm} range {lo}-{hi}")
        if hp > lo:
            errs.append(f"frequency map: {nm}'s high-pass ({hp} Hz) must sit at or below the bottom of its zone ({lo} Hz)")
        if hp < 20:
            errs.append(f"frequency map: {nm}'s high-pass below 20 Hz")
    if [nm for nm, lo, hi, hp in FREQ if hp < 50] != ["Low rumble"]:
        errs.append("only the rumble keeps its lows")
    if freq_of("Low rumble")[2] > 150 or freq_of("Whiteout hiss")[1] < 3000:
        errs.append("the rumble is low and the whiteout hiss is high")
    for nm, txt in (("Whiteout hiss", "3 kHz"), ("Shimmer", "1.5 kHz")):
        if txt not in " ".join(p[2] for p in PALETTE if p[0] == nm) or f"{freq_of(nm)[3] / 1000:g} kHz" != txt:
            errs.append(f"{nm}: its card must name the high-pass the frequency map uses ({txt})")
    # ---- the five automation curves
    cv = {nm: pts for nm, _u, pts in CURVES}
    ys = lambda nm: [y for _, y in cv[nm]]
    if ys("Ramp") != sorted(ys("Ramp")) or ys("Fade") != sorted(ys("Fade"), reverse=True):
        errs.append("ramp rises and fade falls")
    sw = ys("Swell")
    if not (sw[1] > sw[0] and sw[1] > sw[2]):
        errs.append("swell has its peak in the middle")
    if len({y for y in ys("Step")}) != 2:
        errs.append("step has exactly two levels")
    wv = ys("Wave")
    if sum(1 for a_, b_, c_ in zip(wv, wv[1:], wv[2:]) if b_ > a_ and b_ > c_) != 2:
        errs.append("wave has two crests")
    for nm, pts in cv.items():
        xs = [x for x, _ in pts]
        if xs != sorted(xs) or xs[0] != 0 or xs[-1] != 1 or any(not 0 <= y <= 1 for _, y in pts):
            errs.append(f"curve {nm}: points inside 0..1, in order")
    # ---- slides: no bullet may end mid-sentence; page numbers in the notes are real pages
    dangling = {"a", "an", "the", "of", "to", "at", "in", "on", "for", "and", "or", "with", "your", "each", "every", "their", "its", "from", "by"}
    for i, s in enumerate(SLIDES, start=1):
        for b in [x.strip() for x in s[3].split("|") if x.strip()]:
            last = re.sub(r"[^\w’']", "", b.split()[-1]).lower()
            if b.endswith(("’s", "'s")) or last in dangling:
                errs.append(f"slide {i} bullet looks truncated: '{b}'")
    ok_pages = {pg(k) for k in ("timeline", "alchemy", "space", "auto1")}
    for i, s in enumerate(SLIDES, start=1):
        for m in re.finditer(r"\bpage (\d+)\b", s[4]):
            if int(m.group(1)) not in ok_pages:
                errs.append(f"slide {i} notes name page {m.group(1)}, which is not a page the notes mean to cite")
    for i, s in enumerate(SLIDES, start=1):
        for key, word in (("timeline", "own on page"), ("alchemy", "wind bed from page"), ("space", "the page is"), ("auto1", "See page")):
            if word in s[4] and f"{word} {pg(key)}" not in s[4]:
                errs.append(f"slide {i}: page number after '{word}' must be page {pg(key)}")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    txt = " ".join(flat)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, loops, lyrics, artists or albums", "invented plan on paper", "no melody", "Alchemy", "Quick Sampler",
                 "Retro Synth", "ChromaVerb", "Space Designer", "Channel EQ", "Auto Filter", "Step FX", "No student work is included",
                 "Created with the help of digital and AI tools."):
        if need.lower() not in txt.lower():
            errs.append(f"PDF must say: '{need}'")
    if "What changed" in txt or "Kept as I wrote it" in txt or "my project menu" in txt or "my Digital Music Production" in txt:
        errs.append("ORIGINAL kit: no wording about changes to an owner's sheet")
    if "checked by hand" in txt or "handmade" in txt.lower() or "classroom-tested" in txt.lower() or "hand-checked" in txt.lower():
        errs.append("never claim hand checks or classroom testing for a new product")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt:
        errs.append("PDF: 'Grades 9–12'")
    import re
    pal = " ".join(flat[D.IX("palette1") - 1:D.IX("palette2")])
    for p in PALETTE:
        if p[0].lower() not in pal.lower():
            errs.append(f"palette card {p[0]} missing")
        if zone_text(*freq_of(p[0])[1:3]).lower() not in pal.lower():
            errs.append(f"palette card {p[0]}: its zone must print as {zone_text(*freq_of(p[0])[1:3])}")
    al = flat[D.IX("alchemy") - 1]
    for inst, ttl, _rows in RECIPES:
        if inst not in al or ttl.lower() not in al.lower():
            errs.append(f"recipe {inst} · {ttl} missing")
    sp = flat[D.IX("space") - 1]
    for nm, lo, hi, hp in FREQ:
        if f"{hp:g} Hz" not in sp:
            errs.append(f"space page must print {nm}'s high-pass ({hp:g} Hz)")
    a2 = flat[D.IX("auto2") - 1]
    for ly, par, _u, _lo, _hi, pts in EX_AUTO:
        if f"{ly} · {par}".lower() not in a2.lower():
            errs.append(f"automation page 2 must list the lane {ly} · {par}")
        for b_, v in pts:
            if f"bar {b_} ({mmss(bar_time(b_))}): {v:g}" not in a2:
                errs.append(f"automation page 2: point bar {b_} = {v:g} missing")
    a1 = flat[D.IX("auto1") - 1]
    for nm, _u, _p in CURVES:
        if nm.upper() not in a1.upper():
            errs.append(f"automation page 1 must name the curve {nm}")
    for need in ("240 ÷ 120 = 2 seconds",):
        if need not in a1:
            errs.append(f"automation page 1 must say '{need}'")
    import subprocess
    ex = re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-raw", "-f", str(D.IX("example")), "-l", str(D.IX("example2")), D.files()["pdf"], "-"],
                                            capture_output=True, text=True, check=True).stdout)
    for need in ("240 ÷ 120 = 2", "30 bars = 60 seconds", "4 + 10 + 8 + 8 bars = 30", "(bar − 1) × 2", "bar 15 starts at 0:28", "inside 60 to 90"):
        if need not in ex:
            errs.append(f"worked example must say '{need}'")
    for nm, a_, b_ in EX_SECTIONS:
        if f"{b_ - a_ + 1} × 2 = {(b_ - a_ + 1) * 2} s" not in ex:
            errs.append(f"worked example: section {nm} arithmetic missing")
    tl = flat[D.IX("timeline") - 1]
    for need in ("240 ÷ BPM", "seconds = bars × 240 ÷ BPM", "Hush", "Build", "Peak", "Fade", "60 to 90"):
        if need not in tl:
            errs.append(f"timeline page must say '{need}'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up or "no melody" not in up.lower():
        errs.append("UPLOAD.md: must say no audio is included, no melody, and record the open questions")
    m = re.search(r"= 1 cover \+ (\d+) teacher \+ (\d+) student \+ 1 terms page", up)
    if not m or 2 + int(m.group(1)) + int(m.group(2)) != len(PLAN):
        errs.append("UPLOAD.md: the page-count list (1 cover + teacher + student + 1 terms) must total the PDF's pages")
    if m and (int(m.group(1)) != D.IX("example2") - 1 or int(m.group(2)) != D.IX("reflect") - D.IX("brief") + 1):
        errs.append("UPLOAD.md: teacher and student page counts must match the plan")
    mm = re.search(r"plus (\d+) slides = (\d+) for TpT", up)
    if not mm or int(mm.group(1)) != len(SLIDES) or int(mm.group(2)) != len(PLAN) + len(SLIDES):
        errs.append("UPLOAD.md: slides and total pages")
    for t in TAGS:
        if t not in up:
            errs.append(f"UPLOAD.md: tag {t} missing")
    if re.search(r"notation|stave|staff|clef", " ".join(stext + notes), re.I) and "no notation" not in alldeck.lower():
        errs.append("deck mentions notation, but this kit draws none")
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Radiohead", "Billboard", "Bensound", "Ableton"]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
    return errs


def check_summary():
    return (f"the worked example is {EX_BARS} bars at {EX_BPM} BPM = {EX_BARS * EX_BAR_S:g} s (240 / {EX_BPM} = {EX_BAR_S:g} s a bar; sections "
            f"{'+'.join(str(b - a + 1) for _, a, b in EX_SECTIONS)} bars = {'+'.join(f'{(b - a + 1) * EX_BAR_S:g}' for _, a, b in EX_SECTIONS)} s; "
            f"moment and section times recomputed), {len(EX_LAYERS)} layers peak at {max(EX_DENS)} only in the Peak, the intensity curve peaks only in the Peak, "
            f"{len(EX_AUTO)} automation lanes sit inside their layers with their extremes in the Peak; length helper recomputed (25 cells, 13 in range); "
            f"{len(FREQ)} layers have a frequency range and a high-pass at or below it, matching the palette cards; the five automation curves have "
            f"the shapes they name; titles carry no seasonal word; no audio, notation, recordings, artist names or student work; grades 9-12; "
            f"tags and subjects are not headings; no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("brief") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students design a snowstorm from scratch in Logic Pro, with no melody and no audio supplied. They build six or more layers "
            f"of wind, ice, rumble, pads and noise with Alchemy, Quick Sampler and Retro Synth, shape a build, peak and fade of 60 to 90 seconds with "
            f"automation of filter cutoff, volume, pan and reverb send, and place every layer with reverb, EQ and stereo width. This Winter Soundscape "
            f"project takes {CLASSES} class periods and is an original Hudson Beat project; the steps are written for Logic Pro, while the ideas (layers, "
            f"automation, a build, peak and fade) carry over to GarageBand and BandLab.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, two pages of teacher notes "
            f"(struggles, variations, resources, grading), a Logic quick reference, and a two-page worked example (an invented plan on paper: a 60-second "
            f"storm at 120 BPM with a bar and time table, a 30-bar map, eight layers and four automation lanes) ({n_teacher} pages)\n"
            f"• Student pages: a scene brief with three scenes and a scene card, eight sound-palette cards (what each layer does, how to make it in words, and its "
            f"frequency zone), Alchemy, Quick Sampler and Retro Synth recipes, a two-page automation guide with curve diagrams, a reverb, EQ and stereo width "
            f"page with a frequency map, a storm-arc and timeline planner with a length helper, a layer map, an automation plan, the 3-page project sheet "
            f"(overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a feedback planner and a "
            f"reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, the storm arc, "
            f"building the layers, a frequency map, automation curves, a worked-example map, space and mix, what to turn in and the rubric\n\n"
            f"THE FOUR CLASS PERIODS (works in 3 or 4 classes)\n"
            f"• Class 1: hook; choose a scene; plan the storm arc and its timings; start the first layers\n"
            f"• Class 2: build the layers in Alchemy, Quick Sampler and Retro Synth\n"
            f"• Class 3: automate four parameters; add reverb, EQ and stereo width; mix\n"
            f"• Class 4: bounce and hand in; presentations with feedback questions; reflection\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Designing layers of sound from noise, pads and short samples, each with its own job and its own range of pitch\n"
            f"• Planning a timeline in bars and seconds (seconds = bars × 240 ÷ BPM) so the piece lasts 60 to 90 seconds\n"
            f"• Drawing and recording automation (filter cutoff, volume, pan, reverb send) so a sound moves and breathes\n"
            f"• Placing sounds with ChromaVerb or Space Designer, Channel EQ and stereo width, and keeping the loudest moment clean\n"
            f"• Explaining their choices in a presentation and a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource, no melody to enter and no student work. Students make every sound themselves in Logic Pro\n"
            f"• The theme is winter weather, not a holiday: no carols, lyrics, characters or brands\n"
            f"• Requires Logic Pro on a Mac. A microphone and a MIDI keyboard are optional; nobody has to read music\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology, music production or sound design classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"{D.DISCLOSURE_NEW}")
    md = f"""# UPLOAD: Winter Soundscape, original Logic Pro project (TpT 045)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `{SLUG}.zip`. It holds three files in a folder "{ZIP_DIR}":
  - `{SLUG}.pdf`: the teacher and student resource, {np_} pages, US Letter portrait.
  - `{SLUG}-intro-deck.pptx`: the teacher-presented intro deck, {ns} slides (16:9), speaker notes and a Class badge on every slide.
  - `{SLUG}-intro-deck.pdf`: a PDF copy of the deck, {ns} pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

**Page count, adding up to the PDF:** 1 cover + {n_teacher} teacher + {n_student} student + 1 terms = {np_} pages; plus {ns} slides = {np_ + ns} for TpT's "Number of pages or slides".

## 1. Title

```
{LISTING_TITLE}
```
({nt} characters; the limit is 80.) "Logic Pro" is in the first 30 characters, and the title has no seasonal word (Winter, Holiday, Christmas, Snow), because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034); the Winter tag and the cover carry the season. If TpT accepts it, "Winter Soundscape Logic Pro Project ..." would also be a strong search term.

## 2. Description

```
{desc}
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: Music; Computer Science - Technology; Music Composition (all three are in `tpt/SUBJECT-OPTIONS.json` and none is a heading)
- Tags in tpt.json: {", ".join(TAGS)} (four exact entries of `tpt/TAG-OPTIONS.json`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**${PRICE}** (paid), multiple-license price ${PRICE}. $8, in the queue's $7-9 holiday-kit range, for a kit with {np_} pages + {ns} slides, eight palette cards, four recipes, two automation pages, a frequency map and a two-page worked example, listed from November.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the first sound palette page, the second automation page (four lanes on one storm) and the /25 rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **No music notation, no melody and no third-party material.** The kit draws a snowflake, waveforms, automation curves, a frequency map and layer maps only. There is no tune, so there is no public-domain question; the project text, drawings, recipes and numbers are original Hudson Beat work.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036 and 040): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Alchemy (noise source, filter, LFO, envelopes, effects, Library presets), Quick Sampler (recording a sound, pitch, filter, short end), Retro Synth (sine or sub oscillator), Step FX (stated as "if your version has it"), Auto Filter (low-pass, cutoff, LFO), automation (A key, Read, Touch, Latch, Write), ChromaVerb and Space Designer, Channel EQ (lowest band as a high-pass), the Stereo Spread plug-in (stated as "if your version has it"), aux sends, Library (Y), Bounce (Command-B). Menu paths are given only for File › New and File › Bounce; elsewhere the action is described. Nothing says a preset of a given name exists.
"""
    md += """- [ ] **Open questions for the owner:** (1) **Title.** No "Winter" or "Snow" in the title because of TpT's seasonal-title notice (see 1); the Winter tag and the cover carry the season. (2) **Price.** $8, the middle of the $7-9 kit range. (3) **Tag choice.** Winter, Project-based Learning, Projects, Rubrics: the Christmas-Chanukah-Kwanzaa tag is left off on purpose, because this kit is about weather and is not a holiday item.
"""
    with open(os.path.join(HERE, "UPLOAD.md"), "w", encoding="utf8") as f:
        f.write(md)


if __name__ == "__main__":
    if "--check" not in sys.argv:
        write_upload()
    D.main(sys.modules[__name__])
