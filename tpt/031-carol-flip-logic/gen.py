#!/usr/bin/env python3
"""Logic Pro project kit: Carol Flip (TpT 031): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content, melodies, drums, the worked example, drawings, files, page/slide counts, class slots,
                              notes, fonts, fit and overlap, overflow and dead space, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (first kit with dmp2.ORIGINAL = True): it is not built from the owner's course sheets, so there is
no "what changed" page. Students remix a public-domain carol in any genre. The three melodies are given as piano-roll note charts,
drawn here in code from the note lists below (pitch, start and length in sixteenth notes) and checked against them:

  Jingle Bells, the chorus, 8 bars of 4/4 in C major. James Lord Pierpont, first published in Boston in 1857 as "One Horse Open
      Sleigh". Public domain.
  Deck the Halls, the first phrase, 4 bars of 4/4 in C major. Traditional Welsh winter melody ("Nos Galan"), centuries old and in
      print long before 1930. Public domain. (The English words of 1862 are not used.)
  Silent Night, 12 bars of 6/8 in C major. Franz Xaver Gruber, 1818. Public domain. (The words are not used.)

Pitches were checked against public-domain transcriptions of the same tunes, then moved to C major (all three are written without
sharps or flats). NO LYRICS, NO AUDIO, no recordings and no editions are included; students make every sound in Logic Pro.
Every picture (hero, cards, piano rolls, drum grids, arrangement map) is drawn in code. The shared builder is
../_dmp2_common/dmp2.py (see its README; this kit sets ORIGINAL = True).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

ORIGINAL = True
SLUG = "carol-flip"
TITLE = "Carol Flip"
ACCENT = "#2A7DBA"          # this product's single accent: icy winter blue
ACC_LIGHT = "#D6E8F5"
PRICE = "9.00"
CLASSES = 4
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter"]
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # METADATA-GUIDE (a); all in SUBJECT-OPTIONS.json
ANSWER_KEY = None
LISTING_TITLE = "Holiday Remix in Logic Pro | Carol Flip Project | High School Music Tech"
DESC_START = "Holiday remix project for high school music technology:"
DESC_MUST = ["Carol Flip", "piano-roll", "no audio", "Jingle Bells", "Deck the Halls", "Silent Night", "public domain"]
ZIP_DIR = "Carol Flip - Hudson Beat"
ZIP_DATE = (2026, 11, 12, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Remix Project</i> | 4 class periods"
DECK_STRAP = "Same tune, new genre"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Pentato" + "nix", "Trans-" + "Siberian", "Nut" + "cracker", "Home " + "Alone", "Spoti" + "fy", "You" + "Tube"]

# ================================================================ the project text (original; students read these pages)
OVERVIEW = ("Take a carol everyone knows and flip it. Choose one of three public-domain melodies, enter it into Logic Pro from a "
            "piano-roll note chart, and remix it in any genre you like: change the tempo, the drums, the bass, the chords, the sounds "
            "and, if you want, the mode or the rhythm of the tune. Your finished remix is 60 to 90 seconds long, and people should "
            "still be able to name the carol.")
GOALS = ["Enter a melody into Logic Pro’s Piano Roll from a note chart, with the right pitches and lengths",
         "Change a tune’s genre by changing tempo, drums, bass, chords and sounds, not only the speed",
         "Keep a melody recognizable while everything around it is new",
         "Plan, build and explain a 60 to 90 second arrangement"]
VOCAB = [("Remix", "A new version of an existing tune that changes its style, sounds or structure but keeps something people recognize"),
         ("Piano roll", "An editor that shows each note as a bar: height is pitch, length is how long it lasts, and left to right is time"),
         ("Genre", "A style of music, such as lo-fi, house, trap or reggae, set by its tempo, rhythm, sounds and harmony"),
         ("Public domain", "Music whose copyright has ended, so anyone may use the melody; the three carols in this project are")]
REQS = ["Choose one of the three carols (or a melody your teacher approves) and enter it into a Software Instrument track in Logic Pro; "
        "every pitch and length matches the chart",
        "Choose one genre and set a tempo that fits it (genre cards: pages @GENRES1–@GENRES2)",
        "Flip at least three things from this list: tempo, drums, bass, chords, sounds, rhythm of the melody, octave, mode or key",
        "Build a 60 to 90 second arrangement with at least four layers (melody, drums, bass and one more) and an intro, "
        "melody sections and an outro",
        "Use at least one effect that suits your genre, and balance the mix with volume, pan and EQ",
        "Reflect on how the flip went, in writing or out loud (page @REFLECT)"]
FILE_NAME = "“Your Name – Carol Flip – Carol, Genre”"
STEPS = ["<b>Choose</b> — Pick one carol and one genre (carol charts: pages @JINGLE, @DECK and @SILENT; genre cards: pages @GENRES1–@GENRES2)",
         "<b>Plan</b> — Fill in your Flip plan: tempo, key or mode, what stays the same and what you flip (page @FLIP)",
         "<b>Enter the melody</b> — Draw or play the chart into the Piano Roll and listen for wrong notes (Logic quick reference: page @LOGICREF)",
         "<b>Flip it</b> — Build drums, bass and chords in your genre, and change the sounds, the rhythm or the octave of the melody",
         "<b>Arrange</b> — Plan the form on the Arrangement plan (page @ARRANGE), then build 60 to 90 seconds with an intro, melody sections and an outro",
         "<b>Mix and finish</b> — Balance with volume, pan and EQ, add an effect that suits your genre, and bounce with the file name format",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your remix. Play it, say the three "
         "things you flipped, and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Keep the melody the star. If a listener cannot name the carol in the first ten seconds, simplify what is around it.",
        "Change the feel before you change the notes: tempo, drums and bass flip a tune faster than new notes do.",
        "One minute goes fast. Add one layer at a time and let each one be heard before you add the next.",
        "Save a new version of your project before each big experiment, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav handed in where your teacher says",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Flip plan, Arrangement plan and Reflection page handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can name the three or more things I flipped"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; your final grade is the average of your self-score and your teacher’s score."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Melody Accuracy", ["The melody is missing or mostly wrong", "Several wrong pitches or lengths", "Mostly right, with a few slips",
                         "Every pitch and length matches the chart, or a change that was planned",
                         "Exact, and any planned change (octave, mode) is done correctly and on purpose"]),
    ("The Flip", ["Sounds like the original with a new speed", "One or two things changed, little sign of a genre",
                  "Three clear changes; the carol is still recognizable", "Several changes that work together in one genre",
                  "A confident, original take: every choice says the genre and the carol is unmistakable"]),
    ("Genre Craft", ["Tempo, drums and sounds do not fit any genre", "Some choices fit; others pull another way",
                     "Tempo and drums fit the genre", "Tempo, drums, bass and sounds all fit the genre",
                     "Sounds like the genre: groove, bass, chords and effects all line up"]),
    ("Arrangement & Mix", ["No clear form; layers cover each other", "A loop with little change; muddy mix",
                           "Intro, melody sections and outro; mostly balanced", "Clear form with layers that enter and leave; clean mix",
                           "A form that builds and resolves; every layer audible, melody on top"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices",
                           "Plan and reflection complete, with basic detail", "Clear plan; thoughtful reflection and good answers to questions",
                           "Insightful reflection and a polished, confident presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = [ds[4] for _, ds in RUBRIC]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine · / 25"

TN_REINFORCES = ("Teaches how a genre is built. Students learn that tempo, drums, bass, chords and sounds, not only the notes of a melody, "
                 "make a style, and they practice entering and editing notes in Logic Pro’s Piano Roll.")
STRUGGLES = ["The notes go in but the tune sounds wrong: check the grid setting and the note lengths against the chart, bar by bar "
             "(Logic quick reference, page @LOGICREF).",
             "The flip is only a speed change: ask which three things changed besides the tempo (the Flip plan, page @FLIP).",
             "The melody gets buried under drums and bass: turn the backing down or EQ the melody up, so the carol stays the star.",
             "A genre name with no genre craft: use the genre cards (pages @GENRES1–@GENRES2) to check the tempo, drums and sounds."]
VAR_EASY = ("Use Jingle Bells, loop one 4-bar section, and start from a drum pattern on a genre card or a Drummer track.")
VAR_HARD = ("Flip the mode (major to minor) and the rhythm of the melody, then add a countermelody or a key change in the last section. "
            "Silent Night is the hardest chart: it is in 6/8.")
RESOURCES = [("The three note charts (pages @JINGLE, @DECK and @SILENT)",
              "Hand out one chart each, or let students choose. Pitch names are printed, so nobody needs to read staff notation."),
             ("Genre cards (pages @GENRES1–@GENRES2)",
              "Students pick a genre and copy its drum pattern into the Step Sequencer. A blank card is there for a genre of their own."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "Jingle Bells in C minor as house music, planned on paper. Use it as a model, not a template; student projects will differ.")]
TN_NOTE = ("Pairs well with a listening day: play the finished flips without saying the title and let the class name the carol. A tune "
           "that people name quickly is a flip that worked.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Melody Accuracy (rubric row 1): open the project and compare the Piano Roll with the chart, bar by bar. A planned change such "
           "as an octave or a minor mode is correct, not an error.",
           "The Flip and Genre Craft (rubric rows 2 and 3): ask which three things changed, then check tempo, drums and sounds "
           "against the genre card.",
           "Arrangement and Mix (rubric row 4): compare the project with the Arrangement plan (page @ARRANGE). Is there an intro, melody "
           "sections and an outro, and can you hear the melody?",
           "Plan and Reflection (rubric row 5): the Flip plan (page @FLIP), the questions on the feedback planner and the Reflection "
           "page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Choose a carol and a genre, fill in the Flip plan and start entering the melody.",
     "do": "Slides 1–6: the hook, what the project is, the four classes, the five moves and how to read a piano roll. Hand out the project "
           "sheet, the three charts, the genre cards and the Flip plan. Check that each student has a carol and a genre before they leave.",
     "slides": (1, 6), "pages": ["jingle", "deck", "silent", "genres1", "genres2", "flip", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Same tune, new genre · five moves · reading a piano roll"},
    {"n": 2, "owner": "Enter the melody, check it against the chart, then build the drums and bass of the genre.",
     "do": "Slides 7–9: entering the melody, one flip (major to minor) and why genre lives in the drums. Demonstrate the Piano Roll on "
           "the projector, then work time. Walk the room with one question: which of your three flips is this?",
     "slides": (7, 9), "pages": [], "deck": "Enter the melody · one flip · genre is in the drums"},
    {"n": 3, "owner": "Add chords and sounds, plan the form, build the arrangement and mix.",
     "do": "Slides 10–11: the worked example on paper and mixing while keeping the tune. Hand out the Arrangement plan. Then work time; "
           "ask each student to play their first 20 seconds and say which carol they hear.",
     "slides": (10, 11), "pages": ["arrange"], "deck": "Worked example, 75 seconds · mix and keep the tune"},
    {"n": 4, "owner": "Bounce, hand in, present and reflect.",
     "do": "Slides 12–15: what to turn in, the rubric, presentation day and the close. Students bounce, name their files and write "
           "their three feedback questions, then present.",
     "slides": (12, 15), "pages": ["rubric", "present", "reflect"], "deck": "Checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:9.6pt">Make sure every student leaves with a carol, a genre and a tempo written on the Flip plan. If a '
    'genre is only a name, ask: what does the drummer play, and how fast?</p></div>'
    '<div class="box"><span class="k">If you only have three classes</span><p style="margin:0;font-size:9.6pt">Merge Classes 3 and 4: '
    'build and mix on Class 3, then bounce at the start of Class 4 and use the rest of it for presentations and reflection.</p></div></div>')
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


JINGLE = [[("E4", 4), ("E4", 4), ("E4", 8)], [("E4", 4), ("E4", 4), ("E4", 8)],
          [("E4", 4), ("G4", 4), ("C4", 6), ("D4", 2)], [("E4", 16)],
          [("F4", 4), ("F4", 4), ("F4", 6), ("F4", 2)], [("F4", 4), ("E4", 4), ("E4", 6), ("E4", 2)],
          [("E4", 4), ("D4", 4), ("D4", 4), ("E4", 4)], [("D4", 8), ("G4", 8)]]
JINGLE_CH = [("C", "C"), ("C", "C"), ("C", "C"), ("C", "C"), ("F", "F"), ("F", "C"), ("C", "G"), ("G", "G")]
DECK = [[("G4", 6), ("F4", 2), ("E4", 4), ("D4", 4)], [("C4", 4), ("D4", 4), ("E4", 4), ("C4", 4)],
        [("D4", 2), ("E4", 2), ("F4", 2), ("D4", 2), ("E4", 6), ("D4", 2)], [("C4", 4), ("B3", 4), ("C4", 4), ("E4", 2), ("F4", 2)]]
DECK_CH = [("C", "C"), ("C", "C"), ("G", "C"), ("C", "C")]
SILENT = [[("G4", 3), ("A4", 1), ("G4", 2), ("E4", 6)], [("G4", 3), ("A4", 1), ("G4", 2), ("E4", 6)],
          [("D5", 4), ("D5", 2), ("B4", 6)], [("C5", 4), ("C5", 2), ("G4", 6)],
          [("A4", 4), ("A4", 2), ("C5", 3), ("B4", 1), ("A4", 2)], [("G4", 3), ("A4", 1), ("G4", 2), ("E4", 6)],
          [("A4", 4), ("A4", 2), ("C5", 3), ("B4", 1), ("A4", 2)], [("G4", 3), ("A4", 1), ("G4", 2), ("E4", 6)],
          [("D5", 4), ("D5", 2), ("F5", 3), ("D5", 1), ("B4", 2)], [("C5", 6), ("E5", 6)],
          [("C5", 3), ("G4", 1), ("E4", 2), ("G4", 3), ("F4", 1), ("D4", 2)], [("C4", 12)]]
SILENT_CH = [("C", "C"), ("C", "C"), ("G7", "G7"), ("C", "C"), ("F", "F"), ("C", "C"), ("F", "F"), ("C", "C"), ("G7", "G7"), ("C", "C"),
             ("C", "G7"), ("C", "C")]
CHORD_TONES = {"C": {"C", "E", "G"}, "F": {"F", "A", "C"}, "G": {"G", "B", "D"}, "G7": {"G", "B", "D", "F"},
               "Cm": {"C", "Eb", "G"}, "Cm9": {"C", "Eb", "G", "Bb", "D"}, "Fm": {"F", "Ab", "C"}, "Fm7": {"F", "Ab", "C", "Eb"},
               "Gm": {"G", "Bb", "D"}, "Am": {"A", "C", "E"}, "Cmaj7": {"C", "E", "G", "B"}, "Am7": {"A", "C", "E", "G"},
               "Dm7": {"D", "F", "A", "C"}, "G7b": {"G", "B", "D", "F"}, "Ab": {"Ab", "C", "Eb"}, "Eb": {"Eb", "G", "Bb"},
               "Bb": {"Bb", "D", "F"}}
C_MAJOR = {"C", "D", "E", "F", "G", "A", "B"}
C_MINOR = {"C", "D", "Eb", "F", "G", "Ab", "Bb"}

TUNES = {
    "jingle": dict(title="Jingle Bells", part="the chorus", who="James Lord Pierpont", year=1857,
                   src="First published in Boston in 1857 as “One Horse Open Sleigh”.", key="C major", time="4/4", bar_len=16, beat=4,
                   bars=JINGLE, chords=JINGLE_CH, lo=59, hi=68, row_h=24, systems=[(0, 4), (4, 8)],
                   good="The easiest chart: one repeated note, a few skips and a clear shape. A good first choice.",
                   tip="Bars 1 and 2 are the same three notes; bar 8 holds D then G, which pulls back to the start. Loop all eight bars."),
    "deck": dict(title="Deck the Halls", part="the first phrase", who="traditional Welsh melody (“Nos Galan”)", year=None,
                 src="A centuries-old Welsh winter melody, in print long before 1930. The English words (1862) are not used.",
                 key="C major", time="4/4", bar_len=16, beat=4, bars=DECK, chords=DECK_CH, lo=59, hi=68, row_h=34, systems=[(0, 4)],
                 good="A short phrase that loops well: four bars, stepwise, with a quick run of eighth notes in bar 3.",
                 tip="Bar 4 ends on two quick notes (E, F) that lead back into bar 1, so the phrase repeats without a gap."),
    "silent": dict(title="Silent Night", part="the whole melody", who="Franz Xaver Gruber", year=1818,
                   src="Composed in 1818; the melody only. The words are not used.", key="C major", time="6/8", bar_len=12, beat=6,
                   bars=SILENT, chords=SILENT_CH, lo=60, hi=77, row_h=16, systems=[(0, 6), (6, 12)],
                   good="The hardest chart: 6/8 time and a dotted-eighth, sixteenth rhythm. It suits slow, gentle genres.",
                   tip="Set the time signature to 6/8 first. Each bar has two groups of three eighth notes, so count 1-2-3, 4-5-6."),
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


# ---- the worked example: Jingle Bells flipped to C minor, as house music at 128 BPM
FLIP = [[("Eb4" if p == "E4" else p, d) for p, d in bar] for bar in JINGLE]
FLIP_CH = ["Cm", "Cm", "Cm", "Cm", "Fm", "Fm7", "Cm9", "Gm"]
FLIP_BASS = {"Cm": "C2", "Cm9": "C2", "Fm": "F2", "Fm7": "F2", "Gm": "G2"}
EX_BPM = 128
EX_BAR_S = 240 / EX_BPM         # 1.875 s
EX_BARS = 40
EX_SECTIONS = [("Intro", 1, 8), ("Melody A", 9, 16), ("Break", 17, 24), ("Melody B", 25, 32), ("Outro", 33, 40)]
# layer, [(first bar, last bar), ...], how it is made
EX_LAYERS = [("Kick", [(1, 16), (25, 40)], "a four-on-the-floor kick from the Step Sequencer; it drops out for the Break"),
             ("Hi-hat", [(1, 40)], "hats on the offbeats the whole way, quieter in the Break"),
             ("Clap", [(9, 16), (25, 32)], "claps on beats 2 and 4 in the two melody sections"),
             ("Bass", [(9, 16), (25, 36)], "a synth bass on the chord roots (C2, F2, G2), short notes between the kicks"),
             ("Chords", [(9, 32)], "a pad that plays Cm, Cm, Cm, Cm, Fm, Fm7, Cm9, Gm, one chord a bar, three times round"),
             ("Lead", [(9, 16), (25, 32)], "the flipped melody on a bright synth, as drawn on the piano roll"),
             ("Lead 8va", [(25, 32)], "the same melody an octave higher, added only in Melody B"),
             ("Riser", [(23, 24)], "a filter sweep on a synth that rises for two bars into Melody B")]
EX_AUTO = [("Chords", "filter cutoff", [(9, .3), (17, .2), (24, .9), (25, .5), (32, .4)]),
           ("Lead", "reverb send", [(9, .2), (16, .45), (25, .3), (32, .9)]),
           ("Hi-hat", "volume", [(1, .3), (9, .7), (17, .3), (25, .9), (40, .4)])]
EX_WEAK = "I will make Jingle Bells into a cool dance song."
EX_STRONG = ("My carol is Jingle Bells, the 8-bar chorus. My genre is house at 128 BPM. I flip five things: the mode (every E becomes Eb, "
             "so it is in C minor), the tempo (128 BPM), the drums (a four-on-the-floor kick), the bass (short synth notes between the "
             "kicks) and the sounds (a bright synth lead and a pad). The melody keeps its rhythm, so people will still know it. It is "
             "40 bars, 75 seconds: intro, melody, break, melody an octave higher, outro.")
EX_FLIPS = [("Mode", "C major to C minor: every E becomes Eb (the only pitch that changes)"),
            ("Tempo", "from a bouncy walking pace to 128 BPM"),
            ("Drums", "a four-on-the-floor kick, claps on 2 and 4, offbeat hats"),
            ("Bass", "short synth notes on the chord roots, between the kicks"),
            ("Sounds", "a bright synth lead and a pad instead of bells")]
EX_STAYS = "The order of the notes and every length: the melody keeps its rhythm, so the carol is still the carol."
EX_QUESTIONS = ["Which carol did you hear, and how fast did you know?",
                "Where did the music build, and where did it drop?",
                "What would you change so the genre is clearer?"]


def ex_density(bar):
    return sum(1 for _n, spans, _d in EX_LAYERS if any(a <= bar <= b for a, b in spans))


EX_DENS = [ex_density(b) for b in range(1, EX_BARS + 1)]


def mmss(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


def bars_for(sec, bpm):
    return sec * bpm / 240


# ================================================================ genre cards: drum patterns are 16 sixteenth steps (4 per beat)
LANES = ["Hi-hat", "Snare / clap", "Kick"]
GENRES = [
    dict(key="lofi", name="Lo-fi hip-hop", tempo=(70, 90), feel="laid-back, with swing",
         pat={"Hi-hat": "x.x.x.x.x.x.x.x.", "Snare / clap": "....x.......x...", "Kick": "x.........x....."},
         drums="Kick on beat 1 and just after beat 3; snare on beats 2 and 4; hats on every eighth note. Add swing in Logic’s quantize settings.",
         bass="Soft sub or electric bass: long root notes.", chords="Cmaj7 – Am7 – Dm7 – G7 (C major)", cl=["Cmaj7", "Am7", "Dm7", "G7"],
         scale=C_MAJOR, sounds="An electric piano with a low-pass filter, a little Bitcrusher, a quiet Tape Delay.",
         tryit="Play the melody an octave lower, a hair behind the beat."),
    dict(key="house", name="House", tempo=(120, 128), feel="driving, four on the floor",
         pat={"Hi-hat": "..x...x...x...x.", "Snare / clap": "....x.......x...", "Kick": "x...x...x...x..."},
         drums="Kick on every beat; claps on beats 2 and 4; hats on the offbeats (the “and” of each beat).",
         bass="Short synth notes on the offbeats, between the kicks.", chords="Am – F – C – G (A minor or C major)", cl=["Am", "F", "C", "G"],
         scale=C_MAJOR, sounds="Bright synth chords or stabs (Alchemy or Retro Synth), a lead for the melody, a filter-sweep riser.",
         tryit="Use the Compressor’s side chain so the pad ducks on every kick, and cut the kick for a break."),
    dict(key="trap", name="Trap", tempo=(130, 150), feel="half-time: slow and heavy",
         pat={"Hi-hat": "x.x.x.x.x.x.xxxx", "Snare / clap": "........x.......", "Kick": "x.........x....."},
         drums="Snare or clap only on beat 3, halfway through the bar; kick off the beat; busy hats, with a quick roll at the end.",
         bass="808-style: long, low sine-wave notes (a sub bass in Alchemy or Retro Synth).", chords="Cm – Ab – Eb – Bb (C minor)",
         cl=["Cm", "Ab", "Eb", "Bb"], scale=C_MINOR, sounds="A dark pad, a bell or pluck for the melody, crisp hats.",
         tryit="Play the melody half as fast, each note twice as long, so it floats over the beat."),
    dict(key="reggae", name="Reggae", tempo=(70, 80), feel="relaxed, with space",
         pat={"Hi-hat": "x.x.x.x.x.x.x.x.", "Snare / clap": "........x.......", "Kick": "........x......."},
         drums="One drop: kick and snare (or rim) together on beat 3 only, nothing on beat 1; hats on every eighth.",
         bass="Deep and melodic, with plenty of space between notes.", chords="C – F – G – C (C major)", cl=["C", "F", "G"],
         scale=C_MAJOR, sounds="Short chops of keys or guitar-style chords on the offbeats, an organ, a little tape echo.",
         tryit="Leave a gap after every bass note, and sit the melody slightly behind the beat."),
    dict(key="rock", name="Pop-rock", tempo=(100, 130), feel="steady and punchy",
         pat={"Hi-hat": "x.x.x.x.x.x.x.x.", "Snare / clap": "....x.......x...", "Kick": "x.......x......."},
         drums="Kick on beats 1 and 3, snare on beats 2 and 4, hats on every eighth. A Drummer track set to a rock style plays this for you.",
         bass="Root notes in steady eighth notes.", chords="C – G – Am – F (C major)", cl=["C", "G", "Am", "F"], scale=C_MAJOR,
         sounds="An organ or piano for the chords, a clear lead for the melody, a touch of reverb.",
         tryit="Hold the drums back for the intro and bring them in with a fill."),
]
GENRE_BLANK = dict(key="own", name="Your genre")


def genre(key):
    return next(g for g in GENRES if g["key"] == key)


def grid_for(g, W=None, name=None):
    """Drum grid of a genre card as (svg body, w, h); labels logged for the fit check."""
    meas = [{ln: g["pat"][ln] for ln in LANES}]
    return D.grid_body(name or f"grid {g['key']}", meas, [g["name"]], LANES, cw=22, ch=22, gut=140, ls=18, accent_from=0)


def blank_grid(name="grid blank"):
    return D.grid_body(name, [{}], ["Your genre"], LANES, cw=22, ch=22, gut=140, ls=18, accent_from=0, blank=True)


# ================================================================ drawings (original, code-drawn: black + accent only)
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


def flip_notes(bars, a, b):
    t, out = 0, []
    for i, bar in enumerate(bars):
        for p, d in bar:
            if a <= i < b:
                out.append((p, t - a * 16, d))
            t += d
    return out


def flipcmp_body(W=1100, name="flip pic"):
    """Original (C major) above the flip (C minor): bars 1-4 of Jingle Bells; every E becomes Eb."""
    one = roll_body(flip_notes(JINGLE, 0, 4), 64, 16, 4, 59, 68, W, 22, 1, None, name + " a")
    two = roll_body(flip_notes(FLIP, 0, 4), 64, 16, 4, 59, 68, W, 22, 1, None, name + " b", hl=lambda p: p == "Eb4")
    cap1, cap2 = "ORIGINAL · C major", "THE FLIP · C minor: every E becomes Eb"
    body = D.stack([(one[0], one[1], one[2]), (D.t_(W / 2, 22, cap1, 24, 700), W, 34), (two[0], two[1], two[2]),
                    (D.t_(W / 2, 22, cap2, 24, 700, fill_=ACCENT), W, 34)], 6)
    D.lab(name + " caps", cap1, 24, W - 20)
    D.lab(name + " caps", cap2, 24, W - 20)
    return body


def drums_body(name="drums pic"):
    h = grid_for(genre("house"), name=name + " house")
    t = grid_for(genre("trap"), name=name + " trap")
    cap = "Same grid, two genres: house (kick on every beat) and trap (snare on beat 3 only)"
    return D.stack([h, t, (D.t_(430, 22, cap, 22, 500), 860, 34)], 14)


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
    return cards_body([("Choose", "carol + genre"), ("Plan", "what you flip"), ("Enter", "the melody"), ("Flip", "the genre"),
                       ("Arrange", "60–90 seconds")], "Then mix, bounce, present and reflect", W, name, fs, cs)


def hero_body():
    W = 1100
    nts = [(p, s, d) for p, s, d in tune_notes("jingle") if s < 64]
    roll = roll_body(nts, 64, 16, 4, 60, 67, 1000, 34, 1, None, "hero roll", hl=lambda p: p in ("G4", "C4"))
    out = [f'<g transform="translate(50,0)">{roll[0]}</g>']
    y0 = roll[2] + 6
    names = ["REGGAE", "HOUSE", "LO-FI"]
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
    """The worked example's whole 40-bar arrangement: sections, eight layers (some in two parts) and three automation lanes."""
    gx = 300
    pwid = W - gx - 16

    def X(bar):
        return gx + pwid * (bar - 1) / EX_BARS

    out = []
    sh = 54
    shade = {"Intro": "#4a4a4a", "Melody A": "#000", "Break": "#4a4a4a", "Melody B": ACCENT, "Outro": "#4a4a4a"}
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
    for bar in (1, 9, 17, 25, 33, 41):
        t = (bar - 1) * EX_BAR_S
        lbl = mmss(t)
        anc = "start" if bar == 1 else ("end" if bar == 41 else "middle")
        out.append(f'<line x1="{X(bar):.1f}" y1="{ty - 6}" x2="{X(bar):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(bar) + (2 if bar == 1 else (-2 if bar == 41 else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 80)
    cap = f"Bar 1 to bar 40 at {EX_BPM} BPM: {EX_BARS} bars × {EX_BAR_S:g} seconds = {EX_BARS * EX_BAR_S:g} seconds"
    out.append(D.t_(gx + pwid / 2, ty + 8 + ts + 34, cap, ts + 2, 500))
    D.lab(name + " cap", cap, ts + 2, pwid)
    return "".join(out), W, ty + 8 + ts + 48


DRAWINGS = {"hero": hero_body, "cycle": lambda: cycle_body(1600), "roll": lambda: tune_roll("jingle", 0, 4, 1100, "roll deck"),
            "flipcmp": lambda: flipcmp_body(1100), "drums": lambda: drums_body(), "map": lambda: map_body(1600, "map pic")}
DRAWING_PX = {"hero": 1900, "cycle": 2000, "roll": 2000, "flipcmp": 2000, "drums": 2000, "map": 2000}
SIDE = {"cycle": ["Choose a carol and a genre", "Plan what you will flip", "Enter the melody from the chart",
                  "Flip it, arrange it, mix it"],
        "roll": ["Higher bar means higher pitch", "Longer bar means a longer note", "Left to right is time, bar by bar",
                 "The chords are one idea that fits"],
        "flipcmp": ["Same notes, same lengths", "Only the E’s move, down a half step", "Major sounds bright, minor darker",
                    "One flip of the three you need"],
        "map": ["An invented 75-second remix", "Five sections of eight bars", "Eight layers, three automation lanes",
                "Melody B has the most layers"]}


def label_extras():
    for k, T in TUNES.items():
        for a, b in T["systems"]:
            tune_roll(k, a, b, 1100, f"page {k} {a}")
    flipcmp_body(1100, "page flip")
    map_body(1250, "page map", 24, 20)
    cycle_body(1250, "page cycle", 28, 20)
    roll_body([], 64, 16, 4, 60, 72, 1100, 18, 1, None, "blank roll")
    for g in GENRES:
        grid_for(g)
    blank_grid()


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Carol Flip", "Same tune, new genre.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you are going to take a carol everyone knows "
     "and flip it into a new genre in Logic Pro. The three melodies are public domain and arrive as note charts, so every student "
     "can enter them without reading staff notation."),
    (1, "listen", "Think: what stays the same?", "Think, then share|Teacher: say or hum the first line of Jingle Bells slowly and "
     "sadly, then fast and bouncy.|What stayed the same?|What changed?|How much can you change before it "
     "stops being the tune?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker: you say or hum the line yourself, "
     "first slow and sad and then quick and bouncy. Students notice that the notes stayed and the feel changed. That is the whole "
     "project: keep the melody, change the genre around it."),
    (1, "bullets", "What is Carol Flip?", "Choose a public-domain carol|Enter its melody in Logic Pro|Flip it into any genre|Finish "
     "with 60 to 90 seconds",
     "The project in four lines. Students choose Jingle Bells, Deck the Halls or Silent Night; all three are public domain, so "
     "anyone may use the melody. They enter the melody from a piano-roll chart, then flip the tempo, drums, bass, chords and sounds "
     "into a genre of their choice. The finished remix is 60 to 90 seconds. Jingle Bells and Deck the Halls are winter songs; Silent "
     "Night is a Christmas carol. If a student would rather not use a carol, a teacher-approved public-domain melody works."),
    (1, "days", "Four classes", "",
     "The shape of the project. Class 1: hook, choose a carol and a genre, fill in the Flip plan and begin entering the melody. "
     "Class 2: enter and check the melody, then build the drums and bass of the genre. Class 3: add chords and sounds, plan the form, "
     "build the arrangement and mix. Class 4: bounce, hand in, present and reflect. Hand out the project sheet, the charts and the "
     "genre cards now."),
    (1, "pic", "Five moves, then finish", "cycle",
     "Class 1. The five moves in order: choose, plan, enter, flip and arrange. After that students mix, bounce, present and reflect. "
     "Point to each box and say roughly when it happens: choosing and planning today, entering and flipping on Class 2, arranging "
     "on Class 3. The picture and its short labels are drawn for this kit."),
    (1, "pic", "Reading a piano roll", "roll",
     "Class 1. This is the Piano Roll view of the first four bars of the Jingle Bells chorus, drawn the same way as the charts on "
     "students' pages. A higher bar is a higher pitch, a longer bar is a longer note, and time runs left to right. The chord boxes "
     "underneath are one set of chords that fit; other chords can work. Ask a student to read bar 3 aloud: E, G, a long C, a short D."),
    (2, "steps", "Enter the melody", "Set the tempo and the time signature (6/8 for Silent Night)|Make a Software Instrument track and a "
     "MIDI region|Open the Piano Roll and set the grid to sixteenth notes|Draw each note from the chart, bar by bar|Play it back and fix "
     "any wrong note",
     "Class 2. Demonstrate on the projector: set the tempo and, for Silent Night, the 6/8 time signature; create a Software Instrument "
     "track and a MIDI region; open the Piano Roll; set the grid so notes land on sixteenth notes; draw the notes from the chart. "
     "Students then listen for wrong notes. Menu names move between Logic versions; the Logic quick reference lists where things live."),
    (2, "pic", "One flip: major to minor", "flipcmp",
     "Class 2. A flip students can try in seconds: keep every note and every length, but lower each E by a half step to Eb, so the "
     "tune moves from C major to C minor. The notes keep their order and rhythm, so the carol is still recognizable. This is the flip "
     "used in the worked example. Students can do it by selecting the E notes in the Piano Roll and moving them down one row."),
    (2, "pic", "Genre is in the drums", "drums",
     "Class 2. The same 16-step grid in two genres. In house the kick plays on every beat and the claps on 2 and 4. In trap the "
     "snare plays only on beat 3 and the hats are busy, so it feels half as fast. Students copy a pattern from a genre card into the "
     "Step Sequencer or use a Drummer track. Ask: which flip is this, tempo, drums or sounds?"),
    (3, "pic", "Worked example: 75 seconds", "map",
     "Class 3. An invented remix described on paper, nothing here is audio: Jingle Bells in C minor as house music at 128 BPM. Forty "
     "bars at 1.875 seconds a bar is 75 seconds, in five sections of eight bars. Eight layers join and leave, and Melody B has the "
     "most. Three automation lanes keep the sound moving. Students plan their own on the Arrangement plan."),
    (3, "bullets", "Mix it, keep the tune", "Can you name the carol in ten seconds?|Turn the backing down, not the melody up|Can you "
     "hear every layer?|Add one effect that fits the genre",
     "Class 3. Mixing in one idea: the melody is the star. Ask students to play their first 20 seconds and say whether a listener "
     "could name the carol. If the drums or bass bury it, turn the backing down or EQ the melody up. Then check that every layer can "
     "be heard, and add one effect that suits the genre, such as a reverb, a filter or a tape-style delay."),
    (4, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Carol Flip – Carol, Genre|Flip "
     "plan, Arrangement plan, Reflection|Rubric self-score|Three questions for classmates",
     "Class 4. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, Carol "
     "Flip, then the carol and the genre, in that order. Check that every remix is between 60 and 90 seconds before students bounce."),
    (4, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and yours. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (4, "bullets", "Presentation day", "Play your remix, then name the carol|Say the three things you flipped|Your three questions "
     "for classmates|Answer at least 2 of each classmate’s",
     "Class 4, presentations. Each student plays their remix, says which carol it is and names the three things they flipped, then "
     "takes questions. Students write three questions they want classmates to answer, and answer at least two of each classmate's. "
     "Ask the class to name the carol before the presenter does."),
    (4, "closer", "One last thing…", "You picked a carol.|You flipped it.|The tune still shines.|Now press play.",
     "Close with the listening day: play the finished flips without saying the title and let the class name each carol. A melody that "
     "people name quickly is a flip that worked. Ask a few students which of their flips changed the feel most. No audio is included "
     "in this kit; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "4 class periods, slide by slide"), ("jingle", "Piano-roll chart", "Jingle Bells, bar by bar"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 6, 8, 9, 10, 13]
SHOTS3 = [("jingle", "Jingle Bells"), ("deck", "Deck the Halls"), ("silent", "Silent Night"), ("genres1", "Genre cards"),
          ("flip", "Flip plan"), ("example", "Worked example"), ("arrange", "Arrangement plan"), ("tunes", "Tune sources")]

# ================================================================ page plan (teacher pages 2-11, student pages 12-25)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "tunes", "example", "example2", "jingle", "deck", "silent",
        "genres1", "genres2", "flip", "arrange", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "jingle", "genres1", "rubric"]

COVER_A = "Remix a carol in any genre"
COVER_C = "Logic Pro · piano-roll note charts · intro slides"
PDF_COVER = dict(a=28, b=96, c=15, art=7.3)
SQ_COVER = dict(a=44, b=150, c=27, art=740, gap=40)
SQ_B_LINES = ["Carol", "Flip"]
SQ_SUB = "4 class periods · 3 carols · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, charts, genre cards and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Three note charts, five genre cards, a worked example and plans", 28)}
SQ_BANDS = {1: "Choose <em>·</em> plan <em>·</em> enter <em>·</em> flip <em>·</em> arrange",
            2: "Hook <em>·</em> piano roll <em>·</em> major to minor <em>·</em> genre is in the drums",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, recordings, lyrics, artists or albums are named or included. The three melodies are public domain and appear "
             "only as note charts. Students make every sound in their remixes themselves, from the instruments and drum kits in Logic.")
