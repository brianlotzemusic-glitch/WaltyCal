# QA 032 Birdwatching Silhouettes (round 1, 23 Oct 2026)

**Verdict: REJECTED.** Two designs are below the B bar (05, 06); one copy/size decision; then resubmit for round 2. Packaging, listing text and images are sound.

## Must fix
1. **05 Flock disc, top-right (largest) bird is malformed.** At 100% (PNG ~x 1150-1460, y 270-480) its right wing ends in a forked "antler" tip and has lumpy bumps along the wing, so it reads as a deer or dragon, not a bird. Redraw that bird with a clean single tapered wing tip. Also the birds' 'M' wing-base wiggles (a small double bump at the centre of every bird) look like a wobble, and the spike body under each reads pterodactyl/gull. Replace the wiggle with one smooth shallow V and give each bird a short rounded body, not a long hanging spike. Re-run gen.py --check.
2. **06 Heron in flight, neck and head.** At 100% (x 250-800, y 950-1350) the neck sags below the body line in an S with a bulbous head and a sharp notch where neck meets the shoulder (about x 595, y 1150). It reads as a drooping neck, not a tucked heron neck. Raise the neck into a smooth S (head above body line), fillet the notch with the same radius as other joins, and keep the bill. The thin slit in the upper wing (about 0.07 in wide at 6 in, x 760) should be widened to about 0.10 in.

## Decision: firmer minimum width (answered)
Measured on the 300 DPI PNGs by morphological opening: only the tips are under 0.07 in (about 0.05 in at the very ends); at 0.09 in the loss is tips plus, in 01, the upper reed and cattail stalks (stems run about 0.07-0.10 in) and the 06 slit. At 4 in those stalks are about 0.05-0.07 in (1.3-1.8 mm), which is too fragile for laser wood or acrylic and fiddly for vinyl weeding. Required: (a) in gen.py set a firmer floor so tips are rounded at no less than 0.08 in (match 031) and 01's reed and cattail stalks are at least 0.10 in at 6 in; (b) change the copy in LISTING.md, listing.json and README to: "Fine tips taper to about 0.08 in at 6 in; we recommend 5 in or larger for cardstock and vinyl and 6 in for laser-cut wood or acrylic." Keep README to sizes only. The 05 disc cutouts (bird wings 0.05-0.1 in wide) are waste slivers: fine for laser, hard to weed in vinyl at under 5 in, which the 5 in minimum covers.

## Should fix (smaller)
- 04 wren: tail tip is flat-topped with sharp corners; round or taper it. Cartoonish but reads as a wren: B, keep.
- 01: two small notches where neck meets body (x 555, y 720 and x 695, y 630); fillet them.
- 02: tiny notch where head meets wing (x 260, y 1030); fillet.
- 03: tail notches are crisp and fine; leaves/flower a little generic but clean.

## Per-design grades (QA)
01 B+ (recognisable heron, believable; reeds thin), 02 A- (clean swallow), 03 B+ (clean; bill about 0.1 in), 04 B, 05 C+ (top-right bird, wiggles) FAIL, 06 B- (neck) FAIL.

## Checked and passing
- gen.py --check ALL CHECKS PASS: 1 part each; holes: 01 one (10484 units2), 04 two incl. the eye (907, over 600), 05 eight (min 2640).
- SVG: 6 valid XML, 1 path each, width/height 6.000in, closed subpaths. DXF: 6 files, INSUNITS inches, re-open in ezdxf, width 5.95 in, polyline counts match holes+1. PNG: 1800x1800 RGBA, transparent corners, clean edges.
- ZIP: 22 entries (3 folders + 18 files + README = 19 files) byte-identical to bundle/; matches LISTING.md.
- README-LICENSE.txt: formats, sizes, software, licence only. Must be updated with the size sentence above.
- Listing images 1-4: 3000x2250 RGB, opaque, 243-317 KB, no text overlap. Image 1 is a flat preview of the six real files (no scene). 2-4 show only included files. Images 1-4 must be regenerated after the redraws (05, 06 appear in all four).
- Title 126 chars, no brands or IP (heron, swallow, hummingbird, wren are generic). 13 tags all <= 20 chars. Taxonomy 12394, price $4.00. Disclosure line last, mockup sentence present, description identical in LISTING.md and listing.json.
- No functional-guide content (Etsy AI policy).

