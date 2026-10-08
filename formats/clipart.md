# Format spec: clipart (transparent PNG + single-layer SVG)

First built 8 Oct 2026 (pilot: `bundles/015-highland-cow-christmas-clipart`, 12 designs, $3.49). A digital download: the buyer places the designs in their own projects (sublimation, print, print then cut, cards, invitations, stickers). Read with FACTORY.md "Product formats" and "Art quality".

The art comes from AI drafts, like the coloring pages. Each design costs about **$0.042**: `gen --flash --n 4` ($0.028), `removebg` on the kept draft ($0.01) and `upscale` on the kept draft ($0.004). Everything after that is local and free.

## Folder: `bundles/NNN-slug/`
| File | What |
|---|---|
| `subjects.json` | The base prompt and the `[slug, name, subject]` rows. The single source for design order, file names, the README list and the listing |
| `picks.json` | Which of the 4 flash drafts was kept per design |
| `art/raw/NN-slug.png` | The kept 1024 × 1024 draft on white |
| `art/alpha/NN-slug.png` | Its removebg mask (only the alpha channel is kept: it is all `process.py` needs) |
| `art/up/NN-slug.png` | The kept draft through `upscale` (4096 px). **Not committed** (`.gitignore`, ~12 MB each); recreate with `imagegen.py upscale` ($0.004) to rebuild from scratch |
| `process.py` | Draft + mask + upscale → `art/png/` (final PNGs), `art/svg/` (single-layer SVGs) and `art/stats.json`. Per-design fixes live here (`FILL_HOLES`, `ERASE_BOX`) |
| `mockup.py` + `mockup/` | The usage photo: a blank AI flat-lay (one flash draft set + one upscale, about $0.03 a bundle) with the real PNGs multiplied onto it |
| `thumbs.js` | `listing-images/` from the real PNGs, SVGs and the mockup |
| `gen.py` | Runs every step, builds the contact sheet and the ZIP, then the checks. `--check` re-runs only the checks; `--skip-art` keeps `art/png` and `art/svg` |
| `fonts/` | OFL fonts for the listing images only |
| `README-LICENSE.txt`, `LISTING.md`, `listing.json`, `PROMPTS.md` | Buyer README and licence, listing copy, every prompt with the spend |
| `<slug>.zip` | Buyer file: `PNG/` and `SVG/` with one file per design, plus README-LICENSE.txt |

## The files
- **PNG:** transparent background, **3600 px on the longest side** (12 in at 300 dpi, big enough for an adult tee), dpi metadata 300, trimmed to the art. Saved as a 256-colour palette PNG with alpha: flat-colour art looks the same, and a design is ~0.5–2 MB instead of ~8 MB. This matters because **Etsy takes one file of at most 20 MB** (`etsy.py upload` sends one `digital_file`).
- **SVG:** a one-colour line-art version of the same design: the dark linework, eyes and nostrils, plus a closed outer contour, potraced into one even-odd path in deep plum. It opens at the PNG's print size. It is **not a cut file** (fine fur lines); the listing, README and image 4 say so. Colour areas without lines (scarf stripes, a bauble) become outlines only.
- **No text** on any design, ever (no slogans until the Researcher has checked the phrase against trademarks).

## Art (cheap recipe only)
- Prompt: the clipart line in `shop-profile/STYLE.md` + ` Subject: ` + the subject. Generate at **1024 × 1024**. Flash accepts 1024x1024, 896x1152 and 1152x896, not 1536x1024 or 1024x1365.
- Ask for **clean dark outlines and flat colours on plain pure white, one isolated subject, no ground shadow, no scenery**. The outlines make the cut-out clean and the SVG possible, and flat colour keeps the palette PNG small.
- Per design: `gen --flash --n 4` without `--transparent`: with `--n 4`, that flag runs removebg on all four drafts ($0.04). Then `removebg` and `upscale` on the kept draft only. Upscale the **white-background draft**: `upscale` returns RGB and drops alpha, so `process.py` scales the removebg mask itself.
- At most one standard `gen` ($0.035) when all four drafts are unusable; no `--pro`, no `vectorize`.
- Reject a draft that is cropped at the edge, has a text-like mark, extra legs or horns, or a face that looks wrong; a swap to another draft is free.

