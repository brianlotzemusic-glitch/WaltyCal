# Format spec: coloring pages (bold & easy, PDF)

First built 5 Oct 2026 (pilot: `bundles/014-christmas-woodland-coloring-pages`, 20 pages, $3.99). A digital download: the buyer prints the pages at home and colours them. Read with FACTORY.md "Product formats" and "Art quality".

This is the first format whose art comes from AI drafts rather than code: coloring pages need drawn scenes, not geometry. The drafts are cheap (`gen --flash --n 4`, $0.028 a page) and everything after them — scaling, thickening, closing, tracing, the PDFs, the examples and the listing images — is local and free.

## Folder: `bundles/NNN-slug/`
| File | What |
|---|---|
| `subjects.json` | The base prompt and the 20 `[slug, page name, subject]` rows. The single source for the page order, the README list and the listing |
| `art/raw/NN-slug.png` | The chosen AI draft per page, 896 × 1152, greyscale (the drafts not used are not committed) |
| `picks.json` | Which of the 4 flash drafts was kept per page |
| `process.py` | Draft → bold, closed line art: upscale, despeckle, thicken, frame, fill tiny spaces, erase stray blobs, potrace. Writes `art/svg/`, `art/mask/` and `art/stats.json` |
| `build.js` | The buyer PDFs, one page per design, no text (Playwright/Chromium) |
| `colorize.py` | Coloured-in examples of 1–2 real pages, **for the listing images only**, by filling those pages' own regions |
| `thumbs.js` | `listing-images/` from the real PDF pages and the coloured examples |
| `gen.py` | Runs every step, builds the ZIP and the contact sheet, then the checks. `python3 gen.py --check` re-runs only the checks; `--skip-art` keeps the existing line art (process.py takes ~5 min for 20 pages) |
| `fonts/` | OFL fonts for the listing images only (the pages have no text) |
| `README-LICENSE.txt` | Files, page list, bold & easy note, printing tips, personal-use licence |
| `<slug>-printable.zip` | Buyer file: the two PDFs + README-LICENSE.txt, nothing else |
| `LISTING.md`, `listing.json`, `PROMPTS.md` | Listing copy and every prompt, with the spend |

