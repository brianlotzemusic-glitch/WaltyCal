# Format spec: printable picture bingo (party game, PDF)

First built 3 Oct 2026 (pilot: `bundles/010-woodland-christmas-bingo`; updated after QA round 1: tie rule, marker spec, image consistency). A digital download: the buyer prints the PDFs at home. Read with FACTORY.md "Product formats" and "Art quality". The same pipeline fits other party printables (scavenger hunts, "I spy", memory games) with new page layouts.

## Folder: `bundles/NNN-slug/`
| File | What |
|---|---|
| `gen.py` | Runs every step below, builds the ZIP, then the checks. `python3 gen.py --check` re-runs only the checks |
| `icons.py` | The icons, drawn in code (shapely, 1000-unit box, y down) as layers of (shape, fill, outline). Writes `icons/NN-name.svg` and `icons.json` |
| `cards.py` | Deals the cards with a fixed seed and asserts the uniqueness rules; writes `cards.json` (cards + proof). `--check` re-checks |
| `build.js` | HTML → PDF with Playwright/Chromium, once per paper size |
| `contact.js` | `contact-sheet.png`: every icon at 250 px and at about 1 in (96 px), with names, plus the FREE space |
| `thumbs.js` | `listing-images/` from the real PDF pages (rasterised with `pdftoppm`) |
| `fonts/` | OFL fonts (pilot: Fraunces 700/900, Nunito 400/700/800), embedded as data URIs so Chromium can load them |
| `README-LICENSE.txt` | Files, page map, how the cards are dealt, printing tips, personal-use licence |
| `<slug>-printable.zip` | Buyer file: both PDFs + README-LICENSE.txt, nothing else |
| `LISTING.md`, `listing.json` | Listing copy (same fields as the cut-file bundles) |
| `PROMPTS.md` | Only if AI images were used |

