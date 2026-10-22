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

---

# QA 030 Mushroom Clipart (round 2, 22 Oct 2026)

**Verdict: APPROVED.** All five round-1 must-fixes are resolved. No blocking issues; two optional nits below.

## Round-1 fixes, verified
1. **Design 01 fly agaric (new scaly volva).** Viewed at 100% on dark green and on magenta (volva, cap, gills, ring, leaves). The base is now a swollen bulb with rows of white scales and a plum underline: reads as a fly agaric volva, no anatomical joke. Edges are clean on both grounds, no paper fringe. SVG rendered at 3600 px: clean single-colour line art, the same scales, no stray blobs.
2. **Design 12 parasol (plain stem with fern tufts).** The swirl-filled bulb is gone: a plain stem with a rounded foot, two rings, fern tufts at the left and right. Clean edges on dark and magenta; SVG renders cleanly at 100%.
3. **Listing image 5.** Layout redone, no overlap: all six bullets and dots visible, "3600 px" intact, art sits left and bottom right.
4. **README-LICENSE.txt.** Only FILES, FILE FORMATS AND SIZES, COMPATIBLE SOFTWARE, designs list, not-identification note and licence remain. No how-to steps.
5. **Tag.** "foraging clipart" replaced by "mushroom art" (13 tags, all <= 20 chars; no foraging, edibility or ID wording).

## Independent checks
- **HALO_OK.** The new 01 boxes are very large (cap 0-1000 and rim 1000-2400 span the full width, volva 500-2300 x 2550-3600), so the halo test is effectively off for 01. I re-ran the halo mask with no boxes: all hits sit on real white/cream art (warts, rim, gills, ring, volva scales) and I found no paper fringe on dark or magenta at 100%. 12's boxes (stem highlights at 600-1100 x 2700-3200, foot) hold only pale stem highlights; unboxed 12 has one 196 px patch, harmless. Nothing real hidden. Suggestion: tighten 01's boxes later; not blocking.
- **PNGs.** 12 of 12 PNGs and 12 of 12 SVGs in the ZIP are byte-identical to art/png and art/svg (ZIP names carry a "mushroom-" prefix); README identical. ZIP = PNG x12 + SVG x12 + README only.
- **Listing images.** All five are 3000x2250 RGB, opaque, >= 2000 px both sides, 1.0-3.5 MB. Image 1 is a flat white-ground preview of the real PNGs, showing the NEW 01 (scaly volva) and 12 (plain stem). Image 2 shows 01 on checker/green/SVG plus four SVGs; image 3 is a composite with the new 01 and no text overlap; image 4 shows the real SVGs; image 5 as above. No text overlaps anywhere.
- **LISTING.md vs ZIP/listing.json.** Counts, 300 dpi, 3600 px, formats match. Title 125 chars with no edibility/ID claims; "fly agaric" and the mushroom names are species art names, and the description says "not mushroom identification pictures". Disclosure line is last; mockup sentence present. Taxonomy 6844, price $3.49, who_made i_did.
- `python3 gen.py --check`: ALL CHECKS PASS.

## Description: "ready for sublimation, print and print-then-cut"
**Acceptable, no change required.** It is one short factual use-case/compatibility phrase (what the file is suitable for), with no steps, settings or instructions; Etsy's rule bans step-by-step craft instructions, and FACTORY.md allows formats, sizes and software names. If the Manager wants zero risk, the neutral version is: "12 PNG files, transparent background, 300 dpi, 3600 px on the longest side (12 in)". Not required.

## Optional nits (not blocking)
- 12: a tiny scribble reading like "0.9" on the upper ring (about 25 px at 100%) and a faint ghost smudge in the fern. Invisible at listing size.
- 01: a few stray hatch strokes on the volva; reads as texture.
- Image 5 has empty space lower left; fine.

## Open questions for the owner/Manager (unchanged)
- Does the Lister tick Etsy's AI checkbox and "Designed by"? (LISTING.md says yes.)
- Etsy's image-requirements page was still not retrievable; the bundle meets 2000 px and opaque anyway.
- Images 1 and 3 are over 1 MB; consider JPG if uploads are slow.
