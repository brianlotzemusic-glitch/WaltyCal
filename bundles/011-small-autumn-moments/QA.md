# QA: 011 Small Autumn Moments (round 1 of 2)

**Verdict: SEND BACK.** This is a good bundle and close to shippable. The checklist page is attractive, the 30 moments are original, specific and relatable, the 20 stickers are clean and consistent, and the thumbnail passes the scroller bar. Image 3 misrepresents the main Print Then Cut claim, though, and the Cricut sizing step and the "what you need" wording should be made safer before a buyer relies on them. All of the fixes below are small.

## What I checked myself (all OK)
- **`gen.py --check`** prints ALL CHECKS PASS. I re-checked the main points independently below.
- **PDFs** (unzipped from the buyer ZIP; pdfinfo, pdffonts):
  - The checklist PDFs have 4 pages each. Letter is 612×792 and A4 is 594.96×841.92.
  - The sticker PDFs have 1 page each, in the same two sizes.
  - All fonts are embedded and subset (Fraunces 700/900, Nunito 400/700/800), with no fallback fonts. The files are 0.2–0.6 MB.
- **PNG**: 2025×2775 px, 300 DPI tag, RGBA. Composited on dark plum, every sticker has an even white border and nothing touches. The opaque content bbox is (69,77)–(1968,2698). From `stickers.json`, the minimum gap between stickers is 67.7 px (0.23 in) and the minimum edge distance is 56.9 px.
- **Cut paths**: each outline is one piece. The 30 px closing gives smooth notches at the joins between the pill and the disc. I found no thin hairline in any cut outline. The thin elements (rain dashes, dotted inner ring, geese) are only printed, not cut, so the offset does not affect them.
- **ZIP**: holds exactly the 4 PDFs, the PNG and README-LICENSE.txt. The README's file list, page map and sticker list match the files.
- **listing.json**:
  - The title is 126 characters, leads with "Fall Bucket List Printable", has 0 words starting with 2 capitals, and has one "&".
  - There are 13 unique tags, the longest 18 characters.
  - There are no HTML entities, and the description ends with the exact disclosure line.
  - Price is 3.5, `taxonomy_id` is 354, and `digital_file` is the ZIP. LISTING.md matches.
- **Counts**: 8 + 7 + 8 + 7 = 30 moments, 15 write-in lines, 20 stickers at 1.34–1.5 × 1.46 in.
- **Rendered pages** (all 4 pages of Letter and A4, at 80 and 200 dpi):
  - The title is on one line, the columns are balanced and nothing overlaps or clips.
  - The footer art sits inside the frame, and the text is about 19 mm from the edge.
  - The ink-saver pages are truly white.
- **Originality**: the moments and sticker phrases are plain, original everyday phrasing, with no lyrics, quotes, brands or trademarked phrases. The icons are all distinct, and each reads at decoration size on the contact sheet.
- **Images**: all 4 are 3000×2250.
  - **Image 1**: the dark band and big "Fall Bucket List" stand out against the usual orange-on-white results. The stickers shown peeled (soup, candle, frost) are correctly removed from the sheet.
  - **Image 2**: it matches the files ("4 pdf files + 1 PNG").

## Fixes (numbered; 1–4 required, 5–7 quick polish)
1. **Image 3: the dashed "6.75 × 9.25 in" box is the wrong shape, and the stickers spill out of it.** In `thumbs.js` line 111 the box is 285×368, a ratio of 1.29, but the sheet's ratio is 1.37. The PNG at 285 px wide is about 390 px tall, so the bottom row of stickers crosses the dashed line. It looks as though the stickers don't fit the Cricut area, which is the opposite of the claim. Set the box to the PNG's real aspect (285 × 390, plus the border with `box-sizing`) and re-render image 3.
2. **Make the Design Space sizing step foolproof.** The README, description and spec say "set the width to 6.75 in (height 9.25 in)".
   - The risk: Design Space normally trims the transparent margin on upload. The trimmed art is 1899×2621 px, so at a width of 6.75 in its height becomes about 9.32 in. That is over the 9.25 in limit, and Design Space will refuse the image or split it.
   - The fix: tell the buyer to "lock proportions and set the **height** to 9.25 in (the width will be about 6.7 in). Check that neither side is over 6.75 × 9.25 in." Setting the height works whether or not the margin is trimmed.
   - Update the README step 2, the HOW TO USE bullet in listing.json and LISTING.md, and `formats/printable.md`.
3. **State plainly what the buyer needs for the stickers.** Add to the description, near the top or under WHAT'S INCLUDED, and to the README: "To make the stickers you need a printer and sticker paper, plus either scissors or a cutting machine with Print Then Cut (e.g. Cricut). The machine cuts the shapes for you; no machine is needed for the scissors version." The current wording only says that printing and cutting are "not included". A buyer seeing "Print Then Cut Stickers" in the title should not assume they get finished stickers or that no machine is needed.
4. **Reword one moment:** "Get through a rainy commute, then dry off with a hot drink". You can't dry off with a drink. Use "…then warm up with a hot drink". Update `moments.json` and rebuild the PDFs and images.
5. **One-word orphans.** On Letter, "one", "dish", "better)", "good", "lantern" and "purpose" sit alone on a second line. On A4 the same happens with "5pm", "hour" and "before". On a printable this looks unedited. Tighten the wording, for example:
   - "Swap the summer blanket for the heavy one"
   - "Bring home a pocketful of acorns"
   - "Eat leftover soup the next day (even better)"
   - "Bake something so the house smells good"
   - "Take an after-dinner walk with a lantern"
   - "Do nothing on a rainy Sunday, on purpose"

   Or apply `text-wrap: pretty` / balance in `build.js`. Re-check both sizes.
6. **Description wording.** The groups are written as "home & hearth, kitchen and table, out the door, dusk and evenings", but the pages say "Kitchen & table" and "Dusk & evenings". Make them consistent, for example by using "and" for all four.
7. **Page frame margin.** The outer frame is 8.0 mm from the paper edge on both sizes, but the spec says art must be at least 9 mm. It prints fine on most home printers (clip at about 6 mm). Either move the frame in by 1 mm or change the spec to "frame line ≥ 8 mm, other art ≥ 9 mm".

## Spec (`formats/printable.md`) fixes
- **S1.** In "Sticker sheet → README/description", replace "set width 6.75 in" with the height-based step from fix 2. Add a check that the PNG's trimmed content bbox fits 6.75 × 9.25 in when scaled by either side. Alternatively, require the art to be fitted so that the trimmed bbox has the 6.75:9.25 aspect.
- **S2.** Add a required "What you need" line, as in fix 3, to the README and description rules for any print-then-cut product.
- **S3.** Add to the "Then look" checks: "any dimension box drawn on a listing image has the file's real aspect ratio and contains the art", and "no single-word orphan lines on either paper size".
- **S4.** Reconcile the 9 mm art margin with the frame (see fix 7).
- The rest of the spec is sound: the sizes, the 300 DPI/RGBA PNG, the 0.15 in gap allowing for Cricut bleed, the one-piece outlines, the ZIP contents and taxonomy 354.
