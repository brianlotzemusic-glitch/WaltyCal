# QA: 043 Note Naming Speed Drills

## Findings
- `gen.py --check` passes (43 pages, 900 key entries matched, 954 notes recomputed from geometry). `tools/tpt-validate.py` OK.
- Looked at all 43 pages (contact sheets), cover, 3 preview PNGs and the 4-page preview PDF. Nothing clipped, nothing behind footers, one watermark per preview page, cover legible at thumbnail size.
- Independent read-off from rendered pages vs key: treble 1, 9 (sharps, ledger lines); bass 5, 9 (sharps/flats, two ledger lines above); alto 2, 5, 8, 9 (spaces, ledger lines, accidentals). All matched, including accidentals (key letter and sharp/flat match the drawn symbol, accidental sits before the note). Treble/bass/alto line and space facts agree with the brief's corrected values.
- Alto clef glyph is a proper C clef centred on the middle line; middle C placement on the clef reference page is on the middle line.
- tpt.json: grades 5th-8th (4 entries), subjects Music and Instrumental Music, tags Worksheets, Printables, Activities, Bell Ringers (all in the option lists, non-heading), pages 43, files exist.
- UPLOAD.md: title 73 chars, disclosure line present (description and terms page), page list totals 43. Description says grades 3-8 while TpT grades are 5-8; UPLOAD.md states the form limit of four, so it is clearly worded. Minor, not a reject.
- No tunes, lyrics, brands or characters.

**Verdict: APPROVED**

Required fixes: none.
