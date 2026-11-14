# QA: 041 Band and Orchestra Emergency Sub Plans (second-round independent review)

## Checks run
- `gen.py --check`: CHECK OK. `tools/tpt-validate.py`: OK. PDF 29 pages; preview PDF 4 pages.
- Rendered all 29 pages and looked at each (page 2 teacher notes intact; nothing clipped, overlapping or blank; footers clear), the 4 preview pages (one watermark each, counts say 29), the cover (reads at thumbnail size, says 29 pages) and the 3 preview PNGs.
- Round-1 fixes confirmed: Lesson 1 key now D1 B, D2 B only (worksheet has 2 questions); "Italian" capitalised.
- Answer keys checked by hand against the worksheets, all five lessons, item by item. L1 sort/B/C/D, L2 A to F, L3 A to C and order, L4 sample week (105, 6, 17.5, Sat, YES), L5 zones, loudness order, terms, who-is-who, early-finisher scrambles and riddles: all correct. Only exception: item 1 below.
- Word search solved independently from the PDF grid (14 x 14 text read, all 8 directions): all 12 words present exactly once.
- tpt.json (grades 4, subjects Music and Instrumental Music, 6 tags, price 7.00, files exist, pages 29) and UPLOAD.md (title 76 chars, page list totals 29, disclosure present) consistent. No tunes used.

## Findings
1. Lesson 4 "Match the problem to the best strategy" (page 16), items 2 and 4 are ambiguous and the key picks the weaker match. Item 4 "Playing the whole piece every time never fixes the hard part" echoes strategy A almost word for word ("Do not play the whole piece again and again... repeat just those"), yet the key says M4 = C. Item 2 "I keep missing the same two measures" also fits A ("one or two measures that go wrong"). A student or teacher who answers A for both is marked wrong on one.

**Verdict: REJECTED**
1. Make items 2 and 4 on page 16 unambiguous and the key (page 26) match. For example swap the key to M2 C, M4 A, and reword item 2 so chunking is clearly the fix (e.g. "I can play the first line but fall apart when I try to play the whole page"), or reword item 4 away from the "whole piece" phrase. Then rebuild and re-run `--check`.
