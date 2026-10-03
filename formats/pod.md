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
- Pixels: mug wrap exactly 2700x1120; tee exactly 4500x5100 RGBA; design ≥ 2800 px wide with no more than about 1.15x upsampling.
- Tee colours: at most 4; dark designs only on light shirts and light designs on dark shirts; sizes S–3XL (24 variants).
- Mockups: download front + side/lifestyle (mugs) or front on 2 colours + folded (tees). Check placement (centred, not cut by the handle or collar), crop, contrast, and that the **default front image** looks complete.
- Listing: title ≤140, exactly 13 unique tags ≤20 chars, description covers production partner, material, size, care, production + shipping times, and ends with the disclosure line ("Designed with the help of digital and AI tools, and checked by hand." or "Designed by Duskwood Designs Co").
- Printify product matches product.json (title, tags, price, enabled variants) and `external` is empty (not on Etsy yet).

## Pricing rule
After `create`, read variant `cost` (GET `/shops/{shop}/products/{id}.json`). Retail R (.99) such that R − (0.10·R + $0.20) − cost ≥ $6 (mug) / $8 (tee), checked against the **most expensive enabled variant** (tee 3XL), because `printify.py` sets one price for all variants. Then check R against comparable Etsy listings (label the figures as estimates). Pilot: mug $16.99, tee $27.99 (see `pod/PROVIDERS.md`).

## Listing images
Printify generates and sends the mockups on publish: mugs get 1 front image (more angles can be selected in Printify), tees get 4 front images, one per colour. FACTORY.md wants the first photo to show the product in use. The mug `context-1` lifestyle shot (mug with coffee, candle and pine cones) is better than the plain front, so select it as the default in Printify before publishing if possible. The API tool has no image-selection command, so this is a manual Printify step for now.

## Known tool gaps (as of the pilot)
- `printify.py` has no `update`: changing price, copy or art after `create` means editing in the Printify UI, or deleting the unpublished draft and re-running `create`.
- No per-variant price.
- No default-mockup selection.