CREDITS = ["Piano-roll note charts of three public-domain melodies (Jingle Bells, 1857; Deck the Halls, a traditional Welsh melody; "
           "Silent Night, 1818), the worked example, the genre cards, the hero, card and arrangement drawings and all layouts: original "
           "work, Hudson Beat. No lyrics, recordings or published editions are included.",
           "No audio, video, album art, screenshots, presets, templates, links or chart data are included. No student work is included."]
LOGIC_INTRO = ("Where to find the tools a Carol Flip is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then let "
               "students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add a Software Instrument track with Track › New Tracks…. Use one track for the "
              "melody and more for bass, chords and sounds."),
             ("Tempo and time signature", "Type the tempo in the control bar. Silent Night is in 6/8: set the time signature before you "
              "enter notes (the control bar, or the Signature track in Global Tracks)."),
             ("Make a region, open the Piano Roll", "With the Pencil tool, click on the track where bar 1 starts to make an empty MIDI "
              "region, then double-click it to open the Piano Roll editor."),
             ("Draw notes from the chart", "Pick a grid value in the Piano Roll’s Snap menu (for example, 1/16 note) so notes land on the "
              "chart’s sixteenth-note grid, click with the Pencil to add a note and drag its right edge to change its length. A MIDI "
              "keyboard is optional."),
             ("Fix wrong notes", "Select a note and drag it up or down a row, or press delete. To lower every E to Eb, select the E "
              "notes together and move them down one row."),
             ("Timing and swing", "In the Region inspector, use Quantize to tighten notes and its swing setting to make a straight "
              "groove bounce, as in lo-fi or reggae."),
             ("Transpose and octaves", "Select a region and change Transpose in the Region inspector to move a whole melody up or down; "
              "12 steps is one octave."),
             ("Drums", "Make a Drummer track and pick a style, or make a Drum Machine Designer track and open the Step Sequencer: click the "
              "16 steps for each drum, as on the genre cards."),
             ("Bass, chords and sounds", "Browse the Library (press Y) for instruments, or open Alchemy, Retro Synth or Vintage Electric Piano. "
              "Session Players (Bass Player, Keyboard Player) can follow a Chord Track in Global Tracks."),
             ("Effects and mixing", "Add plug-ins in a channel strip’s Audio FX slots: Channel EQ, Compressor, Bitcrusher, Tape Delay, "
              "ChromaVerb. Press X for the Mixer, and use each track’s volume and Pan."),
             ("Automation", "Press A to show automation. Pick a parameter, such as a filter cutoff, volume or reverb send, and draw "
              "points so the sound moves."),
             ("Bounce and zip", "File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and "
              "choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my remix:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">Wrong notes: the chart pages (pages @JINGLE, @DECK and @SILENT) list every note by bar, and the Logic quick reference (page @LOGICREF) shows the grid.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Only a speed change: the Flip plan (page @FLIP) asks for three flips, and slide 8 shows one.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">A buried melody: the mix checks on the Arrangement plan (page @ARRANGE) and slide 11.</li>'
    '<li style="font-size:12pt;margin-bottom:0">A genre in name only: the genre cards (pages @GENRES1–@GENRES2) and slide 9.</li></ul></div>')
