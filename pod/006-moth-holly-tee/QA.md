# QA slot: 006 (Designer built 19 Oct 2026; Printify product 6ad5edd9821a8565d600df74 created, NOT published)
Checks per formats/pod.md: art at 100% on dark colours (cream wings, holly, berries; no black halo), alpha on mid-grey, mockups (front-black/navy/dark-heather/asphalt, folded-black, folded-navy, hanging-navy) + lead-lifestyle.jpg (2x2 grid, one headline, checked at 300 px), listing copy (title 126, 13 tags <= 20), live product matches product.json (24 variants, $29.99, costs 1177/1438/1677).
Publish step after approval: `python3 tools/printify.py publish pod/006-moth-holly-tee`, then `etsy-id`, then `etsy.py lead-photos pod/006-moth-holly-tee mockups/lead-lifestyle.jpg mockups/front-black.jpg mockups/front-navy.jpg mockups/folded-black.jpg`.

## QA review
(pending)
