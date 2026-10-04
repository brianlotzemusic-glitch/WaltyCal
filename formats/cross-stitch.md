# Format spec: counted cross-stitch patterns (PDF charts)

First built 4 Oct 2026 (pilot: `bundles/012-woodland-christmas-cross-stitch`, 12 mini Christmas ornaments; updated after QA round 1: size range, one-colour readability rule and check, lifestyle photo 1, fabric copy). A digital download: the buyer reads or prints the PDF and stitches with their own fabric and floss. Read with FACTORY.md "Product formats" and "Art quality". Cross-stitch charts are naturally geometric (pixel grids), so they are drawn in code. AI is used only for the lifestyle background of listing image 1, never for the stitching (see Listing images).

## Folder: `bundles/NNN-slug/`
| File | What |
|---|---|
| `gen.py` | Runs every step, builds the ZIP, then the checks. `python3 gen.py --check` re-runs only the checks |
| `motifs.py` | The motifs as pixel grids, drawn with a small DSL (ellipse, poly, rect, line, cells, mirror) on a canvas, cropped and given a 1-stitch 3371 outline (4-neighbour). Derives the one-colour grid. Writes `motifs.json` (palette, grids, stitch counts) and `contact-sheet.png`. `--check` re-checks |
| `stitch.py` | Renders each motif as X stitches on Aida in a wooden hoop (`art/hoop-<key>-{colour,mono}.png`) straight from the grids, for the listing images |
| `build.js` | HTML → PDF with Playwright/Chromium, once per paper size. Chart symbols are SVG shapes (no symbol font). Fails on text overflow or a chart larger than its box |
| `thumbs.js` | `listing-images/` from the real PDF pages (`pdftoppm`) and the stitched renders |
| `fonts/` | OFL fonts embedded as data URIs (pilot: Fraunces 700/900, Nunito 400/700/800) |
| `README-LICENSE.txt` | Files, page map, motif list with stitch counts and sizes, stitching notes, licence |
| `<slug>-pattern.zip` | Buyer file: both PDFs + README-LICENSE.txt, nothing else |
| `LISTING.md`, `listing.json` | Listing copy (same fields as the other bundles) |
| `art/` | Working renders for the listing images (stitched hoops, the AI background); not in the ZIP |
| `PROMPTS.md` | The background prompt, drafts, the one chosen and the spend |

## Motifs
- Original designs only; take the subject and size from proven sellers, never their charts.
- **Size:** mini ornament = about 25–35 stitches each way (about 1.8–2.5 in on 14-count, 1.4–1.9 in on 18-count); `motifs.py --check` accepts 23–35 in both directions. **Never type size or stitch-count ranges by hand:** `motifs.py` writes `ranges` (min–max width and height, inches on 14 and 18-count) into `motifs.json`; `build.js` and `thumbs.js` print them, and `gen.py --check` fails if the description, README or PDF text disagrees. Larger formats (samplers, wall pieces) need their own size rule here first.
- **Readability:** clean pixel-art silhouettes, symmetrical where the subject is (use `mirror()`), every motif recognisable at contact-sheet size. **No stray stitches:** every stitched cell has at least one stitched 8-neighbour, in both versions (checked).
- **Colour version:** 3–6 DMC colours per motif (outline 3371 counts as one), all from one shared palette of 8–10 DMC colours. Pilot palette (DMC number, official name, chart symbol): 3371 Black Brown (filled dot), 550 Violet Very Dark (filled diamond), 500 Blue Green Very Dark (filled triangle), 3363 Pine Green Medium (open triangle), 815 Garnet Medium (cross), 920 Copper Medium (open circle), 729 Old Gold Medium (star), 712 Cream (open square), 433 Brown Medium (half-filled square), 436 Tan (open diamond). No two symbols may be rotations of each other (a + next to a × is risky in black-and-white prints). Use real DMC numbers and names, double-checked; screen hex values are approximations.
- **One-colour version:** one DMC colour (pilot 3371). Derived from the colour grid: outline and fills stitched; the motif's "light" set left as negative space; interior 3371 details (eyes, wing lines, the rim under a cap) turned into gaps unless they touch the outline (beaks, paws) or sit next to a light gap (pupils). Optional per-motif `split` (e.g. robin `"CB"`): a one-colour-only gap line where two fills meet, so a breast or patch stays visible.
- **One-colour readability rule:** the light set may contain only light or accent colours that make up a small part of the motif: 712 Cream, 729 Old Gold, 436 Tan highlights or texture, 3363 veins, 815 spots or baubles. Never a mid or dark fill that makes up most of the motif (920 copper body or breast, 500 leaves, 433 body); a motif whose silhouette then becomes a hollow outline does not sell (QA round 1: the robin with its 920 breast as a gap, and the acorn with its 500 leaves as gaps, read as a blob and a beetle). `motifs.py --check` fails a motif when the one-colour version keeps **< 65%** of the colour stitches, has an **enclosed gap > 25%** of the motif's stitches (hollow), or **breaks into new 8-connected parts > 6 stitches** (small new parts such as pupils are listed for review). The pilot lantern keeps 68% (its glowing panes are the gaps) and passed review by eye. The numbers only flag problems: always look at the contact sheet as well.
- **Stitches:** full cross stitch only, 2 strands on 14-count; no fractional stitches. Backstitch only if a motif cannot read without it (then add it to the key and the checks).