TN1_SIZE = 12.8
PROJ_SIZE = 12.6
VOCAB_GAP = 14
LOGIC_SIZE = 10.6
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
             ("Student pages", "jingle", "reflect", "Three note charts, genre cards (2 pages), Flip plan, Arrangement plan, project sheet "
              "(3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period remix project for high school music technology. Each '
             f'student chooses one of three public-domain carols, enters its melody into Logic Pro from a piano-roll note chart, and '
             f'flips it into a genre of their choice: new tempo, drums, bass, chords and sounds around the same tune. The remix is 60 to '
             f'90 seconds. Students plan it, build and mix it, present it and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Decide which carols to offer (page {D.IX("tunes")}) and check the setup (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("jingle")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> see the variations on page {D.IX("tn1")}: one looped section on Jingle Bells, or a mode flip with a new melody rhythm.</li>'
             f'<li><b>Carol choice:</b> Jingle Bells and Deck the Halls are winter songs; Silent Night is a Christmas carol. Offer the ones that suit your school, or a public-domain melody you approve.</li>'
             f'<li><b>Feedback:</b> students write three questions and answer classmates’ on a class board or on paper.</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that a '
             f'genre is more than speed: drums, bass, chords and sounds change a tune while the melody stays.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Remix · Logic Pro<br>Take a carol everyone knows and flip it into any genre.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13pt;line-height:1.5">One original remix, 60 to 90 seconds long, of a public-domain carol. The melody is '
             f'entered from a piano-roll chart and stays recognizable; the tempo, drums, bass, chords and sounds belong to the student’s '
             f'chosen genre. It has at least four layers and an intro, melody sections and an outro, is mixed with volume, pan and EQ, and '
             f'uses an effect that suits the genre. Students hand in a bounced .mp3 or .wav and the zipped .logicx project, plus their '
             f'plans and a reflection, then play the remix and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12.6pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.6pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12.6pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.4pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}, music technology or music production</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: choose and plan, enter and flip, arrange and mix, present and reflect</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Piano Roll, instruments, Step Sequencer or Drummer, effects, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a place to hand in files and a class board or paper for feedback</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>Rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s and the '
             f'teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:11.6pt">Students should know how '
             f'to open a project, add a software instrument and use the mixer in Logic. Nobody needs to read music: the charts name every '
             f'pitch and length.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Remix project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.8pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the final listen.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav, the zipped .logicx and the reflection.</li>'
             f'<li><b>The three charts</b>, printed (pages {D.IX("jingle")}, {D.IX("deck")} and {D.IX("silent")}), or shown on the projector.</li>'
             f'<li><b>The genre cards</b>, printed (pages {D.IX("genres1")}–{D.IX("genres2")}).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("jingle")}–{D.IX("reflect")}).</li>'
             f'<li><b>A MIDI keyboard</b> is optional: every melody can be drawn with the mouse.</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.8pt;margin-bottom:7pt") for c in [
                 "Decide which carols you will offer (page @TUNES).".replace("@TUNES", str(D.IX("tunes"))),
                 "Open Logic Pro on a student computer: can you make a track, open the Piano Roll and hear playback through headphones?",
                 "Decide how students will give each other feedback (a class board, or paper).",
                 "Read the worked example (pages @A–@B).".replace("@A", str(D.IX("example"))).replace("@B", str(D.IX("example2")))]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.6pt">Students enter the notes but get a wrong one, the flip is only a speed change, the melody is buried, '
             f'or a genre is a name and nothing more. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.4pt">Ask while students work: which of your three flips is this? Can you hear the carol?</li>'
             f'<li style="font-size:11.4pt">On Class 1, say each genre’s tempo range aloud and tap it: 70 for lo-fi, 128 for house.</li>'
             f'<li style="font-size:11.4pt">A student who is stuck on a genre can start from a Drummer track and flip the rest.</li></ul></div>'
             f'{D.H2("Choosing carols")}'
             f'<div class="box"><span class="k">A respectful choice</span><p style="margin:0;font-size:11.2pt;line-height:1.4">'
             f'Jingle Bells and Deck the Halls are winter songs; Silent Night is a Christmas carol. Offer the ones that fit your school and '
             f'let students choose. If a student prefers another melody, a public-domain one you approve (first published in the United '
             f'States in 1930 or earlier) works with the same plan, and the blank piano roll on page {D.IX("flip")} is there for their own chart.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.2pt;line-height:1.4">'
             f'Bass-heavy genres and loud peaks are tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


