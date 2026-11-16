# QA: 050 Solfege Snowball Melody Cards (round 2, independent)

Checks: `gen.py --check` OK; `tools/tpt-validate.py` OK; `git status --short` shows only the 050 folder new. Product PDF (19 pages) rendered at 110 dpi; preview PDF 4 pages rendered; cover and preview-1/2/3 viewed at full size.

## Findings
- Round-1 defect fixed: preview-1.png decoration row now reads snowball, flake, snowball, flake, snowball, flake, snowball, flake, snowball. It ends on a whole snowball and nothing is clipped.
- No regressions after the rebuild. Sampled A1-A4, B5, C1-C4, C3, D1-D4, D7 and sample mats 1-2: noteheads match syllables (C4 ledger = do, D4 = re, E4 = mi, G4 = sol, A4 = la), stems up and attached right, beams correct, quarter rests, every bar 4 beats, treble clef and 4/4 on every card. Answer key pp16-17 matches the drawn cards on all sampled rows. Rhythm slot cards R1-R12 (p15) sum to 4 and the bank table (p18) is correct.
- Cover, preview-1/2/3: no overlaps, no clipped art or text, text readable at thumbnail size, counts (32 patterns, 19 pages, 4 sets) match the product. Preview art notation (cover staff, A2, B5, C3, D7) is correct.
- Preview PDF: 4 pages, watermark once per page (checked by `--check` and visible on the images).
- UPLOAD.md and tpt.json are consistent: 19 pages, 4 thumbnails plus preview file present, title "Pentatonic Melody Cards: Solfege Read & Sing Patterns, Music Gr 2-4" is under 80 characters and has no seasonal words, grades 2nd-4th, subjects and tags valid per the validator, price $4.00.
- Tunes: original patterns, no known tunes (checked in round 1). No brands or characters.

No defects found.

**Verdict: APPROVED**
