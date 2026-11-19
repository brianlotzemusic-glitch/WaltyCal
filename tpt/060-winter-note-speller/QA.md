# QA: 060 Winter Note Speller (round 2)

Checks run: `gen.py --check` OK (64 words, 12 riddles, 388 notes read back from the drawn staves; keys equal worksheets; 20 PDF pages, preview 4); `tools/tpt-validate.py` OK; `git status --short` shows only the 060 folder (untracked) plus tpt/_art bookkeeping. PDF, previews and cover were rebuilt together (same timestamps as gen.py).
All 20 PDF pages rendered at 110 dpi and viewed; cover, preview-1..3 viewed at 2000 px; all 4 preview-PDF pages viewed (watermarked).

## Riddle re-read (pp 12-14 vs key p19), noteheads read by hand
1 FACE: notes F A C E; clue "coal eyes and a carrot nose on this part of his head" = face; gloss "the part of his head with the eyes and the nose" fits and no longer contradicts the clue.
2 FEED: F E E D; clue "scatter seeds ... to do this for them" = feed (the A-G word that fits); gloss "to give food to hungry birds, such as by scattering seeds" fits.
3 EGG: E G G. 4 BED: B E D. 5 BAG: B A G (bass). 6 CAFE: C A F E (bass; "without the accent mark"). 7 ACE: A C E. 8 FADE: F A D E. 9 BEAD: B E (ledger) D. 10 BADGE, 11 CABBAGE, 12 BAGGAGE: ledger notes read and match; `--check` recomputes all 12 from the staves.
Each clue is answerable only by its key word among A-G words; each gloss describes its answer; word spelled by the notes equals the key in all 12. Stems correct (up below middle line, down on/above).

## Rest of the product
Worksheet pages 4-11 (64 words), reference p3, teacher notes p2, p15 and p16 blank staves, answer keys pp 17-19 (spell-it notes FEE GAFFE EGGED DECADE CAGED DEFACE EFFACE CEDE correct), terms p20: unchanged in content, notation correct, nothing clipped or overlapping, page refs agree. Cover: clean, edges clear, counts (grades 3-6, 64 words, 12 riddles, 20 pages) agree. Previews 1-3 and preview PDF (pp 4, 10, 12, 17): clean, one watermark each, show the unchanged pages (preview-2 shows riddle 1 with the new key-consistent clue).
tpt.json: files exist, 20 pages, grades 3rd-6th, subjects and tags valid, price set. UPLOAD.md: title 75 chars, description (20 pages, 64 words, 12 riddles, section counts totalling 20) and disclosure line match the product.

## Notes (non-blocking)
- Some words are advanced for grade 3 (EFFACE, DEFACE, GAFFE, FACADE, ADAGE, DECAF); teacher notes position them for stronger readers.

**Verdict: APPROVED**

## Inspector 2026-11-19
Visual inspector (fresh agent, BLOCKING-only brief): after the one fix round (riddle key glosses for FACE and FEED reworded so they no longer contradict their clues; --check now prints and tests the 12 clue/gloss/answer triples) the inspector re-checked cover, preview-1..3, all 20 PDF pages and all 4 preview-PDF pages at full size: OK, no BLOCKING item. All 12 riddle notes, keys and glosses agree. NOTES (not changed): blank space at the bottom of some pages, advanced vocabulary (GAFFE, EFFACE, FACADE).
**Verdict: APPROVED**
