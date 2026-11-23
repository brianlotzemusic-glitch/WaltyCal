# QA: 076 Holiday Mashup (Logic Pro)

## Findings
1. `gen.py --check`: passes before and after my edits. `tools/tpt-validate.py`: OK.
2. **Melody charts.** I fetched the CPDL MusicXML files myself and compared them with the charts using my own script.
   - Jingle Bells chart (G major, 16 bars of 4/4) against CPDL 38153: every bar matches (chart bars 1-8 are the file's bars 9-16, the verse; chart bars 9-16 are the file's bars 1-8, the chorus). The only differences are two D5 lyric pickups that the file adds, at the end of the verse (file bar 16) and after chorus bar 4 (file bar 4). The chart's two half notes before them are correct.
   - Against CPDL 66808 (A-flat, 2/4): the verse and chorus pitch sequences equal the chart moved down 1 semitone.
   - Deck the Halls chart (F major) against CPDL 47663 and CPDL 39398 (E-flat, +2): 0 bars differ. CPDL 502: the top note of each chord matches and bar 1 is empty, as the builder says. All 16 bars of both charts sum to 16 sixteenths.
   - Composition status: Pierpont published "The One Horse Open Sleigh" on 16 Sep 1857 (Wikipedia). Deck the Halls is the Welsh "Nos Galan" melody, dated to the 16th century and first published in 1794; Oliphant's English words are from 1862 (Wikipedia). Both are far older than the 1930 cutoff, so the tunes are public domain.
   - Licensing: the chart equals the soprano line of 38153 (CPDL license, free copying) and of 47663 (CPDL license). The Hale edition (66808, license "Personal") is used only as a cross-check and is not needed to justify any chart. Printing pitches and lengths of public-domain tunes is acceptable. UPLOAD.md and the terms page say plainly that the editions carry editors' licenses and nothing but the tune's pitches and lengths is used. The lyric pickup omission is stated on pages 13, 14 and in UPLOAD.md.
   - **Defect fixed:** the pickup description ("before each chorus and at the end of the verse") was inaccurate. It now reads "at the end of the verse and after the fourth bar of the chorus" (UPLOAD.md and page 13).
3. **Math, recomputed in my own script.** All match the kit. Ratio 120:96 = 5:4. Percent changes -10% and +12.5%. Mean 108 BPM. Seconds per bar 2.2222 at 108, 2.5 at 96 and 2.0 at 120. 44 bars = 97.78 s (110.00 s at 96, 88.00 s at 120). Section starts at 108 BPM: 0, 8.89, 26.67, 35.56, 53.33, 88.89 s (also 96 and 120). Audio length changes +11.11% and -11.11%. Pitch from speed -1.82 and +2.04 semitones. G to F is -2 (up 10), the shorter direction is at most 6. Relative minors (E minor to D minor), key signatures and circle steps are correct. The clash check was recomputed by an independent loop: every shift from -6 to +5 matches page 16 and the slide, -2 gives 45/14/5, and bar 9 gives 0/3/1. The rubric is 5 x 5 = 25. The tempo tables are correct.
4. **Logic claims.** Smart Tempo, Flex Time, Flex Pitch and Session Players are hedged ("if your version has it"). The menu paths are standard or hedged (File > New, File > Bounce > Project or Section, Command-B, X and A keys, Transpose in the region inspector, the Marker global track with a hedged key command). No recordings or brands are named. The framing is secular. No lyrics are printed. The "recording from 1898" mention is a dated fact from Wikipedia, not a named recording.
5. **Defect fixed:** the description and UPLOAD.md promised "Part of the Holiday Logic Pro Project Pack: save about 30%", a bundle that does not exist. I removed the line from the description and removed owner question (4) about it, then renumbered the questions.
6. **Rules.**
   - Page counts agree: 27 pages + 15 slides = 42.
   - Cross-references agree: Step N, class badges, page numbers and slide ranges (Class 1 slides 1-7, Class 2 slides 8-10, Class 3 slides 11-15).
   - The "three classes" slide carries "CLASSES 1-3", not a single-class badge.
   - The title is 79 characters, "Logic Pro" is in the first 30, and it has no seasonal words.
   - tpt.json: grades are 4; the three subjects and five tags are each exact entries in the option lists (Winter 155, Christmas-Chanukah-Kwanzaa 122, Project-based Learning 40, Projects 41, Activities 30), and none is a heading.
   - The disclosure line is present in the description and on the terms page. US spelling throughout.
7. **Visual checks.** I viewed all 27 PDF pages at 110 dpi, all 15 deck slides, all 4 preview-PDF pages, and cover.png and preview-1..3.png at full size, plus a 250 dpi crop of the Jingle Bells piano rolls on page 13. I found no clipped, overlapping or blank content. The piano-roll notes match the tables.

## Sources actually fetched
- English Wikipedia, "Jingle Bells" and "Deck the Halls".
- CPDL ChoralWiki pages "Jingle Bells (James Pierpont)" and "Deck the hall (Traditional)" (edition numbers and licenses).
- CPDL MusicXML files: Jingle_Bells_SAB (38153), Jingle_Bells_adapted (66808), Deck_the_hall (47663), Ws-deckhall (502), Deck_the_halls_Wood (39398).

**Verdict: APPROVED**
