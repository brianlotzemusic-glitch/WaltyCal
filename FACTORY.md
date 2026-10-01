# Shop factory — operating manual

This branch (`shop-factory`) is the Etsy shop's workspace. The shop is **Duskwood Designs Co** (etsy.com/shop/DuskwoodDesignsCo); use that name in README-LICENSE files, listing images and copy. Shop profile text and branding live in `shop-profile/`. It has no history in common with `main`; never merge them.

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
| Researcher | Web-searches Etsy trends and seasonal timing across **all digital product types** (see "Product formats"); reorders `queue.md`; adds themes when fewer than 8 remain; proposes new formats | Last research older than 24 h |
| Designer | Builds ONE bundle from the top unchecked theme (spec below) | Last bundle older than 11 h (so at most 2 per day) |
| QA | Independent review of the Designer's bundle: looks at the contact sheet, runs the checks, sends it back to the Designer with specific fixes or approves it. Max 2 rounds; a bundle that still fails is moved to `bundles/_rejected/` and not listed | Right after the Designer |
| Lister | Uploads approved bundles that have no `etsy_listing_id` (`python3 tools/etsy.py upload bundles/NNN-slug`) | Etsy variables set and fewer than 2 uploads today |
| Analyst | `python3 tools/etsy.py stats`, then applies the optimization rules | Etsy variables set and stats older than 24 h |
| Scout | Researches which business to open next (see "New businesses"); writes `ventures/research/YYYY-MM-DD.md` and re-ranks `ventures/shortlist.md` | Last research older than 7 days |
| Launcher | Builds a launch kit for the Scout's #1 pick (see "New businesses") | Venture gate met, and no kit in progress or the last kit's owner steps are done |

