# Shop factory — operating manual

This branch (`shop-factory`) is the Etsy shop's workspace. It has no history in common with `main`; never merge them.

## Layout
- `bundles/NNN-slug/` — one Etsy listing each: `gen.py`, buyer ZIP, `listing-images/`, `LISTING.md`, `listing.json`, and `etsy_listing_id` once uploaded
- `tools/` — `render.js`, `thumbs.js` (rendering), `etsy.py` (API: upload, stats), `etsy_auth.py` (one-time login, run by the owner)
- `queue.md` — themes waiting to be built, in priority order
- `office/status.json` — what every worker is doing; the owner's office dashboard reads this file
- `log/ACTION-LOG.md` — every action, with timestamp and reason
- `stats/listings.csv` — written by `etsy.py stats`
- `reports/` — weekly reports

## The team
One scheduled **Manager** run fires every hour. The Manager decides which specialists are due, runs each one as a separate subagent (Agent tool) with a focused brief, and records the results. Specialists never run on their own schedule.

| Worker | Job | Due when |
|---|---|---|
| Manager | Reads state, assigns work, updates `office/status.json`, writes the weekly report (Mondays) | Every run |
| Researcher | Web-searches Etsy trends and seasonal timing; reorders `queue.md`; adds themes when fewer than 8 remain | Last research older than 24 h |
| Designer | Builds ONE bundle from the top unchecked theme (spec below) | Last bundle older than 11 h (so at most 2 per day) |
| QA | Independent review of the Designer's bundle: looks at the contact sheet, runs the checks, sends it back to the Designer with specific fixes or approves it. Max 2 rounds; a bundle that still fails is moved to `bundles/_rejected/` and not listed | Right after the Designer |
| Lister | Uploads approved bundles that have no `etsy_listing_id` (`python3 tools/etsy.py upload bundles/NNN-slug`) | Etsy variables set and fewer than 2 uploads today |
| Analyst | `python3 tools/etsy.py stats`, then applies the optimization rules | Etsy variables set and stats older than 24 h |

Work out "last done" times from `office/status.json` and `git log`. If nothing is due, the Manager only refreshes the status file (workers shown as idle with what they're waiting for) and ends the run.

## Bundle spec (Designer + QA)
- `pip install shapely ezdxf pillow` first. Playwright + Chromium are preinstalled; run node scripts with `NODE_PATH=$(npm root -g)`.
- Follow an existing bundle in `bundles/` as the template (002–005 are the strongest).
- 6 original designs, each ONE connected closed shape, no hole under 600 units² (1000-unit design space), SVG 6 in, PNG 1800 px transparent, DXF in inches that re-opens in ezdxf
- Buyer ZIP with SVG/, PNG/, DXF/, README-LICENSE.txt
- 4 listing images at 3000×2250
- `LISTING.md` + `listing.json`: title ≤140 chars, exactly 13 tags each ≤20 chars, AI-disclosure line in the description, price per the pricing rule
- Every design must clearly read as what it is at thumbnail size and look balanced. Never ship a bundle you would not pay for.

## office/status.json
Rewrite it at the end of every run (and after each specialist finishes, if the run is long). Keep this shape:
```json
{
  "updated_at": "ISO-8601 UTC",
  "next_run_at": "ISO-8601 UTC",
  "goal_usd": 70000,
  "revenue_usd": 0,
  "listings_live": 0,
  "bundles_built": 0,
  "uploads_pending": 0,
  "etsy_connected": false,
  "workers": [
    {"id": "manager|researcher|designer|qa|lister|analyst", "name": "Manager", "state": "working|idle|blocked", "task": "one plain sentence", "since": "ISO-8601 UTC"}
  ],
  "queue": ["next 5 theme names"],
  "feed": [{"t": "ISO-8601 UTC", "who": "designer", "msg": "one plain sentence"}]
}
```
`feed` is newest first, capped at 30 entries. Use `blocked` only when a worker can't proceed without the owner (e.g. Lister and Analyst while the Etsy variables are missing), and say what's needed in `task`.

## Each run ends with
Tick finished themes in `queue.md`, append to `log/ACTION-LOG.md`, update `office/status.json`, commit, `git push -u origin shop-factory` (retry up to 4 times on network errors; never force-push).

## Rules
- Original work only. No copyrighted characters, logos, brand names, trademarked phrases, or other sellers' designs. Avoid "Creepmas".
- No weapons, hate content, medical claims, or adult content.
- Pricing: $4.00 per 6-design bundle until stats exist; after that, match the median of the shop's converting listings.
- At most 2 new listings per day (avoid looking like a bulk-AI shop).
- New listings stay drafts unless `ETSY_PUBLISH=1` is set.
- Optimization, once listings have data:
  - Below 0.5% conversion after 200 views → rewrite title, tags and thumbnail once; if still below after another 200 views, deactivate.
  - Above 3% conversion → move similar themes to the top of `queue.md`.
  - Every 2 weeks: change the title or thumbnail on the 3 listings with the most views and the lowest conversion, and log the before/after.
- Weekly (first run on Monday after 12:00 UTC): write `reports/YYYY-MM-DD.md` with listings created, revenue, top listing with metrics, and the next 3 actions.
