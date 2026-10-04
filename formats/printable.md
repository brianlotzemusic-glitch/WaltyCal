# Format spec: printable checklists and sticker sheets (PDF + print-then-cut PNG)

First built 4 Oct 2026 (pilot: `bundles/011-small-autumn-moments`). A digital download: the buyer prints at home. Read with FACTORY.md "Product formats" and "Art quality". Same pipeline as `formats/bingo.md` (code-drawn icons, HTML → PDF with Playwright/Chromium, listing images from the real pages); this spec covers checklists, bucket lists, trackers and sticker sheets.

## Folder: `bundles/NNN-slug/`
| File | What |
|---|---|
| `gen.py` | Runs every step, sets the PNG DPI tag, builds the ZIP, then the checks. `python3 gen.py --check` re-runs only the checks |
| `icons.py` | Icons drawn in code (shapely, 1000-unit box, y down) as layers of (shape, fill, outline). Writes `icons/NN-name.svg` and `icons.json` |
| `moments.json` (or `items.json`) | The checklist text, in sections. Our own writing only |
| `stickers.py` | Lays out the sticker sheet in px at 300 DPI, computes each cut outline with shapely and proves the sheet (`--check`); writes `stickers.json` (sticker SVGs, sheet SVG, proof) |
| `build.js` | Checklist PDF + sticker PDF per paper size, and the transparent PNG. Fails if any text box overflows |
| `contact.js` | `contact-sheet.png`: every icon at 250 px and at page-decoration size, plus every sticker on grey (shows the white border) |
| `thumbs.js` | `listing-images/` from the real PDF pages (`pdftoppm`) and the real sticker SVGs |
| `fonts/` | OFL fonts embedded as data URIs (pilot: Fraunces 700/900, Nunito 400/700/800; the system has no suitable display fonts, see `fc-list`) |
| `README-LICENSE.txt` | Files, page map, sticker list, printing tips, Cricut steps, personal-use licence |
| `<slug>-printable.zip` | Buyer file: PDFs + PNG + README-LICENSE.txt, nothing else |
| `LISTING.md`, `listing.json` | Listing copy (same fields as the other bundles) |
| `PROMPTS.md` | Only if AI images were used |

## Checklist pages
- **Paper:** US Letter 612 × 792 pt and A4 595 × 842 pt, portrait, same page order in both. Keep text and checkboxes at least 15 mm from the edge and the art at least 9 mm (home printers clip about 6 mm).
- **Pages (pilot, 4):** 1 the checklist, 2 a "write your own" page (about 15 ruled lines, checkbox + line + short "when" line), 3–4 the same two on white (**ink saver**).
- **Look:** cream #f1e6cf page background on the main pages (the shop look on screen; home printers leave a white margin, say so in the README), a thin double frame, the title in Fraunces 900 with one word in berry, a small uppercase kicker, a one-line subtitle. Line-art icons (plum outline, spot fills in pine/berry/gold/cream) in the corners and along a ground line at the bottom. No full-bleed dark fills.
- **List:** about 30 items in 2 columns and 4 short sections with a small icon each; checkbox 4.4 mm rounded square; body text Nunito about 10.5 pt (3.7 mm) in plum; items may wrap to 2 lines. Specific, real, cozy moments, written by us: no lyrics, quotes, brands or trademarked phrases.
- **Overflow:** `build.js` measures every column/header/row box and stops on overflow. Letter is 17.6 mm shorter than A4, so check Letter first.

## Sticker sheet
- **Area:** Cricut Print Then Cut max printable area **6.75 × 9.25 in**. The PNG is exactly that: **2025 × 2775 px, 300 DPI tag, RGBA with a transparent background** (Chromium screenshot with `omitBackground`, then `PIL .save(dpi=(300, 300))`).
- **Stickers:** about 20 at 1.3–1.6 in. Pilot design: cream disc with plum ring + icon + phrase pill (Fraunces 700, measured with PIL so it fits). Every sticker gets a **white offset border** (pilot 24 px = 0.08 in) from `union(disc, pill, icon).buffer(border)` with a 30 px closing so the blade has no tight notches; holes are filled. The outer edge of the border is the cut line.
- **Proof (`stickers.py --check`):** 20 stickers; every outline inside the sheet; each outline one polygon with no holes; at least **45 px (0.15 in)** between outlines (Cricut adds bleed); at least 15 px from the sheet edge.
- **PDF version:** the same sheet centred on Letter/A4 at actual size, with light grey cut guides (on the white border) and a dashed outline of the 6.75 × 9.25 area, for sticker paper + scissors.
- **README/description:** Design Space steps: upload the PNG as a Print Then Cut image, set width 6.75 in, print with bleed, cut.

## Checks (Designer, then QA)
`python3 gen.py --check` must print ALL CHECKS PASS:
- every PDF: right page count and size (Letter 612×792 pt, A4 595×842 pt), all fonts embedded (`pdffonts`, no fallback fonts), under 20 MB
- sticker proof as above; PNG 2025×2775, 300 DPI, RGBA, transparent corners, at least 30% transparent and 30% opaque
- ZIP holds exactly the PDFs, the PNG and README-LICENSE.txt
- 4 listing images at 3000×2250; `contact-sheet.png` present
- listing: title ≤140 chars and leads with the search phrase; no more than 3 words starting with 2 capitals (write "pdf", "png"); at most one "&"; exactly 13 unique tags ≤20 chars; plain apostrophes, no HTML entities; description ends with exactly "Designed with the help of digital and AI tools, and checked by hand."; taxonomy id, price, `digital_file` = the ZIP; LISTING.md matches listing.json

Then look, don't only count:
- `contact-sheet.png`: every icon reads at decoration size; no two alike
- render every page of both sizes (`pdftoppm -r 80`): nothing clipped, columns balanced, footer art inside the frame, title on one line
- the PNG composited on a dark colour: every sticker has an even white border, nothing touches
- listing images show only what the files contain (real pages, real stickers; a sticker shown "peeled" is removed from the sheet in the same image)

## Listing images (3000×2250)
1. `1-thumbnail.png`: flat-lay on a dark wood table: the printed checklist, the sticker sheet with a few stickers peeled off and lying on the table, small code-drawn props (mug, pencil, leaves); a plum title band with the search phrase ("Fall Bucket List") and a "+20 stickers" badge. The dark band and table stand out next to the usual orange-on-white results.
2. `2-whats-included.png`: every page + the PNG (on a checkerboard) with labels, 3 feature tiles.
3. `3-formats.png`: Letter and A4 tagged, the PNG with its 6.75 × 9.25 in size, format bullets.
4. `4-sticker-closeup.png`: 4 stickers large on wood + all 20 small, with the border/cut-line note.

## Etsy
- Category: Paper & Party Supplies > Paper > Calendars & Planners, `taxonomy_id` **354** (`python3 tools/etsy.py taxonomy planner`; "checklist" and "printable" return nothing). A sticker-only product would use 1326 (Stickers).
- Type digital, who made "i_did", when made "2020_2026", not a supply. Pilot price $3.50.
- Licence: personal use, unlimited prints for the buyer's own home, planner and family; no resale or sharing of files or printed stickers.

## Reuse
For another season or theme (winter, spring, "small Christmas moments", reading tracker), copy the folder, replace `moments.json`, the icon functions and phrases in `icons.py`, the titles in `build.js` and `thumbs.js`, and run `gen.py`. Keep `stickers.py` (change only the grid if the count changes, then re-check the gap).
