# QA: 035 Hanukkah Color by Note

- `python3 gen.py --check`: CHECK OK (27 worksheets, 27 keys, 255 regions, 358 symbols, 58 pages, preview 4 pages, fonts embedded, images 2000x2000).
- Rendered all 58 pages, 4 preview pages, cover and 3 thumbnails. Nothing clipped, overlapping, blank or unreadably small. Preview is watermarked. Cover reads at thumbnail size.
- Answer keys recomputed independently (own pitch-to-staff-step math: treble bottom line E4, bass bottom line G2; ledger lines at C4, A5, bass C4): 358 symbols, 0 mismatches between symbol class, key colour and region colour. Stem direction and ledger lines correct. Rhythm glyphs match names (whole, half, quarter, eighth, quarter rest). Key colours visually match the answer-key pages. Note-name reference staffs (treble C4-A5, bass E2-C4) are correct.
- Imagery: menorahs on pages 4, 9, 12 (and B/C equivalents) have 9 candles with the shamash raised and centred; dreidel, Star of David, oil lamp with olive leaves, star garland and medallion. No Christmas symbols found. Respectful and accurate.
- No tunes or lyrics, so no public-domain issue. No brands or characters.
- tpt.json: grades 4 entries (same format as 032), subject Music is in SUBJECT-OPTIONS, tags "Christmas-Chanukah-Kwanzaa" and "Winter" are exact entries in TAG-OPTIONS. All 6 listed files exist. Pages 58 matches the PDF.
- UPLOAD.md: title is 78 characters (<=80). Disclosure line is present in the description and on the terms page. Counts match (58 pages: 1 cover, teacher notes, reference, 27 worksheets, 27 keys, terms; 4 preview pages). Price $3.50 in range.
- Minor, not blocking: preview footers show full-product page numbers and "answer key on page N" references to pages not in the preview.

**Verdict: APPROVED**
