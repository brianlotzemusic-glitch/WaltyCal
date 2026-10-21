# QA: TpT 027 Thanksgiving Color by Note (round 1 of 2)

**Verdict: APPROVED**

QA reviewed this on 21 Oct 2026, independently of the Designer. No item files were changed.

## 1. Colour-by-code and notation: pass
- I wrote my own decoder, separate from `gen.py`. It reads `build/resource.html` and takes the key from each page's printed key cells. For Levels B and C it works out clef, pitch (from staff-line y positions), ledger-line count and stem direction/side from the drawn lines and glyphs. For Level A it reads the glyph codepoint. It then finds the region under each symbol and compares the key colour with that region's fill on the matching answer page.
- Result: all 413 symbols on 27 worksheets match their answer keys, with 0 mismatches and 0 notation issues (stems, ledger lines, clef on the right line). Every region holds at least one symbol, and all 27 keys have the same region count as their worksheets.
- `notation.py` is identical to 001's (QA-approved), so the treble C4–A5 and bass E2–C4 ranges, ledger-line rules and glyph anchors are unchanged. Level A is whole, half, quarter, eighth and quarter rest, and the beat values on the reference page are right.
- Visual checks of pages 1–3, 40 (C turkey), 49 and 58 and the preview pages: pictures are fully colourable closed regions, and the turkey key matches the worksheet. The reference-page scales are named correctly (treble C D E F G A B C D E F G A; bass E F G A B C D E F G A B C), and so are the line and space mnemonics.

## 2. Art, cover and previews: pass
- The pictures are original code-drawn line art and kid-friendly: turkey, pumpkin, cornucopia, maple leaf, acorn, apple basket, pie, corn and sunflower. No characters, brands or songs.
- At 350 px the cover title reads clearly. It follows STYLE.md: HUDSON BEAT store line, black and rust accent only, black band. The three previews are clean, and the watermark is on the page shots.
- Minor: preview-1 has about 25% empty white space above the band. This is cosmetic and does not block approval.

## 3. Technical: pass
- `gen.py --check` passes: 58 Letter pages, a 4-page preview, fonts embedded, and the images are 2000×2000.
- `tpt.json` is valid and has the same shape as 001's. Price and license price are 3.75, the tax code is set, there are 4 grades, 1 subject, 1 tag and 4 files.
- The UPLOAD.md title is 79 characters. The description is accurate (58 pages = cover, notes, reference, 27, 27, terms), and it has the disclosure line. It names no trademarks.
- Terms page: it no longer carries 001's optional "at a discount" wording (suggestion 2 from 001 is fixed here).

## 4. Price: acceptable
$3.75 is within the owner's $3.50–4 range. A 25-cent gap from 001 is fine for a seasonal set with 9 pictures and 3 levels.

## Open owner questions (do not block)
1. Price $3.75 vs 001's $3.50.
2. Whether the logo goes beside HUDSON BEAT.
3. The owner should flip through a few keys so "checked by hand" stays true.
4. Suggestion for a later build: the B/C staffs use a 5.4 pt staff space (small for grade 2). The same carries over from 001.
5. Timing: list by early November (Thanksgiving is 26 Nov).
