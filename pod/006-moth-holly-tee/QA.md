# QA slot: 006 (Designer built 19 Oct 2026; Printify product 6ad5edd9821a8565d600df74 created, NOT published)
Checks per formats/pod.md: art at 100% on dark colours (cream wings, holly, berries; no black halo), alpha on mid-grey, mockups (front-black/navy/dark-heather/asphalt, folded-black, folded-navy, hanging-navy) + lead-lifestyle.jpg (2x2 grid, one headline, checked at 300 px), listing copy (title 126, 13 tags <= 20), live product matches product.json (24 variants, $29.99, costs 1177/1438/1677).
Publish step after approval: `python3 tools/printify.py publish pod/006-moth-holly-tee`, then `etsy-id`, then `etsy.py lead-photos pod/006-moth-holly-tee mockups/lead-lifestyle.jpg mockups/front-black.jpg mockups/front-navy.jpg mockups/folded-black.jpg`.

## QA review (QA, 19 Oct 2026; compared with approved 005 QA.md and pod/PROVIDERS.md)

**Art (tee-front-4500x5100.png): pass.** 4500x5100 RGBA, art bbox 3529x3400 px (x 485-4014, y 336-3736), centred, no text, brand or IP (generic luna moth, holly, 4 gold sparkles). Composited on Black, Navy, Dark Grey Heather and Asphalt: cream/gold wings, sage holly and red berries read on all four, no dark halo. 100% crops (antennae, stars, berries) on black and mid-grey: clean alpha, crisp linework; the 1.31x upsample is acceptable (slight softness only, no stair-stepping). One 3 px speck beside the top-left star, invisible in print; not blocking.

**Printify product (live read-only GET): pass.** Blueprint 12 / provider 29, 24 enabled variants = Black, Navy, Dark Grey Heather, Asphalt x S-3XL, ids match product.json, all $29.99; costs 1177 / 1438 / 1677 match PROVIDERS.md. Profit (10% + $0.20 item fees, 10% of $4.49 shipping) = $14.57 S-XL, $11.96 2XL, $9.57 3XL, all >= $8. Front placeholder: the 4500x5100 file at x=0.5, y=0.5, scale 1. Unpublished (external null). Title and 13 tags on the product match product.json.

**Listing copy: FAIL (one factual error).** Title 126 chars, leads with "Moth and Holly Tee" (shopper phrase); exactly 13 unique tags, all <= 20 chars; adult unisex S-3XL, Bella+Canvas 3001 material and care, production 2-5 business days and shipping 3-7 days consistent with SAVED-REPLIES, partner line and AI disclosure present, trademark-clean. BUT the description says "Print: design about 10 in wide on the front"; the art is 3529 px = 11.8 in wide (PROMPTS.md says 12 in; 005's "about 10 in" was true for its 9.9 in art). Wrong size claim on a garment.

**Lead photo (mockups/lead-lifestyle.jpg, 2000x2020): pass.** One headline "Moth and Holly Christmas Tee", one subline "Unisex S to 3XL | 4 dark colors", clean 2x2 of real Printify fronts (Black, Navy, Dark Heather, Asphalt), one label chip each, no duplicated or garbled text, no overlaps, moth fully visible on every card, uniform background. Honest: real renders of the listed colours. At 300 px the headline and subline stay legible and the four colours read, but the moth is about 35 px wide, so it is a tidy colour grid rather than a scroll-stopper (advisory, same as 005; a tighter crop is worth an A/B test). The card corners show white mockup background behind the shirts; acceptable.

**Publish photo order: pass.** lead-lifestyle.jpg, front-black.jpg, front-navy.jpg, folded-black.jpg all exist in mockups/ and are correct colours/design. front-black/navy are clean. folded-black crops the lower wings and tails at the fold (Printify's standard folded render, same style accepted on 005); the moth and holly still read, fine as photo 4.

### Required fixes
1. Change "design about 10 in wide" to "design about 12 in wide" (or "about 11.5 in") in pod/006-moth-holly-tee/LISTING.md and product.json, then `python3 tools/printify.py update pod/006-moth-holly-tee --no-art` and re-read the product description. Nothing else needs changing.

Publish step after approval is unchanged (see top): `python3 tools/printify.py publish pod/006-moth-holly-tee`, then `etsy-id`, then the `etsy.py lead-photos` command above.

**Verdict: REJECTED**
