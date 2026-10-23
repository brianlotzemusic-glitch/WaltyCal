# QA 031 Celestial Christmas Ornaments (round 1, 23 Oct 2026)

**Verdict: REJECTED.** Two design fixes, then resubmit for round 2. Packaging, listing text and images are sound.

## Must fix
1. **Design 03 Celestial Wreath reads as a pentacle / ship's wheel.** An upright five-point star in a circle with five spokes running from its points to the ring is a pentagram-in-circle at thumbnail size (seen in images 1-4), not a Christmas wreath; the ring also has a mix of 5-point and 4-point stars with lumpy joins. Redraw: use an 8-point star or crescent at the heart with 4 or 8 spokes (not 5 from star points), or drop the spokes and hang the centre star from the ring with two short bridges; keep the star-studded ring.
2. **Design 06 Moon Over Pines, hanger joins.** At 100% the ring has knob-like bumps where the moon and the two hanging-star strings join (top left near x 1300 and x 1640/1780 of the 3600-wide sheet), plus a tiny white nick at the top centre of the ring. Smooth these joins (same fillet as the loop) and re-run `gen.py --check`. Also thicken the hanging-star strings a little (they sit at the 0.08 in minimum).

## Should fix (smaller)
- 05 starburst and 04: slight bumps on the loop neck (visible in the 100% view); smooth with the same fillet.
- 06: left tree stands on a very thin ground line; widen it a touch.

## Checked and passing
- All 6 SVGs valid XML, one path each, viewBox 6.000 in; PNGs 1800x1800 RGBA, transparent corners, clean edges; DXFs 6 in, units = inches, re-open in ezdxf; `gen.py --check` ALL CHECKS PASS (1 part each, smallest hole 827 units², over 600).
- Designs 01, 02, 04, 05 recognisable, balanced and attractive; 01 star is attached to the moon, 02 bauble cap and slot are clean, 04 phases read well.
- ZIP: SVG x6 + PNG x6 + DXF x6 + README = 19 files; byte-identical to bundle/, matches LISTING.md.
- README-LICENSE.txt: formats, sizes, software and licence only, no craft how-to.
- Listing images 1-4: 3000x2250 RGB, opaque, 288-352 KB, no text overlap. Image 1 is a flat, accurate preview of the six real designs (no scene). Images 2-4 show only included files.
- Title 134 chars, no brands or IP, no craft-instruction words. 13 tags, all <= 20 chars. Taxonomy 12394, price $4.00. Disclosure line is last; digital-mockup sentence present.

## Disclosure wording
The art is geometry written in code with an AI assistant. Keep the exact mandated line ("Designed with the help of digital and AI tools, and checked by hand for clean cuts."): it is true and the "digital tools only" variant would under-disclose. Owner may overrule.

## Open questions
- Does the Lister tick Etsy's AI checkbox and "Designed by"? (Image requirements page still unconfirmed by Etsy.)
- No live Etsy edits made; Ads test runs until 24 Oct.

---

# QA 031 (round 2, 23 Oct 2026)

**Verdict: APPROVED** (no blocking fixes). Both round-1 rejections are resolved; optional polish listed below.

## Round-1 must-fix items, checked at 100% crops of the final PNGs
- **03 Celestial Wreath:** now an 8-point compass-style star whose points run into a ring studded with 12 stars (mix of 5-point and 4-point, evenly spaced), hanger at top. No pentagram, no 5 spokes. Reads as a compass/starburst wreath; at thumbnail size (images 1-4) it can faintly suggest a wheel because of ring plus 8 tapered rays plus rim studs, but the star-shaped studs and star centre keep it on the celestial side, and nothing occult remains. Joins are small and clean (tiny 45-degree chamfers where star tips meet the ring, no knobs). Ring about 0.2 in wide, smallest hole 1248 units^2.
- **06 Moon Over Pines:** knobs and top-centre nick gone. Both hanging-star strings start inside the ring with clean fillets, 30 units wide (about 0.18 in), stars attached. Moon joins the ring through a short stub; the moon-to-ring slit is about 0.12 in at 6 in (25-unit gap): fine for laser/Cricut at 6 in, tighter (about 0.08 in) at the 4 in minimum, still cuttable but fiddly to weed in vinyl. Left tree ground line still thin-ish but sound.

## Other checks (all pass)
- `gen.py --check`: ALL CHECKS PASS, 1 part per design, smallest hole 827 units^2 (02), valid.
- SVG: 6 files, valid XML, 1 path each, closed subpaths only (path subpath count = Z count), width/height 6.000in. DXF: 6 files, INSUNITS 1 (inches), MEASUREMENT 0 (imperial), reopen in ezdxf, extents 4.5-6.0 in, polyline counts match holes+1. PNG: 1800x1800 RGBA, transparent corners, clean antialiased edges.
- 01, 02, 04: no regression from the fillet change (loop necks smooth, bauble cap/slot clean, phases clear). 05: loop neck now has a small waist pinch where the fillet meets the star tip (visible at 300% only, about 0.09 in wide at the narrowest, not a cut problem). Cosmetic, non-blocking.
- ZIP: 22 entries = 3 folder entries (SVG/, PNG/, DXF/) + 6 SVG + 6 PNG + 6 DXF + README = 19 files. Consistent with round-1 "19 files"; LISTING.md makes no file-count claim, so no mismatch. Contents byte-identical to bundle/ (unzipped and diffed).
- Listing images 1-4: 3000x2250 RGB, opaque, no text overlap. Image 1 is a flat, accurate preview showing the NEW 03 and 06. Images 2-4 also show the new 03/06 and only included files.
- LISTING.md vs listing.json: description identical, title 134 chars, 13 tags (max 19 chars), price 4.00, taxonomy 12394. "Eight-point star at its heart" and the 06 description match the redrawn art. Disclosure line last; mockup sentence present.
- README-LICENSE.txt unchanged: formats/sizes/license only.

## Optional polish (not blocking)
1. 05: remove the slight pinch at the loop neck (extend the fillet radius).
2. 06: tidy the ground line under the left tree (flat then slight slope near x 690 looks like a kink); widen the moon-ring slit to about 30 units if wood/acrylic cutting at 4 in is expected.
3. 03: if the owner still sees a ship's wheel, drop 4 of the 12 rim stars (keep only the diagonal ones) for a more snowflake feel.

## Open questions
- Lister: AI checkbox and "Designed by" on Etsy (unchanged from round 1).
- No paid actions, no live Etsy edits made.
