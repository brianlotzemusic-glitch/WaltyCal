# QA: 026 Thanksgiving Place Cards (printable, $3.50)

## Checked myself
- `gen.py` prints ALL CHECKS PASS. PDFs: 5 pages each, Letter 612x792 and A4 594.96x841.92, Nunito and Fraunces embedded, about 6 MB each. ZIP holds the 2 PDFs and README-LICENSE.txt (identical to the bundle copy). README page map, sizes and license match the PDFs and listing.
- Rendered all 5 pages in Letter and the same pages in A4, plus a 220 dpi crop of a card. 12 distinct, clean AI motifs (fox, hedgehog, squirrel, owl, turkey, deer, acorns, oak leaf, wheat, mushrooms, maple, apple) with no artefacts, garbled text or clipped art. Tartan, gingham, stripe and dot bands are present and varied. Cards are 3.5x4 in flat with a grey rounded cut line, small grey margin ticks beside each fold, a dashed fold line in the middle of the band, a name line on both halves (top half is upside down, so both faces of the tent read correctly) and a greeting. Nothing is near the page margins. Gaps between cards are wide enough to cut. They can be printed, cut, scored and folded into 3.5x2 in tents as the guide says.
- Menu tents (page 4): Mains, Sides, Desserts, Drinks, each with a matching motif, the word on both faces, and two write-in lines per face. Correct. 12 place cards + 4 menu tents = 16, so the "16 cards" badge is accurate.
- Page headers read "1 OF 5" to "4 OF 5" on the card pages; the guide is page 5. Correct.
- listing.json: title 138 chars, leads with "Thanksgiving Place Cards Printable". 13 unique tags, longest 20. Disclosure line is exact and last. Price 3.5. Description counts match (12 designs, 3 pages x 4, 4 menu tents, 5 pages, Letter + A4). It has instant-download wording, license, how-to, and what is not included (printing, card stock). LISTING.md matches. US spelling in the description. No "Friendsgiving", no trademarks or IP.
- Taxonomy: `etsy.py taxonomy place cards` lists 2102 (Place Cards & Holders > Place Cards). Correct. 6056 is Weddings, so 2102 is the right choice.
- Photos, all 3000x2250. Photo 1: plum title block ("Thanksgiving Place Cards"), warm "16 cards Letter + A4" badge, five cards standing on a wood table with leaves and acorns. One headline, honest (a code-drawn flat-lay, not a claimed photo of a physical product), should stand out in an autumn search grid. Photos 2-4 are accurate (real page previews, counts, steps and sizes).

## Minor, not blocking
- "Count Blessings" (oak leaf card) is a common secular phrase, but it is the closest thing to religious wording in the set. Swapping it for e.g. "Count Your Joys" would remove any doubt.
- The tartan bands look slightly soft at 220 dpi (blurred plaid threads). Fine at print size.
- README, listing and photos use "grey" where US spelling is "gray". Cosmetic, same as 025.
- Photo 1 shows the cards as flat panels rather than true folded tents. Acceptable for a mockup.

Would I pay $3.50? Yes. It is a cohesive, usable set with two sizes and useful menu tents.

**Verdict: APPROVED**
