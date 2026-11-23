# UPLOAD: Holiday Mashup, original Logic Pro project (TpT 076)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `holiday-mashup.zip`. It holds three files in a folder "Holiday Mashup - Hudson Beat":
  - `holiday-mashup.pdf`: the teacher and student resource, 27 pages, US Letter portrait.
  - `holiday-mashup-intro-deck.pptx`: the teacher-presented intro deck, 15 slides (16:9), speaker notes and a Class badge on every slide (the three-classes slide carries "Classes 1-3").
  - `holiday-mashup-intro-deck.pdf`: a PDF copy of the deck, 15 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `holiday-mashup-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

**Page count, adding up to the PDF:** 1 cover + 9 teacher + 16 student + 1 terms page = 27 pages; plus 15 slides = 42 for TpT's "Number of pages or slides".

## 1. Title

```
Logic Pro Mashup Project | Match Tempo and Key, Smart Tempo, Flex | High School
```
(79 characters; the limit is 80.) The title leaves out Holiday, Winter, Christmas and the song names because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034); "Mashup Project" and "Match Tempo and Key" are the plain search phrases. "Logic Pro" is in the first 30 characters as a compatibility word.

## 2. Description

```
Mashup project for high school music technology: students make a DJ-style mashup of two public-domain carols in Logic Pro. They compare the tempos of “Jingle Bells” and “Deck the Halls” as a ratio, choose a target tempo and calculate each song’s percent speed change and the seconds per bar (240 ÷ BPM in 4/4). They find the shortest semitone shift between the two keys with the circle of fifths, enter both melodies from a note chart, check the match with Smart Tempo, Flex Time and Flex Pitch (if your version has them), and layer the melodies over one groove in a 44-bar arrangement. The theme is secular and fits any winter lesson. This Holiday Mashup project takes 3 class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; the steps are written for Logic Pro, while the ideas (tempo ratios, transposition, layering, arrangement) carry over to GarageBand.

WHAT'S INCLUDED (ZIP: 27-page PDF = 1 cover + 9 teacher + 16 student + 1 terms page, plus 15-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview with the two carols at a glance, setup, a 3-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented plan at 108 BPM in F major: a 44-bar track of 97.78 seconds, with every percent change, shift and section time) (9 pages)
• Student pages: a tempo page (formulas, ratios, three target tempos with percent changes and six more tempo pairs), a key page (the circle of fifths, semitones up and down for six key pairs and three target keys), note charts of both melodies as piano rolls and bar-by-bar tables in two keys each, a Smart Tempo and Flex page (audio lengths, pitch from speed, frequency ratios), a beat-by-beat clash check for every shift with suggested chords, groove cards (steady and half-time), an arrangement map of seven elements by six sections with a time table, a mix checklist, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a feedback planner and a reflection page (16 pages)
• Teacher-presented intro deck, 15 slides with speaker notes on every slide: a think-and-share hook, what the project is, the tempo ratio, seconds per bar, the circle of fifths, the clash check, Smart Tempo and Flex, building it in Logic, the arrangement map, what to turn in and the rubric

THE THREE CLASS PERIODS
• Class 1: hook; match the tempo and the key; start the first melody
• Class 2: finish both melodies, check with Smart Tempo and Flex, layer them over a groove
• Class 3: arrange the six sections, mix, bounce, present and reflect

WHAT STUDENTS LEARN
• Tempo math: the ratio of two tempos (half-time and double-time are 2 : 1), a target tempo, percent change = (target ÷ original − 1) × 100, and seconds per bar in 4/4 = 240 ÷ BPM; a 44-bar track at 108 BPM lasts 97.78 seconds
• Key math: the semitone distance between two keys, the shorter direction (never more than 6), new key names and relative minors
• Building in Logic Pro: the Piano Roll, Transpose, Alchemy or Retro Synth, Drum Machine Designer, markers, automation and bounce; Smart Tempo, Flex Time, Flex Pitch and Session Players if your version has them
• Layering two melodies, mixing so both stay clear, and explaining their choices in a reflection

