# QA slot: 005 (Designer built 18 Oct 2026; Printify product created, NOT published)
Checks per formats/pod.md: art at 100% (wreath, 4 animals, text), alpha on mid-grey, 4 mockups + lead-lifestyle.jpg, listing copy, live product matches product.json.
Publish step after approval: `python3 tools/printify.py publish pod/005-family-christmas-woodland-tee`, then `etsy-id`, then `etsy.py lead-photos pod/005-family-christmas-woodland-tee mockups/lead-lifestyle.jpg mockups/folded-natural.jpg mockups/folded-white.jpg mockups/front-ash.jpg`.

## QA review (QA, 18 Oct 2026)
Note: 003/004 have no QA.md in the repo; compared against their LISTING.md, product.json and pod/PROVIDERS.md instead.

**Art (tee-front-4500x5100.png): pass.** 4500x5100 RGBA, art bbox 2954 px wide (about 9.9 in, matches the "about 10 in" claim), horizontally centred (centre x 2250), placed in the upper chest area. Looked at it on mid-grey and at 100%: fox, deer, owl, hedgehog, pine, holly, pinecones; "FAMILY CHRISTMAS 2026" is legible, centred in the wreath, no stray pixels or halo, clean alpha edges. No brand, character or IP. Colours (dark plum text, green, rust, mustard, red) hold contrast on White, Natural, Soft Cream and Ash (seen on the Printify mockups). The type is small relative to the wreath (about 8 percent of the print width) but readable at thumbnail on the front mockups.

**Printify product (live read-only via the API): pass.** Blueprint 12 / provider 29, 24 enabled variants = White, Natural, Soft Cream, Ash x S-3XL, ids match product.json, all priced $28.99 (2899), costs 1177 (S-XL), 1438 (2XL), 1677 (3XL) match PROVIDERS.md. Profit $13.67 / $11.06 / $8.67, all >= $8; 3XL sets the price as on 003/004. Front placeholder uses the 4500x5100 file at x=0.5, y=0.5, scale 1. Not published (external is empty). Title and 13 tags on the product match product.json.

**Listing copy: pass.** Title 130 chars, leads with "Family Christmas 2026 Shirt". Exactly 13 tags, all <= 20 chars, no duplicates. Description: adult unisex S-3XL, Bella+Canvas 3001 material and care, production 2-5 business days and shipping consistent with SAVED-REPLIES, partner line, disclosure line present, no false claims. Trademark: "Family Christmas 2026" is a generic phrase, no brand; flag only (the USPTO database was not checked by the Designer; recommend a quick TESS check at publish time), not blocking.

**Lead photo (mockups/lead-lifestyle.jpg): FAIL.** The composite has visible layout defects that would go out as the first Etsy photo:
1. The headline renders as "Family Christmas 2026 026": a second copy of the text is clipped and overlaps behind the headline, so "2026" is duplicated/garbled.
2. A stray fragment "m, Ash" (the tail of a second "White, Natural, Soft Cream, Ash" line) sits to the right of the real colours line, partly hidden by the Ash mockup card.
3. The Ash card overlaps the text block and the left text panel has a hard cut-off edge on the right (a lighter rectangle ends at about x=1140), so the background looks mismatched and unfinished.
4. The Ash mockup card is cropped to a grey rectangle (the shirt image has a visible rectangular edge at the bottom), and the folded-natural card crops the hedgehog and cuts the wreath off at the card edge.
The plain Printify renders (front-*.jpg) are fine; only the composite is broken.

### Required fixes
1. Rebuild mockups/lead-lifestyle.jpg: remove the duplicated/overlapping headline text and the stray "m, Ash" fragment, make the text panel and background one clean layer, keep the Ash card from overlapping text, and use a folded-natural crop that shows the whole wreath (or swap it for front-natural). Re-view at full size and at Etsy thumbnail size before resubmitting.
2. Update mockups.json etsy_lead_photo_plan if the photo order changes (the publish instructions above name lead-lifestyle.jpg, folded-natural.jpg, folded-white.jpg and front-ash.jpg).
Nothing else needs changing; Printify product, art and copy are approved as they stand.

(fix round: lead photo rebuilt)

**Verdict: REJECTED**
