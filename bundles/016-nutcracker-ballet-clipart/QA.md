# QA: 016 Nutcracker Ballet Clipart (round 1)

## Summary

This is a clean second clipart set. The 12 designs read well on dark and light backgrounds, the anatomy holds up, and nothing resembles a known ballet company's or film's characters or branding. The SVGs, ZIP, listing images, copy and licence all match the files. I found no defect that needs fixing, only the notes below. QA ran its own checks on the files unpacked from the ZIP into a scratch dir, and did not rely on `gen.py --check` alone (it prints ALL CHECKS PASS).

## Technical checks

| Check | Result |
|---|---|
| ZIP | PASS. 8.1 MB, with `PNG/` x12, `SVG/` x12 and README-LICENSE.txt. Every file is byte-identical to `art/png`, `art/svg` and the bundle README (the ZIP names carry a `nutcracker-` prefix) |
| PNG basics | PASS. Each is a 3600 px palette PNG with alpha, trimmed, 0.27-0.97 MB |
| Alpha | PASS. Independent count: alpha 250-254 is 0 px in all 12. Exactly-255 pixels are 99.82-99.99% of the solid interior |
| Pinholes | PASS. No enclosed transparent hole under 200 px in any design. The two enclosed holes under 400 px are 04 (284 px) and 09 (227 px), which sit in real gaps between limbs and props, not in fills |
| Halos | PASS. Counting light neutral pixels near transparency with no exemptions, no design exceeds 725 px (05, the cream trim) and no patch exceeds 168 px (03, the teeth). Every other design is under 410 px. There are no frosty fringes on dark. See the exemptions below |
| SVG | PASS. Each has one `<path>`, one fill `#2c1b36`, no `<g>`, text or image, and a width and height in inches matching the PNG's print size |
| Spend | PASS. PROMPTS.md has $0.518 for 12 designs ($0.043 each), under $0.05. The mockup reuses 015's flat-lay at no cost |
| Taxonomy and price | PASS. 6844, $3.49 |

## Design review (all 12 PNGs on near-black and on cream, plus 100% crops of 03, 04, 05 and 12)

- **Text and weapons**: none anywhere. 01 carries a star sceptre, 08 and 09 hold drumsticks, and 06 has empty hands. Nothing reads as a sabre or sword.
- **IP**: PASS. These are generic wooden nutcrackers, a faceless dancer silhouette, a plump taupe mouse with a crown, a snowflake, shoes, plums and a music box. They don't resemble any company's costumes or any film's characters. "Mouse King", "Sugar Plum" and "Nutcracker Ballet" are generic terms for the public-domain story.
- **Anatomy**: good.
  - Full-body figures have two legs and two arms (01, 03, 09). 06 has four toes on each foot, and its hands are empty.
  - 04 is a clean arabesque on pointe. 12's tiny ballerina is fine.
  - 09 has an odd pale-green patch at the back of the head. It reads as hair or a hat lining, so it is a note, not a defect.
- **01, 02, 04, 06, 07, 08, 09, 10, 11, 12**: clean edges, no halo, sliver or hole on either background. The cream and white areas (teeth, shoes, bow, faces) keep a plum outline and read as art.

### The Designer's flagged points

