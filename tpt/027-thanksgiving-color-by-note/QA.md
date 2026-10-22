# QA: TpT 027 Thanksgiving Color by Note (round 1 of 2)

**Verdict: APPROVED**

QA reviewed this on 21 Oct 2026, independently of the Designer. No item files were changed.

## 1. Colour-by-code and notation: pass
- I wrote my own decoder, separate from `gen.py`. It reads `build/resource.html` and takes the key from each page's printed key cells. For Levels B and C it works out clef, pitch (from staff-line y positions), ledger-line count and stem direction/side from the drawn lines and glyphs. For Level A it reads the glyph codepoint. It then finds the region under each symbol and compares the key colour with that region's fill on the matching answer page.
- Result: all 413 symbols on 27 worksheets match their answer keys, with 0 mismatches and 0 notation issues (stems, ledger lines, clef on the right line). Every region holds at least one symbol, and all 27 keys have the same region count as their worksheets.
- `notation.py` is identical to 001's (QA-approved), so the treble C4–A5 and bass E2–C4 ranges, ledger-line rules and glyph anchors are unchanged. Level A is whole, half, quarter, eighth and quarter rest, and the beat values on the reference page are right.
- Visual checks of pages 1–3, 40 (C turkey), 49 and 58 and the preview pages: pictures are fully colourable closed regions, and the turkey key matches the worksheet. The reference-page scales are named correctly (treble C D E F G A B C D E F G A; bass E F G A B C D E F G A B C), and so are the line and space mnemonics.

## 2. Art, cover and previews: pass
- The pictures are original code-drawn line art and kid-friendly: turkey, pumpkin, cornucopia, maple leaf, acorn, apple basket, pie, corn and sunflower. No characters, brands or songs.
- At 350 px the cover title reads clearly. It follows STYLE.md: HUDSON BEAT store line, black and rust accent only, black band. The three previews are clean, and the watermark is on the page shots.
- Minor: preview-1 has about 25% empty white space above the band. This is cosmetic and does not block approval.

## 3. Technical: pass
- `gen.py --check` passes: 58 Letter pages, a 4-page preview, fonts embedded, and the images are 2000×2000.
- `tpt.json` is valid and has the same shape as 001's. Price and license price are 3.75, the tax code is set, there are 4 grades, 1 subject, 1 tag and 4 files.
- The UPLOAD.md title is 79 characters. The description is accurate (58 pages = cover, notes, reference, 27, 27, terms), and it has the disclosure line. It names no trademarks.
- Terms page: it no longer carries 001's optional "at a discount" wording (suggestion 2 from 001 is fixed here).

## 4. Price: acceptable
$3.75 is within the owner's $3.50–4 range. A 25-cent gap from 001 is fine for a seasonal set with 9 pictures and 3 levels.

## Open owner questions (do not block)
1. Price $3.75 vs 001's $3.50.
2. Whether the logo goes beside HUDSON BEAT.
3. The owner should flip through a few keys so "checked by hand" stays true.
4. Suggestion for a later build: the B/C staffs use a 5.4 pt staff space (small for grade 2). The same carries over from 001.
5. Timing: list by early November (Thanksgiving is 26 Nov).

---

# Re-review after Designer redraw (22 Oct 2026)

**Verdict: REJECT (art not yet shippable; mechanics all pass)**

Reviewed independently of the Designer: cover, all 3 previews, all 9 Level A worksheets, Level B cornucopia + its key, Level B/C pages sampled, 028 sampler (5 pages). Judged as a skeptical buyer comparing with top-selling colour-by-number sets.

## Mechanics: pass
- Own decoder (parses `build/resource.html`, shapely point-in-polygon; Level A by glyph codepoint, B/C by staff-line y of the notehead and clef): 468 symbols (156 per level), 0 mismatches vs the answer-key fills, 0 symbols ambiguous, every region holds at least one symbol (except none uncovered), worksheet and key region geometry identical. Smallest region is about 3,470 px2 in SVG units (readable).
- `gen.py --check` OK on 027 (58 pages, 3 levels, 27+27) and 028 (5 pages, 3+3). 028 "See the full set" page is correct (Halloween link, Fall listing names turkey/pumpkin/cornucopia/maple leaf, store link). tpt.json valid, tags Autumn + Thanksgiving, title "Fall Color by Note | ..." matches UPLOAD.md. tpt/001 untouched (no commits since its QA).

