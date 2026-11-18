#!/usr/bin/env python3
"""Logic Pro project kit: Commercial Jingle (TpT 048): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content, the 30-second arithmetic (bars, beats, seconds, tempo helper, chord loops written as
                              Roman numerals), the worked example, the script timing, ducking lane, drawings, files, page/slide counts,
                              class slots, notes, fonts, fit and overlap, overflow and dead space, truncated slide bullets, banned
                              strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 031, 036, 040 and 045). Students act as a jingle writer for an INVENTED
product: they pick one of four fictional client briefs, plan 30 seconds in bars (bars = BPM / 8), choose a tempo, key and chord loop
(Roman numerals), build the music in Logic Pro (Drummer, Session Players, Alchemy or Retro Synth, Quick Sampler, library loops),
write an 8 to 12 word voice-over with a syllable and timing check, record it, process it (Channel EQ, Compressor, DeEsser 2), duck the
music under it, bounce exactly 30 seconds and collect a client's feedback. No melody is supplied, no audio ships, and no music
notation is drawn anywhere in this kit (waveforms, speech bubbles and lanes only). Every number is computed here and verified.

Shared builder: ../_dmp2_common/dmp2.py (see its README).
"""
import math
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402
D.DISCLOSURE_NEW = "Created with the help of digital and AI tools."   # this kit has no notation or answer keys to verify

# the shared reflection page ran its teacher box into the footer rule; add bottom clearance in this kit only.
_reflect_orig = D.reflect_page
def _reflect_tight(n, watermark=False):
    return _reflect_orig(n, watermark).replace('<div class="box" style="margin-top:2pt">', '<div class="box" style="margin-top:2pt;margin-bottom:12pt">')
D.reflect_page = _reflect_tight
D.STD_PAGES["reflect"] = _reflect_tight

# the closing slide's reflection box sat close to the footer rule; lift it before the deck PDF is made.
_deck_pdf_orig = D.deck_pdf
def _deck_pdf_lifted():
    from pptx import Presentation
    from pptx.util import Inches
    p = os.path.join(HERE, "commercial-jingle-intro-deck.pptx")
    prs = Presentation(p)
    sl = prs.slides[len(prs.slides) - 1]
    for sh in sl.shapes:
        if Inches(5.8) <= sh.top < Inches(7.0) and sh.left < Inches(7.0):
            sh.top = sh.top - Inches(0.2)
    prs.save(p)
    _deck_pdf_orig()
D.deck_pdf = _deck_pdf_lifted

_render_orig = D.render
def _render_transparent(jobs):
    # deck art is placed on white slides: make the white transparent so LibreOffice's PDF export cannot leave a faint grey box
    _render_orig(jobs)
    from PIL import Image
    for j in jobs:
        if os.path.basename(j.get("png", "")).startswith("deck-"):
            im = Image.open(j["png"]).convert("RGB")
            px = im.load()
            w, h = im.size
            out = Image.new("RGBA", (w, h))
            op = out.load()
            for y in range(h):
                for x in range(w):
                    r_, g_, b_ = px[x, y]
                    a = 255 - min(r_, g_, b_)
                    if a == 0:
                        op[x, y] = (255, 255, 255, 0)
                    else:
                        op[x, y] = tuple(min(255, max(0, round(255 - (255 - c) * 255 / a))) for c in (r_, g_, b_)) + (a,)
            out.save(j["png"])
D.render = _render_transparent

D.CSS += ".lines { margin-bottom: 14pt; } "   # NOTES lines on the project sheet: keep the last rule clear of the footer rule
D.CSS += "table.rub { table-layout: fixed; } table.rub th:first-child { width: 15%; }"

ORIGINAL = True
SLUG = "commercial-jingle"
TITLE = "Commercial Jingle"
ACCENT = "#B3262E"          # this product's single accent: cranberry
ACC_LIGHT = "#F7DEDF"
PRICE = "8.00"
CLASSES = 4
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Project-based Learning", "Projects", "Rubrics"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Jingle Project | 30-Second Ad Music & Voice-Over | High School Music"
DESC_START = "Commercial music for high school music technology:"
DESC_MUST = ["Commercial Jingle", "30-second", "voice-over", "Drummer", "Alchemy", "Quick Sampler", "ducking", "no audio", "invented"]
ZIP_DIR = "Commercial Jingle - Hudson Beat"
ZIP_DATE = (2026, 11, 16, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Commercial Music Project</i> | 4 class periods"
DECK_STRAP = "A 30-second ad"
REFLECT_ROW = "Feedback &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Ro" + "land", "Sle" + "igh Ride", "Coca" + "-Cola",
                "McDon" + "ald", "Nik" + "e", "Ama" + "zon", "Kit" + "Kat"]

PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2", "brief", "loop", "plan",
        "build", "layers", "script", "voice", "duck", "bounce", "proj1", "proj2", "proj3", "rubric", "vocab", "feedback", "present",
        "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the arithmetic of 30 seconds (everything below is computed)
LEN_S = 30
BEATS_PER_BAR = 4


def bar_s(bpm):
    """Seconds in one bar of 4/4 at this tempo."""
    return BEATS_PER_BAR * 60 / bpm


def bars_in_30(bpm):
    """Bars in exactly 30 seconds: 30 / (240 / BPM) = BPM / 8."""
    return Fraction(LEN_S * bpm, 240)


FIT_BPMS = [b for b in range(60, 161) if bars_in_30(b).denominator == 1]       # tempos whose 30 seconds is a whole number of bars
FIT_PICK = (80, 88, 96, 104, 112, 120, 128)                                    # the helper table's rows
SYL_PER_S = (3, 4)                                                             # a calm announcer: about 3 to 4 syllables a second
WPS = (2, 2.5, 3)                                                              # words per second: slow, steady, fast


def syl(word):
    """Syllables of one English word by vowel groups (good enough for the invented scripts here; checked against the stated counts)."""
    w = re.sub(r"[^a-z]", "", word.lower())
    g = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and g > 1:
        g -= 1
    return max(1, g)


def words_of(text):
    return [w for w in re.split(r"\s+", text.strip()) if re.sub(r"[^A-Za-z]", "", w)]


def mmss(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


def sec3(x):
    """Seconds to at most three decimals, no trailing zeros (an exact 0.625 shows as 0.625, not a rounded 0.62)."""
    return f"{x:.3f}".rstrip("0").rstrip(".")


def sec(x):
    """Seconds with at most two decimals and no trailing zeros."""
    return f"{x:.2f}".rstrip("0").rstrip(".")


# ---- chords: scales and Roman numerals
SCALES = {"C": "C D E F G A B", "G": "G A B C D E F#", "D": "D E F# G A B C#", "A": "A B C# D E F# G#",
          "Am": "A B C D E F G", "Em": "E F# G A B C D", "Bm": "B C# D E F# G A"}
MAJOR_Q = ["", "m", "m", "", "", "m", "dim"]
MINOR_Q = ["m", "dim", "", "m", "m", "", ""]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]


def numeral(degree, quality):
    """Roman numeral with the right case: capital = major, small = minor, small + degree sign = diminished."""
    r = ROMAN[degree]
    return r.lower() + ("°" if quality == "dim" else "") if quality in ("m", "dim") else r


def parse_numeral(s, minor):
    """'vi' -> degree 5; checks the case against the key's own triad quality."""
    core = s.replace("°", "")
    deg = ROMAN.index(core.upper())
    q = (MINOR_Q if minor else MAJOR_Q)[deg]
    want = numeral(deg, q)
    if want != s:
        raise ValueError(f"numeral {s} has the wrong case/sign in a {'minor' if minor else 'major'} key (expected {want})")
    return deg


def chords_in(key, nums):
    minor = key.endswith("m")
    notes = SCALES[key].split()
    q = MINOR_Q if minor else MAJOR_Q
    out = []
    for s in nums:
        d = parse_numeral(s, minor)
        out.append(notes[d] + {"": "", "m": "m", "dim": "dim"}[q[d]])
    return out


def key_name(k):
    return f"{k[:-1]} minor" if k.endswith("m") else f"{k} major"


LOOPS = [("I–V–vi–IV", ["I", "V", "vi", "IV"], False, "Bright and hopeful", "friendly, upbeat ads"),
         ("vi–IV–I–V", ["vi", "IV", "I", "V"], False, "Warm and a little wistful", "cozy, gift and home ads"),
         ("I–vi–IV–V", ["I", "vi", "IV", "V"], False, "Playful and classic", "kids, snacks and fun"),
         ("I–IV–V–IV", ["I", "IV", "V", "IV"], False, "Bold and energetic", "sports, boots and adventure"),
         ("i–VI–III–VII", ["i", "VI", "III", "VII"], True, "Adventurous, a little mysterious", "trails, quests and big outdoors")]
MAJOR_KEYS = ["C", "G", "D", "A"]
MINOR_KEYS = ["Am", "Em", "Bm"]

# ---- the four client briefs: invented products only (no real brands, no real people)
BRIEFS = [
    dict(k="A", product="Marblemint Cocoa", what="a hot-chocolate mix with a peppermint swirl", audience="Families with kids 6 to 12",
         mood="Cozy and warm", tagline="Warm up the whole house", sounds=["a mug clink", "a soft bell"], bpms=(96, 104),
         loop="vi–IV–I–V", key="C"),
    dict(k="B", product="Glimmerwick String Lights", what="warm-white lights for windows and trees", audience="Adults decorating their homes",
         mood="Sparkling and calm", tagline="Light up the long nights", sounds=["a sparkle of high chimes", "a rising whoosh"], bpms=(112, 120),
         loop="I–V–vi–IV", key="G"),
    dict(k="C", product="Frostpaw Snow Boots", what="waterproof boots for kids", audience="Kids 6 to 10 and their parents",
         mood="Playful and energetic", tagline="Stomp through the snow", sounds=["a stomp or crunch beat", "a whistle"], bpms=(112, 120),
         loop="I–vi–IV–V", key="D"),
    dict(k="D", product="Trailhopper Trail Mix", what="a crunchy snack of nuts, seeds and dried fruit", audience="Teens and hikers",
         mood="Adventurous and fresh", tagline="Take the high trail", sounds=["a crunch", "a rising hook"], bpms=(120, 128),
         loop="i–VI–III–VII", key="Em"),
]

# ---- the worked example: an invented fifth client (not one of the four briefs)
EX_PRODUCT = "Fluffwick Snug Wool Socks"
EX_AUDIENCE = "Everyone with cold feet"
EX_MOOD = "Cozy and cheerful"
EX_TAGLINE = "Happy feet all winter"
EX_SOUNDS = ["a finger snap", "a high pluck"]
EX_BPM = 120
EX_BEAT_S = 60 / EX_BPM
EX_BAR_S = bar_s(EX_BPM)
EX_BARS = 15
EX_KEY = "G"
EX_LOOP = ["I", "V", "vi", "IV"]
EX_TAG_CHORDS = ["IV", "V", "I"]              # bars 13 to 15: the tag walks home
EX_SECTIONS = [("Intro", 1, 2), ("Verse", 3, 6), ("Hook", 7, 12), ("Tag", 13, 15)]
EX_JOBS = {"Intro": "Chords and the pluck alone: the listener leans in and hears the mood.",
           "Verse": "Drums and bass join. The first voice line sets up the problem.",
           "Hook": "Everything plays and the snap enters. The second line names the product.",
           "Tag": "The tag walks home on IV, V and I. The tagline is spoken, then a sting."}
# layer, [(first bar, last bar)], tool, what it does
EX_LAYERS = [("Chords", [(1, 15)], "Keyboard Player", "the I–V–vi–IV loop in G, one chord a bar, a soft pad sound"),
             ("Drums", [(3, 15)], "Drummer", "a calm pop-style drummer; the XY pad up and right in the hook"),
             ("Bass", [(3, 15)], "Bass Player", "roots of each chord; it follows the Chord Track"),
             ("Pluck hook", [(1, 2), (7, 10), (14, 14)], "Alchemy", "four notes, one idea, repeated; it rests while the voice talks"),
             ("Snap", [(7, 12)], "Quick Sampler", "my own finger snap on beats 2 and 4, a must-include sound"),
             ("Sparkle sting", [(6, 6), (15, 15)], "Loop Browser", "a rising sparkle into the hook and a short sting at the end")]
# the voice-over: (bar, beat, text, stated syllables)
EX_VO = [(3, 1, "Cold toes? Not today.", 5), (11, 1, "Fluffwick Snug Wool Socks.", 5), (13, 1, "Happy feet all winter.", 6)]
EX_WPS = 2.5
EX_DUCK_DB = 5
EX_DUCK_LEAD = EX_BEAT_S / 2          # the music starts to dip half a beat before the voice
EX_DUCK_TAIL = EX_BEAT_S              # and is back one beat after it ends
EX_WEAK = "I will make a catchy song for the socks with a voice saying something about them."
EX_STRONG = ("My client sells Fluffwick Snug Wool Socks to everyone with cold feet, in a cozy and cheerful mood. My jingle is 30 seconds at 120 BPM, "
             "so 15 bars of 2 seconds each: intro 2, verse 4, hook 6 and tag 3 bars. The loop is I–V–vi–IV in G (G D Em C), and the tag "
             "walks home on C D G. Six layers, 12 spoken words, and the tagline Happy feet all winter lands in bar 13.")
EX_QUESTIONS = ["Which words did you remember after one listen?", "Did the voice ever fight with the music? Where?",
                "Did the mood match cozy and cheerful, and what told you?"]
EX_NOTE = "Invented, on paper: no audio is included, and a student’s numbers will differ."


def bar_time(bar, beat=1, bpm=EX_BPM):
    return (bar - 1) * bar_s(bpm) + (beat - 1) * 60 / bpm


def vo_span(i):
    bar, beat, text, _s = EX_VO[i]
    t0 = bar_time(bar, beat)
    return t0, t0 + len(words_of(text)) / EX_WPS


def ex_density(bar):
    return sum(1 for _n, spans, _t, _d in EX_LAYERS if any(a <= bar <= b for a, b in spans))


EX_DENS = [ex_density(b) for b in range(1, EX_BARS + 1)]


def ex_chords():
    loop = chords_in(EX_KEY, EX_LOOP)
    tag = chords_in(EX_KEY, EX_TAG_CHORDS)
    return [loop[i % 4] for i in range(12)] + tag


def duck_points():
    """The music-level lane as (seconds, dB) points: down half a beat before each voice line, back up a beat after it."""
    pts = [(0.0, 0.0)]
    for i in range(len(EX_VO)):
        t0, t1 = vo_span(i)
        pts += [(t0 - EX_DUCK_LEAD, 0.0), (t0, -float(EX_DUCK_DB)), (t1, -float(EX_DUCK_DB)), (t1 + EX_DUCK_TAIL, 0.0)]
    pts.append((float(LEN_S), 0.0))
    return pts


# ================================================================ the project text (original; students read these pages)
OVERVIEW = ("You are a jingle writer. A client has hired you to make a 30-second commercial for a product that does not exist, and your "
            "music and voice-over must sell it. You choose one of four client briefs, plan the 30 seconds in bars, pick a tempo, key and "
            "chord loop, and build the music in Logic Pro with Drummer, Session Players, Alchemy or Retro Synth, Quick Sampler and library "
            "loops. Then you write and record an 8 to 12 word voice-over, mix it so the voice sits over the music, and export exactly 30 seconds.")
GOALS = ["Plan a 30-second jingle in bars and seconds from a client brief, and prove that the numbers add up",
         "Build a chord loop and a short arrangement (intro, verse, hook, tag) with Logic Pro tools",
         "Write, time, record and mix an 8 to 12 word voice-over so the voice sits clearly over the music",
         "Export a file of exactly 30 seconds and improve it with a client’s feedback"]
VOCAB = [("Jingle", "A short, catchy piece of music written to sell something, usually with a spoken or sung tagline"),
         ("Tagline", "The short phrase a client wants the listener to remember, such as the line that ends the ad"),
         ("Voice-over", "Speech recorded to play over music, spoken by someone who is not seen"),
         ("Ducking", "Turning the music down while the voice speaks, then back up, so every word can be heard"),
         ("Chord progression", "A pattern of chords that repeats as the loop, written with Roman numerals such as I–V–vi–IV"),
         ("Bounce", "To turn a Logic Pro project into one audio file, here exactly 30 seconds long")]