Work out "last done" times from `office/status.json` and `git log`. If nothing is due, the Manager only refreshes the status file (workers shown as idle with what they're waiting for) and ends the run.

## Design direction (Researcher + Designer)
The owner wants a wide range of themes, not gothic everything. Duskwood's look is moody, natural and a little whimsical: woodland animals, birds, botanicals and florals, mushrooms, celestial (moons, stars), cozy seasonal (autumn, winter, spring), cottagecore, and some dark or gothic designs. Choose themes from buyer demand across all of these.
- Gothic, spooky and dark-holiday themes: no more than 1 in 3 of the unchecked queue, and never two in a row.
- Mix seasonal themes (in time for their sales windows) with year-round ones.
- Existing themes stay only if they still rank well against the new ones.
- Proven sellers first: on each run the Researcher looks for digital-download listings of any type selling heavily now (about the last 60 days; 1,000+ sales is the owner's bar). Evidence comes from sales estimators, Bestseller and "bought in the last 24 hours" signals, and marketplace bestseller lists. Every figure is labelled as an estimate with its source. Themes with proven demand go to the top of the queue.
- Take the subject and format from a proven seller, never the design. The Designer makes original designs only. Never trace, redraw or closely imitate another seller's listing, composition, style or text.

## Bundle spec (Designer + QA)
- `pip install shapely ezdxf pillow potracer numpy` first. Playwright + Chromium are preinstalled; run node scripts with `NODE_PATH=$(npm root -g)`.
- Follow an existing bundle in `bundles/` as the template (002–005 are the strongest).
- 6 original designs, each ONE connected closed shape, no hole under 600 units² (1000-unit design space), SVG 6 in, PNG 1800 px transparent, DXF in inches that re-opens in ezdxf
- Buyer ZIP with SVG/, PNG/, DXF/, README-LICENSE.txt
- 4 listing images at 3000×2250
- `LISTING.md` + `listing.json` (with `"taxonomy_id": 12394`, Etsy's Craft Supplies & Tools > Patterns & How To > Craft Machine Files > Cutting Machine Files): title ≤140 chars, exactly 13 tags each ≤20 chars, this exact disclosure line at the end of the description (no separate heading): "Designed with the help of digital and AI tools, and checked by hand for clean cuts.", price per the pricing rule
- Every design must clearly read as what it is at thumbnail size and look balanced. Never ship a bundle you would not pay for.

## Product formats (Researcher + Designer + QA)
Cut files are the core, but the shop can sell any digital download the factory can produce to a sellable standard with code (vector drawing, rendering, PDF generation). AI images: when `OPENAI_API_KEY` is set, the Designer may use `tools/imagegen.py` (OpenAI Images API). `gen` makes a PNG (use `--transparent` for clipart and stickers); `trace` turns black-on-white artwork into a single-path SVG for cut files, which must then pass the normal cut-file checks (prompt for bold black silhouettes on plain white, no gradients). Rules: prompts describe original designs only (never artist names, brands, characters, trademarked phrases or other sellers' work); keep prompts in the bundle's `PROMPTS.md`; respect the monthly cap (`imagegen.py spend`); QA reviews every AI image at full size for artefacts, garbled text, extra limbs or broken shapes and rejects anything off. Without the key, painterly or photographic styles are out and the Designer draws with code. The bundle spec above applies to cut files; other formats use their own spec, written into `formats/<format>.md` the first time the format is built.

Candidate formats (the Researcher checks current demand, prices and competition before proposing one):
- Printable wall art: PDF + JPG at the standard ratios (2:3, 3:4, 4:5, 11×14, ISO A-series), 300 DPI, largest size at least 24×36 in
- Clipart / PNG element sets: transparent PNG, 300 DPI, longest side at least 3600 px, plus SVG where it helps
- Sublimation and tumbler wraps: PNG at 300 DPI in the standard blank sizes (e.g. 20 oz skinny tumbler)
- Digital papers / seamless patterns: 12×12 in, 3600 px JPG, tiles seamlessly (test by tiling 2×2)
- Printable and Print-Then-Cut sticker sheets: PDF sheets + PNG; Cricut Print Then Cut max printable area 6.75×9.25 in
- Coloring pages: PDF in US Letter and A4, clean closed line art
- Printable planners, trackers, gift tags, cards, party printables: PDF, US Letter and A4
- Laser-cut files: SVG/DXF with laser-specific notes (material thickness, kerf), possibly layered/multi-piece
- Machine embroidery files (PES/DST via pyembroidery) only after a test stitch-out plan exists; otherwise skip
- Not possible here: Canva templates (need the owner's Canva account), Procreate brushes, fonts that need hand-tuned kerning. Product mockups (a design shown on a mug, shirt or wall) are fine with AI images; photos of real physical products are not.

Rules for a new format:
- The Researcher adds it to `queue.md` with a `[format]` tag and evidence (proven sellers, price range, competition).
- The first listing in a new format is a pilot: the Designer writes `formats/<format>.md` (files, sizes, checks, listing images), QA checks against it, and the Lister lists it. Build more of that format only after the pilot is listed and passes QA.
- Look up the right Etsy category with `python3 tools/etsy.py taxonomy <word>` and put its `taxonomy_id` in `listing.json`.
- Disclosure line for non-cut-file formats: "Designed with the help of digital and AI tools, and checked by hand."
- Once at least one other format is validated, keep at least 1 in 3 unchecked queue items in formats other than cut files, chosen by demand.

## New businesses (Scout + Launcher)
Owner's limits for every new business:
- Startup cost ≤ $100 in total (fees, subscriptions, samples, initial ads).
- No physical inventory the owner stores, packs or ships (platform-fulfilled print-on-demand is fine).
- Nothing that needs a business license, permits, or regulated claims (health, finance, legal).
- Must be producible by AI workers and allowed under the platform's current AI-content rules.

**Scout:** Look beyond design marketplaces: owned websites (niche content, tools, directories), software (micro-SaaS, extensions, plugins, templates, APIs, apps), other template/asset marketplaces, newsletters and other audience businesses, data products, and affiliate programs that fit the audience. Check each platform's current rules on AI content, automation and bots (e.g. Google's scaled-content-abuse policy, YouTube's mass-produced-content policy, affiliate program terms). Exclude anything that relies on deception, fake engagement, spam, or scraping against terms, and call out "passive income" ideas that commonly fail or get penalized. Use web search with primary sources (platform fee and policy pages) for facts; label blog-sourced or estimated figures as such. Score candidates 1–5 on profit at 6 and 12 months, startup cost, owner hours, automation fit, platform/policy risk, and reuse of existing factory assets. Use real Etsy results from `stats/listings.csv` once they exist: proven themes and formats outrank guesses.

**Venture gate:** the Launcher stays locked until the Etsy shop has $300 in revenue OR 30 days since the first listing went live, whichever comes first. Track it in `office/status.json` → `venture_gate`.

**Launcher:** once the gate is met, build `ventures/NN-slug/` for the Scout's #1 pick:
- The first products, finished and ready to upload, to the same quality bar as the Etsy bundles
- Listing copy, pricing, and the AI disclosure the platform requires
- `LAUNCH.md`: the owner's one-time steps (account, ID, bank, API key), numbered, under 30 minutes in total, with exactly which values to add to the environment settings
- An upload script for the platform's API where one exists, so later products can be listed automatically
- A production section to add to this manual, so the hourly team can keep producing for the new business

The Launcher never creates accounts, signs agreements, spends money, or contacts anyone. It marks itself `blocked` with "Waiting for you: follow ventures/NN-slug/LAUNCH.md" until the owner's steps are done. Only one new business is in progress at a time.

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
  "venture_gate": {"revenue_target_usd": 300, "days_live_target": 30, "first_listing_live_at": null, "met": false, "next_pick": "Scout's #1"},
  "workers": [
    {"id": "manager|researcher|designer|qa|lister|analyst|scout|launcher", "name": "Manager", "state": "working|idle|blocked", "task": "one plain sentence", "since": "ISO-8601 UTC"}
  ],
  "queue": ["next 5 theme names"],
  "feed": [{"t": "ISO-8601 UTC", "who": "designer", "msg": "one plain sentence"}]
}
```
`feed` is newest first, capped at 30 entries. Keep the numbers current every shift: `listings_live` = active listings, `uploads_pending` = approved bundles without `etsy_listing_id`, `bundles_built` = folders in `bundles/` (excluding `_rejected`), `revenue_usd` = total from `stats/listings.csv` (run `etsy.py stats` if older than 24 h), and set `venture_gate.first_listing_live_at` the first time a listing goes live. The owner's dashboard reads this file every 2 minutes; if it is invalid JSON the dashboard freezes, so validate it with `python3 -m json.tool` before committing. Use `blocked` only when a worker can't proceed without the owner (e.g. Lister and Analyst while the Etsy variables are missing), and say what's needed in `task`.

## Getting the owner's input
When a decision or a blocker needs the owner, the Manager sends one push notification (PushNotification tool):
- One line, under 200 characters, starting with "Duskwood:". Say what's needed, the deadline, and the default if there's no answer, e.g. "Duskwood: gingerbread letters A–Z or drop? Answer by 05:56 UTC or the Designer builds village silhouettes."
- Only for decisions and blockers. Never for routine shift results.
- Send it once per question, and once more if it's still open 12 h later. Log each one in `log/ACTION-LOG.md`.
- Every question has a deadline and a default, so work never stalls waiting for an answer.
- Quiet hours: push notifications only between 8:00am and 8:00pm US Eastern (America/New_York). Night shifts (8pm–8am) never notify: they log the question as "HELD for 8am: <question; deadline; default>" and the first shift after 8am sends any held questions together in one notification. If a deadline falls in quiet hours, move it to 10:00am Eastern.

## Each run ends with
Tick finished themes in `queue.md`, append to `log/ACTION-LOG.md`, update `office/status.json`, commit, `git push -u origin shop-factory` (retry up to 4 times on network errors; never force-push).

## Rules
- Original work only. No copyrighted characters, logos, brand names, trademarked phrases, or other sellers' designs. Avoid "Creepmas".
- No weapons, hate content, medical claims, or adult content.
- Pricing: $4.00 per 6-design bundle until stats exist; after that, match the median of the shop's converting listings.
- At most 2 new listings per day (avoid looking like a bulk-AI shop).
  - Temporary (owner, 1 Oct): up to 4 a day until the backlog of approved, unlisted bundles is cleared (`uploads_pending` reaches 0). Then the limit goes back to 2 and this line is removed.
- New listings are published immediately (owner's choice, 1 Oct). `ETSY_PUBLISH=0` in the environment switches back to drafts. Bundle 003 (listing 4586729007) was uploaded as a draft for the owner to review and publish by hand; don't publish it. If publishing fails (e.g. shop billing not set up), mark the Lister blocked with Etsy's message.
- Optimization, once listings have data:
  - Below 0.5% conversion after 200 views → rewrite title, tags and thumbnail once; if still below after another 200 views, deactivate.
  - Above 3% conversion → move similar themes to the top of `queue.md`.
  - Every 2 weeks: change the title or thumbnail on the 3 listings with the most views and the lowest conversion, and log the before/after.
- Weekly (first run on Monday after 12:00 UTC): write `reports/YYYY-MM-DD.md` with listings created, revenue, top listing with metrics, and the next 3 actions.
