# QA 030 Mushroom Clipart (round 1, 22 Oct 2026)

**Verdict: REJECTED.** Four fixes, then re-submit for round 2. The rest of the bundle is sound.

## Must fix
1. **Design 01 fly agaric, base.** The brown three-lobed bulb reads as an anatomical joke at thumbnail size, and the SVG line art (listing image 2, top right) reads worse. A fly agaric volva is a swollen base with scaly rings/warts, not a smooth lobed lump. Redraw or re-roll the base (or drop the design for another). It is the hero of photos 1, 3 and 5, so it matters most.
2. **Design 12 parasol, base.** A teardrop bulb filled with swirls, sprouts and leaves, crossed by the stem's wavy brown bands: nonsensical AI artefact, not a mushroom part (100% crop). Redraw the base as a plain stem or bulb, or replace the design.
3. **Listing image 5 (what you download).** The big fly agaric overlaps the text: the first bullet dot is hidden and "3600 px" shows as "600 px". Fix the layout. Re-check all five images for overlaps after the fly agaric change.
4. **README-LICENSE.txt and "foraging clipart" tag.** "USING THE PNG FILES / USING THE SVG FILES" has how-to steps (print mirrored onto sublimation paper and press onto white polyester; print-then-cut upload steps; "embroidery templates"). Etsy's new rule wants formats, sizes and software names only. Cut those sections down to a list of formats, sizes and compatible software. Also replace the tag "foraging clipart" (it points at foraging and identification) with something neutral such as "mushroom art" or "toadstool png".

## Should fix (smaller)
- Design 06 puffball: the lone yellow dot on top and the striped orange blob behind look odd (read as an eye or nipple). Remove the dot or accept at the Designer's discretion.
- Design 09: tan fills showing between the fern fronds (colour not matching the outline) at 100%. Visible only on dark, so minor.
- Design 11: stray ring and flat near-white patch on the left stem, minor.

## Checked and passing
- ZIP: 12 PNG + 12 SVG + README only, PNGs byte-identical to art/png, matches LISTING.md (counts, 3600 px longest side, 300 dpi, 20 MB limit fine).
- PNGs: palette-mode with alpha, transparent corners, 24-69% transparent, 0.3-1.3% semi-transparent edge pixels (clean anti-aliasing). No opaque backgrounds.
- SVGs: all 12 parse as valid XML, one path each, one colour (#2c1b36), no gradients or embedded images; claim "one-colour, single layer" is true. Honest "not a vinyl cut file" note.
- HALO_OK boxes: viewed honey-fungus (pale sage fern, clean edge on a dark ground, no paper fringe) and the ferns and grass of 09. They look like real art, not hidden defects. The tiny 07 and 12 highlight boxes are 30-45 px, harmless. Did not crop designs 07 and 12 highlights individually.
- Etsy rules: no pattern/recipe/tutorial product (apart from README steps above); disclosure line is last; mockup sentence present; photo 1 is a flat, accurate preview of the real PNGs; all five images 3000x2250 RGB opaque PNG (each under 3.4 MB; photos 1 and 3 are over 1 MB, which Etsy says may fail on slow connections: consider JPG); photo 3 is a composite of five real files, covered by the mockup sentence; all images show only included files.
- Title 125 chars; 13 tags all <= 20 chars; no brands/IP; nothing implies edibility, and the description carries "not identification pictures". Taxonomy 6844 (Clip Art & Image Files) verified with tools/etsy.py. Price $3.49. who_made i_did, AI checkbox noted in LISTING.md.

## Open questions for the owner/Manager
- Does the Lister set Etsy's AI checkbox and "Designed by" (the research report asks)?
- Etsy's image-requirements page was not retrievable, so the 2000 px and opaque rules are unconfirmed by Etsy itself; this bundle meets them anyway.