GOOD TO KNOW
• There is no audio in this resource and no student work. Both melodies are public domain and appear only as note charts; no lyrics are printed. Students make every sound themselves in Logic Pro
• Requires Logic Pro on a Mac. A MIDI keyboard is optional; students need only read the note chart. Where a control may differ between versions, the pages say "if your version has it"
• Rubric: 5 categories scored 1-5, /25; the final grade is the average of the student's and the teacher's score
• Grades 9-12; music technology or music production classes
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present the PDF copy, which shows the intended look
• Every student page prints well in black and white

Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this
Follow the Hudson Beat store for new music resources every week

Created with the help of digital and AI tools. Notation and answer keys are verified before release.
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: Music; Computer Science - Technology; Music Composition (all three are in `tpt/SUBJECT-OPTIONS.json` and none is a heading)
- Tags in tpt.json: Winter, Christmas-Chanukah-Kwanzaa, Project-based Learning, Projects, Activities (five exact entries of `tpt/TAG-OPTIONS.json`, checked with `tools/tpt-validate.py`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used; "Winter" and "Christmas-Chanukah-Kwanzaa" are real entries.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**$9.00** (paid), multiple-license price $9.00. Inside the $8-12 holiday Logic kit range, for a kit with 27 pages + 15 slides, two note charts in two keys each, a tempo page, a key page, a Smart Tempo and Flex page, a beat-by-beat clash check, groove cards, an arrangement map and a two-page worked example, listed in late December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 3-class pacing guide, the tempo page, the key page and the /25 rubric. "Number of pages or slides" is 42 (27 pages + 15 slides).

## 9. Sources and credits

- **Melody sources (public domain).** Jingle Bells: James Lord Pierpont, published September 16, 1857 by Oliver Ditson & Co., Boston, as "The One Horse Open Sleigh" (English Wikipedia, "Jingle Bells", fetched 23 Nov 2026); the familiar chorus is a later form that the same article dates to a recording from 1898 at the latest. Deck the Halls: a Welsh melody, dated by the same kind of source to the sixteenth century (English Wikipedia, "Deck the Halls"); the English words are by Thomas Oliphant, 1862. Both are far older than the 1930 cutoff, so the melodies are in the public domain. The charts (Jingle Bells: 16 bars of 4/4, 96 notes, G major; Deck the Halls: 16 bars of 4/4, 68 notes, F major) were typed from MusicXML files fetched from the Choral Public Domain Library (CPDL) on 23 Nov 2026 and are compared in `gen.py --check` with the typed scores: **Jingle Bells** with CPDL no. 38153 (John Brown, SAB, 4/4, G major, soprano line) and CPDL no. 66808 (William Hale, adapted to the modern tune, 2/4, A-flat major, moved down 1 semitone); **Deck the Halls** with CPDL no. 47663 (Andrew Sims, F major), CPDL no. 502 (Rafael Ornes, F major, top note of each chord; its first bar is empty on the staff read) and CPDL no. 39398 (James Gibb's edition of Charles Wood's harmonization, E-flat major, soprano, moved up 2). Differences found and kept in the check: the 4/4 Jingle Bells edition adds a D5 lyric pickup at the end of the verse (leading into the chorus) and after the fourth bar of the chorus (the chart leaves both out and writes the two held notes before them as half notes); the 2/4 edition splits some held notes into a note and a rest or re-strikes them (F#4, B4 and E4 in the verse, G4 at the end) and adds a D4 pickup in the verse; every pitch on the beats agrees. All three Deck the Halls scores agree with the chart on every pitch, start and length (the Ornes file has no top-line notes in bar 1). The editions carry their editors' CPDL licenses (Hale: personal use); nothing from them is copied except the pitches and lengths of the public-domain tunes. Also opened for key, meter or tempo marks only: CPDL no. 66801 (the 1857 edition, A-flat major, 2/4, 130 BPM) and CPDL no. 20578 (a Jingle Bells edition in F major, 100 BPM).
- **Keys and tempos.** Notated keys in the files read: Jingle Bells A-flat major (two editions), G major, F major; Deck the Halls F major (two editions) and E-flat major. Tempo marks in the files: Jingle Bells 80, 100, 130 and 144 BPM; Deck the Halls 96, 120 and 160 BPM. The kit says plainly that these vary and uses "typical class tempo" values of 120 and 96 BPM, which lie inside those ranges. The 4/4 Jingle Bells chart equals two bars of the 2/4 edition for one bar of 4/4 with the same quarter-note beat.
- **Lyrics and words.** Not printed. Only the titles and the facts above are given.
- **Art:** the cover, previews and deck use the library's mixing-console line art (`art/hero.png`, copied whole from `tpt/_art/library/mixing-console.png`; logged in `tpt/_art/USAGE.md`). Everything else, including every note, number, table, chart and drawing, is drawn or printed in code.
- **Music:** only the two public-domain melodies are notated. No recordings, artists or other arrangements are named or included. Students make every sound.
- **Fonts:** Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: build for late December; listing no sooner than the 2-8 week window allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, song title other than the two tunes' own titles, or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Neutral and secular.** The carols are treated as public-domain tunes: no religious teaching, no alcohol imagery, no brands, no real recordings. `gen.py --check` fails on religious, alcohol and holiday-specific words and on fragments of the lyrics.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; seconds per bar = beats x 60 / BPM (4/4: 240 / BPM). The track is 4 + 8 + 4 + 8 + 16 + 4 = 44 bars (sections start at bars 1, 5, 13, 17, 25, 41). Printed: 96 BPM: 2.5 s per bar, 44 bars 110.00 s; 108 BPM: 2.222 s per bar, 44 bars 97.78 s; 120 BPM: 2 s per bar, 44 bars 88.00 s. Ratio 120 : 96 = 5 : 4; mean 108; percent changes −10% and +12.5%; audio length changes +11.11% and −11.11%; 8 bars last 16.00, 17.78 and 20.00 s at 120, 108 and 96 BPM.
- [ ] **Keys (recomputed in `gen.py --check`).** G down to F is −2 (up 10); the shorter move is never more than 6; the circle of fifths positions, key signatures and relative minors of all 12 keys; the shorter shift for all 144 key pairs; three target keys.
- [ ] **Clash check (recomputed in `gen.py --check` by two independent loops).** At the key-matched shift (−2) the 64 beats split 45 smooth, 14 mild and 5 hard; every other shift from −6 to +5 has more hard clashes; a target of G gives the same counts. It is a quick check, labeled as one on the page.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061, 063, 067 and 070): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged; the deck's three-classes badge and the terms-page thank-you note are applied inside `gen.py`.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Piano Roll (middle C is C3 in Logic and C4 on the chart), Transpose in the region inspector, Smart Tempo, Flex Time and Flex Pitch (all "if your version has it", with "look in the region or track inspector" and no invented menu paths), Bounce in Place (hedged), Alchemy and Retro Synth, Drum Machine Designer, Session Players (hedged), the Marker global track with a plus (+) button and a Create Marker key command (hedged), the Mixer (X), automation (A), Bounce (Command-B) and Compress in Finder.
- [ ] **Open questions for the owner:** (1) **Title.** No Holiday, Winter or song name in the title because of TpT's seasonal-title notice (see 1). (2) **Price.** $9.00, inside the $8-12 range. (3) **Classes.** Three periods; the pacing page shows two and four. (4) **Typical tempos.** 120 and 96 BPM are class choices inside the range of published tempo marks, stated as such. (5) **Editions.** The notes were compared with CPDL editions that carry their editors' own licenses; confirm you are comfortable with the sources line in section 9.
