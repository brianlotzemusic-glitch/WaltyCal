# QA: 065 Key Signature & Scale Worksheets for Band

## Findings
- `gen.py --check` passes. I recomputed every transposition independently on the line of fifths (Bb +M2, Eb +M6, F +P5, folded by 12 past 7 sharps/flats). The charts (pp. 10-12), Worksheets 6-11 keys, quiz key and all asterisk cases (F#/Bb-inst, B and F#/Eb-inst, C#/F-inst not used) match. Circle of fifths, sharps/flats order, 12-key list and 7-accidental limit correct.
- Totals recounted: score sheet 12+15+12+12+12+60+18+20 = 161; quiz 4+4+2+2+8 = 20.
- Notation viewed on all 32 pages, the 4 preview-PDF pages, cover and preview-1..3: clefs, key-signature accidental positions (treble and bass), scale notes/accidentals, stems, ledger lines and 4 quarter notes per bar are correct.
- Facts: trombone, flute, oboe, bassoon, tuba are C instruments; tenor sax and bass clarinet a 9th below; baritone sax an octave plus M6. Correct.
- Listing: title 78 characters, no seasonal words; tags and subjects are exact non-heading entries; 4 grades; disclosure line present; UPLOAD.md page counts total 32 and match the PDF; tpt-validate OK.

## Defects found and fixed in gen.py
1. Grammar: "These instruments sounds ..." on the three chart pages and "B-flat instruments sounds ..." in the Remember boxes on Worksheets 6-8. Fixed to "sound".
2. Pacing plan: sessions 8 and 9 each cover two worksheets but listed one student page (21, 23), so Worksheets 8 and 10 were never referenced; session 7 text claimed B-flat and E-flat although Worksheet 6 is session 6. Fixed (pages 20-21, 22-23; wording) and the --check cross-reference test updated to match.
3. Grade guide: teacher notes listed Worksheet 6 under grades 8-9 while UPLOAD.md did not. Teacher notes now agree with UPLOAD.md.

**Verdict: APPROVED**
