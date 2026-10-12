# QA: 022 Winter Mushroom & Toadstool Ornaments (round 1)

## Summary
`python3 gen.py --check` prints ALL CHECKS PASS. QA viewed a 360 px-cell contact sheet, a 120 px (about 20%) thumbnail strip, 600 px crops of 04, 05 and 06, and listing image 1. Five of six are good and the set reads as one family of round ornaments. 04 (gnome) does not read well enough to sell.

## Technical checks
| Check | Result |
|---|---|
| Parts / validity | PASS. All six: 1 part, valid |
| Smallest hole (limit 600 units2) | PASS. 01: 880, 02: 873, 03: 1248, 04: 925, 05: 764, 06: 784 |
| DXF / PNG | PASS. 10-24 polylines, 5.97-5.98 in; PNG 1800x1800 |
| ZIP | PASS. 22 entries |
| Thin parts | Star threads and the gnome/cottage-door lines are about 0.08 in at 6 in. Connected, cuttable with the 4 in / 4.5 in advice. 05's upper horn tip tapers thin but is attached and acceptable |

## Design review
- **01 Toadstool trio**: good. Three clear spotted caps, hanging stars, snowy ground. No issues.
- **02 Toadstool cottage**: good, the strongest lead. Round windows, arched door, lantern all read at 20%. The door is a thin outline but reads as a door and is connected. Minor.
- **03 Mushroom bauble**: good. Cut-out mushrooms and snowflakes read instantly.
- **04 Gnome and toadstool (FAIL)**: the hat and toadstool read, but the face does not. The nose is a ring/horseshoe cut-out and the beard is a U-outline with three squiggles, so at 20% and 100% the gnome looks like a beetle or a bull-nosed mask, not a bearded gnome. The face and beard rely only on thin cut lines (about 15 units) with no solid shape to carry them. Bottom-right of the ring also has small jagged nubs where the pine and ground meet the frame.
- **05 Crescent moon with mushrooms**: good. Bold moon, two clear toadstools. The thin horn tip and short star threads are fine at the advised size. No block.
- **06 Snow globe**: good. Globe, base with snowflakes, pine and toadstools read well. The faint shine line is a small stroke at upper right; it is visible at 100% and harmless when lost at thumbnail. No block.

## Listing review
- Title: 130 chars, one '&', leads with "Mushroom Ornament SVG Bundle". PASS.
- Tags: 13, unique, each 20 chars or fewer. PASS.
- Description: says "about 6 in", names all 6, sizing tip, licence, digital download, exact disclosure line last. PASS. If 04 is redrawn, update the sizing-tip mention of "fine cut lines on the gnome".
- Price $4.00, taxonomy 12394. PASS.
- No IP: no text, a generic gnome, no brands. PASS.
- Images: lead (01, 02, 06) is well composed, fills the frame, legible. Code-drawn, not a lifestyle photo (known gap, same as 008/020/021). Images 2-4 need refreshing if 04 changes.

## Required fixes
1. Redraw 04's gnome face: make the nose a solid shape (a rounded nose standing out below the hat brim) and the beard a solid bold shape with at most a couple of thick, wide cut lines (at least 0.12 in at 6 in), so it reads as a gnome at 20%. Clean up the small nubs at lower right of the ring.
2. Rebuild 04's PNG/DXF, ZIP, listing images 2-4 (and 1 if it shows 04), update LISTING.md/listing.json text, re-run `gen.py --check`, resubmit.

Everything else can stay as is.

**Verdict: REJECTED**
