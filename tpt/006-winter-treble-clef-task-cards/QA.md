# QA: TpT 006 Winter Treble Clef Note-Name Task Cards (round 1)

QA reviewed this item on 10 Oct 2026, independently of the Designer. I rendered all 23 resource pages at 60 dpi as contact sheets, the Worksheet A key at 100 dpi, the 4-page preview PDF at 40 dpi, and `cover.png` plus `preview-1..3.png` as a 2x2 sheet, with one 100% crop of preview-2. I did not run `gen.py --check` and changed no item files.

## 1. Musical accuracy: pass

I did not trust the Designer's check. My own script (scratchpad) reads the drawn SVG in `build/resource.html` and works out each pitch from geometry: the Bravura notehead baseline against the five staff lines, in half-space steps from the bottom line (E4). It then compares the result with the text printed on answer-key page 19 (extracted with `pdftotext`).

- **All 151 staves on all pages are consistent.** Every notehead falls on an exact half-space step. In every staff the treble clef sits on the second line (G4).
- **Level A (24 cards).** The drawn pitch letter equals the key for A1-A24. Each card has 3 distinct choices and the correct letter is always one of them. The range is E4 to F5, on the staff only, so no ledger lines are needed.
- **Level B (24 cards, 3 notes each).** The drawn letters equal the key for B1-B24, including the D4 (below the staff) and G5 (above the staff) notes. Where a letter repeats on a card (for example B4 E E D, B12 F F G) the octaves differ, so the notes really are different pitches.
- **Level C (24 word cards, 3 to 7 notes).** The drawn letters spell the printed key word for C1-C24. All words are real, simple words: ACE, BAG, FACE, CABBAGE, BAGGAGE and so on. The key is "name the letters", so there are no duplicate-spelling problems.
- **Ledger lines.** For every notehead in the 151 staves, I checked that each ledger line needed to reach the note is drawn, and that no extra ledger line is drawn. Missing: 0. Extra: 0. Low C4 gets one line below the staff. D4 sits just below the bottom line with no ledger line. A5 gets two ledger lines above the staff (a ledger line for A5 at step 12 and one for the C-space at step 10). G5 sits just above the top line with no ledger line.
- **Stems.** All 368 stemmed noteheads follow the rule. Stems go up below the middle line and down on or above it, and every stem is about 3.5 staff spaces long. The 44 notes with no stem are the whole-note reference strips (reference page and the "Lines and spaces" strips), which is correct.
- **Worksheets.**
  - Worksheet A: the blank staves (p16) match the key staves (p20) for all 16 notes. The answers are E C A F D E D C F E C B F C F G.
  - Worksheet A, LINE or SPACE: I checked all 16 circles against the pitch. The five LINE notes are D5, E4, D5, B4 and G4. The other 11 are SPACE, and the "5 on a line, 11 in a space" count is right.
  - Worksheet B: all 8 groups match between p17 and p21.
  - Worksheet C: the 10 words match between p18 and p22. The 10 words are BEG, DEED, EBB, DAB, AGED, CAGED, FACED, FADED, BEADED and ADDED.
- **Reference page (p3).** The full strip is C4 to A5. The line notes are E G B D F and the space notes are F A C E, both in the right positions. The "just outside the staff" strip shows C4 and D4 below and G5 and A5 above, and the note says "Low C and high A sit on their own short line", which is right. The G-clef tip ("curls around the G line, line 2") is right, and the "Every Good Bird Does Fly" and "FACE" memory aids are right.
- **"Lines vs spaces" labels.** Every "LINE" and "SPACE" label on the reference page, the worksheets and the keys matches the note's position.
- **Cover.** The hero staff F4 A4 C5 E5 is labelled F A C E, and the mini cards (A1 with choices A G F, C10 spelling FACE with a ledger-line C) are correct.

## 2. Age fit (grades 2-5): pass

- The language is simple and the levels are well scaffolded. A is clip cards with choices, B is name three notes, and C is word puzzles with ledger lines. The teacher notes give a rough grade guide (A for grade 2, B for grades 3-4, C for grades 4-5).
- All art is snowflakes, mittens and knit hats. The product is deliberately not tied to any celebration, and none of the banned holiday words appear.
- No songs or lyrics are used.
- Terms page and credits follow STYLE.md section 6. The Q&A tab is named and no email address is printed.

## 3. Layout, legibility and print: pass

- All 23 pages are US Letter. Oswald, Source Sans 3 and Bravura are embedded (`pdffonts`).
- Nothing overflows or is clipped. Footers are in the normal position on every page, and the cards sit inside the margins.
- At 60 dpi the cards, notes, answer letters and blanks read clearly. The 7-note Level C cards (C21-C24) use a longer staff but stay inside the card and keep all seven blanks.
- Everything works in black and white. The accent blue is only used for small things and for answers on the keys.
- The preview PDF has 4 pages (Level A 1-8, Level B 1-8, Level C 1-8, Worksheet A key), each with one clean diagonal watermark. This matches UPLOAD.md.

## 4. Cover and preview images: pass

- `cover.png` and `preview-1..3.png` are all 2000x2000. They follow the Hudson Beat stack: store line, art, a two-line title, a light subtitle, and a black band. The big title line is clearly readable at thumbnail size.
- The previews show the three levels side by side, a worksheet next to its key, and the contents grid. Their watermarks are clean.
- Cover art uses only the accent blue and black. There are no borders or photos. It matches the brand.

## 5. tpt.json and UPLOAD.md: pass

- Title is 79 characters (limit 80), and UPLOAD.md states 79 correctly.
- price and license_price are both "4.00", and the net of about $1.90 is right (4.00 x 55% - 0.30).
- tax_code is "Other Digital Goods - No Physical Media".
- Grades: 4 (2nd to 5th). Subjects: 1 (Music). Tags: 1 (Winter). Formats: PDF.
- All 6 `files` exist. The PDF has 23 pages (matches `pages: 23`), the preview PDF has 4, and the images are 2000x2000.
- The description's page breakdown adds up: 2 + 1 + 9 + 3 + 3 + 4 + 1 = 23. The claims (72 cards, 8 per page, 3 levels, C4 to A5, 16-note, 8-group and 10-word worksheets) are verified above.
- The disclosure line is the last line of the description and is also printed on p23.
- The standards claim (MU:Pr4.2) is modest.

## Optional, not blocking

- UPLOAD.md description, "WAYS TO USE THEM": "Scoot or around the room" reads as a typo (the PDF teacher notes say "Scoot / around the room"). Reword to "Scoot around the room".
- preview-2: the small "WORKSHEET B" and "ANSWER KEY" labels sit slightly awkwardly above the page shots. This is cosmetic only.
- Worksheet C key (p22): the answer word sits right on the underline, which is a little tight. It stays legible.

**Verdict: APPROVED**