def tunes_page(n, wm=False):
    rows = ""
    for k in ("jingle", "deck", "silent"):
        T = TUNES[k]
        yr = str(T["year"]) if T["year"] else "centuries old"
        rows += (f"<tr><td><b>{T['title']}</b><br>{T['part']}</td><td>{T['who']}<br>{yr}</td><td>{T['key']}, {T['time']}<br>"
                 f"{len(T['bars'])} bars, {note_count(k)} notes</td><td>{T['good']}</td></tr>")
    srcs = "".join(f"<li><b>{TUNES[k]['title']}:</b> {TUNES[k]['src']}</li>" for k in ("jingle", "deck", "silent"))
    inner = (f'<p style="margin:0 0 4pt;font-size:11.6pt;line-height:1.42">All three melodies are in the public domain, and each is printed '
             f'here as a note chart only: no lyrics, no recordings and no published edition. The charts are written in C major (all white keys) '
             f'so the pitches are easy to read, and checked against the notes in code.</p>'
             f'<table class="t" style="font-size:10.4pt"><tr><th style="width:21%">Tune</th><th style="width:24%">By · year</th><th style="width:19%">In this kit</th>'
             f'<th>Good for</th></tr>{rows}</table>'
             f'{D.H2("Where the tunes come from")}<ul style="font-size:11pt">{srcs}</ul>'
             f'{D.H2("The public-domain rule")}<p style="font-size:11.4pt;line-height:1.42">In 2026 a melody is in the public domain in the United '
             f'States when it was first published in 1930 or earlier (1931 from 1 January 2027). If a student suggests another carol or '
             f'winter song, check its first publication date before you approve it, and never use a recording, a film or pop version, or '
             f'its lyrics unless they are public domain too.</p>'
             f'{D.H2("Picking a tune for a student")}<ul style="font-size:11pt"><li><b>First time in the Piano Roll:</b> Jingle Bells. One repeated note, then a few skips.</li>'
             f'<li><b>Likes to loop and layer:</b> Deck the Halls. Four bars repeat well under any groove, and there is a blank piano roll to write an answer phrase.</li>'
             f'<li><b>Wants a challenge, or a slow, gentle genre:</b> Silent Night, in 6/8.</li></ul>'
             f'<div class="cols" style="gap:12pt;margin-top:4pt"><div class="box acc-b"><span class="k">Reading the charts</span><p style="margin:0;font-size:10.6pt;line-height:1.38">'
             f'Pitch names run down the left; middle C is C4. Bold lines are bars, grey lines are beats. A note’s length is the name beside it: '
             f'16th, eighth, dotted eighth, quarter, dotted quarter, half, dotted half or whole. Chords are one idea that fits, not the only one.</p></div>'
             f'<div class="box"><span class="k">Why 6/8 is harder</span><p style="margin:0;font-size:10.6pt;line-height:1.38">'
             f'Silent Night has six eighth notes in a bar, felt as two groups of three. Students set 6/8 in Logic first. Offer it to students '
             f'who want a challenge or a slow, gentle genre.</p></div></div>')
    return D.page("Tune sources and the public-domain rule", "TEACHER", "Tunes", inner, n, key="tunes")


