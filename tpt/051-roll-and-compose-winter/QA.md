# QA 051 Roll and Compose (round 2)

## Checks run
- `gen.py --check` and `tools/tpt-validate.py` pass. `git status --short` shows only `tpt/051-roll-and-compose-winter/` as new.
- All 16 pages rendered at 110 dpi and viewed. Crops at 260 dpi of p3, p4, p6, p8, p12 and p13. Viewed cover, preview-1/2/3 and all 4 preview-PDF pages.

## Round 1 defects: fixed
1. Eighth-pair symbols on p3, p4, p6, p8 and in preview-1 now show two filled heads, two stems and a thick visible beam. Level C rows 3 and 4 are correct (ti-ti inside ta ti-ti ta ta, and ti-ti ti-ti ta-a). Quarter and half symbols have full stems, none clipped.
2. Stem rule: the A4 A4 pairs now have stems up with the beam on top. This holds on the cover bar 1 and p12 Example B bar 1 (and bar 4). Pairs that mix sides also follow the rule. C5+C4 in Example C bar 3 has its stems up. Pairs on the one-line staff (on the line) have stems down with the beam below. All other pairs (C-G, E-D, D-G, G-A, E-C, E-C-A) have stems up.

## Re-verified
- Examples A, B and C recomputed from the printed rolls: rhythm, notes, letters and note counts all match. Every bar sums to 4 beats. The last-note rules hold (bar 4 is C in B, G in C; bar 8 is C). The rests are correct.
- Ledger lines are present on every C4 and absent elsewhere. C5 sits in the third space.
- Rubric: 5 rows x 4 = 20; bands 18-20 / 13-17 / 8-12 / 5-7.
- Preview PDF: 4 pages, one watermark per page. Thumbnails: the cover plus 3 previews, all clean.
- `tpt.json` (16 pages, 4 files) and `UPLOAD.md` (16 pages, 4 preview pages, thumbnails in order) agree. The page cross-references (4/5, 6/7, 8/9, 12, 13, 14, 15) are correct.

## Defects
None that a buyer would notice or that break a rule.

**Verdict: APPROVED**

Required fixes: none.

## Rescue 2026-11-18
Held rescue (step 2b): the BLOCKING item (dice clipped by their own SVG box on cover.png and the 5-dice banners of preview-1 and preview-3) was fixed in gen.py (die viewBox padded to 120, snowflake icons padded too; --check now renders each die and snowflake alone and fails if ink touches the render box or the padding is below the stroke width, and fails on ink at the top/side edges of the cover and previews). Content unchanged. Fresh Visual inspector re-checked cover, preview-1..3, all 16 PDF pages and 4 preview-PDF pages at full size (crops at ~280 dpi): OK, no BLOCKING item; beamed eighth pairs and A4 A4 stems-up unchanged. NOTES (not changed): thin E4 stem on p3, watermark crosses content as intended.
**Verdict: APPROVED**