## The pages
- **Paper:** US Letter 612 × 792 pt and A4 595 × 842 pt, portrait, the same 20 pages in the same order. `build.js` sets the Chromium `format` plus `preferCSSPageSize`, which is what gives exact paper sizes.
- **Art box:** the same physical size on both papers (pilot 182 × 234 mm, the draft's 896:1152 ratio), centred. So the line weight is identical on Letter and A4, and the margin is ≥ 17 mm on Letter and ≥ 14 mm on A4 (home printers clip about 6 mm).
- **One design per page, and no text at all** — no titles, page numbers or shop name. The check proves it: the PDF must embed no fonts and `pdftotext` must return nothing.
- **Frame:** a rounded rectangle at the art box edge, the same weight as the art. It closes every shape that runs off the edge, so the background is colourable, and it gives the page a finished look.
- **Count:** 20 pages is the pilot size and matches what sells; every page a different subject and composition.

## Bold & easy line art (`process.py`, per page)
1. Upscale the draft 3× (Lanczos) and threshold: smooth edges at print size.
2. Drop ink specks under 1.2 mm².
3. **Thicken** until the median stroke is 1.6 mm, never adding more than 0.55 mm a side (a draft already bold is left alone).
4. Draw the frame, and treat the paper outside its rounded corners as paper, not a space.
5. **Fill every white space under 12 mm² with black.** Fiddly slivers are what makes AI line art unusable for colouring; filled, they become eyes, nostrils, berry centres and snowflake cores.
6. Erase solid blobs 6–18 mm across that float in open background (over 45 mm² of ink, enclosing no paper, in a region over 2500 mm²): they read as ink stains. Faces and anything touching another line stay. Per-page fixes handle what the rule can't: `RAW_WIPE` / `RAW_LINES` (paint a stray stroke out of the draft, redraw a line it cut), `ERASE` boxes, and code-drawn `SHAPES` (chunky six-arm snowflakes, outlined snow mounds).
7. **Clumps:** the fill in step 5 can turn a fine motif (grass tufts, crowded leaves, snowflake details) into one solid black splat. Every patch of newly filled ink over **25 mm²** (filled spaces within 1.2 mm of each other count as one patch) is flagged. Fix each with a wipe, `ERASE` or a code-drawn replacement, or, after looking at it, accept it in `CLUMP_OK` with the reason (a cup of cocoa, a solid bow). An eye or a nose is far smaller and never flags.
8. **Snowflakes** drawn in code need **at least 3 mm between the branches of neighbouring arms** and every space they enclose ≥ 12 mm² at the size used, or they read as dark rosettes (pilot page 04). With the pilot geometry that means an arm length of at least 75 draft px (~15 mm). AI-drawn snowflakes with small inner details fill solid: erase them and draw them in code.
9. `potrace` → one smooth even-odd path per page.

`art/stats.json` records, per page, the stroke before and after, the number of spaces, the smallest space, the ink share, the clumps (and whether each was accepted) and each code-drawn snowflake's arm gap — the contact sheet prints the first few, and `process.py` prints a warning for an unreviewed clump or a tight snowflake.

## Art (cheap recipe only, FACTORY.md "Art quality")
- Prompt: the coloring-page block in `shop-profile/STYLE.md` + ` Subject: ` + the subject. **Generate at 896 × 1152** (Recraft flash refuses 1024 × 1365).
- Per page: `gen --flash --n 4` ($0.028), keep the best. At most one standard `gen` ($0.035) when all four are unusable; no `--pro`, and no `upscale`/`vectorize` (process.py scales the art for free).
- Ask for big simple shapes. Reject a draft with grey shading, hatching, fine needles or lettering: thickening cannot save it, and a swap to another draft is free.
- Budget: about **$0.03 a page**, so a 20-page bundle costs about $0.60.

## Checks (Designer, then QA)
`python3 gen.py --check` must print ALL CHECKS PASS:
- 20 distinct subjects and page names; `art/stats.json` covers all 20
- line art: median stroke ≥ 1.5 mm on every page; no designed space under 12 mm²
- no dark clumps: no patch of filled-in ink over 25 mm² that is not reviewed in `CLUMP_OK`; every code-drawn snowflake has ≥ 3 mm between its arms and no enclosed space under 12 mm²
- every PDF: right page count and size, **no embedded fonts and no extractable text**, under 20 MB
- every rendered page (200 dpi): ≥ 15 colourable spaces, each ≥ 10 mm²; art ≥ 12 mm from the paper edge; ink 8–32% of the page
- pinch points (spaces under 10 mm² where two thick lines meet, under 1 mm wide) are bounded, not banned: at most 16 a page and under 0.25% of the page's colourable area. They exist in hand-style line art at any resolution
- no two pages alike: 24 × 24 average hash of the trimmed art, at least 60 of 576 bits different
- ZIP holds exactly the two PDFs and README-LICENSE.txt; 4 listing images at 3000 × 2250; `contact-sheet.png` present
- listing: title ≤ 140 chars and leads with the search phrase; at most 3 words starting with 2 capitals (write "pdf"); at most one "&"; exactly 13 unique tags ≤ 20 chars; plain apostrophes, no HTML entities; description ends with exactly "Designed with the help of digital and AI tools, and checked by hand."; taxonomy id, price, `digital_file` = the ZIP; LISTING.md matches listing.json; PROMPTS.md present

Then look, don't only count:
- **every page of both PDFs** (`pdftoppm -r 60`) and `contact-sheet.png`: every subject reads at a glance, nothing clipped, no two pages alike
- every page at full size for AI faults: letters, signatures or watermarks, extra limbs, warped faces, grey smudges, a subject that is not what it claims
- **dark clumps or splats made by filling**: grass, leaves, snowflakes or berries that came out as solid black patches; stray strokes and broken fragments where two drawn things overlap (an antler crossing a tree)
- would a child colour it? Anything that needs a fine-tip pen is too detailed: swap the draft
- the listing images at Etsy thumbnail size (300 px wide)

## Listing images (3000 × 2250)
1. `1-thumbnail.png`: flat-lay on dark wood — one page half coloured, one fully coloured, two more fanned behind, coloured pencils and a mug; a plum band with the search phrase and a "20 pages" badge. The dark band stands out next to the usual white coloring-page results.
2. `2-page-grid.png`: all 20 real pages, numbered, with their names beside them.
3. `3-colored-mockup.png`: printed pages coloured in, a "bold lines, big spaces" card and a circular close-up of the real line weight.
4. `4-formats.png`: US Letter and A4 tagged, what's in the files.

The coloured examples must be the real pages' own regions (`colorize.py` fills `art/mask`), never separate artwork, and the listing says the files are black and white line art.

## Etsy
- Category: Books, Movies & Music > Books > Coloring Books, `taxonomy_id` **339** (`python3 tools/etsy.py taxonomy coloring`; the other match, 6513, is Food Coloring).
- Type digital, who made "i_did", when made "2020_2026", not a supply. Pilot price **$3.99** (typical $2.49–$3.49, median ~$2.99 (RankHero est.), so $3.99 for 20 pages with mockups).
- Tick Etsy's AI-assisted disclosure: the line art starts from AI drafts.
- Licence: personal use, unlimited prints for the buyer's own home, family and classroom; no resale, sharing, print-on-demand or AI training.

## Reuse
For another theme (mushroom & woodland, spring garden, Halloween), copy the folder, replace `subjects.json`, generate new drafts into `art/raw/`, update `picks.json`, `README-LICENSE.txt`, the titles in `thumbs.js` and the listing, pick 1–2 pages for `colorize.py`, and run `gen.py`. Everything else carries over unchanged.
