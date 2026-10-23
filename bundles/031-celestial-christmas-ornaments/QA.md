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
