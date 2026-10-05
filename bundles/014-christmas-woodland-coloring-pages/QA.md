# QA: 014 Christmas Woodland Coloring Pages (round 1 of 2, format pilot)

## Summary

The files, listing and listing images are clean, and 16 of the 20 pages are good bold & easy pages. The bundle goes back for one real defect and three smaller ones, all of them local clean-up in `process.py` with no new AI spend needed:
- **19**: the grass tufts look like ink splats.
- **4**: three of the five code-drawn snowflakes have filled in solid.
- **15**: the branch needles are too fine to colour, and the right-hand bird is odd.
- **18**: there are stray marks in the antlers.

## Technical checks (QA ran these on the files unpacked from the ZIP into a scratch dir)

| Check | Result |
|---|---|
| ZIP | PASS. It holds exactly the Letter PDF, the A4 PDF and README-LICENSE.txt. The README inside the ZIP is the same as the bundle copy |
| PDFs | PASS. Each has 20 pages. Letter is 612×792 pt and A4 is 594.96×841.92 pt. Each is 0.8 MB. `pdffonts` lists no fonts and `pdftotext` returns nothing |
| Same art on both papers | PASS. The art box is 182.0 × 234 mm on both. Margins are 16.9 mm (Letter) and 14.1 mm (A4) at the sides. The 20 A4 pages match the Letter pages in the same order |
| `gen.py --check` (run for reference only) | ALL CHECKS PASS. The worst page has 12 nooks (0.14%), the smallest space is 11 mm², and the closest pair of pages differs by 134 bits |
| listing.json | PASS on everything below |
| ↳ title | 124 chars, leads with "Christmas Coloring Pages". No words start with 2 capitals ("pdf" is lowercase). One "&". No entities |
| ↳ tags | 13 unique, the longest is 19 chars |
| ↳ price and category | 3.99, taxonomy 339, digital_file is the ZIP |
| ↳ disclosure | The last line is exactly the non-cut-file disclosure line |
| ↳ LISTING.md | Matches listing.json |
| Spend | PASS. log/image-spend.csv has 21 calls on 5 Oct totalling $0.595, which matches PROMPTS.md (20 flash + 1 standard re-roll for 12) |
| Listing images | PASS. 4 images, each 3000×2250 |

## Page review (QA looked at every page of both PDFs at 60–100 dpi, and at the problem areas at 200 dpi)

Overall: the outlines are thick and even, the frame closes the background, and there is no text, no signature and no grey. Every subject is cute and safe for kids. Nothing resembles a known character: the snowman has no top hat or pipe, and the reindeer's round nose is generic and uncoloured, with no name in the copy.

- **01 Fox, 02 Owl, 05 Cabin, 07 Robin, 09 Bear, 10 Squirrel, 13 Snowman, 14 Mouse, 16 Tree, 17 Fireplace**: good. Each reads at a glance. The pinecones on 02 and 10 are the busiest parts of the set, but they are acceptable.
- **03 Moonlit deer**: good. There are tiny black wedges where the star meets the moon, at the left tree edge and on the right star. These are cosmetic (optional fix 6). The stars lying on the snow are whimsical, and I accept them.
- **04 Mushrooms**: the mushrooms and ferns are good. **Three of the five code-drawn `FLAKES` (top centre, mid-left, mid-right) came out almost solid black.** The gaps between the arms fell under 12 mm² and were filled, so they read as dark ink rosettes next to the two open flakes. This is the ink-stain look that the swap was meant to remove.
- **06 Hedgehog, 08 Bunny**: good. The poses are slightly odd (the blanket and the backward-reaching arm), but nothing is wrong or creepy.
- **11 "Walking home with a tree"**: **the rename is right.** The animal is a generic, round-snouted critter in a bobble hat, not a badger. It is charming and reads clearly. The black rectangle is the tree's trunk, not an artefact. Accept.
- **12 Wreath**: it reads as a wreath with pinecones, berries and a bow. It touches the frame on three sides, but the frame closes those shapes. Accept.
- **15 Birdhouse**: the weakest page. The berries are open circles, so the "solid berries" flag is really about the **merged black wedges in the middle of the berry cluster and at the needle tips**. Those alone are acceptable. The real problems are:
  - The branch needles are white slivers about 1 mm wide, so they need a fine-tip pen. The spec says to swap such a draft.
  - The right-hand chickadee has a sideways, mask-like eye with no clear head, which looks a little off.
  - The post, with its round-footed base, reads as a lamppost.
