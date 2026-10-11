# QA: 021 Woodland Reindeer & Stag Ornaments (round 1)

## Summary
`python3 gen.py --check` prints ALL CHECKS PASS. QA looked at a 1080x720 contact sheet (3x2, 360 px cells), a 120 px thumbnail strip (about 20%), 800 px views of 04, 05 and 06, and listing image 1 at full size. The files are technically clean, but three of the six deer do not look good enough to sell and the lead image is half empty. 02, 03 and 05 are good.

## Technical checks
| Check | Result |
|---|---|
| Parts / validity | PASS. All six are 1 part, valid |
| Smallest hole (limit 600 units2) | PASS. 01: 918, 02: 1078, 03: 1215, 04: 1511, 05: 1248, 06: 1249 |
| DXF | PASS. 5-13 polylines each, about 5.97-5.98 in |
| PNG | PASS. 1800x1800 each |
| ZIP | PASS. 22 entries |
| Thin parts | PASS on paper. Antler tines and legs are about 13 units (0.08 in at 6 in). Cuttable with the 4 in / 4.5 in advice, but 01 and 06 antler tips are very fine |
| 04 hanging hole | Present and connected (0.25 in hole in the back, 1511 units2 hole area). Cuttable, but see design note |

## Design review
- **01 Stag head**: reads as a stag at thumbnail, antlers are good. The face is the problem: narrow slit eyes make it look glaring or sleepy and slightly creepy, and the holly at the base is a lumpy blob that does not read as holly. Antler tips run into the ring at the top. Needs a friendlier face and a clearer holly sprig.
- **02 Leaping reindeer**: good. Clear leaping pose, moon, star, pines. The front hooves merge into a small tree at lower left (a bit fussy) but fine. Minor.
- **03 Woodland stag**: good. Clean standing stag, pines, moon. No issues.
- **04 Reindeer with scarf**: weakest of the set. At thumbnail the scarf is a floating black blob with tendrils, the head is small and blocky with a flat muzzle, the neck is long and the body narrow, and the 0.25 in hole sits mid-body like a spot rather than a hang point. The legs are long and spindly and the base is a plain slab. Does not look like something I would pay for. It is also the only non-round, non-hanging-loop design, so it does not fit the set. Redraw (better head and neck, scarf attached to the neck and clearly a scarf, hole positioned where it hangs level) or replace with a round-frame design.
- **05 Stag bauble**: strong. Cut-out stag head in a bauble with snowflakes, reads instantly. No issues.
- **06 Reindeer pair**: the scalloped frame and star are nice and the pair reads as two deer, but the legs are tiny stick forms, and there are odd little hoof/leg stubs poking out of the frame at lower left and right that look like insects. The empty gap between the two deer looks like a stray tall blob. Fix by keeping the legs inside the frame (or removing the stubs), thickening legs, and filling or reshaping the centre gap (for example a pine between them).
- **Balance and variety**: five round ornaments plus one standing shape. Fine, if 04 is redrawn as an ornament.

## Listing review
- Title: 126 chars, one '&', leads with "Reindeer Ornament SVG Bundle". PASS.
- Tags: 13, unique, longest 18 chars. PASS.
- Description: says "about 6 in", names all 6 designs, sizing tip, licence, digital download, exact disclosure line last. PASS. Note: description says 04 "stands on its own snowy base" and the loop line says "hanging loop (or hanging hole)", so update it if 04 changes.
- Price $4.00, taxonomy 12394. PASS.
- No IP: no text, no named reindeer, no red nose, no sleigh. PASS.
- **Images (fail)**: image 1 (lead) has the three ornaments crammed into the top 55 percent of the frame, leaving the bottom half empty green before the title, and it shows 01 and 06, two of the weaker designs. Recompose so the ornaments fill the frame and lead with 02, 03 and 05. Images 2-4 should be regenerated after the redraws.

## Required fixes
1. Redraw 04 (head, neck, scarf, hang hole), or replace it with a round-frame deer.
2. Fix 06: no stubs outside the frame, thicker legs, rework the centre gap.
3. Fix 01: friendlier eyes, real holly sprig.
4. Recompose lead image 1 to fill the frame and feature the strongest designs; refresh images 2-4, ZIP and listing text to match.
5. Re-run `gen.py --check` and resubmit.

**Verdict: REJECTED**

# Round 2

## Summary
`python3 gen.py --check` prints ALL CHECKS PASS. QA viewed a 1080x720 contact sheet, a 20% thumbnail strip, 900 px dark-background crops of 01, 04 and 06, and all four listing images. The three redraws and the new lead image fix every Round 1 complaint. The set now reads as one family of six round hanging ornaments.

## Technical checks
| Check | Result |
|---|---|
| Parts / validity | PASS. All six: 1 part, valid |
| Smallest hole (limit 600 units2) | PASS. 01: 902, 02: 1078, 03: 1215, 04: 679, 05: 1248, 06: 1249 |
| DXF / PNG | PASS. 6-13 polylines, 5.98 in; PNG 1800x1800 |
| ZIP | PASS. 22 entries, every file byte-identical to bundle/ |
| Rebuild order | PASS. Cut files rebuilt 22:41:53-57; ZIP 22:41:57; all four listing images 22:42:00-02, after the last art change; LISTING.md and listing.json updated for round 2 |
| Cuttability | PASS. Antler tines and legs on 01, 04 and 06 are thin (about 0.08 in) but connected; 06 legs are visibly thicker than before and sit inside the frame. Stars hang from the ring and snowflakes are cut into the base, so nothing floats. Keep the 4 in / 4.5 in size advice |

## Design review
- **01 Stag head**: fixed. Round eyes and a muzzle line give a friendly face, and the holly now reads as two spiky leaves plus berries. Small nit: the muzzle outline looks a little like a bib at 100 percent, and the antler tips touch the ring. Neither blocks approval.
- **04 Reindeer with scarf**: fixed. Now a round-frame ornament with a hanging loop, a proper profile head, and a ribbed scarf with a fringed end that reads as a scarf at 20 percent. The hole no longer looks like a spot. Good.
- **06 Reindeer pair**: fixed. The deer sit fully inside the scalloped frame, legs are thicker, the pine fills the centre gap, and there are no stubs. Antler interiors are slightly fussy but fine.
- **02, 03, 05**: unchanged and still strong.
- **Set**: six round ornaments with loops, varied subjects. Would stop a scroller next to the top results.

## Listing review
- Lead image 1 now fills the frame with 02, 05 and 03 on a green background with hanging berries, "6 ornament designs" and format badges, and the title below. PASS.
- Images 2-4 show the redrawn 01, 04 and 06 and read well. PASS.
- LISTING.md describes the round-2 changes, and all designs now hang from a loop. Title, tags, price and no-IP checks from Round 1 still stand.

**Verdict: APPROVED**
