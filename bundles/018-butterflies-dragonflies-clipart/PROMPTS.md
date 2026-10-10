# Prompts — 018 Butterflies and Dragonflies Clipart

Recraft via `tools/imagegen.py`, cheap recipe only (FACTORY.md "Art quality", formats/clipart.md): one `gen --flash --n 4 --size 1024x1024` per design ($0.028), the best draft kept, then `removebg` ($0.01) and `upscale` ($0.004) on the kept draft. No standard re-rolls, no `--pro`, no `vectorize`. Everything after the AI calls is local and free.

**Spend (log/image-spend.csv, 10 Oct 2026):**
| Item | Calls | Cost |
|---|---|---|
| Flash drafts, 12 designs × 4 | 12 | $0.336 |
| Flash drafts for slot 05, second subject (see below) | 1 | $0.028 |
| `removebg` on the kept drafts | 12 | $0.120 |
| `upscale` on the kept drafts | 12 | $0.048 |
| Mockup photo: garden flat-lay, flash × 4 + `upscale` | 2 | $0.032 |
| **Total** | | **$0.564** (564 credits) |

That is **$0.044 per design** for the art (+ $0.003 each for the mockup photo), under the $0.05 target on average. **One slot went over on its own:** slot 05 cost $0.070 (two flash sets + removebg + upscale), see below. Recraft balance before: 3,296 credits; after: 2,732.

Drafts not used were left in the session scratchpad, not committed. Committed: the kept drafts (`art/raw/`), their removebg masks (`art/alpha/`, alpha channel only), the kept mockup draft (`mockup/blank-flatlay-raw.png`) and its upscale (`mockup/blank-flatlay.jpg`). The 4096 px art upscales (`art/up/`) are not committed; rebuilding from scratch costs 12 × $0.004.

## Base prompt (style bible clipart line, shop-profile/STYLE.md, year-round: "Christmas" dropped, "true-to-life insect colours" added)

> Garden clipart, flat vector illustration style with clean dark plum outlines and flat colours, true-to-life insect colours, limited palette: monarch orange, black, sky blue, teal, sunny yellow, scarlet red, leaf green, lavender purple, cream, soft gold, deep plum; crisp edges, one isolated subject centred on a plain pure white background, no text, no lettering, no frame, no ground shadow, no background scenery, cheerful and a little whimsical.