## Cut-out clean-up (`process.py`)
1. Scale the removebg mask 4× to the upscale, steepen its edge, and un-mix the white from edge pixels (no white halo on dark fabric).
2. Trim to the art and resize so the longest side is 3600 px.
3. **White paper between fine shapes:** removebg keeps the white between pine needles, fur tips and berries as opaque, and it shows as white specks on dark fabric. Near-white, neutral pixels joined to the background are made transparent, with soft edges (`clear_white`). Enclosed whites (eye highlights) stay.
4. **White parts taken as background:** removebg can also cut out small white parts of the art (the mistletoe berries in the pilot). Mark every enclosed transparent hole and look. Put back the ones that are art (`FILL_HOLES`, by size) and leave the real gaps (ribbon loops, between legs, inside a wreath).
5. **Messy bits found at 100%** (grey snow shadow in the pilot's design 05): erase in a box (`ERASE_BOX`), keeping only the subject's own colours. Pieces left wholly inside the box are dropped, and the art is trimmed again.
6. Drop specks under 900 px and faint haze more than 4 px from solid art, then save the palette PNG at 300 dpi and trace the SVG.

## Checks (Designer, then QA)
`python3 gen.py --check` must print ALL CHECKS PASS:
- distinct designs, names and subjects; `picks.json`, `art/stats.json`, `art/raw` and `art/alpha` cover every design
- ZIP: exactly `PNG/` and `SVG/` with one file per design plus README-LICENSE.txt, **under 20 MB**
- every PNG: transparent, longest side 3600 px, 300 dpi, clear corners, ≥ 15% transparent, no piece under 900 px, ≤ 3% paper-white pixels on the art's outer edge (halo test), ≤ 3 MB
- no two designs alike (24 × 24 shape + tone hash, ≥ 60 of 1152 bits differ)
- every SVG: parses, exactly one path in one colour, no text or embedded image, opens at the PNG's print width and aspect, ink 3–45% of the canvas
- README lists every design; 5 listing images at 3000 × 2250, each under 10 MB; `contact-sheet.png` present
- listing: title ≤ 140 chars and leads with the search phrase; at most 3 words starting with 2 capitals (PNG and SVG count; write "dpi"); at most one "&"; exactly 13 unique tags ≤ 20 chars; no HTML entities, plain apostrophes; the description names every design and ends with exactly "Designed with the help of digital and AI tools, and checked by hand."; taxonomy id, price, `digital_file` = the ZIP; LISTING.md matches listing.json; PROMPTS.md present

Then look, don't only count:
- `contact-sheet.png`: every design on a checkerboard, on dark green and as the SVG. Each reads at a glance, nothing is clipped, and there is no white fringe or hole on the dark tile
- every PNG at full size on a dark background, and 100% crops of the fine areas (needles, fur tips, lights, berries): AI faults (letters, extra legs or horns, warped faces), white specks, grey shadow, holes where art should be
- the listing images at Etsy thumbnail size (300 px wide)

## Listing images (3000 × 2250)
1. `1-thumbnail.png`: 4–5 of the strongest designs, large, on dark pine green. A cream band with the search phrase, "PNG + SVG · TRANSPARENT · 300 DPI" and a "12 designs" badge. Few big cows read at 300 px; twelve small ones do not.
2. `2-all-designs.png`: every real PNG on cream, numbered and named, 4 per row.
3. `3-mockup.jpg`: the real PNGs on a tee, a card and a tote (`mockup.py`). JPEG, because a photo as PNG is ~10 MB.
4. `4-png-and-svg.png`: one design on a checkerboard, on a dark colour and as the SVG, plus four more SVGs and the "not a vinyl cut file" note.
5. `5-whats-included.png`: files, sizes, uses, licence.

## Etsy
- Category: Craft Supplies & Tools > Canvas & Surfaces > Stencils, Templates & Transfers > Clip Art & Image Files, `taxonomy_id` **6844** (`python3 tools/etsy.py taxonomy clip`).
- Type digital, who made "i_did", when made "2020_2026", not a supply. Tick Etsy's AI-assisted disclosure.
- Pilot price **$3.49** for 12 designs + SVGs. Evidence: clipart median ~$3.99, "mushroom clipart" ~$3.99, "nutcracker clipart" ~$4.70 (RankHero est.). The proven highland cow PNG set is ~$1.75 for 22 designs (EtsyHunt est.).
- Licence: personal use, plus small-business use on physical items the buyer makes and sells, up to 500 per design. No resale or sharing of the files, no print-on-demand marketplaces, no stock or AI training, no trademark or logo use.

## Reuse
For the next set (nutcracker, butterflies & dragonflies, mushrooms, cardinals): copy the folder, replace `subjects.json`, generate drafts, fill `picks.json`, run `removebg` and `upscale` on the kept drafts into `art/alpha` (alpha channel only) and `art/up`, then clear `FILL_HOLES` and `ERASE_BOX`. Look at every design on dark at 100% and add fixes as needed. Update the README list, the thumbnail's design picks in `thumbs.js`, `mockup.py`'s `PLACES` (the blank flat-lay photo can be reused for free) and the listing, then run `gen.py`.