REQS = ["Choose a client brief (page @BRIEF), or invent a product with your teacher’s approval, and keep its audience, mood, tagline and must-include sounds",
        "Plan exactly 30 seconds: pick a tempo whose bars fit (page @PLAN) and make the sections’ bars and seconds add up",
        "Build a chord loop (page @LOOP) and at least four layers with Drummer or a Session Player and at least one of Alchemy, Retro Synth or Quick Sampler (pages @BUILD–@LAYERS); include both must-include sounds",
        "Write an 8 to 12 word script that includes the tagline, and check its words, syllables and timing (page @SCRIPT)",
        "Record the voice-over, clean it with Channel EQ, Compressor and DeEsser 2, and duck the music under it (pages @VOICE–@DUCK)",
        "Bounce the jingle at exactly 30 seconds (page @BOUNCE), collect a client’s feedback (page @FEEDBACK) and reflect (page @REFLECT)"]
FILE_NAME = "“Your Name – Jingle – Product”"
STEPS = ["<b>Choose</b> — Pick a client brief and fill in your brief card (page @BRIEF)",
         "<b>Plan</b> — Pick a tempo, a key and a chord loop, then plan your sections in bars and seconds (pages @LOOP–@PLAN)",
         "<b>Build the music</b> — Make the loop, drums, bass and hook with the tools on page @BUILD and fill in your layer map (page @LAYERS)",
         "<b>Write the script</b> — Write 8 to 12 words that include the tagline and check their timing (page @SCRIPT)",
         "<b>Record and mix</b> — Record the voice, clean it up and duck the music under it (pages @VOICE–@DUCK)",
         "<b>Bounce</b> — Export exactly 30 seconds and name your files like this: " + FILE_NAME + " (page @BOUNCE)",
         "<b>Present &amp; get feedback</b> — Write three questions you want your client to answer about your jingle. Play it for a classmate "
         "who acts as your client, who fills in the client feedback sheet (page @FEEDBACK), and answer at least 2 of each classmate’s "
         "questions. Then reflect (page @REFLECT)."]
TIPS = ["A jingle is short. Say the product name and the tagline clearly, and make the hook something a listener can hum after one play.",
        "Keep the music simple under the voice. Leave small gaps in the hook for the words, and let the music say more when the voice rests.",
        "Record at least three takes of the whole script and keep the best one. Speak with a smile; listeners can hear it.",
        "Save a new version of your project before each big change, so you can always go back."]
