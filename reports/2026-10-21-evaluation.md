# Full evaluation, 21 Oct 2026 (day 20)

Asked for by the owner after Etsy Ads went on (17 Oct, $5/day) and the first TpT sale.

## Results by channel
| | Etsy (Duskwood Designs Co) | TpT (Hudson Beat) |
|---|---|---|
| Live products | 34 (1–20 days old) | 25 ($3.50–$12) |
| Traffic | 19 views in total, 2 favourites; 29 of 34 listings never viewed | not visible from the cloud (TpT has no seller API) |
| Sales | 0 | 1 (owner-reported); a basic seller keeps 55% minus $0.30 |
| What got views | Christmas Village SVG (7 views, 2 favs), Nativity SVG (7), Woodland cross-stitch (3) | (no data) |
| Ads | $5/day since 17 Oct (about $20–25 so far): views went from 12 to 19. Verdict due 24 Oct with the owner's dashboard numbers | none |

## Money out vs in (approximate)
- Out: Etsy listing fees about $7; Recraft $5 top-up; Etsy Ads about $20–25 so far ($150/month at this rate, more than everything else combined); Printify $0; TpT $0.
- In: one TpT sale (about $2–6 after TpT's cut, depending on the product).

## The factory itself
- Shifts run twice a day and push every time; the Manager rotated itself v3 → v4 on 19 Oct using the procedure in FACTORY.md.
- Claude usage, at list-price equivalent (not a bill): Manager v1 about $352 over 1–9 Oct; v2 $29/day; v3 $14/day; v4 about $7/day. That's about 4× lower since 9 Oct, at the same output.
- Quality: since 15 Oct (everything on Sonnet), QA logged about 8 rejections against 24 approvals, and the fix rounds caught them before listing. No Opus escalations logged.
- Trend desk: no approved picks in any scan so far (8+ scans). It costs usage and has produced nothing.
- Recraft: about $1.91 left for October.
- **Risk: the GitHub repo is public.** All 25 TpT kits and every Etsy file can be downloaded free from github.com/brianlotzemusic-glitch/WaltyCal (branch shop-factory).

## Assessment
- TpT is working better: it made the only sale, it plays to the owner's real expertise (music teaching, existing curriculum), its prices are 2–3× Etsy's, and its products cost $0 in AI art.
- Etsy isn't working yet: almost no listings are being shown in search. A brand-new shop with no sales or reviews gets little search placement, and gothic Christmas cut files are a crowded niche. The listings that got views use plain Christmas searches (village, nativity, cross-stitch). The Christmas buying window (November to early December) is the real test, so judge Etsy in mid-November, not now.

## Recommendations
1. **Make the repo private today** (owner: GitHub → Settings → Change visibility). The watchdog no longer depends on the repo being public.
2. **TpT bundles** from kits that already exist: DMP1 Units 1–6, DMP2 projects, and a seasonal pack, at about 20–25% off. Plus one free product as a follower magnet: TpT followers are notified of every new upload. No new design work, so cheap.
3. **TpT stats from the Mac nightly job**: it's already logged in, so it can read the seller dashboard (sales, views per product) into `stats/tpt.csv`. Then the factory knows which kit sold and can make more like it.
4. **Etsy Ads verdict on 24 Oct:** with no order and few clicks, stop the ads (or drop to $1–2/day). Keep listing through mid-November, leaning on plain Christmas themes. Replace the weak lead photos on the 5 gothic listings (free edits, about $0.02 per image).
5. **Pause the trend desk** until it produces a pick, which saves usage. The Researcher already covers seasonal demand.
