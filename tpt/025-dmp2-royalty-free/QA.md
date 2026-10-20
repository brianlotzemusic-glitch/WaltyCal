# QA: Royalty Free (TpT 025, DMP2, $10), 20 Oct 2026

Reviewer did not build this. shop-factory up to date; `gen.py --check` prints CHECK OK.

## Checks
- **Render review (low-res, 30 dpi contact sheets):** all 25 PDF pages and all 19 slides, plus cover and the 3 preview PNGs. No overflow, clipping, empty pages or layout defects seen. Fonts Oswald and Source Sans 3, all embedded. Letter size.
- **Drive verification (read-only):** Projects (New) "Royalty Free - Project Sheet & Rubric" and "Royalty Free - Teacher Notes" compared with the PDF text. Overview, 4 goals, 4 vocabulary terms, 6 requirements, 7 steps (incl. Padlet step), 4 tips, 6 checklist items, struggles, Easier/More Advanced variations, resources and the 7-class pacing guide all match. Rubric: 5 categories x 1-5 = /25, all 25 cell texts found in the PDF (one only differs by a hyphenated line wrap, "professional- quality mix"); average of student and teacher kept. Old Projects outline (2025) not used as a source.
- **Word list:** "Groups of Words" sheet (16 groups x 10 = 160 words) compared word for word: all 160 present, spellings kept (Mesmerizing/Mesmerising, Wonderous).
- **Reflection handling:** correct. The sheet already requires a reflection paragraph (requirement 6, step 5, checklist), so the shared Reflection element is off (as in 022). The Reflection planner page adds no task, no points and no rubric row; rubric untouched.
- **Disclosed changes:** LMS name written "your class page", tip 4 "a free music library" (BenSound removed), both listed on "What changed". Invented additions (worked example "Open Doors", templates, hit-point sheet, planners, quick reference) are labelled. Worked example arithmetic passes (30 bars at 120 BPM = 60 s). Grading tips labelled as suggestions.
- **tpt.json:** price and license_price $10.00; tax_code set; 4 grades (9th-12th); 1 subject; 1 tag (Autumn, proven value); every file exists; pages 44 = 25 + 19; deck 19 slides with speaker notes on 19/19 (python-pptx); deck PDF 19 pages; preview PDF 4 pages.
- **ZIP:** exactly the 3 files in `zip_contents`, each byte-identical (cmp) to the folder copy, 1.3 MB. No audio or video.
- **Banned content:** greps of PDF, deck text and UPLOAD.md find no school branding, no third-party artist or album names, no links, no audio/video/lyrics. YouTube appears only as a place to find royalty-free music. Only Apple, Logic Pro, Padlet named, as compatibility/product names. Disclosure line present.
- **UPLOAD.md:** title 69 chars (<= 80); follows form order; price $10 with rationale; disclosure line included; owner questions listed.

Minor, not blocking: UPLOAD.md says Class 6 includes writing the 3 Padlet questions, which the owner's pacing line ("Final bounce. Prepare presentations") does not state; it is consistent with step 7 and the PDF labels it as such.

Open owner questions (do not block): whether the Groups of Words list has changed or its 16 groups matter; whether the sources doc / site names should ship; a shareable district video for a later version; the owner's own test for the Apple Loops rule.

Required fixes: none.

**Verdict: APPROVED**
