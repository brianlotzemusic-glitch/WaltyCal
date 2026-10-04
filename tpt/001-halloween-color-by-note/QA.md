# QA: TpT 001 Halloween Color by Note (round 1 of 2)

**Verdict: APPROVED**

QA reviewed this on 4 Oct 2026, independently of the Designer. No item files were changed.

## 1. Musical accuracy: pass

- **Independent decode of every symbol.** I wrote my own decoder, separate from `gen.py` and `notation.py`. It does not use the generator's pitch data. It reads the rendered SVG in `build/resource.html` and works out the following for each mini staff:
  - the clef, from the glyph codepoint and the staff line it sits on;
  - the pitch, from the notehead's y position against the 5 staff lines, using my own bottom-line table (E4 for treble, G2 for bass);
  - the ledger lines, stem direction, stem side and stem length.

  It then looks up the colour in that worksheet's key and checks the fill of the region under the symbol on the matching answer page.
- **Result:** all 508 symbols on 27 worksheets match their answer keys, with 0 mismatches and 0 notation issues.
  - Range used: treble C4–A5 and bass E2–C4. Ledger lines appear only on C4 and A5 (treble) and on E2 and C4 (bass), one line each, which is correct.
  - Stems point up below the middle line and down on or above it. Up-stems are on the right of the notehead and down-stems on the left. Stems are 3.5 spaces long.
  - All noteheads on the staffs are filled quarter notes.
  - Every white region has at least one symbol.
- **Visual spot checks at 300 dpi.** I read pages 22 (B, jack-o'-lantern), 40 (C, jack-o'-lantern) and 3 (reference) by eye, and checked each region against the key on pages 31 and 49. I decoded Level A pages 4 and 13 by eye. All correct.
  - The G clef curls around the G line, and the F clef dots straddle the F line.
  - Whole and half noteheads are open; quarter and eighth noteheads are filled.
  - The eighth-note flags and the Bravura quarter rest are correct.
- **Student reference page (p3).** The treble C4–A5 and bass E2–C4 scales are correctly placed and named. The line and space mnemonics and the stem rule text are correct.

## 2. Age-appropriateness: pass

- The pictures are cute and not scary (smiling pumpkin, "oh" ghost, smiling cat, friendly spider). There are no brands, characters or songs.
- Instructions are short and clear, with name and date lines. Colour names are printed as words, so pages still work in black and white.
- Level A rhythm glyphs are about 40 pt tall, which is large. On the B and C mini staffs a staff space is 5.4 pt (about 1.9 mm). That is readable, but small for grade 2 (see suggestion 1).
- The smallest colourable region has an inscribed diameter of 44 pt (candy wrapper), which meets the ≥40 pt rule.

## 3. Technical: pass

- `gen.py --check` passes.
  - The PDF has 58 pages, all US Letter, and the preview has 4.
  - All fonts are embedded and subset: Oswald, Source Sans 3 and Bravura.
  - The cover and all 3 preview PNGs are 2000×2000.
- The preview shows Level A, Level B, a Level C worksheet and a Level C answer key, each with a diagonal PREVIEW watermark.
- All three fonts are OFL 1.1, which allows embedding in documents. The credits on page 58 name Bravura © Steinberg, Oswald and Source Sans 3 with their OFL licence, and the disclosure line is printed there too.

## 4. UPLOAD.md: pass

- The title is exactly 80 characters.
- The description is accurate: 58 pages = cover + teacher notes + reference + 27 + 27 + terms, and the levels and ranges are correct.
- Grades 1–5, Music + Halloween, Worksheets/Activities and $3.50 are all correct.
- The disclosure line is present. No songs are used and no product names appear.

## 5. Bar: pass

- At about 350 px, "COLOR BY NOTE" reads clearly on the cover.
- The previews sell it well: the 3-level differentiation, a worksheet beside its key, and the 9-picture grid.
- Three levels on the same 9 pictures, plus full-colour keys and a reference page, is good value at $3.50 against typical $3–5 single-level sets.

## Optional suggestions (not blocking; fold into a later build if convenient)

1. Consider raising `B_SPACE` from 5.4 pt to about 6.5 pt where regions allow, so grade 2 readers find the B and C staffs easier. Re-run the placement check afterwards.
2. Page 58 says extra licences are available "at a discount". Remove "at a discount" unless the owner sets a multi-licence discount on TpT.
3. Owner: the description and page 58 say the keys were "checked by hand". Please flip through a few keys before upload so that claim stays true.
