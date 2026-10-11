# QA: 020 Haunted Gingerbread Houses (round 1)

## Summary
`python3 gen.py --check` prints ALL CHECKS PASS. QA looked at a 1080x720 contact sheet (about 90 dpi), 700-1400 px black-on-white views of 01, 03 and 04, and listing images 1-4 at 900 px. All six read as "gingerbread house gone spooky" at thumbnail size, are single connected silhouettes, and are cuttable. The three points the Designer flagged are real but minor and do not block.

## Technical checks
| Check | Result |
|---|---|
| Parts / validity | PASS. All six are 1 part, valid |
| Smallest hole (limit 600 units2) | PASS. 01: 761, 02: 1176, 03: 834, 04: 859, 05: 773, 06: 1297 |
| DXF | PASS. Re-opens, 9-22 polylines each, about 5.8 in on the longest side |
| PNG | PASS. 1800 px, 04 is 1800x872 (wide panel, documented) |
| ZIP | PASS. 22 entries (SVG, PNG, DXF x6, README-LICENSE) |
| Listing | PASS. Title is exactly 140 chars, 13 tags all 20 chars or fewer, taxonomy 12394, $4.00, exact disclosure line is the last line, 4 images at 3000x2250 |

## Design review (thumbnail and cut)
- **01 Crooked house**: reads. Leaning walls, dripping icing, crescent moon, dead tree, tombstone, bat. The smoke trail is a bit lumpy (chimney tendril with wobbly edge ending in the bat) but it is thick enough everywhere and clearly smoke. The dead tree merges into the left wall, so the left edge is busy. Cuttable. Minor.
- **02 Manor with witch-hat tower**: strongest of the set. Clean silhouette, good windows, candy cane. No issues.
- **03 Spiderweb house**: the round web window does read a little like a wheel or sun at thumbnail size (spokes plus ring plus icing arc around it), but the pumpkin, dangling spider and gingerbread roof carry the "haunted" read, so the design as a whole works. Cut-outs are 834 units2 or more, fine. Minor.
- **04 Village panel**: reads as three houses, moon with bats, bare trees, fence. The windows are small but all at least 859 units2 and the listing already tells buyers to use 10 in wide or larger (and 12 in for wood). Moon-to-tree joins are thin-ish but connected. Acceptable as documented.
- **05 Skull-topped house**: clear, charming, coffin door reads, picket fences are chunky enough. No issues.
- **06 Ornament**: round frame, loop, house, moon, bat, tombstones. Clean and cuttable. No issues.
- **Balance and variety**: five distinct silhouettes plus one panel and one ornament; nothing clipped or crowded. Nothing gory.

## Listing review
- Title: 140 chars, leads with "Haunted Gingerbread House SVG Bundle", has the Gothmas and Halloween and Cricut/laser keywords.
- Tags: 13, unique, relevant, all within 20 chars.
- Description matches the files (names all 6, 4 standing / 1 panel / 1 ornament, sizing and licence). Disclosure line is exact and last.
- No IP: no characters, brands, trademarked phrases or text in the designs ("Gothmas" is a generic seasonal term; "Creepmas" is avoided). Cricut and Silhouette are named only for compatibility, as in earlier bundles.
- Images: lit-shelf lead, what's-included, formats and colour-ideas all show the right designs, are legible and uncropped. The lead is a code-drawn shelf scene, not a lifestyle photo (known gap, same as 008).

## Non-blocking notes
- The description says "6 in on the longest side" but the files measure about 5.85 in because of the design margin. Either say "about 6 in" or scale the artwork to exactly 6 in next time.
- Optional polish: simplify 03's web window (fewer spokes or no outer ring) and smooth 01's smoke edge. Not needed to ship.
- Do the test cuts the LISTING.md notes mention (04 at 10 in in cardstock, one standing house in 3 mm wood) when hardware allows.

**Verdict: APPROVED**
