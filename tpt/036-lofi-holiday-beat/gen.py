#!/usr/bin/env python3
"""Logic Pro project kit: Lo-Fi Holiday Beat (TpT 036): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content, melodies, drum patterns, the swing numbers, the worked example, drawings, files,
                              page/slide counts, class slots, notes, fonts, fit and overlap, overflow and dead space, banned strings,
                              tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 031): it is not built from the owner's course sheets, so there is no
"what changed" page. Students turn a public-domain carol into a lo-fi hip-hop beat: a 4-bar loop (melody and chords) in a slow, swung
groove with tape, bitcrush and low-pass effects and vinyl noise. The three melodies are given as piano-roll note charts, drawn here in
code from the note lists below (pitch, start and length in sixteenth notes) and checked against them:

  Good King Wenceslas, 4 bars of 4/4. The melody is the 13th-century spring carol "Tempus adest floridum", first published in the
      Finnish collection Piae Cantiones in 1582. Public domain. (J. M. Neale's English words of 1853 are not used.)
  God Rest Ye Merry, Gentlemen, 4 bars of 4/4 in A minor. English traditional melody, in print in the early 1800s (an 1815 piano rondo
      by Samuel Wesley; William Hone's 1820s parody). Public domain. (No words are used.)
  O Tannenbaum (O Christmas Tree), 4 bars of 3/4. Traditional German tune, printed in August Zarnack's school songbook of 1820.
      Public domain. (Ernst Anschuetz's words of 1824 are not used.)

The pitches were taken from two public-domain transcriptions of each tune and are stored below in the ORIGINAL key (G major, E minor,
G major); the charts are those notes moved down a fifth (7 semitones) so that every note is a white key (C major, A minor, C major).
NO LYRICS, NO AUDIO, no recordings and no editions are included; students make every sound in Logic Pro.
Every picture (hero, cards, piano rolls, swing diagram, drum grids, arrangement map) is drawn in code. The shared builder is
../_dmp2_common/dmp2.py (see its README).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

ORIGINAL = True
SLUG = "lofi-holiday-beat"
TITLE = "Lo-Fi Holiday Beat"
ACCENT = "#B8531B"          # this product's single accent: warm lamp-light orange
ACC_LIGHT = "#F7E0CC"
PRICE = "8.00"
CLASSES = 4
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Christmas-Chanukah-Kwanzaa", "Project-based Learning", "Projects"]     # exact entries of tpt/TAG-OPTIONS.json
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # METADATA-GUIDE (a); all in SUBJECT-OPTIONS.json
ANSWER_KEY = None
LISTING_TITLE = "Lo-Fi Beat in Logic Pro | Holiday Carol Project | High School Music Tech"
DESC_START = "Lo-fi beat making for high school music technology:"
DESC_MUST = ["Lo-Fi Holiday Beat", "piano-roll", "no audio", "Good King Wenceslas", "God Rest Ye", "O Tannenbaum", "public domain",
             "swing", "Bitcrusher", "vinyl noise"]
ZIP_DIR = "Lo-Fi Holiday Beat - Hudson Beat"
ZIP_DATE = (2026, 11, 13, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Beat-Making Project</i> | 4 class periods"
DECK_STRAP = "A carol, rewound"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Pentato" + "nix", "Trans-" + "Siberian", "Nut" + "cracker", "Home " + "Alone", "Spoti" + "fy", "You" + "Tube",
                "Lofi " + "Girl", "Chill" + "hop", "Nuj" + "abes", "J " + "Dilla"]

# ================================================================ the project text (original; students read these pages)
OVERVIEW = ("Turn a carol into a lo-fi hip-hop beat. Choose one of three public-domain melodies, enter its four-bar melody and chords into "
            "Logic Pro from a piano-roll note chart, build a slow, swung drum pattern, and make everything sound warm and a little old with "
            "tape wobble, a Bitcrusher, a low-pass filter and vinyl noise. Your finished beat is 60 to 90 seconds long at 70 to 90 BPM, and "
            "people should still be able to name the carol.")
GOALS = ["Enter a melody and chords into Logic Pro’s Piano Roll from a note chart, with the right pitches and lengths",
         "Program a swung lo-fi drum pattern and a bass line at 70 to 90 BPM",
         "Use swing, tape, bitcrushing, a low-pass filter and vinyl noise on purpose, and explain what each one does",
         "Plan, build and mix a 60 to 90 second beat with an intro, beat sections, a break and an outro"]
VOCAB = [("Lo-fi", "Short for low fidelity: music made to sound a little rough, warm and old on purpose, with noise, wobble and muffled highs"),
         ("Swing", "A timing feel in which the off-beat notes land a little late, so a steady pattern bounces instead of marching"),
         ("Bitcrusher", "An effect that lowers a sound’s bit depth and sample rate, adding a gritty, crunchy, digital roughness"),
         ("Public domain", "Music whose copyright has ended, so anyone may use the melody; the three carols in this project are")]
REQS = ["Choose one of the three carols (or a melody your teacher approves) and enter its four-bar melody into a Software Instrument track "
        "in Logic Pro; every pitch and length matches the chart",
        "Set a tempo from 70 to 90 BPM, build one of the lo-fi drum patterns (page @DRUMS) and swing it",
        "Play the chords of the loop under the melody, and add a bass line on the chord roots",
        "Use at least four of the five lo-fi moves: swing, tape, bitcrush, a low-pass filter and vinyl noise (pages @FX1–@FX2)",
        "Build a 60 to 90 second arrangement with at least five layers, an intro, beat sections and an outro",
        "Reflect on how the beat went, in writing or out loud (page @REFLECT)"]
FILE_NAME = "“Your Name – Lo-Fi Holiday Beat – Carol”"
STEPS = ["<b>Choose</b> — Pick one carol and read its chords (carol charts: pages @WENCE, @REST and @TREE)",
         "<b>Plan</b> — Fill in your Beat plan: tempo, drum pattern, chords, and which lo-fi moves you will use (page @PLAN)",
         "<b>Enter the melody and chords</b> — Draw the chart into the Piano Roll and listen for wrong notes (Logic quick reference: page @LOGICREF)",
         "<b>Build the beat</b> — Program a drum pattern (page @DRUMS), swing it, and add a bass line on the chord roots",
         "<b>Make it lo-fi</b> — Add tape wobble and echo, a Bitcrusher, a low-pass filter and vinyl noise (pages @FX1–@FX2)",
         "<b>Arrange and mix</b> — Plan the form on the Arrangement plan (page @ARRANGE), build 60 to 90 seconds with an intro, beat "
         "sections and an outro, balance with volume, pan and EQ, and bounce with the file name format",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your beat. Play it, say which "
         "lo-fi moves you used, and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Lo-fi is about restraint. Keep every effect small enough that the carol is still easy to hear.",
        "Play the melody softly and a little behind the beat. Lo-fi feels relaxed, never rushed.",
        "Add one effect at a time and listen before you add the next. If you cannot hear what an effect does, turn it up and then back down.",
        "Save a new version of your project before each big experiment, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav handed in where your teacher says",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Beat plan, Arrangement plan and Reflection page handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can name the lo-fi moves I used and what each one does"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; your final grade is the average of your self-score and your teacher’s score."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Melody & Chords", ["The melody is missing or mostly wrong", "Several wrong pitches or lengths; chords missing or clashing",
                         "Mostly right, with a few slips; chords fit most of the loop",
                         "Every pitch and length matches the chart; the chords fit",
                         "Exact, with chords and a bass line that support the melody; the carol is unmistakable"]),
    ("Lo-Fi Beat", ["No clear drum pattern or tempo", "A drum pattern, but stiff, or outside 70 to 90 BPM",
                    "A steady drum pattern in range, with some swing", "A swung pattern with kick, snare and hats that fit the tempo",
                    "A relaxed, bouncing groove: swing, drums and bass lock together"]),
    ("Lo-Fi Sound", ["No lo-fi effects", "One or two effects, hard to hear or overdone", "Four lo-fi moves used, each audible",
                     "Four or five moves, balanced, and the student can say what each does",
                     "Every effect is used on purpose, with automation, and the carol is still clear"]),
    ("Arrangement & Mix", ["No clear form; layers cover each other", "A loop with little change; muddy mix",
                           "Intro, beat sections and outro; mostly balanced", "Clear form with a break; layers enter and leave; clean mix",
                           "A form that builds and resolves; every layer audible, melody on top, noise quiet"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices",
                           "Plan and reflection complete, with basic detail", "Clear plan; thoughtful reflection and good answers to questions",
                           "Insightful reflection and a polished, confident presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = [ds[4] for _, ds in RUBRIC]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine · / 25"

TN_REINFORCES = ("Teaches how a style is built from small choices. Students learn that a slow tempo, swing, softened and crushed sounds "
                 "and a layer of noise, not only the notes, make a beat sound lo-fi, and they practice entering notes and chords in Logic "
                 "Pro’s Piano Roll.")
STRUGGLES = ["The notes go in but the tune sounds wrong: check the grid setting and the note lengths against the chart, bar by bar "
             "(Logic quick reference, page @LOGICREF).",
             "The drums sound stiff, not lazy: check that swing is on and that the melody sits a little behind the beat (page @FX1).",
             "The beat is muddy or buried in noise: turn the effects and the vinyl noise down until the carol is clear (page @FX2).",
             "Effects are on but nothing sounds lo-fi: compare with the cards on pages @FX1–@FX2: a low-pass filter, a little wobble, "
             "grit on one sound and quiet noise under everything."]
VAR_EASY = ("Use Good King Wenceslas, loop one four-bar section for the whole beat, and start from pattern A on the drum patterns page or a "
            "Drummer track in a hip-hop style.")
VAR_HARD = ("Write a second four-bar section with a different chord order, add a counter-melody or a chopped copy of the melody in Quick "
            "Sampler, and automate the filter across the whole piece. O Tannenbaum is the hardest chart: it is in 3/4, so it needs the waltz "
            "pattern.")
RESOURCES = [("The three note charts (pages @WENCE, @REST and @TREE)",
              "Hand out one chart each, or let students choose. Pitch names are printed, so nobody needs to read staff notation."),
             ("Lo-fi drum patterns (page @DRUMS)",
              "Students copy a pattern into the Step Sequencer or use a Drummer track. Pattern D is the 3/4 waltz for O Tannenbaum."),
             ("Lo-fi effect cards (pages @FX1–@FX2)",
              "One card each for swing, tape, bitcrushing, vinyl noise and the low-pass filter, with the setting to try and what to listen for."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "Good King Wenceslas as an 84-second lo-fi beat, planned on paper. Use it as a model, not a template; student projects will differ.")]
TN_NOTE = ("Pairs well with a listening day: play the finished beats without saying the title and let the class name the carol. A tune "
           "that people name quickly is a beat that kept the melody.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Melody & Chords (rubric row 1): open the project and compare the Piano Roll with the chart, bar by bar. Check that the chords "
           "match the plan.",
           "Lo-Fi Beat and Lo-Fi Sound (rubric rows 2 and 3): check the tempo is 70 to 90 BPM, that swing is on, and that at least four of "
           "the five lo-fi moves can be heard and named.",
           "Arrangement and Mix (rubric row 4): compare the project with the Arrangement plan (page @ARRANGE). Is there an intro, beat "
           "sections, a break and an outro, and can you hear the melody over the noise?",
           "Plan and Reflection (rubric row 5): the Beat plan (page @PLAN), the questions on the feedback planner and the Reflection "
           "page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Choose a carol, fill in the Beat plan, and enter the melody and chords.",
     "do": "Slides 1–6: the hook, what the project is, the four classes, the five moves and how to read a piano roll. Hand out the project "
           "sheet, the three charts and the Beat plan. Check that each student has a carol and a tempo before they leave.",
     "slides": (1, 6), "pages": ["wence", "rest", "tree", "plan", "proj1", "proj2", "proj3", "vocab"],
     "deck": "A carol, rewound · five moves · reading a piano roll"},
    {"n": 2, "owner": "Build the beat: drums, swing and a bass line.",
     "do": "Slides 7–9: building the beat, straight against swung, and three lo-fi drum patterns. Demonstrate the Step Sequencer and "
           "Q-Swing on the projector, then work time. Walk the room with one question: is it lazy yet?",
     "slides": (7, 9), "pages": ["drums"], "deck": "Build the beat · straight or swung · three drum patterns"},
    {"n": 3, "owner": "Make it lo-fi, plan the form, and build the arrangement and mix.",
     "do": "Slides 10–11: the worked example on paper and the four sound moves. Hand out the Arrangement plan. Then work time; "
           "ask each student to play their first 20 seconds and say which carol they hear.",
     "slides": (10, 11), "pages": ["fx1", "fx2", "arrange"], "deck": "Worked example, 84 seconds · make it lo-fi, keep the tune"},
    {"n": 4, "owner": "Bounce, hand in, present and reflect.",
     "do": "Slides 12–15: what to turn in, the rubric, presentation day and the close. Students bounce, name their files and write "
           "their three feedback questions, then present.",
     "slides": (12, 15), "pages": ["rubric", "present", "reflect"], "deck": "Checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:9.6pt">Make sure every student leaves with a carol, a tempo from 70 to 90 BPM and four chords written on the '
    'Beat plan. If the tempo is only a guess, tap it: tap a steady beat for ten seconds and count the taps.</p></div>'
    '<div class="box"><span class="k">If you only have three classes</span><p style="margin:0;font-size:9.6pt">Merge Classes 2 and 3: '
    'build the beat and add the lo-fi effects on Class 2, then arrange and mix on Class 3 and use Class 4 for bouncing, presentations and reflection.</p></div></div>')
PACING_SIZE = 9.6

# ================================================================ the melodies: (pitch, length in sixteenth notes), bar by bar
# Lengths: 1 = sixteenth, 2 = eighth, 3 = dotted eighth, 4 = quarter, 6 = dotted quarter, 8 = half, 12 = dotted half, 16 = whole.
LEN_NAMES = {1: "16th", 2: "eighth", 3: "dotted eighth", 4: "quarter", 6: "dotted quarter", 8: "half", 12: "dotted half", 16: "whole"}
_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
BLACK_PC = {1, 3, 6, 8, 10}


def midi(p):
    acc = 0 if len(p) == 2 else (1 if p[1] == "#" else -1)
    return 12 * (int(p[-1]) + 1) + _PC[p[0]] + acc


def pname(m):
    return ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"][m % 12] + str(m // 12 - 1)


# The notes in the ORIGINAL key, as found in two public-domain transcriptions of each tune (checked against each other).
SRC = {
    # Good King Wenceslas, G major, 4/4: G G G A | G G D(half) | E D E F# | G(half) G(half)
    "wence": [[("G4", 4), ("G4", 4), ("G4", 4), ("A4", 4)], [("G4", 4), ("G4", 4), ("D4", 8)],
              [("E4", 4), ("D4", 4), ("E4", 4), ("F#4", 4)], [("G4", 8), ("G4", 8)]],
    # God Rest Ye Merry, Gentlemen, E minor, 4/4: the "God" before bar 1 is the last quarter of bar 4 (it leads back into the loop)
    "rest": [[("E4", 4), ("B4", 4), ("B4", 4), ("A4", 4)], [("G4", 4), ("F#4", 4), ("E4", 4), ("D4", 4)],
             [("E4", 4), ("F#4", 4), ("G4", 4), ("A4", 4)], [("B4", 12), ("E4", 4)]],
    # O Tannenbaum, G major, 3/4: the pickup D before bar 1 is the last quarter of bar 4
    "tree": [[("G4", 3), ("G4", 1), ("G4", 4), ("A4", 4)], [("B4", 3), ("B4", 1), ("B4", 6), ("B4", 2)],
             [("A4", 2), ("B4", 2), ("C5", 4), ("F#4", 4)], [("A4", 4), ("G4", 4), ("D4", 4)]],
}
DOWN = 7        # the charts are the source notes moved down a fifth: G major -> C major, E minor -> A minor


def moved(bars, semis):
    return [[(pname(midi(p) - semis), d) for p, d in bar] for bar in bars]


WENCE = moved(SRC["wence"], DOWN)
REST = moved(SRC["rest"], DOWN)
TREE = moved(SRC["tree"], DOWN)
WENCE_CH = [("Cmaj7", "Cmaj7"), ("Cmaj7", "Em7"), ("Am7", "Am7"), ("Fmaj7", "Cmaj7")]
REST_CH = [("Am7", "Em7"), ("Cmaj7", "Am7"), ("Fmaj7", "Dm7"), ("Em7", "Am7")]
TREE_CH = [("Cmaj7", "Cmaj9"), ("Am7", "Am7"), ("Dm7", "G7"), ("G7", "G7")]
CHORD_TONES = {"Cmaj7": {"C", "E", "G", "B"}, "Cmaj9": {"C", "E", "G", "B", "D"}, "Am7": {"A", "C", "E", "G"}, "Em7": {"E", "G", "B", "D"},
               "Dm7": {"D", "F", "A", "C"}, "Fmaj7": {"F", "A", "C", "E"}, "G7": {"G", "B", "D", "F"}}
BASS_ROOT = {"Cmaj7": "C2", "Cmaj9": "C2", "Am7": "A1", "Em7": "E2", "Dm7": "D2", "Fmaj7": "F2", "G7": "G1"}
C_MAJOR = {"C", "D", "E", "F", "G", "A", "B"}      # the charts use white keys only (C major and A minor)

TUNES = {
    "wence": dict(title="Good King Wenceslas", part="the first phrase", who="melody “Tempus adest floridum”", yr="1582",
                  src="A 13th-century spring carol, first published in the Finnish collection Piae Cantiones in 1582. The English words (1853) are not used.",
                  key="C major", time="4/4", bar_len=16, beat=4, bars=WENCE, chords=WENCE_CH, lo=55, hi=64, row_h=36,
                  systems=[(0, 4)],
                  good="The easiest chart: all quarter notes and two halves, one long note at the end of each line. A good first choice.",
                  tip="Bar 1 is C C C D; bar 4 is two long Cs, so the loop breathes before it starts again. Loop all four bars."),
    "rest": dict(title="God Rest Ye Merry, Gentlemen", part="the first line", who="English traditional melody", yr="early 1800s",
                 src="An English traditional melody in print in the early 1800s (an 1815 piano rondo, a parody in the 1820s). The words are not used.",
                 key="A minor", time="4/4", bar_len=16, beat=4, bars=REST, chords=REST_CH, lo=55, hi=64, row_h=36, systems=[(0, 4)],
                 good="A natural for lo-fi: a minor key, steady quarter notes and a long note in bar 4. Sounds moody with seventh chords.",
                 tip="The last quarter of bar 4 (A) is the lead-in to bar 1, so the loop turns around smoothly. Leave it in."),
    "tree": dict(title="O Tannenbaum (O Christmas Tree)", part="the first line", who="traditional German tune", yr="1820",
                 src="A traditional German tune, printed in August Zarnack’s school songbook in 1820. The words (1824) are not used.",
                 key="C major", time="3/4", bar_len=12, beat=4, bars=TREE, chords=TREE_CH, lo=55, hi=65, row_h=34, systems=[(0, 4)],
                 good="The one to pick for a waltz feel: it is in 3/4, so it takes the waltz drum pattern (pattern D). A challenge, and a winter tune with no holiday in its title.",
                 tip="Set the time signature to 3/4 first. Each bar is three beats: count 1-2-3. The last quarter of bar 4 (G) leads back into bar 1."),
}


def tune_notes(key):
    """Flat list of (pitch, start, length) for a tune, start in sixteenths from the first bar."""
    T, out, t = TUNES[key], [], 0
    for bar in T["bars"]:
        for p, d in bar:
            out.append((p, t, d))
            t += d
    return out


def note_count(key):
    return sum(len(b) for b in TUNES[key]["bars"])


def bar_text(bar):
    return " · ".join(f"{p} {LEN_NAMES[d]}" for p, d in bar)


def chord_text(pair):
    return pair[0] if pair[0] == pair[1] else f"{pair[0]} · {pair[1]}"


# ---- the worked example: Good King Wenceslas as a lo-fi beat at 80 BPM, 28 bars = 84 seconds
EX_BPM = 80
EX_BAR_S = 240 / EX_BPM         # 3 s
EX_BARS = 28
EX_SECTIONS = [("Intro", 1, 4), ("Beat A", 5, 12), ("Break", 13, 16), ("Beat B", 17, 24), ("Outro", 25, 28)]
# layer, [(first bar, last bar), ...], how it is made
EX_LAYERS = [("Vinyl noise", [(1, 28)], "a very quiet noise track under the whole beat, a little louder in the break"),
             ("Keys", [(1, 28)], "an electric piano playing the chords, with a low-pass filter closed in the intro and the break"),
             ("Melody", [(1, 12), (17, 24)], "the carol on a soft pluck sound with a Bitcrusher; it rests in the break"),
             ("Bass", [(5, 12), (17, 24)], "a soft sub bass: long notes on the chord roots (C2, E2, A1, F2)"),
             ("Kick", [(5, 12), (17, 24)], "pattern A: kick on beat 1 and just after beat 3"),
             ("Snare", [(5, 12), (17, 24)], "snare on beats 2 and 4"),
             ("Hi-hat", [(5, 16), (17, 24)], "swung eighth-note hats; they carry on through the break"),
             ("Bells", [(17, 24)], "the melody an octave higher on a bell sound, only in Beat B")]
EX_AUTO = [("Keys", "low-pass cutoff", [(1, .2), (5, .6), (13, .25), (17, .8), (28, .15)]),
           ("Melody", "Bitcrusher mix", [(1, .8), (5, .4), (17, .3), (24, .6)]),
           ("Vinyl noise", "volume", [(1, .7), (5, .25), (13, .8), (17, .25), (28, .7)])]
EX_WEAK = "I will make Good King Wenceslas into a chill lo-fi beat."
EX_STRONG = ("My carol is Good King Wenceslas, the four-bar melody from the chart in C major. My beat is lo-fi hip-hop at 80 BPM. The loop "
             "is 4 bars with the chords Cmaj7 | Cmaj7 Em7 | Am7 | Fmaj7 Cmaj7. I use all five lo-fi moves: swing on the hi-hats, tape "
             "wobble and echo on the keys, a Bitcrusher on the melody, a low-pass filter on the keys in the intro and the break, and vinyl noise "
             "under everything. The beat is 28 bars, 84 seconds: intro, beat, break, beat with bells, outro.")
EX_MOVES = [("Swing", "the off-beat hi-hat 16th notes land late (Quantize 1/16 and Q-Swing, page @FX1)"),
            ("Tape", "a little Scanner Vibrato for wobble and a Tape Delay with low feedback on the keys"),
            ("Bitcrush", "a Bitcrusher on the melody, with Mix about half"),
            ("Low-pass", "Channel EQ High Cut closes on the keys in the intro and the break"),
            ("Vinyl noise", "a quiet noise track under the whole beat")]
EX_STAYS = "Every pitch and every length of the melody chart: the carol keeps its tune, so people still know it."
EX_QUESTIONS = ["Which carol did you hear, and how fast did you know?",
                "Where did the beat drop out, and what stayed?",
                "Which lo-fi move did you notice first?"]


def ex_density(bar):
    return sum(1 for _n, spans, _d in EX_LAYERS if any(a <= bar <= b for a, b in spans))


EX_DENS = [ex_density(b) for b in range(1, EX_BARS + 1)]


def mmss(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


# ---- swing: the second 16th of every 8th-note pair is moved from the straight 50% mark to the swing ratio
SWING = [("Straight", 0.50), ("Light swing", 0.58), ("Triplet swing", 2 / 3)]


def swing_offset(ratio):
    """How far (in 16th-note steps) the off-beat 16th moves later: an 8th-note pair lasts 2 steps, and the 2nd note sits at 2 * ratio."""
    return 2 * ratio - 1


def swing_ms(ratio, bpm):
    """Milliseconds later than straight: one 16th note lasts 60000 / bpm / 4 ms."""
    return swing_offset(ratio) * 60000 / bpm / 4


def length_s(bars, bpm):
    return bars * 240 / bpm


# ================================================================ drum patterns: 16 sixteenth steps (4 per beat); the waltz has 12
LANES = ["Hi-hat", "Ghost snare", "Snare", "Kick"]
LANES3 = ["Hi-hat", "Rim / snare", "Kick"]
EIGHTHS = "x.x.x.x.x.x.x.x."
PATTERNS = [
    dict(key="a", name="Pattern A · Lazy kick", feel="relaxed, with space",
         pat={"Hi-hat": EIGHTHS, "Ghost snare": "." * 16, "Snare": "....x.......x...", "Kick": "x.........x....."},
         drums="Kick on beat 1 and an eighth note after beat 3; snare on beats 2 and 4; hats on every eighth note.",
         bass="Soft sub: one long note on each chord root.",
         sounds="A dusty kit with a soft kick, a short snare and quiet, swung hats.",
         tryit="Turn the hats down so they are felt, not heard."),
    dict(key="b", name="Pattern B · Boom-bap", feel="nodding, a little busier",
         pat={"Hi-hat": EIGHTHS, "Ghost snare": "." * 16, "Snare": "....x.......x...", "Kick": "x.....x...x....."},
         drums="Kick on beat 1, the “and” of 2 and the “and” of 3; snare on beats 2 and 4; hats on every eighth note.",
         bass="Follow the kick: short notes on the root, a little behind the beat.",
         sounds="A punchy but soft kick, a snare with a short tail, a touch of room reverb.",
         tryit="Nudge the snare a hair late. Lo-fi drummers rarely sit dead on the grid."),
    dict(key="c", name="Pattern C · Ghost notes", feel="rolling, with little taps",
         pat={"Hi-hat": EIGHTHS, "Ghost snare": ".......x......x.", "Snare": "....x.......x...", "Kick": "x.......x.x....."},
         drums="Kick on beats 1 and 3 and an eighth note after beat 3; snare on 2 and 4; very quiet ghost snare hits on the last sixteenth of beat 2 and the “and” of beat 4; hats on every eighth.",
         bass="Long roots, with a short walk-up note before each chord change.",
         sounds="The same kit as A, with the ghost snare played at very low velocity.",
         tryit="In the Piano Roll or Step Sequencer, set the ghost notes’ velocity low, about a quarter of full."),
]
WALTZ = dict(key="d", name="Pattern D · Waltz (3/4)", feel="slow, rocking, for O Tannenbaum",
             pat={"Hi-hat": "x.x.x.x.x.x.", "Rim / snare": "....x...x...", "Kick": "x.....x....."},
             drums="Kick on beat 1 and the “and” of 2; rim or snare on beats 2 and 3; hats on every eighth note. One bar is 12 steps.",
             bass="One long root per bar.", sounds="Soft kick, a rim click, quiet hats with swing.",
             tryit="Count 1-2-3 out loud while you click the steps. Keep the swing light.")


def pattern(key):
    return next(p for p in PATTERNS if p["key"] == key)


def grid_for(p, name=None):
    """Drum grid of a pattern card as (svg body, w, h); labels logged for the fit check."""
    meas = [{ln: p["pat"][ln] for ln in LANES}]
    return D.grid_body(name or f"grid {p['key']}", meas, [p["name"].split(" · ")[1]], LANES, cw=22, ch=22, gut=140, ls=18, accent_from=0)


def blank_grid(name="grid blank"):
    return D.grid_body(name, [{}], ["Your pattern"], LANES, cw=22, ch=22, gut=140, ls=18, accent_from=0, blank=True)


def waltz_grid(name="grid waltz"):
    """A 12-step grid (3 beats of 4 steps) in the same look as D.grid_body."""
    cw, ch, gut, ls, head = 22, 22, 140, 18, 22
    n = 12
    out = []
    W = gut + n * cw + 4
    for b in range(3):
        out.append(D.t_(gut + (b * 4) * cw + cw / 2, 16, str(b + 1), 14, 700))
        D.lab(f"{name} beats", str(b + 1), 14, cw * 2)
    for r, ln in enumerate(LANES3):
        y = head + r * ch
        out.append(D.t_(gut - 8, y + ch * 0.7, ln, ls, 500, anchor="end"))
        D.lab(f"{name} lanes", ln, ls, gut - 14)
        for i in range(n):
            x = gut + i * cw
            bg = "#e4e4e4" if i % 4 == 0 else "#fff"
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ch}" fill="{bg}" stroke="#000" stroke-width="{1.3 if i % 4 == 0 else .55}"/>')
            if WALTZ["pat"][ln][i] == "x":
                out.append(f'<rect x="{x + 3:.1f}" y="{y + 3:.1f}" width="{cw - 6:.1f}" height="{ch - 6}" rx="2.5" fill="{ACCENT}"/>')
    gh = len(LANES3) * ch
    for xx in (gut, gut + n * cw):
        out.append(f'<line x1="{xx:.1f}" y1="{head - 4}" x2="{xx:.1f}" y2="{head + gh + 4}" stroke="#000" stroke-width="3"/>')
    out.append(f'<rect x="{gut}" y="{head}" width="{n * cw:.1f}" height="{gh}" fill="none" stroke="#000" stroke-width="1.8"/>')
    cap = "Waltz"
    out.append(D.t_(gut + n * cw / 2, head + gh + 21, cap, 16, 700, fill_=ACCENT))
    D.lab(f"{name} captions", cap, 16, n * cw - 12)
    return "".join(out), W, head + gh + 28
def roll_body(notes, nsteps, bar_len, beat, lo, hi, W=1100, row_h=24, first_bar=1, chords=None, name="roll", hl=None, key_w=80, head=30):
    """A piano roll: rows are pitches lo..hi (MIDI numbers, black-key rows grey), columns are sixteenth notes, bars in bold, beats
    in grey. notes = [(pitch name, start, length)]; hl(p) -> True fills a note with the accent. chords = [(start, length, name)]."""
    cw = (W - key_w - 4) / nsteps
    rows = hi - lo + 1
    gh = rows * row_h
    x0 = key_w
    out = []
    for r in range(rows):
        m = hi - r
        y = head + r * row_h
        black = m % 12 in BLACK_PC
        out.append(f'<rect x="{x0}" y="{y}" width="{nsteps * cw:.1f}" height="{row_h}" fill="{"#e3e3e3" if black else "#fff"}" stroke="#bdbdbd" stroke-width="0.6"/>')
        out.append(f'<rect x="0" y="{y}" width="{key_w}" height="{row_h}" fill="#fff" stroke="#000" stroke-width="1"/>')
        if black:
            out.append(f'<rect x="0" y="{y + 1}" width="{key_w * 0.6:.1f}" height="{row_h - 2}" fill="#000"/>')
        else:
            nm = pname(m)
            out.append(D.t_(key_w - 8, y + row_h / 2 + 5.2, nm, 15, 500, anchor="end", fill_=ACCENT if m % 12 == 0 else "#000"))
            D.lab(name + " keys", nm, 15, key_w - 14)
    for s in range(nsteps + 1):
        x = x0 + s * cw
        if s % bar_len == 0:
            out.append(f'<line x1="{x:.1f}" y1="{head - 4}" x2="{x:.1f}" y2="{head + gh}" stroke="#000" stroke-width="3"/>')
        elif s % beat == 0:
            out.append(f'<line x1="{x:.1f}" y1="{head}" x2="{x:.1f}" y2="{head + gh}" stroke="#7a7a7a" stroke-width="1.1"/>')
        elif s % 2 == 0:
            out.append(f'<line x1="{x:.1f}" y1="{head}" x2="{x:.1f}" y2="{head + gh}" stroke="#d6d6d6" stroke-width=".6"/>')
    nb = nsteps // bar_len
    for b in range(nb):
        out.append(D.t_(x0 + (b + .5) * bar_len * cw, head - 9, str(first_bar + b), 18, 700))
        D.lab(name + " bars", str(first_bar + b), 18, bar_len * cw - 6)
    fs = min(row_h - 9, 16)
    for p, s, d in notes:
        r = hi - midi(p)
        assert 0 <= r < rows, (p, lo, hi)
        x, y, w, h = x0 + s * cw + 1.5, head + r * row_h + 2.5, d * cw - 3, row_h - 5
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="{ACCENT if hl and hl(p) else "#000"}"/>')
        txt = p[:-1]
        if w >= D.text_w(txt, fs) + 10:
            out.append(D.t_(x + w / 2, y + h / 2 + fs * .35, txt, fs, 700, fill_="#fff"))
            D.lab(name + " notes", txt, fs, w - 8)
    out.append(f'<rect x="{x0}" y="{head}" width="{nsteps * cw:.1f}" height="{gh}" fill="none" stroke="#000" stroke-width="2"/>')
    H = head + gh + 8
    if chords:
        yc = head + gh + 10
        out.append(D.t_(key_w - 8, yc + 24, "CHORDS", 14, 700, anchor="end", fill_=ACCENT))
        D.lab(name + " keys", "CHORDS", 14, key_w - 14)
        for s, d, ch in chords:
            out.append(f'<rect x="{x0 + s * cw + 2:.1f}" y="{yc}" width="{d * cw - 4:.1f}" height="34" rx="6" fill="{ACC_LIGHT}" stroke="{ACCENT}" stroke-width="2"/>')
            out.append(D.t_(x0 + (s + d / 2) * cw, yc + 24, ch, 20, 700))
            D.lab(name + " chords", ch, 20, d * cw - 12)
        H = yc + 44
    return "".join(out), W, H


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




def tune_roll(key, a, b, W=1100, name=None, chords=True):
    """Bars a..b-1 (0-based) of a tune as a roll."""
    T = TUNES[key]
    bl = T["bar_len"]
    nts = [(p, s - a * bl, d) for p, s, d in tune_notes(key) if a * bl <= s < b * bl]
    chs = []
    for i in range(a, b):
        c1, c2 = T["chords"][i]
        if c1 == c2:
            chs.append(((i - a) * bl, bl, c1))
        else:
            chs += [((i - a) * bl, bl // 2, c1), ((i - a) * bl + bl // 2, bl // 2, c2)]
    return roll_body(nts, (b - a) * bl, bl, T["beat"], T["lo"], T["hi"], W, T["row_h"], a + 1, chs if chords else None,
                     name or f"roll {key} {a}")


def swing_body(W=1100, name="swing pic", bpm=EX_BPM):
    """One bar of 16th-note hi-hats three times: straight, light swing and triplet swing. The even steps stay on the grid (black);
    the odd steps (accent) move later by swing_offset(ratio) of a step."""
    gut, head, rh = 250, 34, 78
    cw = (W - gut - 20) / 16
    out = []
    for b in range(4):
        x = gut + (b * 4) * cw
        out.append(D.t_(x + 2 * cw, 22, str(b + 1), 20, 700))
        D.lab(name + " beats", str(b + 1), 20, 4 * cw - 10)
    for r, (nm, ratio) in enumerate(SWING):
        y = head + r * rh
        cy = y + rh / 2
        lbl = f"{nm.upper()} · {round(ratio * 100)}%"
        out.append(D.t_(gut - 14, cy + 7, lbl, 20, 700, anchor="end", fill_=ACCENT if r else "#000"))
        D.lab(name + " rows", lbl, 20, gut - 24)
        out.append(f'<rect x="{gut}" y="{y + 4}" width="{16 * cw:.1f}" height="{rh - 8}" fill="#fff" stroke="#000" stroke-width="1.6"/>')
        for s in range(0, 16, 4):
            out.append(f'<rect x="{gut + s * cw:.1f}" y="{y + 4}" width="{4 * cw:.1f}" height="{rh - 8}" fill="{"#ececec" if (s // 4) % 2 == 0 else "#fff"}"/>')
        for s in range(0, 17, 4):
            out.append(f'<line x1="{gut + s * cw:.1f}" y1="{y + 4}" x2="{gut + s * cw:.1f}" y2="{y + rh - 4}" stroke="#7a7a7a" stroke-width="1.4"/>')
        for s in range(16):
            off = swing_offset(ratio) if s % 2 == 1 else 0
            x = gut + (s + off) * cw + cw / 2
            out.append(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="11" fill="{ACCENT if s % 2 == 1 else "#000"}"/>')
    out.append(f'<rect x="{gut}" y="{head + 4}" width="{16 * cw:.1f}" height="{3 * rh - 8}" fill="none" stroke="#000" stroke-width="2.4"/>')
    ms1, ms2 = swing_ms(SWING[1][1], bpm), swing_ms(SWING[2][1], bpm)
    cap = f"At {bpm} BPM a 16th note lasts {60000 / bpm / 4:g} ms: light swing is {ms1:g} ms late, triplet swing {ms2:g} ms late"
    out.append(D.t_(W / 2, head + 3 * rh + 28, cap, 21, 500))
    D.lab(name + " cap", cap, 21, W - 20)
    return "".join(out), W, head + 3 * rh + 44


def drums_body(name="drums pic"):
    a = grid_for(pattern("a"), name=name + " a")
    c = grid_for(pattern("c"), name=name + " c")
    cap = "Same grid, two lo-fi feels: pattern A (lazy kick) and pattern C (ghost notes on top)"
    return D.stack([a, c, (D.t_(430, 22, cap, 22, 500), 860, 34)], 14)


def cycle_body(W=1600, name="cycle pic", fs=30, cs=22):
    return cards_body([("Choose", "a carol"), ("Plan", "your beat"), ("Enter", "melody + chords"), ("Beat", "drums + swing"),
                       ("Lo-fi it", "tape · crush · vinyl")], "Then arrange, mix, bounce, present and reflect", W, name, fs, cs)


def hero_body():
    W = 1100
    roll = tune_roll("wence", 0, 4, 1000, "hero roll", chords=False)
    out = [f'<g transform="translate(50,0)">{roll[0]}</g>']
    y0 = roll[2] + 6
    names = ["SWING", "TAPE", "VINYL"]
    pw, gap, x0 = 300, 40, 60
    for i, nm in enumerate(names):
        x = x0 + i * (pw + gap)
        cx = x + pw / 2
        out.append(f'<line x1="{cx}" y1="{y0}" x2="{cx}" y2="{y0 + 46}" stroke="#000" stroke-width="5" stroke-dasharray="3 10" stroke-linecap="round"/>')
        out.append(f'<polygon points="{cx - 16},{y0 + 42} {cx + 16},{y0 + 42} {cx},{y0 + 72}" fill="#000"/>')
        out.append(f'<rect x="{x}" y="{y0 + 84}" width="{pw}" height="78" rx="39" fill="{ACCENT if i != 1 else "#000"}"/>')
        out.append(D.t_(cx, y0 + 84 + 39 + 14, nm, 40, 700, fill_="#fff"))
        D.lab("hero pills", nm, 40, pw - 50)
    return "".join(out), W, y0 + 168


def map_body(W=1600, name="map", fs=24, ts=20):
    """The worked example's whole 28-bar arrangement: sections, eight layers (some in two parts) and three automation lanes."""
    gx = 300
    pwid = W - gx - 16

    def X(bar):
        return gx + pwid * (bar - 1) / EX_BARS

    out = []
    sh = 54
    shade = {"Intro": "#4a4a4a", "Beat A": "#000", "Break": "#4a4a4a", "Beat B": ACCENT, "Outro": "#4a4a4a"}
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
    for i, (ly, par, pts) in enumerate(EX_AUTO):
        yy = ay0 + 16 + i * (lh + lg + 6)
        lbl = f"{ly} · {par}".upper()
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, lbl, 18, 700, anchor="end"))
        D.lab(name + " lanes", lbl, 18, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh + 6}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        xy = [(X(t), yy + lh + 2 - v * (lh - 2)) for t, v in pts]
        out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in xy)}" fill="none" stroke="{ACCENT}" stroke-width="4" stroke-linejoin="round"/>')
        for a, b in xy:
            out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="4.5" fill="#000"/>')
    ty = ay0 + 16 + len(EX_AUTO) * (lh + lg + 6) + 4
    ticks = (1, 5, 9, 13, 17, 21, 25, 29)
    for bar in ticks:
        t = (bar - 1) * EX_BAR_S
        lbl = mmss(t)
        anc = "start" if bar == 1 else ("end" if bar == 29 else "middle")
        out.append(f'<line x1="{X(bar):.1f}" y1="{ty - 6}" x2="{X(bar):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(bar) + (2 if bar == 1 else (-2 if bar == 29 else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 80)
    cap = f"Bar 1 to bar 28 at {EX_BPM} BPM: {EX_BARS} bars × {EX_BAR_S:g} seconds = {EX_BARS * EX_BAR_S:g} seconds"
    out.append(D.t_(gx + pwid / 2, ty + 8 + ts + 34, cap, ts + 2, 500))
    D.lab(name + " cap", cap, ts + 2, pwid)
    return "".join(out), W, ty + 8 + ts + 48


DRAWINGS = {"hero": hero_body, "cycle": lambda: cycle_body(1600), "roll": lambda: tune_roll("wence", 0, 4, 1100, "roll deck"),
            "swing": lambda: swing_body(1100, "swing deck"), "drums": lambda: drums_body(), "map": lambda: map_body(1600, "map pic")}
DRAWING_PX = {"hero": 1900, "cycle": 2000, "roll": 2000, "swing": 2000, "drums": 2000, "map": 2000}
SIDE = {"cycle": ["Choose a carol and a tempo", "Plan your beat and lo-fi moves", "Enter the melody and chords",
                  "Beat first, then lo-fi it, then arrange"],
        "roll": ["Higher bar means higher pitch", "Longer bar means a longer note", "Left to right is time, bar by bar",
                 "The chords are one idea that fits"],
        "swing": ["Black dots stay on the grid", "Orange dots land later and later", "Straight marches, swing bounces",
                  "Q-Swing in the Region inspector"],
        "map": ["An invented 84-second beat", "Five sections: 4, 8, 4, 8, 4 bars", "Eight layers, three automation lanes",
                "Beat B has the most layers"]}


def label_extras():
    for k, T in TUNES.items():
        for a, b in T["systems"]:
            tune_roll(k, a, b, 1100, f"page {k} {a}")
    swing_body(1100, "page swing")
    tune_roll("wence", 0, 4, 1100, "page example roll")
    map_body(1250, "page map", 24, 20)
    cycle_body(1250, "page cycle", 28, 20)
    roll_body([], 64, 16, 4, 55, 67, 1100, 14, 1, None, "blank roll")
    for p in PATTERNS:
        grid_for(p)
    blank_grid()
    waltz_grid()


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Lo-Fi Holiday Beat", "A carol, slowed down and dusted off.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you are going to turn a carol everyone knows "
     "into a lo-fi hip-hop beat in Logic Pro, with swing, tape wobble, a Bitcrusher and vinyl noise. The three melodies are public domain "
     "and arrive as note charts, so every student can enter them without reading staff notation."),
    (1, "listen", "Think: what makes music sound lo-fi?", "Think, then share|Teacher: say or hum the first line of Good King Wenceslas, "
     "first bright and crisp, then slow, soft and a little behind the beat.|What changed?|What would make it sound warm or old?|"
     "Which sounds would you add?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker: you say or hum the first line yourself, first "
     "bright and crisp and then slow, soft and a little late. Students will say slower, quieter and bouncier and, if they know the style, "
     "crackle and warmth. Write their words on the board; the project turns each one into a tool."),
    (1, "bullets", "What is Lo-Fi Holiday Beat?", "Choose a public-domain carol|Enter its melody and chords in Logic Pro|Make it lo-fi: "
     "swing, tape, bitcrush, vinyl noise|Finish a 60 to 90 second beat",
     "The project in four lines. Students choose Good King Wenceslas, God Rest Ye Merry, Gentlemen or O Tannenbaum; all three melodies are "
     "public domain, so anyone may use them. They enter the melody and chords from a piano-roll chart, then build a slow, swung beat and "
     "make it sound lo-fi. The finished beat is 60 to 90 seconds. If a student would rather use another carol, a teacher-approved "
     "public-domain melody works, and a blank piano roll is provided."),
    (1, "days", "Four classes", "",
     "The shape of the project. Class 1: hook, choose a carol, fill in the Beat plan and enter the melody and chords. Class 2: build the "
     "beat, with drums, swing and a bass line. Class 3: make it lo-fi with tape, a Bitcrusher, a low-pass filter and vinyl noise, then plan "
     "the form, arrange and mix. Class 4: bounce, hand in, present and reflect. Hand out the project sheet, the charts and the Beat plan now."),
    (1, "pic", "Five moves, then finish", "cycle",
     "Class 1. The five moves in order: choose, plan, enter, beat and lo-fi it. After that students arrange, mix, bounce, present and "
     "reflect. Point to each box and say roughly when it happens: choosing and planning today, entering and the beat on Class 2, lo-fi "
     "sound and arranging on Class 3. The picture and its short labels are drawn for this kit."),
    (1, "pic", "Reading a piano roll", "roll",
     "Class 1. This is the Piano Roll view of the four-bar Good King Wenceslas loop, drawn the same way as the charts on students' pages. "
     "A higher bar is a higher pitch, a longer bar is a longer note, and time runs left to right. The chord boxes underneath are the loop's "
     "chords; other chords can work. Ask a student to read bar 2 aloud: C, C, then a long G."),
    (2, "steps", "Build the beat", "Set the tempo, 70 to 90 BPM|Pick a drum pattern: kick, snare, hats|Enter it in the Step Sequencer, or "
     "start from a Drummer track|Swing it: Quantize 1/16, then Q-Swing|Add a soft bass on the chord roots",
     "Class 2. Demonstrate on the projector: set the tempo between 70 and 90 BPM, make a Drum Machine Designer track and open the Step "
     "Sequencer, or make a Drummer track in a hip-hop style. Click in pattern A from page 15. Then select the region, set Quantize to 1/16 "
     "and raise Q-Swing until the hats bounce. Add a soft bass playing one long note on each chord root. Menu names move between Logic versions."),
    (2, "pic", "Straight or swung?", "swing",
     "Class 2. One bar of sixteenth-note hi-hats three times. The black dots are on the grid in all three rows; the orange dots are the "
     "off-beat sixteenths, and each row moves them later. At 80 BPM a sixteenth lasts 187.5 milliseconds, so light swing is 30 ms late and "
     "triplet swing is 62.5 ms late. Logic's Q-Swing slider has its own scale, so students compare by ear."),
    (2, "pic", "Three lo-fi drum patterns", "drums",
     "Class 2. The same 16-step grid in two lo-fi feels. Pattern A is the lazy kick: kick on beat 1 and just after beat 3, snare on 2 and 4. "
     "Pattern C adds very quiet ghost snare hits between the backbeats. Students copy a pattern from page 15 into the Step Sequencer. "
     "Ask: which of your lo-fi moves is this, swing, drums or sound? O Tannenbaum needs pattern D, the 3/4 waltz."),
    (3, "pic", "Worked example: 84 seconds", "map",
     "Class 3. An invented beat described on paper, nothing here is audio: Good King Wenceslas at 80 BPM. Twenty-eight bars at 3 seconds a "
     "bar is 84 seconds, in five sections of 4, 8, 4, 8 and 4 bars. Eight layers join and leave, and Beat B has the most. Three automation "
     "lanes keep the sound moving. Students plan their own on the Arrangement plan."),
    (3, "bullets", "Make it lo-fi, keep the tune", "Low-pass the keys: soften the highs|Tape: a little wobble and echo|Bitcrusher on one "
     "sound, not everything|Vinyl noise: so quiet you miss it when it stops",
     "Class 3. The four sound moves in one idea: each one is small, and the melody stays the star. Close the High Cut filter in Channel EQ "
     "on the keys; add a little Scanner Vibrato and a Tape Delay with low feedback; put a Bitcrusher on one sound only; and place a very "
     "quiet noise track under everything. Ask each student to play their first 20 seconds and say whether a listener could name the carol."),
    (4, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Lo-Fi Holiday Beat – Carol|Beat plan, "
     "Arrangement plan, Reflection|Rubric self-score|Three questions for classmates",
     "Class 4. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, Lo-Fi "
     "Holiday Beat, then the carol, in that order. Check that every beat is between 60 and 90 seconds before students bounce."),
    (4, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and yours. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (4, "bullets", "Presentation day", "Play your beat, then name the carol|Say which lo-fi moves you used|Your three questions "
     "for classmates|Answer at least 2 of each classmate’s",
     "Class 4, presentations. Each student plays their beat, says which carol it is and names the lo-fi moves they used, then takes "
     "questions. Students write three questions they want classmates to answer, and answer at least two of each classmate's. "
     "Ask the class to name the carol before the presenter does."),
    (4, "closer", "One last thing…", "You picked a carol.|You slowed it down.|You added the dust.|Now press play.",
     "Close with the listening day: play the finished beats without saying the title and let the class name each carol. A melody that "
     "people name quickly is a beat that kept the tune. Ask a few students which lo-fi move changed the mood most. No audio is included "
     "in this kit; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "4 class periods, slide by slide"), ("wence", "Piano-roll chart", "Good King Wenceslas, bar by bar"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 6, 8, 9, 10, 13]
SHOTS3 = [("wence", "Wenceslas"), ("rest", "God Rest Ye"), ("tree", "O Tannenbaum"), ("drums", "Drum patterns"),
          ("fx1", "Swing and tape"), ("fx2", "Bitcrush and vinyl"), ("example", "Worked example"), ("arrange", "Arrangement plan")]

# ================================================================ page plan (teacher pages 2-11, student pages 12-26)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "tunes", "example", "example2", "wence", "rest", "tree",
        "drums", "fx1", "fx2", "plan", "arrange", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "wence", "fx1", "rubric"]

COVER_A = "Turn a carol into lo-fi hip-hop"
COVER_C = "Logic Pro · piano-roll charts · swing, tape, vinyl · intro slides"
PDF_COVER = dict(a=26, b=58, c=14, art=7.3)
SQ_COVER = dict(a=40, b=150, c=27, art=740, gap=40)
SQ_B_LINES = ["Lo-Fi", "Holiday Beat"]
SQ_SUB = "4 class periods · 3 carols · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, charts, drum patterns and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Three note charts, drum patterns, effect cards, a worked example and plans", 28)}
SQ_BANDS = {1: "Choose <em>·</em> enter <em>·</em> swing <em>·</em> lo-fi it <em>·</em> arrange",
            2: "Piano roll <em>·</em> swing <em>·</em> drum patterns <em>·</em> worked example",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, recordings, lyrics, artists or albums are named or included. The three melodies are public domain and appear "
             "only as note charts. Students make every sound in their beats themselves, from the instruments, drum kits and plug-ins in Logic.")