## Art: per picture
- 1 Friendly Turkey: **C**. Feathers are rounded blobs of uneven size, no tail-feather detail, no wattle/feet, body circle mostly hidden behind head and wing blobs. Reads as a flower with a face. Fix: 7-9 symmetrical teardrop feathers of one size in a clean fan, oval body with visible belly, a red wattle region, two feet, a head smaller than the body.
- 2 Harvest Pumpkin: **B**. Good silhouette and ribs, stem and leaves fine. The big white rib regions are easy to colour. Minor: vines missing; stem region has a note touching its edge.
- 3 Cornucopia: **C- (worst)**. Not recognisable as a horn: it is a bent grey-brown tube with a lumpy bend, an orange disc with two stray parentheses, a pear, an apple and leaves piled on it. Odd polygonal outline with kinks. Fix: redraw as a classic horn (wide curled mouth opening left, tapering tail curling up right) with a woven-band pattern, and fruit spilling from the mouth in a clear row (apple, pear, grapes, small pumpkin); remove the parenthesis highlights.
- 4 Maple Leaf: **B-**. Recognisable, but veins are thick bars that do not close regions, so the leaf is effectively 3 big blobs; stem is very heavy. Fix: thinner stem, close the veins so each lobe is its own region.
- 5 Acorn: **B**. Cap scallops good, nut oval patch looks odd (floating ellipse); thick stem OK. Fix: drop or reshape the highlight.
- 6 Apple Basket: **B**. Clear, big handle, nice weave cells. Apples are plain circles overlapping with stems that float; add a leaf per apple.
- 7 Pumpkin Pie: **C**. Perspective is confused: scalloped crust ellipse, an inner filling ellipse and a lower rim ellipse do not agree; slice lines stop in mid-air. Fix: a straight 3/4 view (rim ellipse + side band + filling + whipped cream swirl) with 6 slice regions.
- 8 Corn on the Cob: **C**. Egg-shaped grid of rectangles does not read as kernels; husks are two leaf blobs. Fix: elongated cob with rows of rounded kernels, 2-3 husk leaves peeling down.
- 9 Sunflower: **B**. Best of the set: 14 petals, dotted seed head, stem and leaves. The dotted ring is fine. Petals are slightly uneven.
- Cover: **B-**. Turkey is the weakest picture and is the hero of the cover, so it carries the C. Layout, title and black band are good. Previews 1-3 are clean and the coloured 9-picture grid looks professional; the worksheets themselves look weaker than the coloured previews (marketing/product gap).
- 028 Sampler: **B**. It uses the three best pictures (sunflower, acorn, basket), so it is fine as is; if the set is redrawn, rebuild it.

## Buyer view
At $3.75 a teacher would likely buy for the music levels, but with the turkey on the cover and a cornucopia nobody can identify, the first page reviews would say the pictures are childish and odd. Top sellers have recognisable symmetrical subjects. Not proud to ship.

## Required before approval
1. Redraw turkey (cover hero) and cornucopia as described.
2. Fix pie and corn (C to at least B); polish maple leaf veins.
3. Rebuild 027 and 028, re-run `gen.py --check`, regenerate previews and cover.

## Open questions
- Owner: acceptable to drop cornucopia for a simpler subject (e.g. a leaf wreath or a pilgrim hat) if it cannot be drawn well?

---

# Round 2 re-review (after Designer's second redraw, commit e58247d): REJECT

Reviewed independently: cover, 3 previews, 9 Level A worksheets + 9 keys rendered at 100 dpi (Level B/C pages viewed in the previews and sampled), as a skeptical buyer comparing with top-selling colour-by-number sets.

## Mechanics: pass
- Own decoder (shapely point-in-polygon on build/resource.html): Level A 162 symbols over 9 pictures, 0 mismatches vs answer-key fill, 0 symbols outside a region, 0 regions without a symbol, worksheet and key geometry identical. Levels B/C share the same geometry; their symbol-to-colour mapping was verified by `gen.py --check` only this round.
- `gen.py --check` OK on 027 (58 pages, 3 levels, 27+27, 390 regions) and 028 (5 pages, 3+3). 028 "See the full set" page present (Halloween link, Fall listing). 028 tpt.json valid; 027 tpt.json has no top-level "title" key (title lives in UPLOAD.md; not a defect, flagged). tpt/001 untouched since last QA.

