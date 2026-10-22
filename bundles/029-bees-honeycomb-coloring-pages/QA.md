# QA: 029 Bee & Honeycomb Coloring Pages (round 1)

## Summary
REJECTED, two small fixes needed (page 05 art, disclosure line). Everything else is clean.

## Required fixes
1. **Page 05 Sunflower and bees (lower left, around the stem and leaf):** at 150 dpi the leaf behind the flower is tangled. There is a stray black wedge at the leaf tip (left), a loose straight line segment inside the leaf, and the bee's antenna runs into the second leaf. Redraw so the two leaves are clean closed shapes clear of the bee and the stem, with no stray marks. Re-run process.py, build.js, thumbs.js and gen.py --check. The page grid image must be refreshed after.
2. **AI-disclosure line is not honest for this bundle.** PROMPTS.md and LISTING.md state the art is drawn in code with no AI, yet the description ends "Designed with the help of digital and AI tools". FACTORY.md already allows the plain form when no AI was used for the design (POD section: "or the plain 'Designed by Duskwood Designs Co' if no AI was used"). Change the last line of the description in listing.json and LISTING.md to: "Designed by Duskwood Designs Co, drawn with digital tools and checked by hand." and update the gen.py check to expect it. Also drop the open-question wording in LISTING.md "Creation method": with no AI, the owner should tick Etsy's "I made it / no AI" option (the owner still confirms in the Etsy form).

## Checks passed
- `python3 gen.py --check`: ALL CHECKS PASS (QA re-ran it). Median stroke at least 2.07 mm, smallest space 12 mm2, worst page 2 nooks (0.01%), margin 17 mm Letter and 14 mm A4, closest page pair 150 bits.
- ZIP (unpacked): exactly Letter PDF, A4 PDF and README-LICENSE.txt. Matches LISTING.md. PDFs 20 pages each, correct sizes, 0.9 MB, no fonts or text.
- Listing: title 126 chars, leads with "Bee Coloring Pages", one "&" in the images only (title has "&" once). 13 unique tags, longest 19. Price $3.99. Taxonomy 339 (Coloring Books) matches 014, 024 and formats/coloring.md. No IP phrases (no brands, characters, trademarks). "National Honey Bee Day" is a generic observance, fine. Page list in listing matches the contact sheet.
- Listing images: 4 at 3000x2250. They show real pages, counts and names match, colored examples labelled as examples, the copy says black and white files. Honest.
- Pages 1-20 (contact sheet and 100% crops): bold even lines, closed colourable spaces, rounded frame, no text, no grey. Bees are well formed and consistent. Page 03 door is a deliberate solid black arch (acceptable). Pages 01-04, 06-20 are good. Same style across all pages, though the set is simpler than the 024 AI pages (bold and easy as promised).
- Cost: $0, no paid calls, no Etsy edits.

## Open questions
- Etsy's own AI-content tick box: with no AI used, the owner/Lister should answer it as not AI-generated.

# Round 2

## Verdict
APPROVED.

## Verified independently
- Page 05, rendered at 100% and 150 dpi from the Letter PDF inside the ZIP: both lower leaves are clean closed shapes, no stray wedge, no loose line segment; the lower bee was moved clear of the leaves and stem, antenna touches nothing. Upper bee sits beside the petals with no tangle. Only a tiny pinch where the right leaf meets the stem (cosmetic, still colourable).
- listing-images/2-page-grid.png shows the redrawn page 05 (same as the PDF) and still lists 20 pages with matching names.
- Other pages: pixel diff of the round-1 ZIP vs the shipped ZIP at 100 dpi shows pages 01-04 and 06-20 identical; only page 05 differs. Letter and A4 PDFs are 20 pages each, correct sizes, no text or fonts.
- Disclosure: last line of listing.json description and LISTING.md is "Designed by Duskwood Designs Co, drawn with digital tools and checked by hand." (identical). LISTING.md Creation method now says no AI, owner ticks Etsy's option and confirms.
- ZIP contents: Letter PDF, A4 PDF, README-LICENSE.txt, matching LISTING.md.
- `python3 gen.py --check`: ALL CHECKS PASS.
- Cost $0, no Etsy edits.

## Open questions
- Owner confirms Etsy's AI-content answer (not AI-generated) at listing time.