CREDITS = ["Piano-roll note charts of three public-domain melodies (Good King Wenceslas, 1582; God Rest Ye Merry, Gentlemen, a traditional "
           "English melody; O Tannenbaum, 1820), the worked example, the drum patterns, the effect cards, the hero, card, swing and "
           "arrangement drawings and all layouts: original work, Hudson Beat. No lyrics, recordings or published editions are included.",
           "No audio, video, album art, screenshots, presets, templates, links or chart data are included. No student work is included."]
LOGIC_INTRO = ("Where to find the tools a Lo-Fi Holiday Beat is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add a Software Instrument track with Track › New Tracks…. Use one track for the "
              "melody and more for chords, bass and drums."),
             ("Tempo and time signature", "Type the tempo in the control bar (70 to 90 BPM). O Tannenbaum is in 3/4: set the time signature "
              "before you enter notes (the control bar, or the Signature track in Global Tracks)."),
             ("Make a region, open the Piano Roll", "With the Pencil tool, click on the track where bar 1 starts to make an empty MIDI "
              "region, then double-click it to open the Piano Roll editor."),
             ("Draw notes and chords", "Pick a grid value in the Piano Roll’s Snap menu (for example, 1/16 note) so notes land on the "
              "chart’s sixteenth-note grid, click with the Pencil to add a note and drag its right edge to change its length. Draw a chord as "
              "notes stacked in one column. A MIDI keyboard is optional."),
             ("Fix wrong notes", "Select a note and drag it up or down a row, or press delete. To play a melody an octave lower, select the "
              "region and change Transpose in the Region inspector by 12 steps."),
             ("Swing", "Select the MIDI region. In the Region inspector, set Quantize to a 1/16-note value, then raise Q-Swing so the off-beat "
              "notes land late. The slider is Logic’s own scale, so compare with the diagram on page " + str(PLAN.index("fx1") + 1) + " by ear."),
             ("Drums", "Make a Drummer track and pick a hip-hop style, or make a Drum Machine Designer track and open the Step Sequencer: "
              "click the 16 steps for each drum, as on the patterns on page " + str(PLAN.index("drums") + 1) + "."),
             ("Bass, keys and sounds", "Browse the Library (press Y) for instruments, or open Alchemy, Retro Synth or Vintage Electric Piano. "
              "A Session Player (Bass Player, Keyboard Player) can follow a Chord Track in Global Tracks."),
             ("Tape and bitcrush", "Add plug-ins in a channel strip’s Audio FX slots. For wobble try Scanner Vibrato or a light Chorus; for echo "
              "try Tape Delay with low feedback; for warmth try ChromaGlow if your version has it, or a little Overdrive. For grit use Bitcrusher."),
             ("Low-pass filter", "In Channel EQ, switch on the High Cut filter (a low-pass filter) and slide it down until the highs soften. "
              "Draw its frequency with automation to open and close it."),
             ("Vinyl noise", "Search the Loop Browser (press O) for a noise or crackle loop, or make quiet noise from a synthesizer’s noise "
              "oscillator (Alchemy has one) and filter it with Channel EQ. Keep it very low in the mix."),
             ("Automation, mixing and bounce", "Press A to show automation, pick a parameter such as a filter cutoff or volume, and draw points. "
              "Press X for the Mixer. Then File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx "
              "and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my beat:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">Wrong notes: the chart pages (pages @WENCE, @REST and @TREE) list every note by bar, and the Logic quick reference (page @LOGICREF) shows the grid.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Stiff drums: the swing card (page @FX1) and slide 8 show what swing does.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">A muddy or noisy mix: the effect cards (page @FX2), the mix checks on the Arrangement plan (page @ARRANGE) and slide 11.</li>'
    '<li style="font-size:12pt;margin-bottom:0">Effects with no lo-fi feel: the effect cards (pages @FX1–@FX2) and the worked example (pages @EXAMPLE–@EXAMPLE2).</li></ul></div>')