def chart_page(key):
    def build(n, wm=False):
        T = TUNES[key]
        yr = str(T["year"]) if T["year"] else "centuries old"
        glance = (f'<p style="margin:0 0 3pt;font-size:10.4pt"><b>{T["title"]}</b>, {T["part"]} · {T["who"]}, {yr} · {T["key"]}, {T["time"]} · '
                  f'{len(T["bars"])} bars · {note_count(key)} notes</p>')
        systems = "".join(f'<div style="margin:0 0 2pt">{D.body_svg(tune_roll(key, a, b, 1100, f"page {key} {a}"))}</div>' for a, b in T["systems"])
        nb = len(T["bars"])
        half = (nb + 1) // 2 if nb > 4 else nb
        fs = 8.4 if key == "silent" else 10

        def tab(a, b):
            rr = "".join(f"<tr><td style='width:11%'><b>{i + 1}</b></td><td>{bar_text(T['bars'][i])}</td><td style='width:15%;white-space:nowrap'>{chord_text(T['chords'][i])}</td></tr>"
                         for i in range(a, b))
            return (f'<table class="t" style="font-size:{fs}pt;line-height:1.16;margin:2pt 0 3pt"><tr><th>Bar</th><th>Notes (pitch, length)</th><th>Chords</th></tr>{rr}</table>')
        if nb > 4:
            tabs = f'<div class="cols" style="gap:10pt"><div>{tab(0, half)}</div><div>{tab(half, nb)}</div></div>'
        else:
            tabs = tab(0, nb)
        more = ""
        if key == "deck":
            blank = D.body_svg(roll_body([], 64, 16, 4, 60, 72, 1100, 20, 5, None, "blank roll deck"))
            more = (f'<span class="k" style="margin-top:6pt">Your turn: write an answer phrase for bars 5–8 (pencil), ending on C</span>'
                    f'<div style="margin-top:2pt">{blank}</div>')
        about = f'{T["src"]} {T["tip"]}' + (" Chords shown are one idea that fits; try others by ear." if key != "silent" else "")
        inner = (f'{glance}{systems}{tabs}{more}'
                 f'<div class="box acc-b" style="margin-top:4pt;padding:4pt 10pt"><span class="k">About this chart</span><p style="margin:0;font-size:9.4pt;line-height:1.3">'
                 f'{about}</p></div>')
        return D.page(f"Note chart · {T['title']}", "STUDENT", "Class 1", inner, n, wm, name=True, key=key)
    return build


