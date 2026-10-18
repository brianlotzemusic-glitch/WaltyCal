# QA slot: 005 (Designer built 18 Oct 2026; Printify product created, NOT published)
Checks per formats/pod.md: art at 100% (wreath, 4 animals, text), alpha on mid-grey, 4 mockups + lead-lifestyle.jpg, listing copy, live product matches product.json.
Verdict: (QA fills in) 
Publish step after approval: `python3 tools/printify.py publish pod/005-family-christmas-woodland-tee`, then `etsy-id`, then `etsy.py lead-photos pod/005-family-christmas-woodland-tee mockups/lead-lifestyle.jpg mockups/folded-natural.jpg mockups/folded-white.jpg mockups/front-ash.jpg`.