CHECK = ["Bounced .wav or .mp3 of exactly 30 seconds handed in where your teacher says",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Brief card, structure plan, script check and layer map handed in",
         "Client feedback sheet and rubric self-score done (pages @FEEDBACK and @RUBRIC)",
         "I can name every layer and say where the voice ducks the music"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; your final grade is the average of your self-score and your teacher’s score."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Brief & Concept", ["The brief is ignored: no tagline or no product name",
                         "Part of the brief is met; mood or audience unclear",
                         "Tagline, product and one must-include sound; mood roughly fits",
                         "Tagline, both must-include sounds and mood all match the brief",
                         "A memorable concept; tagline, sounds and mood fit"]),
    ("Music & Structure", ["No clear sections, or the plan does not add up to 30 seconds",
                           "A loop and fewer than three layers; sections hard to hear",
                           "A chord loop and three layers; four sections; the bars add up",
                           "A fitting loop and four or more layers; bars and seconds add up to 30",
                           "Clear intro, verse, hook and tag; a hook that sticks; layers enter on purpose"]),
    ("Voice-over & Script", ["No voice-over, or the script is under 8 or over 12 words",
                             "A script of 8 to 12 words, but hard to hear or off time",
                             "Script with the tagline, recorded clearly; some words rushed",
                             "A timed script with the tagline; a clean recording with EQ and Compressor",
                             "A script that fits its bars; a clear, de-essed voice; the tagline lands on a strong beat"]),
    ("Mix & Export", ["The voice is buried or the mix clips; the length is wrong",
                      "The voice can be heard, but the music never steps aside",
                      "The voice is mostly clear; some ducking; close to 30 seconds",
                      "Ducking works, nothing clips; the file is within a second of 30",
                      "The voice sits clearly over smooth ducking, with headroom; exactly 30 seconds"]),
    ("Feedback & Reflection", ["Feedback or reflection missing", "Thin feedback; little to say about choices",
                               "A feedback sheet and a reflection, with basic detail", "Clear answers to the client and a thoughtful reflection",
                               "Insightful reflection and a change made because of the client’s feedback"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = [ds[4] for _, ds in RUBRIC]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.84
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches commercial music as a design problem with a client. Students learn to plan music to a clock (bars, beats and seconds), "
                 "build a loop from a chord progression, record and process a voice, and balance music and speech with ducking, then take a "
                 "client’s feedback and improve their work.")
STRUGGLES = ["The music does not add up to 30 seconds: start from the tempo table (page @PLAN) and use bars = BPM ÷ 8, then set the locators "
             "on the bar after the last one (page @BOUNCE).",
             "The voice is lost under the music: duck the music (page @DUCK), thin the layers while the voice speaks, and make sure the voice "
             "has a high-pass filter and a Compressor (page @VOICE).",
             "The script is too long to say clearly: count words and syllables (page @SCRIPT). More than 12 words, or more than about 8 "
             "syllables in one 2-second bar, will rush.",
             "The chord loop sounds wrong: check the Roman numerals and key on page @LOOP (a capital numeral is a major chord, a small one is "
             "minor), and make sure the Session Players follow the same chords."]
VAR_EASY = ("Offer brief C at 120 BPM (15 bars) with the I–V–vi–IV loop. Students use Drummer and Keyboard Player for the whole backing, write a "
            "script of 8 words, and duck by automation (volume points) instead of sidechain. Give a script starter if needed.")
VAR_HARD = ("Ask for two versions: the full 30-second ad and a 15-second cut-down at the same tempo, with the tagline kept. Or ask for a "
            "sung tagline instead of a spoken one, a key change into the tag, or a second voice. Students can design an audio logo of "
            "about 3 seconds from the hook.")
RESOURCES = [("Four client briefs and the brief card (page @BRIEF)",
              "Hand out the briefs first and let students choose. Each brief gives the product, audience, mood, tagline, two must-include sounds and tempo choices."),
             ("Tempo table, chord loops and the structure planner (pages @LOOP–@PLAN)",
              "The table of tempos that fit 30 seconds exactly, and five loops with their chords in seven keys. Demonstrate one example on the projector."),
             ("Logic recipes, script, voice and ducking pages (pages @BUILD–@DUCK)",
              "Settings are described in words, so they work in any current Logic Pro. Students adapt them by ear."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "An invented 30-second ad for Fluffwick Snug Wool Socks, planned on paper with its bar and time table, six layers, three voice lines and ducking numbers. Use it as a model, not a template.")]
TN_NOTE = ("Pairs well with a listening day: play the finished jingles without saying the product and ask the class what is being sold, who it is "
           "for and what the tagline was. A jingle the class can repeat after one listen is a jingle that works.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Brief & Concept (rubric row 1): read the brief card (page @BRIEF) and listen for the tagline, the product and both must-include sounds.",
           "Music & Structure (rubric row 2): compare the structure plan (page @PLAN) and the layer map (page @LAYERS) with the project: do the bars add up to 30 seconds, and do the sections enter where planned?",
           "Voice-over & Script (rubric row 3): check the script has 8 to 12 words and the tagline (page @SCRIPT), then listen for clear words, a clean recording and no harsh S sounds.",
           "Mix & Export (rubric row 4): listen for ducking, check nothing clips and check the file length in Finder. Feedback & Reflection (rubric row 5): the client feedback sheet (page @FEEDBACK) and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Choose a brief, plan the 30 seconds and pick a tempo, key and chord loop.",
     "do": "Slides 1–6: the hook, what the project is, the four classes, the five steps and the 30-second plan. Hand out the project sheet, "
           "the briefs, the loop page and the structure planner. Check that each student leaves with a brief, a tempo and bars that add up to 30 seconds.",
     "slides": (1, 6), "pages": ["brief", "loop", "plan", "proj1", "proj2", "proj3", "vocab"],
     "deck": "A 30-second ad · five steps · bars and seconds"},
    {"n": 2, "owner": "Build the music: loop, drums, bass, hook and the must-include sounds.",
     "do": "Slides 7–8: build the music and the chord loop. Demonstrate Drummer and the Chord Track on the projector, then work time. "
           "Walk the room with one question: what does this layer do, and where does it enter?",
     "slides": (7, 8), "pages": ["build", "layers"], "deck": "Build the music · the chord loop"},
    {"n": 3, "owner": "Write the script, record the voice-over, duck the music and mix.",
     "do": "Slides 9–11: the script, ducking and the voice chain. Count the words and syllables of one student script aloud together, then "
           "record. Demonstrate one ducking method, then hand out the bounce page.",
     "slides": (9, 11), "pages": ["script", "voice", "duck"], "deck": "A script that fits · ducking · the voice chain"},
    {"n": 4, "owner": "Bounce, hand in, get client feedback, present and reflect.",
     "do": "Slides 12–15: what to turn in, the rubric, client feedback and the close. Students bounce, check the length, name their files and "
           "write three questions for their client, then present.",
     "slides": (12, 15), "pages": ["bounce", "rubric", "feedback", "present"], "deck": "Checklist · rubric · client feedback"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:9.6pt">Make sure every student leaves with a brief, a tempo from the table (page @PLAN) and a plan whose bars '
    'add up to exactly 30 seconds. If the sums are wrong now, the whole jingle is wrong later: use bars = BPM ÷ 8.</p></div>'
    '<div class="box"><span class="k">If you only have three classes</span><p style="margin:0;font-size:9.6pt">Combine Classes 3 and 4: '
    'finish the music and write the script on Class 2, then record, duck, bounce, collect client feedback and reflect together in Class 3. Plan on a longer Class 3.</p></div></div>')
PACING_SIZE = 10.6


# ================================================================ drawings (waveforms, a speech bubble, lanes, cards; no notation)
def noise01(i):
    """A fixed pseudo-random value 0..1 for bar i (no random module: the artwork is the same on every build)."""
    v = math.sin(i * 12.9898 + 78.233) * 43758.5453
    return v - math.floor(v)


def env_at(u):
    """How full the music is 0..1 at position u (0..1) of the 30 seconds: intro, verse, hook, tag."""
    t = u * EX_BARS
    for nm, a, b in EX_SECTIONS:
        if a - 1 <= t < b:
            return {"Intro": .30, "Verse": .52, "Hook": 1.0, "Tag": .62}[nm] if not (nm == "Tag" and t > b - 1) else .40
    return .3


def time_x(t, gx, pw):
    return gx + pw * t / LEN_S


def hero_body():
    W = 1100
    out = []
    # the speech bubble with the tagline slot
    out.append('<path d="M400,214 L878,214 A72,72 0 0 0 950,142 L950,80 A72,72 0 0 0 878,8 L222,8 A72,72 0 0 0 150,80 L150,142 '
               'A72,72 0 0 0 222,214 L300,214 L262,290 Z" fill="#fff" stroke="#000" stroke-width="8" stroke-linejoin="round"/>')
    out.append(D.t_(550, 88, "30-SECOND AD", 38, 500))
    out.append(D.t_(550, 178, "YOUR TAGLINE", 88, 700, fill_=ACCENT))
    D.lab("hero", "30-SECOND AD", 38, 700)
    D.lab("hero", "YOUR TAGLINE", 88, 700)
    # the 30-second waveform
    n = 90
    gx, pw = 50, W - 100
    y0, hh = 470, 118
    bw = pw / n
    for i in range(n):
        u = (i + .5) / n
        a = env_at(u) * (.55 + .45 * noise01(i))
        h = max(6, a * hh)
        out.append(f'<rect x="{gx + i * bw + 1:.1f}" y="{y0 - h:.1f}" width="{max(2, bw - 2):.1f}" height="{2 * h:.1f}" rx="2" fill="#000"/>')
    out.append(f'<line x1="{gx}" y1="{y0}" x2="{gx + pw}" y2="{y0}" stroke="#000" stroke-width="2"/>')
    # the voice-over lane: three lines, as in the worked example
    vy = y0 + hh + 18
    for i in range(len(EX_VO)):
        t0, t1 = vo_span(i)
        x0, x1 = time_x(t0, gx, pw), time_x(t1, gx, pw)
        out.append(f'<rect x="{x0:.1f}" y="{vy}" width="{x1 - x0:.1f}" height="34" rx="10" fill="{ACCENT}"/>')
    # legend for the three red pills (the voice-over lines), set in the gap between the first and second pill
    gx0 = time_x(vo_span(0)[1], gx, pw)
    gx1 = time_x(vo_span(1)[0], gx, pw)
    out.append(D.t_((gx0 + gx1) / 2, vy + 27, "VOICE-OVER LINES", 32, 700, fill_=ACCENT))
    D.lab("hero", "VOICE-OVER LINES", 32, gx1 - gx0 - 40)
    # sections
    ty = vy + 34 + 56
    for nm, a, b in EX_SECTIONS:
        x0, x1 = time_x((a - 1) * EX_BAR_S, gx, pw), time_x(b * EX_BAR_S, gx, pw)
        out.append(f'<line x1="{x0 + 8:.1f}" y1="{ty - 30}" x2="{x1 - 8:.1f}" y2="{ty - 30}" stroke="{ACCENT if nm == "Hook" else "#000"}" stroke-width="6" stroke-linecap="round"/>')
        out.append(D.t_((x0 + x1) / 2, ty + 14, nm.upper(), 36, 700, fill_=ACCENT if nm == "Hook" else "#000"))
        D.lab("hero", nm.upper(), 36, x1 - x0 - 16)
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
    return cards_body([("Brief", "product + mood"), ("Plan", "30 s in bars"), ("Build", "loop · drums · hook"),
                       ("Voice", "script · record"), ("Mix", "duck · bounce")],
                      "Then get the client’s feedback and reflect", W, name, fs, cs)


SHADE = {"Intro": "#4a4a4a", "Verse": "#000", "Hook": None, "Tag": "#4a4a4a"}


def sec_fill(nm):
    return SHADE[nm] or ACCENT


def structure_body(W=1600, name="structure pic", fs=26, ts=20):
    """The worked example's 30 seconds: sections with bars and seconds, a bar ruler, the chord of each bar, the voice lines and a time ruler."""
    gx = 150
    pw = W - gx - 16
    X = lambda bar: gx + pw * (bar - 1) / EX_BARS
    out = []
    sh = 52
    for nm, a, b in EX_SECTIONS:
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b + 1) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{sec_fill(nm)}"/>')
        out.append(D.t_((X(a) + X(b + 1)) / 2, sh / 2 + fs * .3 + 2, nm.upper(), fs - 2, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 2, X(b + 1) - X(a) - 10)
        sub = f"bars {a}–{b} · {sec((b - a + 1) * EX_BAR_S)} s"
        out.append(D.t_((X(a) + X(b + 1)) / 2, sh + ts + 6, sub, ts - 2, 500))
        D.lab(name + " subs", sub, ts - 2, X(b + 1) - X(a) - 8)
    ry = sh + ts + 24
    chords = ex_chords()
    out.append(D.t_(gx - 12, ry + 24, "BAR", ts, 700, anchor="end", fill_=ACCENT))
    out.append(D.t_(gx - 12, ry + 24 + 46, "CHORD", ts, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " row names", "CHORD", ts, gx - 20)
    for bar in range(1, EX_BARS + 1):
        x0, x1 = X(bar), X(bar + 1)
        out.append(f'<rect x="{x0:.1f}" y="{ry}" width="{x1 - x0:.1f}" height="34" fill="#fff" stroke="#000" stroke-width="1.6"/>')
        out.append(D.t_((x0 + x1) / 2, ry + 24, str(bar), ts, 500))
        out.append(f'<rect x="{x0:.1f}" y="{ry + 46}" width="{x1 - x0:.1f}" height="38" fill="{ACC_LIGHT}" stroke="#000" stroke-width="1.6"/>')
        out.append(D.t_((x0 + x1) / 2, ry + 46 + 27, chords[bar - 1], ts + 2, 700))
        D.lab(name + " chords", chords[bar - 1], ts + 2, x1 - x0 - 6)
    vy = ry + 46 + 38 + 16
    out.append(D.t_(gx - 12, vy + 30, "VOICE", ts, 700, anchor="end", fill_=ACCENT))
    out.append(f'<rect x="{gx}" y="{vy}" width="{pw:.1f}" height="44" fill="#fff" stroke="#000" stroke-width="1.6"/>')
    for i in range(len(EX_VO)):
        t0, t1 = vo_span(i)
        x0, x1 = time_x(t0, gx, pw), time_x(t1, gx, pw)
        out.append(f'<rect x="{x0:.1f}" y="{vy + 5}" width="{x1 - x0:.1f}" height="34" rx="8" fill="{ACCENT}"/>')
        out.append(D.t_((x0 + x1) / 2, vy + 5 + 25, str(i + 1), ts, 700, fill_="#fff"))
    ty = vy + 44 + 8
    for bar in (1, 4, 7, 10, 13, 16):
        lbl = mmss(bar_time(bar)) if bar <= EX_BARS else mmss(EX_BARS * EX_BAR_S)
        anc = "start" if bar == 1 else ("end" if bar == 16 else "middle")
        xx = X(bar) if bar <= EX_BARS else gx + pw
        out.append(f'<line x1="{xx:.1f}" y1="{ty}" x2="{xx:.1f}" y2="{ty + 12}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(xx, ty + 12 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 70)
    cap = f"{EX_BARS} bars × {sec(EX_BAR_S)} seconds = {sec(EX_BARS * EX_BAR_S)} seconds at {EX_BPM} BPM · key of {EX_KEY}"
    out.append(D.t_(gx + pw / 2, ty + 12 + ts + 34, cap, ts + 2, 500))
    D.lab(name + " cap", cap, ts + 2, pw)
    return "".join(out), W, ty + 12 + ts + 48


def map_body(W=1250, name="map", fs=24, ts=20):
    """The worked example's whole arrangement: sections, six layers, the voice lines and the music-level (ducking) lane."""
    gx = 280
    pwid = W - gx - 16
    X = lambda bar: gx + pwid * (bar - 1) / EX_BARS
    out = []
    sh = 50
    for nm, a, b in EX_SECTIONS:
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b + 1) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{sec_fill(nm)}"/>')
        out.append(D.t_((X(a) + X(b + 1)) / 2, sh / 2 + fs * .3 + 2, nm.upper(), fs - 4, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 4, X(b + 1) - X(a) - 10)
    lh, lg = 30, 7
    y0 = sh + 14
    out.append(D.t_(gx - 14, y0 + 10, "LAYERS", fs - 6, 700, anchor="end", fill_=ACCENT))
    for i, (nm, spans, tool, _d) in enumerate(EX_LAYERS):
        yy = y0 + 18 + i * (lh + lg)
        lbl = f"{nm} · {tool}".upper()
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, lbl, 18, 700, anchor="end"))
        D.lab(name + " lanes", lbl, 18, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.4"/>')
        for a, b in spans:
            out.append(f'<rect x="{X(a):.1f}" y="{yy + 4}" width="{X(b + 1) - X(a):.1f}" height="{lh - 8}" rx="6" fill="#bdbdbd" stroke="#000" stroke-width="2"/>')
    vy = y0 + 18 + len(EX_LAYERS) * (lh + lg) + 14
    out.append(D.t_(gx - 14, vy + lh / 2 + 7, "VOICE-OVER", 18, 700, anchor="end", fill_=ACCENT))
    out.append(f'<rect x="{gx}" y="{vy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.4"/>')
    for i in range(len(EX_VO)):
        t0, t1 = vo_span(i)
        x0, x1 = time_x(t0, gx, pwid), time_x(t1, gx, pwid)
        out.append(f'<rect x="{x0:.1f}" y="{vy + 4}" width="{x1 - x0:.1f}" height="{lh - 8}" rx="6" fill="{ACCENT}"/>')
    my = vy + lh + 14
    mh = 70
    out.append(D.t_(gx - 14, my + 22, "MUSIC LEVEL", 18, 700, anchor="end", fill_=ACCENT))
    out.append(D.t_(gx - 14, my + 46, f"0 to −{EX_DUCK_DB} dB", 16, 500, anchor="end"))
    D.lab(name + " lanes", "MUSIC LEVEL", 18, gx - 24)
    out.append(f'<rect x="{gx}" y="{my}" width="{pwid:.1f}" height="{mh}" fill="#fff" stroke="#000" stroke-width="1.4"/>')
    pts = []
    for t, db in duck_points():
        pts.append((time_x(t, gx, pwid), my + 10 + (-db) / EX_DUCK_DB * (mh - 20)))
    out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{ACCENT}" stroke-width="4.5" stroke-linejoin="round"/>')
    ty = my + mh + 6
    for bar in (1, 4, 7, 10, 13, 16):
        lbl = mmss(bar_time(bar)) if bar <= EX_BARS else mmss(EX_BARS * EX_BAR_S)
        anc = "start" if bar == 1 else ("end" if bar == 16 else "middle")
        xx = X(bar) if bar <= EX_BARS else gx + pwid
        out.append(f'<line x1="{xx:.1f}" y1="{ty}" x2="{xx:.1f}" y2="{ty + 10}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(xx, ty + 10 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 70)
    cap = f"Bars 1 to {EX_BARS} at {EX_BPM} BPM: {EX_BARS} bars × {sec(EX_BAR_S)} seconds = {sec(EX_BARS * EX_BAR_S)} seconds"
    out.append(D.t_(gx + pwid / 2, ty + 10 + ts + 32, cap, ts + 2, 500))
    D.lab(name + " cap", cap, ts + 2, pwid)
    return "".join(out), W, ty + 10 + ts + 46


def duck_body(W=1600, name="duck pic", fs=24, ts=20):
    """Ducking: the voice lines on top, and the music level that dips under each one (from duck_points)."""
    gx = 150
    pw = W - gx - 16
    out = []
    vy = ts + 14
    out.append(D.t_(gx - 12, vy + 36, "VOICE", ts, 700, anchor="end", fill_=ACCENT))
    out.append(f'<rect x="{gx}" y="{vy}" width="{pw:.1f}" height="54" fill="#fff" stroke="#000" stroke-width="1.6"/>')
    for i in range(len(EX_VO)):
        t0, t1 = vo_span(i)
        x0, x1 = time_x(t0, gx, pw), time_x(t1, gx, pw)
        out.append(f'<rect x="{x0:.1f}" y="{vy + 6}" width="{x1 - x0:.1f}" height="42" rx="9" fill="{ACCENT}"/>')
        lbl = f"LINE {i + 1}"
        out.append(D.t_((x0 + x1) / 2, vy - 8, lbl, ts, 700))
        D.lab(name + " lines", lbl, ts, 100)
        D.span(name, "lines", lbl, ts, (x0 + x1) / 2, lo=0, hi=W)
    my = vy + 54 + 30
    mh = 230
    out.append(D.t_(gx - 12, my + mh / 2 + 8, "MUSIC", ts, 700, anchor="end", fill_=ACCENT))
    out.append(f'<rect x="{gx}" y="{my}" width="{pw:.1f}" height="{mh}" fill="#fff" stroke="#000" stroke-width="1.6"/>')
    top, bot = my + 34, my + mh - 34
    for db, lbl in ((0, "0 dB"), (-EX_DUCK_DB, f"−{EX_DUCK_DB} dB")):
        yy = top + (-db) / EX_DUCK_DB * (bot - top)
        out.append(f'<line x1="{gx}" y1="{yy:.1f}" x2="{gx + pw:.1f}" y2="{yy:.1f}" stroke="#9a9a9a" stroke-width="1.4" stroke-dasharray="7 6"/>')
        out.append(D.t_(gx - 12, yy + 7, lbl, ts, 700, anchor="end"))
        D.lab(name + " levels", lbl, ts, gx - 20)
    pts = [(time_x(t, gx, pw), top + (-db) / EX_DUCK_DB * (bot - top)) for t, db in duck_points()]
    poly = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    out.append(f'<polygon points="{gx:.1f},{my + mh} {poly} {gx + pw:.1f},{my + mh}" fill="{ACC_LIGHT}"/>')
    out.append(f'<polyline points="{poly}" fill="none" stroke="{ACCENT}" stroke-width="6" stroke-linejoin="round"/>')
    ty = my + mh + 8
    for t in range(0, LEN_S + 1, 6):
        lbl = mmss(t)
        anc = "start" if t == 0 else ("end" if t == LEN_S else "middle")
        xx = time_x(t, gx, pw)
        out.append(f'<line x1="{xx:.1f}" y1="{ty}" x2="{xx:.1f}" y2="{ty + 12}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(xx, ty + 12 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 70)
    cap = f"The music dips {EX_DUCK_DB} dB half a beat before each line and is back one beat after it ends"
    out.append(D.t_(gx + pw / 2, ty + 12 + ts + 34, cap, ts + 2, 500))
    D.lab(name + " cap", cap, ts + 2, pw)
    return "".join(out), W, ty + 12 + ts + 48


def loop_body(W=1600, name="loop pic", fs=40, ts=24):
    """The I–V–vi–IV loop as Roman numerals over its chords in C major and G major (computed from the scale)."""
    nums = LOOPS[0][1]
    keys = ["C", "G"]
    gx = 250
    gap = 22
    cw = (W - gx - 3 * gap) / 4
    out = []
    for k, nm in enumerate(nums):
        x0 = gx + k * (cw + gap)
        out.append(f'<rect x="{x0:.1f}" y="2" width="{cw:.1f}" height="76" rx="12" fill="#000"/>')
        out.append(D.t_(x0 + cw / 2, 2 + 54, nm, fs + 8, 700, fill_="#fff"))
        D.lab(name + " numerals", nm, fs + 8, cw - 20)
    for r, key in enumerate(keys):
        y = 96 + r * 112
        out.append(D.t_(gx - 18, y + 60, key_name(key).upper(), ts + 2, 700, anchor="end", fill_=ACCENT))
        D.lab(name + " keys", key_name(key).upper(), ts + 2, gx - 30)
        for k, ch in enumerate(chords_in(key, nums)):
            x0 = gx + k * (cw + gap)
            out.append(f'<rect x="{x0:.1f}" y="{y}" width="{cw:.1f}" height="92" rx="12" fill="{ACC_LIGHT}" stroke="#000" stroke-width="3"/>')
            out.append(D.t_(x0 + cw / 2, y + 64, ch, fs + 10, 700))
            D.lab(name + " chords", ch, fs + 10, cw - 20)
    cap = "A capital numeral is a major chord (I, IV, V). A small numeral is a minor chord (vi). One chord a bar, round and round."
    out.append(D.t_(W / 2, 96 + 2 * 112 + 22, cap, ts, 500))
    D.lab(name + " cap", cap, ts, W - 20)
    return "".join(out), W, 96 + 2 * 112 + 38


def script_body(W=1600, name="script pic", fs=34, ts=22):
    """The worked example's three voice lines as cards: where each starts, its words, syllables and seconds at 2.5 words a second."""
    n = len(EX_VO)
    gap = 36
    cw = (W - (n - 1) * gap) / n
    out = []
    for i, (bar, beat, text, sy) in enumerate(EX_VO):
        x0 = i * (cw + gap)
        t0, t1 = vo_span(i)
        out.append(f'<rect x="{x0:.1f}" y="4" width="{cw:.1f}" height="250" rx="14" fill="#fff" stroke="#000" stroke-width="3"/>')
        out.append(f'<rect x="{x0:.1f}" y="4" width="{cw:.1f}" height="62" rx="14" fill="{"#000" if i % 2 == 0 else ACCENT}"/>')
        hd = f"LINE {i + 1} · BAR {bar} · {sec(t0)} S"
        out.append(D.t_(x0 + cw / 2, 4 + 42, hd, ts + 2, 700, fill_="#fff"))
        D.lab(name + " heads", hd, ts + 2, cw - 24)
        q = "“" + text + "”"
        out.append(D.t_(x0 + cw / 2, 4 + 62 + 66, q, fs, 500))
        D.lab(name + " text", q, fs, cw - 24)
        st = f"{len(words_of(text))} words · {sy} syllables"
        out.append(D.t_(x0 + cw / 2, 4 + 62 + 66 + 56, st, ts + 2, 700))
        D.lab(name + " stats", st, ts + 2, cw - 24)
        tm = f"{len(words_of(text))} ÷ {EX_WPS:g} = {sec(len(words_of(text)) / EX_WPS)} s"
        out.append(D.t_(x0 + cw / 2, 4 + 62 + 66 + 56 + 42, tm, ts + 2, 500))
        D.lab(name + " time", tm, ts + 2, cw - 24)
    cap = f"{sum(len(words_of(v[2])) for v in EX_VO)} words in all, about {sec(sum(len(words_of(v[2])) for v in EX_VO) / EX_WPS)} seconds of speech in a 30-second ad"
    out.append(D.t_(W / 2, 4 + 250 + 46, cap, ts + 4, 500))
    D.lab(name + " cap", cap, ts + 4, W - 20)
    return "".join(out), W, 4 + 250 + 64


DRAWINGS = {"hero": hero_body, "cycle": lambda: cycle_body(1600), "structure": lambda: structure_body(1600, "structure deck"),
            "loop": lambda: loop_body(1600, "loop deck"), "script": lambda: script_body(1600, "script deck"),
            "duck": lambda: duck_body(1600, "duck deck")}
DRAWING_PX = {"hero": 1900, "cycle": 2000, "structure": 2000, "loop": 2000, "script": 2000, "duck": 2000}
SIDE = {"cycle": ["Choose a brief and plan in bars", "Build the music, then the voice", "Mix last: duck and bounce", "A client gives feedback"],
        "structure": ["Four sections: 2, 4, 6 and 3 bars", "Bars × 2 seconds at 120 BPM", "15 bars = exactly 30 seconds", "Voice lines sit in the gaps"],
        "loop": ["One chord a bar, four bars", "Same numerals, any key", "Capital = major, small = minor", "Session Players follow the chords"],
        "script": ["8 to 12 words, tagline last", "About 2 to 3 words a second", "Count syllables too", "Each line fits its bar"],
        "duck": ["Voice speaks, music dips", "About 4 to 6 dB is enough", "Sidechain or draw it", "Back up a beat later"]}


def label_extras():
    structure_body(1250, "page structure", 24, 19)
    map_body(1250, "page map", 24, 20)
    duck_body(1250, "page duck", 22, 18)
    loop_body(1250, "page loop", 34, 20)
    cycle_body(1250, "page cycle", 28, 20)
    script_body(1250, "page script", 30, 19)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Commercial Jingle", "A 30-second ad, from a client brief.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: each student is a jingle writer, and a client has "
     "hired them to sell a product that does not exist. They will plan 30 seconds in bars, build the music in Logic Pro, record a short "
     "voice-over and mix the two so every word can be heard. Hand out the project sheet and the four client briefs at the end of this class."),
    (1, "listen", "Think: what makes a jingle stick?", "Think, then share · Teacher: ask who can hum an ad tune, without naming the brand|"
     "Take three answers, then ask the questions below.|Why does a short tune stay in your head?|What did the ad want you to remember?|"
     "Who was it made for, and how did it feel?",
     "Ask for a show of hands: who can hum an ad tune right now? Do not let anyone name the brand or sing the words; humming is enough. "
     "Then ask the three questions aloud and take a few answers. Students will say it was short, it repeated and it was easy to sing. "
     "Write their words on the board; the project turns each one into a tool: a loop, a hook and a tagline."),
    (1, "bullets", "What is Commercial Jingle?", "Make a 30-second ad for an invented product|Plan in bars, then build the music in Logic Pro|"
     "Record a voice-over and duck the music under it|Bounce exactly 30 seconds, then ask your client",
     "The project in four lines. Students choose a client brief, plan 30 seconds in bars, build the music, write and record an 8 to 12 word "
     "voice-over, and duck the music under it so every word can be heard. The finished file is exactly 30 seconds. There is no audio in this "
     "kit and no melody is supplied: every sound and every tune is the students' own, and every product is invented."),
    (1, "days", "Four classes", "",
     "The shape of the project. Class 1: hook, choose a brief and plan the 30 seconds. Class 2: build the music with Drummer, Session Players, "
     "Alchemy, Quick Sampler and loops. Class 3: write the script, record, duck and mix. Class 4: bounce, hand in, collect client feedback, "
     "present and reflect. Hand out the project sheet, the briefs and the structure planner now."),
    (1, "pic", "Five steps, then finish", "cycle",
     "Class 1. The five steps in order: brief, plan, build, voice and mix. After that students get the client's feedback and reflect. Point to "
     "each box and say roughly when it happens: the brief and the plan today, the music on Class 2, the voice and the mix on Class 3. The "
     "picture and its short labels are drawn for this kit."),
    (1, "pic", "The 30-second plan", "structure",
     f"Class 1. This is the worked example for an invented client, Fluffwick Snug Wool Socks: 15 bars at 120 BPM. A bar of 4/4 lasts 4 beats of "
     f"0.5 seconds, so 2 seconds, and 15 bars is exactly 30 seconds. The sections are 2, 4, 6 and 3 bars. The numbered boxes are the three "
     f"voice lines. Students plan their own on page {pg('plan')}, using bars = BPM ÷ 8."),
    (2, "steps", "Build the music", "Set the tempo and write your chord loop|Add Drummer, then a bass and a keyboard player|Make the hook "
     "in Alchemy or Retro Synth|Record your must-include sound in Quick Sampler|Add one layer at a time and listen",
     f"Class 2. Demonstrate on the projector: set the tempo from the table, type the four chords of the loop into the Chord Track if your "
     f"version has it, add a Drummer track and move the puck on the XY pad. Then show a Bass Player or Keyboard Player following the chords. "
     f"Recipes are on page {pg('build')}. Menu names move between Logic versions, so describe the action, not the path."),
    (2, "pic", "The chord loop", "loop",
     f"Class 2. The same four numerals give the same sound in any key: I, V, vi and IV in C major are C, G, A minor and F, and in G major they "
     f"are G, D, E minor and C. A capital numeral is a major chord and a small one is minor. One chord a bar, four bars, then round again. "
     f"Students choose a loop and a key on page {pg('loop')} and write out their four chords before they open Logic."),
    (3, "pic", "A script that fits", "script",
     f"Class 3. A script of 8 to 12 words, ending with the tagline. Each line is checked three ways: its words, its syllables, and the seconds "
     f"it needs at about 2.5 words a second. These three lines are 4 words each, so each fits in one 2-second bar. Students count their own "
     f"words and syllables on page {pg('script')}; more than 12 words will rush."),
    (3, "pic", "Ducking: music out of the way", "duck",
     f"Class 3. Ducking turns the music down while the voice speaks and back up afterwards. The colored lines on top are the voice; the line "
     f"below is the music's level. Show one method on the projector: insert Compressor on the music and choose the voice track in its Side Chain "
     f"menu, or press A and draw the dips by hand. Both methods are on page {pg('duck')}."),
    (3, "bullets", "The voice chain", "Channel EQ: cut the lows of the voice|Compressor: even out loud and quiet words|"
     "DeEsser 2: soften harsh S sounds|Duck the music while the voice speaks",
     f"Class 3. Four steps to a clean voice, in order. Channel EQ's high-pass filter removes room rumble and breath. Compressor evens out loud "
     f"and quiet words. DeEsser 2 softens sharp S and T sounds. Then the music ducks under the voice. Record at least three takes first; the "
     f"recording steps are on page {pg('voice')}. Remind students to keep headphones on while recording."),
    (4, "check", "What you turn in", "Bounced file of 30 seconds|Zipped .logicx project|Named: Your Name – Jingle – Product|"
     "Brief card, plan and layer map|Feedback sheet and rubric score|Three questions for your client",
     f"Class 4. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, Jingle, then the "
     f"product, in that order. Before students bounce, remind them to set the end locator on the bar after the last one (page {pg('bounce')}) and "
     f"to check the file's length in Finder."),
    (4, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average "
     "of their score and yours. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score "
     "before they present."),
    (4, "bullets", "Presentation day", "Play your jingle for a classmate who is your client|The client fills in the feedback sheet|"
     "Answer at least 2 of each classmate’s questions|Say one change you will make",
     f"Class 4, presentations. Each student plays their jingle for a classmate who acts as their client; the client fills in the feedback sheet on "
     f"page {pg('feedback')}. Students write three questions they want their client to answer, and answer at least two of each classmate's. "
     f"Ask the class what is being sold and what the tagline was before the writer says."),
    (4, "closer", "One last thing…", "You planned the bars.|You wrote the hook.|You found the voice.|Now press play.",
     "Close with a listening day: play the finished jingles without naming the product and let the class say what is being sold, who it is "
     "for and what the tagline was. Ask a few students which choice made the biggest difference, the loop, the voice or the ducking. No "
     "audio is included in this kit; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "4 class periods, slide by slide"), ("brief", "Client briefs", "four invented products"),
          ("script", "Script check", "words, syllables, seconds")]
SHOTS2 = [1, 5, 6, 8, 9, 10]
SHOTS3 = [("brief", "Client briefs"), ("loop", "Chord loops"), ("plan", "30-second plan"), ("build", "Logic recipes"),
          ("duck", "Ducking"), ("bounce", "Exact export"), ("example", "Worked example"), ("rubric", "Rubric / 25")]
PREVIEW_PICKS = ["pacing", "example", "duck", "rubric"]

COVER_A = "A winter ad for an invented product"
COVER_C = "Logic Pro · voice-over · ducking · intro slides"
PDF_COVER = dict(a=26, b=58, c=14, art=7.3)
SQ_COVER = dict(a=38, b=140, c=27, art=690, gap=30)
SQ_B_LINES = ["Commercial", "Jingle"]
SQ_SUB = "4 class periods · client briefs · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, briefs, recipes, a worked example and a /25 rubric", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Briefs, chord loops, script check, voice-over, ducking, export", 28)}
SQ_BANDS = {1: "Brief <em>·</em> plan <em>·</em> build <em>·</em> voice-over <em>·</em> mix",
            2: "30 seconds <em>·</em> chord loops <em>·</em> script timing <em>·</em> ducking",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, recordings, loops, lyrics, jingles, artists or brands are named or included, and no melody is supplied. Students "
             "write every tune and every word themselves, from the instruments, samplers and plug-ins in Logic Pro. Every client, product and "
             "tagline is invented.")
CREDITS = ["The four client briefs, chord-loop tables, Logic recipes, script and timing checks, ducking guide, worked example, the hero, card, lane "
           "and ducking drawings and all layouts: original work, Hudson Beat. No recordings, loops, presets or published material are included.",
           "No audio, video, album art, screenshots, presets, templates, links or chart data are included. No student work is included."]
LOGIC_INTRO = ("Where to find the tools a jingle is likely to use. Demonstrate what your class needs on Classes 1 to 3 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add tracks with Track › New Tracks… (Software Instrument, Audio, Drummer). Name every track so your layer map matches (page " + str(pg("layers")) + ")."),
             ("Tempo and the ruler", "Type the tempo in the control bar (double-click it) and keep 4/4. Bars = BPM ÷ 8 for 30 seconds (page " + str(pg("plan")) + "). "
              "The position display can show bars and beats or minutes and seconds."),
             ("Chord Track", "Show the global tracks (G) and add the Chord Track, if your version has it, then enter your four chords. Session Players and "
              "some loops follow it. Without it, play the chords yourself or draw them in the Piano Roll."),
             ("Drummer and Session Players", "Add a Drummer track, choose a drummer whose style fits the mood and move the puck on its XY pad: right is louder, up is busier. "
              "If your version has Session Players, add a Bass Player and a Keyboard Player (page " + str(pg("build")) + ")."),
             ("Alchemy and Retro Synth", "Click the instrument slot on a channel strip and choose Alchemy or Retro Synth. Browse the Library (Y) for a pluck, bell or bass "
              "as a starting point and change the filter and effects."),
             ("Quick Sampler", "Choose Quick Sampler as the instrument and use its record function to capture a sound from your microphone, "
              "such as a mug clink or a snap. Shorten it, set its pitch and play it from the keyboard or draw notes."),
             ("Loop Browser", "Press O to open it. Search by mood or instrument, and drag a loop into the project. Loops follow the project tempo; "
              "check that the key fits your chords."),
             ("Recording the voice", "Add an Audio track, choose your microphone as its input, click the track’s R button to record-enable it and press the Record button. "
              "Wear headphones so the music does not leak into the microphone."),
             ("Channel EQ, Compressor, DeEsser 2", "Insert them on the voice track in that order (page " + str(pg("voice")) + "). Turn the lowest band of Channel EQ into a high-pass filter; "
              "DeEsser 2 softens harsh S sounds."),
             ("Ducking", "Either insert Compressor on the music and pick the voice track in its Side Chain menu, or press A and draw volume points on the music "
              "(page " + str(pg("duck")) + ")."),
             ("Bounce", "Turn Cycle on (C) and set it from bar 1 to the bar after your last one. File › Bounce › Project or Section (Command-B), WAV or MP3. "
              "Check the length in Finder (page " + str(pg("bounce")) + ").")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .wav or .mp3 and zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for my client written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my jingle:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12.4pt;margin-bottom:4pt">Not 30 seconds: the tempo table (page @PLAN) and the end-locator table (page @BOUNCE).</li>'
    '<li style="font-size:12.4pt;margin-bottom:4pt">A lost voice: the voice chain (page @VOICE), the ducking page (page @DUCK) and slides 10–11.</li>'
    '<li style="font-size:12.4pt;margin-bottom:4pt">A script that rushes: the word, syllable and seconds check (page @SCRIPT) and slide 9.</li>'
    '<li style="font-size:12.4pt;margin-bottom:0">A wrong-sounding loop: the Roman numeral tables (page @LOOP) and slide 8.</li></ul></div>')
TN1_SIZE = 12.8
PROJ_SIZE = 11.8
VOCAB_GAP = 7
LOGIC_SIZE = 10.4
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""

CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; table-layout: fixed; } table.sg td, table.sg th { border: 1.25pt solid #000; text-align: center; "
          "padding: 0; font-size: 8pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.2in; font-size: 9pt; } "
          "table.sg td.b { border-left: 2.5pt solid #000; } </style>")


def chord_str(key, nums):
    return " ".join(chords_in(key, nums))


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, worked example (2 pages)"),
             ("Student pages", "brief", "reflect", "Client briefs, chord loops, 30-second plan, Logic recipes, layer map, script check, voice-over, ducking, "
              "export, project sheet (3 pages), rubric, vocabulary, client feedback sheet, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:11.6pt;line-height:1.42">A {CLASSES}-class-period commercial music project for high school music technology. Each '
             f'student is a jingle writer. A client, an invented product with a brief, needs a 30-second ad: students plan it in bars, pick a '
             f'tempo, key and chord loop, build the music in Logic Pro, write and record an 8 to 12 word voice-over, duck the music under it, '
             f'and bounce exactly 30 seconds. A classmate acts as the client and gives feedback. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look through the client briefs (page {D.IX("brief")}) and the worked example (pages {D.IX("example")}–{D.IX("example2")}), and check the setup (page {D.IX("setup")}).</li>'
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
             f'<li><b>Own product:</b> students may invent a product with your approval; it needs a name, an audience, a mood, a tagline and two sounds.</li>'
             f'<li><b>No microphone?</b> The Mac’s built-in microphone works; see the setup page ({D.IX("setup")}).</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that a jingle '
             f'is planned to a clock: bars become seconds, a loop becomes a hook, and ducking lets music and voice share 30 seconds.</p></div>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Commercial music · Logic Pro<br>Write a 30-second ad for an invented product, with a voice-over.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12.4pt;line-height:1.45">One original jingle of exactly 30 seconds for one of four invented clients. It has a chord loop in a '
             f'chosen key and tempo, at least four layers (made with Drummer or a Session Player and at least one of Alchemy, Retro Synth or Quick Sampler), '
             f'both must-include sounds, an 8 to 12 word voice-over that ends with the tagline, and a mix in which the music ducks under the voice. '
             f'Students hand in a bounced .wav or .mp3 and the zipped .logicx project, plus their plans, a client feedback sheet and a reflection.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12.6pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.6pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12.6pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.4pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}, music technology, music production or media music</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods (3 or 4 classes work: see page {D.IX("pacing")}): choose and plan, build the music, write and record, bounce and present</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Drummer, Session Players, Alchemy, Retro Synth, Quick Sampler, Loop Browser, Channel EQ, Compressor, DeEsser 2, automation, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a quiet corner for recording, a place to hand in files</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>Rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s and the '
             f'teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:11pt">Students should know how '
             f'to open a project, add a software instrument and an audio track and use the mixer in Logic. Nobody needs to read music: '
             f'Drummer and the Session Players can play the backing, and the chord tables name every chord.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Commercial music project", inner, n, key="overview")


def setup_page(n, wm=False):
    chk_items = ["Decide which briefs you will offer (page @BRIEF).",
                 "Open Logic Pro on a student computer: can you add a Drummer track, an Audio track and a Quick Sampler track, and hear them through headphones?",
                 "Test the microphone: record two words, play them back, and find a quiet place for recording (a practice room, a closet or a corner).",
                 "Read the worked example (pages @EXAMPLE–@EXAMPLE2)."]
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.8pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Headphones matter: they keep the music out of the voice recording.</li>'
             f'<li><b>A microphone</b> for the voice-over. The Mac’s built-in microphone works; a USB microphone is better. A quiet corner helps more than a better microphone.</li>'
             f'<li><b>A place to hand in</b> the .wav or .mp3, the zipped .logicx and the reflection.</li>'
             f'<li><b>The client briefs</b>, printed (page {D.IX("brief")}), or shown on the projector.</li>'
             f'<li><b>The recipes, script, voice, ducking and bounce pages</b>, printed (pages {D.IX("build")}–{D.IX("bounce")}).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("brief")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(D.fill(c) if "@" in c else c, 13, "font-size:11.8pt;margin-bottom:7pt") for c in chk_items) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.6pt">Students build a jingle that is 28 or 33 seconds long, write a script too long to say clearly, bury the voice under the music, '
             f'or crush the mix.</p><p style="font-size:11.6pt"><b>Try this:</b> {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.4pt">Ask while students work: what does this layer do? Where does the voice start? What does the client want to remember?</li>'
             f'<li style="font-size:11.4pt">Recording needs quiet. Stagger it: half the class records while the other half edits, then swap.</li>'
             f'<li style="font-size:11.4pt">A student who is stuck can start from a Drummer track and a Keyboard Player and change only the chords and the hook.</li></ul></div>'
             f'{D.H2("Originality and voices")}'
             f'<div class="box"><span class="k">Everything is original</span><p style="margin:0;font-size:11.2pt;line-height:1.4">'
             f'Students write their own tune and words. No real jingle, song, slogan or brand is used or imitated, and every product in this kit is invented. '
             f'Students record their own voice or a classmate who agrees; nobody imitates a real person. The season is winter and secular: no carols or holiday songs.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.2pt;line-height:1.4">'
             f'Voices and loud hooks are tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


EX_MOMENTS = [(3, "the verse: drums, bass and the first voice line"), (7, "the hook: the pluck and the snap enter"),
              (11, "the second voice line names the product"), (13, "the tag: the tagline is spoken"), (15, "the final sting")]


def example_page(n, wm=False):
    secs = "".join(f"<tr><td style='width:11%'><b>{nm}</b></td><td style='white-space:nowrap'>bars {a}–{b}</td>"
                   f"<td style='white-space:nowrap'>{b - a + 1} × {sec(EX_BAR_S)} = {sec((b - a + 1) * EX_BAR_S)} s</td>"
                   f"<td style='white-space:nowrap'>{mmss(bar_time(a))}–{mmss(bar_time(b + 1))}</td><td>{EX_JOBS[nm]}</td></tr>" for nm, a, b in EX_SECTIONS)
    mom = "".join(f"<tr><td style='width:14%'>bar {b}</td><td style='width:12%'>{mmss(bar_time(b))}</td><td>{t}</td></tr>" for b, t in EX_MOMENTS)
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">An <b>invented plan on paper</b>: a 30-second ad for {EX_PRODUCT}, for {EX_AUDIENCE.lower()}, '
             f'mood {EX_MOOD.lower()}, tagline “{EX_TAGLINE}”, must include {EX_SOUNDS[0]} and {EX_SOUNDS[1]}. {EX_NOTE} Page 1 of 2: the plan and the numbers.</p>'
             f'<div class="cols" style="gap:10pt"><div class="box" style="align-self:flex-start"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10pt">{EX_WEAK}</p>'
             f'<p style="margin:2pt 0 0;font-size:9pt">It names no tempo, key, loop, sections or script, and nothing says it is 30 seconds.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The 30 seconds: 15 bars, four sections")}'
             f'<div style="width:7.4in;margin:1pt auto 2pt">{D.body_svg(structure_body(1250, "page structure", 24, 19))}</div>'
             f'{D.H2("4 · Sections, bars and seconds")}'
             f'<table class="t" style="font-size:8.8pt;line-height:1.2"><tr><th>Section</th><th>Bars</th><th>Length</th><th>Time</th><th>What the listener hears</th></tr>{secs}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:3pt"><div><span class="k" style="font-size:9.4pt">5 · Moments</span>'
             f'<table class="t" style="font-size:8.6pt;line-height:1.18;margin-top:2pt">{mom}</table></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;align-self:flex-start"><span class="k">6 · Checking the numbers</span><p style="margin:0;font-size:8.8pt;line-height:1.3">'
             f'One bar of 4/4 at {EX_BPM} BPM lasts 240 ÷ {EX_BPM} = {sec(EX_BAR_S)} seconds, so {EX_BARS} bars = {sec(EX_BARS * EX_BAR_S)} seconds, and bars = {EX_BPM} ÷ 8 = {EX_BARS}. '
             f'The sections are {" + ".join(str(b - a + 1) for _, a, b in EX_SECTIONS)} bars = {EX_BARS}. '
             f'Time at a bar = (bar − 1) × {sec(EX_BAR_S)}, so bar 13 starts at {mmss(bar_time(13))}. The loop I–V–vi–IV in G is {chord_str(EX_KEY, EX_LOOP)}.</p></div></div>')
    return D.page("Worked example · an invented ad", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    lay = "".join(f"<tr><td style='width:14%'><b>{nm}</b></td><td style='width:16%'>{tool}</td><td style='width:12%;white-space:nowrap'>bars "
                  + ", ".join(f"{a}–{b}" if a != b else f"{a}" for a, b in spans) + f"</td><td>{d}</td></tr>" for nm, spans, tool, d in EX_LAYERS)
    vo = ""
    for i, (bar, beat, text, sy) in enumerate(EX_VO):
        t0, t1 = vo_span(i)
        w = len(words_of(text))
        vo += (f"<tr><td>{i + 1}</td><td>{text}</td><td>{w}</td><td>{sy}</td><td style='white-space:nowrap'>bar {bar}, beat {beat} = {sec(t0)} s</td>"
               f"<td style='white-space:nowrap'>{w} ÷ {EX_WPS:g} = {sec(w / EX_WPS)} s</td><td>{sec(t1)} s</td></tr>")
    dk = ""
    for i in range(len(EX_VO)):
        t0, t1 = vo_span(i)
        dk += (f"<tr><td>{i + 1}</td><td>{sec(t0 - EX_DUCK_LEAD)} s</td><td>{sec(t0)}–{sec(t1)} s</td><td>{sec(t1 + EX_DUCK_TAIL)} s</td></tr>")
    tw = sum(len(words_of(v[2])) for v in EX_VO)
    ts_ = sum(v[3] for v in EX_VO)
    top = max(EX_DENS)
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same ad, page 2 of 2: the map of the whole piece, then the layers, the script and the ducking.</p>'
             f'{D.H2("7 · The map: 0:30, four sections, six layers, the voice and the music level")}'
             f'<div style="width:7.4in;margin:1pt auto 3pt">{D.body_svg(map_body(1250, "page map", 24, 20))}</div>'
             f'<span class="k" style="font-size:9.4pt;display:block">8 · Layers (bars they play, tool and job)</span>'
             f'<table class="t" style="font-size:8.2pt;line-height:1.15;margin-top:2pt"><tr><th>Layer</th><th>Tool</th><th>Bars</th><th>What it does</th></tr>{lay}</table>'
             f'<span class="k" style="font-size:9.4pt;display:block;margin-top:2pt">9 · The script (invented)</span>'
             f'<table class="t" style="font-size:8.2pt;line-height:1.15;margin-top:2pt"><tr><th>Line</th><th>Words spoken</th><th>Words</th><th>Syllables</th><th>Starts</th><th>Time at {EX_WPS:g} words a second</th><th>Ends</th></tr>{vo}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:3pt"><div><span class="k" style="font-size:9.4pt">10 · Ducking points</span>'
             f'<table class="t" style="font-size:8.6pt;line-height:1.2;margin-top:2pt;table-layout:fixed"><tr><th>Line</th><th>Dip starts</th><th>Voice</th><th>Back to full</th></tr>{dk}</table></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;align-self:flex-start"><span class="k">11 · Checking the numbers</span><p style="margin:0;font-size:9pt;line-height:1.28">'
             f'{tw} words, {ts_} syllables: inside 8 to 12 words. Each line has 4 words, so at 2 words a second it needs 2 s, one bar. The hook (bars 7–10) has {top} layers, the most. '
             f'The music dips {EX_DUCK_DB} dB half a beat ({sec(EX_DUCK_LEAD)} s) before each line and returns one beat ({sec(EX_DUCK_TAIL)} s) after it. '
             f'<b>Three client questions (invented):</b> {qs}</p></div></div>')
    return D.page("Worked example · the map", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


def tempo_rows():
    rows = ""
    for b in FIT_PICK:
        nb = bars_in_30(b)
        rows += (f"<tr><td><b>{b}</b></td><td>{sec3(60 / b)} s</td><td>{sec3(bar_s(b))} s</td><td><b>{nb}</b></td><td>{nb} × 240 ÷ {b} = {sec(float(nb * 240 / b))} s</td></tr>")
    return rows


def brief_page(n, wm=False):
    rows = ""
    for b in BRIEFS:
        bs = " or ".join(f"{t} ({bars_in_30(t)} bars)" for t in b["bpms"])
        rows += (f"<tr><td style='width:5%;text-align:center'><b>{b['k']}</b></td>"
                 f"<td style='width:25%'><b>{b['product']}</b><br>{b['what']}</td><td style='width:18%'>{b['audience']}<br><i>{b['mood']}</i></td>"
                 f"<td style='width:17%'><b>“{b['tagline']}”</b></td><td style='width:17%'>{b['sounds'][0]}<br>{b['sounds'][1]}</td><td>{bs}</td></tr>")
    inner = (f'<p style="margin:0 0 4pt;font-size:11pt;line-height:1.4">Four invented clients each need a <b>30-second</b> radio ad for the winter season. '
             f'You write the jingle and record the voice-over. Choose one brief (or invent a product with your teacher’s approval: a name, an audience, a mood, '
             f'a tagline and two sounds). The tagline must be spoken in your script. Every product here is made up.</p>'
             f'<table class="t" style="font-size:9.6pt"><tr><th>#</th><th>Product</th><th>Audience · mood</th><th>Tagline to speak</th><th>Must include</th><th>Tempo choices</th></tr>{rows}</table>'
             f'<div class="box acc-b" style="margin:5pt 0 4pt"><span class="k">My brief card</span>'
             f'<div class="fl" style="margin:3pt 0 7pt"><b>My brief (A to D) and product:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 7pt"><b>Audience:</b><span></span><b>Mood in three words:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 7pt"><b>The tagline I must speak:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 7pt"><b>My two must-include sounds:</b><span></span><span></span></div>'
             f'<div class="fl" style="margin:0 0 7pt"><b>My tempo:</b><span style="flex:0 0 0.7in"></span><b>BPM, so</b><span style="flex:0 0 0.7in"></span><b>bars (BPM ÷ 8)</b>'
             f'<b style="margin-left:8pt">My key and loop:</b><span></span></div>'
             f'<div class="fl" style="margin:0"><b>What I want the listener to remember:</b><span></span></div></div>'
             f'<div class="cols" style="gap:12pt"><div class="box"><span class="k">Rules of the brief</span><ul style="margin:0;font-size:10pt">'
             f'<li style="font-size:10pt">Exactly 30 seconds, set by your tempo and bars (page {D.IX("plan")}).</li>'
             f'<li style="font-size:10pt">A script of 8 to 12 words that ends with the tagline (page {D.IX("script")}).</li>'
             f'<li style="font-size:10pt">At least four layers, with both must-include sounds in the music.</li>'
             f'<li style="font-size:10pt">Original tune and words: no real jingle, slogan or brand, and no imitation of real people.</li></ul></div>'
             f'<div class="box"><span class="k">Listen first</span><p style="margin:0;font-size:10pt;line-height:1.35">'
             f'Imagine your client’s ad on the radio. Who is listening, and where? What is the first sound they hear? What word must they remember after one play? '
             f'Write one sound or idea for each question on the lines below.</p></div></div>'
             f'<div class="ln2" style="height:19pt;margin-top:0"></div><div class="ln2" style="height:19pt"></div>')
    return D.page("Client briefs", "STUDENT", "Class 1", inner, n, wm, name=True, key="brief")


def loop_page(n, wm=False):
    mrows = ""
    for nm, nums, minor, feel, fits in LOOPS:
        if minor:
            continue
        mrows += f"<tr><td><b>{nm}</b></td><td>{feel}<br><span class='small'>{fits}</span></td>" + "".join(f"<td>{chord_str(k, nums)}</td>" for k in MAJOR_KEYS) + "</tr>"
    nm, nums, _m, feel, fits = LOOPS[4]
    mn = f"<tr><td><b>{nm}</b></td><td>{feel}<br><span class='small'>{fits}</span></td>" + "".join(f"<td>{chord_str(k, nums)}</td>" for k in MINOR_KEYS) + "</tr>"
    fit_rows = ""
    for b in FIT_PICK:
        nb = int(bars_in_30(b))
        fit_rows += f"<tr><td><b>{b}</b></td><td>{nb}</td><td>{nb // 4}</td><td>{nb % 4}</td></tr>"
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.38">A <b>chord progression</b> is a short pattern of chords that repeats. Producers write it with '
             f'<b>Roman numerals</b> so it works in any key. A <b>capital</b> numeral is a <b>major</b> chord (I, IV, V); a <b>small</b> numeral is a <b>minor</b> chord (ii, vi). '
             f'In C major, I = C, ii = Dm, iii = Em, IV = F, V = G and vi = Am. The loop <b>I–V–vi–IV</b> in C is <b>C G Am F</b>.</p>'
             f'<div style="margin:2pt 0 4pt">{D.body_svg(loop_body(1250, "page loop", 34, 20))}</div>'
             f'<span class="k">Major-key loops (one chord a bar)</span>'
             f'<table class="t" style="font-size:9.6pt"><tr><th style="width:14%">Loop</th><th style="width:30%">Feel · fits</th>' + "".join(f"<th>{k} major</th>" for k in MAJOR_KEYS) + f'</tr>{mrows}</table>'
             f'<span class="k" style="margin-top:3pt">A minor-key loop (small numerals are minor chords)</span>'
             f'<table class="t" style="font-size:9.6pt"><tr><th style="width:14%">Loop</th><th style="width:30%">Feel · fits</th>' + "".join(f"<th>{key_name(k)}</th>" for k in MINOR_KEYS) + f'</tr>{mn}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:3pt"><div><span class="k">How a 4-bar loop fits 30 seconds</span>'
             f'<table class="t" style="font-size:9pt;margin-top:2pt;table-layout:fixed"><tr><th>BPM</th><th>Bars</th><th>Full loops</th><th>Bars left</th></tr>{fit_rows}</table></div>'
             f'<div class="box acc-b" style="padding:5pt 10pt"><span class="k">My loop</span>'
             f'<div class="fl" style="margin:3pt 0 5pt"><b>Key:</b><span></span><b>Loop:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 5pt"><b>Chords, bar by bar:</b><span></span></div>'
             f'<p style="margin:0;font-size:9.4pt;line-height:1.3">Bars left over become the tag. Walk home with IV, V, I, or just hold I, and end on the I chord so the jingle sounds finished.</p></div></div>')
    return D.page("Tempo, key and chord loop", "STUDENT", "Class 1", inner, n, wm, name=True, key="loop")


def plan_page(n, wm=False):
    secs = "".join("<tr>" + f"<td style='height:30pt'><b>{nm}</b></td>" + "<td></td>" * 5 + "</tr>" for nm in ("Intro", "Verse", "Hook", "Tag"))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 2: plan exactly 30 seconds. One bar of 4/4 has 4 beats and lasts <b>240 ÷ BPM</b> seconds, '
             f'so <b>bars in 30 seconds = BPM ÷ 8</b>. Only tempos that divide by 8 give a whole number of bars. Pick one from the table, then decide how many bars each section gets. '
             f'Compare your plan with the worked example (page {D.IX("example")}).</p>'
             f'<table class="t" style="font-size:9.6pt;table-layout:fixed"><tr><th>Tempo (BPM)</th><th>One beat</th><th>One bar</th><th>Bars in 30 s</th><th>Check: bars × 240 ÷ BPM</th></tr>{tempo_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 4pt">Beats and bars are rounded to 3 decimal places; the last column is exact.</p>'
             f'<div class="fl" style="margin:0 0 4pt"><b>My tempo:</b><span style="flex:0 0 0.7in"></span><b>BPM. Bars = tempo ÷ 8 =</b><span style="flex:0 0 0.7in"></span>'
             f'<b>bars. One bar =</b><span style="flex:0 0 0.8in"></span><b>seconds</b></div>'
             f'<table class="map" style="margin-bottom:3pt"><tr><th style="width:11%">Section</th><th style="width:33%">What the listener hears</th><th style="width:10%">First bar</th>'
             f'<th style="width:10%">Bars</th><th style="width:16%">Seconds</th><th>Time (from–to)</th></tr>{secs}'
             f'<tr><td><b>Total</b></td><td></td><td style="background:#ececec"></td><td></td><td></td><td style="background:#ececec"></td></tr></table>'
             f'<div class="fl" style="margin:3pt 0 4pt"><b>Do my sections add up to my bars?</b><span></span><b>Total seconds =</b><span style="flex:0 0 0.8in"></span><b>(must be 30)</b></div>'
             f'<div class="cols" style="gap:10pt"><div class="box acc-b" style="padding:4pt 9pt"><span class="k">Time at a bar</span><p style="margin:0;font-size:9.4pt;line-height:1.3">'
             f'Time = (bar − 1) × seconds per bar. At 120 BPM, bar 13 starts at (13 − 1) × 2 = 24 s. A beat is 60 ÷ BPM seconds. Use it to place the voice lines and the hook.</p></div>'
             f'<div class="box" style="padding:4pt 9pt"><span class="k">Rules of thumb</span><p style="margin:0;font-size:9.4pt;line-height:1.3">'
             f'Keep the intro to 1 or 2 bars: ads are short. Make the hook the biggest section. Say the tagline in the tag or at the end of the hook, and finish on a clear last chord.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">Moments I plan (bar, time, what happens)</span>'
             + '<div class="ln2" style="height:21pt"></div>' * 3)
    return D.page("The 30-second plan", "STUDENT", "Class 1", inner, n, wm, name=True, key="plan")


