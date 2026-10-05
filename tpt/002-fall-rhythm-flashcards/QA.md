# QA: TpT 002 Fall Rhythm Flashcards & Tracing (round 1)

QA reviewed this item on 5 Oct 2026, independently of the Designer. I rendered all 29 resource pages (100 dpi, with problem areas re-rendered at 200 dpi), the 4 preview pages, `cover.png` and `preview-1..3.png`, and looked at each one by eye. I did not use `gen.py --check`, and I changed no item files.

## 1. Musical accuracy: pass on cards and worksheets, one defect on the tracing page

- **Symbol cards (p4–5).** These are correct.
  - The quarter note has a filled head with its stem up on the right.
  - The two eighth notes have filled heads, up-stems and one thick beam.
  - The quarter rest is the correct Bravura glyph.
  - The half note has an open head with its stem up on the right.
  - The stick-notation versions are correct: |, the beamed ⊓, the zig-zag rest, and a half note drawn with an open head.
  - The beat labels (1, 1, 1, 2) are correct.
- **Pattern cards (p6–17).** I recounted all 12 patterns from the printed notes. All 12 total exactly 4 beats in 4/4.
  - Set A: q q ee q · ee ee q q · q ee ee q · ee q ee ee
  - Set B: q q q r · ee ee q r · q r ee q · ee r q ee
  - Set C: q q h · ee ee h · h q r · ee r h
  - Each stick card (p12–17) matches its standard-notation card. Half notes sit under leaf 1 or leaf 3 with the next leaf empty, which is correct.
  - The time signature, one-line staff and final double bar are correct.
- **Reference (p3) and cover card.** The examples total 4 beats (ee q h, and ee r h), and the "Remember" rules are correct.
- **Kodály syllables.** Every card and the reference page show them only as "Kodály syllable (optional)". The teacher notes name other syllable systems.
  - Note: the TpT title, the PNG cover subtitle and the preview-1 subtitle use "ta, ti-ti" as search and marketing terms. That is acceptable because the printed student material keeps the syllables optional.
- **DEFECT, tracing p22, pattern 3** (`TRACE_PATTERNS[2] = "qqh"`).
  - All three symbols are drawn as identical dotted outlines (open oval plus stem). The intended half note cannot be told apart from the two quarter notes.
  - The quarter notes in patterns 1–3 are also open outlines. Unlike p18, this page never tells the child to colour them in.
  - As printed, a child traces three half-note shapes over three leaves, or reads pattern 3 as 3 quarter notes = 3 beats. Either way it contradicts the page's "every pattern fills 4 leaves".

## 2. Answer keys (p26–28): pass

I recounted every item by hand from the printed worksheets.
- **WS1 (p23 → key p26):** 1, 2, 1, 1, 2, 1, 1, 1. All correct.
- **WS2 (p24 → key p27):** q+ee = 2, h+q = 3, q q r q = 4, ee ee ee = 3, h h = 4, r q = 2. All correct.
- **WS3 (p25 → key p28):** 4 YES, 3 NO, 4 YES, 5 NO, 4 YES, 3 NO. The circles and the small totals are all correct.

The key items match their worksheets symbol for symbol, and the cross-references ("Answer key on page N" / "Worksheet on page N") are correct.

## 3. Age fit (K–2): pass, apart from the p22 issue above

- The symbols are very large: about 1 in on the symbol cards and about 0.7 in on the pattern cards.
- The instructions are one or two short sentences. The tracing start dots are large, and every student page has Name and Date lines.
- The art is friendly: a leaf, acorn, pumpkin and smiling owl.

## 4. Print quality: pass with one layout defect

- All pages are US Letter and all fonts are embedded and subset (`pdffonts`).
- The STYLE.md footer "© 2026 Brian Lotze · Hudson Beat · For single-classroom use" and the page number appear on every page from 2 to 29.
- Everything is black on white with a rust accent, so it works in black and white. The accent dots and key circles print as mid-grey.
- The Hudson Beat cover stack is correct: store line, art, two-line title, subtitle, black band.
- **DEFECT, symbols crowding the card border on the worksheets.**
  - p24, rows 3 and 6: the quarter rest hangs below the noteheads, and its bottom ends about 1 pt from the card's bottom border.
  - p25, row 1 (and row 6 nearly): the half note's open head touches or almost touches the bottom border.
  - At home-printer tolerances this will read as clipped.

## 5. tpt.json / UPLOAD.md: pass

- The title is 77 characters, within the 80 limit.
- Price and license_price are both 4.00, and tax_code is "Other Digital Goods - No Physical Media".
- Grades: 3 (K, 1, 2). Subjects: 1. Tags: 1 ("Autumn"; confirm it on the dry run, as UPLOAD.md says).
- All six files in `files` exist, the PNGs are 2000×2000, and the preview PDF has 4 pages.
- The description is accurate.
  - The page count works out: 1 + 1 + 1 + 2 + 12 + 5 + 6 + 1 = 29.
  - The card count works out: 8 + 24 = 32.
  - The "every pattern card is exactly 4 beats" claim is verified, and the "answer keys … checked by hand" claim is verified (section 2).
  - The disclosure line is present.
  - No songs, lyrics or brand names appear. The standards claim is modest.
  - The structure and art are original, and I found no copying of another seller.

