# QA 052 Holiday Music Word Puzzles (round 2)

## Findings
- `gen.py --check` passes. `tools/tpt-validate.py` prints OK. `git status --short` shows only the new 052 folder. The product PDF has 19 pages and the preview PDF has 4. `tpt.json` still says 19 pages, grades 3-6, valid subjects and tags.
- Directions, checked with my own code on the rendered PDF (letters read by position, all 8 directions, every listed word found exactly once, no extras):
  - WS1: right and down only.
  - WS2: right, down and down-right.
  - WS3: right, down, down-right and up-right.
  - WS4: adds left (backwards).
  - WS5 and WS6: all 8 directions.
  - These match the stated sets everywhere. On-page labels: WS1 says across and down, WS2 says "(down and to the right)", WS3 says "either up or down", WS4 says some words go backwards, WS5 and WS6 say any of the 8 directions. The Teacher Notes (both sections), UPLOAD.md and the gen.py description text give the same sets. The how-to page is generic ("every direction the puzzle allows", "harder puzzles use all 8") and does not contradict. The cover and preview captions make no direction claims.
- Puzzles and keys: all 6 word searches have 12/12/13/14/14/14 words. The key start rows, columns and directions match what I computed. I recomputed the key text for WS4 (cocoa and concert left, mittens up-right) and for WS5 and WS6, and it is right. The 4 crosswords are intact, the keys are filled in and the clue counts match the headers (12/13/13/13).
- Visuals: I looked at all 19 pages at 110 dpi, the cover, preview-1..3 and all 4 pages of the preview PDF. Page 2 has no overflow, and the glance table sits above the footer. There is no clipping, overlap or blank art, and the previews are watermarked. The cover art is correct: BELLS, FORTE and TEMPO in the grid, and the TEMPO/TIE/PIANO/FORTE mini crossword. The page counts on the terms page are right.
- Content: the wording is secular and non-denominational. There are no brands or lyrics. The disclosure line is on page 19 and in UPLOAD.md.

The round-1 defect is fixed. I found nothing a buyer would notice.

**Verdict: APPROVED**

## Rescue 2026-11-18
Held rescue (step 2b): the BLOCKING item (two-digit crossword clue numbers colliding with letters in the answer-key grids, also preview-2 and PREVIEW p4) was fixed in gen.py (clue numbers small in the top-left corner, letter centred and shifted down/right, shared metrics for every crossword grid; --check tests number against letter boxes for 1-, 2- and 3-digit numbers). Puzzles, words and keys unchanged. Fresh Visual inspector re-checked cover, preview-1..3, all 19 PDF pages and 4 preview-PDF pages at full size, with 250 dpi crops of every crossword grid: OK, no BLOCKING item. NOTES (not changed): clue numbers are small (about 6 pt at print size, readable; dots in the preview thumbnails), blank bands between crossword grids and clue lists, one-word last columns in word lists, blank gap on p3.
**Verdict: APPROVED**