RECIPES = [
    ("Drummer", "The groove",
     [("Add", "Add a Drummer track (the + button in the track list, then choose Drummer) and choose a drummer whose style fits the brief’s mood."),
      ("Shape", "Drag the puck on the XY pad: right is louder, up is busier. Keep it low in the verse and high in the hook."),
      ("Trim", "Turn off parts you do not need (such as the hi-hat) so the voice has room, and draw a short fill into the hook.")]),
    ("Session Players", "Chords and bass",
     [("Chord Track", "Show the global tracks (G), add the Chord Track if your version has it, and type your four chords bar by bar."),
      ("Players", "If your version has Session Players, add a Bass Player and a Keyboard Player; they follow the Chord Track. "
                  "If not, draw chords in the Piano Roll with a Software Instrument."),
      ("Keep it simple", "Roots of the chords are enough for bass. Choose a soft keyboard sound so the voice can sit on top.")]),
    ("Alchemy or Retro Synth", "The hook",
     [("Sound", "Pick a pluck, bell or bright lead from the Library (Y), then change its filter and release by ear. Retro Synth is a simpler choice for a bass or lead."),
      ("Tune", "Write a hook of three to five notes from your key. Repeat it. A hook people can hum is better than a clever one."),
      ("Room", "Leave the hook out, or play it quietly, when the voice speaks.")]),
    ("Quick Sampler", "A must-include sound",
     [("Record", "Choose Quick Sampler and use its record function to capture your own sound: a mug clink, a stomp, a crunch or a snap. Nothing is supplied."),
      ("Shape", "Trim the start, set the pitch and add a high-pass filter if it sounds boomy. Play it from the keyboard."),
      ("Place", "Put it on a beat you can hear every time, such as beats 2 and 4, and use it in the hook.")]),
    ("Loop Browser", "Fills, risers and stings",
     [("Search", "Press O. Search by mood or by words such as riser, sparkle or whoosh. Click a loop to preview it at your tempo."),
      ("Use a little", "Drag in one riser before the hook and one sting for the last bar. Check that any loop with pitch fits your key."),
      ("Rights", "Use only the Apple Loops that come with Logic, and do not copy a loop that sounds like a real jingle.")]),
]