def genre_card(g):
    if g["key"] == "own":
        body, w, h = blank_grid()
        txt = ('<p style="margin:0 0 3pt;font-size:10.4pt">Pick a genre that is not on these cards. Listen to two or three tracks in it '
               '(not included in this kit), then fill in the card.</p>'
               '<div class="fl" style="margin:0 0 5pt;font-size:10.4pt"><b>Tempo range:</b><span></span></div>'
               '<div class="fl" style="margin:0 0 5pt;font-size:10.4pt"><b>Drums:</b><span></span></div>'
               '<div class="fl" style="margin:0 0 5pt;font-size:10.4pt"><b>Bass:</b><span></span></div>'
               '<div class="fl" style="margin:0 0 5pt;font-size:10.4pt"><b>Chords:</b><span></span></div>'
               '<div class="fl" style="margin:0 0 5pt;font-size:10.4pt"><b>Sounds:</b><span></span></div>')
        head = '<span class="k" style="font-size:12pt;margin:0">Your genre · fill in your own card</span>'
        foot = '<p class="small" style="margin:2pt 0 0">Click the steps you want in the grid: 16 steps = 1 bar, 4 steps = 1 beat.</p>'
    else:
        body, w, h = grid_for(g)
        a, b = g["tempo"]
        txt = (f'<p style="margin:0 0 2pt;font-size:10.2pt;line-height:1.3"><b>Drums.</b> {g["drums"]}</p>'
               f'<p style="margin:0 0 2pt;font-size:10.2pt;line-height:1.3"><b>Bass.</b> {g["bass"]}</p>'
               f'<p style="margin:0 0 2pt;font-size:10.2pt;line-height:1.3"><b>Chords.</b> {g["chords"]}</p>'
               f'<p style="margin:0 0 2pt;font-size:10.2pt;line-height:1.3"><b>Sounds.</b> {g["sounds"]}</p>'
               f'<p style="margin:0;font-size:10.2pt;line-height:1.3"><b>Try.</b> {g["tryit"]}</p>')
        head = (f'<span class="k" style="font-size:13pt;margin:0">{g["name"]} · {a}–{b} BPM · {g["feel"]}</span>')
        foot = ""
    return (f'<div class="box" style="margin-bottom:6pt;padding:6pt 10pt">{head}<div style="display:flex;gap:12pt;margin-top:3pt;align-items:flex-start">'
            f'<div style="flex:1">{txt}</div><div style="width:3.55in;flex:0 0 3.55in">{D.body_svg((body, w, h))}{foot}</div></div></div>')


def genres1_page(n, wm=False):
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt;line-height:1.38">A genre is a bundle of choices. Each card gives the tempo range, a one-bar '
             f'drum pattern (16 steps, 4 to a beat; shaded steps are the beats), a bass idea, chords in a key that works with the carol charts, and '
             f'sounds to try. Copy a pattern into the Step Sequencer, or use a Drummer track. Page {D.IX("genres2")} has two more cards and a blank one.</p>'
             + "".join(genre_card(genre(k)) for k in ("lofi", "house", "trap")))
    return D.page("Genre cards · 1 of 2", "STUDENT", "Classes 1–2", inner, n, wm, name=False, key="genres1")


def genres2_page(n, wm=False):
    inner = ("".join(genre_card(genre(k)) for k in ("reggae", "rock")) + genre_card(GENRE_BLANK))
    return D.page("Genre cards · 2 of 2", "STUDENT", "Classes 1–2", inner, n, wm, name=False, key="genres2")


FLIP_MENU = ["Tempo", "Drums", "Bass", "Chords", "Sounds", "Rhythm of the melody", "Octave", "Mode or key", "Effects"]


def flip_page(n, wm=False):
    half = (len(FLIP_MENU) + 1) // 2
    items = [D.chk(f"<b>{m}</b> — how: <span style='display:inline-block;width:1.2in;border-bottom:1pt solid #000'>&nbsp;</span>", 11,
                   "font-size:10.2pt;margin-bottom:4pt") for m in FLIP_MENU]
    rows = "".join("<tr><td style='height:21pt'></td><td></td><td></td></tr>" for _ in range(5))
    roll = D.body_svg(roll_body([], 64, 16, 4, 60, 72, 1100, 17, 1, None, "blank roll"))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.36">Step 2: plan. Pick one carol and one genre, then decide what you will flip. '
             f'You need at least three flips (requirement 3), and the carol must still be recognizable.</p>'
             f'<div class="box acc-b" style="margin:0 0 5pt"><span class="k">My choices</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>My carol:</b><span></span><b>My genre:</b><span></span></div>'
             f'<div class="fl" style="margin:0"><b>Tempo (BPM):</b><span style="flex:0 0 0.9in"></span><b>Key or mode:</b><span></span>'
             f'<b>Why this tempo:</b><span></span></div></div>'
             f'<span class="k">What I flip (check at least three)</span>'
             f'<div class="cols" style="gap:12pt"><div>{"".join(items[:half])}</div><div>{"".join(items[half:])}</div></div>'
             f'<div class="fl" style="margin-top:3pt"><b>What stays the same, so people still know the tune:</b><span></span></div>'
             f'<span class="k">My layers</span>'
             f'<table class="map" style="margin-bottom:4pt"><tr><th style="width:18%">Layer</th><th style="width:38%">Sound or instrument in Logic</th>'
             f'<th>What it plays</th></tr>{rows}</table>'
             f'<span class="k">Sketch: a changed rhythm for the first four bars (pencil, optional)</span>'
             f'<div style="margin-top:2pt">{roll}</div>')
    return D.page("Flip plan", "STUDENT", "Class 1", inner, n, wm, name=True, key="flip")


def arrange_page(n, wm=False):
    nb = 40
    head = "<tr><th style='width:1.1in'>Layer</th>" + "".join(f"<th>{i + 1}</th>" for i in range(nb)) + "</tr>"
    body = "".join("<tr><td class='l' style='height:25pt'></td>" + "".join(f"<td class='{'b' if i % 8 == 0 else ''}'></td>" for i in range(nb))
                   + "</tr>" for _ in range(8))
    help_rows = [(80, 20, 25, 30), (96, 24, 30, 36), (112, 28, 35, 42), (128, 32, 40, 48), (144, 36, 45, 54)]
    hr = "".join(f"<tr><td><b>{b}</b></td><td>{240 / b:.4g} s</td><td>{x}</td><td>{y}</td><td>{z}</td></tr>" for b, x, y, z in help_rows)
    inner = (f'{CSS_SG}<style>table.sg th {{ font-size: 4.6pt; }} table.sg td.l {{ width: 1.1in; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.4pt">Step 5: arrange. Give your remix a form: an intro, melody sections and an outro. Shade the bars where each '
             f'layer plays, write the layer’s name at the left, and mark where each section starts (every thick line is 8 bars). 60 to 90 seconds only.</p>'
             f'<table class="sg">{head}{body}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:6pt"><div class="box acc-b"><span class="k">My sections</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Intro:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Melody:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Break or change:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>Outro:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div></div>'
             f'<div><span class="k">Length helper (4/4)</span><table class="t" style="font-size:9.4pt;margin-top:2pt"><tr><th>BPM</th><th>One bar</th>'
             f'<th>60 s</th><th>75 s</th><th>90 s</th></tr>{hr}</table><p class="small" style="margin:1pt 0 0">Bars needed for each length. '
             f'Bars × 240 ÷ BPM = seconds. In 6/8, read the length from Logic’s clock.</p></div></div>'
             f'<div class="fl" style="margin-top:6pt"><b>My tempo:</b><span style="flex:0 0 0.8in"></span><b>Bars:</b><span style="flex:0 0 0.8in"></span>'
             f'<b>Length: bars × 240 ÷ tempo =</b><span style="flex:0 0 0.8in"></span><b>seconds</b></div>'
             f'<div class="box" style="margin-top:4pt"><span class="k">Checks before I bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:2pt") for c in [
                 "I can name the carol in the first ten seconds, and the melody is louder than the drums and bass.",
                 "Every pitch and length matches the chart, or a change I planned.",
                 "I can hear every layer, and none is buried or too loud.",
                 "At least one effect fits my genre, and EQ is in use.",
                 "The remix is between 60 and 90 seconds."]) + '</div>')
    return D.page("Arrangement plan", "STUDENT", "Classes 2–3", inner, n, wm, name=True, key="arrange")


