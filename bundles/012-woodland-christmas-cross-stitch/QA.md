# QA — 012 Woodland Christmas cross-stitch (format pilot), round 1 of 2

**Verdict: SEND BACK**

The technical side is solid. Two one-colour charts would not sell, though, and there are several copy errors and two gaps in the spec. All fixes are small. The colour set already passes the "stop a scroller" bar.

## What I checked (and passed)
- `python3 gen.py --check`: ALL CHECKS PASS, and the working tree is unchanged afterwards.
- PDFs (from the ZIP): 28 pages each. Letter is 612×792 on every page and A4 is 595×842 (594.96×841.92) on every page. All 11 font objects are embedded and subset (Fraunces, Nunito). Sizes are 1.1 MB and 1.2 MB.
- My own pass over `motifs.json` (not using gen.py):
  - All 12 grids match W×H, crop tight to the motif and have counts that match the keys.
  - 3–6 colours per motif.
  - No 8-neighbour stray stitches in either version.
  - No one-colour stitch falls outside the colour shape.
  - The finished sizes on the chart pages and in the README equal W/14 and W/18 (e.g. fox 1.79×2.43 in → 1.8×2.4; 18-count range 1.39–1.89 → "1.4 to 1.9").
- DMC numbers and names: all 10 are real and correctly paired (3371 Black Brown, 550 Violet Very Dark, 500 Blue Green Very Dark, 3363 Pine Green Medium, 815 Garnet Medium, 920 Copper Medium, 729 Old Gold Medium, 712 Cream, 433 Brown Medium, 436 Tan).
- Symbols: the 10 palette symbols are unique, and the one-colour key's × is only ever used alone.
- Skeins: 1 skein ≈ 1,600 crosses is plausible and slightly conservative. An 8 m skein makes 3 lengths of 2 strands (≈24 m), at ≈1.3–1.5 cm per cross with waste.
  - The shopping-list totals match my sums: 3371 = 1397 → 1 skein; one-colour total 4883 → 4.
- ZIP: exactly both PDFs plus README-LICENSE.txt.
- listing.json:
  - price 3.5, taxonomy 6343, digital_file correct.
  - Title is 119 characters, with 0 words starting with two capitals and no "&".
  - 13 unique tags, each ≤20 characters.
  - No HTML entities, and the disclosure line is exact.
- Charts rendered at 110 dpi (robin colour on Letter + A4, acorn one-colour on A4, robin one-colour on Letter):
  - Squares are about 5.4 mm, and the symbols are legible on both fills.
  - Bold lines fall at 10/20/30, and the numbers line up.
  - Centre arrows are at the true centre (e.g. 30 wide → between columns 15 and 16; 29 high → middle of row 15).
  - The key matches the chart, and nothing is clipped.
- Cover, contents, how-to and shopping-list pages are clean and accurate apart from the points below.
- Licence (personal use, up to 50 hand-stitched finished pieces, no sharing, kits or conversion) is standard for this market.

## Fixes (numbered, all required unless marked optional)

1. **Robin one-colour does not read.** Its light set is `"C"` (`motifs.py` around line 212), so the whole copper breast and face become empty space. What is left is a thin outline with a dark wing and tail, a broken beak, a dotted belly line (row 21) and a branch broken in the middle (row 22). At contact-sheet size it reads as an empty blob.
   - Use `"W"` as the light set (cream belly as the gap), and keep the copper breast stitched.
   - Leave the eye as a 1-stitch gap.
   - Make sure the branch line (row 22) stays continuous.

2. **Acorn one-colour does not read.** Its light set is `"TG"`, so both oak leaves turn into hollow outlines, mostly diagonal-only stitch chains. It looks like a beetle with wings (see `listing-images/4-colour-vs-one-colour.png`, bottom right).
   - Drop `G` from the light set so the leaves are solid, with the `L` veins as gaps (like the holly one-colour, which reads).
   - This image is a sales image, so it must be fixed or the motif swapped out of image 4.

