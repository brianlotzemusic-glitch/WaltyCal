# QA: Anti-Music Manifesto (TpT 019, DMP2, $10), 17 Oct 2026

Reviewer did not build this. git pull done on shop-factory; `gen.py --check` prints CHECK OK.

## Checks
- **Render review:** all 23 PDF pages, all 19 deck slides (PDF), cover, 3 preview PNGs and the 4-page preview PDF viewed. No overflow, clipping, empty pages or typos found. Page 18 (tips/checklist) is about half blank below a labelled Notes area, and the oral-reflection box on page 22 sits close to the footer: both are acceptable, not defects.
- **tpt.json:** grades 9th-12th (4); 1 subject; 1 tag; price and license_price $10.00; tax_code set; every file in `files` exists; pages 42 = 23 + 19 (PDF 23, deck PDF 19, preview 4 pages, pptx 19 slides).
- **ZIP:** exactly the 3 files listed in `zip_contents`, each byte-identical (cmp) to the folder copy. Folder is 6.5 MB, nothing near 90 MB.
- **UPLOAD.md:** title 76 chars (<= 80); description has the disclosure line; order follows TpT's form.
- **Deck:** speaker notes present on all 19 slides; each slide carries a Class badge.
- **Banned content:** no "word for word"/"verbatim", no school or Blind Brook branding, no student names, no audio/video/lyrics/links/screenshots (grep of PDF, deck and UPLOAD.md).
- **Owner's rubric:** /25 kept (5 categories x 1-5, average of student and teacher); kit tips are labelled "Suggestions from this kit, not part of my rubric" (pages 6-7) and "Kit suggestions, not part of my sheets" (page 4).
- **Reflection page (22):** defined as a written or oral conversation about how the student did and what they would do differently next time; adds no points or rubric row. Disclosed on the "What changed from the original" page (Wording changes and "Reflection added" section) and in UPLOAD.md section 9.
- **Invented additions:** the Rules page (three conventions drawn, six rule cards), the worked example ("Kitchen Table", an invented 50 s piece, numbers check: 10+18+8+14) and the sample artist statement are listed under "New in this kit" on the changes page. Marked as invented/on paper.
- **Artist names:** Tip 2 (John Cage, Merzbow, Aphex Twin, Death Grips) and the Cage 4'33" resource appear as names only, exactly as in the owner's notes, with no lyrics, audio or links. Acceptable. The deck names none. The owner question (keep or replace) is already logged in ACTION-LOG; it does not block approval.

Required fixes: none.

**Verdict: APPROVED**
