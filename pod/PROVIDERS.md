# Print providers (Printify), chosen 3 Oct 2026

Printify's API returns provider names and locations but **not ratings**, so the ratings below come from Printify's catalogue reputation and need confirming in the Printify UI (catalogue → product → provider list shows score, production time and price). Costs are the real variant costs Printify returned after `create` (no Printify Premium).

| Product | Blueprint | Provider (id) | Location | Why | Base cost | US shipping (1st / each extra) |
|---|---|---|---|---|---|---|
| 11 oz mug | 68 "Mug 11oz" | SPOKE Custom Products (1) | Norcross, GA, US | The only provider Printify offers for blueprint 68; US-based, sublimation full wrap 2700x1120 px | $6.44 | $6.69 / $2.99 |
| Unisex tee | 12 Bella+Canvas 3001 | Monster Digital (29) | Miami, FL, US | Long-standing, well-rated US DTG provider on Printify; largest print area of the US options (4500x5100 px = 15x17 in for M–3XL); full colour range incl. Black, Dark Grey Heather, Navy, Asphalt, White, Natural, Soft Cream, Ash | S–XL $11.77, 2XL $14.38, 3XL $16.77 | $4.49 / $2.09 |

Other US tee providers checked (blueprint 12): SwiftPOD (39, San Jose CA, 3692x4800 front + sleeves), Printify Choice (99, Miami FL, 3951x4800, shipping $3.99), Dimona Tee (61, FL), Stakes Manufacturing (52, OH), Stacked Commerce (103, PA), Underground Threads (50, TX), Fulfill Engine (217, NC), Printful (410, NC). Non-US providers (CZ, CA, AU, GB) were skipped. Printify returns base costs only for products that exist, so SwiftPOD and Printify Choice costs were not compared; one of them may be cheaper than Monster Digital. **Worth checking in the Printify UI before scaling tees.**

Handling time reported by the API: up to 10 days for all three (a maximum, not typical). The listings say "usually 2–5 business days" for production, matching `SAVED-REPLIES.md`.

## Pricing (Etsy fees ≈ 10% + $0.20 of the item price; rule: profit ≥ $6 mug, ≥ $8 tee; .99 endings)
| Product | Retail | Cost | Fees | Profit |
|---|---|---|---|---|
| Mug (both) | $16.99 | $6.44 | $1.90 | **$8.65** (rule minimum would be $13.99; $16.99 sits inside the comparable range) |
| Tee S–XL | $27.99 | $11.77 | $3.00 | **$13.22** |
| Tee 2XL | $27.99 | $14.38 | $3.00 | **$10.61** |
| Tee 3XL | $27.99 | $16.77 | $3.00 | **$8.22** (the size that sets the price) |

- Buyers pay shipping at Printify's rates (Printify sends its shipping profile when it publishes). Etsy's fees also apply to the shipping charge, so real profit is a few cents lower than shown.
- `printify.py` sets one price for every variant. A per-size price would be more competitive: S–XL $24.99 ($10.52), 2XL $26.99 ($9.71), 3XL $28.99 ($9.12). That needs a tool change (variant price map) or a manual edit in Printify.
- Comparable Etsy prices (estimates, checked 3 Oct 2026): 11 oz moth/cottagecore mugs about $15–21 (RankHero "cottagecore mug" median $20.77; an Etsy 11 oz luna moth mug at $15.45). Skull and gothic tees about $20–32 (RankHero "skull shirt" median $25.65, "skull t shirt" $24.99). Both prices are inside these ranges; the tees sit slightly above the median.