def example_page(n, wm=False):
    flips = "".join(f"<tr><td style='width:14%'><b>{a}</b></td><td>{b}</td></tr>" for a, b in EX_FLIPS)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.2pt">An <b>invented plan on paper</b>: Jingle Bells, the 8-bar chorus, flipped to C minor as house music at '
             f'{EX_BPM} BPM. No audio is included. Student projects will differ. Page 1 of 2: the plan and the flip.</p>'
             f'<div class="cols" style="gap:10pt"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no carol part and nothing that changes.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.8pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · Five flips, and what stays")}'
             f'<table class="t" style="font-size:9.4pt;line-height:1.22">{flips}<tr><td><b>Stays</b></td><td>{EX_STAYS}</td></tr></table>'
             f'{D.H2("4 · The mode flip on the piano roll (bars 1–4)")}'
             f'<div style="width:6.6in;margin:2pt auto 0">{D.body_svg(flipcmp_body(1100, "page flip"))}</div>')
    return D.page("Worked example · an invented flip", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    secs = "".join(f"<tr><td style='width:22%'><b>{nm}</b></td><td style='white-space:nowrap'>bars {a}–{b}</td><td>{mmss((a - 1) * EX_BAR_S)}–{mmss(b * EX_BAR_S)}</td></tr>"
                   for nm, a, b in EX_SECTIONS)
    lay = "".join(f"<tr><td style='width:17%'><b>{nm}</b></td><td>{d}</td></tr>" for nm, _s, d in EX_LAYERS)
    chs = "".join(f"<td>{c}<br><span style='font-size:7.4pt'>bass {FLIP_BASS[c]}</span><br><span style='font-size:7.4pt'>bar {i + 1}</span></td>"
                  for i, c in enumerate(FLIP_CH))
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same remix, page 2 of 2: the map of the whole piece, then the numbers.</p>'
             f'{D.H2("5 · The map: 1:15, five sections, eight layers, three lanes")}'
             f'<div style="width:6.5in;margin:1pt auto 3pt">{D.body_svg(map_body(1250, "page map", 24, 20))}</div>'
             f'<div class="cols" style="gap:10pt"><div><span class="k" style="font-size:9.4pt">6 · Sections</span>'
             f'<table class="t" style="font-size:8.6pt;line-height:1.2;margin-top:2pt">{secs}</table></div>'
             f'<div><span class="k" style="font-size:9.4pt">7 · Layers (in to out)</span>'
             f'<table class="t" style="font-size:8pt;line-height:1.16;margin-top:2pt">{lay}</table></div></div>'
             f'<span class="k" style="font-size:9.4pt;display:block;margin-top:3pt">8 · The chords of the 8-bar loop, with the bass root (the melody’s long notes are chord tones)</span>'
             f'<table class="t" style="font-size:8.8pt;line-height:1.1;margin-top:2pt;text-align:center"><tr>{chs}</tr></table>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">9 · Checking the numbers</span><p style="margin:0;font-size:8.6pt;line-height:1.28">'
             f'One bar of 4/4 at {EX_BPM} BPM lasts 240 ÷ {EX_BPM} = {EX_BAR_S:g} seconds, so {EX_BARS} bars = {EX_BARS * EX_BAR_S:g} seconds, inside 60 to 90. '
             f'The sections are {" + ".join(str(b - a + 1) for _, a, b in EX_SECTIONS)} bars = {EX_BARS}. Melody B has the most layers ({max(EX_DENS)}). '
             f'<b>Three feedback questions (invented):</b> {qs}</p></div>')
    return D.page("Worked example · the map", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "tunes": tunes_page, "example": example_page,
         "example2": example2_page, "jingle": chart_page("jingle"), "deck": chart_page("deck"), "silent": chart_page("silent"),
         "genres1": genres1_page, "genres2": genres2_page, "flip": flip_page, "arrange": arrange_page}