TN1_SIZE = 12.8
PROJ_SIZE = 12.6
VOCAB_GAP = 14
LOGIC_SIZE = 10.2
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ small page helpers
CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; } table.sg td, table.sg th { border: 1pt solid #000; text-align: center; "
          "padding: 0; font-size: 8pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.2in; font-size: 9pt; } "
          "table.sg td.b { border-left: 2.2pt solid #000; } </style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, tune sources, "
              "worked example (2 pages)"),
             ("Student pages", "wence", "reflect", "Three note charts, drum patterns, effect cards (2 pages), Beat plan, Arrangement plan, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period beat-making project for high school music technology. Each '
             f'student chooses one of three public-domain carols, enters its melody and chords into Logic Pro from a piano-roll note chart, and '
             f'turns it into a lo-fi hip-hop beat: a slow, swung groove with tape wobble, a Bitcrusher, a low-pass filter and vinyl noise. The beat '
             f'is 60 to 90 seconds. Students plan it, build and mix it, present it and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Decide which carols to offer (page {D.IX("tunes")}) and check the setup (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("wence")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> see the variations on page {D.IX("tn1")}: one looped section on Good King Wenceslas, or a counter-melody.</li>'
             f'<li><b>Carol choice:</b> two winter or Christmas carols and a winter tune about an evergreen (page {D.IX("tunes")}). Offer the ones that suit your school.</li>'
             f'<li><b>Feedback:</b> students write three questions and answer classmates’ on a class board or on paper.</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that a '
             f'style is made of small choices: a slow tempo, swing, softened sounds and a little noise turn the same tune into lo-fi.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Beat making · Logic Pro<br>Turn a carol everyone knows into a lo-fi hip-hop beat.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13pt;line-height:1.5">One original beat, 60 to 90 seconds long, built on a public-domain carol. The melody is '
             f'entered from a piano-roll chart and stays recognizable; the tempo is 70 to 90 BPM, the drums are swung, and the sounds are '
             f'softened, wobbled and crushed with a layer of vinyl noise. It has at least five layers and an intro, beat sections and an outro, is '
             f'mixed with volume, pan and EQ, and uses at least four of the five lo-fi moves. Students hand in a bounced .mp3 or .wav and the zipped '
             f'.logicx project, plus their plans and a reflection, then play the beat and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12.6pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.6pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12.6pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.4pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}, music technology or music production</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: choose and enter, build the beat, make it lo-fi and arrange, present and reflect</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Piano Roll, instruments, Step Sequencer or Drummer, Q-Swing, effects, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a place to hand in files and a class board or paper for feedback</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>Rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s and the '
             f'teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:11.6pt">Students should know how '
             f'to open a project, add a software instrument and use the mixer in Logic. Nobody needs to read music: the charts name every '
             f'pitch and length.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Beat-making project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.8pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the final listen.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav, the zipped .logicx and the reflection.</li>'
             f'<li><b>The three charts</b>, printed (pages {D.IX("wence")}, {D.IX("rest")} and {D.IX("tree")}), or shown on the projector.</li>'
             f'<li><b>The drum patterns and effect cards</b>, printed (pages {D.IX("drums")}–{D.IX("fx2")}).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("wence")}–{D.IX("reflect")}).</li>'
             f'<li><b>A MIDI keyboard</b> is optional: every melody can be drawn with the mouse.</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.8pt;margin-bottom:7pt") for c in [
                 "Decide which carols you will offer (page @TUNES).".replace("@TUNES", str(D.IX("tunes"))),
                 "Open Logic Pro on a student computer: can you make a track, open the Piano Roll and hear playback through headphones?",
                 "Check that the plug-ins on page @FX1 and page @FX2 are installed (Bitcrusher, Channel EQ, Tape Delay) and that your Logic has a noise or crackle loop or a synthesizer with a noise oscillator.".replace("@FX1", str(D.IX("fx1"))).replace("@FX2", str(D.IX("fx2"))),
                 "Read the worked example (pages @A–@B).".replace("@A", str(D.IX("example"))).replace("@B", str(D.IX("example2")))]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.6pt">Students enter the notes but get a wrong one, the drums stay stiff, the melody is buried in noise, '
             f'or the effects are on but nothing sounds lo-fi. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.4pt">Ask while students work: is it lazy yet? Can you hear the carol? Which lo-fi move is this?</li>'
             f'<li style="font-size:11.4pt">On Class 1, tap 70, 80 and 90 BPM on the desk so students feel how slow lo-fi is.</li>'
             f'<li style="font-size:11.4pt">A student who is stuck on drums can start from a Drummer track in a hip-hop style and swing it.</li></ul></div>'
             f'{D.H2("Choosing carols")}'
             f'<div class="box"><span class="k">A respectful choice</span><p style="margin:0;font-size:11.2pt;line-height:1.4">'
             f'Good King Wenceslas is a winter carol about snow and kindness, God Rest Ye Merry, Gentlemen is a Christmas carol, and O Tannenbaum is a '
             f'winter tune about an evergreen tree. Offer the ones that fit your school and let students choose. If a student prefers another '
             f'melody, a public-domain one you approve (first published in the United States in 1930 or earlier) works with the same plan, and '
             f'the blank piano roll on page {D.IX("plan")} is there for their own chart.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.2pt;line-height:1.4">'
             f'Bass-heavy beats and loud peaks are tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


