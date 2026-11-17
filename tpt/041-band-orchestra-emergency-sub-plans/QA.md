# QA: 041 Band and Orchestra Emergency Sub Plans (third-round independent review)

## Checks run
- `gen.py --check`: CHECK OK (123 key items, problem-to-strategy mapping, word search, timeline math, 29 pages, 4-page preview). `tools/tpt-validate.py`: OK. `git status`: only gen.py, resource.html and the two PDFs modified.
- Rendered all 29 pages at 110 dpi and looked at each; looked at the 4 preview PDF pages (one watermark each), cover and preview-1..3 at full size. Nothing clipped, overlapping or blank. Cover and preview notation: 4/4, two beamed eighth pairs, quarter, quarter rest, double bar; stems and beams correct.

## Lesson 4 matching (page 16), solved as a student
Strategies: A isolate hard spot, B steady beat, C small chunks, D mark music, E one goal.
- M1 "I forget where I made mistakes": D only (marking music is the only strategy about remembering). Key D.
- M2 "The same hard spot goes wrong every time I play": A (the hard spot, repeat it). A weak argument for D (circle trouble spots) exists but D does not fix the problem; C is not about one spot. Key A.
- M3 "My practice time feels random and goes nowhere": E (goal keeps practice from drifting). Key E.
- M4 "I can play the first line, but I fall apart when I try the full page": C (short chunks, then join). A does not fit (no single hard spot). Key C.
- M5 "I speed up whenever the notes get fast": B (rush or drag, metronome). Key B.
One clear best answer per item, equal to the key on page 26. Defect closed.

## Other items re-solved (all match the keys)
- L1: sort (16 instruments), B1-6 B D F A E C, C1-6 T F T F F T, D1 B, D2 B.
- L2: A 4 5 4 3 5 7; B 2 1 1 2 3 1; C = > = > < =; D Y N Y N N Y Y Y; E 3/4 2/4 2/2 4/4; F 128, 1, 4, 60, 96.
- L3: A D B A B C; B Beethoven, Bach, Sousa, Mozart; C 71, 6, 14, 72, 1756; order Bach 1, Mozart 2, Beethoven 3, Sousa 4. Facts correct: Bach 1685-1750 (Leipzig from 1723, Brandenburgs 1721), Mozart 1756-1791 age 35, Beethoven 1770-1827 (Ninth, Vienna 1824), Sousa 1854-1932 (Marine Band 1880-92, Stars and Stripes 1896, national march 1987).
- L4 sample week 105, 6, 17.5, Sat, YES.
- L5: loudness pp1 p2 mp3 mf4 f5 ff6; terms D H B F J A G I C E; who-is-who conductor, section, concertmaster, first; band zones woodwinds, brass, percussion; orchestra zones match standard layout. Word search: 12 words, each findable, solution page agrees.
- Early finishers: scrambles clarinet, trumpet, timpani, trombone, bassoon, viola; riddles double bass, trombone, timpani, violin, saxophone.
- Instrument-family facts correct (saxophone woodwind, tuba, timpani pitched, violin smallest).
- Read-aloud scripts and timed steps are usable by a non-music sub; step minutes add to the stated class length; page references correct.
- UPLOAD.md/tpt.json: title 76 chars; disclosure line present on the terms page and in the description; 29 pages (list totals 29); 4 grade entries; subjects Music and Instrumental Music and the 6 tags are exact non-heading entries in the option lists; files exist.

## Findings
None blocking.

**Verdict: APPROVED**

## Rescue 2026-11-17
Held rescue (step 2b): Lesson 4 matching (p16) reworded so each item fits exactly one strategy (M1 D, M2 A, M3 E, M4 C, M5 B, key p26 unchanged); --check now asserts the mapping and key counts for Lessons 3-5. QA re-checked the whole product: APPROVED. Visual inspector re-checked cover, previews and the touched pages (15-17, 24-27, preview PDF): OK, no BLOCKING item. Open NOTES (not changed): p15 says 'the four pages for this lesson (page 16, 17, 18)' but lists three; p16 numbers items 1-5 while the p26 key says M1-M5; blank lower areas on pp15-17, 24; 'violins' wraps alone in the word bank on p20.
**Verdict: APPROVED**
