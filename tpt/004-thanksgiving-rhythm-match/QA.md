# QA: TpT 004 Thanksgiving Rhythm Match + Echo Cards (round 1)

QA reviewed this item on 9 Oct 2026, independently of the Designer. I rendered all 21 resource pages at 60 dpi as contact sheets and looked at the answer keys (p17-20) at 100 dpi. I looked at the 4-page preview PDF at 40 dpi, and at `cover.png` and `preview-1..3.png` as a 2x2 sheet. I checked the music data with my own script (scratchpad), which reads only the phrase and pattern lists from `gen.py`. I did not run `gen.py --check`, and I changed no item files.

## 1. Musical accuracy: pass

- **Bar sums.** My script found every one of the 24 match rhythms, the 6 "Write the Rhythm" rhythms and the 24 echo patterns totals exactly 4 beats in 4/4. Every staff shows a 4/4 time signature and a final barline.
- **Syllables match notes.** I derived the rhythm from each phrase (1 syllable = ta, 2 = ti-ti, "shh" = rest, "~" = held two beats) and it equals the stored rhythm for all 24 match cards and all 6 write phrases. The 24 echo cards print ta / ti-ti / shh / ta-a under the right beats, as seen on p13-16 (for example #13 "ti-ti ta ti-ti shh", #20 "ta-a ti-ti ti-ti"). Stressed syllables fall on the beat.
- **Uniqueness.** All 24 match rhythms are different, so each word card has exactly one match. The 24 echo patterns are all different too.
- **Notation.**
  - Eighth pairs are beamed by the beat.
  - Half notes have open heads and stems up.
  - The quarter-rest glyph is the right shape.
  - Everything sits on the one-line rhythm staff.
  - Each word box is one beat, with a dotted arrow for the held beat.
- **Answer keys.** I traced every line on p18 (Match It! 1) and p19 (Match It! 2) by eye.
  - Turkey -> eeeq, Corn -> qqqq, Leaf -> qeqe, Crunch -> qqee, Leaves -> qeeq, Pies -> qeee.
  - Leaves -> qeqr, Gobble -> eeh, Pie~ -> hqq, Fall~ -> heq, Turkey -> eerq, Pie shh -> qreq.
  - All 12 are correct.
  - The p20 stick rhythms for the six write phrases are correct: eqqr, eqeq, qeqr, eeer, qqh, hh.
  - The p17 table lists rhythm letters. The two I spot-checked (word card 1 -> D, card 12 -> H) agree with the cards on p6.
- **Cover and previews.**
  - The cover's mini rhythm card "D" shows ee q ee q, which matches "Pump-kin pie, pump-kin pie".
  - preview-3 rows (eqeq, eeee, eqrq, eeh) match their words.

## 2. Age fit (grades 1-3): pass

- The language is simple and the phrases are original and silly (gobble, pop-corn, crunch). There are no history scenes, religious images or characters.
- The two levels are clear, and Set 2 is marked grades 2+.
- The art is turkey, pie, corn, apple, leaf, acorn and pumpkin in black plus rust.
- No songs or lyrics are used.
- The terms page and teacher notes follow STYLE.md section 6.

## 3. Layout, legibility and print: pass

- All 21 pages are US Letter. Fonts are all embedded (`pdffonts`), including Bravura, Oswald and Source Sans 3. The one Liberation Serif subset is on p17 only (probably the "->" glyph in the key heading). It is embedded and harmless.
- Nothing overflows or is clipped. Footers sit at the normal position on every page, and the cut grids stay inside the margins.
- The word boxes shrink for long beats ("Pies", "pump-kin", "Fall", "crunch-y", "leaves"), but stay readable. The small print on the cards ("Say it, clap it...", "ECHO ME!") is decorative.
- The cover is readable at thumbnail size. It has the store line, art, a two-line title, a subtitle and a black band, and it follows the Hudson Beat stack.
- The preview PDF (4 pages) has a single, clean diagonal watermark per page. Its pages are p5 (Set 1 word cards), p15 (echo #13-18), p9 (Match It! 1) and p20 (the Write the Rhythm answer key). The range is good.
- preview-1..3 are 2000x2000, each with the store line, a headline, a black benefit band and one watermark per page shot. In preview-2 the worksheet/key shot is cropped by the black band, which reads as a stacked-pages look.

## 4. tpt.json and UPLOAD.md: pass

- The title is 77 characters (limit 80). UPLOAD.md says 78, which is a harmless miscount.
- price and license_price are both "3.50", and tax_code is "Other Digital Goods - No Physical Media".
- Grades: 3 (1st-3rd). Subjects: 1 (Music). Tags: 2 (Thanksgiving, Autumn).
- All 6 `files` exist. The PDF has 21 pages (matches `pages`), the preview PDF has 4, and the PNGs are 2000x2000.
- The description's page breakdown adds up (2+1+4+4+4+4+1 = 20 + cover = 21). The claims (24+24 cards, two levels, 24 echo cards, every phrase 4 beats, every rhythm different) are verified.
- The disclosure line is the last line of the description and is printed on p21.
- The standards claim (MU:Pr4.2) is modest. The net $1.63 is correct (3.50 x 55% - 0.30).

## Optional (not blocking)

- Confirm in the `--dry-run` that TpT offers the exact tag text "Thanksgiving". UPLOAD.md already says to drop it if not.
- Fix the title length in UPLOAD.md (77, not 78).
- A few shrunken word boxes (sheet 2 "Fall", "crunch-y") could be slightly larger for grade 1.

**Verdict: APPROVED**