def tunes_page(n, wm=False):
    rows = ""
    for k in ("wence", "rest", "tree"):
        T = TUNES[k]
        rows += (f"<tr><td><b>{T['title']}</b><br>{T['part']}</td><td>{T['who']}<br>{T['yr']}</td><td>{T['key']}, {T['time']}<br>"
                 f"{len(T['bars'])} bars, {note_count(k)} notes</td><td>{T['good']}</td></tr>")
    srcs = "".join(f"<li><b>{TUNES[k]['title']}:</b> {TUNES[k]['src']}</li>" for k in ("wence", "rest", "tree"))
    inner = (f'<p style="margin:0 0 4pt;font-size:11.6pt;line-height:1.42">All three melodies are in the public domain, and each is printed '
             f'here as a note chart only: no lyrics, no recordings and no published edition. The charts are written in C major or A minor (all white keys) '
             f'so the pitches are easy to read, and checked against the notes in code.</p>'
             f'<table class="t" style="font-size:10.4pt"><tr><th style="width:21%">Tune</th><th style="width:24%">Source · year</th><th style="width:19%">In this kit</th>'
             f'<th>Good for</th></tr>{rows}</table>'
             f'{D.H2("Where the tunes come from")}<ul style="font-size:11pt">{srcs}</ul>'
             f'{D.H2("The public-domain rule")}<p style="font-size:11.4pt;line-height:1.42">In 2026 a melody is in the public domain in the United '
             f'States when it was first published in 1930 or earlier (1931 from 1 January 2027). If a student suggests another carol or '
             f'winter song, check its first publication date before you approve it, and never use a recording, a film or pop version, or '
             f'its lyrics unless they are public domain too.</p>'
             f'{D.H2("Picking a tune for a student")}<ul style="font-size:11pt"><li><b>First time in the Piano Roll:</b> Good King Wenceslas. Mostly quarter notes, and a loop that repeats cleanly.</li>'
             f'<li><b>Wants a moody sound:</b> God Rest Ye Merry, Gentlemen. A minor key, so the seventh chords sound dark and warm.</li>'
             f'<li><b>Wants a challenge, or a waltz:</b> O Tannenbaum, in 3/4 with the waltz pattern.</li></ul>'
             f'<div class="cols" style="gap:12pt;margin-top:4pt"><div class="box acc-b"><span class="k">Reading the charts</span><p style="margin:0;font-size:10.6pt;line-height:1.38">'
             f'Pitch names run down the left; middle C is C4. Bold lines are bars, grey lines are beats. A note’s length is the name beside it: '
             f'16th, eighth, dotted eighth, quarter, dotted quarter, half or dotted half. Chords are one idea that fits, not the only one.</p></div>'
             f'<div class="box"><span class="k">Why a four-bar loop</span><p style="margin:0;font-size:10.6pt;line-height:1.38">'
             f'Lo-fi beats are built on a short loop that repeats. Each chart ends so that it leads back into bar 1; where a tune starts with a '
             f'lead-in note, that note sits at the end of bar 4.</p></div></div>')
    return D.page("Tune sources and the public-domain rule", "TEACHER", "Tunes", inner, n, key="tunes")


