# UPLOAD: Holiday Radio Ident, original Logic Pro project (TpT 080)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `holiday-radio-ident.zip`. It holds three files in a folder "Holiday Radio Ident - Hudson Beat":
  - `holiday-radio-ident.pdf`: the teacher and student resource, 27 pages, US Letter portrait.
  - `holiday-radio-ident-intro-deck.pptx`: the teacher-presented intro deck, 16 slides (16:9), speaker notes and a Class badge on every slide (the three-classes slide carries "Classes 1-3").
  - `holiday-radio-ident-intro-deck.pdf`: a PDF copy of the deck, 16 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `holiday-radio-ident-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

**Page count, adding up to the PDF:** 1 cover + 9 teacher + 16 student + 1 terms page = 27 pages; plus 16 slides = 43 for TpT's "Number of pages or slides".

## 1. Title

```
Logic Pro Radio Ident Project | Voice, Music Bed, Ducking, EQ | High School
```
(75 characters; the limit is 80.) The title leaves out Holiday, Winter and Christmas because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034); "Radio Ident Project" and "Voice, Music Bed, Ducking, EQ" are the plain search phrases. "Logic Pro" is in the first 30 characters as a compatibility word.

## 2. Description

```
Radio ident project for high school music technology: students make a 20-second radio station ident (a short sound logo and spot) for an invented winter station in Logic Pro, with a voice, an original music bed and sound effects. They plan the length with timing math (one bar of 4/4 = 240 ÷ BPM seconds, so tempo = 12 × bars: 96, 120 and 144 BPM give 8, 10 and 12 bars), write a script that fits its time (about 150 words per minute, which is 2.5 words per second, so a 12-second read is about 30 words), record the voice with good microphone technique and levels, clean it up with a high-pass filter and a gentle compressor, and duck the music under the voice with sidechain compression or with automation. The theme is a winter-season station and the project suits any class. This Holiday Radio Ident project takes 3 class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; the steps are written for Logic Pro, while the ideas (gain staging, EQ, compression, ducking) carry over to GarageBand.

WHAT'S INCLUDED (ZIP: 27-page PDF = 1 cover + 9 teacher + 16 student + 1 terms page, plus 16-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup, a 3-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented ident at 120 BPM: 10 bars = 20 seconds, a 24-word script, the voice from 4 to 16 seconds, the duck, the levels and the processing) (9 pages)
• Student pages: a tempo table (seconds per beat and per bar, bars in 20 seconds at seven tempos, and the bars in 15, 20 and 30 seconds), three original scripts for invented stations with word counts and read times, a signal-chain diagram (microphone, interface, track, EQ, compressor, mix bus) with a recording checklist, a dB ladder (levels in dBFS, amplitudes and the −6 dB rule), a music bed and effects plan, an EQ and compression page with starting points and the gain-reduction arithmetic, a ducking page with both methods and a depth table, a cue sheet (the bar and beat of every cue at three tempos plus a blank sheet), a mix checklist, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a feedback planner and a reflection page (16 pages)
• Teacher-presented intro deck, 16 slides with speaker notes on every slide: a think-and-share hook, what the project is, the 20-second timeline, the timing math, the signal chain, the dB ladder, building it in Logic, EQ, compression, ducking, what to turn in and the rubric

THE THREE CLASS PERIODS
• Class 1: hook; the timing math and a tempo; the script; microphone technique, levels and the first recording
• Class 2: build the music bed and sound effects; EQ and compression for the voice
• Class 3: duck the music, mix, bounce, present and reflect

WHAT STUDENTS LEARN
• Timing math: seconds per bar in 4/4 = 240 ÷ BPM; bars in 20 seconds = BPM ÷ 12; tempo = 12 × bars gives a whole number of bars; the same for 15 and 30 seconds; words = seconds × 2.5
• Recording: microphone distance, a pop filter, gain at the interface, and levels that peak around −12 to −6 dBFS; −6 dB is about half the amplitude (20 × log10(0.5) = −6.02)
• Processing: a high-pass filter near 80 Hz, small moves, a compressor at about 3:1 or 4:1 with about 3 to 6 dB of gain reduction on the loudest words, and ducking the music by about 6 to 12 dB with a half-second ramp
• Building in Logic Pro: the Loop Browser, Session Players and a simple Piano Roll pattern if your version has them, Channel EQ, Compressor and its Side Chain menu, volume automation, the Mixer and bounce

