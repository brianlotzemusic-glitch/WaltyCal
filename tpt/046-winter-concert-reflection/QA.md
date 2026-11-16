# QA: 046 Winter Concert Reflection (round 2)

## Findings
- `python3 gen.py --check` (run from the product folder; there is no root gen.py) passes: 14 pages, 54 statements, totals 6-24, 4 bands, worked example 19 Proficient, no overflow, one watermark per preview page. `tools/tpt-validate.py` prints OK. `git status --short` shows only `tpt/046-winter-concert-reflection/` as new.
- Scoring recomputed: 6 areas x 3 statements = 18 ticks per sheet (counted on the Band, Choir and Orchestra pages). Level = ticks + 1, so each area is 1-4 and totals run 6-24. Bands 6-10, 11-15, 16-20, 21-24 cover every integer with no gaps or overlaps.
- Worked example: ticks 3,2,2,3,1,2 give levels 4,3,3,4,2,3 = 19, Proficient. Correct on the guide page.
- All 14 pages were rendered at 110 dpi and viewed individually (the rebuild did not break any). Also viewed at full size: cover, preview-1..3 and all 4 pages of the PREVIEW PDF. Nothing clipped, overlapping, blank or unreadable. Cover reads at thumbnail size. No notation or tunes, so no public-domain issue.
- UPLOAD.md and tpt.json agree: title is 78 characters (<= 80), 14 pages and the page list totals 14, "Answer Key: Not Included (the rubric and worked example cover scoring)" is now in the description and `answer_key` is set in tpt.json, the disclosure line is present in the description and on the terms page, 4 grades, price $3.50, files exist, no heading-type subjects or tags.
- Wording is secular and non-denominational; teacher guide instructions are complete enough for a substitute.
- Minor, not blocking: the rubric total row's first cell is labelled "Band"; preview-3 cards have empty lower space.

**Verdict: APPROVED**

## Fix round 16 Nov 2026
Fixed in gen.py: rubric total-score row now labelled "Level" (was "Band" over level names); credits/disclosure line no longer claims notation or answer keys are verified (page, UPLOAD.md and check updated); Class Summary rows "Class total per area" / "Average level per area" now shade the TOTAL and BAND cells and the area headers use full names; p7 legend moved clear of the footer. Fresh inspector (all images, 14 pages, 4 preview pages): no real defects, only trivial nits. gen.py --check OK, tpt-validate OK.

**Verdict: APPROVED**
