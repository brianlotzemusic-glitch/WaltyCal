# QA: Free Play (TpT 021, DMP2, $9), 18 Oct 2026

Reviewer did not build this. git pull done on shop-factory; `gen.py --check` prints CHECK OK.

## Checks
- **Render review:** all 22 PDF pages, all 19 deck slides (PDF), the cover, 3 preview PNGs and the 4-page preview PDF viewed. No overflow, clipping, empty pages or typos found. Deck slide 1's black banner sits on one line (no wrap). Minor, acceptable: several student pages (Idea sketchpad, Work plan, Reflection, checklist page 17) end with whitespace, which is writing room.
- **tpt.json:** grades 9th-12th (4); 1 subject (Music); 1 tag (Autumn, same as approved 019/020; METADATA-GUIDE says replace once the dropdown offers others, an uploader matter); price and license_price $9.00; tax_code set; every file in `files` exists; pages 41 = 22 + 19 (PDF 22, deck PDF 19, pptx 19 slides, preview PDF 4 pages).
- **ZIP:** exactly the 3 files in `zip_contents` (inside a "Free Play - Hudson Beat" folder, as in 020), each byte-identical (cmp) to the folder copy. Folder 6.6 MB, nothing near 90 MB.
- **UPLOAD.md:** title 74 chars (<= 80); order follows TpT's form.
- **Deck:** speaker notes on all 19 slides.
- **Banned content:** no "word for word"/"verbatim", no school or Blind Brook branding, no student names or work, no audio/video/lyrics/links, no individual third-party author names (grep of PDF text, deck text, UPLOAD.md).
- **Owner's rubric:** /25 kept (5 categories x 1-5, average of student and teacher, page 18). Kit tips labelled "Suggestions from this kit, not part of my rubric" (page 7) and "Kit suggestions, not part of my sheets" (setup page).
- **Reflection page (21):** states the owner's definition (a written or oral conversation about how you did on the project and what you would do differently next time); no points or rubric row. Disclosed on the "What changed from the original" page (page 8, "Reflection added") and under "New in this kit".
- **Invented additions disclosed on page 8:** Idea starters, the "Late Bus Home" worked example (invented, on paper, no audio; 4+12+8+12+8+4+8+4 = 60 bars x 2.5 s at 96 BPM = 150 s = 2:30, checks), Idea sketchpad, Proposal planner, Work plan, Logic quick reference, vocabulary and presentation planner pages, deck.
- **Wording changes:** the 7 are listed on page 8 (class page for LMS name, "Day 1" to "Class 1", page numbers in steps, past-student-work resource with no work included, pacing "Classes 3-5" row split, layout-only rubric changes, deck shortenings), plus the Reflection disclosure.

Required fixes: none.

**Verdict: APPROVED**
