# QA 055 Winter Recorder Songbook (B-A-G), round 2

Checked: `gen.py --check` CHECK OK (13 pages, preview 4, 2000x2000 images); `tpt-validate.py` OK; git status shows only this folder as new plus unrelated `_art` moves.

- Looked at all 13 PDF pages at 110 dpi, cover, preview-1..3 and all 4 preview-PDF pages. No clipping, overlap, blank page or collision. Cover edges clean (black band bottom, no cut art).
- Notation: stems, heads, beams, rests and bar sums right on every tune and quiz staff; Au Clair first phrase G G G A | B A | G B A A | G; Hot Cross Buns B A G | B A G | eighths | B A G.
- Answer keys recomputed from the images: quiz 1 (1-12 notes, 13-18 fingerings A G B G A B), quiz 2 drawn notes and step/skip/repeat, tune 5-8 note names all match. Fingering diagrams B/A/G correct hole by hole, repeated correctly in quiz.
- Cross-references (pages 3, 4-7, 8, 9, 10-11, 12, 13) all correct. Page list in UPLOAD.md totals 13.
- Provenance: grep of both PDFs, UPLOAD.md, tpt.json finds no "Voitures", "Herold" or "Lully". Remaining claims: Hot Cross Buns "traditional English street cry, in print by 1733" (Poor Robin's Almanack 1733, matches the source) and Au Clair "traditional French tune, 18th century, composer unknown" (safe, generic). Nothing else unverifiable.
- Listing: title 77 chars, no seasonal word; description 13 pages, disclosure line present; tpt.json pages 13, subjects/tags as listed, files exist.
- Non-blocking note: tune 8 breath hint says breathe after bar 6 "on the half note or the rest", but bar 6 ends on a quarter note.

**Verdict: APPROVED**

Required fixes: none.
