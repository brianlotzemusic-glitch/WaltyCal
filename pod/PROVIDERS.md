# Print providers (Printify), chosen 3 Oct 2026

Printify's API returns provider names and locations but **not ratings**, so the ratings below come from Printify's catalogue reputation and need confirming in the Printify UI (catalogue → product → provider list shows score, production time and price). Costs are the real variant costs Printify returned after `create` (no Printify Premium).

| Product | Blueprint | Provider (id) | Location | Why | Base cost | US shipping (1st / each extra) |
|---|---|---|---|---|---|---|
| 11 oz mug | 68 "Mug 11oz" | SPOKE Custom Products (1) | Norcross, GA, US | The only provider Printify offers for blueprint 68; US-based, sublimation full wrap 2700x1120 px | $6.44 | $6.69 / $2.99 |
| Unisex tee | 12 Bella+Canvas 3001 | Monster Digital (29) | Miami, FL, US | Long-standing, well-rated US DTG provider on Printify; largest print area of the US options (4500x5100 px = 15x17 in for M–3XL); full colour range incl. Black, Dark Grey Heather, Navy, Asphalt, White, Natural, Soft Cream, Ash | S–XL $11.77, 2XL $14.38, 3XL $16.77 | $4.49 / $2.09 |

Other US tee providers checked (blueprint 12): SwiftPOD (39, San Jose CA, 3692x4800 front + sleeves), Printify Choice (99, Miami FL, 3951x4800, shipping $3.99), Dimona Tee (61, FL), Stakes Manufacturing (52, OH), Stacked Commerce (103, PA), Underground Threads (50, TX), Fulfill Engine (217, NC), Printful (410, NC). Non-US providers (CZ, CA, AU, GB) were skipped. Printify returns base costs only for products that exist, so SwiftPOD and Printify Choice costs were not compared; one of them may be cheaper than Monster Digital. **Worth checking in the Printify UI before scaling tees.**

Handling time reported by the API: up to 10 days for all three (a maximum, not typical). The listings say "usually 2–5 business days" for production, matching `SAVED-REPLIES.md`.

## Pricing (live in Printify since QA round 1)
Rule: profit ≥ $6 per mug and ≥ $8 per tee, prices ending in .99. Profit = retail − (10% of retail + $0.20) − (10% of the buyer's shipping charge, because Etsy's transaction and processing fees also apply to shipping; QA's estimate was 6.5%, and 10% is the conservative figure) − Printify cost.

| Product | Retail | Cost | Fees on item | Fees on shipping | Profit |
|---|---|---|---|---|---|
| Mug (001, 002) | $16.99 | $6.44 | $1.90 | $0.67 (of $6.69) | **$7.98** |
| Tee S–XL (003, 004) | $28.99 | $11.77 | $3.10 | $0.45 (of $4.49) | **$13.67** |
| Tee 2XL | $28.99 | $14.38 | $3.10 | $0.45 | **$11.06** |
| Tee 3XL | $28.99 | $16.77 | $3.10 | $0.45 | **$8.67** (sets the price; $27.99 would give $7.67) |

- Mug: the rule minimum is $14.99 when fees on shipping are counted. $16.99 sits inside the comparable range.
- `printify.py` sets one price for every variant. Per-size prices would be more competitive: S–XL $24.99 ($10.07), 2XL $26.99 ($9.26), 3XL $28.99 ($8.67). That needs a variant price map in product.json and `update`.
- Comparable Etsy prices (estimates, checked 3 Oct 2026): 11 oz moth/cottagecore mugs about $15–21 (RankHero "cottagecore mug" median $20.77; an Etsy 11 oz luna moth mug at $15.45). Skull and gothic tees about $20–32 (RankHero "skull shirt" median $25.65, "skull t shirt" $24.99). $28.99 is inside the range but above the median.