GOOD TO KNOW
• There is no audio in this resource and no student work. No melody, song, jingle or lyrics are printed; the three station names are invented. Students make every sound themselves in Logic Pro, from Logic's own loops, instruments and effects and their own voices
• Requires Logic Pro on a Mac. A microphone and a pop filter are recommended, and the voice can be a classmate's read; nobody has to read music. Where a control may differ between versions, the pages say "if your version has it"
• All audio numbers are starting points to set by ear, not rules
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
- Tags in tpt.json: Winter, Project-based Learning, Projects, Activities (four exact entries of `tpt/TAG-OPTIONS.json`, checked with `tools/tpt-validate.py`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used; "Winter" is a real entry.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**$8.00** (paid), multiple-license price $8.00. The price the queue set, at the low end of the $8-12 holiday Logic kit range, for a kit with 27 pages + 16 slides, a tempo table, three scripts, a signal chain, a dB ladder, an EQ and compression page, a ducking page, a cue sheet and a two-page worked example, listed in late December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 3-class pacing guide, the signal chain and recording page, the ducking page and the /25 rubric. "Number of pages or slides" is 43 (27 pages + 16 slides).

## 9. Sources and credits

Every audio number in the product is a starting point, and the product says so. What each one rests on (all fetched on 24 Nov 2026):

- **About 150 words per minute (2.5 words per second).** English Wikipedia, "Words per minute": 150-160 words per minute is the recommended range for audiobooks; 100-125 for slide presentations. The kit uses 150, the low end of the audiobook range, as a relaxed radio read; the page gives no figure for radio itself, so the kit does not claim one. Words = seconds × 150 ÷ 60 is arithmetic.
- **Decibels and dBFS.** English Wikipedia, "Decibel": amplitude ratios use 20 log10; a halving is about −6 dB (table value 0.501 ≈ 1/2). English Wikipedia, "DBFS": 0 dBFS is the maximum digital level, so a signal at 50% of maximum sits at about −6 dBFS, and digital audio clips there. 20 log10(0.5) = −6.02 is computed in `gen.py --check`, with every amplitude on the dB ladder (10^(dB/20)).
- **Voice peaks around −12 to −6 dBFS.** A common beginner target, not a standard. MusicRadar, "Back to basics: the beginner's guide to headroom and levels": peaks no higher than −6 dBFS, average around −18 dBFS. Sound on Sound, "Gain staging in Logic Pro": −18 dBFS peaks as a working reference, −12 dBFS as an analog-style reference line, no headroom above 0 dBFS, final mix peaks several dB below 0. Sound on Sound, "How should I set my compressor when recording vocals?": at 24-bit, leave 10-15 dB of headroom and compress at the mix. An Adorama guide to audio levels (page read) calls the −12 to −6 dB meter zone the "sweet spot" and "ideal for dialogue" (it does not say peaks). The exact phrase "−12 and −6 dBFS" for a vocal peak was found in a search summary of an ask.audio article, whose page was not read; the kit therefore calls the range a starting point and says a quieter recording is safe.
- **Microphone distance 10 to 20 cm, pop filter, steady distance, proximity effect.** Shure's "vocal miking tips" page (read in full): the proximity effect is the boomy, bass-heavy sound of a source very close to the microphone; studio vocals are typically captured from 6 to 12 inches (about 15 to 30 cm); distances run from an inch to arm's length depending on the performance. That page does not mention pop filters and gives no 10 to 20 cm figure. So **10 to 20 cm (about 4 to 8 inches; 10 ÷ 2.54 = 3.94, 20 ÷ 2.54 = 7.87) is this kit's choice for a classroom speaking voice, not a Shure figure**, and a pop filter and a steady distance are ordinary recording practice, not sourced here. The pages tell students to try two distances and listen.
- **High-pass filter near 80 Hz.** Sage Audio, "Mastering Voice-Over Dialogue for Video": a high-pass filter covering 0-80 Hz removes plosives and microphone rumble. The kit says "near 80 Hz" and "raise it a little only if the voice still sounds full" (the second half is general practice, not sourced).
- **Compression: ratio about 3:1 or 4:1, about 3 to 6 dB of gain reduction.** Sound on Sound (vocal compressor Q&A, seen as a search summary): ratios from roughly 2:1 to 5:1. Sage Audio (page read): compressors typically use ratios such as 2:1 or 4:1, and it is generally wise not to add more than about 6 dB of compression. A voice-over mixing blog (search summary) suggests trying 2:1 or 3:1. No page read says "3 to 6 dB"; the **3:1 or 4:1 picks and the "about 3 to 6 dB" window are the teacher's choice, inside those ranges and under Sage Audio's 6 dB ceiling**. Gain reduction = dB over threshold × (1 − 1 ÷ ratio) is the standard hard-knee formula, computed in `gen.py --check`; real compressors soften the knee, which the page says.
- **Ducking by about 6 to 12 dB with a half-second ramp.** Audacity manual, "Auto Duck": the defaults are a duck amount of −12 dB and outer fade lengths of 0.5 seconds. 12 dB is therefore a documented default; 6 dB as the lower end is this kit's choice (it halves the amplitude) and is not a published standard. A search for typical depths found no single standard, so the kit calls 6 to 12 dB a starting point to adjust by ear. Sidechain compression and the Side Chain menu: Apple's Logic Pro documentation (Compressor side chain parameters) and a Sound on Sound Logic Pro article (the side chain menu chooses any track as the source). The menu location is hedged with "if your version has it" and no menu path is invented.
- **Example values (not from any source).** The worked example's levels (voice −9, bed −12, shaker −18, wind −24, chime −15 dBFS), the −8 dB duck, the −17 dB compressor threshold, the +2 dB presence boost near 3 kHz, the −3 dBFS mix ceiling and all invented cue times are example values chosen for this kit and labeled as examples.
- **Station names.** Snowline Radio, Northlight Radio and Hollow Pine Radio are invented. None is a call-letter name. Searches on 24 Nov 2026 found no station by these names, but a search is not a trademark clearance (see the open questions).
- **Art:** the cover, previews and deck use the owner's pre-made art (`art/hero.png`: a microphone with headphones and a small radio with a blank dial), copied whole from `tpt/_art/next/holiday-radio-ident/`; logged in `tpt/_art/USAGE.md`. Everything else, including every number, table, curve and drawing, is drawn or printed in code.
- **Music:** nothing is notated or printed. No songs, jingles, artists or recordings are named. Students make every sound.
- **Fonts:** Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: build for late December; listing no sooner than the 2-8 week window allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, melody, song title or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Neutral and secular.** The theme is a winter-season radio station; no religious content, no alcohol imagery, no brands, no real stations, no existing jingles. `gen.py --check` fails on alcohol, religious and holiday-specific words and on call-letter names in the scripts.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; seconds per bar in 4/4 = 240 / BPM; bars in 20 seconds = BPM / 12, a whole number only when tempo = 12 x bars (15 seconds: 16 x bars; 30 seconds: 8 x bars). Not whole: 90 BPM = 7.5000 bars; 100 BPM = 8.3333 bars; 110 BPM = 9.1667 bars; 128 BPM = 10.6667 bars. Choices: 96 BPM: 2.500 s per bar, 8 bars = 20 s; 120 BPM: 2.000 s per bar, 10 bars = 20 s; 144 BPM: 1.667 s per bar, 12 bars = 20 s. Cues at 120 BPM: music bed starts at full level at 0 s = bar 1 beat 1, duck starts at 3.5 s = bar 2 beat 4, voice comes in at 4 s = bar 3 beat 1, voice ends at 16 s = bar 9 beat 1, music is back at full level at 16.5 s = bar 9 beat 2, chime and final hit at 18 s = bar 10 beat 1, end of the ident, after the tail rings out at 20 s = bar 11 beat 1. Scripts: 24, 25 and 28 words = 9.6, 10 and 11.2 seconds at 2.5 words per second, all inside the 12-second window. Rounding: seconds per beat and per bar to 3 decimals, bars to 4 (2 in the length table), half up.
- [ ] **Level numbers (recomputed).** Amplitude = 10^(dB/20): 1.000, 0.708, 0.501, 0.355, 0.251, 0.126, 0.100 at 0, −3, −6, −9, −12, −18, −20 dBFS; halving = −6.02, −12.04, −18.06 dB; the example's worst-case combined peaks −7.1, −6.8 and −7.4 dBFS, all below its −3 dBFS ceiling; compression table (2:1, 3:1, 4:1 at 3, 6, 9, 12 dB over); the 4:1 example: 8 dB over, 6 dB of reduction, −9 in gives −15 out.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061, 063, 067, 070 and 076): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged; the deck's three-classes badge and the terms-page thank-you note are applied inside `gen.py`.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** The Loop Browser (the loop icon in the toolbar), Session Players such as the Drummer (hedged), Alchemy and Retro Synth, the Piano Roll, Channel EQ's lowest band as a high-pass or low-cut filter (hedged), Compressor with its gain reduction meter and make-up gain (hedged) and Side Chain menu (hedged), record-enable (R), automation (A), the Mixer (X), Bounce (Command-B) and Compress in Finder. Nothing says a loop or preset of a given name exists; the shaker, wind and chime sounds are "if your version has one".
- [ ] **Open questions for the owner:** (1) **Title.** No Holiday, Winter or Christmas in the title because of TpT's seasonal-title notice (see 1). (2) **Price.** $8.00, as queued, the low end of the $8-12 range. (3) **Ranges.** −12 to −6 dBFS for voice peaks and 6 to 12 dB for the duck are starting points drawn from the sources above; 6 dB for the duck is the kit's own lower end, and the −12 to −6 range rests on a source that was only read as a search summary. Say if you want them rephrased. (4) **Loops.** The kit tells students to use only the loops and sounds that come with Logic. Apple's support page "Use the royalty-free content included with Logic Pro for Mac and MainStage in commercial works" says the sample content may be used royalty-free to create original soundtracks, and that individual assets may not be distributed standalone; the kit promises nothing beyond that, and does not say your school's license covers anything in particular. (5) **Station names.** Confirm you are comfortable with the three invented names. (6) **Classes.** Three periods; the pacing page shows two and four.
