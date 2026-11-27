# UPLOAD: House Remix, original Logic Pro project (TpT 092)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `house-remix-sidechain.zip`. It holds three files in a folder "House Remix - Hudson Beat":
  - `house-remix-sidechain.pdf`: the teacher and student resource, 26 pages, US Letter portrait.
  - `house-remix-sidechain-intro-deck.pptx`: the teacher-presented intro deck, 20 slides (16:9), speaker notes and a Class badge on every slide (the three-classes slide carries "Classes 1-3").
  - `house-remix-sidechain-intro-deck.pdf`: a PDF copy of the deck, 20 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `house-remix-sidechain-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, melody notation, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

**Page count, adding up to the PDF:** 1 cover + 9 teacher + 15 student + 1 terms page = 26 pages; plus 20 slides = 46 for TpT's "Number of pages or slides".

## 1. Title

```
Logic Pro House Remix | 128 BPM, Sidechain, Four on the Floor | High School
```
(75 characters; the limit is 80.) The title leaves out Winter, Holiday, Christmas, Carol and the song's name because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 080, 083, 087 and 090 for the working format); "House Remix", "Sidechain" and "Four on the Floor" are the plain search phrases. "Logic Pro" is in the first 30 characters as a compatibility word.

## 2. Description

```
House remix project for high school music technology: students remix one traditional winter song (the Welsh tune Deck the Halls, public domain) as a 128 BPM four-on-the-floor house track in Logic Pro. They work out the timing with simple arithmetic, build a 4-bar pattern on a 16-step grid (kick on every beat, open hat and bass on the off-beat, clap on beats 2 and 4; use the Step Sequencer or Drum Machine Designer, if your version has them), add a four-chord loop and the tune, set up sidechain compression so the bass, pad and tune duck when the kick hits, and arrange a 64-bar track with an intro, a build, a drop, a break, a second drop and an outro. Math runs through every step: one beat at 128 BPM = 60 ÷ 128 = 0.46875 seconds = 468.75 ms, one 16th-note step = 15 ÷ 128 = 117.19 ms (0.1171875 s), one bar of 4/4 = 240 ÷ 128 = 1.875 seconds, 16 bars = 30 seconds and 64 bars = 120 seconds; the release of the sidechain is timed to the beat, and the song's tempo change to 128 BPM is worked out as a ratio and a percent. The gain-reduction curve and the ducking graph are drawn from stated example settings (a ratio of 4:1 and a threshold of -20 dB) and labeled as examples, not Logic defaults. This House Remix takes 3 class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; the steps are written for Logic Pro, while the ideas (four on the floor, sidechain compression, chord loops, build and drop) carry over to GarageBand and other music software.

WHAT'S INCLUDED (ZIP: 26-page PDF = 1 cover + 9 teacher + 15 student + 1 terms page, plus 20-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup, a 3-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented remix at 128 BPM: 6 layers and their jobs, a 4-bar pattern of 90 hits, a chord loop, the sidechain numbers, timing at three tempos and a 64-bar arrangement of 6 layers = 120 seconds) (9 pages)
• Student pages: a timing page (milliseconds per beat and per step and seconds per bar at six tempos, 16-bar and 64-bar lengths, and a length table at three tempos), a song page (facts, a tempo-change table, a key and meter note and a checklist for entering the tune), a 4-bar step grid with the hits per bar and a blank grid, a chord page (I, IV, V and vi in three keys, the bass on the off-beats and a tune-against-chord check), a sidechain page (a gain-reduction curve, a ducking graph at 128 BPM and release times), a layer table with a signal-chain drawing, an arrangement map with a blank table, a mix checklist, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page (four on the floor, sidechain, kick, off-beat, build, drop, breakdown, release), a feedback planner and a reflection page (15 pages)
• Teacher-presented intro deck, 20 slides with speaker notes on every slide: a think-and-share hook, what the project is, four on the floor, the timing math, the step grid, the song, bass and chords, the sidechain in three slides, who ducks, the arrangement, the mix, what to turn in and the rubric

THE THREE CLASS PERIODS
• Class 1: hook; four on the floor; the timing math and a tempo of 128 BPM; prepare the song; build the 4-bar step grid
• Class 2: add the chord loop, the bass and the tune; set up the sidechain and time the release
• Class 3: arrange 64 bars, mix, bounce, present and reflect

WHAT STUDENTS LEARN
• Timing math: seconds per bar in 4/4 = 240 ÷ BPM; seconds per step = 15 ÷ BPM; 64 bars = 15360 ÷ BPM seconds; the ratio and percent change between two tempos
• Beats: a 16-step grid, hits per bar, the kick on every beat, the off-beat, claps on 2 and 4
• Harmony and bass: a I-IV-V-vi loop built by stacking thirds, bass roots between the kicks, checking the tune against the chords
• Mixing: sidechain compression (ratio, threshold, attack, release), headroom, and a build, a drop and a break

