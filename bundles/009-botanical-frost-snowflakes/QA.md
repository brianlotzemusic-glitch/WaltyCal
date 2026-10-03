# QA: 009 Botanical Frost Snowflakes (round 1 of 2)

## Verdict: SEND BACK

There is one real cut defect. Everything else passes, and the bundle is close to approval.

## Technical checks (run by QA on the files inside the ZIP)

| Check | Result |
|---|---|
| ZIP layout | PASS. SVG/ (6), PNG/ (6), DXF/ (6), README-LICENSE.txt |
| SVG: one `<path>`, one outer ring, every hole inside it, valid | PASS for all 6 (1 polygon each) |
| SVG size | PASS. 6.000 in x 6.000 in |
| Smallest hole (normalised to 1000 units) | PASS. 01: 1665, 02: 3833, 03: 831, 04: 756, 05: 1023, 06: 5386 (all at least 600) |
| Material width (morphological opening at r=6, so 12 units) | PASS. Only vertex noise is lost (under 0.4 u²). The shape never splits |
| Gap width (closing at r=1 to 6) | **FAIL on 02 Fern Frond** (see fix 1). The other 5 pass |
| DXF reopens in ezdxf | PASS. $INSUNITS=1 (inches), closed LWPOLYLINEs only, extents about 0.45–5.55 x 0.07–5.93 in |
| PNG | PASS. 1800x1800 RGBA, transparent corners, alpha 0–255 |
| Listing images | PASS. 4 images, each 3000x2250 |
| listing.json | PASS. taxonomy_id 12394, price 4.0, title 133 chars, 13 unique tags (longest 19 chars), description ends with the exact disclosure line |
| Trademarks | PASS. Cricut and Silhouette are named only as compatibility. No other brands |
| Copy matches the ZIP | PASS. 6 named designs, SVG/DXF/PNG, 1800 px, inches, single path and nothing loose all match the files. **Except** that the "narrowest ... 0.08 in" claim in README is false for 02 until fix 1 is done |

## Visual review

- All 6 read clearly as six-fold snowflakes at 120 px, and all are symmetric and balanced. The botanical theme reads on 03 Berry, 04 Holly, 05 Acorn & Oak and 06 Twig. 01 Pine and 02 Fern read as pine and fern at listing size. The set is cohesive and distinct from the generic geometric flakes in the top results, so it would stand up on the "snowflake svg" page.
- Joints: stems are about 18–30 units and needles/leaves are at least 13 units. No fragile spurs except the one below.

## Fixes (numbered, required)

1. **`gen.py` → `d2_fern_frond()`, fiddlehead curl (`spiral(P(132, 0), 30, 12, 0.85, 90, 16, cw=-1)`)**: the end knob of the curl almost touches the curl's own stem. This leaves a hairline slit of about **1–2 units** (under 0.012 in at 6 in) at all 6 fiddleheads. They sit at about r=114 from the centre, e.g. near (439, 403) and (561, 597) in SVG units. A cutter will either fuse the two cut lines or tear the knob off, and in vinyl the slit cannot be weeded. Either open the gap to **at least 13 units** (for example fewer turns, ~0.7, or start the curl further from the stem) or merge the knob solidly into the stem, so it does not just almost touch. Check it again with a closing test (buffer +r/−r with r=6.5 must add no area at the curl). Note: `finish()` did not catch this, so the close/open pass is not enough on its own.
2. **Rebuild outputs after fix 1**: regenerate SVG/DXF/PNG for 02, then `contact-sheet.png`, all 4 `listing-images/*.png` (02 appears in each of them) and `botanical-frost-snowflakes-svg.zip`.

## Optional (not blocking)

3. `listing-images/1-thumbnail.png`: the sage-coloured flakes (02, 04, 06) are noticeably lower in contrast on the dark green than the white ones. At search-grid size they look faint. Consider making all 6 near-white, or lightening the sage.
4. `listing.json` / `LISTING.md`: `&#39;` entities appear in "WHAT'S INCLUDED" and "don't". The approved bundles 005 and 008 have the same thing, so this is not a blocker. Confirm that Etsy shows a plain apostrophe after publishing.

---

# QA round 2 (final)

## Verdict: APPROVED

I re-ran every check myself on the files unpacked from the rebuilt ZIP (all files dated 16:27). I checked all 6 designs, not just 02.

- **Fix 1 (02 Fern Frond curl)**: done. The closing test at r=2/4/6 now adds at most 0.3 u² (vertex noise) on 02, where round 1 found 6 slits of about 15–20 u². A zoomed render shows a clearly open curl with the knob well clear of the stem.
- **Gap and width across all 6**: closing at r=2/4/6 adds at most 1.7 u² (01, vertex noise) and 0.4 u² or less on the rest. Opening at r=6 (12 units) never splits a design, and the largest piece it removes is 0.4 u². So no gap or material is under ~12 units.
- **Shapes**: each design is a single `<path>` and one valid polygon with all holes inside it. Smallest holes are 1665 / 3833 / 831 / 756 / 1023 / 5386 u², all at least 600. SVGs are 6.000 in.
- **DXF**: all 6 reopen in ezdxf, $INSUNITS=1, closed LWPOLYLINEs only, about 6 in tall.
- **PNG**: 1800x1800 RGBA, transparent.
- **ZIP**: holds SVG/, PNG/, DXF/ and README-LICENSE.txt. The new 02 files are in it (SVG 41114 B, PNG 113246 B, DXF 157088 B, all different from round 1). The README now says the narrowest material and gap are about 0.08 in at 6 in, which is consistent with the ~13-unit minimum.
- **listing.json**: unchanged and still passing (taxonomy 12394, price 4.0, 133-char title, 13 unique tags of 19 chars or less, exact disclosure ending, Cricut/Silhouette named only as compatibility).
- **Images**: the contact sheet and all 4 listing images (3000x2250) are rebuilt and show the new 02. The thumbnail's sage flakes are now near-white, and all 6 have good contrast. The set reads as botanical snowflakes at thumbnail size, is balanced, and would hold its own next to the top "snowflake svg" results.

Carried-over note (not blocking): `&#39;` in the description, the same as approved bundles 005 and 008. The Lister should check the apostrophes on the live listing.
