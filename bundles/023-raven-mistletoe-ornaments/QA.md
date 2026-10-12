# QA: 023 Raven & Mistletoe Ornaments (round 1)

## Summary
`python3 gen.py --check` prints ALL CHECKS PASS. QA viewed a 1080x720 contact sheet (360 px cells, about 60 dpi), a 120 px (20%) strip, 600 px views of 02, 03 and 06, and listing image 1. The files are technically clean and 01, 04 and 05 are good, but 06 does not look good enough to sell, 02 and 03 are only so-so, and the mistletoe does not read as mistletoe in any design.

## Technical checks
| Check | Result |
|---|---|
| Parts / validity | PASS. All six: 1 part, valid |
| Smallest hole (limit 600 units2) | PASS. 01: 1011, 02: 659, 03: 1248, 04: 772, 05: 850, 06: 881 |
| DXF / PNG | PASS. 5-9 polylines, 5.98 in; PNG 1800x1800 |
| ZIP | PASS. 22 entries |
| Thin parts | Raven toes and mistletoe stems about 0.08 in at 6 in, connected, cuttable with the 4 in / 4.5 in advice. The only cut detail on a bird is a round eye (about 0.18 in), so the 022 lesson was applied |

## Design review
- **01 Moonlit raven on a branch**: good. Clear perched raven, crescent moon, ring. Nit: the branch ends poke out past the ring on both sides (small stubs, same kind of thing flagged in 021 round 1); acceptable but trim them or shorten the branch.
- **02 Raven bauble**: so-so. A cut-out flying bird in a bauble reads as a bird, but the wing and tail edges are ragged, with sawtooth feather spikes and a notched tail, and the body is stubby with a short beak, so at 20% it looks more like a dove or pigeon than a raven. Smallest star is 659 units2, only just over the limit. Needs a bolder raven (longer heavy beak, fingered wingtips, smoother edges).
- **03 Raven lantern**: acceptable. The lantern and candles read well and the perched raven on top is good. But the raven is small and thin-legged next to the lantern, and the mistletoe is stuck on the right side like a floating decoration. It is the thinnest design (at 4 in the raven is tiny). Minor, would improve with a larger raven.
- **04 Gothic window ravens**: good. Two ravens beak to beak under the arch, reads clearly. The splayed feet at the bottom corners are a little odd but fine.
- **05 Raven on the moon**: strong. Bold moon, clear raven, stars. No issues.
- **06 Mistletoe wreath raven (FAIL)**: the weakest. The wreath is a lumpy, wobbly ring of blobs that reads as seaweed or a sponge, not mistletoe, and the flying raven is a big blob whose wing, back and tail merge into the wreath on the top and left, so the bird silhouette is lost. The cut-out between the wing and the wreath is an irregular jagged shape. At 20% it is a dark mass with a beak. I would not pay for it.
- **Mistletoe overall**: the four blunt paddle leaves with berries read as a flower or a bow at 20% in 01, 02, 03 and 04. The listing and description sell "mistletoe", so it must be recognisable. Use two or three clearly paired oval leaves on a forked stem with a berry cluster (bigger berries as round cut-outs or attached dots), or a clear sprig shape.
- **Set**: five round / compact ornaments plus the lantern; variety is good.

## Listing review
- Title: 132 chars, one '&', leads with "Raven Ornament SVG Bundle". PASS.
- Tags: 13, unique, each 20 chars or fewer (longest "laser cut ornament", 18). PASS.
- Description: says "about 6 in", names all 6, sizing tip, licence, digital download, exact disclosure line is the last line. PASS. "Stars, moons... attached" wording is fine. Update the 06 and mistletoe text if they change.
- Price $4.00, taxonomy 12394. PASS.
- No IP: no text, no quotes ("Nevermore" avoided), no brands. PASS. "Creepy christmas" tag is fine (not "Creepmas").
- Image 1 (lead): nicely composed on purple with 05, 04 and 01 filling the frame, legible, title readable. Code-drawn rather than a lifestyle photo (known gap, same as 008/020/021/022). PASS. Images 2-4 must be rebuilt after any redraw.

## Required fixes
1. Redraw 06: a clean, evenly sized mistletoe wreath (or leaf ring) with a clear gap between the ring and the bird, and a raven whose wing, body and tail stay separate from the ring and smooth-edged, so the bird reads at 20%.
2. Redraw the mistletoe sprig used in 01, 02, 03, 04 so it reads as mistletoe (paired oval leaves, forked stem, visible berries) at 20%.
3. 02: bolder raven (heavier beak, smoother wing and tail edges, fewer sawtooth spikes); make the stars comfortably above 600 units2.
4. 03: enlarge the raven and attach the mistletoe more convincingly (or move it under the lantern roof).
5. 01 nit: trim the branch ends that poke outside the ring.
6. Rebuild PNG/DXF, ZIP, listing images 1-4, update LISTING.md/listing.json text, re-run `gen.py --check` and resubmit.

**Verdict: REJECTED**
