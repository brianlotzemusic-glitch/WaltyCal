# QA: 058 Tempo & Dynamics Anchor Charts

Checks run
- `python3 gen.py --check`: CHECK OK. `tools/tpt-validate.py`: OK. `git status --short`: only `tpt/_art/USAGE.md` (bookkeeping) and the 058 folder.
- Viewed all 19 PDF pages at 110 dpi, the cover and 3 preview PNGs at full size, all 4 PREVIEW.pdf pages; reference-sheet hairpins/symbols cropped at 250 dpi.

Content
- Terms, spelling, abbreviations and meanings all correct (pp very soft ... ff very loud; cresc.; decresc./dim.; accel.; rit.; largo very slow, adagio slow, andante walking pace, moderato moderate, allegro fast, presto very fast).
- Hairpins: crescendo opens to the right, decrescendo/diminuendo closes (posters 7 and 8, reference sheet, quiz Q5). Correct. Dynamic glyphs (Bravura) render cleanly and read as pp, p, mp, mf, f, ff everywhere.
- BPM ranges (largo 40-60, adagio 66-76, andante 76-108, moderato 108-120, allegro 120-156, presto 168-200) match common published tables (MasterClass, Skoove, Simple Wikipedia); sources vary and the text says so ("About", "common ranges", "books, teachers and conductors use slightly different numbers", teacher-notes paragraph). Gaps (60-66, 156-168) and shared endpoints (76, 120) are covered by that hedge; no false claim is made.
- Quiz: every question has exactly one correct answer. Key recomputed: Q1 E D F A B C, Q2 C B E A F D, Q3 B, Q4 D, Q5 A, Q6 B, Q7 4 1 6 2 5 3, Q8 6 2 5 1 4 3, Q9 D, Q10 C. Points 6+6+1x6+1+1 = 20. Matches the key.
- Counts agree everywhere: 12 posters, 10 questions, 20 points, 19 pages (cover, UPLOAD.md, tpt.json, terms page, previews).
- Grades: cover and listing say 2-8; content (plain-word meanings, symbols plus BPM and abbreviations, differentiation notes for 2-4 and 5-8) fits. tpt.json lists 3rd-6th and UPLOAD.md section 3 explains the four-grade limit. Fine.
- Wording is age-appropriate, US spelling, complete sentences, no internal QA wording; disclosure line present on the terms page and in the description.
- Layout: posters readable at distance, safe margins, nothing clipped or overlapping. Preview PDF is watermarked on all 4 pages; cover and previews are 2000x2000 with clear edges.
- UPLOAD.md: title 76 chars, no seasonal words, page list totals 19. tpt.json files exist; subjects and tags are non-heading entries.

Notes (non-blocking)
- Poster 8 body text is 4 lines, a little long for a 2nd grader; the heading and "GRADUALLY SOFTER" band carry the meaning.
- The reference-sheet hairpins are slightly uneven in length; fine at print size.

**Verdict: APPROVED**

## Inspector 2026-11-18
Visual inspector (fresh agent, BLOCKING-only brief): OK, no BLOCKING item. Viewed cover (four edges), preview-1..3, all 19 PDF pages and all 4 preview-PDF pages at full size; hairpin directions, definitions, BPM ranges ('about', common ranges), quiz key (20 points) checked. NOTES (not changed): the PREVIEW watermark crosses the adagio gauge and highlighted scale pills, poster 10 title wraps to two lines.
**Verdict: APPROVED**
