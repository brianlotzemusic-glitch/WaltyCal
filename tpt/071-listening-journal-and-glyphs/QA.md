# QA: 071 Listening Journal and Listening Glyphs (independent review)

## Checks run
- `gen.py --check`: CHECK OK, before and after the fix. `tools/tpt-validate.py`: OK.
- Vocabulary: all 40 definitions read; correct and age-appropriate for grades 2-8. Groups are 6+8+6+7+7+6 = 40. Italian terms and pronunciations are correct. Dynamics are p, mp, mf, f with correct meanings.
- Hairpins: crescendo opens to the right, decrescendo closes to the right (page 8 drawn and checked in code).
- Beat page (page 11) at 250 dpi: 2/4, 3/4 and 4/4 have 2, 3 and 4 quarter notes. Stems sit on the left edge of the head going down from the middle line. Bars sum correctly.
- Glyphs: 4 glyphs, 6 stamps each = 24 stamps. The stamp sheet matches the key and the pages that show glyphs.
- Counts: 10 response pages (6-15), 4 glyphs, 24 stamps, 40 words. Rubric is 4 rows x 3 = 12 points, and the score bands 11-12, 9-10, 6-8, 0-5 cover every total. Page counts in UPLOAD.md sum to 19 and the PDF has 19 pages.
- Track A (grades 2-4) and Track B (grades 5-8) wording is appropriate. No named recordings, composers or copyrighted works. US spelling. Complete sentences.
- Listing: title is 71 characters with no seasonal words. Disclosure line is present in UPLOAD.md, teacher notes and terms. I checked each of Worksheets, Graphic Organizers, Printables, Rubrics, Activities, Handouts, Music and Speaking & Listening individually in a script. All are exact entries in TAG-OPTIONS.json and SUBJECT-OPTIONS.json, and none is a group heading. There are 4 grade entries, and UPLOAD.md explains the 2-8 span.

## Viewed
All 19 PDF pages at 110 dpi, one at a time. All 4 preview-PDF pages at 110 dpi. cover.png (all four edges), preview-1, preview-2 and preview-3 at full size. Page 11 notation cropped at 250 dpi. Page 4 re-viewed after the fix.

## Defect found and fixed
1. Page 4 (glyph key) said the glyphs "also appear on page 6, 13, 14 and 15", but they also appear on pages 7, 8, 10 and 11. Fixed in `gen.py`; the sentence now lists pages 6, 7, 8, 10, 11, 13, 14 and 15. Rebuilt, check OK.

## Notes (no change needed)
- "Keyboards belong to more than one family" on page 7 is an acceptable simplification.
- The preview PNGs were rebuilt by gen.py after the fix and show the corrected page 4.

**Verdict: APPROVED**