# ================================================================ content checks (melodies, drums, the worked example, no audio)
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
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 4), reqs=(REQS, 6), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 3))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    # ---- the three melodies
    expect = {"jingle": (8, 25, 16, "C4", "G4", "G4"), "deck": (4, 19, 16, "B3", "G4", "F4"), "silent": (12, 46, 12, "C4", "F5", "C4")}
    for k, T in TUNES.items():
        nb, nn, bl, lo, hi, last = expect[k]
        if len(T["bars"]) != nb or len(T["chords"]) != nb:
            errs.append(f"{k}: {nb} bars and a chord pair for each expected")
        if T["bar_len"] != bl or (T["time"] == "4/4") != (bl == 16) or (T["time"] == "6/8") != (bl == 12):
            errs.append(f"{k}: bar length {T['bar_len']} sixteenths does not match {T['time']}")
        for i, bar in enumerate(T["bars"]):
            if sum(d for _, d in bar) != bl:
                errs.append(f"{k}: bar {i + 1} adds to {sum(d for _, d in bar)} sixteenths, not {bl}")
            for p, d in bar:
                if d not in LEN_NAMES:
                    errs.append(f"{k}: bar {i + 1} has a length ({d}) with no name")
                if p[:-1] not in C_MAJOR:
                    errs.append(f"{k}: {p} is not a white key (charts are in C major)")
        if note_count(k) != nn:
            errs.append(f"{k}: {note_count(k)} notes, expected {nn}")
        ms = [midi(p) for p, _, _ in tune_notes(k)]
        if min(ms) != midi(lo) or max(ms) != midi(hi):
            errs.append(f"{k}: range {pname(min(ms))}-{pname(max(ms))}, expected {lo}-{hi}")
        if not T["lo"] <= min(ms) or not max(ms) <= T["hi"]:
            errs.append(f"{k}: the roll's rows do not cover the notes")
        if T["bars"][-1][-1][0] != last:
            errs.append(f"{k}: last note {T['bars'][-1][-1][0]}, expected {last}")
        for i, (c1, c2) in enumerate(T["chords"]):
            for half, ch in enumerate((c1, c2)):
                bl2 = bl // 2
                if not seg_ok(tune_notes(k), i * bl + half * bl2, i * bl + (half + 1) * bl2, ch):
                    errs.append(f"{k}: chord {ch} in bar {i + 1} half {half + 1} does not hold the first and longest notes")
        if k == "jingle" and [ms[:3], ms[3:6]] != [[64, 64, 64], [64, 64, 64]]:
            errs.append("jingle: bars 1 and 2 are E E E")
    if [p for p, _ in JINGLE[2]] != ["E4", "G4", "C4", "D4"] or [d for _, d in JINGLE[2]] != [4, 4, 6, 2]:
        errs.append("jingle bar 3 is E G C. D (quarter, quarter, dotted quarter, eighth)")
    if [p for p, _ in JINGLE[4]] != ["F4"] * 4 or [d for _, d in JINGLE[7]] != [8, 8] or JINGLE[7][0][0] != "D4" or JINGLE[7][1][0] != "G4":
        errs.append("jingle bars 5 and 8 changed")
    if [p for p, _ in DECK[0]] != ["G4", "F4", "E4", "D4"] or [p for p, _ in DECK[1]] != ["C4", "D4", "E4", "C4"]:
        errs.append("deck the halls bars 1-2 are G F E D / C D E C")
    if [p for p, _ in SILENT[0]] != ["G4", "A4", "G4", "E4"] or [d for _, d in SILENT[0]] != [3, 1, 2, 6]:
        errs.append("silent night bar 1 is G. A G E with the dotted-eighth, sixteenth rhythm")
    if SILENT[2][2][0] != "B4" or SILENT[9][1][0] != "E5" or SILENT[11] != [("C4", 12)]:
        errs.append("silent night bars 3, 10 and 12 changed")
    for k in TUNES:
        for i, bar in enumerate(TUNES[k]["bars"]):
            if len(bar) < 1:
                errs.append(f"{k}: empty bar {i + 1}")
    # ---- the flip: same notes, E becomes Eb, nothing else
    for bj, bf in zip(JINGLE, FLIP):
        for (pj, dj), (pf, df) in zip(bj, bf):
            if dj != df or (pj == "E4") != (pf == "Eb4") or (pj != "E4" and pj != pf):
                errs.append("the flip changes only E to Eb, never a length")
    if any(p[:-1] not in C_MINOR for bar in FLIP for p, _ in bar):
        errs.append("the flip must be in C minor")
    if sum(p == "Eb4" for bar in FLIP for p, _ in bar) != sum(p == "E4" for bar in JINGLE for p, _ in bar):
        errs.append("every E becomes Eb")
    fn = [(p, s, d) for p, s, d in flip_notes(FLIP, 0, 8)]
    for i, ch in enumerate(FLIP_CH):
        for half in range(2):
            if not seg_ok(fn, i * 16 + half * 8, i * 16 + half * 8 + 8, ch):
                errs.append(f"flip chord {ch} in bar {i + 1} half {half + 1} does not hold the first and longest notes")
        if FLIP_BASS[ch].rstrip("0123456789") not in CHORD_TONES[ch] or ch[0] != FLIP_BASS[ch][0]:
            errs.append(f"bass root for {ch}")
    # ---- genre cards: patterns have 16 steps and the facts the cards claim
    for g in GENRES:
        if any(len(g["pat"][ln]) != 16 or set(g["pat"][ln]) - {"x", "."} for ln in LANES):
            errs.append(f"{g['key']}: each drum lane is 16 steps of x and .")
        a, b = g["tempo"]
        if not 60 <= a < b <= 160:
            errs.append(f"{g['key']}: tempo range")
        for ch in g["cl"]:
            if not CHORD_TONES[ch] <= g["scale"]:
                errs.append(f"{g['key']}: chord {ch} is not in its key")
    hit = lambda g, ln: [i for i, c in enumerate(g["pat"][ln]) if c == "x"]
    h, t, r, rk, lf = genre("house"), genre("trap"), genre("reggae"), genre("rock"), genre("lofi")
    if hit(h, "Kick") != [0, 4, 8, 12] or hit(h, "Snare / clap") != [4, 12] or hit(h, "Hi-hat") != [2, 6, 10, 14]:
        errs.append("house: kick on every beat, claps on 2 and 4, hats on the offbeats")
    if hit(t, "Snare / clap") != [8] or 0 not in hit(t, "Kick") or len(hit(t, "Hi-hat")) < 10:
        errs.append("trap: snare on beat 3 only, busy hats")
    if hit(r, "Kick") != [8] or hit(r, "Snare / clap") != [8] or hit(r, "Hi-hat") != list(range(0, 16, 2)):
        errs.append("reggae: one drop (kick and snare on beat 3 only), hats on eighths")
    if hit(rk, "Kick") != [0, 8] or hit(rk, "Snare / clap") != [4, 12]:
        errs.append("pop-rock: kick on 1 and 3, snare on 2 and 4")
    if hit(lf, "Kick") != [0, 10] or hit(lf, "Snare / clap") != [4, 12] or hit(lf, "Hi-hat") != list(range(0, 16, 2)):
        errs.append("lo-fi: kick on 1 and the 'and' of 3, snare on 2 and 4, hats on eighths")
    # ---- the worked example adds up
    if EX_BAR_S != 1.875 or EX_BARS * EX_BAR_S != 75 or not 60 <= EX_BARS * EX_BAR_S <= 90:
        errs.append("40 bars x 1.875 s = 75 s, inside 60 to 90")
    if not 120 <= EX_BPM <= 128 or genre("house")["tempo"] != (120, 128):
        errs.append("house at 128 BPM sits inside the house range")
    if EX_SECTIONS[0][1] != 1 or EX_SECTIONS[-1][2] != EX_BARS or any(b + 1 != c for (_, _, b), (_, c, _) in zip(EX_SECTIONS, EX_SECTIONS[1:])):
        errs.append("sections must tile bars 1-40")
    if [b - a + 1 for _, a, b in EX_SECTIONS] != [8] * 5 or sum(b - a + 1 for _, a, b in EX_SECTIONS) != EX_BARS:
        errs.append("five sections of 8 bars = 40")
    if len(EX_LAYERS) != 8 or len(EX_AUTO) != 3 or len(FLIP) != 8:
        errs.append("eight layers, three automation lanes, an 8-bar melody")
    for nm, spans, _d in EX_LAYERS:
        for a, b in spans:
            if not 1 <= a <= b <= EX_BARS:
                errs.append(f"layer {nm}: span {a}-{b} outside the piece")
    spans = {nm: (min(a for a, _ in sp), max(b for _, b in sp)) for nm, sp, _ in EX_LAYERS}
    for ly, par, pts in EX_AUTO:
        a, b = spans[ly]
        ts = [t_ for t_, _ in pts]
        vs = [v for _, v in pts]
        if ts != sorted(ts) or len(pts) < 3 or ts[0] < a or ts[-1] > b:
            errs.append(f"lane {ly}/{par}: points in order, 3+, inside its layer")
        if max(vs) - min(vs) < .5:
            errs.append(f"lane {ly}/{par}: a lane that barely moves")
    top = max(EX_DENS)
    mb = next((a, b) for nm, a, b in EX_SECTIONS if nm == "Melody B")
    if [i + 1 for i, d in enumerate(EX_DENS) if d == top] != list(range(mb[0], mb[1] + 1)):
        errs.append("the most layers must play in exactly Melody B")
    if EX_DENS[0] >= top or EX_DENS[-1] >= top or min(EX_DENS[16:24]) >= EX_DENS[10]:
        errs.append("the piece starts smaller than its peak, drops in the Break and resolves down")
    for bpm in (80, 96, 112, 128, 144):
        for sec, bars in zip((60, 75, 90), {80: (20, 25, 30), 96: (24, 30, 36), 112: (28, 35, 42), 128: (32, 40, 48), 144: (36, 45, 54)}[bpm]):
            if bars_for(sec, bpm) != bars:
                errs.append(f"length helper wrong at {bpm} BPM, {sec} s")
    if len(EX_QUESTIONS) != 3:
        errs.append("three feedback questions")
    if "♭" in EX_STRONG or "♭" in EX_FLIPS[0][1]:
        errs.append("plain text only (no flat sign) in the clear plan")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    txt = " ".join(flat)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, lyrics, artists or albums", "invented plan on paper", "public domain", "Pierpont", "Gruber", "1857",
                 "1818", "Nos Galan", "1930 or earlier", "No student work is included",
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
    for k in ("jingle", "deck", "silent"):
        raw = re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-raw", "-f", str(D.IX(k)), "-l", str(D.IX(k)), D.files()["pdf"], "-"],
                                                 capture_output=True, text=True, check=True).stdout)
        for i, bar in enumerate(TUNES[k]["bars"]):
            if bar_text(bar) not in raw:
                errs.append(f"{k} chart page: bar {i + 1} '{bar_text(bar)}' is not printed")
    for g in GENRES:
        if g["name"] not in " ".join(flat[D.IX("genres1") - 1:D.IX("genres2")]) or f"{g['tempo'][0]}–{g['tempo'][1]} BPM" not in " ".join(flat[D.IX("genres1") - 1:D.IX("genres2")]):
            errs.append(f"genre card {g['name']} (name and tempo range) missing")
    ex = " ".join(flat[D.IX("example") - 1:D.IX("example2")])
    for need in ("240 ÷ 128 = 1.875", "40 bars = 75 seconds", "8 + 8 + 8 + 8 + 8 bars = 40", "every E becomes Eb"):
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
    return (f"Jingle Bells chorus (8 bars, {note_count('jingle')} notes), Deck the Halls phrase (4 bars, {note_count('deck')} notes) and Silent Night (12 bars of 6/8, {note_count('silent')} notes) add up "
            f"bar by bar, use only white keys, and every chord suggestion holds each half-bar's first and longest note; the flip changes only E to Eb "
            f"and is in C minor; {len(GENRES)} genre drum patterns match what their cards say; the worked example is {EX_BARS} bars at {EX_BPM} BPM = "
            f"{EX_BARS * EX_BAR_S:g} s (sections {'+'.join(str(b - a + 1) for _, a, b in EX_SECTIONS)}, {len(EX_LAYERS)} layers, peak {max(EX_DENS)} layers only in "
            f"Melody B, {len(EX_AUTO)} moving lanes); length helper integral; no audio, lyrics, artist names or student work; grades 9-12; "
            f"no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students choose a public-domain carol, enter its melody into Logic Pro from a piano-roll note chart, and remix it "
            f"in any genre, from lo-fi and house to trap and reggae. This Carol Flip project takes {CLASSES} class periods and is an original "
            f"Hudson Beat project; the steps are written for Logic Pro, while the ideas (tempo, drums, bass, chords and sounds make a genre) "
            f"carry over to GarageBand, Ableton Live and BandLab.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + 10 teacher + {np_ - 12} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, two pages of teacher notes "
            f"(struggles, variations, resources, grading), a Logic quick reference, tune sources and the public-domain rule, and a two-page worked "
            f"example (an invented plan on paper: Jingle Bells flipped to C minor as house music, with its five flips, a 40-bar map, eight layers, "
            f"chords and three automation lanes) (10 pages)\n"
            f"• Student pages: three piano-roll note charts (Jingle Bells chorus, Deck the Halls phrase, Silent Night in 6/8) with every note listed "
            f"bar by bar, five genre cards with drum grids plus a blank card, a Flip plan, an Arrangement plan with a length helper, the 3-page project "
            f"sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a feedback "
            f"planner and a reflection page ({np_ - 12} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what Carol Flip is, how to read a "
            f"piano roll, entering the melody, a major-to-minor flip, genre in the drums, a worked-example map, mixing, what to turn in and the rubric\n\n"
            f"THE FOUR CLASS PERIODS\n"
            f"• Class 1: hook; choose a carol and a genre; fill in the Flip plan; start entering the melody\n"
            f"• Class 2: enter and check the melody; build the drums and bass of the genre\n"
            f"• Class 3: add chords and sounds; plan the form; build the arrangement and mix\n"
            f"• Class 4: bounce and hand in; presentations with feedback questions; reflection\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Entering and editing notes in Logic Pro's Piano Roll from a note chart\n"
            f"• What makes a genre: tempo, drums, bass, chords and sounds, not only speed\n"
            f"• Keeping a melody recognizable while everything around it changes\n"
            f"• Planning a 60 to 90 second arrangement with an intro, melody sections and an outro\n"
            f"• Balancing a mix and explaining their choices in a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. The three melodies are in the public domain and appear only as note charts, "
            f"with no lyrics; students make every sound themselves in Logic Pro\n"
            f"• Jingle Bells and Deck the Halls are winter songs; Silent Night is a Christmas carol. Offer the ones that suit your school\n"
            f"• Requires Logic Pro on a Mac. A MIDI keyboard is not needed; nobody has to read staff notation\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"{D.DISCLOSURE_NEW}")
    md = f"""# UPLOAD: Carol Flip, original Logic Pro holiday project (TpT 031)

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

Per tpt/METADATA-GUIDE.md, `tpt.json` keeps only values TpT has accepted or the subject list offers.
- Subjects in tpt.json: Music; Computer Science - Technology; Music Composition (all three are in `tpt/SUBJECT-OPTIONS.json`)
- Tags in tpt.json: Winter (proven). Candidate extras, only if the Tag box offers them: High School, Project Based Learning, Technology, Christmas, Creativity (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**${PRICE}** (paid), multiple-license price ${PRICE}. Top of the first-kit range in the queue ($9) for a kit this size ({np_} pages + {ns} slides, three note charts, five genre cards, a two-page worked example) and a hook buyers search for in November and December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the Jingle Bells note chart, the first genre cards page and the /25 rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Tunes are public domain (year and source for QA.md).** Jingle Bells, the chorus: James Lord Pierpont, first published in Boston in 1857 as "One Horse Open Sleigh". Deck the Halls, the first phrase: traditional Welsh melody "Nos Galan", centuries old and in print long before 1930; the 1862 English words are not used. Silent Night: Franz Xaver Gruber, composed 1818; melody only, no words. All three are shown as note charts transcribed for this kit (pitches checked against public-domain transcriptions, then moved to C major); no published edition is reproduced.
- [ ] **Original project.** This is the first kit built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py`: no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row.
- [ ] **Open question for the owner:** (1) **Carols and schools.** Silent Night is a Christmas carol; the kit offers it next to two winter songs and tells teachers to choose what suits their school. Say if you want a secular-only version of the charts or a fourth winter melody. (2) **Tags and the season.** Only "Winter" is a proven tag; the candidate extras above need a dry run on the Mac. (3) **Price.** $9 is the top of the holiday-kit range; say if you would rather list it at $8 for launch.
"""
    with open(os.path.join(HERE, "UPLOAD.md"), "w", encoding="utf8") as f:
        f.write(md)


if __name__ == "__main__":
    if "--check" not in sys.argv:
        write_upload()
    D.main(sys.modules[__name__])
