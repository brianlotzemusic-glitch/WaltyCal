# UPLOAD: New Year's Countdown, original Logic Pro project (TpT 067)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `new-years-countdown.zip`. It holds three files in a folder "New Years Countdown - Hudson Beat":
  - `new-years-countdown.pdf`: the teacher and student resource, 23 pages, US Letter portrait.
  - `new-years-countdown-intro-deck.pptx`: the teacher-presented intro deck, 14 slides (16:9), speaker notes and a Class badge on every slide.
  - `new-years-countdown-intro-deck.pdf`: a PDF copy of the deck, 14 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `new-years-countdown-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

**Page count, adding up to the PDF:** 1 cover + 9 teacher + 12 student + 1 terms page = 23 pages; plus 14 slides = 37 for TpT's "Number of pages or slides".

## 1. Title

```
Logic Pro Build-Up and Drop | Risers, Snare Rolls, Countdown | High School
```
(74 characters; the limit is 80.) The title leaves out New Year, Winter and Holiday because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034); "Countdown" alone is a plain search word. "Logic Pro" sits in the first 30 characters.

## 2. Description

```
Build-up and drop project for high school music technology: students arrange a track of 40 to 48 bars in Logic Pro in five sections: an intro, a build-up with risers, a snare roll that speeds up from quarter notes to eighth, sixteenth and thirty-second notes, a filter sweep that opens a low-pass filter and a pitch-up, a 10-second countdown with the numbers 10 to 1 one second apart, the drop on the first beat after 1, and an outro. The theme is a New Year countdown, but it is a music-technology project that suits any class (students may count down to a launch, a game start or a finish line). This New Year’s Countdown project takes 3 class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; the steps are written for Logic Pro, while the ideas (sections, tempo math, automation) carry over to GarageBand.

WHAT'S INCLUDED (ZIP: 23-page PDF = 1 cover + 9 teacher + 12 student + 1 terms page, plus 14-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup, a 3-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented track at 120 BPM: 45 bars = 90 seconds, a countdown of 5 bars from bar 17, the drop at bar 22, the cue sheet, the snare ladder and the filter sweep) (9 pages)
• Student pages: a tempo table (seconds per beat and per bar, bars in 10 seconds at seven tempos, and the start of every section at 96, 120 and 144 BPM), a section map of ten elements by five sections, a snare-roll ladder with riser and automation checklists, a countdown cue sheet (the bar and beat of every number at three tempos plus a blank sheet), a mix checklist, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a feedback planner and a reflection page (12 pages)
• Teacher-presented intro deck, 14 slides with speaker notes on every slide: a think-and-share hook, what the project is, the section map, the timing math, the snare ladder, the filter sweep and pitch-up, building it in Logic, the countdown timeline, what to turn in and the rubric

THE THREE CLASS PERIODS
• Class 1: hook; the section map; the timing math and a tempo; plan the build
• Class 2: set up Logic with a marker at every section; build the intro and the build-up
• Class 3: place the countdown, land the drop, add the outro; mix, bounce, present and reflect

WHAT STUDENTS LEARN
• Tension: what a riser, a snare roll that speeds up, a filter sweep and a pitch-up each do, and why a countdown makes a drop feel bigger
• Timing math: seconds per bar in 4/4 = 240 ÷ BPM; bars in 10 seconds = BPM ÷ 24; tempo = 24 × bars gives a whole number of bars (96, 120 or 144 BPM = 4, 5 or 6 bars); at 120 BPM a snare roll has 500, 250, 125 and 62.5 milliseconds between hits
• Building in Logic Pro: markers for sections, risers in Alchemy or Retro Synth, Quick Sampler or Sample Alchemy, Drum Machine Designer, Channel EQ or filter automation, reverse effects and the Step Sequencer if your version has them; automation, mixing and bounce
• Mixing so the build-up grows, the countdown is clear and the drop is the biggest part, and explaining their choices in a reflection

GOOD TO KNOW
• There is no audio in this resource and no student work. No melody, song or lyrics are printed or notated; students make every sound themselves in Logic Pro, from instruments, their own voices or synth beeps
• Requires Logic Pro on a Mac. A MIDI keyboard and a microphone are optional; nobody has to read music. Where a control may differ between versions, the pages say "if your version has it"
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