## Open questions
- Lister: does it tick Etsy's AI checkbox and "Designed by"? (unchanged)
- No paid actions, no live Etsy edits; Ads test runs until 24 Oct.

## Designer log, round 2 (23 Oct 2026)
Applied all round-1 fixes: 05 flock redrawn (one gull-V bird, 7 birds, no merging, checked), 06 S-neck raised/filleted/slit ~0.10 in, tip floor 0.08 in (gen.py MIN_TIP), 01 stalks >= 0.10 in, 01/02 notches filleted, 04 tail tip pointed; copy updated in LISTING.md, listing.json, README; ZIP and images 1-4 rebuilt; gen.py --check passes (new tip-floor, stalk and flock-gap checks). Self-grade 05 B+/A-, 06 B+. Awaiting QA round 2. Not published.

## QA round 2 (23 Oct 2026)
**Verdict: REJECTED (one design, small fix).** 06 is below B because of two new artifacts. All else passes.

### Must fix (06 only, then resubmit round 3)
1. **06 lower (rear) wing tip has a round bead** (PNG ~x 1760-1790, y 855-880): a dot ~0.04 in wider than the tapering wing, joined by a visible neck. The 0.08 in tip rounding produced a ball on the tip instead of a rounded taper. Fix the tip so the wing ends in a single smooth taper/rounded end (no ball). Visible in all 4 listing images.
2. **06 head crown has a nick** (PNG ~x 320-335, y 775): two lobes meet at a sharp notch on top of the head. Merge into one smooth dome (fillet or re-draw the crown). Also soften the sharp shoulder corner at about x 700, y 1050.
After the fix: re-run gen.py --check, rebuild ZIP, regenerate images 1-4 (06 appears in all), crop-check 06 again at 100%.

### Per-design grades (100% crops, white-flattened PNG, plus 4x on joins)
- 01 B (heron believable, stalks now clear; tiny rounded nubs on the baseline at x 225/330/1730, y ~1690 are cosmetic; neck notches filleted)
- 02 A- (swallow fillet and head notch smooth, no kinks)
- 03 B+ (unchanged, no regression)
- 04 B (tail now tapers to a rounded point; wren reads well; eye hole intact)
- 05 B+ (7 smooth gull-V birds, no fork, no wiggle, all separate, reads as a flock; thin wings but fine at 5 in+)
- 06 B- FAIL (S neck, filleted notch and ~0.10 in slit are good; bead and crown nick above)

### Checked and passing
- gen.py --check: ALL CHECKS PASS (1 part each; holes 01:1, 04:2, 05:7; no new files modified).
- SVG: 6 valid XML, 1 path each, 6.000in square, subpaths closed (M count = Z count). DXF: 6 files, INSUNITS inches, closed LWPOLYLINEs, width 5.95 in, counts = holes+1 (05 has 8). PNG: 1800x1800 RGBA, transparent corners, clean edges.
- ZIP: 22 entries (testzip OK), every file byte-identical to bundle/; matches LISTING.md.
- Listing images 1-4: 3000x2250 RGB opaque, no text overlap, only included files shown. Image 1 is a flat preview showing the redrawn 05 and 06 (06's bead barely visible there).
- Copy: the exact min-size sentence is in LISTING.md, listing.json and README (README still formats/sizes/licence only); description identical in LISTING.md and listing.json; mockup sentence present; disclosure line last; title 126 chars, 13 tags <= 20, price $4.00, taxonomy 12394.
- No paid actions, no live Etsy edits.

### Open questions
- Lister: tick Etsy AI checkbox / "Designed by"? (unchanged). Do not publish before the Ads test ends 24 Oct.

## Designer log, round 3 (23 Oct 2026)
06 only: rear wing tip now one smooth rounded taper (tip 15 units, was a 12-unit cap beaded by the 0.08 in opening); crown nick came from the eye hole breaking through the thin wall, so the (already vanished) eye is removed and head + neck end share one convex dome; core fillet 16 -> 30 softens the shoulder. 100% crops of head, neck S, bill, wing slit and tip checked clean. gen.py --check passes, ZIP and images 1-4 rebuilt (3000x2250 opaque), other designs byte-identical. Self-grade 06 B+. Not published.
