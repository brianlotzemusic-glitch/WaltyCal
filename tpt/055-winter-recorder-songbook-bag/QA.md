# QA 055 Winter Recorder Songbook (B-A-G): independent re-review after breath-hint rebuild

Checks run: `gen.py --check` CHECK OK; `tools/tpt-validate.py` OK; `git status --short` shows only expected modified files (gen.py, build/*, previews, both PDFs). All 13 product pages rendered at 110 dpi and viewed; cover (four edges clean, no clipping), preview-1..3 at full size, and all 4 preview-PDF pages (pp. 3, 4, 7, 12, one watermark each) viewed.

## Breath hints, read from the notated bars (bar lines visible, counted from bar 1)
- T1 Snow Settles, "after bar 2": bar 2 = B half, A half. Ends on half note. OK. (4 bars.)
- T2 Mitten Walk, "after bars 3 and 6": bar 3 = B, rest, A, rest; bar 6 = G A B rest. Both end on a quarter rest. OK.
- T3 Au Clair, "one breath, or after bar 2, on the half note": bar 2 = B half, A half. OK. Tune has 4 bars, so "four bars" is right.
- T4 Frosty Window (3/4), "after bars 4 and 8, quarter rest": bar 4 = A half + rest; bar 8 = G half + rest. OK.
- T5 Icicle Steps, "after bars 3 and 6, half note": bar 3 = A q, G q, G half; bar 6 = A q, A q, B half. OK.
- T6 Cocoa Break, "after bars 3 and 6, quarter rest": bar 3 = B rest A rest; bar 6 = B rest B rest. OK.
- T7 Hot Cross Buns, "after bars 2 and 4, half notes; bar 3 ends on an eighth": bars 2 and 4 end on G half; bar 3 is the eight eighths. OK and accurate.
- T8 Skating Pond, "after bars 2 and 4, half note and quarter rest": bar 2 ends G half; bar 4 = B half, A q, rest. OK.
- Every one of the 8 tunes has a Breath line, each on the correct tune's card. The cover/preview-3 claim "breath hints on every tune" is true. No "before bar" wording.

## Other checks
- p2 weekly plan: Week 3 reads "Breathe only after bars that end on a rest or half note" (T5/T6 hints agree). Weeks 1, 2, 4 page refs (4, 5, 6, 7, 10-11) match the pages. Page lists on p2, p9, p13 agree.
- Tune note names, answer-key note strings for tunes 5-8, quiz 1/2 answers and key: unchanged and consistent (notes only B, A, G; stems correct; bars add up).
- Hot Cross Buns credit (in print by 1733) and Au Clair credit ("Traditional French tune, 18th century, composer unknown") present on tune cards, p13 and UPLOAD.md.
- Page counts: PDF 13, preview 4; UPLOAD.md, tpt.json, cover band, preview-1 band all say 13. UPLOAD.md preview page list matches the preview PDF. tpt.json files, grades, subjects, tags, price valid (validator OK). Title 77 characters, no seasonal word.
- Visual: no clipping, overlap or blank areas found on any page or image. Minor note only: preview-3 shows Quiz 1 which the caption names correctly.

**Verdict: APPROVED**

Required fixes: none.

## Rescue 2026-11-18
Held rescue (step 2b): the BLOCKING items (breath hints contradicting the music on p7 tune 8, p6 tune 5 and the p2 Week 3 text) were fixed in gen.py: every tune has a breath_after list from which its hint is built (T1 bar 2; T2 bars 3, 6; T3 bar 2; T4 bars 4, 8; T5 bars 3, 6; T6 bars 3, 6; T7 bars 2, 4; T8 bars 2, 4), Week 3 now reads 'Breathe only after bars that end on a rest or half note', and --check verifies every hint bar ends on a half note, whole note or rest (also tune 7's 'before bar 3 and 4' fixed). Notation and keys unchanged. QA re-checked every tune: APPROVED. Fresh Visual inspector re-checked cover, preview-1..3, all 13 pages and 4 preview-PDF pages at full size (250 dpi crops of fingerings and every staff): OK, no BLOCKING item. NOTES (not changed): watermark crosses content on thumbnails as intended, blank space at the bottom of p9 and p13.
**Verdict: APPROVED**