- **18 Reindeer**: it reads well. Stray antler fragments overlap the left tree and look broken: a black wedge at about (255, 400) and a loose antler stub crossing the tree outline. There is also a lone ink tick at about (282, 528) in 100 dpi page coordinates.
- **19 Hare**: the hare, moon and tree are lovely. **The four grass tufts are a real defect.** Each is a solid black splat with melted, broken white ruffles inside. At print size they look like ink blots or dirt, not grass, and the page's own blob rule should have caught them.
- **20 Gnome**: good. The faint "face" on the left mushroom (two dot spots and a curve) is cute and harmless. The wavy strands hanging off the lantern are a little odd (optional fix 7).
- **Nooks (≤16 a page)**: I accept the bound. The worst page has 12, at 0.14% of the area. At 200 dpi they appear only as tiny black pinches where two lines meet, and nobody colours there.

## Listing images

- **1 Thumbnail**: strong. At 300 px wide the plum band, "Christmas Coloring Pages", the "20 pages" badge and the coloured fox and owl all read clearly. It would stand out among the white coloring-page results. It is honest: the pages shown are real pages 01, 02 and 18, coloured using their own regions.
- **2 Page grid**: shows all 20 real pages, numbered and named to match the PDFs. Honest. Pages 4, 15, 18 and 19 must be re-rendered after the fixes.
- **3 Coloured mockup**: the owl and fox are filled using their real regions, and the close-up is the real page 6 at its real line weight. Honest. The copy says the files are black and white.
- **4 Formats**: correctly labels US Letter and A4, the 2 PDFs and that it is a digital download. Honest.

## Copy and README

The description is accurate:
- 20 pages and 2 PDFs (Letter 8.5×11 in and A4)
- the page list matches the PDFs
- outlines of about 2 mm, which matches stroke_after of 1.63–2.18 mm
- the colour examples are labelled as ideas only
- the personal-use licence (home, family and classroom; no sharing or resale) matches the README

The README is complete and correct: the files, the page list, the "at least 14 mm" margin (measured at 14.1 mm on A4), printing tips, and a licence covering no POD and no AI training. The shop name is correct.

## formats/coloring.md: a sound spec, with three amendments

The pipeline, page sizes, no-text proof, the pinch-point bound, the hash check, the cost recipe, the Etsy category and honest colour examples are all sound. The spec needs these changes:
- **S1.** Step 5 (fill every space under 12 mm²) can turn a fine motif into a solid clump, as on 04, 15 and 19. Add a check: after the fill, flag any connected patch of newly filled ink over about 25 mm² that is not an eye or nose, and require an `ERASE` or replacement. Also add "dark clumps or splats made by filling" to the "Then look" list.
- **S2.** `FLAKES` must be drawn with arm gaps of at least 12 mm² at the size used, or the fill blacks them out (page 04).
- **S3.** FACTORY.md "Turnaround week" still says Recraft is used up and to "draw in code until 1 Nov". The newer "October 2026 one-time top-up" rule (commit 3550011, written after it) allows spending until the balance runs out, so this bundle's $0.60 was within the rules. The Manager should delete the stale turnaround line so later briefs don't conflict.

## Fixes (required)

1. **19 Hare, grass tufts**: erase all four tufts (ERASE boxes). Replace them with outlined grass tufts or plain snow mounds with open interiors of at least 12 mm² each, drawn in code like `FLAKES`, or leave the snowy meadow bare.
2. **04 Mushrooms, snowflakes**: redraw the three solid flakes (top centre, mid-left, mid-right) so they match the two open ones: larger, with arm gaps that survive the 12 mm² fill.
3. **15 Birdhouse**:
   - Erase the pine-branch needles and redraw the sprig as a simple stem with a few broad leaves or needle clusters (each white space at least 12 mm²), keeping the outlined berries.
   - Erase the right-hand chickadee and replace it with a second simple round bird like the left one (a code-drawn copy or mirror is fine).
   - Alternatively, use page 15's one allowed standard re-roll ($0.035) with a simpler prompt.
   - Optionally make the post base square so it reads less like a lamppost.
4. **18 Reindeer**: erase the stray black wedge and the loose antler stub where the left antler crosses the tree, and the lone tick mark in the tree at about 70 × 132 mm from the top-left of the art box.
5. **Rebuild** these, then re-run `gen.py --check` and look at the four pages at full size:
   - `process.py` for 04, 15, 18 and 19
   - both PDFs, the ZIP and `contact-sheet.png`
   - listing images 1 (it shows page 18 behind the fox) and 2. Image 4 shows only pages 06 and 13, so it does not change.

## Optional (not blocking)

6. 03: clear the small black wedges at the star/moon join and the left tree edge.
7. 20: trim the wavy strands hanging off the lantern.

## Would I pay $3.99?

After fixes 1–4, yes. The fox, owl, hedgehog, bear, mouse and gnome pages are better than most "bold and easy christmas coloring" results, and the thumbnail would stop a scroller. As shipped, page 19's ink splats would look like a printing fault to a parent.

**Verdict: REJECTED**