def build_page(n, wm=False):
    boxes = ""
    for inst, ttl, rows in RECIPES:
        body = "".join(f'<p style="margin:0 0 2pt;font-size:10.5pt;line-height:1.3"><b>{a}.</b> {b}</p>' for a, b in rows)
        boxes += (f'<div class="box" style="margin-bottom:5pt;padding:5pt 10pt"><span class="k" style="font-size:12pt;margin:0 0 2pt;color:#000">'
                  f'{inst} · {ttl}</span>{body}</div>')
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.36">Five recipes, in words. Settings are starting points: change them by ear. '
             f'Use <b>at least four layers</b>: Drummer or a Session Player, and at least one of Alchemy, Retro Synth or Quick Sampler. '
             f'Both must-include sounds from your brief go in the music.</p>{boxes}'
             f'<div class="box acc-b" style="padding:4pt 10pt"><span class="k">Three habits of a good jingle writer</span><p style="margin:0;font-size:10.4pt;line-height:1.3">'
             f'<b>Simple:</b> a loop, a groove and one hook are enough. <b>Repeat:</b> a hook the listener hears three times will stay. '
             f'<b>Leave room:</b> the voice is the most important sound, so keep the middle of the mix free when it speaks.</p></div>')
    return D.page("Build the music · Logic Pro recipes", "STUDENT", "Class 2", inner, n, wm, name=False, key="build")


