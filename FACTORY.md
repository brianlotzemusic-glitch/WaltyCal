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
The **Manager** runs 5 shifts a day: **6:12am, 9:12am, 12:12pm, 3:12pm and 9:12pm Eastern** (owner, 4 Oct 2026, to cut usage; routine "Shop factory: shifts"). The watchdog checks at 10:40am and 4:40pm Eastern. Each shift does everything that's due, then stops. The Manager decides which specialists are due, runs each one as a separate subagent (Agent tool) with a focused brief, and records the results. Specialists never run on their own schedule.

| Worker | Job | Due when |
|---|---|---|
| Manager | Reads state, assigns work, updates `office/status.json`, writes the weekly report (Mondays) | Every run |
| Researcher | Web-searches Etsy trends and seasonal timing across **all digital product types** (see "Product formats"); reorders `queue.md`; adds themes when fewer than 8 remain; proposes new formats | Last research older than 24 h |
| Designer | Builds ONE bundle from the top unchecked theme (spec below) | Every shift, if fewer than 4 products were built today (Eastern) and the last one is QA-approved or rejected. That's up to 5 shifts, so 4 a day is reachable. |
| QA | Independent review of the Designer's bundle: looks at the contact sheet, runs the checks, sends it back to the Designer with specific fixes or approves it. Max 2 rounds; a bundle that still fails is moved to `bundles/_rejected/` and not listed | Right after the Designer |
| Lister | Uploads approved bundles that have no `etsy_listing_id` (`python3 tools/etsy.py upload bundles/NNN-slug`) | Etsy variables set and fewer than 4 uploads today |
| Analyst | `python3 tools/etsy.py stats`, then applies the optimization rules | Etsy variables set and stats older than 24 h |
| Scout | Researches which business to open next (see "New businesses"); writes `ventures/research/YYYY-MM-DD.md` and re-ranks `ventures/shortlist.md` | Last research older than 7 days |
| Launcher | Builds a launch kit for the Scout's #1 pick (see "New businesses") | Venture gate met, and no kit in progress or the last kit's owner steps are done |
| Trend Hunter | Scans what is going viral right now and writes candidates to `trends/` (see "Trend desk") | Twice a day: the 6am and 3pm shifts |
| Trend Judge | Screens the Hunter's candidates for IP risk, buyer demand and lifespan; puts approved ones at the top of `queue.md` as `[trend]` | Right after the Trend Hunter |

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
Cut files are the core, but the shop can sell any digital download the factory can produce to a sellable standard with code (vector drawing, rendering, PDF generation). AI images: when `RECRAFT_API_KEY` (preferred) or `OPENAI_API_KEY` is set, the Designer uses `tools/imagegen.py`. With Recraft, `vector` makes true SVG art directly (best for cut files: no tracing needed, but still run the cut-file checks) and `gen` makes raster art; `removebg`, `upscale` and `vectorize` are available. `gen` makes a PNG (use `--transparent` for clipart and stickers); `trace` turns black-on-white artwork into a single-path SVG for cut files, which must then pass the normal cut-file checks (prompt for bold black silhouettes on plain white, no gradients). Rules: prompts describe original designs only (never artist names, brands, characters, trademarked phrases or other sellers' work); keep prompts in the bundle's `PROMPTS.md`; respect the monthly budget (`imagegen.py spend`, default $5, owner can set `IMAGE_MONTHLY_BUDGET_USD`); QA reviews every AI image at full size for artefacts, garbled text, extra limbs or broken shapes and rejects anything off. Without the key, painterly or photographic styles are out and the Designer draws with code. The bundle spec above applies to cut files; other formats use their own spec, written into `formats/<format>.md` the first time the format is built.

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

## Art quality (all products)
The owner judged the code-drawn art too basic. When an image key (`RECRAFT_API_KEY` or `OPENAI_API_KEY`) is set, AI images are the default art source for every new product; code-drawn geometry is only for patterns that are naturally geometric (cross-stitch grids, bingo layouts, borders).
- **Style bible**: keep `shop-profile/STYLE.md` with the Duskwood look written as a reusable prompt block (palette, line weight, level of detail, mood, what to avoid). Every image prompt starts from it, so the shop looks like one brand.
- **Cheap art recipe** (owner's rule, 3 Oct 2026: "it needs to be cheaper to create content"). A test on the luna moth prompt showed flash and standard images close to pro quality (`log/` 3 Oct). Per design:
  1. Drafts: `gen --flash --n 4` ($0.028). If one is good, it is the final.
  2. Otherwise one standard `gen` from the best draft's prompt ($0.035). No more re-rolls; draw it in code or drop the idea.
  3. Print size: `upscale` ($0.004, 4x, about 4096 px) for mugs, tees and wall art; `vectorize` ($0.01) when the art is flat enough to need any size. Cut files: `trace` (free) on a black-on-white flash image, or one `vector` ($0.08) only if tracing fails.
  4. Reuse: one approved motif should feed several products (cut-file bundle, mug, tee, sticker) before a new one is made.
  Target **≤ $0.05 per design** (about 100 a month inside the cap). `--pro` is refused unless `IMAGE_ALLOW_PRO=1`, which only the owner sets.
- **Monthly AI cap: $5** (owner's choice, 3 Oct 2026; the tool's default, `IMAGE_MONTHLY_BUDGET_USD` overrides). Check `imagegen.py spend` before starting. When the month's cap is reached, or Recraft reports `not_enough_credits`, the Designer draws in code for the rest of the month; it does not ask for a top-up again. Topping up Recraft is the owner's call.
- **October 2026 one-time top-up** (owner, 3 Oct). `log/image-budget.json` has `"2026-10": "credits"`, so this month the prepaid Recraft balance is the limit instead of $5. `imagegen.py` checks the balance before every call and stops when it runs out. This is the only top-up for October: when it runs out, draw in code until 1 Nov and don't ask again. Make the credits last: use the cheap recipe only, spend them first on trend items, POD art and lead photos, and never on refreshing old listings this month. From November the $5 cap applies again unless the owner says otherwise.
- **Cut files**: prompt for "bold black silhouette on pure white, no shading, no gradients, thick connected shapes", then `imagegen.py trace`, then the normal cut-file checks. Reject any trace that loses detail or breaks into islands.
- **Resolution**: standard Recraft images are about 1 MP (e.g. 896×1152), too small for print. For anything printed (POD, wall art, clipart, stickers) use the cheap art recipe above: a flash or standard image, then `upscale` or `vectorize` to reach the placeholder or 300 DPI size; vectors scale freely.
- **Print / POD / clipart**: generate at the largest size, upscale cleanly if needed, and check at 100% zoom for artefacts, garbled text, extra fingers or legs, smudged edges and stray marks.
- **Listing photos**: the first photo must show the product in use: an AI lifestyle mockup (the ornament hanging on a tree, the decal on a mug, the print framed on a wall, the shirt worn flat-lay). The remaining photos keep the "what's included", formats and colour-ideas images.
- **Refresh old listings**: once AI art is available, and only while the month's AI cap has room after new products, the Designer remakes the weakest existing bundles (lowest views per day) with AI art and lifestyle mockups, at most one per day, and the Lister updates them with `etsy.py update` plus new images.
- QA's bar: "Would this stop a scroller on Etsy's search page next to the top 10 results for its keyword?" If not, it goes back.

## Print on demand (mugs, tees and more, via Printify)
Physical products listed on the same Etsy shop. Printify prints and ships each order; Printify charges the owner's card the base cost + shipping when an order arrives, and Etsy pays the owner the retail price. Tool: `tools/printify.py` (needs `PRINTIFY_API_TOKEN`). Connected 3 Oct 2026: Printify shop id 29175603 ("My Etsy Store", sales channel etsy); ignore the disconnected shop 9174258. Owner set orders to go to production automatically after 1 hour, order routing on (exact matches only), card on file, and Etsy production partner "Printify" created.
- **Products**: start with the 11 oz mug (blueprint 68) and a unisex tee (blueprint 12, Bella+Canvas 3001). Add others (15 oz mug, tote, sticker, sweatshirt, poster) only after the first ones sell. Pick print providers in the US with good ratings; record the choice in `pod/PROVIDERS.md`.
- **Artwork**: one design per product, PNG at the provider's placeholder size from `printify.py variants` (300 DPI), transparent background for tees. Sources: the factory's own vector designs recoloured for print (available now), or AI images from `tools/imagegen.py` (Recraft). Same originality rules as everything else. No text slogans until the Researcher has checked the phrase against USPTO trademarks; no brand, film, band, sports-team or character references, ever.
- **Tee colours**: dark designs only on light shirts and light designs on dark shirts; enable at most 4 colours and sizes S–3XL.
- **Folder**: `pod/NNN-slug/` with `product.json` (see `printify.py` docstring), the art files, `PROMPTS.md` if AI was used, and the mockup URLs Printify returns. QA checks the mockups (placement, crop, contrast, resolution) before publishing. The Lister sets the lifestyle mockup as the first Etsy photo itself after publishing (`printify.py etsy-id`, then `etsy.py lead-photos`; see formats/pod.md). No owner step.
- **Pricing**: after `create`, read the product's variant `cost` from Printify and set retail so profit after Etsy fees (≈10% + $0.20) is at least $6 on a mug and $8 on a tee, rounded to .99; check that the price is within the range of comparable Etsy listings.
- **Listing copy**: same 13-tag and title rules; the description says it is printed and shipped by our production partner, lists material, size and care, and gives production + shipping times. Disclosure line: "Designed with the help of digital and AI tools, and checked by hand." (or the plain "Designed by Duskwood Designs Co" if no AI was used for that design).
- **Etsy rules**: listings must be "Designed by" the seller with Printify as the production partner. The owner creates a production partner named "Printify" in Etsy once; Printify then assigns it automatically.
- **Volume**: POD listings count toward the daily listing cap. Pilot = 2 mugs + 2 tees using the strongest existing designs; scale only after the first sale or 2 weeks of views data.
- **Orders and buyers**: fulfilment is automatic. Buyer messages (shipping questions, damage) go to the owner through Etsy; the Manager keeps `pod/SAVED-REPLIES.md` up to date for those. Misprints/damage are reported to Printify support for a free reprint; note any such case in the log.

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
- A production section to add to this manual, so the team can keep producing for the new business

The Launcher never creates accounts, signs agreements, spends money, or contacts anyone. It marks itself `blocked` with "Waiting for you: follow ventures/NN-slug/LAUNCH.md" until the owner's steps are done. Only one new business is in progress at a time.

## Owner's dashboard (pixel office)
The owner watches https://claude.ai/artifact/YLmsuTYzib9cGUaL4b9QWe. The page is `office/floor/index.html` and it reads `status.json` published alongside it (it polls every 30 s). It does NOT read GitHub, so the Manager must publish to it.
- Publish with the Artifact tool: `url` = the link above, `file_path` = `office/floor/index.html`, `files` = `{"status.json": "office/status.json"}`. If the publish is refused because this session hasn't read the artifact, read it once (`action: "read"`, same url) and publish again.
- Publish at the **start of every shift** (Manager "working", task = what it's checking), **when each specialist starts** (that worker "working" with a one-line task, e.g. "Drawing 4 fox designs for the mug pilot"), **when each specialist finishes** (feed entry + state), and at the **end of the shift**. Several publishes per shift is expected; the page animates every change (walking to desks, carrying finished work to QA and the Etsy door).
- Feed messages drive the animations, so use plain verbs: "Built…/Sent to QA", "Approved…", "Sent … back", "Published…/Listed…".
- Don't edit `office/floor/index.html` unless the owner asks for a dashboard change.

## office/status.json
Rewrite it at the end of every run (and after each specialist finishes, if the run is long). Keep this shape:
```json
{
  "updated_at": "ISO-8601 UTC",
  "next_run_at": "ISO-8601 UTC, the next scheduled shift (6:12am, 9:12am, 12:12pm, 3:12pm or 9:12pm Eastern); the dashboard uses it to tell a quiet gap from a stopped factory",
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

## Changing the schedule
Shifts run from routines (the "Shop factory: shifts" routine, plus the watchdog). Before switching to a new or changed shift routine:
- Fire it once by hand and confirm the run pushed a commit to `shop-factory`. Keep the old routine enabled until then.
- Never leave zero shift routines enabled. If a new routine fails, turn the old one back on before anything else.
- Shift routines need the WaltyCal repo attached on the `shop-factory` branch. Fresh sessions also need the owner's permission rules for the factory's own commands (Etsy upload, update, publish and stats; image generation; pushing `shop-factory`), or they stop at those steps. Only the owner adds or changes permission rules.

## Each run ends with
Tick finished themes in `queue.md`, append to `log/ACTION-LOG.md`, update `office/status.json`, commit, `git push -u origin shop-factory` (retry up to 4 times on network errors; never force-push).

## Keeping costs low (owner's standing order, 3 Oct 2026: "make sure the Manager keeps costs low")
The shop has no revenue yet, so every dollar counts. The Manager enforces these limits on every shift and never raises them without the owner's OK:
- **Etsy listing fees**: at most 4 new listings a day ($0.80). Fixing titles, tags, photos and descriptions is free, so prefer improving an existing listing over adding a weak new one. Don't relist, renew early or create duplicate listings.
- **AI art**: the cheap recipe only (flash drafts, at most one standard final, no `--pro`), at most $0.05 per design, and reuse one motif across several products. Check `imagegen.py spend` before each Designer run. The limit is the Recraft balance in October and $5 a month after that.
- **No new paid anything** without asking the owner first: no Etsy Ads (not before 40 listings, and only with the owner's yes), no Etsy Plus, no Printify Premium, no paid tools, subscriptions, samples or test orders.
- **Print on demand**: never place orders; Printify only charges when a customer buys. Keep the profit floor at ≥ $6 per mug and ≥ $8 per tee after Etsy fees, so a sale can never lose money.
- **Cloud usage (the factory's own running cost)**:
  - On a shift where nothing is due, only refresh `office/status.json` and stop. Don't do research or reading "while waiting".
  - Keep subagent briefs short, and give each one only the files it needs.
  - Run each specialist at most as often as its "Due when" says.
  - Don't re-read large files (dashboard HTML, past research) unless the task needs them.
- **Weekly cost line**: the Monday report and the 10 Oct report list the week's listing fees, Recraft spend and the Recraft balance.

## Trend desk (Trend Hunter + Trend Judge)
The owner's request (3 Oct 2026): a dedicated team chasing current viral trends to make things people buy right now.

**Trend Hunter** (6am and 3pm shifts). Find what is taking off this week, not what sold last year.
**TikTok comes first** (owner, 3 Oct 2026: "whatever is becoming viral on TikTok needs to be made"). Every scan starts with TikTok, and at least 2 of each scan's 3 picks for the Judge must come from TikTok.
- The cloud can't read TikTok directly: the Creative Center's data needs a login, and its pages fail behind the proxy. So find TikTok trends through web search, every scan:
  - "viral on TikTok this week"
  - "TikTok trends this week"
  - "TikTok trending hashtags" and "trending sounds" roundups, which marketing blogs and newsletters publish weekly from the Creative Center
  - "#TikTokMadeMeBuyIt"
  - "TikTok shirt", "TikTok mug" and "TikTok phrase"
  - news stories about a phrase, sound or aesthetic going viral

  Note the date of every source and ignore anything older than 10 days. A trend counts only if there's evidence it is rising now: a recent date, a growing video count, or several sources in the same week.
- Look especially for the things that turn into products:
  - catchphrases and slang people repeat
  - aesthetics ("___core", "___ girl autumn")
  - in-jokes for a hobby or job
  - seasonal TikTok moments
- Other sources, after TikTok:
  - Google Trends daily RSS: `curl -s "https://trends.google.com/trending/rss?geo=US"`, which is reachable from the cloud. Use it to confirm a TikTok trend is spreading to search.
  - Pinterest, Reddit and X, through web search.
  - Etsy's "trending now" and the editors' picks shown in search results.
  - Viral phrases, sounds and memes from the last 7 days.
  - Upcoming dates in the next 6 weeks: holidays, awareness days, big releases and seasonal moments.
- For each candidate, write to `trends/YYYY-MM-DD-HH.md`:
  - what it is
  - evidence it is rising, with links and dates
  - who would buy it
  - the product idea: phrase or graphic tee/mug, cut file, printable or sticker sheet
  - the number of Etsy listings already matching it
  - how long it is likely to last
- Aim for 5–10 candidates per scan, and add at most 3 to the Judge's list each time.

**Trend Judge** (right after the Hunter). Reject anything that fails any of these:
- **IP**: no brand, show, film, game, song lyric, sports team, celebrity name or likeness, or a meme built on someone's copyrighted image. Search "<phrase> trademark" before approving a catchphrase, and reject it if it is registered or pending. Etsy removes these listings and they can close the shop.
- **Taste**: nothing about tragedies, real crimes, politics or mocking real people.
- **Lifespan**: it must still be selling at least 2 weeks from now. Print-on-demand needs 2–5 days to make plus shipping, so a 3-day meme is already dead by delivery.
- **Demand**: there must be real buyer intent, not just views, such as people asking "where can I get this shirt" or a rising Etsy search. Skip it if Etsy already has more than about 5,000 matching listings, unless we have a clear angle.
- **Makeable this week**: within the current AI art budget (code-drawn typography and simple graphics are fine, and cost nothing).
- Approved trends go to the top of `queue.md` as `- [ ] [trend] <idea> (expires YYYY-MM-DD; evidence: ...)`. Remove expired `[trend]` items unbuilt, and log the rejections with reasons in the same `trends/` file.

**Fast lane**: a `[trend]` item takes the first of the day's 4 listing slots (up to 2 slots if there are 2 approved trends), and the Designer builds it before anything else. The best formats are a print-on-demand tee or mug (phrase or simple graphic) plus a matching SVG cut file of the same design, which counts as 2 listings. The Analyst tags trend listings in `stats/` so the 10 Oct report shows whether trends beat evergreen themes.

## Turnaround week (4–10 Oct 2026, owner's deadline)
The owner will shut the factory down unless the shop shows signs of life by 10 Oct. The owner's cost concerns are Recraft and Etsy listing fees, so:
- **Spending limit for the week: $5.60 of Etsy listing fees** (4 new listings/day × $0.20, owner raised it from 2 on 3 Oct). Don't go above 4 a day. Edits to existing listings are free, so use them freely.
- **Recraft**: October runs on the one-time prepaid top-up (see "October 2026 one-time top-up" above). Cheap recipe only; when the balance runs out, draw in code until 1 Nov. Don't ask the owner for a top-up.
- **Day 1 (4 Oct), Lister, free**: retitle and retag all 8 live cut-file listings with `etsy.py update`. Lead each title with the highest-volume plain search phrase (e.g. "Christmas SVG Bundle", "Snowflake SVG", "Christmas Ornament SVG", "Bat SVG"). Put "gothic", "spooky" and "creepy" later in the title and in the tags, not first. Use all 13 tags, mixing broad terms (christmas svg, cricut files, ornament svg) with specific ones. Keep the disclosure line. Log the before and after titles.
- **New listings in this order**: the 4 POD products (all on the 4th), then Botanical frost snowflakes (cut files), Woodland Christmas bingo (printable) and the Woodland Christmas mini cross-stitch charts. Pick only proven-demand items; nothing speculative this week.
- **Analyst**: every day at the first shift after 8am ET, push the owner one line: total views, favourites and sales, and the change since yesterday.
- **No Etsy Ads yet** (owner, 3 Oct 2026: "no ads till we build a decent library of items"). Never turn on or suggest paid ads before then. When the shop reaches **40 live listings**, the Manager asks the owner once whether to start Etsy Ads at $1/day.
- **10 Oct check**: write `reports/2026-10-10-turnaround.md` with the week's views, favourites, sales and spend. Targets: ≥100 views and ≥5 favourites. Recommend honestly whether to continue. If there are under 20 views, recommend shutting down or pausing.

## Teachers Pay Teachers (owner's music store, added 4 Oct 2026)
The owner also sells on TpT: https://www.teacherspayteachers.com/store/brian-lotze. As of 4 Oct it holds 4 high-school digital music production items built around Logic Pro ($0–$10, 3 followers). The owner's decisions (4 Oct):
- **A new classroom music line**, K-2, 3-5, 6-8 and high school. These are separate products; overlapping the owner's curriculum is fine.
- **Brand: "Hudson Beat"** (owner's choice, 4 Oct 2026). Covers and title pages say HUDSON BEAT, and the TpT seller stays Brian Lotze. **Match the owner's store** style, not Duskwood. Before the first build, the Designer looks at the store's thumbnails and covers, then writes the look into `tpt/STYLE.md` (fonts, colours, layout, cover format).
- **Uploading** (owner, 4 Oct 2026: automate it). TpT has no seller API, so `tools/tpt.js` drives the TpT website with Playwright, logged in as the owner's VA account. It **runs on the owner's Mac** (setup in `tpt/LOCAL-SETUP.md`): cloud sessions can't open TpT in a browser because of the proxy certificate, and weakening TLS isn't allowed. The factory never runs it from the cloud. `publish` (owner approved, 4 Oct 2026) uploads an item live from its UPLOAD.md + `tpt.json` (see tpt/README.md); run `--dry-run` first on a new item. **Nightly publishing, under the Manager** (owner, 4 Oct 2026: "help me set that up... all under your purview"). A launchd job on the owner's Mac (`tools/tpt-nightly.sh`, installed by `tools/tpt-install-nightly.sh`) runs `node tools/tpt.js publish-pending` every evening. It publishes **only items the Manager has released**: at most 3 a night, never while `tpt/PAUSED` exists. It commits `uploaded` markers and `tpt/UPLOADER-STATUS.json`. Each Manager shift:
  - **Release.** For each `tpt/NNN-slug/` that has a QA `**Verdict: APPROVED**`, a `tpt.json` and no `uploaded`, run these checks:
    - title ≤80 chars
    - price and license_price set
    - tax_code set
    - 1–4 grades, 1–3 subjects, 1–6 tags
    - every file in `files` exists

    If they all pass, write `release` containing the date and "released by Manager". If any fails, send the item back to the Designer. Release at most 3 a day.
  - **Check the last run** in `tpt/UPLOADER-STATUS.json`:
    - `needs_login`: push the owner once (8am–8pm ET): "TpT login expired: on your Mac run `source ~/.tpt-env && node tools/tpt.js login` and click Log in."
    - `failed` items: read the error. If it's an item problem, the Designer fixes the item. If the same item fails twice, or a failure suggests TpT's form changed, create `tpt/PAUSED` (commit it) and push the owner once with the reason.
    - Released items waiting and `ran_at` older than 36 h: push once, "the nightly TpT job hasn't run: is the Mac on and logged in?"
  - **Verify.** For each newly `uploaded` item, check its public TpT URL returns 200. Add it to the log, the dashboard feed and `tpt/README.md`'s list.
  - **Unpause.** Delete `tpt/PAUSED` only after the cause is fixed, or when the owner says so. For each item the factory builds `tpt/NNN-slug/` containing:
  - the resource PDF and a 4-page preview PDF
  - a square cover/thumbnail and 3 preview images
  - `UPLOAD.md`, laid out in the order of TpT's upload form, with title (≤80 chars), description, grades, subjects, resource type, standards if any, price, and a "free or paid" note, ready to paste
- **Batching**: when 2–3 TpT items are approved, the Manager sends one push ("2 TpT items ready, ~15 min to upload: tpt/…"), at most twice a week and only between 8am and 8pm ET. The owner replies "uploaded", and the Manager records it in `tpt/NNN-slug/uploaded`.
- **Researcher**: once a week, look at proven TpT music sellers (best-seller and "most popular" lists, review counts, seasonal demand: Halloween, Thanksgiving, winter/holiday concerts, Music In Our Schools Month in March, end of year, sub plans). Add items to `queue.md` tagged `[tpt]` with grade, type, a typical price and evidence. Take the subject and format only; never copy another seller's resource.
- **Designer**: every TpT item also gets a `tpt.json` (format in `tpt/README.md`; see `tpt/001-halloween-color-by-note/tpt.json`; tax_code "Other Digital Goods", license_price = price unless the owner says otherwise, at most 4 grades). Build `[tpt]` items like any other product, drawn in code at no image cost (notation, rhythm cards, bingo, worksheets, posters, colour-by-note). They take turns with Etsy builds, about 1 in 3 Designer runs. Use music21, LilyPond or hand-drawn SVG for notation.
- **QA**, in addition to the usual checks:
  - **Musical accuracy**: note values add up to each bar's time signature, stems and beams are correct, notes sit on the right staff positions, the clef is right, and the rhythm syllables match the notes.
  - **Age-appropriateness**, and answer keys that are correct.
- **Rules**:
  - No copyrighted songs, lyrics or arrangements; public-domain folk songs and composers are fine.
  - "Logic Pro" and other product names only to describe compatibility.
  - The disclosure line goes in the description: "Designed with the help of digital and AI tools, and checked by hand."
- **Money**: no TpT fees are paid by the factory. Basic seller keeps 55% minus $0.30 per resource; Premium costs $59.95/yr, and only the owner decides on it.

## Rules
- Original work only. No copyrighted characters, logos, brand names, trademarked phrases, or other sellers' designs. Avoid "Creepmas".
- No weapons, hate content, medical claims, or adult content.
- Pricing: $4.00 per 6-design bundle until stats exist; after that, match the median of the shop's converting listings.
- At most 4 new listings per day (owner, 3 Oct 2026; was 2). Quality bar unchanged: QA still approves every one, and listings spread across the day rather than going out in one burst.
- New listings are published immediately (owner's choice, 1 Oct). `ETSY_PUBLISH=0` in the environment switches back to drafts. Bundle 003 (listing 4586729007) was uploaded as a draft for the owner to review and publish by hand; don't publish it. If publishing fails (e.g. shop billing not set up), mark the Lister blocked with Etsy's message.
- Optimization, once listings have data:
  - Below 0.5% conversion after 200 views → rewrite title, tags and thumbnail once; if still below after another 200 views, deactivate.
  - Above 3% conversion → move similar themes to the top of `queue.md`.
  - Every 2 weeks: change the title or thumbnail on the 3 listings with the most views and the lowest conversion, and log the before/after.
- Weekly (first run on Monday after 12:00 UTC): write `reports/YYYY-MM-DD.md` with listings created, revenue, top listing with metrics, and the next 3 actions.
