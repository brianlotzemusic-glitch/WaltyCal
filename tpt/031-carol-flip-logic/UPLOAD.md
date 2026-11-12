# UPLOAD: Carol Flip, original Logic Pro holiday project (TpT 031)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `carol-flip.zip`. It holds three files in a folder "Carol Flip - Hudson Beat":
  - `carol-flip.pdf`: the teacher and student resource, 26 pages, US Letter portrait.
  - `carol-flip-intro-deck.pptx`: the teacher-presented intro deck, 15 slides (16:9), speaker notes and a Class badge on every slide.
  - `carol-flip-intro-deck.pdf`: a PDF copy of the deck, 15 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `carol-flip-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

## 1. Title

```
Holiday Remix in Logic Pro | Carol Flip Project | High School Music Tech
```
(72 characters; the limit is 80.)

## 2. Description

```
Holiday remix project for high school music technology: students choose a public-domain carol, enter its melody into Logic Pro from a piano-roll note chart, and remix it in any genre, from lo-fi and house to trap and reggae. This Carol Flip project takes 4 class periods and is an original Hudson Beat project; the steps are written for Logic Pro, while the ideas (tempo, drums, bass, chords and sounds make a genre) carry over to GarageBand, Ableton Live and BandLab.

WHAT'S INCLUDED (ZIP: 26-page PDF = 1 cover + 10 teacher + 14 student + 1 terms page, plus 15-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup, a 4-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference, tune sources and the public-domain rule, and a two-page worked example (an invented plan on paper: Jingle Bells flipped to C minor as house music, with its five flips, a 40-bar map, eight layers, chords and three automation lanes) (10 pages)
• Student pages: three piano-roll note charts (Jingle Bells chorus, Deck the Halls phrase, Silent Night in 6/8) with every note listed bar by bar, five genre cards with drum grids plus a blank card, a Flip plan, an Arrangement plan with a length helper, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a feedback planner and a reflection page (14 pages)
• Teacher-presented intro deck, 15 slides with speaker notes on every slide: a think-and-share hook, what Carol Flip is, how to read a piano roll, entering the melody, a major-to-minor flip, genre in the drums, a worked-example map, mixing, what to turn in and the rubric

THE FOUR CLASS PERIODS
• Class 1: hook; choose a carol and a genre; fill in the Flip plan; start entering the melody
• Class 2: enter and check the melody; build the drums and bass of the genre
• Class 3: add chords and sounds; plan the form; build the arrangement and mix
• Class 4: bounce and hand in; presentations with feedback questions; reflection

WHAT STUDENTS LEARN
• Entering and editing notes in Logic Pro's Piano Roll from a note chart
• What makes a genre: tempo, drums, bass, chords and sounds, not only speed
• Keeping a melody recognizable while everything around it changes
• Planning a 60 to 90 second arrangement with an intro, melody sections and an outro
• Balancing a mix and explaining their choices in a reflection

GOOD TO KNOW
• There is no audio in this resource and no student work. The three melodies are in the public domain and appear only as note charts, with no lyrics; students make every sound themselves in Logic Pro
• Jingle Bells and Deck the Halls are winter songs; Silent Night is a Christmas carol. Offer the ones that suit your school
• Requires Logic Pro on a Mac. A MIDI keyboard is not needed; nobody has to read staff notation
• Rubric: 5 categories scored 1-5, /25; the final grade is the average of the student's and the teacher's score
• Grades 9-12; music technology or music production classes
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present the PDF copy, which shows the intended look
• Every student page prints well in black and white

Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Created with the help of digital and AI tools. Notation and answer keys are verified before release.
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

**$9.00** (paid), multiple-license price $9.00. Top of the first-kit range in the queue ($9) for a kit this size (26 pages + 15 slides, three note charts, five genre cards, a two-page worked example) and a hook buyers search for in November and December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 4-class pacing guide, the Jingle Bells note chart, the first genre cards page and the /25 rubric. "Number of pages or slides" is 41 (26 pages + 15 slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Tunes are public domain (year and source for QA.md).** Jingle Bells, the chorus: James Lord Pierpont, first published in Boston in 1857 as "One Horse Open Sleigh". Deck the Halls, the first phrase: traditional Welsh melody "Nos Galan", centuries old and in print long before 1930; the 1862 English words are not used. Silent Night: Franz Xaver Gruber, composed 1818; melody only, no words. All three are shown as note charts transcribed for this kit (pitches checked against public-domain transcriptions, then moved to C major); no published edition is reproduced.
- [ ] **Original project.** This is the first kit built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py`: no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row.
- [ ] **Open question for the owner:** (1) **Carols and schools.** Silent Night is a Christmas carol; the kit offers it next to two winter songs and tells teachers to choose what suits their school. Say if you want a secular-only version of the charts or a fourth winter melody. (2) **Tags and the season.** Only "Winter" is a proven tag; the candidate extras above need a dry run on the Mac. (3) **Price.** $9 is the top of the holiday-kit range; say if you would rather list it at $8 for launch.
