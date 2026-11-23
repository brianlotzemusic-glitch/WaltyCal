# QA: 074 Winter Music Mega Bundle

Independent review. `gen.py --check` passed before and after my fixes; `tools/tpt-validate.py` OK.

## Recomputed myself (own script, reading each member's tpt.json, UPLOAD.md and PDF)
- 23 members present, each with a `release` file; each PDF's page count equals its tpt.json and `pdfinfo`.
- Sum of prices $95.25; bundle $62.00; saving $33.25 = 34.908%; ribbon "SAVE 34%" (rounded down) on cover; 612 member pages + 4 guide = 616.
- Numbered list in UPLOAD.md and the guide: 1 to 23, complete, same titles, grades and page counts as the member files; page list sums to 616.
- ZIP unzipped into a fresh temp dir: 24 files, 23 member PDFs byte-identical (sha256) to the member folders' product PDFs, clean folder names, no work files, 18.1 MiB (20.1 MB decimal).
- Each member's UPLOAD.md lists exactly one customer file (the PDF); no deck or zip is omitted.
- Tags (Winter, Christmas-Chanukah-Kwanzaa, Printables, Activities, Worksheets, Games) and subjects (Music, Instrumental Music, Music Composition) are each exact entries of TAG-OPTIONS.json / SUBJECT-OPTIONS.json; "Audience" and "Seasonal" are the headings and are not used. Grades: 4 entries.

## Defects found and fixed in gen.py
1. Title was seasonal ("Winter Music Mega Bundle | ..."), at risk of TpT's Seasonal Titles block (as 027). Now `Music Mega Bundle | 23 Resources: Rhythm, Color by Note, Games | Gr K-6` (71 characters). UPLOAD.md and the check updated; winter stays in tags, description and cover art. STYLE.md has no rule against seasonal cover text, so the cover and guide keep "WINTER MUSIC".
2. Grade honesty: the description and guide said "two stretch to grade 8 and grade 12", but three members go beyond elementary. Now names 005 (K-8), 059 (3-8) and 046 (4-12, band, choir, orchestra). Description and guide intro now say "mostly for elementary". UPLOAD.md section 3 explains the four grade boxes (K, 2, 4, 6) against the real span.

## Viewed
Guide pages 1-4 at 110 dpi; the 4 preview-PDF pages (guide, resource list, Bingo page 37, Bell Ringers day 9, one PREVIEW watermark each); cover.png (all four edges clean, 23 member covers readable, "23 RESOURCES" callout, SAVE 34% ribbon, $33.25); preview-1, -2, -3 at full size. No mangled collage tiles. Minor: preview-2 has empty space below the page mockups (cosmetic).

## Questions for the owner
- 046 Winter Concert Reflection (band, choir, orchestra, grades 4-12) and 005/059 (to grade 8) are not strictly elementary; kept because the queue lists them and the description says so. Should 046 stay in an "elementary" bundle?
- TPT-FACTORY.md "Bundles" still gives "Winter Music Mega Bundle | ..." as the title example; update it to a non-seasonal title.

**Verdict: APPROVED**
