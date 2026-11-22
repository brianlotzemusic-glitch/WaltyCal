# UPLOAD: Auld Lang Syne Reharmonized, original Logic Pro project (TpT 070)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `auld-lang-syne-reharmonized.zip`. It holds three files in a folder "Auld Lang Syne Reharmonized - Hudson Beat":
  - `auld-lang-syne-reharmonized.pdf`: the teacher and student resource, 26 pages, US Letter portrait.
  - `auld-lang-syne-reharmonized-intro-deck.pptx`: the teacher-presented intro deck, 14 slides (16:9), speaker notes and a Class badge on every slide.
  - `auld-lang-syne-reharmonized-intro-deck.pdf`: a PDF copy of the deck, 14 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `auld-lang-syne-reharmonized-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

**Page count, adding up to the PDF:** 1 cover + 9 teacher + 15 student + 1 terms page = 26 pages; plus 14 slides = 40 for TpT's "Number of pages or slides".

## 1. Title

```
Logic Pro Reharmonize a Melody | Pop, Ballad, EDM Chords | High School
```
(70 characters; the limit is 80.) The title leaves out New Year, Winter, Holiday and the song's name because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034); "Reharmonize a Melody" is the plain search phrase. "Logic Pro" sits in the first 30 characters.

## 2. Description

```
Reharmonizing project for high school music technology: students re-harmonize a public-domain melody in Logic Pro. They enter the traditional Scottish tune of “Auld Lang Syne” from a note chart (16 bars in 4/4 with a pickup, in C major or G major), then put new chords under it in a pop, ballad or EDM style: a pop loop (I–V–vi–IV), a slower ballad with added 7ths and suspended chords, or an EDM track with four on the floor and a sidechain pump. Every chord must hold the melody note on its downbeat, and students name each chord by Roman numeral and letter. The tune is a song of remembrance and friendship, so the theme is secular and fits any class. This Auld Lang Syne Reharmonized project takes 3 class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; the steps are written for Logic Pro, while the ideas (chord tones, Roman numerals, grooves, arrangement) carry over to GarageBand.

WHAT'S INCLUDED (ZIP: 26-page PDF = 1 cover + 9 teacher + 15 student + 1 terms page, plus 14-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup, a 3-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented ballad in G major at 72 BPM: 40 bars = 133.33 seconds, every chord with its numeral and the check that each downbeat is a chord tone, the section times and the mix) (9 pages)
• Student pages: a tempo table (seconds per beat and per bar, one pass and the 40-bar track at eight tempos, and the start of every section at 72, 100 and 128 BPM), a two-page note chart of the melody in C major and G major (piano roll and bar-by-bar table), pop, ballad and EDM chord tables for all 16 bars in both keys with Roman numerals, chord tones and passing notes, a chord key of 13 chords, groove cards for the three styles with the sidechain explained, an arrangement map of eight elements by four sections, a mix checklist, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a feedback planner and a reflection page (15 pages)
• Teacher-presented intro deck, 14 slides with speaker notes on every slide: a think-and-share hook, what the project is, the melody in a piano roll, how a chord fits a melody note, three styles, four on the floor and the sidechain pump, building it in Logic, the arrangement map, what to turn in and the rubric

THE THREE CLASS PERIODS
• Class 1: hook; the tempo table, the melody and the chord tables; enter the first eight bars
• Class 2: finish the melody, enter and check the chords, build the groove
• Class 3: arrange the four sections, mix, bounce, present and reflect

WHAT STUDENTS LEARN
• Harmony: a chord fits a melody when it holds the downbeat note (a chord tone); Roman numerals and letter names in two keys; what pop, ballad and EDM chords have in common and where they differ
• Timing math: seconds per bar in 4/4 = 240 ÷ BPM; a 40-bar track at 72 BPM lasts 133.33 seconds, at 100 BPM 96 seconds and at 128 BPM 75 seconds
• Building in Logic Pro: the Piano Roll, Alchemy or Retro Synth, Drum Machine Designer, a Compressor side chain, markers, automation and bounce; the Chord Track, Session Players, the Step Sequencer and Smart Tempo if your version has them
• Mixing so the melody stays clear and the second pass is bigger, and explaining their choices in a reflection

GOOD TO KNOW
• There is no audio in this resource and no student work. The melody is public domain and appears only as a note chart; the poem’s words are not printed. Students make every sound themselves in Logic Pro
• Requires Logic Pro on a Mac. A MIDI keyboard is optional; students need only read the note chart. Where a control may differ between versions, the pages say "if your version has it"
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

