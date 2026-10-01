# Proven sellers research: 2026-10-01 (Researcher)

## Summary
- **No cut-file listing is confirmed at 1,000+ sales in the last ~60 days.** One listing could plausibly be at that level: "Christmas Gingerbread Letter Ornaments with Name" (shop AnitaDesignArt). EtsyHunt estimates it at **~209 sales/week (about 1,800 per 60 days if that rate held)**, with only **1,202 total sales** since it was listed. Its "2026" title suggests a new listing, so most of those sales are probably recent. That is still an estimate. I could not confirm that it is a digital file rather than a physical ornament. Its revenue figure ($3,967 ÷ 1,202 ≈ $3.30/sale) points to digital or very cheap items.
- Every other SVG or cut-file listing that EtsyHunt shows publicly sells at an estimated **35-70 sales/week (~300-600 per 60 days)**. These are the top-10 SVG listings on all of Etsy, so the 1,000-in-60-days bar is very rarely met in this category. The listings that do reach it are physical personalised goods (makeup bags, stockings), not cut files.
- The proven **subjects** that our format can serve are: gingerbread alphabet ornaments, Christmas villages, Christmas laser-cut ornaments, soccer, witchy crystals, dragonflies, birds, nativity/Christian silhouettes, goth Valentine and highland cows. Many top sellers are huge mega bundles (400-10,000 files) or franchise bundles. We can't copy that format at $4 for 6, and we must not touch franchises.
- **Evidence strength: weak to moderate.** It all comes from one estimator (EtsyHunt) that is updated monthly. It shows weekly-sales estimates and lifetime totals, not 60-day totals, and its revenue column is often inconsistent with its sales column (e.g. 192 sales and $192 revenue for a canvas print). Etsy, Design Bundles and Creative Fabrica all returned HTTP 403, so I could not check Bestseller badges, "in carts" or "bought in last 24 h" signals.

## Method and access log
| Source | Result |
|---|---|
| etsy.com search, /market/<term>, /shop/<name> (curl + WebFetch) | **HTTP 403** every time |
| EtsyHunt public "best selling" lists (etsyhunt.com/best-etsy-<slug>), page header "Updated on 2026-10-01", ranked by weekly sales, updated monthly | **Used.** Lists found: svg, svg-files, christmas-ornaments, christmas-decorations, christmas-gifts, wall-art, metal-wall-art, wall-decals, stickers, monogram, halloween-decorations, fall-decor; plus ehunt.ai research/clip-art, research/font, etsy-competitor-research/sublimation-designs, digital-planner |
| EtsyHunt slugs that don't exist (laser-cut-files, christmas-svg, mandala-svg, snowflake-svg, svg-bundle, cricut-files, ornaments, stencils etc.) | etsyhunt.com/best-etsy-<slug> returns **404**. etsyhunt.com/research/best-etsy-<slug> **301-redirects** to ehunt.ai, which serves a "404 Page not found" page. Not blocked, just not published. The same subjects were covered by the svg / svg-files / christmas-ornaments lists |
| RankHero keyword pages | Used for search volume and competing-listing counts (third-party estimates) |
| designbundles.net bestsellers, creativefabrica.com popularity sort | **HTTP 403** |
| SoFontsy | Shop JSON reachable, but the sort order was ignored and there are no sales counts. Not usable as sales evidence |
| Silhouette Design Store home | No bestseller titles or counts visible |
| Cricut Design Space trending | Not publicly reachable (app only) |
| eRank / Alura / EverBee / Marmalead / Sale Samurai / InsightFactory | No listing-level sales figures publicly visible (account required) |
| Web search for "bought in the last 24 hours" / Bestseller snippets | Only bare etsy.com listing links with no visible signals |

All figures below are **EtsyHunt estimates** unless marked otherwise. "60-day est." = weekly × 8.6, **assuming the weekly rate held for 60 days**. Where the lifetime total is lower than that, the lifetime total is the ceiling.

