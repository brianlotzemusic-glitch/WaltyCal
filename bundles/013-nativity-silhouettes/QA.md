# QA: 013 Nativity Silhouettes (round 1 of 2)

## Verdict: SEND BACK

The files are technically clean. The bundle goes back for two design problems: the angel (06) has no readable head, and the magi panel (03) is half empty. There are also two copy/image errors. 01, 02, 04 and 05 are good.

## Technical checks (run by QA on the files unpacked from the ZIP)

| Check | Result |
|---|---|
| ZIP layout | PASS. SVG/ (6), PNG/ (6), DXF/ (6), README-LICENSE.txt |
| SVG: one `<path>`, one valid polygon, every hole inside the outer ring | PASS for all 6 |
| SVG size | PASS. 6.000 in on the longest side (03 is 6.000 x 3.681 in) |
| Smallest hole (normalised to 1000 units) | PASS. 1071 / 1330 / 2511 / 1401 / 2074 / 4963 u² (all at least 600) |
| Material width (opening at r=6, so 12 units) | PASS. No design splits. The largest piece lost is 0.3 u² (vertex noise) |
| Gap width (closing at r=2/4/6) | PASS. The largest single filled sliver is 2.2 u² (01, at r=6, corner rounding). There are no hairline slits |
| DXF | PASS. All 6 reopen in ezdxf, $INSUNITS=1, closed LWPOLYLINEs only, extents within 0.07 to 5.93 in |
| PNG | PASS. 1800 px on the longest side, RGBA, transparent corners, alpha 0 to 255 |
| Listing images | PASS on size. 4 images, each 3000x2250 |
| listing.json | PASS. taxonomy_id 12394, price 4.0, 133-char title, only one word with 2 capitals ("SVG"), one "&", 13 unique tags (longest is 19), no HTML entities (an improvement on 008/009), and the description ends with the exact disclosure line |

## Visual review

- **01 Holy Family**: the strongest design. Mary kneeling, Joseph with his staff and the manger all read at 90 px. It is reverent and balanced. It works well as the hero in the thumbnail.
- **02 Manger Under the Star**: reads as a manger with the child, a star and sheep. The rayed arc is a little busy, but it is acceptable.
- **03 Three Magi**: the riders, crowns and camels read at full size. The figures fill only the bottom ~50% of the frame, and the top half is an empty window with a small star hanging from the frame like a drip. At 90 px it is a thin strip of specks. The approved 008 light-box panel fills its frame with sky detail, and this one looks unfinished next to it. Each rider's robe also merges into the camel's body, with no saddle line, so each camel+rider reads as one lump with stilt legs.
- **04 Good Shepherd**: reads clearly. The crook and sheep are good.
- **05 Star of Bethlehem**: clean and clear.
- **06 Herald Angel**: **the Designer's flag is right, and it is worse than "blends into the sleeve".** At full size the head is only a small bump inside the halo, sitting on a solid block that runs straight into the wing and the raised trumpet arm. There is no neck, face, shoulder line or sleeve edge, so the angel reads as headless. The wing lobes are blunt and finger-like, so the wing reads more like a claw or hand than feathers. There is also a small ragged hook on the left of the robe hem. This is the second-largest figure on the thumbnail, so it pulls the whole listing down. I would not pay for this one as it is.
- **Fine detail and 8 in**: the geometry passes the 12-unit width and gap checks at the default 6 in, so the "8 in wide or larger" advice for 03 is conservative but honest. Both the description and the README state it, which is enough. Keep it.
- **Scroller test ("nativity svg")**: the thumbnail is attractive (navy with cream and gold, the stable as hero). Once 06 and 03 are fixed it would hold its own. With a headless angel in the top-right it does not yet.

## Fixes (numbered, required)