def bass_roll(key, name="bass roll"):
    T = TUNES[key]
    nb = len(T["bars"])
    return roll_body([], nb * T["bar_len"], T["bar_len"], T["beat"], 36, 48, 1100, 17, 1, None, name)


def chart_page(key):
    def build(n, wm=False):
        T = TUNES[key]
        glance = (f'<p style="margin:0 0 3pt;font-size:10.4pt"><b>{T["title"]}</b>, {T["part"]} · {T["who"]}, {T["yr"]} · {T["key"]}, {T["time"]} · '
                  f'{len(T["bars"])} bars · {note_count(key)} notes</p>')
        systems = "".join(f'<div style="margin:0 0 2pt">{D.body_svg(tune_roll(key, a, b, 1100, f"page {key} {a}"))}</div>' for a, b in T["systems"])
        nb = len(T["bars"])
        rr = "".join(f"<tr><td style='width:11%'><b>{i + 1}</b></td><td>{bar_text(T['bars'][i])}</td><td style='width:22%;white-space:nowrap'>{chord_text(T['chords'][i])}</td></tr>"
                     for i in range(nb))
        tab = (f'<table class="t" style="font-size:10pt;line-height:1.16;margin:2pt 0 3pt"><tr><th>Bar</th><th>Notes (pitch, length)</th><th>Chords</th></tr>{rr}</table>')
        pat = "pattern D, the waltz" if T["time"] == "3/4" else "pattern A, B or C"
        about = f'{T["src"]} {T["tip"]} Chords shown are one idea that fits; try others by ear. Drums: {pat} (page {D.IX("drums")}).'
        bass = D.body_svg(bass_roll(key, f"page {key} bass"))
        inner = (f'{glance}{systems}{tab}'
                 f'<div class="box acc-b" style="margin-top:4pt;padding:4pt 10pt"><span class="k">About this chart</span><p style="margin:0;font-size:9.4pt;line-height:1.3">'
                 f'{about}</p></div>'
                 f'<span class="k" style="margin-top:6pt">Your turn: write a bass line on the chord roots (pencil), one long note per chord</span>'
                 f'<div style="margin-top:2pt">{bass}</div>')
        return D.page(f"Note chart · {T['title']}", "STUDENT", "Class 1", inner, n, wm, name=True, key=key)
    return build