## PDF (US Letter 612 × 792 pt and A4 595 × 842 pt, portrait, same page order)
1. Cover (all motifs, title, badges) 2. Contents / overview: every motif in both versions with stitch count and page numbers 3. How to stitch & finish as an ornament (materials, reading the chart, stitching, flat felt-backed ornament, mini hoop) 4. Floss shopping list: every DMC colour with symbol, name, charts it is used in, stitches, skeins (rounded up), plus the one-colour option and fabric. Fabric copy must be true: a 6 × 6 in piece per ornament; a fat quarter (about 18 × 21 in) cuts only 9 such pieces 5+. One chart page per motif, colour charts first, then the one-colour charts.

Each chart page:
- the grid as large as fits (cap 5.4 mm per square; about 5 mm for 34 rows on Letter), a symbol in every stitched square, colour fill on the colour chart and a light grey fill on the one-colour chart; white or black symbol by fill luminance
- thin lines on every square, **bold lines every 10** (counted from the top-left), **row and column numbers** every 5 (bold at 10s), **centre arrows** on all four sides
- facts: stitch count W × H, finished size on 14-count and 18-count (in and cm), strands note ("2 strands, full cross stitch only. No backstitch needed."), fabric
- floss key: symbol swatch, DMC number, name, stitches, skein estimate (1 skein ≈ 1,600 full crosses with 2 strands on 14-count, conservative; shown as "1 (uses N%)")
- name DMC only as a floss reference; say "not made or endorsed by DMC" (shopping list footer, README, description)

## Checks (Designer, then QA)
`python3 gen.py --check` must print ALL CHECKS PASS:
- motifs: one-colour readability (keeps ≥ 65%, no enclosed gap > 25%, no new parts > 6 stitches); size ranges in `motifs.json` match the grids; count, grid dimensions (W × H match `motifs.json`, 23–35), every stitched cell has a palette colour with a symbol, symbols unique within each key and across the palette, 3–6 colours per motif, palette 8–10 unique DMC numbers, stitch counts match, no stray stitches in either version, one-colour stitches only inside the colour shape
- PDFs: right page count, every page 612×792 (Letter) or 595×842 (A4), all fonts embedded (`pdffonts`), under 20 MB; each chart page (`pdftotext`) carries the right motif title, version and "Stitch count: W W × H H"; the PDF text, README and description use the computed size and stitch ranges and the correct fat-quarter count; the README motif table matches the grids
- ZIP holds exactly both PDFs and README-LICENSE.txt; README has the page map and licence
- 4 listing images at 3000×2250; `contact-sheet.png` present
- listing: title ≤140 chars leading with the search phrase; no more than 3 words starting with 2 capitals ("pdf" lowercase; "DMC" counts, so keep it out of the title); at most one "&"; exactly 13 unique tags ≤20 chars; plain apostrophes, no HTML entities; description ends with exactly "Designed with the help of digital and AI tools, and checked by hand."; taxonomy id, price, `digital_file` = the ZIP; LISTING.md matches listing.json

Then look, don't only count:
- `contact-sheet.png`: every motif recognisable in both versions; one-colour versions still read as the subject, not a hollow outline or an unrelated shape (eyes, spots, windows as negative space); no two alike; the subject name matches the colours (a brown owl is not a "snowy owl")
- render one chart page of each version on both sizes (`pdftoppm -r 110`): symbols legible, bold 10-lines and numbers line up, arrows at the true centre, key matches the colours on the chart, nothing clipped
- listing images show only what the charts make (stitched renders come from the grids)

## Listing images (3000×2250)
1. `1-thumbnail.png` (FACTORY.md: the first photo shows the product in use): a **lifestyle composite**. Generate ONE empty scene with the cheap recipe (`imagegen.py gen "<STYLE.md mockup block> + table/tree scene with open space, no embroidery, no hoops, no text" art/bg.png --flash --n 4`, $0.028), pick the clean draft, crop it to 4:3 and place the code-rendered `stitch.py` hoops of our real motifs on it, with a plum title band (search phrase) and a "12 charts × 2 versions" badge. Never let AI draw the stitching: it won't match the charts. Record the prompt and spend in `PROMPTS.md`. With no AI budget, use the code-drawn wood scene instead ($0).
2. `2-whats-included.png`: the real pages (cover, contents, how-to, shopping list, one colour chart, one one-colour chart) with labels, 3 feature tiles, all motifs as small hoops.
3. `3-chart-closeup.png`: a real chart page with a magnifier on the symbols and grid, plus feature bullets.
4. `4-colour-vs-one-colour.png`: the same motifs stitched in colour and in one colour, side by side.

## Etsy
- Category: Craft Supplies & Tools > Patterns & How To > Patterns & Blueprints, `taxonomy_id` **6343** (`python3 tools/etsy.py taxonomy "cross stitch"` returns it and 87, which is for finished cross-stitch art, not patterns).
- Type digital, who made "i_did", when made "2020_2026", not a supply. Pilot price $3.50.
- Fabric copy (README, shopping list, description): about 6 × 6 in per ornament; a fat quarter cuts 9 pieces. Don't promise more.
- Licence: personal use; the buyer may sell finished pieces they stitch by hand in small quantities (pilot: up to 50 in total), as is common for cross-stitch; no sharing, reselling or converting the pattern (kits, machine-embroidery files, printed products).

## Reuse
For the next set (e.g. cottagecore frogs and mushrooms), copy the folder, replace the motif functions and `MOTIFS` list in `motifs.py` (keep or adjust the palette, max 10), update titles in `build.js` (cover/contents text) and `thumbs.js` (which motifs appear), the README motif table and the listing copy, then run `gen.py`. Page numbers follow the motif count (cover, contents, how-to, shopping list, then colour and one-colour charts); update `PAGES` in `gen.py`.
