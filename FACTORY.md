# Shop factory — operating manual

This branch (`shop-factory`) is the Etsy shop's workspace. It has no history in common with `main`; never merge them.

## Layout
- `bundles/NNN-slug/` — one Etsy listing each: `gen.py`, buyer ZIP, `listing-images/`, `LISTING.md`, `listing.json`, and `etsy_listing_id` once uploaded
- `tools/` — `render.js`, `thumbs.js` (rendering), `etsy.py` (API: upload, stats), `etsy_auth.py` (one-time login, run by the owner)
- `queue.md` — themes waiting to be built, in priority order
- `log/ACTION-LOG.md` — every action, with timestamp and reason
- `stats/listings.csv` — written by `etsy.py stats`
- `reports/` — weekly reports

## Each production run (scheduled twice daily)
1. `pip install shapely ezdxf pillow` (Playwright + Chromium are preinstalled; run node scripts with `NODE_PATH=$(npm root -g)`).
2. If `ETSY_REFRESH_TOKEN` is set: run `python3 tools/etsy.py stats`, then apply the rules below before building anything.
3. Take the top unchecked theme from `queue.md` that is not marked "in progress". Build ONE bundle in `bundles/NNN-slug/` following an existing bundle as the template:
   - 6 original designs, each ONE connected closed shape, no hole under 600 units² (1000-unit design space), SVG 6 in, PNG 1800 px transparent, DXF in inches
   - Buyer ZIP with SVG/, PNG/, DXF/, README-LICENSE.txt
   - 4 listing images at 3000×2250
   - `LISTING.md` + `listing.json`: title ≤140 chars, exactly 13 tags each ≤20 chars, AI-disclosure line in the description, price per the pricing rule
   - Render a contact sheet and look at it. If a design doesn't clearly read as what it is, or looks unbalanced, fix it or replace it. Never ship a bundle you would not pay for.
4. If the Etsy variables are set and `log/` shows fewer than 2 uploads today: `python3 tools/etsy.py upload bundles/NNN-slug`.
5. Tick the theme in `queue.md`, append to `log/ACTION-LOG.md`, commit, `git push -u origin shop-factory`.
6. When the queue has fewer than 5 themes left, add new ones: seasonal themes 6–10 weeks ahead of the holiday, plus year-round themes in niches where sales data shows traction.

## Rules
- Original work only. No copyrighted characters, logos, brand names, trademarked phrases, or other sellers' designs. Avoid "Creepmas".
- No weapons, hate content, medical claims, or adult content.
- Pricing: $4.00 per 6-design bundle until stats exist; after that, match the median of the shop's converting listings.
- At most 2 new listings per day (avoid looking like a bulk-AI shop).
- Optimization, once listings have data:
  - Below 0.5% conversion after 200 views → rewrite title, tags and thumbnail once; if still below after another 200 views, deactivate.
  - Above 3% conversion → move similar themes to the top of `queue.md`.
  - Every 2 weeks: change the title or thumbnail on the 3 listings with the most views and the lowest conversion, and log the before/after.
- Weekly (Monday run): write `reports/YYYY-MM-DD.md` with listings created, revenue, top listing with metrics, and the next 3 actions.
