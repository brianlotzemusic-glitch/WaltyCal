# QA: 091 Year-Long Music Sub Plans Bundle

Independent review. `gen.py --check` and `tools/tpt-validate.py` OK before and after my fix.

## Recomputed myself (own script: each member's tpt.json, UPLOAD.md, QA.md, PDF)
- 12 members in school-year order (088, 084, 085, 086, 073, 075, 077, 078, 079, 081, 082, 089), each with a `release` file, each own QA.md verdict APPROVED (uploader will not skip any), each $15.00 (sum $180.00), each 48 pages (pdfinfo) and 16 student sheets.
- Bundle $149.00; saving $31.00 = 17.22%; chip "SAVE 17%" (rounded down, never up). 576 member pages + 4 guide = 580; 96 days; 192 sheets.
- Numbered list in UPLOAD.md and the guide (table, calendar): 1-12 complete, in order, themes character-for-character the same as each member's own UPLOAD.md title; no invented theme.
- ZIP unzipped into a fresh /tmp dir: guide + 12 folders 01-August .. 12-July, one PDF each, 13 files, all 12 PDFs sha256-identical to the member folders' PDFs, clean names, no work files, 22.1 MB (21.1 MiB), well under 100 MB. Guide 4 pp, preview PDF 4 pp with one PREVIEW watermark per page.
- Listing: title 76 chars, no month/season word ("Year-Long" fine). Price "149.00"; subject Music; 4 grades; tags Back to School, Printables, Worksheets, Activities, Summer, Winter each checked individually as exact non-heading entries of TAG-OPTIONS.json. No bundle marker field is needed: tpt.js only treats a `tpt-bundle` FILE (written after a hand upgrade on TpT, as for 030) as state; 074 has none and validate.py requires none for a ZIP bundle. No mismatch.
- Description: buyer's problem first, numbered members with grade and page count, dollar saving, "also sold separately", US spelling, full sentences, disclosure line present.
- Honesty of price: clearly stated as $180.00 sum vs $149.00, "save $31.00, 17.2%" everywhere; no 30-35% claim anywhere (the Standard closing "save 30%" line is correctly not used). The factory's 30-35% rule is waived by the owner price; fine.

## Defect found and fixed in gen.py
1. Guide credits and the UPLOAD description said facts are "sourced in that month's own notes", but the member PDFs contain no sources (the SOURCES.md files are not in the ZIP); the description line was also self-contradictory. Reworded to "short and drawn from standard reference works; no lyrics or speeches are quoted". 
2. preview-3 subtitle said "plan page"; the pages shown are Day 2 K-2 student sheets. Now "One day-2 student sheet from eight of the 12 months".

## Viewed
Guide pages 1-4 at 110 dpi; the 4 preview-PDF pages (guide 1, guide 2, October and February student sheets, one watermark each); cover.png (all edges clean; 12 tiles readable and uncropped, 12 MONTHS - 96 DAYS bar, SAVE 17% chip, blue accent matches the calendar hero); preview-1, -2, -3 at full size. No notation in the art. Cosmetic only: empty space below the content on preview-2/-3 and on guide pages 1-3.

**Verdict: APPROVED**