ARR_COLS = 16


def layers_page(n, wm=False):
    cg = "<colgroup><col style='width:1.15in'>" + "<col>" * ARR_COLS + "</colgroup>"
    head = "<tr><th>Row</th>" + "".join(f"<th>{i + 1}</th>" for i in range(ARR_COLS)) + "</tr>"
    names = ["Sections", "Chord", "", "", "", "", "", "", "Voice-over", "Music level (dB)"]
    body = "".join(f"<tr><td class='l' style='height:29pt'>{nm}</td>" + "".join(f"<td class='{'b' if i % 4 == 0 else ''}'></td>" for i in range(ARR_COLS))
                   + "</tr>" for nm in names)
    inner = (f'{CSS_SG}<style>table.sg th {{ font-size: 7pt; }} table.sg td.l {{ width: 1.15in; font-size: 8.4pt; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.4pt">Step 3: the layer map. Each column is one bar (the number is the bar). Write the section names and the chord of each bar in the first rows, '
             f'name each layer at the left of the next six rows, and shade the bars where it plays. Show the voice lines in the voice-over row and sketch where the music dips. '
             f'A jingle builds when layers enter on purpose, so not every layer should play from start to finish. A thick line marks every fourth bar.</p>'
             f'<table class="sg">{cg}{head}{body}</table>'
             f'<p class="small" style="margin:2pt 0 0">If your tempo gives fewer than 16 bars, cross out the columns after your last bar.</p>'
             f'<div class="cols" style="gap:10pt;margin-top:6pt"><div class="box acc-b"><span class="k">My sections</span>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Intro:</b><span style="flex:0 0 0.6in"></span><b>bars</b><span></span></div>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Verse:</b><span style="flex:0 0 0.6in"></span><b>bars</b><span></span></div>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Hook:</b><span style="flex:0 0 0.6in"></span><b>bars</b><span></span></div>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Tag:</b><span style="flex:0 0 0.6in"></span><b>bars</b><span></span></div></div>'
             f'<div class="box"><span class="k">Count my layers</span>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Layers in the intro:</b><span></span></div>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Layers in the hook:</b><span></span></div>'
             f'<div class="fl" style="margin:5pt 0 0"><b>Layers in the last bar:</b><span></span></div>'
             f'<p class="small" style="margin:3pt 0 0">The hook should have the most layers.</p></div></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Checks before I record the voice</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:2pt") for c in [
                 "My chord loop matches my key, and the Session Players or my own chords follow it.",
                 "At least four layers, and both must-include sounds are in the music.",
                 "The intro is short, the hook is the biggest section and the last bar ends on the I chord.",
                 "I have left gaps in the music where the voice will speak."]) + '</div>')
    return D.page("Layer map", "STUDENT", "Classes 2–3", inner, n, wm, name=True, key="layers")


def script_page(n, wm=False):
    wrow = ""
    for w in range(8, 13):
        wrow += f"<tr><td><b>{w}</b></td>" + "".join(f"<td>{sec(round(w / r, 1))} s</td>" for r in WPS) + "</tr>"
    last = EX_VO[2]
    t0, t1 = vo_span(2)
    rows = "".join("<tr>" + "<td style='height:36pt'></td>" * 8 + "</tr>" for _ in range(4))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.4pt;line-height:1.36">Step 4: write the voice-over. It has <b>8 to 12 words</b> in all, includes your client’s '
             f'<b>tagline, spoken as given</b>, and says the product name. Listeners hear about <b>2 to 3 words a second</b> (about 3 to 4 syllables a second) from a calm announcer. '
             f'Check each line three ways: its words, its syllables, and the seconds you give it.</p>'
             f'<div class="cols" style="gap:10pt"><div><span class="k">Words to seconds</span>'
             f'<table class="t" style="font-size:9.4pt;margin-top:2pt"><tr><th>Words</th><th>Slow, 2 a second</th><th>Steady, 2.5</th><th>Fast, 3</th></tr>{wrow}</table></div>'
             f'<div class="box acc-b" style="padding:5pt 9pt"><span class="k">A line fits when…</span><p style="margin:0;font-size:9.6pt;line-height:1.32">'
             f'seconds needed = words ÷ 2 (slow) and also syllables ÷ 3, and the larger of the two must be no more than the seconds you give the line. '
             f'Start time = (bar − 1) × seconds per bar + (beat − 1) × seconds per beat.<br>'
             f'<b>Example:</b> “{last[2]}” has {len(words_of(last[2]))} words and {last[3]} syllables, starts at bar {last[0]}, beat {last[1]} = {sec(t0)} s and takes '
             f'{sec(len(words_of(last[2])) / EX_WPS)} s at {EX_WPS:g} words a second, so it ends at {sec(t1)} s.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">My script, line by line (the last line should end with the tagline)</span>'
             f'<table class="map" style="font-size:9.4pt"><tr><th style="width:5%">#</th><th style="width:31%">The words I say</th><th style="width:8%">Words</th><th style="width:10%">Syllables</th>'
             f'<th style="width:11%">Bar, beat</th><th style="width:11%">Starts (s)</th><th style="width:11%">Needs (s)</th><th>Ends (s)</th></tr>{rows}'
             f'<tr><td></td><td><b>Totals</b></td><td></td><td></td><td colspan="4" style="background:#ececec"></td></tr></table>'
             f'<div class="cols" style="gap:10pt;margin-top:5pt"><div class="box"><span class="k">Syllable check</span><p style="margin:0;font-size:9.6pt;line-height:1.3">'
             f'Clap or tap each syllable: “Hap-py feet all win-ter” is 6. Count each line. One bar at 120 BPM lasts 2 s, enough for about 6 to 8 syllables. '
             f'If a line has too many, cut words or give it two bars.</p></div>'
             f'<div class="box"><span class="k">Tips</span><p style="margin:0;font-size:9.6pt;line-height:1.3">Short words win. Put the product name early and the tagline last. '
             f'Read it aloud against a metronome or the playing loop before you record.</p></div></div>'
             f'<div class="box acc-b" style="margin-top:5pt;padding:4pt 10pt"><span class="k">Check my script</span>'
             + "".join(D.chk(c, 10.5, "font-size:9.6pt;margin-bottom:1.5pt") for c in [
                 "Between 8 and 12 words in all, and the product name is spoken.",
                 "The tagline is spoken exactly as the brief gives it, near the end.",
                 "Every line fits the bars I give it, and no line starts on top of another."]) + '</div>')
    return D.page("Write the script · words, syllables, seconds", "STUDENT", "Class 3", inner, n, wm, name=True, key="script")


def voice_page(n, wm=False):
    chain = ["Microphone", "Audio track", "Channel EQ", "Compressor", "DeEsser 2", "Fader and a little reverb"]
    boxes = "".join(f'<div style="flex:1 1 0;min-width:0;display:flex;align-items:center;justify-content:center;background:{"#000" if i % 2 == 0 else ACCENT};color:#fff;font-family:Oswald;font-weight:700;font-size:9.6pt;text-transform:uppercase;'
                    f'text-align:center;padding:6pt 3pt;border-radius:6pt;line-height:1.15">{c}</div>' + ('<div style="flex:0 0 8pt;display:flex;align-items:center;justify-content:center;font-weight:700">›</div>' if i < len(chain) - 1 else "")
                    for i, c in enumerate(chain))
    take = "".join("<tr>" + "<td style='height:22pt'></td>" * 5 + "</tr>" for _ in range(3))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.4pt;line-height:1.36">Step 5: record your voice-over and clean it up. A clear voice matters more than the music: '
             f'it carries the product name and the tagline. Settings below are starting points; trust your ears and your headphones.</p>'
             f'<div style="display:flex;align-items:stretch;gap:3pt;margin:2pt 0 6pt">{boxes}</div>'
             f'<div class="cols" style="gap:10pt"><div class="box" style="padding:5pt 9pt"><span class="k">Record it</span><ol style="margin:0;padding-left:13pt">'
             f'<li style="font-size:9.8pt;margin-bottom:2pt">Put on headphones. Add an Audio track, choose the microphone as its input and click its R button.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:2pt">Sit 6 to 8 inches from the microphone, a little to one side so “p” and “b” do not pop. Use a pop screen if you have one.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:2pt">Say the line out loud, then set the level so the loudest word reaches about the top of the meter’s green or yellow, never red.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:2pt">Play the music quietly in your headphones and record at least three takes of the whole script.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:0">Choose the best take of each line. Trim the silence around it and line it up with the bar you planned.</li></ol></div>'
             f'<div class="box acc-b" style="padding:5pt 9pt"><span class="k">Clean it up</span><ul style="margin:0;padding-left:13pt">'
             f'<li style="font-size:9.8pt;margin-bottom:2pt"><b>Channel EQ:</b> turn the lowest band into a high-pass filter near 80 Hz to remove rumble and breath.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:2pt"><b>Compressor:</b> start with a ratio around 3:1 and lower the threshold until the loudest words are turned down by a few dB.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:2pt"><b>DeEsser 2:</b> if “s” and “t” sound sharp, set it near the harsh frequency (often 5 to 8 kHz) and raise the amount until they soften.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:0"><b>Reverb:</b> add only a trace, so the voice stays close and clear.</li></ul></div></div>'
             f'<span class="k" style="margin-top:5pt">My take log</span>'
             f'<table class="map" style="font-size:9.4pt"><tr><th style="width:8%">Take</th><th style="width:22%">Line(s)</th><th style="width:30%">What I noticed</th><th style="width:20%">Best?</th><th>Fix for next time</th></tr>{take}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:5pt"><div class="box"><span class="k">Check my voice</span>'
             + "".join(D.chk(c, 10.5, "font-size:9.6pt;margin-bottom:1.5pt") for c in [
                 "I can hear every word, including the product name and the tagline.",
                 "No clicks, pops, clipping or room noise, and no music in the recording.",
                 "Each line starts on the bar and beat I planned (page " + str(D.IX("script")) + ")."]) + '</div>'
             f'<div class="box acc-b"><span class="k">Honest voice rules</span><p style="margin:0;font-size:9.6pt;line-height:1.3">Record your own voice or a classmate who agrees. '
             f'Do not imitate a real person or a real ad voice. Smile while you speak: it changes the sound.</p></div></div>')
    return D.page("Record the voice-over", "STUDENT", "Class 3", inner, n, wm, name=True, key="voice")


def duck_page(n, wm=False):
    rows = "".join("<tr>" + f"<td style='height:28pt'>{i}</td>" + "<td></td>" * 4 + "</tr>" for i in (1, 2, 3, 4))
    inner = (f'<p style="margin:0 0 3pt;font-size:10.4pt;line-height:1.36">Step 5, continued: duck the music. <b>Ducking</b> turns the music down while the voice speaks, then back up. About <b>4 to 6 dB</b> is '
             f'enough. The picture is the worked example: the colored lines are the voice, and the line below is the music level.</p>'
             f'<div style="margin:2pt 0 4pt">{D.body_svg(duck_body(1250, "page duck", 22, 18))}</div>'
             f'<div class="cols" style="gap:10pt"><div class="box acc-b" style="padding:5pt 9pt"><span class="k">Method A · sidechain</span><ol style="margin:0;padding-left:13pt">'
             f'<li style="font-size:9.6pt;margin-bottom:2pt">Group the music tracks (select them and make a Track Stack) so one plug-in controls all of them.</li>'
             f'<li style="font-size:9.6pt;margin-bottom:2pt">Insert Compressor on the stack. In its Side Chain menu (top right of the plug-in window) choose the voice track.</li>'
             f'<li style="font-size:9.6pt;margin-bottom:2pt">Play a voice line and lower the threshold until the music dips by about 4 to 6 dB.</li>'
             f'<li style="font-size:9.6pt;margin-bottom:0">Set a short attack and a release of about half a second so it returns smoothly.</li></ol></div>'
             f'<div class="box" style="padding:5pt 9pt"><span class="k">Method B · automation</span><ol style="margin:0;padding-left:13pt">'
             f'<li style="font-size:9.6pt;margin-bottom:2pt">Press A to show automation on the music tracks or stack, and choose Volume.</li>'
             f'<li style="font-size:9.6pt;margin-bottom:2pt">Click to add four points around each voice line: the level half a beat before it, the dip when it starts, the end of the line and back up one beat later.</li>'
             f'<li style="font-size:9.6pt;margin-bottom:2pt">Drag the two middle points down 4 to 6 dB.</li>'
             f'<li style="font-size:9.6pt;margin-bottom:0">Play it and smooth the points until you cannot hear the dip, only the clear voice.</li></ol></div></div>'
             f'<span class="k" style="margin-top:5pt">My ducking points (seconds): beat = 60 ÷ BPM</span>'
             f'<table class="map" style="font-size:9.4pt"><tr><th style="width:8%">Line</th><th style="width:23%">Dip starts (start − half a beat)</th><th style="width:23%">Voice starts</th><th style="width:23%">Voice ends</th><th>Back up (end + a beat)</th></tr>{rows}</table>'
             f'<div class="box" style="margin-top:5pt;padding:4pt 10pt"><span class="k">Check my mix</span>'
             + "".join(D.chk(c, 10.5, "font-size:9.6pt;margin-bottom:1.5pt") for c in [
                 "Every word of the voice is clear, even on small speakers. I listened quietly first.",
                 "The music comes back up between lines and I cannot hear the dip pump or click.",
                 "The master fader never goes into the red, and the voice and music both sound natural."]) + '</div>')
    return D.page("Duck the music under the voice", "STUDENT", "Class 3", inner, n, wm, name=True, key="duck")


def bounce_page(n, wm=False):
    rows = ""
    for b in FIT_PICK:
        nb = int(bars_in_30(b))
        rows += f"<tr><td><b>{b}</b></td><td>{nb}</td><td>bar {nb + 1}</td><td>{nb} × 240 ÷ {b} = {sec(nb * 240 / b)} s</td></tr>"
    fix = [("The file is a little short or long", "The end locator is not on the bar after your last bar. Move it, then bounce again."),
           ("The reverb or the last sound is cut off", "Let the sting finish inside the last bar, or shorten the reverb tail. Do not move the end past 30 seconds."),
           ("The voice starts late or clips", "Check the take is still on its bar after editing, and lower the voice fader before bouncing."),
           ("The tempo changed", "Check there is only one tempo in the whole project.")]
    frows = "".join(f"<tr><td style='width:34%'><b>{a}</b></td><td>{b}</td></tr>" for a, b in fix)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.4pt;line-height:1.36">Step 6: bounce exactly 30 seconds. The clock starts at bar 1 and stops at the start of the bar after your last one, '
             f'so for a whole number of bars the end locator sits at <b>bar (bars + 1)</b>. At 120 BPM that is bar 16, because 15 bars × 2 seconds = 30 seconds.</p>'
             f'<table class="t" style="font-size:9.6pt;table-layout:fixed"><tr><th>Tempo (BPM)</th><th>Bars</th><th>End locator at</th><th>Length</th></tr>{rows}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:4pt"><div class="box acc-b" style="padding:5pt 9pt"><span class="k">Bounce it</span><ol style="margin:0;padding-left:13pt">'
             f'<li style="font-size:9.8pt;margin-bottom:2pt">Listen once from the top with the master fader below the red.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:2pt">Turn Cycle on (C) and drag its range from bar 1 to your end locator, or type the positions.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:2pt">Open File › Bounce › Project or Section (Command-B). Choose WAV or MP3, and check the start and end shown match the cycle area.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:2pt">If your version offers an option to include the audio tail, turn it off so the file stays exactly 30 seconds.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:0">Name the file {FILE_NAME} and bounce.</li></ol></div>'
             f'<div class="box" style="padding:5pt 9pt"><span class="k">Check the length</span><ol style="margin:0;padding-left:13pt">'
             f'<li style="font-size:9.8pt;margin-bottom:2pt">In Finder, select the file and press the space bar: the preview shows its length.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:2pt">Or press Command-I; the info window shows the duration under More Info.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:2pt">It should read 0:30. If it does not, use the table below, fix and bounce again.</li>'
             f'<li style="font-size:9.8pt;margin-bottom:0">Save a zipped copy of the .logicx project too (in Finder, Control-click it and choose Compress).</li></ol></div></div>'
             f'<span class="k" style="margin-top:5pt">If it is not 30 seconds</span>'
             f'<table class="t" style="font-size:9.4pt">{frows}</table>'
             f'<div class="box" style="margin-top:5pt;padding:4pt 10pt"><span class="k">My export</span>'
             f'<div class="fl" style="margin:4pt 0 6pt"><b>My tempo:</b><span style="flex:0 0 0.7in"></span><b>BPM. Bars:</b><span style="flex:0 0 0.7in"></span><b>End locator at bar:</b><span style="flex:0 0 0.7in"></span><b>Length in Finder:</b><span></span></div>'
             + "".join(D.chk(c, 10.5, "font-size:9.6pt;margin-bottom:1.5pt") for c in [
                 "The file reads 0:30 in Finder, nothing is cut off and nothing clips.",
                 "I handed in the .wav or .mp3 and the zipped .logicx, named correctly."]) + '</div>')
    return D.page("Bounce exactly 30 seconds", "STUDENT", "Class 4", inner, n, wm, name=True, key="bounce")


