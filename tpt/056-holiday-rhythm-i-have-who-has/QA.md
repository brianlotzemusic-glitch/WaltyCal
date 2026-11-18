# QA 056 Holiday Rhythm: I Have, Who Has

## Findings
- `gen.py --check` OK; `tools/tpt-validate.py` OK; git status: only the 056 folder plus tpt/_art bookkeeping.
- Rendered all 13 pages at 110 dpi, cover plus 3 preview PNGs at full size, all 4 preview-PDF pages; Level 2 cards cropped at 250 dpi.
- Level 1 (24 cards): read each I-have from notation (note values, rests, single-beam eighth pairs, stems up); every bar = 4 beats; syllables match the notation. Every Who-has prompt matches exactly one card. Chain 1,13,18,15,24,6,2,17,12,23,22,16,7,8,10,19,21,3,5,4,11,14,20,9, back to 1 = 24 steps, all cards once. START on 1, END on 9. Key matches. Only quarters, quarter rests, eighth pairs, half notes.
- Level 2 (24 cards): each bar = 4 beats; double beams on sixteenths; ti-ti-ka (secondary beam on right pair) and ti-ka-ti (left pair) drawn correctly and spoken correctly; prompts each match one card; chain 1,13,3,15,20,6,10,24,23,8,17,4,11,9,22,19,18,5,14,16,21,12,7,2, back to 1 = 24 steps. START 1, END 2. Key matches. All 24 rhythms distinct in each game.
- Syllables guide correct (ta, shh, ti-ti, ta-a, ti-ka-ti-ka, ti-ti-ka, ti-ka-ti; Try It examples add to 4). Teacher notes and how-to-play are complete sentences, grade 2-5 fit, US spelling, non-denominational art (star, ornament, tree, snowflake, bow and holly), no internal QA wording; disclosure line present.
- Cut lines clear of content. Page and card counts agree everywhere (13 pages, 48 cards, page refs 5-7, 8, 9-11, 12, 13). Cover edges clean; previews watermarked and clean.
- tpt.json: grades 2-5, subject Music, tags Winter/Games/Activities/Printables/Centers all exact in options files; files exist. UPLOAD.md: title 72 chars, no seasonal words, page list totals 13.
- Notes (non-blocking): preview-1 caption "Eight cards a page, cut lines, START marker" wraps to two lines; some blank space on preview images 2-3 between header and pages.

**Verdict: APPROVED**

## Inspector 2026-11-18
Visual inspector (fresh agent, BLOCKING-only brief): OK, no BLOCKING item. Viewed cover, preview-1..3, all 13 PDF pages, all 4 preview-PDF pages and 250 dpi crops of Level 2 cards at full size; read cards from the notation (bar sums, syllables, prompts, loops closing L1 9 to 1 and L2 2 to 1). NOTES (not changed): preview-1 caption wraps onto two lines, last notehead of L2 cards 16 and 21 about 15-20px (at 250 dpi) from the final barline, dense Teacher Notes page, blank lower thirds on pp8, 12, 13.
**Verdict: APPROVED**
