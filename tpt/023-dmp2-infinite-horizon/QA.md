# QA: Infinite Horizon (TpT 023, DMP2, $10), 19 Oct 2026

Reviewer did not build this. git pull done on shop-factory; `gen.py --check` prints CHECK OK.

## Checks
- **Render review:** all 23 PDF pages, all 20 deck slides (PDF), the cover, 3 preview PNGs and the 4-page preview PDF viewed. No overflow, clipping, empty pages or typos found. The hero drawing's rings are whole (cover, slide 1, closing slide): the clipping fix is confirmed. Slide 1's black banner sits on one line. Notes only: slide 11 (Automate everything) has bottom whitespace under the diagram, as expected; page 18 (tips and checklist) is about half empty, and pages 10 and 15 end with some room; none is a defect.
- **tpt.json:** grades 9th-12th (4); 1 subject (Music); 1 tag (Autumn, proven value per METADATA-GUIDE); price and license_price $10.00; tax_code set; every file in `files` exists; pages 43 = 23 + 20 (PDF 23, deck PDF 20, pptx 20 slides, preview PDF 4).
- **ZIP:** exactly the 3 files in `zip_contents` (in "Infinite Horizon - Hudson Beat"), each byte-identical (cmp) to the folder copy. Nothing near 90 MB (ZIP 1.0 MB).
- **UPLOAD.md:** title 72 chars (<= 80); order follows TpT's form.
- **Deck:** speaker notes on all 20 slides (python-pptx); Class badge on each.
- **Banned content:** no "word for word"/"verbatim", no school or Blind Brook branding, no student names or work, no audio/video/lyrics/links; no individual third-party artist or album names (grep of PDF text, deck text, UPLOAD.md; the Teacher Notes' album and three artists are left out and the "What changed" page says so). Only Apple, Logic Pro, Padlet and Alchemy named as product names.
- **Owner's rubric:** /25 kept (5 x 1-5, average of student and teacher, page 19); text matches the Drive sheet. Kit tips labelled "Suggestions from this kit, not part of my rubric" (page 7) and "Kit suggestions, not part of my sheets" (page 4). Owner's overview, goals, vocabulary, requirements, steps, tips and checklist match the Drive sheet (LMS name changed to "your class page", disclosed).
- **Drive verification (read-only):** "Infinite Horizon - Project Sheet & Rubric" (Projects (New) > Infinite Horizon) has no reflection goal, requirement, step or checklist item. Only the rubric's Documentation & Presentation row says "reflection". So the Designer's reading is correct: the kit adds a prompt-only page, not a new rubric requirement.
- **Reflection page (22):** states the owner's definition (a written or oral conversation about how you did on the project and what you would do differently next time), offers written or oral, no points or rubric row, requirements unchanged. Disclosed on page 7 ("Reflection, added by this kit"), page 8 ("Reflection added" in Wording changes and "New in this kit") and in UPLOAD.md.
- **Invented additions disclosed on page 8 ("New in this kit"):** worked example (invented 75-second piece, on paper; 12+33+18+12 = 75 s checks), starter-template recipe and Harder variation page, Listening log, Phase plan, Automation plan, Listen-back sheet, quick reference, vocabulary and presentation pages, deck, suggested minimum of three lanes. The name "Slow Tide" appears only on page 11 and in the deck notes, not on page 8 (page 8 says "an invented 75-second piece"); acceptable.
- **Wording changes:** listed on page 8 and consistent with the owner's sheet.

Required fixes: none.

**Verdict: APPROVED**