## Art grades
- 1 Friendly Turkey: **B**. Big improvement: 7 matching teardrop feathers in a symmetric fan, round body, wings, feet. Remaining: quill lines look like stray sticks, beak is a small black triangle with no red wattle, face is a flat circle with a stray whole-note oval on the cheek, body is a plain dark circle. Clean and recognisable but still plain.
- 2 Harvest Pumpkin: **B**. Unchanged and fine.
- 3 Cornucopia: **C+**. Now a horn shape, but the mouth is not a clear opening, the weave is a few wedges rather than bands, and the fruit is a clumped pile with overlapping circles and a stem touching the apple; the pear and leaf float. Still the weakest subject apart from corn. Fix: either simplify to a horn with an obvious oval mouth and 3-4 woven bands plus 3 non-overlapping fruits in a row, or swap for a simpler subject (leaf wreath, pilgrim hat, acorn pair).
- 4 Maple Leaf: **B**. Recognisable, lobes separate.
- 5 Acorn: **B**. Unchanged.
- 6 Apple Basket: **B**. Unchanged.
- 7 Pumpkin Pie: **C+**. Still a flat top-down oval with huge scalloped crust and a separate tin band below that does not match the perspective; four slice regions fine but the cream blob is tiny and cute-less. Fix: a true 3/4 view (rim ellipse, one side band with a fluted edge, filling, whipped cream swirl) or a simple top-down circle pie with 6-8 wedge slices.
- 8 Corn on the Cob: **C**. Still an egg of a grid with a stem on top; husks are two big blobs. Does not read as corn. Fix: swap for a simpler subject, or draw a pointed cob with rounded kernels in staggered rows and 3 narrow husk leaves.
- 9 Sunflower: **B**. Unchanged.
- Cover: **B**. Layout and title strong, turkey is now clean; but the cover is mostly uncoloured line art next to the title and looks dull against coloured competitor covers. A coloured turkey (as in the preview) would lift it to B+.
- 028 Sampler: **B**.

## Verdict: REJECT
Cover and turkey are B, not B+; pie (C+), cornucopia (C+) and corn (C) are below B. Fixes: see per-picture notes above (corn is the weak spot; swap allowed). Re-run `gen.py --check` for 027 and 028 after any change; 028 shares pictures.py.

---

# Round 3 re-review (after Designer round 3, commit afc3bbd): REJECT (close)

Reviewed independently as a skeptical buyer: cover, 3 previews, all 9 Level A worksheets, Level A keys for turkey/pie/owl/maple, Level B turkey and Level C owl pages, pie at 150 dpi crop, 028 page 5.