Each prompt = base + ` Subject: ` + the subject below. Original designs only: no brand, character or field-guide artwork, no text. "True-to-life insect colours" was added because QA 017 noted stylised colours on a species-named design (the robin's blue crown).

| Design | Subject | Draft kept |
|---|---|---|
| 01 Monarch butterfly | a monarch butterfly seen from directly above with wings fully open, bright orange wings with bold black veins, wide black wing borders dotted with small white spots, black body, two thin black antennae with clubbed tips, symmetrical | #3 of 4 (flash) |
| 02 Blue morpho butterfly | a blue morpho butterfly seen from directly above with wings fully open, vivid bright blue wings with wide black outer borders and a few small white spots in the borders, dark body, two thin black antennae, symmetrical | #1 of 4 (flash) |
| 03 Tiger swallowtail | an eastern tiger swallowtail butterfly seen from directly above with wings fully open, sunny yellow wings with bold black tiger stripes, black wing edges with a row of small yellow spots, long black tails on the hind wings with a few small blue and orange spots near the tails, two thin black antennae, symmetrical | #3 of 4 (flash) |
| 04 Red admiral butterfly | a red admiral butterfly seen from directly above with wings fully open, velvety black wings with a bright orange-red band across each forewing and along the hind wing edges, a few small white spots near the forewing tips, two thin black antennae, symmetrical | #2 of 4 (flash) |
| 05 Monarch caterpillar | a plump monarch caterpillar crawling along a broad green milkweed leaf, side view, its body banded with bold black, sunny yellow and cream stripes, a pair of thin black tentacles at the head and a shorter pair at the tail, little black legs | #3 of 4 (flash) |
| 06 Little blue butterfly | a small common blue butterfly seen from directly above with wings fully open, soft lilac blue wings with a thin dark grey border, small rounded wings, slim dark body, two thin black antennae, symmetrical | #2 of 4 (flash) |
| 07 Monarch on a coneflower | a monarch butterfly perched on top of a purple coneflower, side three-quarter view with wings half open, bright orange wings with black veins and black borders with small white spots, the flower with drooping lavender purple petals around a spiky orange-brown centre, a short green stem with one leaf | #4 of 4 (flash) |
| 08 Blue dragonfly | a blue dragonfly seen from directly above with all four wings spread flat, long slim sky blue body with thin black rings, large round teal eyes, four long narrow wings filled with a soft pale blue tint with fine dark plum veins and outlines, symmetrical | #1 of 4 (flash) |
| 09 Red dragonfly | a red darter dragonfly seen from directly above with all four wings spread flat, slim bright scarlet red body, large round red-brown eyes, four long narrow wings filled with a soft pale amber gold tint with fine dark plum veins and outlines, symmetrical | #1 of 4 (flash) |
| 10 Green darner dragonfly | a green darner dragonfly seen from directly above with all four wings spread flat, bright leaf green head and thorax, long slim sky blue abdomen with a thin dark stripe, large round green eyes, four long narrow wings filled with a soft pale golden tint with fine dark plum veins and outlines, symmetrical | #1 of 4 (flash) |
| 11 Damselfly on a reed | a slender electric blue damselfly with black bands on its long thin body, resting on a single upright green reed stem, side view, its four narrow wings folded together along its back, wings filled with a soft pale blue tint with dark plum outlines, large blue eyes | #1 of 4 (flash) |
| 12 Dragonfly on a water lily | a teal blue dragonfly with wings spread, resting on a pink water lily flower with pointed petals and a sunny yellow centre, the flower sitting on one round green lily pad, three-quarter view, wings filled with a soft pale blue tint with dark plum veins and outlines | #3 of 4 (flash) |

**Slot 05, first subject (dropped):** "a zebra longwing butterfly seen from directly above with wings fully open, long narrow black wings with bold sunny yellow stripes, two thin black antennae, symmetrical". All four drafts came out orange/plum tiger-striped or moth-like, none a zebra longwing, so the name would not have matched the art. Rather than ship a mismatched name or pay for a standard re-roll ($0.035), one more flash set ($0.028) was spent on a new subject (the monarch caterpillar) that also gives the set a life-cycle piece.

**Mockup photo** (`mockup/blank-flatlay.jpg`, draft #1 of 4, 1152x896, upscaled): 015's flat-lay has pine sprigs and red berries, wrong for a year-round garden set, so a new one was made:

> Realistic product photo, soft natural window light, shallow depth of field. Top-down flat lay on a light natural oak wooden table: a plain blank white crew-neck t-shirt laid flat in the centre with a large empty chest area, beside it a plain blank white square greeting card and a plain blank cream canvas tote bag laid flat, a few fresh spring garden flowers, lavender sprigs and green leaves at the edges, everything blank and unprinted, no print, no pattern, no text, no logos, no people, no insects

## Designer's notes for QA (not an approval)
Every draft was looked at on a low-res contact sheet before picking; every finished PNG on dark green and checkerboard in `contact-sheet.png`, plus crops of the areas below on dark. No text, letters or signatures seen; every insect has one head, two antennae, four wings (or folded wings on the damselfly) and no extra legs that I could see.

Draft choices and names (QA 017 asked that names match contents):
- 01 #3 over #1 (#1 had plum, not black, wing borders and a pale blue spot). A few small blue-grey touches near the body remain from the draft.
- 06 is named **"Little blue butterfly"** (the subject was a common blue; the draft is lilac-blue with a grey border, close to a male common blue's upperside, without the white fringe), so the name doesn't claim more than it shows.
- 11 #1 over #4: #4's reed ran off the bottom edge (cropped).
- 12 makes no species claim: a teal dragonfly with lilac and orange eyes (stylised) on a pink water lily. Its eyes are the one deliberately whimsical colour left in the set.

**Colour corrections in code** (`RECOLOR`, `TINT`, `PAINT` in `process.py`; hue shifts only, linework and shading kept) so colours are true to the names:
- **05 Monarch caterpillar:** the draft drew the milkweed leaf sky blue and teal, with a lilac stalk, a maroon three-lobed leaflet under the caterpillar and a yellow oval on the leaf. All are shifted to leaf greens (the oval stays as a pale green spot). The caterpillar's bands are the draft's own (black, golden yellow, cream). Please judge whether the leaf now reads naturally.
- **04 Red admiral:** the draft's lilac and sage striped body is darkened to near-black, like the real butterfly.
- **11 Damselfly:** orange legs and an orange thorax patch darkened (real blue damselflies have dark legs); the yellow curl at the reed's foot made reed green.
- **08, 10, 11, 12 dragonfly wings:** they came out near-white, which would vanish on white blanks and failed the halo test as if they were paper. Every light neutral wing area is multiplied by the pale tint the prompt asked for (blue for 08, 11, 12; gold for 10). Small eye glints on those designs turn pale blue too.
- **02 Blue morpho:** the draft drew white seams along the body and between its segments; removebg took them as background (slits). `PAINT` fills them with the body plum.

Clean-up (no edge snapping, per QA 017):
- `EDGE_SNAP` is empty. The anti-aliased outer edge keeps its soft alpha.
- New `interior_opaque`: the quantizer had merged thin interior plum veins with edge colours into palette entries at alpha ~244 (11 was at 97.7% opacity). Interior pixels (more than 3 px inside the art) on such entries are moved to the nearest fully opaque palette colour; the palette and the outer edge are unchanged. 11 is now 98.10% overall, 100% interior: the lowest in the set, from its thin legs, antennae and reed edge. Please look at 11's legs at 100% on dark.
- New `solidify`: part-transparent removebg pixels deep inside the art take the draft's colour at alpha 255.
- `CLEAR_BOX` (small, local): 02 (1 px paper rims on the cream wing bases), 04 (a paper sliver between antenna and head), 06 (pale rims in the gaps beside the body), 09 (1 px paper lines along the thorax), 12 (pale ragged rims where wings overlap).
- `HALO_OK` (real light art, all plum-outlined): 01 a white spot on the head; 07 the eye highlight and one white border spot; 09 the pale amber base of the right forewing; 12 a pale glint where two wings cross. 12 also keeps a few small ragged background slits where its wings overlap (as drawn: the paper between the wings).
- 04 SVG: the wings are flat near-black, so `LINE_MIN_BY_SLUG` leaves them out of the ink (otherwise 51% ink, over the 45% check); its SVG is the outlines and veins.

`python3 gen.py --check`: ALL CHECKS PASS (ZIP 7.1 MB; closest design pair 08/09 at 89 bits, the two top-view dragonflies, which differ by colour and wing shape).

## QA round 1 fixes (Designer, round 2; $0, no new AI calls)
- **03 Tiger swallowtail:** new `BODY_GAP` in `process.py`: inside a box round the body (final PNG coordinates), each row's transparent gap between the two dark hindwing-margin strips is filled with the strips' body colour (45, 31, 38) at alpha 255, from below the thorax down to the hindwing notch (the narrowest row, 33 px). The body is now one closed dark shape with the abdomen drawn inside it; the natural V between the tails below the notch stays transparent.
- **06 Little blue butterfly:** new `NEUTRAL_PAINT`: the wobbly mid-grey border band, the darker grey line inside it and their grey-lilac mixes (every non-plum pixel darker than the wing, outside the body and antennae boxes) take the wing colour, so each wing runs cleanly to its thin plum outline; one stray plum dash inside the left hind wing is wiped. A `RECOLOR` rule then turns the grey-lilac into a clear sky blue (hue 212, saturation x2). Name kept: it now matches. A faint lighter hairline remains where the grey band used to meet the wing; please judge at 100% on dark.
- Rebuilt PNG/SVG for 03 and 06, the ZIP, contact sheet and listing images 2-4. `gen.py --check`: ALL CHECKS PASS.
