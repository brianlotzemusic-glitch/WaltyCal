# QA: 050 Solfege Snowball Melody Cards (independent re-review after rescue)

## Checks run
- `python3 gen.py --check`: CHECK OK (32 cards, notehead/syllable mapping C=do D=re E=mi G=sol A=la, bar sums, sets, key, slot cards, sample mats, layout, 19/4 pages, UPLOAD.md and tpt.json).
- `tools/tpt-validate.py`: OK. `git status --short`: only this folder's build/, cover.png, preview-1.png, gen.py and the two PDFs modified (expected for the rescue); no stray files.
- Page counts: product PDF 19, PREVIEW PDF 4 (one watermark each); UPLOAD.md says 19 / 4, cover says 19 pages and 32 patterns; section page counts total 19; tpt.json consistent.

## Visuals (110 dpi, all 19 pages and 4 preview pages; cover, preview-1..3 at full size)
- Cover and PDF p1: snow hill now ends inside the canvas with rounded outlined ends on both sides; snowman and snowball pile sit on it; nothing clipped on any of the four edges. Cover notation (la re sol re do | mi re mi sol | do rest re) has attached stems, correct beams and a rest; syllables match.
- Mats p13/p14 (and preview-1 and PREVIEW p3): the four dashed BAR boxes have a visible gutter, text fits inside the boxes, and the boxes sit over their bars. Nothing overlaps.
- p15: 12 slot cards in a clean 2-column grid, labels and rhythms legible, nothing clipped.
- pp1-12, 16-19 and the other previews: no clipping, overlaps or blank pages.

## Theory and numbers verified
- p3 Snow tip: mi to re = step (adjacent degrees); mi to sol = minor third = skip (the E to G gap in C pentatonic); do to mi = major third = skip; do to sol = a fifth = leap (larger than a third). All correct. Also G to A is a step and A to C is a minor third.
- Singing range: C4 to A4 is a sixth (C D E F G A) and E4 to A4 is a fourth. The teacher notes say "a range of a sixth", which is correct. The "start do a step higher on D4" tip is fine.
- Fit of slot cards: the cards are 215 wide and the BAR boxes 223 wide, so each card fits with about 4 pt of slack per side. Heights fit as well (about 69 pt of card in a 77 pt box, checked from the render and by the --check assertions). The 12 slot rhythms sum to 4 beats each; the p18 bank-check table agrees.
- Sample mats (p18) are unchanged and correct: Mat 1 uses R1, R10, R6, R2 (mi sol mi mi | mi rest mi | mi mi mi sol la | la mi mi); Mat 2 uses R4, R6, R8, R11 (do sol | re do do sol mi | la sol mi rest | la sol sol do). Key pp16-17 is unchanged and matches the cards. Cross-references (cards pp4-11, tracker p12, mats pp13-14, slots p15, key pp16-17, sample mats p18) are all correct.

## Findings
- No blocking issues.
- Notes only: the header snowball icons sit close to the title text on key and tracker pages (touching-free); fine.

**Verdict: APPROVED**

## Rescue 2026-11-18
Held rescue (step 2b): the BLOCKING items were fixed in gen.py: snow hill now ends inside the canvas with rounded outlined ends (cover, p1), BAR boxes on mats p13/p14, preview-1 and PREVIEW p3 have a 12pt gutter (the old boxes were narrower than the cut-out cards, so the cards could not fit; cards are now 215 wide in 223x78 boxes), p3 Snow tip reworded (step: mi to re; skip: mi to sol or do to mi; leap: do to sol; --check asserts it). QA re-checked everything: APPROVED. Fresh Visual inspector re-checked cover, preview-1..3, all 19 pages and 4 preview-PDF pages: OK, no BLOCKING item. NOTES (not changed): cover staff's last bar has no closing barline, mat dashed boxes narrower than their bars, p16/17 title row tight against the icon row, blank space at the bottom of p15-17.
**Verdict: APPROVED**
