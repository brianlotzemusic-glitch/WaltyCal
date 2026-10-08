# QA: 015 Highland Cow Christmas Clipart (round 1 of 2, format pilot)

## Summary

This is a strong pilot. The 12 cows are charming, varied and on-brand, the SVGs are clean, and the copy and licence are accurate. The listing would hold its own next to the top "highland cow christmas png" results. It goes back for two real defects and one rule conflict. None of them needs new AI spend:
- **03 Pine wreath** (and the sprig ends on **10 Wreath collar**): white and light-grey paper slivers are left between the pine needles. On dark fabric they show as a frosty white fringe, which is the thing this format promises not to do. 03 is also the centre of the lead image.
- **Alpha 254**: 25–98% of the solid pixels in each PNG are saved at alpha 254 instead of 255 (97–98% on 05 and 10). The palette quantizer does this. It can't be seen on screen, but a print file sold for sublimation and DTF should be truly opaque. It's a one-line fix.
- **Listing photo order**: FACTORY.md "Art quality" says the first photo must show the product in use (a lifestyle mockup). Here the mockup is photo 3. QA enforced the same rule on 012.

## Technical checks (QA ran these on the files unpacked from the ZIP into a scratch dir)

| Check | Result |
|---|---|
| ZIP | PASS. It is 10.2 MB (under Etsy's 20 MB) and holds exactly `PNG/` ×12, `SVG/` ×12 and README-LICENSE.txt. Every file is byte-identical to `art/png`, `art/svg` and the bundle README |
| PNG size and dpi | PASS. Each is 3600 px on the longest side (12.00 in) with 300 dpi metadata, in palette mode with alpha, 0.46–1.88 MB each. Every PNG is trimmed tight to the art. No art is clipped: none of the 12 raw drafts touches its canvas edge |
| PNG transparency | Transparent corners and 24–69% transparent pixels. At alpha > 128 each design is one piece, or a few deliberate pieces (06 berries and grass, 08 bulbs, 11 mistletoe). **FAIL on full opacity** (alpha 254, see fix 2). **FAIL on fringe** for 03 and 10 (fix 1) |
| SVG | PASS. Each parses with only `<svg>` and one `<path>` element, a single fill `#2c1b36`, even-odd fill, and no text or embedded image. Each opens at the PNG's print size: width and height in inches match the PNG to within 0.004 in |
| `gen.py --check` (for reference only) | ALL CHECKS PASS. Its halo test counts only pure paper-white, so it misses the tinted slivers in fix 1 and the alpha in fix 2 (see spec amendments S1 and S2) |
| Spend | PASS. log/image-spend.csv for 8 Oct has 13 flash calls, 12 removebg and 13 upscales, totalling $0.536. That matches PROMPTS.md: $0.042 per design, under the $0.05 target |
| Taxonomy | PASS. `etsy.py taxonomy clip` returns 6844 = Craft Supplies & Tools > … > Clip Art & Image Files |

## Design review (QA viewed every PNG on near-black, on white and on berry red, plus 100% crops of the foliage, lights, fur edges and legs)

- **Anatomy**: every design is good.
  - Each full-body cow (05, 07, 10, 12) has four legs and believable hooves.
  - No design has extra horns or ears.
  - Eyes are hidden under the fringe, a pair of matching dots, closed (06, 12) or a single eye in three-quarter view (09). None looks odd.
- **03 Pine wreath**: the art is lovely and reads at a glance, but the needles carry the fringe described in fix 1. QA mapped the near-white and light-grey pixels near the edge:
  - 03 has about 30,800 such pixels in 191 slivers along almost every needle tip of the wreath.
  - The next highest are 01 (8,500, all on the horn rim, which is fine), 05 (6,300) and 10 (2,300).
  - At 100% on dark, 03 shows white blotches up to about 3 mm inside the needles. There are also light slivers between the fringe strands next to the cow's cheeks.
- **10 Wreath collar**: the cow is good. The two pine sprigs sticking out right and left of the collar have bright white slivers between their needles on dark.
- **05 Winter stroll**: the needles on the remaining sprigs have a faint light rim, and there is one small white sliver at about (2550, 2815) by the right-hand sprig. This is minor; include it in the same clean-up if it's cheap.
- **01, 02, 04, 06, 08, 09, 11, 12**: clean on all three backgrounds, with no specks, haze or holes.
  - 08's soft glow around the bulbs is intended and looks right on dark.
  - 11's white mistletoe berries are filled correctly, and the ribbon loops are open.
- **Notes, not defects**:
  - 07's "tree" reads as a pine bough with a bow rather than a whole tree. The name "Tree carrier" still works.
  - 12's green ruff on the chest was not in the prompt, but it reads as a green collar.
  - 11's horns are very wide, but within highland-cow range.
  - The angled nostrils with a downturned mouth (02, 12) are the usual cute-cow look, not grumpy.
- **Originality, text and IP**: PASS. There is no text, lettering or signature on any PNG or SVG. There are no Santa hats or character references. All 12 are generic cows with seasonal props, and nothing resembles a known character or brand.

## SVGs

All 12 match their PNGs line for line. As the spec says, colour areas without lines become plain outlines: 02's scarf stripes, 07's tree and 12's green ruff. The fringe lines are fine (04, 03), so "not a vinyl cut file" is the right claim. That note is clear in three places: the description ("not vinyl cut files: some fur lines are fine"), the README ("NOT designed as vinyl cut files… cut them only at a large size, or use the PNGs") and image 4.

## Listing images

- **1 Thumbnail**: strong.
  - At 300 px wide, the cream band, "Highland Cow Christmas Clipart", "PNG + SVG · TRANSPARENT · 300 DPI" and the "12 designs" badge all read clearly. The five big cows read too.
  - It is honest: the cows shown are real PNGs 01, 03, 04, 06 and 12.
  - The 03 fringe is visible on the dark green at full size, so rebuild this image after fix 1.
- **2 All designs**: all 12 real PNGs, numbered and named to match the README and description. Honest.
- **3 Mockup**: honest. It shows the real PNGs 04, 01 and 06 multiplied onto a blank AI flat-lay, so the fabric shading shows through. The description says "you receive the digital files only". It also reads well at 300 px ("Tees, totes, cards").
- **4 PNG + SVG**: accurate. It shows 02 on a checkerboard and on dark plum, and five real SVGs, with the "not a vinyl cut file" line. The "sits cleanly on dark colors" claim is true for 02. Make it true for every design with fix 1.
- **5 What's included**: accurate. 12 PNG, 3600 px / 12 in, 300 dpi, 12 SVG, the licence "500 items per design" and digital download all match the files.

## Listing text

| Rule | Result |
|---|---|
| Title | PASS. 135 chars, leading with "Highland Cow Christmas Clipart". The only words with two capitals are PNG and SVG (2). No "&" and no entities |
| Tags | PASS. 13 unique, the longest "commercial use png" is 20 chars. "commercial use png" is fair, because the licence allows commercial use and the 500-item cap is disclosed in the description and image 5 |
| Price | PASS. $3.49 for 12 designs + SVGs sits just under the ~$3.99 clipart median quoted. It is above the ~$1.75 for 22 designs of the proven set, but this set adds SVGs and a commercial licence. The FACTORY $4.00 rule is for 6-design cut-file bundles |
| Category and type | PASS. 6844, digital, i_did, 2020_2026, not a supply. LISTING.md tells the Lister to tick Etsy's AI disclosure |
| Disclosure | PASS. The last line is exactly "Designed with the help of digital and AI tools, and checked by hand.", with no heading, plain apostrophes and no curly quotes |
| Description | PASS. Accurate: the 12 names match the files; 300 dpi, 3600 px and 12 in are true; there is no text on the designs; the photos are described as showing the designs in use; Duskwood Designs Co is named. LISTING.md matches listing.json |

## README-LICENSE

- **Shop name**: names Duskwood Designs Co (the header and the © line) and the Etsy shop URL. The design list matches the files, and the sublimation, Print Then Cut and SVG notes are correct.
- **Licence**: clear and well structured, with "You may" / "You may NOT" lists.
  - It allows personal use, plus physical items the buyer makes and sells, up to 500 per design.
  - It forbids selling, sharing or giving away the files "alone or in a bundle, or as part of templates, sticker files or other digital products". So reselling the digital files themselves is clearly not allowed. That was the key test, and it passes.
  - It also forbids POD marketplaces, stock sites, AI training, and trademark or logo use.
- **Consistency**: consistent with the listing's LICENSE paragraph and image 5. The listing gives a shorter version (it leaves out stock sites, AI training and logos) but nothing contradicts. It is also consistent with the shop's policy text in `shop-profile/SHOP-PROFILE.md`: 500 items per design is the same cap the shop already uses for cut files, so it isn't really new.
- **FACTORY.md**: no conflict. FACTORY.md sets no licence terms, and nothing in the licence touches its rules.
- **Optional wording**:
  - Say whether "500 items per design" is in total.
  - Say whether a buyer may sell items through their own print-on-demand fulfilment (for example, their own Etsy shop with Printify), as opposed to uploading to POD marketplaces. Buyers in this niche ask.
- **Shop policy**: `shop-profile/SHOP-PROFILE.md` "License (cut files and printables)" has no clipart line. The Manager should add one so the shop policy covers this format. This does not block the bundle.

## formats/clipart.md: a sound spec, with five amendments

The folder layout, cheap recipe ($0.042/design, spend verified), 3600 px / 300 dpi palette PNG under Etsy's 20 MB, the single-path SVG with the honest "not a cut file" framing, the no-text rule, the `FILL_HOLES` / `ERASE_BOX` clean-up steps, the hash check, the category and the listing-image set are all sound. It needs these changes:

- **S1. Halo test.** "≤ 3% paper-white on the outer edge" only catches pure white. It passed 03, which has a light-grey and white fringe on almost every needle tip, and enclosed slivers that `clear_white` skips because they are not joined to the background. Change it to:
  - Count light, neutral pixels near transparency: all channels ≥ 195, tint ≤ 35, within 12 px of alpha < 20. Fail a design over about 5,000 such pixels, or with slivers over 30 px, unless they are listed as art.
  - Add a `CLEAR_BOX` fix: inside a box, make light neutral pixels transparent whether or not they are enclosed. Use it for foliage.
- **S2. Full opacity.** FASTOCTREE quantization puts solid art at alpha 254. After `quantize`, set every palette alpha ≥ 250 to 255. Add a check that at least 99% of pixels with alpha > 127 are exactly 255.
- **S3. Listing images.** The spec's order (collage first, mockup third) conflicts with FACTORY.md "Art quality → Listing photos": the first photo must show the product in use. Make `3-mockup.jpg` photo 1, with a small band or badge carrying the search phrase, "PNG + SVG" and "12 designs" so it still sells at 300 px. The collage becomes photo 2. (Bundle 014 also led with its thumbnail. For the Manager.)
- **S4. `FILL_HOLES` skips `clear_white`.** `process.py` line 56 means any design that needs berries put back gets no white-paper clean-up at all. 11 happens to be clean, but the next set may not be. Run both.
- **S5. Shop licence text.** Add the clipart licence to `shop-profile/SHOP-PROFILE.md` (for the Manager).

## Fixes (required)

1. **White fringe in the foliage, 03 and 10 (and 05's sprigs if cheap)**:
   - Clear the light, neutral paper slivers between the pine needles: a `CLEAR_BOX` over the wreath on 03, and over the two collar sprigs on 10, with the S1 thresholds.
   - Also clear the slivers between 03's fringe strands beside the cheeks.
   - Then check 03 and 10 at 100% on near-black: no white or grey slivers, and the needle tips still intact.
2. **Alpha 254**: after `quantize`, force palette alpha ≥ 250 to 255 (S2), so the solid art in all 12 PNGs is alpha 255.
3. **Photo order**: make the lifestyle mockup photo 1, adding a compact title and "12 designs · PNG + SVG" band so it reads at 300 px. Move the collage to photo 2. Update listing.json `images`, LISTING.md "Photos" and `thumbs.js`.
4. **Rebuild** the PNGs, SVGs, ZIP, contact sheet and listing images (03 is in images 1 and 2, and 10 is in images 2 and 5). Re-run `gen.py --check` with the S1 and S2 checks added, and update formats/clipart.md (S1–S4).

## Optional (not blocking)

5. README licence: add "in total" to the 500-item cap, and one sentence on the buyer's own POD fulfilment.
6. 07: the name could be "Christmas bough" if the tree reading bothers you. The current name is acceptable.

## Would I pay $3.49?

Yes, after fixes 1 and 2. The cows are better than most of the highland cow Christmas PNG results, and the SVG line-art versions are a real extra. As shipped, a buyer pressing 03 onto a black or green sweatshirt would see white flecks all round the wreath and ask for a refund.

**Verdict: REJECTED**
