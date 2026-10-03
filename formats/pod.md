# Format spec: print-on-demand (Printify → Etsy)

First built 3 Oct 2026 (pilot: `pod/001`–`pod/004`, 2 mugs + 2 tees). Physical products: Printify prints and ships; the owner's card pays base cost + shipping per order. Read with FACTORY.md "Print on demand" and "Art quality".

## Folder: `pod/NNN-slug/`
| File | What |
|---|---|
| `product.json` | Spec for `printify.py create` (format in the `printify.py` docstring): title, description, 13 tags, blueprint, provider, `price_cents`, `variant_ids`, `placements` |
| print PNG | `mug-wrap-2700x1120.png` or `tee-front-4500x5100.png`, built by `pod/make_art.py` (deterministic, free) |
| `candidates/` | The chosen Recraft source(s) at full size (and the `-up` upscale for tees); rejected candidates as 1024 px `-preview.jpg` |
| `PROMPTS.md` | Every prompt, model, cost, which candidate was kept and why, and any manual fixes |
| `LISTING.md` | Title (≤140 chars), 13 unique tags (≤20 chars each), price, full description |
| `printify_product_id` | Written by `create`; `create` refuses to run again while it exists |
| `mockups.json` | `selected_for_publishing` (what Printify sends to Etsy) + `all_cameras` (every angle) |
| `mockups/` | 3 downloaded mockups for QA |
| `etsy_published` | Written by `printify.py publish` (Lister only, after QA) |

Shared: `pod/PROVIDERS.md` (providers, costs, pricing), `pod/SAVED-REPLIES.md`, `pod/make_art.py`.

## Sizes (300 DPI, from `printify.py variants`)
- **11 oz mug**, blueprint 68, SPOKE (1), variant 33719: full wrap **2700x1120 px** (9 x 3.73 in), RGB, solid background colour edge to edge. Printify's mockup cameras look at **1/4 (left), 1/2 (front, the default Etsy photo) and 3/4 (right)** of the wrap, so put a motif at all three. The middle must not be empty: either 3 narrow motifs at x = 675/1350/2025, or 2 wide ones at 675/2025 plus a centre accent. Keep motifs within about 60 px of the top and bottom.
- **Tee**, blueprint 12, Monster Digital (29): front **4500x5100 px** (15 x 17 in) **transparent PNG**. Design about 10 in (3000 px) wide, centred, top 1 in (300 px) below the top of the print area. S and M have smaller placeholders with the same aspect ratio, and Printify scales the file to fit. `scale` 1 = full placeholder width.

## Art pipeline
1. Prompt = STYLE.md Prints/POD block + subject, palette hexes named, "solid flat <colour> background", "generous empty margin", no text.
2. `imagegen.py gen ... --pro --n 4 --size 2048x2048`, contact sheet, check the best at 100%, regenerate the batch if none is clean (the skull needed 2 batches).
3. Tees: `imagegen.py upscale` once. Recraft crisp upscale **caps at 4096 px**, and a second pass returns 4096 again, so don't pay for it. 4096 px of source is about 10 in of design at true 300 DPI.
4. Mugs: the 2048 px Pro source is already enough (the motif is downsampled), so no upscale is needed.
5. `pod/make_art.py` does the layout. Tee backgrounds are keyed out locally (soft ramp, unpremultiplied), so solid black/white areas inside the art become the shirt colour. Light-on-black art goes on dark shirts; dark-on-white art goes on light shirts. Mug motifs are pasted with a feathered mask on the sampled flat background colour, so no paste edge can show.