def feedback_page(n, wm=False):
    crit = ["The product name and the tagline were easy to hear", "The music matches the mood in the brief", "Both must-include sounds are in the music",
            "I could hear every word of the voice-over", "The music and voice sit well together (the music steps aside)", "The jingle feels like 30 seconds, with a clear ending"]
    CB = D.checkbox(13)
    rows = "".join(f"<tr><td style='height:31pt;font-size:10.6pt'>{c}</td><td style='text-align:center'>{CB}</td><td style='text-align:center'>{CB}</td><td style='text-align:center'>{CB}</td></tr>" for c in crit)
    inner = (f'<p style="margin:0 0 5pt;font-size:10.8pt;line-height:1.38">Step 7: the <b>client feedback sheet</b>. A classmate acts as the client. The writer plays the jingle once, the client reads the '
             f'brief card and fills in this sheet, and the writer answers the client’s questions. Be honest and kind: say what works and what you would change.</p>'
             f'<div class="fl" style="margin:0 0 5pt"><b>Product:</b><span></span><b>Writer:</b><span></span><b>Client:</b><span></span></div>'
             f'<table class="map" style="font-size:10pt"><tr><th style="width:61%">When I listened to this jingle…</th><th>Yes</th><th>Mostly</th><th>Not yet</th></tr>{rows}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:8pt"><div class="box acc-b"><span class="k">What I remember</span>'
             f'<div class="fl" style="margin:6pt 0 9pt"><b>The tagline was:</b><span></span></div><div class="fl" style="margin:0 0 9pt"><b>The mood was:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 3pt"><b>I would buy it because:</b><span></span></div></div>'
             f'<div class="box"><span class="k">Two stars and a wish</span>'
             f'<div class="fl" style="margin:6pt 0 9pt"><b>Star 1:</b><span></span></div><div class="fl" style="margin:0 0 9pt"><b>Star 2:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 3pt"><b>My wish (one change):</b><span></span></div></div></div>'
             f'<div class="box" style="margin-top:8pt"><span class="k">Writer’s reply</span>'
             f'<div class="fl" style="margin:6pt 0 9pt"><b>The change I will make:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 9pt"><b>Which page or tool I will use for it:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 3pt"><b>What I will keep exactly as it is:</b><span></span></div></div>'
             f'<div class="box" style="margin-top:8pt"><span class="k">Client’s signature</span><div class="fl" style="margin:10pt 0 2pt"><b>Name:</b><span></span><b>Date:</b><span style="flex:0 0 1.2in"></span></div></div>')
    return D.page("Client feedback sheet", "STUDENT", "Class 4", inner, n, wm, name=True, key="feedback")


def vocab_page(n, wm=False):
    """Kit version of the vocabulary page: a real gap between the boxes and clearance from the footer rule."""
    cells = "".join(
        f'<div class="box" style="margin-bottom:13pt;padding:6pt 10pt 3pt"><p style="margin:0 0 1pt;font-size:11.6pt"><b style="font-family:Oswald;'
        f'font-size:13pt;text-transform:uppercase;letter-spacing:.02em">{a}</b> — {b}</p>'
        f'<div class="fl" style="margin:6pt 0 6pt"><b>In my own words:</b><span></span></div>'
        f'<div class="fl" style="margin:0 0 3pt"><b>{VOCAB_PROMPT}</b><span></span></div></div>' for a, b in VOCAB)
    inner = (f'<p style="font-size:11.4pt;margin:0 0 6pt">The six words from your project sheet, with definitions. Rewrite each in your '
             f'own words, then show where it happens in your own project.</p>{cells}')
    return D.page("Key vocabulary", "STUDENT", "Vocabulary", inner, n, wm, name=True, key="vocab")


def present_page(n, wm=False):
    """Kit version of the feedback planner: the three question lines are evenly spaced (every rule 24pt below the last)."""
    qs = "".join(f'<div class="fl" style="margin:0;height:24pt"><b>Question {i}:</b><span style="height:24pt"></span></div>'
                 f'<div class="ln2" style="margin:0"></div>' for i in (1, 2, 3))
    rows = "".join("<tr><td style='height:40pt'></td><td></td><td></td></tr>" for _ in range(4))
    inner = (f'<div class="box acc-b"><span class="k">From your project sheet, step {len(STEPS)}</span><p style="margin:0;font-size:11.4pt">'
             f'{D.fill(STEPS[-1])}</p></div>'
             f'{D.H2("My three questions for my client")}<p style="margin:0 0 6pt">Ask about things you really want to know, not yes-or-no questions.</p>{qs}'
             f'{D.H2("Classmates’ questions I answered (at least 2)")}'
             f'<table class="map"><tr><th style="width:24%">Classmate</th><th style="width:38%">Their question</th><th>My answer</th></tr>{rows}</table>'
             f'{D.H2("Before I present")}'
             + "".join(D.chk(D.fill(c), 12, "font-size:11.4pt;margin-bottom:6pt") for c in PRESENT_CHECK))
    return D.page("Present and get feedback", "STUDENT", f"Class {CLASSES}", inner, n, wm, name=True, key="present")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "brief": brief_page, "loop": loop_page, "plan": plan_page, "build": build_page, "layers": layers_page, "script": script_page,
         "voice": voice_page, "duck": duck_page, "bounce": bounce_page, "feedback": feedback_page, "vocab": vocab_page, "present": present_page}


