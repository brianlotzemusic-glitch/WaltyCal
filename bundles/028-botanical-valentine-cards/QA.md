# QA: 028 Botanical Valentine Cards & Gift Tags (printable, $3.50)

## Checked myself
- `gen.py` prints ALL CHECKS PASS. PDFs: 5 pages each, Letter and A4, fonts embedded, about 5.4 MB each; art embedded at about 270-330 ppi. ZIP holds the 2 PDFs and README-LICENSE.txt (current). Page map, sizes and license match the PDFs and listing.
- Rendered all 5 pages (Letter 100 dpi, A4 thumbnails) and 250 dpi crops of a card and two tags. 12 distinct AI motifs (lovebirds, dove, rose heart wreath, fox, bunny, hedgehog, peony, tulips, bluebird, rose, fern heart, posy): clean outlines, no extra limbs, garbled text or broken shapes. Greetings are legible and generic.
- Geometry: 4 cards per page (3.75x5 in) and 9 tags per page (2.25x3.25 in, chamfered top, hole ring); all pieces are well inside the page margins with workable gaps, grey cut lines, and long enough To/From lines. Same layout in A4. Cards are flat (README says no folding), so nothing contradicts that.
- Claims vs ZIP: 8 cards in 8 designs (2 pages x 4); 18 tags = 12 designs on page 3 plus the first 3 of page 4, and 6 repeats in a second colourway on page 4 (lovebirds, heart wreath, rose, dove, fox, posy; they also change the greeting). Counted by eye, the numbers hold. "26 cards & tags" badge = 8 + 18, true. Nothing overstated.
- listing.json: title 127 chars, leads with "Valentine Gift Tags and Cards Printable". 13 unique tags, all <=20. Disclosure line exact and last. Price 3.5. who_made/when_made fine. Description has license, digital-download note, what is not included. No trademarks, brands or IP phrases.
- Photos, all 3000x2250. 1: strong plum title block, "26 cards & tags" badge, real art on a soft pink flat-lay; reads as a code-drawn composite, not a claimed photo. 2: page previews and counts match. 3: all 18 tags, matches PDF. 4: steps and sizes correct.
- Taxonomy: `etsy.py taxonomy` shows 12482 Gift Tag Templates, 12483 Greeting Card Templates, 1261/1279 Greeting Cards / Valentines Cards (physical-card categories). A digital printable must use a Templates category, so 1261 and 1279 are wrong. 12482 is right: 18 of 26 pieces are tags, tags lead the title, and it matches 025. 12483 is an acceptable alternative if the Lister wants to test card search.

## Minor, not blocking
- Tag 5 "galentine gift tags": "Galentine's" originates from a TV show and the products contain nothing galentine-specific. Low risk, but the Lister may swap it for "friend valentine" or "valentine for friends" at listing time.
- Tartan and gingham bands are soft at 250 dpi (as in 025/026); fine at print size.
- Photo 4 has empty space at lower left, and its filename says "fold-and-stand" though the cards are flat (filename only, not visible).
- "grey" in README and photos, "gray" US spelling elsewhere. Cosmetic.
- Colorway repeats reuse the same art; the description is honest about this ("12 designs plus 6 in a second colorway").

Would I pay $3.50? Yes. Cute, cohesive, and 26 usable pieces in two sizes.

**Verdict: APPROVED**
