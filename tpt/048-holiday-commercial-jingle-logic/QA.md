# QA: 048 Commercial Jingle (Logic Pro), round 2

## Checks that passed
- `python3 gen.py --check` (run inside the 048 folder; the repo root has no gen.py) prints CHECK OK; `python3 tools/tpt-validate.py tpt/048-holiday-commercial-jingle-logic` prints OK; `git status --short` shows only `tpt/048-holiday-commercial-jingle-logic/` as new.
- Round 1 fixes confirmed. Searched all text of the 28-page PDF, the PREVIEW PDF, the deck PDF, every PPTX XML part (slides, notes), UPLOAD.md, tpt.json and gen.py for "Toasty", "coloured", "colour", "organis", "favour", "centre", "licence", "grey", "metre", "practise", "recognis", "realis" and "New Drummer Track": zero hits. The Drummer recipe (page 14) now says "the + button in the track list, then choose Drummer". Page 18 reads "colored". Cover reads "A WINTER AD FOR AN INVENTED PRODUCT" on cover.png and on the PDF cover.
- Brand check: WebSearch for "Fluffwick" brand socks and "Fluffwick Snug" socks found no such brand or product (closest results were Fluffepuff, Swiftwick, Snuggy, SnugBug, none the same name). Acceptable.
- Worked example with the new name: line 2 "Fluffwick Snug Wool Socks." = 4 words, 5 syllables (Fluff-wick Snug Wool Socks). Script totals 12 words (4+4+4), 16 syllables (5+5+6). 4 words / 2.5 words per second = 1.6 s per line, inside the 2-3 words per second band; lines start at bar 3 = 4 s, bar 11 = 20 s, bar 13 = 24 s and end 5.6 / 21.6 / 25.6 s. Ducking points 3.75/6.1, 19.75/22.1, 23.75/26.1 are right (half a beat before, one beat after, no overlap).
- Bars/BPM: 240/BPM s per bar; bars in 30 s = BPM/8 (80-128 BPM gives 10-16 bars); beat and bar rounding correct (0.75, 0.682, 0.625, 0.577, 0.536, 0.5, 0.469; 3, 2.727, 2.5, 2.308, 2.143, 2, 1.875); end locators bar+1 correct; loop table full loops/bars left correct (e.g. 15 bars = 3 loops + 3 left). Worked example 15 bars at 120 BPM = 30 s, sections 2+4+6+3 = 4+8+12+6 s.
- Chord loops in C, G, D, A major and A, E, B minor are spelled correctly (F#m, Bm etc.), Roman numeral case correct. Rubric 5 x 5 = /25 on page 23, slide 13 and preview.
- Listing: UPLOAD.md title "Logic Pro Jingle Project | 30-Second Ad Music & Voice-Over | High School Music" = 78 chars (<= 80); page list 1 + 9 + 17 + 1 = 28 PDF pages plus 15 slides = 43; tpt.json pages 43, grades 9th-12th, subjects Music / Computer Science - Technology / Music Composition, tags Winter / Project-based Learning / Projects / Rubrics (no headings), files and zip_contents match the ZIP (PDF, PPTX, deck PDF; no audio). Cover says 28 pages + 15 slides, consistent. Disclosure line present in the description and on the terms page.
- Visual review at 110 dpi: all 28 PDF pages, all 15 deck-PDF slides, all 4 PREVIEW PDF pages, plus cover.png and preview-1/2/3 at full size, each looked at individually. No clipping, overlap, blank pages, broken art, or typos; watermark present on the 4 preview pages and the three preview thumbnails; cover and thumbnails read at small size. No music notation anywhere (waveforms, lanes, chord cards only).
- Rules: invented products only; Logic features named are real; no brands other than the Apple compatibility line; no tune or lyrics, so no public-domain question.

## Problems
- Minor, not blocking: slide 3 title "What is Commercial Jingle?" reads slightly oddly (carried from round 1).

**Verdict: APPROVED**

Required fixes: none.