# ================================================================ content checks (30 seconds, chords, script timing, ducking, tables, slides)
def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 6), reqs=(REQS, 6), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 4), briefs=(BRIEFS, 4), recipes=(RECIPES, 5),
                  loops=(LOOPS, 5), layers=(EX_LAYERS, 6), vo=(EX_VO, 3), logicref=(LOGIC_REF, 11))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    if set(TAGS) & {"Holiday", "Student Practice", "Theme", "Seasonal"} or "Performing Arts" in SUBJECTS:
        errs.append("tags and subjects must not be headings")
    if re.search(r"winter|holiday|christmas|snow|hanukkah|kwanzaa|season", LISTING_TITLE, re.I):
        errs.append("the listing title must not contain a seasonal word")
    # ---- 30 seconds: a bar of 4/4 lasts 240 / BPM seconds, so 30 seconds hold BPM / 8 bars
    if bar_s(120) != 2 or Fraction(240, 120) != 2 or EX_BAR_S != 2 or EX_BEAT_S != .5:
        errs.append("at 120 BPM a beat is 0.5 s and a bar of 4/4 is 2 s")
    if EX_BARS * EX_BAR_S != LEN_S or bars_in_30(EX_BPM) != EX_BARS or EX_BPM // 8 != EX_BARS:
        errs.append("15 bars x 2 s = 30 s at 120 BPM, and bars = BPM / 8")
    if len(FIT_PICK) != 7 or any(b not in FIT_BPMS for b in FIT_PICK) or any(bars_in_30(b) != b // 8 or b % 8 for b in FIT_PICK):
        errs.append("the tempo helper must hold only tempos that divide by 8 (whole bars in 30 s)")
    if [int(bars_in_30(b)) for b in FIT_PICK] != [10, 11, 12, 13, 14, 15, 16]:
        errs.append("bars for 80..128 BPM must be 10..16")
    for b in FIT_PICK:
        if Fraction(int(bars_in_30(b)) * 240, b) != LEN_S:
            errs.append(f"{b} BPM: {bars_in_30(b)} bars is not exactly 30 s")
    if [b for b in range(60, 161) if bars_in_30(b).denominator != 1] and 100 in FIT_BPMS:
        errs.append("100 BPM does not give whole bars in 30 s (12.5)")
    if EX_SECTIONS[0][1] != 1 or EX_SECTIONS[-1][2] != EX_BARS or any(b_ + 1 != c_ for (_, _, b_), (_, c_, _) in zip(EX_SECTIONS, EX_SECTIONS[1:])):
        errs.append("sections must tile bars 1-15")
    if [b_ - a_ + 1 for _, a_, b_ in EX_SECTIONS] != [2, 4, 6, 3] or sum(b_ - a_ + 1 for _, a_, b_ in EX_SECTIONS) != EX_BARS:
        errs.append("sections 2 + 4 + 6 + 3 = 15")
    if [nm for nm, _, _ in EX_SECTIONS] != ["Intro", "Verse", "Hook", "Tag"] or set(EX_JOBS) != {"Intro", "Verse", "Hook", "Tag"}:
        errs.append("the four sections are Intro, Verse, Hook and Tag")
    if [mmss(bar_time(a_)) for _, a_, _ in EX_SECTIONS] != ["0:00", "0:04", "0:12", "0:24"] or mmss(bar_time(EX_BARS + 1)) != "0:30":
        errs.append("section starts 0:00, 0:04, 0:12, 0:24 and the end at 0:30")
    if [mmss(bar_time(b_)) for b_, _ in EX_MOMENTS] != ["0:04", "0:12", "0:20", "0:24", "0:28"] or bar_time(13) != 24:
        errs.append("moment times recomputed")
    # ---- the tempo / key choices of the four briefs, and every chord written from the scale
    names = [b["product"] for b in BRIEFS]
    if len(set(names)) != 4 or [b["k"] for b in BRIEFS] != list("ABCD"):
        errs.append("four briefs A-D with different products")
    loopmap = {nm: (nums, minor) for nm, nums, minor, _f, _u in LOOPS}
    for nm, nums, minor, _f, _u in LOOPS:
        if "–".join(nums) != nm:
            errs.append(f"loop {nm} must be its numerals joined")
        try:
            for s in nums:
                parse_numeral(s, minor)
        except ValueError as e:
            errs.append(str(e))
    for b in BRIEFS:
        if any(t not in FIT_PICK for t in b["bpms"]):
            errs.append(f"brief {b['k']}: tempos must be in the tempo helper")
        if b["loop"] not in loopmap or loopmap[b["loop"]][1] != b["key"].endswith("m") or b["key"] not in SCALES:
            errs.append(f"brief {b['k']}: loop and key must agree (major or minor)")
        tw = words_of(b["tagline"])
        if not 3 <= len(tw) <= 5:
            errs.append(f"brief {b['k']}: tagline should be 3 to 5 words")
        if len(b["sounds"]) != 2:
            errs.append(f"brief {b['k']}: two must-include sounds")
    if chords_in("C", ["I", "V", "vi", "IV"]) != ["C", "G", "Am", "F"] or chords_in("G", ["I", "V", "vi", "IV"]) != ["G", "D", "Em", "C"]:
        errs.append("I-V-vi-IV in C is C G Am F, and in G is G D Em C")
    if chords_in("D", ["I", "V", "vi", "IV"]) != ["D", "A", "Bm", "G"] or chords_in("A", ["I", "V", "vi", "IV"]) != ["A", "E", "F#m", "D"]:
        errs.append("I-V-vi-IV in D is D A Bm G, and in A is A E F#m D")
    if chords_in("Am", ["i", "VI", "III", "VII"]) != ["Am", "F", "C", "G"] or chords_in("Em", ["i", "VI", "III", "VII"]) != ["Em", "C", "G", "D"] \
            or chords_in("Bm", ["i", "VI", "III", "VII"]) != ["Bm", "G", "D", "A"]:
        errs.append("i-VI-III-VII in A minor is Am F C G, in E minor Em C G D, in B minor Bm G D A")
    try:
        parse_numeral("VI", False)
        errs.append("a capital VI is not a chord of a major key's scale (vi is minor)")
    except ValueError:
        pass
    if numeral(5, "m") != "vi" or numeral(3, "") != "IV" or numeral(6, "dim") != "vii°":
        errs.append("Roman numeral case: capital major, small minor")
    exc = ex_chords()
    if len(exc) != EX_BARS or exc[:4] != ["G", "D", "Em", "C"] or exc[4:8] != exc[:4] or exc[8:12] != exc[:4] or exc[12:] != ["C", "D", "G"]:
        errs.append("worked example chords: G D Em C three times, then C D G")
    # ---- layers
    for nm, spans, tool, _d in EX_LAYERS:
        for a_, b_ in spans:
            if not 1 <= a_ <= b_ <= EX_BARS:
                errs.append(f"layer {nm}: span {a_}-{b_} outside the piece")
    top = max(EX_DENS)
    hook = next((a_, b_) for nm, a_, b_ in EX_SECTIONS if nm == "Hook")
    if [i + 1 for i, d_ in enumerate(EX_DENS) if d_ == top] != list(range(7, 11)) or not hook[0] <= 7 <= 10 <= hook[1]:
        errs.append("the most layers must play only in bars 7-10, inside the Hook")
    if EX_DENS[0] >= top or EX_DENS[-1] >= top:
        errs.append("the jingle starts and ends with fewer layers than the hook")
    # ---- script: 8 to 12 words, syllables recomputed, tagline last, product named, lines fit their bars
    tw_all = sum(len(words_of(v[2])) for v in EX_VO)
    if not 8 <= tw_all <= 12:
        errs.append(f"the worked script has {tw_all} words, needs 8 to 12")
    for i, (bar, beat, text, st) in enumerate(EX_VO):
        got = sum(syl(w) for w in words_of(text))
        if got != st:
            errs.append(f"line {i + 1} '{text}': syllables counted {got}, stated {st}")
        t0, t1 = vo_span(i)
        if not 0 <= t0 < t1 <= LEN_S:
            errs.append(f"line {i + 1} must sit inside 30 seconds")
        need = max(len(words_of(text)) / 2, st / 3)
        if need > EX_BAR_S + 1e-9:
            errs.append(f"line {i + 1} needs {need} s, more than one bar ({EX_BAR_S} s)")
        if i + 1 < len(EX_VO) and t1 > bar_time(*EX_VO[i + 1][:2]):
            errs.append(f"line {i + 1} runs into line {i + 2}")
    if re.sub(r"[^a-z ]", "", EX_VO[-1][2].lower()) != EX_TAGLINE.lower():
        errs.append("the last voice line must be the tagline")
    if EX_PRODUCT.lower().replace("’", "'") not in " ".join(v[2] for v in EX_VO).lower().replace("’", "'"):
        errs.append("the product name must be spoken in the worked script")
    if [round(vo_span(i)[0], 2) for i in range(3)] != [4.0, 20.0, 24.0] or [round(vo_span(i)[1], 2) for i in range(3)] != [5.6, 21.6, 25.6]:
        errs.append("voice lines start 4, 20, 24 s and end 5.6, 21.6, 25.6 s")
    if [bar_time(*v[:2]) for v in EX_VO] != [4.0, 20.0, 24.0]:
        errs.append("voice line starts from bar and beat")
    if [round(w / r, 1) for w in (8, 12) for r in WPS] != [4.0, 3.2, 2.7, 6.0, 4.8, 4.0]:
        errs.append("words-to-seconds table: 8 words 4.0/3.2/2.7 s, 12 words 6.0/4.8/4.0 s")
    for b in BRIEFS:
        t = b["tagline"]
        if len(words_of(t)) >= 13:
            errs.append("a tagline cannot be 12+ words")
    # ---- ducking: down half a beat before, up a beat after, never overlapping the next line, within 0 and -5 dB
    pts = duck_points()
    if [t for t, _ in pts] != sorted(t for t, _ in pts) or pts[0] != (0.0, 0.0) or pts[-1] != (30.0, 0.0):
        errs.append("duck points in order from 0 to 30 s")
    for i in range(3):
        t0, t1 = vo_span(i)
        want = [(t0 - .25, 0.0), (t0, -5.0), (t1, -5.0), (t1 + .5, 0.0)]
        if pts[1 + 4 * i:5 + 4 * i] != want:
            errs.append(f"ducking points for line {i + 1}: {want}")
    if any(not -EX_DUCK_DB <= d_ <= 0 for _, d_ in pts) or not 4 <= EX_DUCK_DB <= 6:
        errs.append("ducking depth 4 to 6 dB")
    for i in range(2):
        if vo_span(i)[1] + EX_DUCK_TAIL > vo_span(i + 1)[0] - EX_DUCK_LEAD:
            errs.append(f"the music must be back up before line {i + 2} starts to dip")
    # ---- slides: no bullet may end mid-sentence; page numbers in the notes are real pages
    dangling = {"a", "an", "the", "of", "to", "at", "in", "on", "for", "and", "or", "with", "your", "each", "every", "their", "its", "from", "by", "is"}
    for i, s in enumerate(SLIDES, start=1):
        for b in [x.strip() for x in s[3].split("|") if x.strip()]:
            last = re.sub(r"[^\w’']", "", b.split()[-1]).lower()
            if b.endswith(("’s", "'s", ",", ":")) or last in dangling:
                errs.append(f"slide {i} bullet looks truncated: '{b}'")
    ok_pages = {pg(k) for k in ("plan", "build", "loop", "script", "duck", "voice", "bounce", "feedback")}
    for i, s in enumerate(SLIDES, start=1):
        for m in re.finditer(r"\bpage (\d+)\b", s[4]):
            if int(m.group(1)) not in ok_pages:
                errs.append(f"slide {i} notes name page {m.group(1)}, which is not a page the notes mean to cite")
    for i, s in enumerate(SLIDES, start=1):
        for key, word in (("plan", "own on page"), ("build", "Recipes are on page"), ("loop", "loop and a key on page"), ("script", "own words and syllables on page"),
                          ("duck", "Both methods are on page"), ("voice", "recording steps are on page"), ("bounce", "bounce (page"), ("feedback", "feedback sheet on page")):
            if word in s[4] and f"{word} {pg(key)}" not in s[4]:
                errs.append(f"slide {i}: page number after '{word}' must be page {pg(key)}")
    return errs


def has_words(need, text):
    """True when every word of `need` (letters and digits) occurs in `text`: table cells wrap, so a phrase can be split across text lines."""
    words = re.findall(r"[A-Za-z0-9#]+", need.lower())
    have = set(re.findall(r"[A-Za-z0-9#]+", text.lower()))
    return all(w in have for w in words)


P_PREVIEW = os.path.join(HERE, SLUG + "-PREVIEW.pdf")
P_DECKPDF = os.path.join(HERE, SLUG + "-intro-deck.pdf")


def verify_outputs(flat, stext, notes):
    import subprocess
    errs = []
    alldeck = " ".join(stext + notes)
    txt = re.sub(r"\s+", " ", " ".join(flat))
    # every 'Step N' anywhere must exist on the project sheet (STEPS)
    extra = []
    for f in (P_PREVIEW, P_DECKPDF):
        if os.path.exists(f):
            extra.append(subprocess.run(["pdftotext", f, "-"], capture_output=True, text=True).stdout)
    up = os.path.join(HERE, "UPLOAD.md")
    if os.path.exists(up):
        extra.append(open(up, encoding="utf8").read())
    for src in [txt0 := " ".join(flat), alldeck] + extra:
        for m in re.finditer(r"\bstep\s+(\d+)\b", re.sub(r"\s+", " ", src), re.I):
            if not 1 <= int(m.group(1)) <= len(STEPS):
                errs.append(f"'Step {m.group(1)}' is referenced but the project sheet has {len(STEPS)} steps")
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, loops, lyrics, jingles, artists or brands", "invented plan on paper", "Drummer", "Alchemy", "Quick Sampler",
                 "Retro Synth", "Channel EQ", "Compressor", "DeEsser 2", "Side Chain", "No student work is included",
                 "Created with the help of digital and AI tools.", "bars = BPM ÷ 8"):
        if need.lower() not in txt.lower():
            errs.append(f"PDF must say: '{need}'")
    if "What changed" in txt or "Kept as I wrote it" in txt or "my project menu" in txt or "my Digital Music Production" in txt:
        errs.append("ORIGINAL kit: no wording about changes to an owner's sheet")
    if "checked by hand" in txt or "handmade" in txt.lower() or "classroom-tested" in txt.lower() or "hand-checked" in txt.lower():
        errs.append("never claim hand checks or classroom testing for a new product")
    if "verified before release" in txt.lower() or "recomputed" in txt.lower():
        errs.append("no boilerplate about verification, and no internal QA wording, in buyer-facing text")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt:
        errs.append("PDF: 'Grades 9–12'")
    lp = flat[D.IX("loop") - 1]
    for k in MAJOR_KEYS:
        for nm, nums, minor, _f, _u in LOOPS:
            if not minor and chord_str(k, nums).replace(" ", "") not in lp.replace(" ", ""):
                errs.append(f"loop page must print {nm} in {k}: {chord_str(k, nums)}")
    for k in MINOR_KEYS:
        if chord_str(k, LOOPS[4][1]).replace(" ", "") not in lp.replace(" ", ""):
            errs.append(f"loop page must print i–VI–III–VII in {k}")
    for need in ("C G Am F", "capital", "small", "Roman numerals"):
        if need not in lp:
            errs.append(f"loop page must say '{need}'")
    pl = flat[D.IX("plan") - 1]
    for b in FIT_PICK:
        nb = int(bars_in_30(b))
        if f"{nb} × 240 ÷ {b} = 30 s" not in pl:
            errs.append(f"plan page: {b} BPM row must read {nb} × 240 ÷ {b} = 30 s")
    for need in ("BPM ÷ 8", "240 ÷ BPM", "Intro", "Verse", "Hook", "Tag", "30"):
        if need not in pl:
            errs.append(f"plan page must say '{need}'")
    bp = flat[D.IX("bounce") - 1]
    for b in FIT_PICK:
        nb = int(bars_in_30(b))
        if f"bar {nb + 1}" not in bp or f"{nb} × 240 ÷ {b} = 30 s" not in bp:
            errs.append(f"bounce page: {b} BPM must give the end locator at bar {nb + 1} and 30 s")
    bf = flat[D.IX("brief") - 1]
    for b in BRIEFS:
        for need in (b["product"], b["tagline"], b["sounds"][0], b["sounds"][1], b["audience"]):
            if not has_words(need, bf):
                errs.append(f"brief page must print: {need}")
        for t in b["bpms"]:
            if not has_words(f"{t} {bars_in_30(t)} bars", bf):
                errs.append(f"brief {b['k']}: tempo {t} with its bars missing")
    sc = re.sub(r"\s+", " ", flat[D.IX("script") - 1])
    for w in range(8, 13):
        for r in WPS:
            if f"{sec(round(w / r, 1))} s" not in sc:
                errs.append(f"script page: {w} words at {r} a second = {sec(round(w / r, 1))} s missing")
    for need in ("8 to 12 words", "tagline", "syllables", "2 to 3 words a second", "Happy feet all winter"):
        if need not in sc:
            errs.append(f"script page must say '{need}'")
    ex = re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-raw", "-f", str(D.IX("example")), "-l", str(D.IX("example2")), D.files()["pdf"], "-"],
                                            capture_output=True, text=True, check=True).stdout)
    for need in ("240 ÷ 120 = 2", "15 bars = 30 seconds", "2 + 4 + 6 + 3 bars = 15", "(bar − 1) × 2", "bar 13 starts at 0:24", "G D Em C", "bars = 120 ÷ 8 = 15",
                 "12 words", "16 syllables", "dips 5 dB", "Fluffwick Snug Wool Socks"):
        if need not in ex:
            errs.append(f"worked example must say '{need}'")
    for nm, a_, b_ in EX_SECTIONS:
        if f"{b_ - a_ + 1} × 2 = {sec((b_ - a_ + 1) * 2)} s" not in ex:
            errs.append(f"worked example: section {nm} arithmetic missing")
    for i, (bar, beat, text, sy) in enumerate(EX_VO):
        t0, t1 = vo_span(i)
        row = f"{text} {len(words_of(text))} {sy} bar {bar}, beat {beat} = {sec(t0)} s {len(words_of(text))} ÷ {EX_WPS:g} = {sec(len(words_of(text)) / EX_WPS)} s {sec(t1)} s"
        if row not in ex:
            errs.append(f"worked example script row {i + 1} missing or wrong: {row}")
        t0d = sec(t0 - EX_DUCK_LEAD)
        if f"{t0d} s {sec(t0)}–{sec(t1)} s {sec(t1 + EX_DUCK_TAIL)} s" not in ex:
            errs.append(f"worked example ducking row {i + 1} missing")
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
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Radiohead", "Billboard", "Bensound", "Ableton", "GarageBand loops"]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
    if "Winter" in LISTING_TITLE or "Holiday" in LISTING_TITLE:
        errs.append("title")
    return errs


def check_summary():
    return (f"the worked example is {EX_BARS} bars at {EX_BPM} BPM = {sec(EX_BARS * EX_BAR_S)} s (240 / {EX_BPM} = {sec(EX_BAR_S)} s a bar, bars = BPM / 8; sections "
            f"{'+'.join(str(b - a + 1) for _, a, b in EX_SECTIONS)} bars = {'+'.join(sec((b - a + 1) * EX_BAR_S) for _, a, b in EX_SECTIONS)} s; section and moment times "
            f"recomputed); the tempo helper holds only tempos whose 30 s is a whole number of bars (80-128 BPM = 10-16 bars) and the bounce page's end locators; "
            f"every chord in the loop tables is written from its scale with correct Roman numeral case (I-V-vi-IV in C = C G Am F); the {len(EX_LAYERS)} layers peak at "
            f"{max(EX_DENS)} only inside the Hook; the script has {sum(len(words_of(v[2])) for v in EX_VO)} words (8 to 12), syllables recounted, every line fits one bar, "
            f"timings from bar and beat; ducking points sit half a beat before and one beat after each line and never overlap; words-to-seconds table recomputed; "
            f"four briefs have fitting tempos and loops; the title carries no seasonal word; no audio, notation, recordings, artist names or student work; grades 9-12; "
            f"tags and subjects are not headings; no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("brief") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students act as a jingle writer for an invented product. From one of four fictional client briefs they plan a 30-second ad in bars, "
            f"choose a tempo, key and chord loop, and build the music in Logic Pro with Drummer, Session Players (if your version has them), Alchemy, Retro Synth, "
            f"Quick Sampler and library loops. They write and record an 8 to 12 word voice-over, clean it up with EQ, compression and a de-esser, duck the music "
            f"under it so every word is clear, and export exactly 30 seconds. A classmate then acts as the client and fills in a feedback sheet. This Commercial "
            f"Jingle project takes {CLASSES} class periods and is an original Hudson Beat project; the steps are written for Logic Pro, while the ideas (bars, chord "
            f"loops, voice-over, ducking) carry over to GarageBand and BandLab.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, two pages of teacher notes "
            f"(struggles, variations, resources, grading), a Logic quick reference, and a two-page worked example (an invented 30-second ad on paper: a 15-bar plan at "
            f"120 BPM with a bar and time table, six layers, a three-line script with its timing and the ducking points) ({n_teacher} pages)\n"
            f"• Student pages: four invented client briefs with a brief card, a tempo, key and chord-loop page with Roman numerals written out in seven keys, a "
            f"30-second plan with a tempo table (bars = BPM ÷ 8), Logic Pro recipes, a layer map, a script page with words, syllables and seconds, voice-over "
            f"recording and processing, a ducking page, an exact-length bounce page, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, "
            f"tips, submission checklist), the /25 rubric, a vocabulary page, a client feedback sheet, a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, the 30-second plan, the "
            f"chord loop, a script that fits, ducking, the voice chain, what to turn in and the rubric\n\n"
            f"THE FOUR CLASS PERIODS (works in 3 or 4 classes)\n"
            f"• Class 1: hook; choose a client brief; pick a tempo, key and loop; plan the 30 seconds in bars\n"
            f"• Class 2: build the music with Drummer, Session Players, Alchemy, Quick Sampler and loops\n"
            f"• Class 3: write and time the script; record and process the voice-over; duck the music; mix\n"
            f"• Class 4: bounce exactly 30 seconds and hand in; client feedback and presentations; reflection\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Planning a short piece to a clock: a bar of 4/4 lasts 240 ÷ BPM seconds, so 30 seconds hold BPM ÷ 8 bars\n"
            f"• Building a chord loop from Roman numerals (capital = major, small = minor) and turning it into a hook\n"
            f"• Writing a script of 8 to 12 words and checking its words, syllables and seconds\n"
            f"• Recording a voice with Channel EQ, Compressor and DeEsser 2, and ducking the music with sidechain or automation\n"
            f"• Taking a client's feedback and explaining their choices in a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource, no melody supplied and no student work. Students make every sound and write every tune and word themselves; every product is invented\n"
            f"• The ad season is winter and secular: no carols, holiday songs, real jingles, characters or brands\n"
            f"• Requires Logic Pro on a Mac, headphones and a microphone for the voice-over (the Mac's built-in microphone works). Session Players need a recent Logic Pro; the recipes say what to do without them\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology, music production or media music classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"{D.DISCLOSURE_NEW}")
    md = f"""# UPLOAD: Commercial Jingle, original Logic Pro project (TpT 048)

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
({nt} characters; the limit is 80.) "Logic Pro" is in the first 30 characters, and the title has no seasonal word (Winter, Holiday, Christmas, Snow), because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034); the Winter tag and the cover carry the season.

## 2. Description

```
{desc}
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: {"; ".join(SUBJECTS)} (all in `tpt/SUBJECT-OPTIONS.json`, none a heading)
- Tags in tpt.json: {", ".join(TAGS)} (exact entries of `tpt/TAG-OPTIONS.json`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**${PRICE}** (paid), multiple-license price ${PRICE}. $8, in the queue's $7-9 holiday-kit range, for a kit with {np_} pages + {ns} slides, four client briefs, a tempo and chord-loop page, five Logic recipes, voice-over and ducking pages and a two-page worked example.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the first worked-example page, the ducking page and the /25 rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **No music notation, no melody supplied and no third-party material.** The kit draws a speech bubble, waveforms, lanes, chord cards and a ducking curve only. Every client and product is invented, and no real jingle, slogan, brand or person is named; the project text, drawings, recipes and numbers are original Hudson Beat work.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 040 and 045): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Feedback & Reflection" row.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Drummer (the XY pad), Session Players (Bass Player and Keyboard Player, stated as "if your version has them"), the Chord Track (stated as "if your version has it"), Alchemy, Retro Synth, Quick Sampler (its record function), Loop Browser (O), the Library (Y), Channel EQ (lowest band as a high-pass), Compressor and its Side Chain menu, DeEsser 2, Track Stacks, automation (A), Cycle (C) and Bounce (Command-B). Menu paths are given only for File › New, Track › New Tracks and File › Bounce; elsewhere the action is described. Nothing says a preset of a given name exists.
- [ ] **Open questions for the owner:** (1) **Title.** No "Winter", "Holiday" or "Snow" in the title because of TpT's seasonal-title notice (see 1); the Winter tag and the cover carry the season. (2) **Price.** $8, the middle of the $7-9 kit range. (3) **Tag choice.** Winter, Project-based Learning, Projects, Rubrics: the Christmas-Chanukah-Kwanzaa tag is left off on purpose, because the ads are secular winter-season products. (4) **Microphones.** Students need a microphone for the voice-over; the Mac's built-in one works, and the setup page explains how to arrange quiet recording.
"""
    with open(os.path.join(HERE, "UPLOAD.md"), "w", encoding="utf8") as f:
        f.write(md)


if __name__ == "__main__":
    if "--check" not in sys.argv:
        write_upload()
    D.main(sys.modules[__name__])