## Hot listings (EtsyHunt, fetched 2026-10-01)
| # | Subject | Format | Price (rev ÷ sales) | Weekly est. | Lifetime est. | 60-day est. | Source list | Usable? |
|---|---|---|---|---|---|---|---|---|
| 1 | Gingerbread letter/name ornaments, "2026" (AnitaDesignArt) | Alphabet letter ornaments, personalised; digital vs physical unconfirmed | ~$3.30 | **209** | 1,202 | **~1,000-1,200 possible (capped by lifetime total)**. **FLAG: only candidate for 1,000+** | [christmas-ornaments](https://etsyhunt.com/best-etsy-christmas-ornaments), [christmas-gifts](https://etsyhunt.com/best-etsy-christmas-gifts) | Yes, subject + format |
| 2 | Gingerbread alphabet ornaments (TheSquidAtelier, 2 listings) | Letter ornaments, likely physical | ~$2.90 | 59 / 24 | 3,866 / 334 | ≤ ~510 / ≤ ~210 | [christmas-ornaments](https://etsyhunt.com/best-etsy-christmas-ornaments), [christmas-decorations](https://etsyhunt.com/best-etsy-christmas-decorations) | Supports #1 |
| 3 | Fall/Thanksgiving PNG | Sublimation PNG bundle | ~$1 | 189 | 660 | ≤ 660 | [svg](https://etsyhunt.com/best-etsy-svg) | No: sublimation, season over |
| 4 | Soccer SVG bundle (ball, silhouettes, monogram) | SVG bundle | ~$1.40 | 70 | 382 | ≤ ~380 | [svg](https://etsyhunt.com/best-etsy-svg) | Yes (silhouettes only) |
| 5 | Witchy crystals slogan SVG | Shirt design, text + crystals | ~$2.60 | 60 | 93 | ≤ 93 | [svg-files](https://etsyhunt.com/best-etsy-svg-files) | Partly (crystals, no text) |
| 6 | Winter/Christmas village light box | Multi-piece 3 mm/4 mm laser file | ~$8.10 | 55 | 132 | ≤ 132 | [svg-files](https://etsyhunt.com/best-etsy-svg-files) | Partly (single-layer panels) |
| 7 | Golden dragonflies clipart | Watercolour clipart | ~$4 | 53 | 122 | ≤ 122 | [clip-art](https://ehunt.ai/research/best-etsy-clip-art) | Subject only |
| 8 | Flock-of-3-birds metal wall hanging | Physical metal art | ~$40 | 47 | 75 | ≤ 75 | [metal-wall-art](https://etsyhunt.com/best-etsy-metal-wall-art) | Subject only |
| 9 | Houses clipart (black-and-white town) | Vector clipart | ~$6.50 | 46 | 86 | ≤ 86 | [clip-art](https://ehunt.ai/research/best-etsy-clip-art) | Supports village |
| 10 | Goth/horror couples Valentine | SVG cut-file bundle | ~$2.75 | 43 | 120 | ≤ 120 | [svg-files](https://etsyhunt.com/best-etsy-svg-files) | Subject only; horror-film couples skipped |
| 11 | Christian cross / crucifix | SVG/DXF plasma/laser file | ~$1.75 | 42 | 94 | ≤ 94 | [metal-wall-art](https://etsyhunt.com/best-etsy-metal-wall-art) | Subject (we adapt to nativity) |
| 12 | 730-piece Christmas laser mega bundle (ornaments, advent, nativity, gift box) | Mega bundle | ~$5.75 | 37 | 220 | ≤ 220 | [christmas-ornaments](https://etsyhunt.com/best-etsy-christmas-ornaments) | Subject only (we can't match quantity) |
| 13 | Standing gingerbread village table decoration | Laser cut file | ~$4.90 | 36 | 80 | ≤ 80 | [svg-files](https://etsyhunt.com/best-etsy-svg-files) | Supports village |
| 14 | Christmas laser cut mega bundle 400+ | Mega bundle | ~$2 | 35 | 93 | ≤ 93 | [svg-files](https://etsyhunt.com/best-etsy-svg-files) | Subject only |
| 15 | Christmas highland cow PNG (22 designs) | Sublimation clipart | ~$1.75 | 29 | 244 | ≤ 244 | [sublimation-designs](https://ehunt.ai/etsy-competitor-research/best-etsy-sublimation-designs) | Partly (silhouette) |
| 16 | Hummingbird metal garden sign | Physical | ~$30 | 22 | 3,668 | ≤ ~190 | [metal-wall-art](https://etsyhunt.com/best-etsy-metal-wall-art) | Subject only |
| 17 | Bear & deer forest metal wall art | Physical | ~$60 | 20 | 85 | ≤ 85 | [metal-wall-art](https://etsyhunt.com/best-etsy-metal-wall-art) | Subject only |
| 18 | Wildflower wall-decal border | Physical decal | — | 20 | 142 | ≤ 142 | [wall-decals](https://etsyhunt.com/best-etsy-wall-decals) | Subject only |
| 19 | Monogram SVG font bundle (6 fonts) | Font/alphabet bundle | ~$5.40 | 63 | 16,493 | ≤ ~540 | [svg](https://etsyhunt.com/best-etsy-svg) | Not as a font; letters idea folded into #1 |

**Keyword context (RankHero estimates, fetched 2026-10-01):** snowflake ornament ~5,400/mo on ~44k listings; ornament svg ~1,000/mo on ~94k; christmas ornament svg ~880/mo on ~57k (peaks Nov); laser cut ornament ~720/mo on ~53k; mandala svg ~880/mo on ~36k; angel svg ~720/mo on ~17k; nativity svg ~260/mo on ~7.4k; gingerbread alphabet ~90/mo on ~2.9k; christmas village svg (volume not shown) on only ~1.6k listings; gingerbread house svg on ~2.0k listings. URL pattern: `https://www.rankhero.com/keywords/<keyword>`.

## Themes built from this (all original designs: subject and format only)
| Theme | Evidence | Feasibility |
|---|---|---|
| Gingerbread letter ornaments | #1, #2 (strongest: ~209/wk est.) | **Feasible.** Each letter is a cookie-shaped outline with icing-scallop edges and cut-out dots ≥600 u², plus a hanging hole. A full A-Z is the proven format. For a 6-design bundle the Designer could make 6 letter-blank/initial ornaments, or the Manager could allow a larger alphabet bundle. Buyers add names themselves. No other seller's lettering style. |
| Christmas village silhouettes | #6, #9, #13; low listing count | **Partly feasible.** Proven listings are multi-piece 3D light boxes. We make single-layer skyline panels and standing house silhouettes with window cut-outs. Merged with the old "Snowy woodland village" theme. |
| Filigree Christmas ornament shapes | #12, #14; ornament/snowflake-ornament keywords | **Feasible.** Bauble, bell, star, tree and drop outlines with lace/botanical cut-outs. Keep it visually distinct from botanical frost snowflakes. |
| Soccer silhouettes | #4 | **Feasible** (player silhouettes, ball with pentagon cut-outs, goal). Off the Duskwood look; the Manager may demote it. No teams, crests or names. |
| Witchy crystals (gothic slot) | #5 | **Partly feasible.** We drop the slogan text and make crystal clusters/points. No "healing" claims. |
| Butterflies & dragonflies | #7 + keywords | **Feasible** (existing theme, moved up). |
| Nativity silhouettes | #11, #12 | **Feasible.** Classic manger/magi/star silhouettes. Religious, so a bit off-look, but proven demand and Christmas-timed. |
| Birdwatching silhouettes | #8, #16 | **Feasible** (existing theme, moved up; flocks added). |
| Gothic Valentine (gothic slot) | #10 | **Feasible** (existing theme, moved up). Original hearts/bats only. |
| Highland cow Christmas | #15 (weak) | **Partly feasible.** The proven versions are sublimation or layered. We make a one-shape silhouette with holly/wreath. |
| Woodland reindeer & stag, Spring wildflowers | #17, #18 (weak, physical) | Already queued; evidence notes added. |

## Queue changes
- 10 proven-seller themes are now at the top of the unchecked list (24 unchecked total). Ordered by evidence, with one small swap (nativity between dragonflies and birds) so that the two flying-nature sets are not neighbours.
- Merged: "Snowy woodland village" into "Christmas village silhouettes". Moved up with evidence: Butterflies & dragonflies, Birdwatching, Gothic Valentine.
- Gothic/dark slots: Witchy crystals (#5), Gothic Valentine (#9), Raven & mistletoe (#13), Haunted gingerbread (#16). That is 4 of 24 (17%), none adjacent.
- Christmas themes run from #1 to #18, so at ~2 bundles/day all are built by about Oct 10, well before mid-November.

## Skipped (not queued) and why
- **Franchise/character/brand:** Pokémon bundles (2 listings, ~40/wk each), Rapunzel/Tangled bundle (~35/wk), Stitch bundle (~66/wk), Toy Story font + PNG (~65/wk, ~52/wk), "Mouse" cartoon font (~48/wk, Disney-style), Pooh digital paper (~67/wk), Moana kit, Lord of the Rings map, The 1975 lyrics, Yayoi Kusama print, Disney "Jungle Cruise" sign, chibi superheroes, "Grich" Christmas PNG, horror-movie Ghostface tumbler, and the horror-couples angle of the goth Valentine listing.
- **Medical/health:** "Mental Health Matters" brain-and-flowers PNG (~97/wk). It is sublimation art with a health message, so it is not feasible and too close to health claims. "Healing crystal" wording dropped from the crystals theme.
- **Not feasible in our format:** sublimation/tumbler/mug wraps, fall/Halloween PNG bundles (season also over), coloring-page PLR mega bundles, 10,000-file "whole shop" bundles, text slogans ("Mama wears her heart on her sleeve", ~73/wk), fonts and embroidery fonts, monogram font bundle (letters idea folded into gingerbread letters).
- **Physical personalised goods** (makeup bags 500+/wk, stockings, neon signs, pet portraits): not our product. They are the only listings clearly above 1,000 sales per 60 days on the lists I could see.