def pattern_card(p):
    if p["key"] == "d":
        body, w, h = waltz_grid()
    else:
        body, w, h = grid_for(p)
    txt = (f'<p style="margin:0 0 2pt;font-size:10.2pt;line-height:1.3"><b>Drums.</b> {p["drums"]}</p>'
           f'<p style="margin:0 0 2pt;font-size:10.2pt;line-height:1.3"><b>Bass.</b> {p["bass"]}</p>'
           f'<p style="margin:0 0 2pt;font-size:10.2pt;line-height:1.3"><b>Sounds.</b> {p["sounds"]}</p>'
           f'<p style="margin:0;font-size:10.2pt;line-height:1.3"><b>Try.</b> {p["tryit"]}</p>')
    head = f'<span class="k" style="font-size:13pt;margin:0">{p["name"]} · {p["feel"]}</span>'
    return (f'<div class="box" style="margin-bottom:6pt;padding:6pt 10pt">{head}<div style="display:flex;gap:12pt;margin-top:3pt;align-items:flex-start">'
            f'<div style="flex:1">{txt}</div><div style="width:3.55in;flex:0 0 3.55in">{D.body_svg((body, w, h))}</div></div></div>')


def drums_page(n, wm=False):
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt;line-height:1.38">Lo-fi drums are simple and soft. Each card gives a one-bar pattern '
             f'(16 steps, 4 to a beat; shaded steps are the beats; the waltz has 12), a bass idea and sounds to try. Pick one for your '
             f'beat at 70 to 90 BPM, copy it into the Step Sequencer, or use a Drummer track, then swing it (page {D.IX("fx1")}). Patterns A to C are for the '
             f'4/4 carols; pattern D is for O Tannenbaum.</p>'
             + "".join(pattern_card(p) for p in (*PATTERNS, WALTZ)))
    return D.page("Lo-fi drum patterns", "STUDENT", "Class 2", inner, n, wm, name=False, key="drums")


def fx_card(head, rows, extra=""):
    body = "".join(f'<p style="margin:0 0 3.5pt;font-size:11.6pt;line-height:1.36"><b>{a}.</b> {b}</p>' for a, b in rows)
    return (f'<div class="box" style="margin-bottom:6pt;padding:6pt 10pt"><span class="k" style="font-size:13pt;margin:0">{head}</span>'
            f'{extra}<div style="margin-top:3pt">{body}</div></div>')


FX_SWING = ("Swing · make the beat bounce", [
    ("What it does", "Moves the off-beat 16th notes a little later, so a steady pattern rolls and bounces instead of marching. More swing, more bounce."),
    ("In Logic", "Select the MIDI region. In the Region inspector, set Quantize to a 1/16-note value, then raise Q-Swing. Try the hats first."),
    ("Try", "Light swing on the hats, a little less on the kick and snare. Q-Swing is Logic’s own scale, so use the diagram as a guide and decide by ear."),
    ("Listen for", "The pattern leans back instead of marching. If it sounds loose or sloppy, you have too much.")])
FX_TAPE = ("Tape · wobble, warmth and echo", [
    ("What it does", "Old tape drifts a little in pitch, softens the highs and adds warm distortion and echo. A touch of all of that makes a digital sound feel played from a tape."),
    ("In Logic", "Put Scanner Vibrato or a light Chorus on the keys for a slow, small wobble. Add Tape Delay with low feedback for a soft echo. "
                 "For warmth use ChromaGlow if your version has it; if not, turn Overdrive down to a tiny amount."),
    ("Try", "Keep the wobble depth low: the pitch should drift, not warble. Set the delay to an eighth note and the mix low."),
    ("Listen for", "A slightly seasick warmth. If the chords sound out of tune, back the depth off.")])
FX_CRUSH = ("Bitcrusher · grit", [
    ("What it does", "Throws away detail: it lowers the bit depth and the sample rate, so a sound gets gritty and fuzzy, like an old sampler."),
    ("In Logic", "Insert Bitcrusher in an Audio FX slot. Lower Resolution and Downsampling, then pull Mix back so some of the clean sound stays."),
    ("Try", "Use it on one sound, such as the melody or the drums. Around 12 bits is subtle; around 8 bits is crunchy. Start with Mix near half."),
    ("Listen for", "Grit you can hear on the tail of a note or on the hats. If the melody turns to mush, raise the bits.")])
FX_VINYL = ("Vinyl noise · the bed under everything", [
    ("What it does", "A soft bed of hiss and crackle, as if the beat were playing from a record. It glues the sounds together and says “lo-fi” at once."),
    ("In Logic", "Search the Loop Browser (press O) for a noise or crackle loop, or make quiet noise with a synthesizer’s noise oscillator and "
                 "filter it with Channel EQ. Put it on its own track and loop it across the whole beat."),
    ("Try", "Turn it up until it is loud, then bring it down until you only notice it when it stops. Raise it a little in the break."),
    ("Listen for", "Warmth under everything, not a wall of noise. The carol must stay clear.")])
FX_LOWPASS = ("Low-pass filter · muffled and far away", [
    ("What it does", "A low-pass filter lets the low sounds through and cuts the highs, so keys and drums sound muffled, like a radio in another room."),
    ("In Logic", "In Channel EQ, switch on the High Cut filter and slide it down. Automate its frequency to close it in the intro and the break and open it when the drums come in."),
    ("Try", "A cutoff of about 3 to 6 kHz muffles keys; higher is a lighter touch."),
    ("Listen for", "The highs soften and the sound sits back. If the keys go dull and lifeless, open the filter a little.")])


def fx1_page(n, wm=False):
    swing = D.body_svg(swing_body(1100, "page swing"))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt;line-height:1.38">Five small moves make a beat sound lo-fi: swing, tape, a Bitcrusher, a low-pass '
             f'filter and vinyl noise. Use at least four. This page has swing and tape; page {D.IX("fx2")} has the other three. Every move should be small enough that the '
             f'carol is still easy to hear.</p>'
             + fx_card(FX_SWING[0], FX_SWING[1], f'<div style="margin-top:3pt">{swing}</div>')
             + fx_card(FX_TAPE[0], FX_TAPE[1]))
    return D.page("Lo-fi effect cards · 1 of 2", "STUDENT", "Class 3", inner, n, wm, name=False, key="fx1")


def fx2_page(n, wm=False):
    checks = "".join(D.chk(c, 11, "font-size:10.2pt;margin-bottom:2pt") for c in [
        "I can name the carol in the first ten seconds.",
        "The melody is louder than the drums and the noise.",
        "I can say what each lo-fi move does, and where I used it."])
    cheat_rows = [("Swing", "Quantize 1/16, then raise Q-Swing until the hats bounce"), ("Tape", "Wobble depth low; Tape Delay feedback low, mix low"),
                  ("Bitcrusher", "About 8 to 12 bits, Mix near half, on one sound"), ("Low-pass filter", "High Cut about 3 to 6 kHz on the keys"),
                  ("Vinyl noise", "Quiet enough that you notice it only when it stops")]
    cheat = "".join(f"<tr><td style='width:22%'><b>{a}</b></td><td>{b}</td></tr>" for a, b in cheat_rows)
    inner = (fx_card(*FX_CRUSH) + fx_card(*FX_VINYL) + fx_card(*FX_LOWPASS)
             + f'<div class="box" style="padding:5pt 10pt;margin-bottom:6pt"><span class="k">Starting settings, all five moves</span>'
               f'<table class="t" style="font-size:10.8pt;margin-top:3pt">{cheat}</table></div>'
)
    return D.page("Lo-fi effect cards · 2 of 2", "STUDENT", "Class 3", inner, n, wm, name=False, key="fx2")


LOFI_MENU = ["Swing", "Tape wobble or echo", "Bitcrusher", "Low-pass filter", "Vinyl noise", "A soft bass on the chord roots",
             "Ghost notes", "Automation (filter or noise volume)"]


def plan_page(n, wm=False):
    half = (len(LOFI_MENU) + 1) // 2
    items = [D.chk(f"<b>{m}</b> — where: <span style='display:inline-block;width:1.2in;border-bottom:1pt solid #000'>&nbsp;</span>", 11,
                   "font-size:10.2pt;margin-bottom:4pt") for m in LOFI_MENU]
    rows = "".join("<tr><td style='height:21pt'></td><td></td><td></td></tr>" for _ in range(5))
    chords = "".join(f"<td style='height:24pt;text-align:center'><b>Bar {i}</b></td>" for i in range(1, 5))
    roll = D.body_svg(roll_body([], 64, 16, 4, 55, 67, 1100, 14, 1, None, "blank roll"))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.36">Step 2: plan. Pick one carol, a tempo from 70 to 90 BPM and a drum pattern, '
             f'then decide which lo-fi moves you will use. You need at least four of the five (requirement 4), and the carol must still be recognizable.</p>'
             f'<div class="box acc-b" style="margin:0 0 5pt"><span class="k">My choices</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>My carol:</b><span></span><b>Key and time signature:</b><span></span></div>'
             f'<div class="fl" style="margin:0"><b>Tempo (BPM):</b><span style="flex:0 0 0.9in"></span><b>Drum pattern (A, B, C or D):</b><span style="flex:0 0 0.9in"></span>'
             f'<b>Why this tempo:</b><span></span></div></div>'
             f'<span class="k">The chords of my loop (from my chart, or my own)</span>'
             f'<table class="map" style="margin-bottom:4pt"><tr>{chords}</tr><tr>' + "".join("<td style='height:24pt'></td>" for _ in range(4)) + '</tr></table>'
             f'<span class="k">My lo-fi moves (check at least four)</span>'
             f'<div class="cols" style="gap:12pt"><div>{"".join(items[:half])}</div><div>{"".join(items[half:])}</div></div>'
             f'<div class="fl" style="margin-top:3pt"><b>What stays the same, so people still know the tune:</b><span></span></div>'
             f'<span class="k">My layers</span>'
             f'<table class="map" style="margin-bottom:4pt"><tr><th style="width:18%">Layer</th><th style="width:38%">Sound or instrument in Logic</th>'
             f'<th>What it plays</th></tr>{rows}</table>'
             f'<span class="k">Sketch: a counter-melody or a changed rhythm for the first four bars (pencil, optional)</span>'
             f'<div style="margin-top:2pt">{roll}</div>')
    return D.page("Beat plan", "STUDENT", "Class 1", inner, n, wm, name=True, key="plan")


def arrange_page(n, wm=False):
    nb = 32
    head = "<tr><th style='width:1.1in'>Layer</th>" + "".join(f"<th>{i + 1}</th>" for i in range(nb)) + "</tr>"
    body = "".join("<tr><td class='l' style='height:25pt'></td>" + "".join(f"<td class='{'b' if i % 4 == 0 else ''}'></td>" for i in range(nb))
                   + "</tr>" for _ in range(8))
    help_rows = [(b, 240 / b) for b in (70, 75, 80, 85, 90)]
    hr = "".join(f"<tr><td><b>{b}</b></td><td>{s:.2f} s</td>" + "".join(f"<td>{length_s(bars, b):.1f} s</td>" for bars in (20, 24, 28)) + "</tr>"
                 for b, s in help_rows)
    inner = (f'{CSS_SG}<style>table.sg th {{ font-size: 5pt; }} table.sg td.l {{ width: 1.1in; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.4pt">Step 6: arrange. Give your beat a form: an intro, beat sections with a break, and an outro. Shade the bars where each '
             f'layer plays, write the layer’s name at the left, and mark where each section starts (every thick line is 4 bars). 60 to 90 seconds only.</p>'
             f'<table class="sg">{head}{body}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:6pt"><div class="box acc-b"><span class="k">My sections</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Intro:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Beat:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Break:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>Outro:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div></div>'
             f'<div><span class="k">Length helper (4/4)</span><table class="t" style="font-size:9.4pt;margin-top:2pt"><tr><th>BPM</th><th>One bar</th>'
             f'<th>20 bars</th><th>24 bars</th><th>28 bars</th></tr>{hr}</table><p class="small" style="margin:1pt 0 0">Aim for 60 to 90 seconds. '
             f'Seconds = bars × 240 ÷ BPM. In 3/4, one bar is 180 ÷ BPM seconds.</p></div></div>'
             f'<div class="fl" style="margin-top:6pt"><b>My tempo:</b><span style="flex:0 0 0.8in"></span><b>Bars:</b><span style="flex:0 0 0.8in"></span>'
             f'<b>Length: bars × 240 ÷ tempo =</b><span style="flex:0 0 0.8in"></span><b>seconds</b></div>'
             f'<div class="box" style="margin-top:4pt"><span class="k">Checks before I bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:2pt") for c in [
                 "I can name the carol in the first ten seconds, and the melody is louder than the drums and the noise.",
                 "Every pitch and length matches the chart, or a change I planned.",
                 "I can hear every layer, and none is buried or too loud.",
                 "At least four lo-fi moves are on, each audible, and EQ is in use.",
                 "The beat is between 60 and 90 seconds."]) + '</div>')
    return D.page("Arrangement plan", "STUDENT", "Classes 3–4", inner, n, wm, name=True, key="arrange")


