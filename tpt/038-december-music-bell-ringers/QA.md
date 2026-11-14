# QA (round 2): 038 December Music Bell-Ringers

## Findings
- `python3 gen.py --check`: CHECK OK (20 days, 192 note names, 306 rhythm tokens, 100 symbol answers, 80 missing-beat items, 35 pages, preview 4 pages with one watermark each, images 2000x2000).
- Rendered all 35 pages at 40 dpi and looked at every one (cover, teacher notes, 2 reference pages, 20 daily pages, 10 key pages, terms). Nothing blank, overlapping or unreadable; regeneration broke nothing. Key page numbers and "Answer key on page N" footers are consistent.
- Preview PDF: 4 pages (days 1, 9, 17, key for days 7-8), one diagonal watermark per page.
- Cover: reads at thumbnail size; badge now says "20 DAILY PAGES" (round-1 fix confirmed). preview-1 and preview-2 are fine.
- Round-1 UPLOAD.md fix confirmed: list is 1+1+1+1+20+10+1 = 35 pages, matching tpt.json (pages 35), the PDF and the description. Title 75 chars; disclosure line present in the description and on the terms page; price 4.50; grades 3rd-6th (4); tags/subject as in round 1; all 6 files exist.
- Content: secular winter theme, no tunes, lyrics, brands or characters.
- ISSUE: `preview-3.png` ("20 DAYS, STEP BY STEP") is clipped. The Day 17-20 row of cards runs under the black footer bar, so the cards are cut off mid-box. It is thumbnail #4 on the listing and a buyer would notice it.

**Verdict: REJECTED**
1. Fix `preview-3.png` layout so the Day 17-20 row sits fully above the footer bar (shorten the empty space in the cards or reduce the card height or gap); regenerate and re-run `gen.py --check`.
