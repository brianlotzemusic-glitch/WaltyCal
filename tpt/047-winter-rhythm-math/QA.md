# QA: 047 Winter Rhythm Math

## Checks run
- `python3 gen.py --check`: OK (15 worksheets, 120 items, 22-page PDF, 4-page preview).
- `python3 tools/tpt-validate.py tpt/047-winter-rhythm-math`: OK. `git status --short`: only `tpt/047-winter-rhythm-math/` is new.
- Rendered all 22 pages at 110 dpi and looked at each at full size, plus cover.png, preview-1/2/3.png (2000 px) and all 4 pages of the PREVIEW PDF (watermarked, one watermark each). Zoomed (250-300 dpi) on A4 item 5 (whole rest) and C5 item 5.

## Answer keys recomputed from the rendered notes
Read independently and compared with the keys: A1-A5, B1-B5, C1-C5 (all 15 worksheets, all 120 items): every item matches its key. This covered dotted notes, ties, rests (quarter, half, whole, eighth), 3/4, 2/4 and 4/4 fullness, > < = comparisons, missing beats (including 1/2 and 1 1/2) and the "which note fits" items. Each worksheet has 8 items and each key has 8 entries. No item has two right answers. B4 offers exactly one fitting note in every item. C4 asks only for a number, so ½-beat gaps cause no ambiguity.

## Notation
- Percussion clef on a 5-line staff. Every note sits on the middle line, so all stems go down, from the left edge of the head. Checked on the cover, previews and pages.
- Open and filled heads match the note named. Flags are on the right of the stem, beams join the pairs, and dots sit in the space above the line.
- Ties arc over the heads (above, because the stems are down) and join the intended notes.
- Half rest sits on a line and whole rest hangs below it (confirmed in the zoom of A4 item 5, which is a whole rest worth 4). Barlines and time signatures are correct.
- The cover and preview artwork have the same correct stems.

## Wording and listing
- Instructions are full sentences and fit the grades (A 2-3, B 3-4, C 4-5). Labels match their contents. Pages named in the footers and level guide (A pp. 4-8, B pp. 9-13, C pp. 14-18, keys 19-21, terms 22) are right.
- The disclosure line is on the terms page and in the UPLOAD.md description. There is no hand-checked, handmade or classroom-tested claim.
- No tunes, lyrics, characters or brands. The tune public-domain rule does not apply.
- tpt.json: 4 grade entries (2nd to 5th), subjects Music, Arithmetic, Basic Operations and tags Winter, Worksheets, Printables, Activities, Homework are all non-heading entries in the options files. All six files exist, pages = 22, price 3.50.
- UPLOAD.md: title is 64 characters (80 allowed), with no seasonal words. The page list totals 22. The description matches the product: 15 worksheets, 8 items each, 3 key pages, 4-page preview.

## Minor, not blocking
- Teacher notes and page 3 use British "practise" and "practise"-style wording ("WHAT STUDENTS PRACTISE"); US "practice" would suit the buyers better.
- Page 3 has a stray small blue dot after the "HOW LONG IS EACH NOTE AND REST?" heading.
- The page 3 "snow tip" (1 beat, then 2, then 3) is slightly cryptic.

**Verdict: APPROVED**

Required fixes: none.