def example_page(n, wm=False):
    moves = "".join(f"<tr><td style='width:14%'><b>{a}</b></td><td>{D.fill(b)}</td></tr>" for a, b in EX_MOVES)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.2pt">An <b>invented plan on paper</b>: Good King Wenceslas, the four-bar loop, as a lo-fi beat at '
             f'{EX_BPM} BPM. No audio is included. Student projects will differ. Page 1 of 2: the plan and the lo-fi moves.</p>'
             f'<div class="cols" style="gap:10pt"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no moves and nothing that would sound lo-fi.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.8pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · Five lo-fi moves, and what stays")}'
             f'<table class="t" style="font-size:9.4pt;line-height:1.22">{moves}<tr><td><b>Stays</b></td><td>{EX_STAYS}</td></tr></table>'
             f'{D.H2("4 · The loop on the piano roll, with its chords (bars 1–4)")}'
             f'<div style="width:6.6in;margin:2pt auto 0">{D.body_svg(tune_roll("wence", 0, 4, 1100, "page example roll"))}</div>')
    return D.page("Worked example · an invented beat", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    secs = "".join(f"<tr><td style='width:22%'><b>{nm}</b></td><td style='white-space:nowrap'>bars {a}–{b}</td><td>{mmss((a - 1) * EX_BAR_S)}–{mmss(b * EX_BAR_S)}</td></tr>"
                   for nm, a, b in EX_SECTIONS)
    lay = "".join(f"<tr><td style='width:17%'><b>{nm}</b></td><td>{d}</td></tr>" for nm, _s, d in EX_LAYERS)
    chs = "".join(f"<td><b>Bar {i + 1}</b><br>{chord_text(c)}<br><span style='font-size:7.4pt'>bass {' · '.join(dict.fromkeys(BASS_ROOT[x] for x in c))}</span></td>"
                  for i, c in enumerate(WENCE_CH))
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same beat, page 2 of 2: the map of the whole piece, then the numbers.</p>'
             f'{D.H2("5 · The map: 1:24, five sections, eight layers, three lanes")}'
             f'<div style="width:6.5in;margin:1pt auto 3pt">{D.body_svg(map_body(1250, "page map", 24, 20))}</div>'
             f'<div class="cols" style="gap:10pt"><div><span class="k" style="font-size:9.4pt">6 · Sections</span>'
             f'<table class="t" style="font-size:8.6pt;line-height:1.2;margin-top:2pt">{secs}</table></div>'
             f'<div><span class="k" style="font-size:9.4pt">7 · Layers (in to out)</span>'
             f'<table class="t" style="font-size:8pt;line-height:1.16;margin-top:2pt">{lay}</table></div></div>'
             f'<span class="k" style="font-size:9.4pt;display:block;margin-top:3pt">8 · The chords of the 4-bar loop, with the bass root (the melody’s first and longest notes are chord tones)</span>'
             f'<table class="t" style="font-size:8.8pt;line-height:1.15;margin-top:2pt;text-align:center"><tr>{chs}</tr></table>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">9 · Checking the numbers</span><p style="margin:0;font-size:8.6pt;line-height:1.28">'
             f'One bar of 4/4 at {EX_BPM} BPM lasts 240 ÷ {EX_BPM} = {EX_BAR_S:g} seconds, so {EX_BARS} bars = {EX_BARS * EX_BAR_S:g} seconds, inside 60 to 90. '
             f'The sections are {" + ".join(str(b - a + 1) for _, a, b in EX_SECTIONS)} bars = {EX_BARS}. Beat B has the most layers ({max(EX_DENS)}). '
             f'<b>Three feedback questions (invented):</b> {qs}</p></div>')
    return D.page("Worked example · the map", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "tunes": tunes_page, "example": example_page,
         "example2": example2_page, "wence": chart_page("wence"), "rest": chart_page("rest"), "tree": chart_page("tree"),
         "drums": drums_page, "fx1": fx1_page, "fx2": fx2_page, "plan": plan_page, "arrange": arrange_page}


# ================================================================ content checks (melodies, drums, swing, the worked example, no audio)
def seg_ok(notes, a, b, chord):
    """The first note and the longest note that start in [a, b) are tones of the chord."""
    ins = [(p, s, d) for p, s, d in notes if a <= s < b]
    if not ins:      # a note held through the whole segment
        held = [p for p, s, d in notes if s < a and s + d >= b]
        return bool(held) and held[0].rstrip("0123456789") in CHORD_TONES[chord]
    first = ins[0][0]
    longest = max(ins, key=lambda x: x[2])[0]
    tones = CHORD_TONES[chord]
    return first.rstrip("0123456789") in tones and longest.rstrip("0123456789") in tones