## 6. Cover and previews: pass

- At 350 px, "FLASHCARDS" and the band "GRADES K–2 · 32 CARDS · TRACING · ANSWER KEYS" read clearly.
- The previews show what's inside, a worksheet beside its key, and the 12-pattern grid. All 12 patterns in the grid match the cards.
- The preview PDF holds symbol cards, stick pattern cards 5–6, tracing 2 and worksheet 2, each with a watermark.

## Required fixes

1. **p22 tracing pattern 3 (and the quarter notes in patterns 1–3):** make quarter notes and half notes look different.
   - For example, draw the quarter noteheads as a light grey solid fill (or tell the child to "colour in the quarter-note heads"), and keep the half note as an open outline.
   - Or add a "2 beats" bracket spanning leaves 3–4 under the half note.
   - Then re-render, so the p19-style preview stays consistent.
2. **p24 and p25 worksheet rows:** keep every symbol at least about 6 pt inside the card border.
   - Raise the rest so it sits on the noteheads' baseline, not below them.
   - Raise the stick half notes, or make the row taller.
   - Check every row of all three worksheets and keys (p23–28), then rebuild the preview PNG that shows p24/p27.

## Optional (not blocking)

- Preview-3 leaves about a quarter of the square empty under the grid. Consider larger cards, or adding the stick-notation versions.
- On the tracing rest (p20 and p22), the dotted path doubles up at the curl. A cleaner single path would be easier to trace.
- On pattern card 4 (p7), the last beam sits close to the double bar. A little more right padding would help.

**Verdict: REJECTED**

---

# Round 2 (5 Oct 2026)

I re-rendered the rebuilt PDF (29 pages), the preview PDF (4 pages) and all four PNGs, and checked them by eye. Pages 22–28 were re-rendered at 200 dpi and their clearances measured from pixels. I changed no item files.

## Round-1 fixes: both pass

1. **p22 tracing patterns: fixed.**
   - Quarter and eighth noteheads are now grey-filled ovals, and the instruction says "Color in the gray noteheads; leave the half-note head open."
   - Pattern 3's half note is an open outline, with a "HALF NOTE: 2 BEATS" bracket under leaves 3–4.
   - Recounted: pattern 1 is q q ee q, pattern 2 is ee ee r q, pattern 3 is q q h. All three are 4 beats.
   - Pages 18–21 now show grey heads only where the head is filled (quarter and eighths). The half-note page (p21) correctly keeps open heads.
2. **Worksheet clearance: fixed.**
   - Measured gap from symbol ink to the card border: at least 7.2 pt on p25 and p28, and at least 10.8 pt on p24 and p27. Every gap is at least 8.6 pt at the top.
   - The rests now sit on the noteheads' baseline. Nothing touches a border.

## Regression check

- **Pattern cards p6–17.** All 12 patterns, in both standard and stick notation, are unchanged. Each one still totals 4 beats, and there is now clear space before the final double bar (including card 4).
- **Worksheets and keys p23–28.** I recounted every item again:
  - WS1: 1, 2, 1, 1, 2, 1, 1, 1
  - WS2: 2, 3, 4, 3, 4, 2
  - WS3: YES (4), NO (3), YES (4), NO (5), YES (4), NO (3)

  All correct, and the cross-references are intact.
- **Preview PDF** (p4, p14, p19 with grey heads, p24), **preview-1..3.png**, footers and page count: all fine.
- **DEFECT (new in this build): the cover's final double bar collides with the card edge.**
  - In `cover.png` (around x 1500–1560, y 450–650 at 2000 px) and on the PDF cover (p1), the thick final barline now overlaps the front card's right border.
  - This is probably a side effect of the "more room before the final barline" change.
  - It is visible on the main TpT image even at 900 px, and it reads as a drawing error on the one notation example a buyer sees first.

## Required fix

1. **Cover card (cover.png and PDF p1).** Pull the final double bar back inside the card, with at least about 12 px clearance at 1000 CSS px.
   - Do this either by shortening the staff or by widening the card.
   - Then rebuild cover.png and the PDF. The preview PDF does not include p1.

## Optional (not blocking)

- On p22, the "HALF NOTE: 2 BEATS" label sits about 3 pt above the next heading, and the compose box sits about 3.6 pt above the footer rule. Both are legible, but a few points more air would help.
- Pages 19–21 also say "Color in any gray noteheads". That is harmless where none appear (p20, p21), but it could be dropped there.

**Verdict: REJECTED**