3. **Owl is called "Snowy Owl", but it is brown** (433/436 body). A snowy owl is white, and buyers will notice.
   - Rename it everywhere, e.g. "Little Owl" or "Woodland Owl": chart page titles (pp 6 and 18), contents, README table, the description ("a snowy owl") and contact-sheet labels.
   - The page 3 tip mentions "the owl's face"; that is fine once the owl is renamed.

4. **Fat-quarter claim is wrong** (shopping list, page 4: "a 6 × 6 in piece per ornament, or a fat quarter for all 12"). A fat quarter (about 18×21 in) gives only nine 6×6 in pieces.
   - Say "a fat quarter makes 9; get a half yard for all 12", or use smaller pieces. 5×5 in works for a 2.4 in design in a 4 in hoop.

5. **Size copy does not match the charts.** The real range is 1.8–2.4 in on 14-count, but the copy says "about 2 to 2.5 in":
   - description paragraph 1
   - page 3 "Sizes"
   - the image 2 tile "Mini ornaments"

   Change these to "about 1.8 to 2.4 in". Page 3 also says "1.5 to 2 in on 18-count"; change it to "1.4 to 1.9 in", which matches the description and README.

6. **"Stitch counts from 25 × 25 to 32 × 34" is inaccurate** (description, STITCHING). No chart is 25×25 or 32×34. Write "25 to 32 stitches wide and 25 to 34 high".

7. **Listing photo 1 breaks FACTORY.md "Art quality".** The rule says the first photo must be an AI lifestyle mockup when an image key is set. A key is set, and October runs on prepaid credits.
   - The code-drawn hoop scene is good, but next to the top results for "christmas ornament cross stitch" (photos of real stitched ornaments on trees) it looks flat.
   - Do not let AI invent the stitching: it will not match the chart.
   - Instead, make one flash `gen` of an empty scene (tree branch, lights, wood or knit backdrop, room for hoops). That costs about $0.03.
   - Composite the existing `stitch.py` hoop renders onto it, and keep the title band.
   - Record the prompt in `PROMPTS.md`, and update the disclosure note in LISTING.md ("No AI images used").

8. **Spec fixes (`formats/cross-stitch.md`):**
   - a) Size rule: "25–35 stitches wide (2–2.5 in on 14-count)" is wrong. 25/14 is 1.8 in, so write "about 1.8–2.5 in".
   - b) One-colour rule: say the light set may contain only light colours (712 Cream, 729 Old Gold, 436 Tan highlights, 815 spots). Never a mid or dark fill (920, 500, 433) that makes up most of the motif.
   - c) Add a check that fails when the one-colour version keeps less than about 70% of the colour stitches, or when the one-colour version has gained new 8-connected parts. This would have flagged robin (75%, but hollow), acorn (68%) and owl (3 parts); review whatever it flags by eye.
   - d) Listing image 1: replace "code-drawn hoops on dark wood" with the composite approach from fix 7, so the spec agrees with FACTORY.md.
   - e) Fabric line: drop the fat-quarter claim, or state the correct number of pieces.

9. *(Optional)* × (815) and + (433) appear on the same chart (robin, pine). They are legible at 5.4 mm, but one is just the other rotated. Consider a vertical bar or a half-filled square for 433 to make black-and-white prints safer.

10. *(Optional)* The title leads with "Christmas Cross Stitch Pattern", but the target search phrase is "christmas ornament cross stitch". Consider leading with "Christmas Ornament Cross Stitch Pattern, 12 Woodland Minis, …" (still ≤140 characters). You could also swap the generic tag "christmas pattern" for "ornament pattern" or "woodland cross stitch".

## Notes (no action)
- Fox one-colour is close to reading as a cat or husky, but the tail carries it.
- Holly one-colour berries are a bit fragmented but read.
- Moon: the star touches the moon's tip and the sleepy face is faint, which is acceptable.
- Snowflake has 8 arms in violet and gold, which is a common stylised look.
- After the fixes, re-run `gen.py`. Then re-check the contact sheet, image 4, pages 6/8/16/18/20/28 and the page 3 and page 4 text.