- **05 renamed "Red tutu dancer"**: the rename is right. The drawing is a high leg extension on pointe (the raised leg is overhead, the working foot is en pointe), not a leap. The name is consistent across subjects, README, LISTING.md, listing.json and image 3. The words "leap" and "leaping" survive only in the `subjects.json` prompt text and the PROMPTS.md table row. Those are the literal prompt that was sent to the generator, so they are an accurate record and not a listing claim. The listing text has no "leap" wording.
- **05's hairline crack at the collar**: the crack is real, and it separates the head and neck from the torso at alpha > 127 (two connected pieces). QA measured it: a transparent line about 4-5 px tall (0.35-0.4 mm at 12 in) across the full width of the neck, between the plum neck and the navy collar. It replaces the dark outline that would sit there. On any fabric it shows as a thin fabric-coloured line, and it reads as an intentional gap or highlight between neck and collar, not damage. There are also a few 1-2 px pale hairlines along the right shoulder and torso edge, invisible at print size. This is cosmetic, below the size of 015's accepted pinholes, and it stays within the check's piece-size rule (the head piece is 167,260 px). It is not blocking. Optional: close it with the plum or navy rim colour in `process.py` on the next set.
- **03's blocky profile face**: acceptable. It is a deliberately toy-like carved face: a wedge nose, one almond eye, a big moustache, and the hinged jaw with a row of teeth. At full size and in the 12-design sheet, it reads at once as a wooden nutcracker in three-quarter view. It is stylised, not warped, and there is no extra eye or odd feature. It is the least polished face of the three, but it does not look wrong.
- **HALO_OK exemptions**: all four are real light art, and each is a small box.
  - **03 teeth**: white teeth with a plum outline in the open mouth.
  - **04 shoe**: the cream pointe shoe and ribbon ties on the raised foot.
  - **05 neckline**: the thin cream trim line on the bodice.
  - **12 bow**: the cream ribbon bow on the lid.
  
  At 100% on dark each has a clean outline and no fringe, and none hides a sliver. Even without the exemptions, the largest light patch in any design is 168 px, so the exemptions are not masking a problem.

## SVGs

All 12 match their PNGs. Colour areas without lines become outlines only (the dark plum silhouettes of 04 and 05 trace as line art, and 11's plums lose their highlights), as the spec describes. 03's bare-silhouette risk was solved with the line threshold change, and its SVG shows the face, coat and gift. "Not a vinyl cut file" is stated in the description, the README and image 4.

## Listing images

- **1 Mockup**: the product in use, a white tee, a card and a tote on the reused wooden flat-lay. At 300 x 225 the cream title "Nutcracker Ballet Clipart", the strip "12 designs · PNG + SVG · transparent · 300 dpi" and the "12 designs" badge all read, and so do the nutcracker on the tee and the dancer on the card. It is honest: it shows the real PNGs 02, 04 and 07, and the description says you receive the digital files only. The tote design runs off the bottom edge, which is natural for a tote and does not mislead.
- **2 Collage**: five real designs, large, on dark green, with the same title band and badge. No fringe at full size.
- **3 All designs**: all 12 real PNGs, numbered and named exactly as in the README and listing.
- **4 PNG + SVG**: 02 on a checkerboard and on dark plum, plus four real SVGs and the "not a vinyl cut file" line. "Sits cleanly on dark colors" is true of 02 and of the set.
- **5 What's included**: files, sizes, uses and licence all match the product.

## Listing text

| Rule | Result |
|---|---|
| Title | PASS. 138 chars, and it opens with "Nutcracker Clipart". The only two-capital words are PNG and SVG (2 of 3 allowed). No "&" and no entities |
| Tags | PASS. Exactly 13 and all unique. The longest is "sublimation designs" at 19 chars (limit 20). "commercial use png" is fair, because the licence allows small-business use and the 500-item cap is disclosed |
| Price and taxonomy | PASS. $3.49, taxonomy 6844, digital, i_did, 2020_2026, not a supply |
| Disclosure | PASS. The last line is exactly "Designed with the help of digital and AI tools, and checked by hand." LISTING.md matches listing.json |
| Description | PASS. It names all 12 designs, and the facts are right (300 dpi, 3600 px, 12 in, single-layer SVG, no text). It says "sugar plum style ballerinas", with no "leap" wording. The photo caveat and the licence are consistent with the README. Duskwood Designs Co is named |

## README-LICENSE

PASS. It names Duskwood Designs Co (header and (c) line) and the Etsy shop URL. The 12-design list matches the files. The licence allows personal use and physical items up to 500 per design, and forbids reselling or sharing the files, POD marketplaces, stock sites, AI training and trademark use. It is consistent with the listing's licence paragraph and image 5.

## Fixes

None required.

## Optional (not blocking)

1. 05: close the 4-5 px neck crack with the rim colour next time `process.py` is run (the check's S6 does not cover cracks that touch the exterior).
2. The shop policy still has no clipart licence line (S5, for the Manager, as in 015).

## Would I pay $3.49?

Yes. The set has a clear theme, variety (characters, a drum, a snowflake, shoes, plums), a usable dancer pair and clean cut-outs. The SVGs and the commercial licence add real value, and the listing images show what the buyer gets.

**Verdict: APPROVED**
