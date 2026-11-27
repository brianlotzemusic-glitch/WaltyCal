# QA: 092 House Remix (Logic Pro), 27 Nov 2026

## Findings

**Defects found and fixed in gen.py (rebuilt, `--check` OK, `tools/tpt-validate.py` OK)**
1. The song facts said the tune "was published in 1794". Sources disagree: English Wikipedia gives 1794 for the first known publication of "Nos Galan"; IMSLP's page for the tune gives 1784 (Edward Jones, Relicks of the Welsh Bards); other sources cite both editions. Reworded on pages 3 and 12 and in the slide 8 notes to "was in print by the 1790s" (true on either date); the gen.py checks and the UPLOAD.md sources paragraph were updated to match.
2. Page 15 (and slide 12, preview 3): the "0" label at the threshold sat on the dashed threshold line. Added a white halo behind every point label.
3. Page 15 (and slide 11): the "release 468.75 ms" label touched the arrow line under it. Moved it up.

**Math (own script, exact fractions; every printed value compared cell by cell): all correct**
- Bar 240/128 = 1.875 s; beat 468.75 ms; 16th 117.1875 ms (printed 117.19, half up).
- Timing table at six tempos (100, 110, 120, 124, 128, 130), the 8/16/32/64-bar table at 120/124/128, and the worked-example table: all match.
- Tempo change at 90, 100, 110, 120: ratio 1.4222, 1.2800, 1.1636, 1.0667; 42.22, 28.00, 16.36, 6.67 percent; 16 bars 42.667, 38.400, 34.909, 32.000 s: all match.
- Arrangement: section starts 0, 15, 30, 60, 75, 105, end 120 s; layer-bars 48, 40, 48, 32, 64, 40 = 272; the per-bar layer row `2222 3333 ...` (64 numbers) matches the table, the drawing and slide 15. The bars drawn on the map (250 dpi crop) match the printed bar ranges.
- Step grid, counted from the 250 dpi render of page 13 (pixel sampling of all 320 cells, not gen.py data): kick on steps 1, 5, 9, 13 in all four bars; clap 5 and 13, plus 15 and 16 in bar 4; closed hat on the even steps; open hat and bass on 3, 7, 11, 15. Hits per bar 22, 22, 22, 24 = 90; per lane 16, 10, 32, 16, 16 = 90. Matches the printed table, page 9 and slide 7. The blank grid is blank. "Two and four = steps 5 and 13" is true.
- Sidechain: gain reduction (level + 20) x 3/4 = 0, 3, 6, 9, 12, 15 dB; the plotted points sit on the line at the right levels; the ducking graph is labeled a schematic; release 1-4 steps = 117.1875, 234.375, 351.5625, 468.75 ms; kicks at 0, 468.75, 937.5, 1406.25 ms. Bar 2 step 5 = 20 x 15/128 = 2.34375 s.
- Rubric 5 x 5 = 25. Chord table (I, IV, V, vi in C, F, G) correct. Layer table icons/dots/chips (6 rows, 3 ducked, 1 trigger) correct.

**Claims (live sources, below)**
- Four on the floor, house tempo, sidechain, ducking, build/drop, off-beat hi-hats: the pages' wording is supported. Tempo wording "typically 115 to 130 BPM, and 120 to 130 BPM in its most typical form" matches the two ranges in Wikipedia's House music article (lead 115-130, Characteristics 120-130). Wikipedia's Drop article does not define "breakdown" as a section; the kit defines it as its own term (UPLOAD.md says so), which is fine.
- Deck the Halls: Welsh, sixteenth-century, "Nos Galan", English words 1862 by Thomas Oliphant (the 1862 date is mentioned only in UPLOAD.md; the kit prints no lyrics and no English-lyric date); public domain. Fixed the 1794 wording (above).
- Key and meter: "working choices, not facts" is honest. I could not find a score to confirm F major and 4/4: the Wikipedia article gives neither, IMSLP lists no key or meter, and 8notes lists the tune as 2/2 and in G, C or E-flat major in different arrangements. The hedge stays and is in fact the right wording. No melody chart anywhere; every mention (page 14 blank tune-against-chord check, page 12 checklist, page 4, quick reference) is consistent: "from a public-domain score or by ear".
- Logic Pro: Apple's side chain page again returned only the guide's table of contents. Every control is hedged ("if your version has it"), no invented menu paths; only File > Bounce > Project or Section (Command-B), Mixer (X) and Compress in Finder are stated, as in earlier kits.
- Secular: no religious teaching, no lyrics, no alcohol/brand words (text grep clean). US spelling clean.

**Rules**
- UPLOAD.md counts: 26 + 20 = 46, tpt.json pages 46, deck PDF has 20 pages, preview PDF 4 pages. Student/teacher split (9 + 15 + cover + terms) is true.
- Step N, page and class cross-references agree across the pages, project sheet, pacing page and slide notes. Deck badges: slides 1-8 Class 1 (slide 4 "Classes 1-3"), 9-14 Class 2, 15-20 Class 3, as the pacing page says. Page badges (11-13 Class 1, 14-16 Class 2, 17-18 Class 3, 24 Classes 2-3) agree with the pacing page.
- Title 75 characters, "Logic Pro" in the first 30, no seasonal word. Tags (Winter, Project-based Learning, Projects, Activities) and subjects (Music, Music Composition, Computer Science - Technology) each checked individually against the option lists: exact, none a heading ("Activities" is an entry under the "Hands-on Activities" heading). 4 grade entries. Disclosure line present.

**Viewed:** all 26 PDF pages at 110 dpi; all 20 deck slides; all 4 preview-PDF pages; cover.png (all four edges clear), preview-1, -2, -3 at full size, one at a time; 250 dpi crops of the step grid, gain curve, ducking graph, signal chain and layer table, and arrangement map. Notes only (not blocking): the cover follows the same layout as released 090 (no ribbons or page mockup); slide 20's reflection box sits close to the footer rule.

## Sources actually fetched (27 Nov 2026)
- en.wikipedia.org: Four on the floor (music); House music; Deck the Halls; Drop (music); Dynamic range compression; Ducking; Hi-hat.
- imslp.org: Deck the Halls (Welsh Folk Music) (no key/meter; melody first published 1784 per IMSLP).
- Web searches: Deck the Halls scores (8notes lists 2/2 and several keys); Nos Galan 1784 vs 1794.
- support.apple.com Logic Pro side chain page (contents only, nothing readable on the Side Chain menu). musescore.com returned HTTP 403.

**Verdict: APPROVED**