## Game content
- **Icon pool larger than the card.** A 5×5 card with a FREE centre holds 24 pictures. Use a pool of **30** (at least 26). With exactly 24, every card holds the same set and everyone wins a blackout on the same call.
- **Icons**: original, code-drawn, in the shop palette only (plum #2c1b36, pine #2f4a3a, berry #8b2f3c, gold #e8c97a, cream #f1e6cf, white). Light fills (gold, cream, white) get a plum outline (22 units) so they read on white paper. Each icon is scaled to fill an 860-unit box (`fit()`), so all icons look the same size on the card. Each must read as what it is at **0.8 in** (the icon size in a US Letter cell of about 1.2 × 0.9 in; `contact-sheet.png` shows it at 77 px = 0.8 in at 96 DPI), for kids and adults, carry the same visual weight as its neighbours (mostly-white icons such as the snowman get a heavier 40-unit outline), and no two may be confusable (the FREE space must not look like any icon: the pilot uses three small stars + the word FREE, not a moon, because the moon is an icon).
- **Cards**: 30 cards. `cards.py` must assert: (1) no two cards share the same set of icons; (2) no two share a layout; (3) no two share a winning line (row, column or diagonal, as a set); (4) every icon is on the same number of cards (30 × 24 / 30 = 24). Deal: 6 rounds, each shuffles the pool into 5 groups of 6, and each group is what one card leaves out.
- **Ties.** Rule 3 only stops two players winning on the *same line*; it does not stop ties. QA simulated 20,000 games per setting with the pilot cards: about 22% of 30-player "any line" games (17% with 10 players) and about 54% of blackouts have 2 or more winners on the same call. The instructions page, README and description must include a tie rule (pilot: "Two BINGOs on the same call: both win, or play one quick 'any line' round"). Never claim ties are rare.
- Each card: a title ("Woodland Christmas" + vertical B-I-N-G-O panel on the left), a card number ("Card 07"), a 5×5 grid, FREE centre.

## PDF layout (both sizes, same page order)
| Paper | Page size | Card (half page) | Grid cell |
|---|---|---|---|
| US Letter | 612 × 792 pt (215.9 × 279.4 mm), portrait | 197.9 × 124.2 mm | about 30.5 × 23 mm |
| A4 | 595 × 842 pt (210 × 297 mm), portrait | 192 × 133 mm | about 29.5 × 25 mm |

- Two cards per page, stacked, with a dashed "cut here" line on the middle of the page. Keep at least 9 mm from every outer edge (home printers clip about 6 mm).
- Page order (20 pages): 1 instructions (what's inside with page numbers, getting ready, how to play, 5 ways to win with mini diagrams, printing tips, party ideas, licence line); 2–16 cards; 17–18 calling cards (3 × 5 per page, dashed cut lines, icon about 31 mm + name); 19 caller's checklist (all icons with names and tick circles); 20 markers: **opaque, high-contrast filled discs** (pilot: solid gold #e8c97a, 0.6 mm plum ring, thin cream inner ring), **22 mm**, 8 × 9 = 72 per page, with **no game icon** on them (a covered picture must look covered, for the player and the caller). A 22 mm disc covers the picture, not the whole cell.
- Print-friendly: white page, white cells, no full-bleed fills; colour only in the icons, the thin plum frames and the titles. FREE cell may have a very light cream tint (#fbf6ea). The marker page is the one exception to light ink: solid discs, because a covered cell must stand out.
- **Marker maths in the copy:** a blackout needs 24 markers per player, so one page of 72 covers 3 players. Page 1, README and description must say so ("72 markers, enough for 3 players at blackout; print the page once for every 3 players, or use candy or buttons").
- Fonts embedded (check with `pdffonts`); file size well under 20 MB (pilot: 1.6 MB each; icons are reused with `<symbol>`/`<use>`, and paths are rounded to whole units).

## Checks (Designer, then QA)
`python3 gen.py --check` must print ALL CHECKS PASS:
- both PDFs: the right page count (20) and size (Letter 612×792 pt, A4 595×842 pt), all fonts embedded
- `cards.py --check`: rules 1–4 above
- ZIP has exactly the two PDFs + README-LICENSE.txt
- 4 listing images at 3000×2250; `contact-sheet.png` present
- copy: no "ties are rare" claim; tie rule ("both win") and the marker count are in the description and README
- listing: title ≤140 chars, leads with the main keyword, no more than 3 words starting with 2 capitals (write "pdf", not "PDF"); exactly 13 unique tags ≤20 chars; no HTML entities (`&#39;`, `&amp;`); description ends with exactly "Designed with the help of digital and AI tools, and checked by hand."; `taxonomy_id` 1350; price; `digital_file` = the ZIP

Then look, don't only count:
- `contact-sheet.png`: every icon recognisable at the small size; no two look alike; FREE is clearly not an icon
- render pages with `pdftoppm -r 90 -png -f 1 -l 2 <pdf> out` and look at page 1, one card page, the calling cards, checklist and markers, in **both** sizes: nothing clipped or overflowing (US Letter is 17.6 mm shorter than A4; the instructions page is the tightest), cut line centred, card numbers in order
- the page numbers on page 1 and in README match the PDF
- **listing images show only what the file contains**: the markers, page layouts and cards in the images must be the real ones (render them from the PDF pages; draw markers exactly as printed)
- any calling card shown in an image is one of the covered pictures, and only called pictures are covered (pilot: image 1 covers row 3 of Card 01 and shows Snowflake + Squirrel; image 4 covers the diagonal of Card 07 and shows Pine Tree)

## Listing images (3000×2250, same names as other bundles)
1. `1-thumbnail.png`: printed cards on a "table" (code-drawn wood texture), one card with the printed gold markers on a winning line, the calling cards for covered pictures, spare markers on the table (never on a card), a big two-tone title band ("Christmas Bingo"), a "30 unique cards" badge. It must stand out next to the top results for the keyword, which are mostly flat red/green on white: the dark plum band + wood table does that.
2. `2-whats-included.png`: the real pages (instructions, cards, calling cards, checklist, markers) with labels, plus 4 feature tiles (players, ages, fairness, reusable).
3. `3-formats.png`: US Letter and A4 pages tagged, with print/format bullets.
4. `4-color-ideas.png` (name kept for the uploader): all 30 pictures with names + a card close-up and "how to play" in 3 steps.

## Etsy
- Category: Paper & Party Supplies > Party Supplies > Party Favors & Games > Party Games, `taxonomy_id` **1350** (`python3 tools/etsy.py taxonomy "party games"`). The other match for "bingo", 2392 (Toys & Games > Board Games > Bingo), is for physical games; don't use it.
- Type digital, who made "i_did", when made "2020_2026", not a supply.
- Licence: personal use, unlimited prints for the buyer's own family, party or classroom; no resale or sharing.
- Timing: list seasonal games at least 6 weeks before the peak (Christmas bingo: by mid-November).

## Reuse
For another theme (Halloween, Easter, baby shower, winter), copy the folder, replace the icon functions in `icons.py` and the titles/text in `build.js` and `thumbs.js`, keep `cards.py` as it is (change the pool size only with care: the 6-round deal needs pool = 30 and 6 left out per card), and run `gen.py`.
