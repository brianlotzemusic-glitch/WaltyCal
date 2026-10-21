# QA: 027 Winter Botanical Wall Art, set of 3 ($5.00)
Independent QA, 2026-10-21. Verdict: **REJECTED round 1 (3 small text fixes, art and files are fine)**.

## Checked and OK
- `gen.py --check`: ALL CHECKS PASS. It needs `out/` (not committed), so I ran it on an extract of the shipped ZIP rebuilt into `out/`: 15 JPG + 5 PDF + README, 19.18 MB (under 20 MB), pixel sizes, 300 DPI tag, ratios, PDF page sizes, title/13 tags/disclosure/taxonomy 2078/price/images 3000x2250.
- Art: contact sheet and 100% crops of all three at 2:3. No garbled shapes, extra limbs or stray marks. The fern is slightly crystalline and the rose petals mushy at 100%, both fine for wall art viewed at normal distance. Background is the same #152444 on all three.
- Cohesion: good palette and background. Weaker points: the pine is clearly narrower and smaller than the fern and rose, and the rose has more colour and heavier outline than the other two. Acceptable as a set; not a reject.
- Ratios and sizes in LISTING.md match the ZIP and README. "About 300 DPI up to roughly 11x14" is honest (art core 3186x4096). The 24x36 JPG is about 183 DPI on the canvas and the art is an enlargement; the listing says so. ACCEPTABLE: it is stated, and the spec's "300 DPI at 24x36" cannot be met with a 4096 px upscale.
- Lead image (code-drawn room): clean, shows the real art, readable at thumbnail. Flat and basic but honest; accepted for this pilot given credits. Images 2 and 4 clean.
- Listing text: no trademark/IP phrases, no medical claims, disclosure line present, 13 unique tags, title 130 chars. "Christmas rose" is the plain flower name; fine.
- Price $5 for 3 prints x 5 ratios + PDFs: plausible for the niche (sets of 3 usually $3 to $8); I did not look up competitors live.
- art/unified/ (38 MB) not a QA concern.

## Fix before approval
1. LISTING.md and listing.json (keep them identical, gen.py checks that): the PDFs are about 80 to 130 DPI at their largest size, but the listing only says "set to the largest size of that ratio". Change the PDF bullet to say they are lighter files for print shops and smaller sizes, and add to GOOD TO KNOW: "Use the JPG files for the best quality; the PDFs are lower resolution." Same honest wording as README.
2. listing-images/3-sizes.png: "Fits every standard frame" and "so you never have to crop or resize" are overclaims (no 5x7, 8.5x11, 50x70 cm etc., and the buyer must scale/fit). Change to "Fits most standard frames" and e.g. "Five ratios included, sized for popular frames". Re-run listing_images.py; 3000x2250 check must still pass. Optional: the big empty band between the ratio labels and the bottom panel looks unfinished.
3. Image 2 says "15 high-res JPGs": fine, but "any size from 4 x 6 to 24 x 36 in" next to it should read "most sizes from 4 x 6 to 24 x 36 in".
No art change needed. Rebuild the ZIP only if README changes (it does not need to).

## Notes for Manager
- `gen.py --check` cannot run from a fresh checkout (out/ absent, 4x originals deleted). Not blocking.
- Ads test until 24 Oct: nothing touched on Etsy.

## Round 2 (2026-10-21): **APPROVED**
- Fix 1 verified: LISTING.md and listing.json PDF bullet now says lighter, lower-resolution (about 80-130 DPI at largest size), use JPGs for best quality; GOOD TO KNOW line added. Description text in LISTING.md and listing.json is byte-identical (checked by script). Title 130 chars, 13 tags unchanged.
- Fix 2 verified (viewed at low-res): image 3 reads "Fits most standard frames" / "Five ratios included, sized for popular frames". Layout intact; the empty band is still there (optional, not blocking).
- Fix 3 verified: image 2 reads "most sizes from 4 x 6 to 24 x 36 in". Images 1 and 4 not modified. All four images 3000x2250.
- ZIP unchanged vs round 1 (git diff empty, 19,178,013 bytes = 19.18 MB, under 20 MB). No new problems found.
- Still true: no Etsy edits made; upload and publishing remain a Manager/owner decision.