## Checks (Designer, then QA)
- Each art file at 100%: no artefacts, smudges, stray marks (one drip was painted out on 002), garbled shapes, text or signatures.
- Tees: alpha has no faint specks outside the design (Recraft upscale leaves faint noise along the image border, which make_art drops by cropping to alpha > 0.5). Preview on a real shirt colour for every enabled colour family.
- **Alpha check on mid-grey** (required for every tee): composite the PNG on a mid-grey (#b2b2af, roughly Ash) at 100% and look for unkeyed near-white patches (dark-on-light art) or near-black patches (light-on-dark art), and for a light or dark fringe along gap edges. Numeric check: semi-transparent pixels (0 < alpha < 250) should not be much lighter or darker than the opaque design. If the fringe median luminance is far from the design's, decontaminate it (004: semi-transparent pixels take the nearest opaque colour). Look at every small gold/accent mark: AI "stars" are often squiggles or smudges; replace them with drawn shapes (`clean_stars()`) rather than shipping them.
- Pixels: mug wrap exactly 2700x1120; tee exactly 4500x5100 RGBA; design ≥ 2800 px wide with no more than about 1.15x upsampling.
- Tee colours: at most 4; dark designs only on light shirts and light designs on dark shirts; sizes S–3XL (24 variants).
- Mockups: download front + side/lifestyle (mugs) or front on 2 colours + folded (tees). Check placement (centred, not cut by the handle or collar), crop, contrast, and that the **default front image** looks complete.
- Listing: title ≤140, exactly 13 unique tags ≤20 chars, description covers production partner, material, size, care, production + shipping times, and ends with the disclosure line ("Designed with the help of digital and AI tools, and checked by hand." or "Designed by Duskwood Designs Co").
- The live Printify product (GET) matches product.json: title, **description** (compare text with HTML tags stripped), tags, enabled variant ids, one price, the print file in the placeholder, and `external` empty (not on Etsy yet). After any change to product.json, run `printify.py update pod/NNN-slug` (add `--no-art` when only copy or price changed) and check again. Never let the draft and the files drift apart.

## Pricing rule
After `create`, read variant `cost` (GET `/shops/{shop}/products/{id}.json`). Retail R (.99) such that
R − (0.10·R + $0.20) − 0.10·shipping − cost ≥ $6 (mug) / $8 (tee). Shipping is Printify's first-item US rate, which the buyer pays and Etsy also charges fees on (mug $6.69, tee $4.49; 10% is conservative). Check against the **most expensive enabled variant** (tee 3XL), because `printify.py` sets one price for all variants. Then check R against comparable Etsy listings, labelling the figures as estimates. Pilot: mug $16.99 (profit $7.98), tee $28.99 (profit $8.67 at 3XL, $13.67 at S–XL). See `pod/PROVIDERS.md`.

## Listing images: the lead photo (set by the Lister, no owner step)
Printify sends Etsy only the mockups it marks "selected for publishing" (after `create`: just the plain front view). Its API ignores `is_default` / `is_selected_for_publishing` (tested 3 Oct 2026), so the lead photo is set on the Etsy side instead, by the Lister, in the same shift as the publish or the next one:
1. `python3 tools/printify.py publish <pod_dir>` (counts toward the daily listing cap).
2. A few minutes later: `python3 tools/printify.py etsy-id <pod_dir>` writes `etsy_listing_id`. If it is not on Etsy yet, retry next shift.
3. `python3 tools/etsy.py lead-photos <pod_dir> <files...>` uploads the mockups saved in `pod_dir/mockups/` as photos #1, #2, ... ahead of Printify's front view:
   - **Mugs:** `mockups/context-1-11oz.jpg mockups/left-11oz.jpg`
   - **Tees:** `mockups/folded-<colour>.jpg`, then the other colour fronts not already on Etsy.
4. Check: GET `/listings/<id>/images` (or view the listing) and confirm the lifestyle shot is first, then log it in `mockups.json` as `"etsy_lead_photo"`.

Later re-publishes from Printify send `images: false` (the tool does this once `etsy_published` exists), so the Etsy photo order is kept. If a product's images ever get reset, run step 3 again.

## Tool notes
- `printify.py update <pod_dir> [--no-art]` (added in QA round 1) syncs title, description, tags, one price for the enabled variants (all others disabled) and, without `--no-art`, re-uploads the print files. With print files, Printify requires `print_areas.variant_ids` to cover **every** variant of the product, enabled or not; the tool does this. It never publishes.
- Still missing: per-variant prices. Mockup selection in Printify is not possible through the API, so the lead photo is set through Etsy (see above).
- Delete-and-recreate (DELETE `/shops/{shop}/products/{id}.json`, then `create`) is only for unpublished drafts, i.e. those whose `external` field is empty.