1. **06 Herald Angel, head and sleeve** (`gen.py`, angel function): give the head a clear round or profile silhouette with a **neck notch** under it. Turn the face toward the trumpet. Separate the head from the raised trumpet sleeve with a gap of **at least 13 units**, or a clear concave notch, so the head stands free inside the halo. Shape the raised arm as a draped sleeve hanging under the trumpet, so the arm and the body are two readable masses. Then check it at 90 px: you should see head, halo, trumpet and wing at a glance.
2. **06 wing**: replace the blunt rounded lobes with tapered, layered, pointed feathers (primary feathers longest at the tip). Keep every feather and every gap at least 13 units. Tidy the ragged hook on the left of the robe hem, so the hem is a clean curve or a flat base.
3. **03 Three Magi panel, composition**: fill the frame. Either cut the frame height so the riders take up about 70% of it, or add a sky: a larger Star of Bethlehem with a beam or rays, plus a few small cut-out stars (each hole at least 600 u², material at least 13 units). Attach the star so it does not look like a drip off the top bar. Scale the riders and camels up while you do this.
4. **03 camels**: add a saddle-cloth or blanket notch (gap at least 13 units) between each rider's robe and the camel's back, so the hump and the rider read separately. Shape the legs a little (knee, foot) so they do not look like stilts.
5. **`listing-images/3-formats.png`**: the text says "6 designs", but the icon row shows only 5. The magi panel is missing. Add it.
6. **`README-LICENSE.txt`**: "The scenes with a flat ground strip (01, 02, 04, 05, 06)" is wrong. 05 (star) ends in a point and has no ground strip, and 06 stands on a robe hem, not a strip. Change it to "01, 02 and 04 have a flat ground strip; 06 stands on its robe hem" (or whatever is true after fix 2).
7. **Rebuild** after fixes 1 to 6: the SVG/PNG/DXF for 03 and 06, `contact-sheet.png`, all 4 listing images (03 and 06 appear in each of them) and `nativity-silhouettes-svg.zip`. Then re-run `python3 build.py check`, plus an opening (r=6) and closing (r=2/4/6) test on 03 and 06.

## Optional (not blocking)

8. 02: the rayed arc over the manger reads a little like a sunrise or a cage. Consider fewer, longer rays, or a plain glow arc.

---

# QA round 2 (final)

## Verdict: APPROVED

I re-ran every check myself on the files unpacked from the rebuilt ZIP (all dated 19:37). I checked all 6 designs, not just 03 and 06.

- **Shapes**: each design is one `<path>` and one valid polygon with all holes inside it. The smallest holes are 1071 / 1330 / 645 / 1401 / 2074 / 1016 u², all at least 600. 03's new sky stars are the tightest at 645 (still within spec). The SVGs are 6.000 in (03 is now 6.000 x 3.422 in).
- **Width and gaps**: opening at r=6 never splits a design (the largest piece lost is 0.4 u²). Closing at r=2/4/6 fills no single sliver above 2.2 u². There are no slits or spurs, including at the new saddle cut-outs, the angel's neck notch and the arm slit.
- **DXF**: all 6 reopen in ezdxf, $INSUNITS=1, closed LWPOLYLINEs only. **PNG**: 1800 px on the longest side, RGBA, transparent. **ZIP**: SVG/, PNG/, DXF/ and README-LICENSE.txt. The new 03 and 06 files are in it.
- **listing.json**: unchanged and passing (12394, 4.0, 133-char title, 1 double-capital word, one "&", 13 unique tags of 19 chars or less, no entities, exact disclosure ending).
- **Fix 1 (angel head)**: done. There is now a round head inside the halo, a neck notch, and a raised forearm cut clear of the head and body. The angel reads as an angel blowing a trumpet, including at 90 px.
- **Fix 2 (wing and hem)**: done. Slotted, tapered feathers, and the hem is flat and clean. The lower feather lobes are still a little blunt, but that is acceptable.
- **Fixes 3 and 4 (magi)**: done. A starry sky band, a star in a moon disc, bigger riders that fill the frame, saddle cut-outs that separate rider and camel, and jointed legs. It now matches the approved 008 light-box for richness. The "8 in wide or larger" advice stays in the copy (honest and conservative).
- **Fix 5**: `3-formats.png` now shows all 6 designs. **Fix 6**: the README now says 01, 02 and 04 have a ground strip, 06 stands on its hem, and 05 is for hanging. This is accurate.
- **No regressions**: 01, 02, 04 and 05 are unchanged and identical in size to round 1. The contact sheet and all 4 listing images (3000x2250) are rebuilt and consistent. The thumbnail now has six clearly readable, reverent designs with good contrast on navy, and it would hold its own next to the top "nativity svg" results.

Cosmetic note (not blocking): 03's bottom frame corners have a tiny kink where the rounded corner meets the base (about 1 to 2 units). It has no effect on cutting.