**$8.00** (paid), multiple-license price $8.00. Inside the $7-9 holiday-kit range, for a kit with 23 pages + 14 slides, a tempo table, a section map, a snare-roll ladder, a countdown cue sheet, a mix checklist and a two-page worked example, listed in late December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 3-class pacing guide, the snare-roll ladder, the tempo table and the /25 rubric. "Number of pages or slides" is 37 (23 pages + 14 slides).

## 9. Sources and credits

- Art: the cover, previews and deck use the owner's pre-made art (`art/hero.png`: a laptop with a rising waveform, headphones, microphone, monitor, controller and a plain stopwatch dial with no numbers, and confetti), copied whole from `tpt/_art/next/new-years-countdown/`; the file is logged in `tpt/_art/USAGE.md`. Everything else, including every number on the cover and pages, is drawn or printed in code.
- Facts: none beyond arithmetic. Every timing number comes from the formulas printed in the product (seconds per bar = 240 ÷ BPM; bars in 10 seconds = BPM ÷ 24; hits-per-beat gaps = 60000 ÷ (BPM × hits)). The theme text says only that many communities count down the last seconds of the year together; it names no date, place, custom or recording.
- Music: nothing is notated or printed. No songs, artists or recordings are named. Students make every sound, including the countdown voice or beeps.
- Fonts: Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: build for late December; listing no sooner than the 2-8 week window allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, melody, song title or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Neutral and secular.** The theme is a count to a big moment; no religious content, no alcohol imagery, no brands, no real recordings. `gen.py --check` fails on alcohol, religious and holiday-specific words. The stopwatch on the art has a plain dial with no numbers; the numbers on the cover are printed text.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; seconds per bar in 4/4 = 240 / BPM; bars in 10 seconds = BPM / 24, a whole number only when tempo = 24 x bars. Not whole: 90 BPM = 3.7500 bars; 100 BPM = 4.1667 bars; 110 BPM = 4.5833 bars; 128 BPM = 5.3333 bars. Choices: 96 BPM: 2.500 s per bar, 4 countdown bars, 44 bars, 110.00 s, drop at bar 21 (50.00 s); 120 BPM: 2.000 s per bar, 5 countdown bars, 45 bars, 90.00 s, drop at bar 22 (42.00 s); 144 BPM: 1.667 s per bar, 6 countdown bars, 46 bars, 76.67 s, drop at bar 23 (36.67 s). Sections are 8 + 8 + countdown + 16 + 8 bars (44 to 46 bars); the intro, build-up and countdown start at bars 1, 9 and 17. Cue = second x BPM / 60 beats after bar 17 beat 1. At 120 BPM: number 10 at bar 17 beat 1, number 9 at bar 17 beat 3, number 8 at bar 18 beat 1, number 7 at bar 18 beat 3, number 6 at bar 19 beat 1, number 5 at bar 19 beat 3, number 4 at bar 20 beat 1, number 3 at bar 20 beat 3, number 2 at bar 21 beat 1, number 1 at bar 21 beat 3, drop at bar 22 beat 1. Snare ladder: 1/4: 1 per beat, 500 ms at 120 BPM; 1/8: 2 per beat, 250 ms at 120 BPM; 1/16: 4 per beat, 125 ms at 120 BPM; 1/32: 8 per beat, 62.5 ms at 120 BPM; 120 hits across bars 9 to 16. Rounding: seconds per beat and per bar to 3 decimals, bars in 10 seconds to 4, sections and totals to 2, half up.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061 and 063): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** The Marker global track with a plus (+) button and a Create Marker key command (hedged), Alchemy and Retro Synth patches, Quick Sampler and Sample Alchemy (Reverse, hedged), Drum Machine Designer, the Step Sequencer, Channel EQ high cut and Auto Filter ("if your version has it"), automation (A), Mixer (X), Command-B bounce. Nothing says a loop or preset of a given name exists.
- [ ] **Open questions for the owner:** (1) **Title.** No New Year, Winter or Holiday in the title because of TpT's seasonal-title notice (see 1). (2) **Price.** $8.00, inside the $7-9 range. (3) **Classes.** Three periods; the pacing page shows how to run it in two or four. (4) **Tempos.** Students choose 96, 120 or 144 BPM so 10 seconds is 4, 5 or 6 whole bars; say if you would also allow 72 or 168 BPM (3 or 7 bars, 43 or 47 bars in all).