- Subjects in tpt.json: Music; Computer Science - Technology; Music Composition (all three are in `tpt/SUBJECT-OPTIONS.json` and none is a heading)
- Tags in tpt.json: New Year, Project-based Learning, Projects, Activities (four exact entries of `tpt/TAG-OPTIONS.json`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used; "New Year" is a real entry under the Holiday heading.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**$8.00** (paid), multiple-license price $8.00. Inside the $7-9 holiday-kit range, for a kit with 26 pages + 14 slides, a note chart in two keys, three chord tables, groove cards, an arrangement map, a tempo table and a two-page worked example, listed in late December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 3-class pacing guide, the first note chart page, the pop and ballad chord tables and the /25 rubric. "Number of pages or slides" is 40 (26 pages + 14 slides).

## 9. Sources and credits

- **Melody sources (public domain).** The tune is a traditional Scottish melody; Robert Burns wrote the poem in 1788 and the standard tune's first documented use with the words is from 1799 (George Thomson's *Select Songs of Scotland*), both far before the 1930 cutoff, so the melody is in the public domain worldwide. The chart (16 bars in 4/4 plus a one-beat pickup, 56 notes, five pitches) was typed in C major and in G major and checked in `gen.py --check` against two sources fetched on 22 Nov 2026: (1) the LilyPond transcription in F major engraved on the English Wikipedia article "Auld Lang Syne" (note for note and length for length, after moving it down 5 semitones; the melody only, no words are used); (2) Brigid Baker's public-domain edition on the Choral Public Domain Library (CPDL no. 21485, MusicXML), compared on the pitch at the start of every beat of all 16 bars (the same on all 64 beats; it splits two beat-4 quarter notes into two eighths). The G major chart is the C major chart moved up 7 semitones, checked note by note. Also read and compared, but not used as the chart: Philip Rice's CPDL edition (no. 37897, public domain), which differs in one place (the last pickup note of the third phrase, tune bar 12, is F5 in F major instead of D5), and two 19th-century arrangements, Felix Horetzky's for guitar (Mutopia Project, public domain) and Beethoven's WoO 156 (CPDL, from the 1814 *Scottish Folksongs*). Published editions vary some pickup notes and rhythms (Horetzky's guitar setting is in 2/4 and in D major, for example), which the plain 4/4 chart does not follow. This is stated on the chart page.
- **Poem and facts.** The poem's words are not printed. The kit gives only the facts: written by Robert Burns in 1788 (from older Scottish song), the title is Scots for "old long since" (often "days gone by"), the chorus line is often rendered "for the sake of old times", and the tune is traditional and pentatonic (English Wikipedia and Britannica agree; the Library of Congress blog on the song says the tune derives from a traditional Scottish folk-dance tune).
- **Art:** the cover, previews and deck use the owner's pre-made art (`art/hero.png`: a laptop with a waveform, headphones, a small keyboard controller and sparkles), copied whole from `tpt/_art/next/auld-lang-syne-reharmonized/`; the file is logged in `tpt/_art/USAGE.md`. Everything else, including every note, chord and number, is drawn or printed in code.
- **Music:** only the public-domain melody is notated. No songs, artists, recordings or other arrangements are named or included. Students make every sound.
- **Fonts:** Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: build for late December; listing no sooner than the 2-8 week window allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, song title other than the tune's own title, or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Neutral and secular.** The theme is remembrance and friendship; no religious content, no alcohol imagery (the song's drinking lines are not quoted), no brands, no real recordings. `gen.py --check` fails on alcohol, religious and holiday-specific words and on fragments of the poem.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; seconds per bar in 4/4 = 240 / BPM. The track is 4 + 16 + 16 + 4 = 40 bars (sections start at bars 1, 5, 21, 37). Printed: 72 BPM (Ballad): 3.333 s per bar, one pass 53.33 s, 40 bars 133.33 s, Pass 2 starts at 66.67 s; 100 BPM (Pop): 2.400 s per bar, one pass 38.40 s, 40 bars 96.00 s, Pass 2 starts at 48.00 s; 128 BPM (EDM): 1.875 s per bar, one pass 30.00 s, 40 bars 75.00 s, Pass 2 starts at 37.50 s. Rounding: seconds per beat and per bar to 3 decimals, passes, starts and totals to 2, half up.
- [ ] **Chords (recomputed in `gen.py --check` from pitch classes, in C major and in G major).** Every one of the 48 downbeat notes (16 bars in three styles) is a chord tone in both keys; each chord is also rebuilt by stacking thirds on the key's scale. Roman numerals and letter names: Am = vi (Em in G), Am7 = vi7 (Em7 in G), C = I (G in G), Cadd9 = Iadd9 (Gadd9 in G), Cmaj7 = Imaj7 (Gmaj7 in G), Dm7 = ii7 (Am7 in G), Em = iii (Bm in G), Em7 = iii7 (Bm7 in G), F = IV (C in G), Fmaj7 = IVmaj7 (Cmaj7 in G), G = V (D in G), G7sus4 = V7sus4 (D7sus4 in G), Gsus4 = Vsus4 (Dsus4 in G).
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061, 063 and 067): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Piano Roll (middle C is C3 in Logic and C4 on the chart), Alchemy and Retro Synth, Drum Machine Designer, Compressor with a Side Chain source menu (hedged), Chord Track, Session Players, Step Sequencer and Smart Tempo ("if your version has it"), the Marker global track with a plus (+) button and a Create Marker key command (hedged), automation (A), Mixer (X), Command-B bounce. No menu path beyond File › New and File › Bounce is given.
- [ ] **Open questions for the owner:** (1) **Title.** No New Year, Winter, Holiday or song name in the title because of TpT's seasonal-title notice (see 1). (2) **Price.** $8.00, inside the $7-9 range. (3) **Classes.** Three periods; the pacing page shows how to run it in two or four. (4) **Melody variants.** Published settings differ in a few pickup notes (see 9); the chart follows the plain 4/4 version that two sources agree on. (5) **Release date.** Late December per the queue; the song is New Year's Eve music but the kit is secular and year-round.
