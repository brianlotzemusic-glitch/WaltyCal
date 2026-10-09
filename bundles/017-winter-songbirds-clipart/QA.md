# QA: 017 Winter Songbirds Clipart (round 1)

## Summary
A clean third clipart set. The 12 designs read at a glance on dark green and cream, the cut-outs are clean, and the files, ZIP, listing images, copy and licence agree. QA ran `gen.py --check` (ALL CHECKS PASS), unpacked the ZIP into a scratch dir and compared every PNG to `art/png` (all byte-identical, names carry a `songbirds-` prefix; ZIP is PNG/ x12, SVG/ x12 and the README, 7.9 MB). QA looked at a 330 px-per-design contact sheet on dark green, the listing images at 600 px, and 100% crops of 11 (needles, the edge-snapped design) with no defect found. No blocking defect.

## Technical checks
| Check | Result |
|---|---|
| PNGs | PASS. 3600 px, 300 dpi, transparent, trimmed, largest 0.84 MB, smallest piece 10,173 px, whitest outer edge 0.00% |
| Halo | PASS. Worst design 1,733 light px near transparency, biggest patch 19 px. Two `HALO_OK` boxes (08 cream holly in the beak, 11 cream stem), both real plum-outlined light art |
| Pinholes | PASS. None under 60 px |
| Opacity | PASS. No alpha 250-254; lowest interior 99.56%, lowest overall 98.08% (11, just over the 98% bar thanks to `EDGE_SNAP` on 02 and 11; needle edges are ~1 px crisper, no fringe on dark at 100%) |
| Distinct | PASS. Closest pair 05/10, 260 of 1152 bits |
| SVG | PASS. One path, one colour, no text or image, print size matches |
| Spend | PASS. $0.504 for 12 designs ($0.042 each), under $0.05 |
| Listing text | PASS. Title 131 chars, leads with "Cardinal Clipart", only PNG and SVG in capitals, no "&"; 13 unique tags, longest 19; disclosure line exact; 6844, $3.49, i_did, 2020_2026; LISTING.md matches listing.json; description names all 12 |
| Listing images | PASS. 5 at 3000 x 2250. Image 1 shows the real PNGs on a tee, card and tote (product in use, "12 designs" badge reads at thumbnail size); 3 numbers and names match the README |

## Design review
- **Text, weapons, IP**: none. Generic songbirds, a birdhouse and holly. No brand or character resemblance.
- **Anatomy**: good. Every bird has one head, one beak, two eyes (owl has two big eyes), two wings and plausible legs. 08's flying cardinal is a clean wing-spread pose with legs tucked. 09's small bird in the entrance reads clearly. 03's blue-grey crown is stylised (disclosed in the listing as "stylized clipart look rather than field-guide illustrations"). Acceptable.
- **Designer's flagged points**:
  - **11 name**: the design holds three tiny birds, so "Pine cone sprig" under-describes it. It reads as an attractive pine sprig with a cardinal, bluebird and orange bird, and it is not misleading enough to block. Optional: rename "Pine sprig with birds" in subjects.json, README, listing, LISTING.md and image 3.
  - **08 beige holly**: reads as frosted holly, fine. **12 plum-red holly**: reads fine.
  - **04 sprig, 02/11 needles**: clean at 100% on dark, no pale rim.
- **Mockup honesty**: the tee shows 01, the card 07 and the tote 10, all real files; description says digital files only.

## Fixes
None required.

## Optional (not blocking)
1. Rename 11 to "Pine sprig with birds" everywhere.
2. Shop policy still lacks a clipart licence line (S5, for the Manager).

## Would I pay $3.49?
Yes. Clear theme, good variety (singles, flight, scene, props), clean files and SVGs, commercial licence.

**Verdict: APPROVED**