GOOD TO KNOW
• There is no audio in this resource, no lyrics, no melody notation and no student work. Students enter the public-domain tune from a score of their choice or by ear and make every other sound themselves
• Requires Logic Pro on a Mac; nobody has to read notation. Where a control may differ between versions, the pages say "if your version has it" and describe controls generically
• Rubric: 5 categories scored 1-5, /25; the final grade is the average of the student's and the teacher's score
• Grades 9-12; music technology or music production classes
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present the PDF copy, which shows the intended look
• Every student page prints well in black and white

Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Part of the Hudson Beat Logic Pro project series
Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this
Follow the Hudson Beat store for new music resources every week

Created with the help of digital and AI tools. Notation and answer keys are verified before release.
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: Music; Music Composition; Computer Science - Technology (all are in `tpt/SUBJECT-OPTIONS.json` and none is a heading)
- Tags in tpt.json: Winter, Project-based Learning, Projects, Activities (four exact entries of `tpt/TAG-OPTIONS.json`, checked with `tools/tpt-validate.py`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used; "Winter" is a real entry. "Christmas-Chanukah-Kwanzaa" is also a real entry but is left out because the kit is secular.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**$8.00** (paid), multiple-license price $8.00. The price the queue set, at the low end of the $8-12 holiday Logic kit range, for a kit with 26 pages + 20 slides, a timing page, a song page, a 4-bar step grid with a blank grid, a chord page, two sidechain pages, a 64-bar arrangement map, a mix checklist and a two-page worked example, listed for winter.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 3-class pacing guide, the step grid, the sidechain page and the arrangement map. "Number of pages or slides" is 46 (26 pages + 20 slides).

## 9. Sources and credits

Fetched on 27 Nov 2026 (English Wikipedia, through its raw-text interface) unless a line says "could not". Each fact below says which source it came from; anything marked "not from any source" is an example value or a choice made for this kit.

- **Four on the floor.** English Wikipedia, "Four-on-the-floor (music)": "a steady, uniformly accented beat in 4/4 time in which the bass drum is hit on every beat (1, 2, 3, 4)"; used in dance genres such as disco and electronic dance music. The kit's definition follows this.
- **House music: tempo and the parts of the beat.** English Wikipedia, "House music": "a repetitive four-on-the-floor beat and a typical tempo of 115-130 beats per minute" (lead) and, in Characteristics, "repetitive 4/4 rhythms including bass drums, off-beat hi-hats, snare drums, claps, and/or snaps at a tempo of between 120 and 130 beats per minute"; "the bass drum is usually played on beats one, two, three, and four, and the snare drum, claps, or other higher-pitched percussion on beats two and four". The kit's kick on every beat, off-beat open hat and clap on beats 2 and 4, and the statement that 128 BPM lies inside both ranges, come from this article. The model pattern's closed hat on the even steps, the bass on the off-beats and the bar-4 clap fill are choices for this kit, not from any source.
- **Sidechain compression.** English Wikipedia, "Dynamic range compression": "A compressor with a side-chain input controls gain from main input to output based on the level of the signal at the side-chain input"; "In electronic dance music, side-chaining is often used on basslines, controlled by the kick drum or a similar percussive trigger, to prevent the two from conflicting, and provide a pulsating, rhythmic dynamic to the sound"; "a ratio of 4:1 means that if input level is 4 dB over the threshold, the output signal level is reduced to 1 dB over the threshold. The gain and output level has been reduced by 3 dB"; attack is when the compressor is decreasing gain and release when it is increasing gain; "There is no industry standard for the exact meaning of these time parameters". The gain-reduction formula (level - threshold) x (1 - 1 / ratio) follows from the 4:1 example, and the example threshold of -20 dB, the 0 to 15 dB table, the release of one beat and the fast attack are **starting points chosen for this kit, not from any source** and are labeled as such on the pages. The ducking graph is a schematic (straight-line recovery).
- **Ducking.** English Wikipedia, "Ducking": "one track is made quieter (the ducked track) whenever another (the ducking track) gets louder"; the bass timbre ducked under the kick drum is the dance-music use. The kit's word "duck" follows this.
- **Build, drop and break.** English Wikipedia, "Drop (music)": a drop is "a point in a music track where a sudden change of rhythm or bass line occurs, which is preceded by a build-up section and break", and "the loudest portion of an EDM song". The kit's definitions of build, drop and breakdown follow this and say what each means in the kit; the word "breakdown" means different things in different genres (English Wikipedia, "Breakdown (music)"), so the kit says what it means here. The section lengths of the 64-bar model (8, 8, 16, 8, 16, 8) are **not from any source**.
- **Meter, tempo and hi-hats.** English Wikipedia, "Time signature": the upper numeral "indicates how many such note values constitute a bar" and the lower numeral the note value being counted, so 4/4 is four quarter-note beats per bar. English Wikipedia, "Tempo": tempo is measured in beats per minute, and in electronic dance music it is typically simply stated in BPM. English Wikipedia, "Hi-hat": a hi-hat is a pair of cymbals that can be played open or closed. One beat = 60 / BPM s is the definition of beats per minute; the 16th-note step = 15 / BPM s (four steps to a beat), the bar = 240 / BPM s = 16 steps, 128 BPM: 468.75 ms per beat, 117.1875 ms (printed 117.19) per step, 1.875 s per bar, 30 s for 16 bars and 120 s for 64 bars, and every table are arithmetic computed in `gen.py --check` exactly with fractions and with an independent decimal method.
- **The song.** English Wikipedia, "Deck the Halls": "The melody is Welsh, dating back to the sixteenth century, and belongs to a winter carol, 'Nos Galan'"; the melody was published by Edward Jones in Musical and Poetical Relicks of the Welsh Bards (English Wikipedia dates the first known publication of "Nos Galan" to 1794; IMSLP's page for the tune gives 1784 and other sources cite both editions, so the kit says only "in print by the 1790s" and was corrected from "published in 1794" at QA on 27 Nov 2026); the English words are dated 1862. The melody is therefore far older than the 1930 cutoff and in the public domain. The kit prints no words (the 1862 words are not used). The kit calls it "a traditional winter song". **Key and meter:** the kit uses F major and 4/4 as working choices for its examples and says so; it does **not** claim them as facts from a source. Kit 076 (QA.md, 23 Nov 2026) recorded F major and 4/4 for this tune in CPDL editions no. 47663 and no. 502, but I **could not** re-fetch CPDL today (every request, page or file, returned HTTP 403 from Cloudflare's challenge page), so that is only a pointer. The "usual tempo" of the song: **no tempo source was fetched**, so the kit's tempo-change table uses four plain tempos (90, 100, 110, 120 BPM) as examples chosen for this kit and tells students to use their own version's tempo.
- **No melody chart (honest note).** The brief allowed a note chart only if checked note by note against two independent sources fetched by the builder. I tried CPDL (HTTP 403), Wikimedia Commons' MIDI file and image of the melody (HTTP 429, upload host refused this machine), Mutopia (no Deck the Halls in its catalog), IMSLP (page not found) and abcnotation.com / folktunefinder.com (a bot challenge or HTTP 503). **No melody chart is included**: students enter the tune from a public-domain score of their choice or by ear. The chord page therefore has a blank check (first tune note of each bar against the bar's chord) instead of a chord-versus-melody table verified in code. The chord table itself (I, IV, V and vi built by stacking thirds in C, F and G major) is computed and checked in `gen.py --check`.
- **Logic Pro.** Apple's Logic Pro User Guide page on side chains was fetched (support.apple.com) but returned only its table of contents, so **could not** read how Logic words the Side Chain menu, the Compressor controls, Drum Machine Designer, the Step Sequencer, Retro Synth, Alchemy or the Marker track. The kit therefore names the tools, says "if your version has it", and invents no menu paths or key commands, except File › Bounce › Project or Section (Command-B), the Mixer key command (X) and "Compress in Finder", carried over from kits 083, 087 and 090 (those kits confirmed the Bounce path and Command-B on Apple Support search results; I did not re-fetch them).
- **Level: 0 dBFS and headroom.** English Wikipedia, "DBFS" (read for kit 090, 27 Nov 2026; not re-fetched): "The level of 0 dBFS is assigned to the maximum possible digital level". The kit says "keep the master peak below 0 dBFS with room to spare" and prints no target peak level, because no source for a target was fetched.
- **Example values (not from any source).** The pattern's steps and hits, the pitch and length descriptors (low, mid, high, short, medium, long: listening guides, not measurements), the chord loop's order and the loop's use of F major, the arrangement's layers and bars, the invented example remix and every invented time are example values chosen for this kit and labeled as examples.
- **No recordings, no brands.** No recordings, remixes, artists or albums are named. The kit uses no film, game or pop-music reference.
- **Art:** the cover, previews and deck use a piece from the art library (`art/hero.png`: a pair of studio monitor speakers, no text), copied whole and unchanged from `tpt/_art/library/studio-monitors.png`; logged in `tpt/_art/USAGE.md`. There is no pre-made art for this item in `tpt/_art/next`. Everything else, including every number, table, icon, step grid, chord table, gain curve, ducking graph, layer table, signal chain and arrangement map, is drawn or printed in code.
- **Fonts:** Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: listing no sooner than the 2-8 week window before winter allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, recording name or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Secular and inclusive.** The song is described as a traditional winter song; no religious content, no alcohol imagery, no brands other than Logic Pro, no lyrics. `gen.py --check` fails on alcohol, religious and shopping words and on lines of the song's words.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions, with an independent decimal method and against hand-typed expectations).** Seconds per beat = 60 / BPM; per 16th-note step = 15 / BPM; per bar of 4/4 = 240 / BPM = 4 beats = 16 steps; 16 bars = 3840 / BPM; 64 bars = 15360 / BPM. At 128 BPM: 468.75 ms per beat, 117.1875 ms per step (117.19 rounded half up), 234.375 ms per eighth note, 1.875 s per bar, 7.5 s per 4-bar loop, 30 s per 16 bars, 60 s per 32 bars, 120 s per 64 bars. Lengths of 8 / 16 / 32 / 64 bars: 15 / 30 / 60 / 120 s at 128 BPM, 16 / 32 / 64 / 128 s at 120 BPM and 15.484 / 30.968 / 61.935 / 123.871 s at 124 BPM. Rounding: milliseconds per beat and step to 2 decimals, seconds to 3, half up. Section starts at 128 BPM: 0, 15, 30, 60, 75, 105 s; the arrangement ends at 120 s. Tempo change from a plain tempo T to 128 BPM: ratio 128 / T and percent (128 - T) / T x 100: 1.4222 and 42.22% at 90, 1.28 and 28% at 100, 1.1636 and 16.36% at 110, 1.0667 and 6.67% at 120.
- [ ] **Sidechain numbers.** Gain reduction (level - (-20)) x 3/4 dB for a kick at -20, -16, -12, -8, -4 and 0 dB = 0, 3, 6, 9, 12 and 15 dB (4 dB over at 4:1 is 3 dB down, as in the source's example); the example release is one beat = 4 steps = 468.75 ms (1, 2 and 3 steps = 117.1875, 234.375 and 351.5625 ms); the four kicks of a bar fall at 0, 468.75, 937.5 and 1406.25 ms. The gain-curve drawing plots those six points and one line; the ducking drawing shows 4 kicks and 4 dips.
- [ ] **Pattern and arrangement numbers (recomputed from the data and from the drawings).** 5 lanes (kick, clap, closed hat, open hat, bass); 4 bars of 16 steps = 64 steps; hits per bar 22, 22, 22, 24 = 90; hits per lane 16, 10, 32, 16, 16 = 90; kick on grid steps 1, 5, 9, 13 (4 a bar); open hat and bass on 3, 7, 11, 15 (the kick and the bass never share a step); clap on 5 and 13 (beats 2 and 4) plus a fill on 15 and 16 in bar 4; bar 2 grid step 5 = (16 + 4) x 15 / 128 = 2.34375 s. Arrangement: 64 bars, 6 sections (8, 8, 16, 8, 16, 8 bars), 6 layers; bars per layer 48, 40, 48, 32, 64, 40 = 272; layers sounding per bar 2 (bars 1-4), 3 (5-16), 6 (17-32), 2 (33-40), 6 (41-56), 3 (57-60), 2 (61-64) = 272. Layer table drawing: 6 rows, 6 icons, 6 role chips, 6 side-chain chips (1 trigger, 3 ducked, 2 not ducked), 36 dots; signal chain: 5 stages, 4 arrows.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061, 063, 067, 070, 076, 080, 083, 087 and 090): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged; the deck's three-classes badge and the terms-page thank-you note are applied inside `gen.py`.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Drum Machine Designer (hedged), the Step Sequencer (hedged), Retro Synth and Alchemy (hedged), the Compressor's Side Chain menu (hedged), the gain-reduction meter, the Piano Roll's 16th-note grid, a transpose option on the region (hedged), the Marker track (hedged), the Mixer (X), Bounce (Command-B) and Compress in Finder.
- [ ] **Open questions for the owner:** (1) **No melody chart.** The tune could not be checked against two fetched sources, so students enter it from a public-domain score or by ear; if you want a chart, a builder with CPDL access can reuse the verified Deck the Halls chart from 076. (2) **Song tempo.** No source for the song's usual tempo was fetched; the tempo-change table uses four example tempos. (3) **Key and meter.** F major and 4/4 are stated as working choices, not as facts from a source. (4) **Title.** No Winter, Holiday, Christmas, Carol or song name in the title because of TpT's seasonal-title notice (see 1); the brief's longer example title was 83 characters, so this one drops "Project". (5) **Price.** $8.00, as queued. (6) **Art.** There is no pre-made art for this item; the studio-monitors library piece fits the low kick and bass. (7) **Logic details.** Apple's pages for the Side Chain menu and the Compressor could not be read, so the kit stays generic; say if you want a Mac check before release. (8) **Classes.** Three periods; Class 2 holds the chords, the tune and the sidechain, so the pacing page shows how to use two or four.