## Mechanics: pass (all three levels decoded this time)
- Own decoder (parses `build/resource.html`; Level A by glyph codepoint vs the key's printed names, Levels B and C by staff-line y of the notehead -> letter, clef on its correct line, ledger-line count, stem direction; shapely point-in-polygon for the region): 517 symbols (A, B and C, 9 pictures each), 0 mismatches vs the answer-key fill, 0 symbols outside a region, 0 regions without a symbol, 0 clef/ledger/stem issues, worksheet and key geometry identical. Matches `gen.py`'s own count (423 regions, 517 symbols).
- `gen.py --check` OK for 027 (58 pages, preview 4 pages, fonts, 2000x2000) and 028 (5 pages, 3+3). Labels and staves legible at 100 dpi. 028 "See the full set" is accurate: turkey, pumpkin, owl and pumpkin pie are all in 027; Halloween link and store link present. tpt/001 untouched (no commit since its QA).

## Art grades
- 1 Friendly Turkey: **A-**. Symmetric 7+7 feather fan, wattle, wings, feet, head smaller than body. Clean, recognisable, comparable to top sellers. Only nit: the worksheet body is a plain grid of big regions (easy colouring, fine).
- 2 Harvest Pumpkin: **B**.
- 3 Forest Mushrooms: **B+**. Instantly readable, big spotted cap, small second mushroom, clean regions.
- 4 Maple Leaf: **B-**. Unchanged: thick stem and four thick bars inside the lobes that look like scratches and close nothing. The bars are the one amateur detail left in the set.
- 5 Acorn: **B**. Highlight gone, good.
- 6 Apple Basket: **B**.
- 7 Pumpkin Pie: **B-**. Top-down plate, scalloped crust, filling and cream swirl are readable, and the lifted slice is a nice idea. Defects at 150 dpi: the removed-slice gap and the slice lines read as a pinwheel/wagon wheel on the black-and-white worksheet; crust on the cut slice ends in a sharp pointed shard that pokes past the plate edge area; the crust ring is off-centre (thick top-left, thin bottom-right); the cream swirl is white like the plate and the gap, so the three whites merge in the key. Fix: centre the crust ring on the filling, make the cut-slice crust end square, give the cream a one-colour fill and the plate a pale grey or accent colour in the key, and shorten or remove the gap so the pie reads as a whole pie with one slice line.
- 8 Autumn Owl: **B+**. Big eyes, ear tufts, feathered chest, perched on a branch with leaves; charming and professional.
- 9 Sunflower: **B**.
- Cover: **B+**. Turkey filled with three tints of the one rust accent plus black on white, feather depth reads well, title and band strong. This is a clear step up from the uncoloured cover and holds up at thumbnail size.
- Previews 1-3: **B+**. The 9-picture grid is attractive. 028 sampler: **B**.

## Verdict: REJECT (near-miss: two pictures at B-)
Turkey and cover meet B+ and the set is much improved, but maple leaf (B-) and pie (B-) are under the B bar. Fix list: maple leaf, replace the four thick bars with thin lines that close each lobe into its own region and slim the stem; pie, as in the grade note above. Rebuild 027 and 028 (028 shares pictures.py but uses sunflower/acorn/basket, so it is unaffected unless pictures.py changes them), rerun `gen.py --check`.

## STYLE.md one-accent rule vs the tinted cover
STYLE.md section 2 says cover art "uses only the accent and black" and cites 001's orange-and-black fill. The new cover uses three tints of the accent (#E08A5C, #F6D2BC, #6E2A0F) plus black. I judge it within the spirit: still one hue, no new colours, no extra store chrome; the tints are the reason the cover now looks finished. But the letter of the rule is "accent + black", so STYLE.md should be amended in one line ("tints and shades of the single accent are allowed on the cover art") and `gen.py` already labels them cover-only. Owner/Designer to confirm; not a blocker.

## Title consistency (Thanksgiving vs "Fall")
- The listing title is "Fall Color by Note | ..." because TpT's Seasonal Titles notice blocked a holiday-named title; the pictures are general autumn (mushrooms, owl, maple, acorn, sunflower, only the turkey and pie are holiday-ish). The product itself still says THANKSGIVING on the cover (the biggest word), every worksheet header, the teacher page, preview 1/3 band and the resource.html title. A buyer or TpT reviewer opening the thumbnail sees "THANKSGIVING" against a "Fall" title; that mismatch is likely to re-trigger the notice and is also a conversion risk (not Thanksgiving-only use). Recommendation: **yes, change to Fall**. Exact text fixes in `tpt/027-thanksgiving-color-by-note/gen.py` (folder, file slugs and tpt.json name can stay; renaming the PDF is optional):
  1. L316 worksheet header `Thanksgiving Color by Note` -> `Fall Color by Note` (every worksheet, and the answer-key headers that share the pattern).
  2. L352 cover `<div class="a">THANKSGIVING</div>` -> `FALL` (keep `COLOR BY NOTE` big line).
  3. L361 teacher page `Thanksgiving Color by Note · 3 levels · grades 1–5` -> `Fall Color by Note · ...`.
  4. L370 teacher bullet `before or after Thanksgiving and autumn lessons` -> `before or after autumn lessons` (Thanksgiving may stay as one mention in the description, not in headers).
  5. L499 preview 1 headline `Thanksgiving` -> `Fall`; L514 band `9 Thanksgiving pictures` -> `9 Fall pictures` (or `9 autumn pictures`).
  6. L572 document title -> `Fall Color by Note`.
  7. The word-list check at L711 requires `Thanksgiving` in UPLOAD.md; keep it in section 4 (subject) and the description's closing sentence only.
  8. UPLOAD.md: description is already Fall-led; the line "(including a Thanksgiving week activity)" is fine as a use case. Rename 027's folder/PDF only if the owner wants; filenames are not shown to buyers on the listing but the PDF name is seen on download: suggest `fall-color-by-note.pdf` (update SLUG, UPLOAD.md, tpt.json, and `tools/tpt.js` if it refers to the file).
- Also, STYLE.md's colour table lists "Thanksgiving/fall rust"; harmless.

## Open questions for owner
1. Approve changing the cover/headers to FALL (recommended) and renaming the PDF?
2. Accept tints of the accent on cover art (STYLE.md one-line amendment)?
3. Maple leaf and pie redraws need one more Designer pass; the rest can ship as is.
