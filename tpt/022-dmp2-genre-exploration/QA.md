# QA: Genre Exploration (TpT 022, DMP2, $11), 19 Oct 2026

Reviewer did not build this. git pull done on shop-factory; `gen.py --check` prints CHECK OK.

## Checks
- **Render review:** all 23 PDF pages, all 19 deck slides (PDF), the cover, 3 preview PNGs and the 4-page preview PDF viewed. No overflow, clipping, empty pages, typos or big empty gaps found. Deck slide 1's black banner sits on one line (no wrap). Minor, acceptable: Reference log, Loop and form sketch and checklist pages end with ruled/blank writing room.
- **tpt.json:** grades 9th-12th (4); 1 subject (Music); 1 tag (Autumn, as in approved 019-021; uploader matter per METADATA-GUIDE); price and license_price $11.00; tax_code set; every file in `files` exists; pages 42 = 23 + 19 (PDF 23, deck PDF 19, pptx 19 slides, preview PDF 4).
- **ZIP:** exactly the 3 files in `zip_contents` (inside "Genre Exploration - Hudson Beat"), each byte-identical (cmp) to the folder copy. Folder 7.2 MB, nothing near 90 MB.
- **UPLOAD.md:** title 74 chars (<= 80); order follows TpT's form.
- **Deck:** speaker notes on all 19 slides (python-pptx); Class badge on each.
- **Banned content:** no "word for word"/"verbatim", no school or Blind Brook branding, no student names or work, no audio/video/lyrics/links; only Spotify/YouTube/Apple Music named as the owner's resource names them; no individual third-party author names (grep of PDF text, deck text, UPLOAD.md).
- **Owner's rubric:** /25 kept (5 x 1-5, average of student and teacher, page 19), text matches the Drive sheet. Kit tips labelled "Suggestions from this kit, not part of my rubric" (page 7) and "Kit suggestions, not part of my sheets" (page 4).
- **Drive verification (read-only):** "Genre Exploration - Project Sheet & Rubric" (Genre Exploration folder) really contains the reflection: goal 4 "Reflect on the creative process and what you learned", requirement 6 "Write a short reflection (1 paragraph minimum) on what you learned", step 6 "Write your reflection and finalize your bounce", checklist "Written reflection submitted via Google Classroom". So REFLECTION=False plus a prompt-only page is correct: no new task is added.
- **Reflection page (22):** states the owner's definition (a written or oral conversation about how you did on the project and what you would do differently next time), offers oral option, no points or rubric row, requirements unchanged. Disclosed on page 8 ("Reflection page, not a new task") and in the "New in this kit" paragraph; step 6 and the checklist point to it.
- **Invented additions disclosed on page 8:** worked example (invented genre "Harbor Drift", three invented references, on paper, no audio; 4+8+8+8+8+4+8+4 = 52 bars x 3 s at 80 BPM = 156 s = 2:36, checks), Loop and form sketch, Work plan, research sheet, reference log, Genre shortlist, vocabulary and presentation pages, Reflection prompts, deck. The name "Harbor Drift" itself appears only on page 11, not on page 8 (page 8 says "an invented genre"); acceptable.
- **Wording changes:** listed on page 8 and consistent with the owner's sheet (class page for LMS name, page numbers in steps, Form not included, pacing row split, layout-only rubric changes, deck shortenings).

Required fixes: none.

**Verdict: APPROVED**
