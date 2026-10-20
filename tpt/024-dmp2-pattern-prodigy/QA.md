# QA: Pattern Prodigy (TpT 024, DMP2, $10), 20 Oct 2026

Reviewer did not build this. shop-factory up to date; `gen.py --check` prints CHECK OK.

## Checks
- **Render review (low-res):** all 24 PDF pages and all 20 deck slides viewed as contact sheets, plus cover; sampled legible at 40 dpi. No overflow, clipping, empty pages or layout defects seen. Pages 7 and 10 have some bottom whitespace; not a defect.
- **Drive verification (read-only):** Projects (New) "Pattern Prodigy - Project Sheet & Rubric" and "Pattern Prodigy - Teacher Notes" compared with the PDF text. Overview, 4 goals, 5 vocabulary terms, 4 requirements, 7 steps, 4 tips, 6 checklist items, 4 struggles, Easier/More Advanced variations, 3 resources and the pacing guide all match. Rubric: 5 categories x 1-5 = /25, all cell text found in the PDF (average of student and teacher); the one "miss" was a hyphenated line wrap ("professional- quality mix"). The old Projects folder (2025 outline) was not used as a source.
- **Disclosed changes:** LMS name written "your class page"; invented additions (drum chart, "Night Shift" worked example, grids, trackers, quick reference) are labelled; Reflection page has no points and the rubric is untouched; grading tips labelled as suggestions. Worked example arithmetic (20 bars at 96 BPM = 50 s) checks.
- **tpt.json:** price and license_price $10.00; tax_code set; grades 9th-12th (4); 1 subject (Music); 1 tag (Autumn, proven value); every file exists; pages 44 = 24 + 20 (deck pptx 20 slides, deck PDF 20, preview PDF 4 pages).
- **ZIP:** exactly the 3 files in `zip_contents`, each byte-identical (cmp) to the folder copy, 1.2 MB. No audio or video.
- **Deck:** speaker notes on 20/20 slides; Class badge on each; no Blind Brook branding.
- **Banned content:** greps of PDF, deck and UPLOAD.md find no school branding, no individual third-party artist or album names (the Teacher Notes list no artists), no links, no audio/video/lyrics. YouTube appears only as the owner's resource titles, with "no video or link included". Only Apple, Logic Pro, Padlet named, as compatibility/product names. Disclosure line present.
- **UPLOAD.md:** title 72 chars (<= 80); follows form order; price $10 with rationale; disclosure line included.

Open owner questions (do not block): pre-built Logic drum project for the Easier variation; whether to ship the two older tutorial videos; which Step Sequencer features count beyond the suggested five.

Required fixes: none.

**Verdict: APPROVED**
