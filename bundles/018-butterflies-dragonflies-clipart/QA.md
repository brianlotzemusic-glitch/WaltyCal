# QA: 018 Butterflies & Dragonflies Clipart (round 1)

## Summary
`gen.py --check` prints ALL CHECKS PASS, and the ZIP's 12 PNGs are byte-identical to `art/png` (fresh unzip, 7.5 MB, PNG/ x12, SVG/ x12, README). The set is mostly strong: the monarch, morpho, red admiral, caterpillar, coneflower scene and the five dragonflies read well on dark green. Two designs fail the visual review (03 and 06), so the bundle goes back. QA looked at a 300 px-per-design contact sheet on dark green and 100% crops of 03, 06, 11 and 12 on dark green.

## Technical checks
| Check | Result |
|---|---|
| PNGs | PASS. 3600 px, 300 dpi, transparent, largest 1.03 MB, smallest piece 2,929 px, whitest edge 0.00% |
| Halo | PASS. Worst design 801 px, biggest patch 29 px (limit 30, close) |
| Pinholes / opacity | PASS. Lowest interior 99.87%, lowest overall 98.10% |
| Distinct | PASS. Closest pair 08/09 (89 of 1152 bits; both are top-view dragonflies, visibly different colours) |
| SVG | PASS. One path, one colour, print size matches |
| Listing text and images | PASS. Title 135 chars, leads with "Butterfly Clipart", 13 tags, exact disclosure, 6844, $3.49; 5 images at 3000 x 2250; descriptions name all 12 |

## Design review
- **Text, weapons, IP**: none found.
- **Names vs contents**: 01, 02, 04, 05, 07-12 match. 06 "Little blue butterfly" is a dull grey-lilac, not blue (see below).
- **Edge alpha / halos**: no white fringe or specks on dark in the crops. 12 has a pale grey-white patch inside the lily base (bottom petals/lily pad junction) that reads as a smudge, minor.
- **11 damselfly**: six legs on the reed, two eyes, one wing pair visible in side view, plausible. OK.

## Blocking defects
1. **03 Tiger swallowtail, body is split.** At 100% the body is two separate dark vertical strips with transparent background showing between them from the thorax down to the hindwing notch (dark green shows through on the dark crop). It reads as a hollow, broken body and the forewings/hindwings do not join at the centre. Fix: pick another flash draft (`picks.json`) with a single closed body, or close the gap in `process.py` (fill the gap between the strips with the body colour) and re-check on dark.
2. **06 "Little blue butterfly", weakest design and off-name.** The wings are a flat, desaturated grey-lilac (not the soft blue in the subject), with a thick wobbly dark-grey border band that looks like a rough blob rather than a wing edge; it looks washed out beside the saturated others and would not stop a scroller. Fix: use a different draft with true blue wings and a clean thin outline, or one standard `gen` ($0.035) from its prompt; if still dull, replace the design and update subjects, README, listing, LISTING.md and image 3.

## After fixes
Re-run `gen.py` and `--check`, rebuild the ZIP and listing images (03 and 06 appear in the mockup/collage/all-designs images; 03 is in image 2 and 4), and look at both on dark at 100%.

## Optional (not blocking)
- Tidy the grey-white patch in 12's lily base.
- Shop policy still lacks a clipart licence line (S5, for the Manager).

**Verdict: REJECTED**

## Round 2
`gen.py --check` prints ALL CHECKS PASS. A fresh unzip of the ZIP (12 PNG + 12 SVG + README) is byte-identical to `art/png` and `art/svg`; the 03/06 PNGs, SVGs, ZIP, contact sheet and all five listing images are timestamped after the fix commit (12:38-12:41) and show the new 03 and 06 (checked at 600 px: images 1-4 on screen). Halo worst patch is still 29 px (limit 30), no pinholes, lowest interior opacity 99.87%.

- **03 Tiger swallowtail**: fixed. At 100% on dark green the body is now one closed dark shape from thorax to the hindwing notch with no background showing through; wings meet it cleanly. A faint seam line down the middle of the body is visible but reads as shading.
- **06 Little blue butterfly**: fixed. Wings are now a clear cornflower blue with a thin plum outline and veins, clean edges, matches its name. It is the plainest design (flat blue, sparse veins) but is saturated and reads at thumbnail size; a tiny smeared vein near the left wing at 100% is not noticeable at normal size.
- Contact sheet and listing images (mockup, collage, all-designs, PNG+SVG) at low resolution: every design reads, nothing clipped, no white fringe on dark; image 3 and collage show the corrected 03 and 06.
- Not blocking: 12's grey-white lily patch and the missing clipart licence line (S5, Manager) remain from round 1.

**Verdict: APPROVED**
