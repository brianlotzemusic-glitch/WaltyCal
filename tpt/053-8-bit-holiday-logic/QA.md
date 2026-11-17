# QA, round 2: 053 8-Bit Holiday (Logic Pro chiptune)

Checked after the fixer padded the waves, cycle, roll, arps and map art.

- `gen.py --check`: CHECK OK. `tools/tpt-validate.py`: OK. `git status --short`: only this folder (untracked) and the expected `tpt/_art` changes.
- Counts: PDF 27 pages, deck PDF 15, pptx 15 slides, preview PDF 4. ZIP holds the 3 files and nothing else. UPLOAD.md and tpt.json agree: 27 + 15 = 42 pages, 4 class periods, grades 9-12, title 77 characters.
- All 27 pages (110 dpi), all 15 slides, cover, preview-1..3 and all 4 preview-PDF pages were viewed at full size. No clipped text or art, no overlaps, no blank pages.
- Note chart (pp. 12-14, plus the worked-example roll and slide 6), bar by bar against the printed notes: 21 bars, 62 notes, every bar fills 16 sixteenths, pitches unchanged, nothing shifted or clipped by the 3-unit padding. The pickup is C5 on beat 4 and bar 9 is a dotted half plus a rest. Bar 13 is B dotted quarter, A eighth, G quarter, C5 quarter. The chart agrees with the tune page and the answer table. Chords sit under the notes, and the bass table matches the chords.
- 250 dpi crops: the SQUARE, PULSE, TRIANGLE and NOISE tiles are whole, with the noise trace inside its frame. The cycle art, the roll art, the four arpeggio cards (Up, Down, Up & Down and Up two octaves, each 16 steps) and the worked-example map are all complete. Lane bars in the map sit flush with their lane boxes; nothing is cut off.
- The cover's four edges are clear. The previews and preview PDF are watermarked and show correct content.
- Logic features are real and hedged. The rubric is 5 x 5 = /25. The length helper is correct (33 bars at 120 BPM = 66 s). Public-domain source and year are noted.

Minor notes (do not block):
- The pale off-white box behind the hero or drum art is faintly visible on slides 1, 10 and 15 and in preview-3.
- The bottom box on p. 26 touches the footer rule.

**Verdict: APPROVED**

## Inspector 2026-11-17
Visual inspector (fresh agent, new BLOCKING-only brief): OK, no BLOCKING item. Viewed cover, preview-1..3, all 27 PDF pages, all 15 deck slides and all 4 preview-PDF pages at full size. NOTES (not changed): soft pixels on the small cover/deck snowflakes, slide 2 empty gap in the black box, p26 teacher box flush on the footer rule, p7 last notes line near the footer rule, p11 last automation dot ~40px short of the 1:06 tick, faint off-white box behind hero art on slides 1, 10, 11, 15 and preview-3, half-empty bottoms on p5 and p17.
**Verdict: APPROVED**