def verify_content():
    import re
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 4), reqs=(REQS, 6), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 4))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    # ---- the three melodies
    expect = {"wence": (4, 13, 16, "G3", "D4", "C4", "4/4"), "rest": (4, 14, 16, "G3", "E4", "A3", "4/4"),
              "tree": (4, 15, 12, "G3", "F4", "G3", "3/4")}
    for k, T in TUNES.items():
        nb, nn, bl, lo, hi, last, ts = expect[k]
        if len(T["bars"]) != nb or len(T["chords"]) != nb or len(SRC[k]) != nb:
            errs.append(f"{k}: {nb} bars and a chord pair for each expected")
        if T["bar_len"] != bl or T["time"] != ts:
            errs.append(f"{k}: bar length {T['bar_len']} sixteenths does not match {T['time']}")
        for i, bar in enumerate(T["bars"]):
            if sum(d for _, d in bar) != bl:
                errs.append(f"{k}: bar {i + 1} adds to {sum(d for _, d in bar)} sixteenths, not {bl}")
            for p, d in bar:
                if d not in LEN_NAMES:
                    errs.append(f"{k}: bar {i + 1} has a length ({d}) with no name")
                if p[:-1] not in C_MAJOR:
                    errs.append(f"{k}: {p} is not a white key (charts use C major and A minor)")
        if note_count(k) != nn:
            errs.append(f"{k}: {note_count(k)} notes, expected {nn}")
        ms = [midi(p) for p, _, _ in tune_notes(k)]
        if min(ms) != midi(lo) or max(ms) != midi(hi):
            errs.append(f"{k}: range {pname(min(ms))}-{pname(max(ms))}, expected {lo}-{hi}")
        if not T["lo"] <= min(ms) or not max(ms) <= T["hi"]:
            errs.append(f"{k}: the roll's rows do not cover the notes")
        if T["bars"][-1][-1][0] != last:
            errs.append(f"{k}: last note {T['bars'][-1][-1][0]}, expected {last}")
        # the chart is the source (original key) moved down 7 semitones, note for note and length for length
        for bs, bc in zip(SRC[k], T["bars"]):
            if [(midi(p) - DOWN, d) for p, d in bs] != [(midi(p), d) for p, d in bc]:
                errs.append(f"{k}: the chart is not the source moved down a fifth")
        for i, (c1, c2) in enumerate(T["chords"]):
            for half, ch in enumerate((c1, c2)):
                bl2 = bl // 2
                if not seg_ok(tune_notes(k), i * bl + half * bl2, i * bl + (half + 1) * bl2, ch):
                    errs.append(f"{k}: chord {ch} in bar {i + 1} half {half + 1} does not hold the first and longest notes")
            for ch in (c1, c2):
                if BASS_ROOT[ch].rstrip("0123456789") not in CHORD_TONES[ch] or ch[0] != BASS_ROOT[ch][0]:
                    errs.append(f"bass root for {ch}")
    # the melodies themselves, in the original key (the facts two transcriptions agree on)
    if [p for b in SRC["wence"] for p, _ in b] != ["G4", "G4", "G4", "A4", "G4", "G4", "D4", "E4", "D4", "E4", "F#4", "G4", "G4"] \
            or SRC["wence"][1][2] != ("D4", 8) or SRC["wence"][3] != [("G4", 8), ("G4", 8)]:
        errs.append("good king wenceslas: G G G A | G G D(half) | E D E F# | G(half) G(half)")
    if [p for b in SRC["rest"] for p, _ in b] != ["E4", "B4", "B4", "A4", "G4", "F#4", "E4", "D4", "E4", "F#4", "G4", "A4", "B4", "E4"] \
            or SRC["rest"][3] != [("B4", 12), ("E4", 4)]:
        errs.append("god rest ye: E B B A | G F# E D | E F# G A | B(dotted half) + E lead-in")
    if [p for b in SRC["tree"] for p, _ in b] != ["G4", "G4", "G4", "A4", "B4", "B4", "B4", "B4", "A4", "B4", "C5", "F#4", "A4", "G4", "D4"] \
            or [d for _, d in SRC["tree"][0]] != [3, 1, 4, 4] or [d for _, d in SRC["tree"][1]] != [3, 1, 6, 2]:
        errs.append("o tannenbaum: G. G G A | B. B B. B | A B C F# | A G + D lead-in")
    if TUNES["tree"]["time"] != "3/4" or TUNES["tree"]["bar_len"] != 12 or WALTZ["pat"]["Kick"].__len__() != 12:
        errs.append("o tannenbaum is 3/4: 12 sixteenths a bar and a 12-step waltz pattern")
    # ---- drum patterns: 16 steps (12 for the waltz) and the facts the cards claim
    hit = lambda p, ln: [i for i, c in enumerate(p["pat"][ln]) if c == "x"]
    for p in PATTERNS:
        if any(len(p["pat"][ln]) != 16 or set(p["pat"][ln]) - {"x", "."} for ln in LANES):
            errs.append(f"pattern {p['key']}: each drum lane is 16 steps of x and .")
    a, b, c = pattern("a"), pattern("b"), pattern("c")
    if hit(a, "Kick") != [0, 10] or hit(a, "Snare") != [4, 12] or hit(a, "Hi-hat") != list(range(0, 16, 2)) or hit(a, "Ghost snare"):
        errs.append("pattern A: kick on beat 1 and an eighth after beat 3, snare on 2 and 4, hats on eighths, no ghost notes")
    if hit(b, "Kick") != [0, 6, 10] or hit(b, "Snare") != [4, 12] or hit(b, "Hi-hat") != list(range(0, 16, 2)):
        errs.append("pattern B: kick on beat 1, the 'and' of 2 and the 'and' of 3; snare on 2 and 4")
    if hit(c, "Kick") != [0, 8, 10] or hit(c, "Snare") != [4, 12] or hit(c, "Ghost snare") != [7, 14] or hit(c, "Hi-hat") != list(range(0, 16, 2)):
        errs.append("pattern C: kick on 1, 3 and the 'and' of 3; snare on 2 and 4; ghost snare on step 7 and 14 (0-based)")
    if 7 != 4 + 3 or 14 != 12 + 2:
        errs.append("ghost snare steps: the last 16th of beat 2 and the 'and' of beat 4")
    if any(len(WALTZ["pat"][ln]) != 12 for ln in LANES3) or hit(WALTZ, "Kick") != [0, 6] or hit(WALTZ, "Rim / snare") != [4, 8] \
            or hit(WALTZ, "Hi-hat") != list(range(0, 12, 2)):
        errs.append("waltz: 12 steps; kick on 1 and the 'and' of 2; rim on 2 and 3; hats on eighths")
    # ---- swing numbers
    if [round(r, 2) for _, r in SWING] != [0.5, 0.58, 0.67]:
        errs.append("swing levels: 50%, 58%, 67%")
    offs = [swing_offset(r) for _, r in SWING]
    if abs(offs[0]) > 1e-9 or not 0 < offs[1] < offs[2] < 0.5 or abs(offs[2] - 1 / 3) > 1e-9:
        errs.append("swing offsets must grow from 0 to one third of a 16th")
    if abs(60000 / EX_BPM / 4 - 187.5) > 1e-9 or abs(swing_ms(SWING[1][1], EX_BPM) - 30) > 1e-6 or abs(swing_ms(SWING[2][1], EX_BPM) - 62.5) > 1e-6:
        errs.append("at 80 BPM a 16th is 187.5 ms; light swing 30 ms, triplet swing 62.5 ms")
    # ---- the worked example adds up
    if EX_BAR_S != 3 or EX_BARS * EX_BAR_S != 84 or not 60 <= EX_BARS * EX_BAR_S <= 90:
        errs.append("28 bars x 3 s = 84 s, inside 60 to 90")
    if not 70 <= EX_BPM <= 90:
        errs.append("the example tempo must sit in 70 to 90 BPM")
    if EX_SECTIONS[0][1] != 1 or EX_SECTIONS[-1][2] != EX_BARS or any(b + 1 != c for (_, _, b), (_, c, _) in zip(EX_SECTIONS, EX_SECTIONS[1:])):
        errs.append("sections must tile bars 1-28")
    if [b - a + 1 for _, a, b in EX_SECTIONS] != [4, 8, 4, 8, 4] or sum(b - a + 1 for _, a, b in EX_SECTIONS) != EX_BARS:
        errs.append("sections 4 + 8 + 4 + 8 + 4 = 28")
    if len(EX_LAYERS) != 8 or len(EX_AUTO) != 3 or len(EX_MOVES) != 5:
        errs.append("eight layers, three automation lanes, five lo-fi moves")
    for nm, spans, _d in EX_LAYERS:
        for a_, b_ in spans:
            if not 1 <= a_ <= b_ <= EX_BARS:
                errs.append(f"layer {nm}: span {a_}-{b_} outside the piece")
    spans = {nm: (min(a_ for a_, _ in sp), max(b_ for _, b_ in sp)) for nm, sp, _ in EX_LAYERS}
    for ly, par, pts in EX_AUTO:
        a_, b_ = spans[ly]
        ts_ = [t_ for t_, _ in pts]
        vs = [v for _, v in pts]
        if ts_ != sorted(ts_) or len(pts) < 3 or ts_[0] < a_ or ts_[-1] > b_:
            errs.append(f"lane {ly}/{par}: points in order, 3+, inside its layer")
        if max(vs) - min(vs) < .5:
            errs.append(f"lane {ly}/{par}: a lane that barely moves")
    top = max(EX_DENS)
    mb = next((a_, b_) for nm, a_, b_ in EX_SECTIONS if nm == "Beat B")
    if [i + 1 for i, d in enumerate(EX_DENS) if d == top] != list(range(mb[0], mb[1] + 1)):
        errs.append("the most layers must play in exactly Beat B")
    if EX_DENS[0] >= top or EX_DENS[-1] >= top or min(EX_DENS[12:16]) >= EX_DENS[8]:
        errs.append("the piece starts smaller than its peak, drops in the Break and resolves down")
    if [round(length_s(bars, bpm), 1) for bpm in (70, 75, 80, 85, 90) for bars in (20, 24, 28)] != \
            [68.6, 82.3, 96.0, 64.0, 76.8, 89.6, 60.0, 72.0, 84.0, 56.5, 67.8, 79.1, 53.3, 64.0, 74.7]:
        errs.append("length helper numbers")
    if len(EX_QUESTIONS) != 3:
        errs.append("three feedback questions")
    if "♭" in EX_STRONG:
        errs.append("plain text only (no flat sign) in the clear plan")
    # slide notes that name a page number name the right one
    for i, s in enumerate(SLIDES, start=1):
        for m in re.finditer(r"\bpage (\d+)\b", s[4]):
            if int(m.group(1)) != D.IX("drums"):
                errs.append(f"slide {i} notes name page {m.group(1)}, which is not the drum patterns page")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    txt = " ".join(flat)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, lyrics, artists or albums", "invented plan on paper", "public domain", "Piae Cantiones", "1582",
                 "Zarnack", "1820", "1930 or earlier", "No student work is included", "Q-Swing",
                 "Created with the help of digital and AI tools. Notation and answer keys are verified before release."):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if "What changed" in txt or "Kept as I wrote it" in txt or "my project menu" in txt or "my Digital Music Production" in txt:
        errs.append("ORIGINAL kit: no wording about changes to an owner's sheet")
    if "checked by hand" in txt or "handmade" in txt.lower() or "classroom-tested" in txt.lower() or "hand-checked" in txt.lower():
        errs.append("never claim hand checks or classroom testing for a new product")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt:
        errs.append("PDF: 'Grades 9–12'")
    # every chart page prints every note of its tune, bar by bar (raw text keeps each table cell's words in order)
    import re
    import subprocess
    for k in ("wence", "rest", "tree"):
        raw = re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-raw", "-f", str(D.IX(k)), "-l", str(D.IX(k)), D.files()["pdf"], "-"],
                                                 capture_output=True, text=True, check=True).stdout)
        for i, bar in enumerate(TUNES[k]["bars"]):
            if bar_text(bar) not in raw:
                errs.append(f"{k} chart page: bar {i + 1} '{bar_text(bar)}' is not printed")
    pat_pages = " ".join(flat[D.IX("drums") - 1:D.IX("drums")])
    for p in (*PATTERNS, WALTZ):
        if p["name"].lower() not in pat_pages.lower():
            errs.append(f"drum pattern card {p['name']} missing")
    fx = " ".join(flat[D.IX("fx1") - 1:D.IX("fx2")])
    for need in ("Swing", "Tape", "Bitcrusher", "Vinyl noise", "Low-pass filter", "light swing is 30 ms late", "triplet swing 62.5 ms late"):
        if need.lower() not in fx.lower():
            errs.append(f"effect cards must say '{need}'")
    ex = " ".join(flat[D.IX("example") - 1:D.IX("example2")])
    for need in ("240 ÷ 80 = 3", "28 bars = 84 seconds", "4 + 8 + 4 + 8 + 4 bars = 28"):
        if need not in ex:
            errs.append(f"worked example must say '{need}'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up or "public domain" not in up:
        errs.append("UPLOAD.md: must say no audio is included, say public domain and record the open questions")
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Radiohead", "Billboard", "Roland", "TR-808", "Bensound", "Ableton"]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
    return errs


def check_summary():
    return (f"Good King Wenceslas (4 bars, {note_count('wence')} notes), God Rest Ye Merry, Gentlemen (4 bars, {note_count('rest')} notes) and O Tannenbaum "
            f"(4 bars of 3/4, {note_count('tree')} notes) are the source notes moved down a fifth, add up bar by bar, use only white keys, and every "
            f"chord holds each half-bar's first and longest note; {len(PATTERNS) + 1} drum patterns match what their cards say; swing is 0/30/62.5 ms "
            f"at {EX_BPM} BPM; the worked example is {EX_BARS} bars at {EX_BPM} BPM = {EX_BARS * EX_BAR_S:g} s (sections "
            f"{'+'.join(str(b - a + 1) for _, a, b in EX_SECTIONS)}, {len(EX_LAYERS)} layers, peak {max(EX_DENS)} layers only in Beat B, "
            f"{len(EX_AUTO)} moving lanes); length helper correct; no audio, lyrics, artist names or student work; grades 9-12; "
            f"no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students turn a public-domain carol into a lo-fi hip-hop beat in Logic Pro. They enter the melody and chords from a "
            f"piano-roll note chart, build a slow, swung drum pattern, and add tape wobble, a Bitcrusher, a low-pass filter and vinyl noise. This "
            f"Lo-Fi Holiday Beat project takes {CLASSES} class periods and is an original Hudson Beat project; the steps are written for Logic Pro, "
            f"while the ideas (a slow tempo, swing, softened sounds and noise make lo-fi) carry over to GarageBand, Ableton Live and BandLab.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + 10 teacher + {np_ - 12} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, two pages of teacher notes "
            f"(struggles, variations, resources, grading), a Logic quick reference, tune sources and the public-domain rule, and a two-page worked "
            f"example (an invented plan on paper: Good King Wenceslas as an 84-second beat at 80 BPM, with its five lo-fi moves, a 28-bar map, "
            f"eight layers, chords and three automation lanes) (10 pages)\n"
            f"• Student pages: three piano-roll note charts (Good King Wenceslas, God Rest Ye Merry, Gentlemen and O Tannenbaum in 3/4) with every note "
            f"listed bar by bar and a blank bass-line roll, four lo-fi drum patterns with grids, two pages of effect cards (swing with a diagram, tape, "
            f"Bitcrusher, vinyl noise, low-pass filter), a Beat plan, an Arrangement plan with a length helper, the 3-page project sheet "
            f"(overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a feedback "
            f"planner and a reflection page ({np_ - 12} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, how to read a "
            f"piano roll, building the beat, straight against swung, three lo-fi drum patterns, a worked-example map, the four sound moves, what to turn in and the rubric\n\n"
            f"THE FOUR CLASS PERIODS\n"
            f"• Class 1: hook; choose a carol; fill in the Beat plan; enter the melody and chords\n"
            f"• Class 2: build the beat: drum pattern, swing and a bass line\n"
            f"• Class 3: make it lo-fi with tape, Bitcrusher, a low-pass filter and vinyl noise; plan the form; arrange and mix\n"
            f"• Class 4: bounce and hand in; presentations with feedback questions; reflection\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Entering and editing notes and chords in Logic Pro's Piano Roll from a note chart\n"
            f"• Programming a lo-fi drum pattern and adding swing\n"
            f"• What makes a sound lo-fi: tape wobble, bit crushing, a low-pass filter and vinyl noise, each used small\n"
            f"• Planning a 60 to 90 second arrangement with an intro, beat sections, a break and an outro\n"
            f"• Balancing a mix and explaining their choices in a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. The three melodies are in the public domain and appear only as note charts, "
            f"with no lyrics; students make every sound themselves in Logic Pro\n"
            f"• Good King Wenceslas is a winter carol, God Rest Ye Merry, Gentlemen is a Christmas carol and O Tannenbaum is a winter tune. Offer the ones that suit your school\n"
            f"• Requires Logic Pro on a Mac. A MIDI keyboard is not needed; nobody has to read staff notation\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"{D.DISCLOSURE_NEW}")
    md = f"""# UPLOAD: Lo-Fi Holiday Beat, original Logic Pro holiday project (TpT 036)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `{SLUG}.zip`. It holds three files in a folder "{ZIP_DIR}":
  - `{SLUG}.pdf`: the teacher and student resource, {np_} pages, US Letter portrait.
  - `{SLUG}-intro-deck.pptx`: the teacher-presented intro deck, {ns} slides (16:9), speaker notes and a Class badge on every slide.
  - `{SLUG}-intro-deck.pdf`: a PDF copy of the deck, {ns} pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

## 1. Title

```
{LISTING_TITLE}
```
({nt} characters; the limit is 80.)

## 2. Description

```
{desc}
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: Music; Computer Science - Technology; Music Composition (all three are in `tpt/SUBJECT-OPTIONS.json`)
- Tags in tpt.json: Winter, Christmas-Chanukah-Kwanzaa, Holiday, Project-based Learning, Projects (five exact entries of `tpt/TAG-OPTIONS.json`; the limit is 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**${PRICE}** (paid), multiple-license price ${PRICE}. The $8 set in the queue, inside the $7-9 holiday-kit range, for a kit with {np_} pages + {ns} slides, three note charts, four drum patterns, five effect cards and a two-page worked example, listed in November and December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the Good King Wenceslas note chart, the first effect-card page (swing and tape) and the /25 rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Tunes are public domain (year and source for QA.md).** Good King Wenceslas, the first phrase: the melody "Tempus adest floridum", first published in the Finnish collection Piae Cantiones in 1582; J. M. Neale's 1853 English words are not used. God Rest Ye Merry, Gentlemen, the first line: English traditional melody, in print in the early 1800s (an 1815 piano rondo by Samuel Wesley, a parody of the 1820s); no words are used. O Tannenbaum, the first line: a traditional German tune, printed in August Zarnack's school songbook in 1820; Ernst Anschütz's 1824 words are not used. All three are shown as note charts transcribed for this kit (pitches checked against two public-domain transcriptions each, then moved down a fifth to C major / A minor); no published edition is reproduced.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. For this kit `dmp2.py` now checks tags against `tpt/TAG-OPTIONS.json` instead of the old proven-tag list.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Q-Swing in the Region inspector, Scanner Vibrato, Tape Delay, Bitcrusher (Resolution, Downsampling, Mix), Channel EQ High Cut, Drummer hip-hop styles, the Step Sequencer, ChromaGlow (stated as "if your version has it"), the Loop Browser (O). Nothing says a loop of a given name exists.
- [ ] **Open question for the owner:** (1) **Carols and schools.** Two of the three tunes are Christmas or winter carols and O Tannenbaum is a winter tune; the kit tells teachers to offer what suits their school. Say if you want a fourth, fully secular chart (any public-domain winter tune first published by 1930). (2) **Price.** $8, as in the queue; the other holiday kit (031) is $9.
"""
    with open(os.path.join(HERE, "UPLOAD.md"), "w", encoding="utf8") as f:
        f.write(md)


if __name__ == "__main__":
    if "--check" not in sys.argv:
        write_upload()
    D.main(sys.modules[__name__])
