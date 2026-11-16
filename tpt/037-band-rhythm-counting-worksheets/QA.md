# QA: 037 Beginning Band Rhythm Counting Worksheets

## Findings
- `gen.py --check`: CHECK OK (120 exercises, 279 measures; PDF 34 pages, preview 4, fonts embedded, images 2000x2000).
- Independent recompute (own code, not gen.py's): all 279 measures sum to their meter; all written counts match (simple meters: 1 & 2 & ...; 6/8: 1-6). Hand-read samples: 5.4 and 6.4 (3/4, 2/4 with rests), 7.1 (dotted half, 3/4), 12.2 (eighth rests, 4/4), 13.1 (dotted quarter + eighth), 19.2 (2/4), 17.3, 20.3 and 20.4 (6/8, 3/4 mixed), plus visual cross-check of all key pages against the sheets. No errors.
- All 34 PDF pages and 4 preview pages rendered and viewed; notation (stems, beams, rests, dots, time signatures) correct; nothing clipped or overlapping; boxes align under notes.
- tpt.json: tags (Worksheets, Student Practice, Printables) and subjects (Music, Instrumental Music) are exact entries in the option files; 4 grades (5th-8th); all 6 files exist; price $5.
- UPLOAD.md: title is under 80 chars, disclosure line present (description and terms page), page counts (34 / 4 / 20) match, no seasonal or brand content. No tunes used (original rhythms), so no PD sourcing needed.
- Preview PDF pages are watermarked (diagonal PREVIEW); preview PNGs also carry it.
- Cosmetic, not blocking: preview-1.png watermark looks doubled/ghosted ("PPREVIEW"); preview-3.png has an empty bottom third; cover music block is left-heavy; preview-1 caption "Quarter and half notes" sits under worksheet 3 (half rests).

**Verdict: APPROVED**

## Fix round 16 Nov 2026
- Doubled "PREVIEW" watermark on preview-1/2 removed (second stamp drawn over page images already cut from the watermarked preview PDF).
- Cover: the notation block now spans the full art width (it sat left of centre with the right third empty); count labels in answer keys moved down 2 pt so quarter rests no longer touch their counts (cover line 1 bar 2, and all keys).
- P3: preview-3 cards made taller so the grid fills the image.
- Rebuilt; `gen.py --check` and `tools/tpt-validate.py` pass.
- Fresh Sonnet inspector: no real defects (single watermark, bars add up, no rest touching a count). Remarks left as is: first note near the 6/8 time signature in the downscaled preview-2 thumbnail only (the PDF page has a clear gap); quarter-rest-to-count gap tight but clear (about 5 px at 220 dpi).

**Verdict: APPROVED**
