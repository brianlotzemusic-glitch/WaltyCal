# QA: 059 Winter Bucket Drumming

## Checks run
- `gen.py --check`: OK. `tools/tpt-validate.py`: OK. `git status --short`: only the 059 folder and `tpt/_art/USAGE.md` (one added line).
- Rendered all 16 pages at 110 dpi and viewed each. Cropped pages 4 and 8 to 13 at 250 dpi (grooves 1, 3, 5, 6 including the sixteenth parts, and the key icons). Viewed cover.png, preview-1/2/3.png and the preview PDF page 1 (watermarked, page 4 notation key). The preview PDF has 4 pages.
- All 6 grooves and 18 parts re-read from the rendered pages:
  - Every bar sums to 4 beats.
  - Syllables match the notation.
  - R/L hands are present on every note and alternate through rests and across barlines. Sparkle alternates within its own part.
  - Printed counts (notes, rests, accents, rim clicks) match what is drawn.
  - No two grooves are identical.
- The stacked sample score (page 7, Groove 1) matches the page 8 notation exactly. Barlines and beat positions line up, and the "read straight down" lines are correct.
- The key defines every symbol used: quarter and half notes, quarter rest, eighth pairs, sixteenth groups (ti-ka-ti-ka, ti-ti-ka, ti-ka-ti), accent, rim click x, neutral clef, 4/4, barline, final barline, hand letters.
- Stems are all up on the right of the head, one beam for eighths and two for sixteenths, consistent everywhere. Cover and preview art have no notation problems and no clipping.
- Counts agree across pages, previews, UPLOAD.md and tpt.json: 6 grooves, 18 parts, 16 pages. Page cross-references are correct (safety p3, key p4-5, layering p6, score p7, grooves p8-13, planner p14, rubric p15, terms p16). Layering steps 1 to 4 match the planner. The timing arithmetic (24 bars at 70 bpm, about 80 seconds) is right.
- The safety page is sensible: clean plastic buckets, no cracks or sharp edges, tape rough spots, hearing protection, sticks or hands, stable setup. Language is grade 3-8 level, US spelling, complete sentences, no internal QA wording. The disclosure line is present on the terms page and in the description. No standards codes are cited.
- Rubric: Part A is 18 parts (6 grooves x 3). Part B is 4 skills x 3 points = 12. Both match the teacher notes.
- tpt.json: grades 3rd to 6th (UPLOAD.md section 3 explains why the listing says 3-8). Subjects "Music" and "Instrumental Music" and tags Winter, Activities, Lessons, Printables, Rubrics are exact entries in the options files. All files exist and pages = 16. The title is 73 characters with no seasonal words. The page list totals 16.

## Notes (non-blocking)
- Page 5 "The three parts" table lists Part 2 as quarters, eighths, rests and sixteenths. Grooves 2 to 5 also use half notes and accents in Part 2, which the key does define elsewhere.
- UPLOAD.md description line "Notation key (two pages) (2 pages)" is redundant.

**Verdict: APPROVED**

Required fixes: none.

## Inspector 2026-11-19
Visual inspector (fresh agent, BLOCKING-only brief): OK, no BLOCKING item. Viewed cover (four edges), preview-1..3, all 16 PDF pages and all 4 preview-PDF pages at full size with 250 dpi crops of grooves 5 and 6; note, rest, accent and rim-click counts on every groove page match the notation, beams and hand letters correct. NOTES (not changed): empty lower bands on p5, p14, p16; the PREVIEW watermark spans each preview image rather than each thumbnail; redundant 'Notation key (two pages) (2 pages)' line in UPLOAD.md.
**Verdict: APPROVED**
