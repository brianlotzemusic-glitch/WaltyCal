# Format spec: printable wall art (PDF + JPG, AI raster art)

First built 21 Oct 2026 (pilot: `bundles/027-winter-botanical-wall-art`, set of 3 midnight-blue botanical prints, $5.00). A digital download: the buyer prints at home or at a print shop. Read with FACTORY.md "Product formats" and "Art quality".

## Folder
`art/` (AI images; art/unified/*.png kept; the 4x originals and drafts deleted to save space), `prep_art.py` (one shared flat background colour across the set), `mk.py` (JPGs and PDFs per ratio), `listing_images.py`, `gen.py` (ZIP + checks), `README-LICENSE.txt`, `LISTING.md`, `listing.json`, `PROMPTS.md`, `QA.md`.

## Art
- Cheap recipe per print: `gen --flash --n 4 --size 896x1152` ($0.028), pick one, `upscale` ($0.004, 3186x4096). A second upscale is refused (size cap), so 24x36 is an enlargement; say so in the README and listing.
- Prompt for ONE centred subject on a plain flat colour with generous margin and no frame/text. A flat background lets `prep_art.py` unify the set and lets any ratio be made by padding with the colour.
- Look at the three side by side: same palette, similar subject size, no garbled detail.

## Files (one ZIP, must be under 20 MB: tools/etsy.py uploads a single digital file)
- JPG, 5 ratios x each print: 2:3 4400x6600 (up to 24x36), 3:4 3300x4400 (18x24), 4:5 3200x4000 (16x20), 11x14 3300x4200, ISO 3508x4961 (A3 at 300 DPI, A2 enlarged). Quality 66, 4:2:0, DPI tag 300.
- PDF, one per ratio, one page per print, page = the largest print size, image at about 80-130 DPI (quality 68). Without this cut the ZIP is about 40 MB.
- README-LICENSE.txt with the size list, quality note, printing tips and personal-use licence.
- Spec said "largest size at least 24x36 in": met as an enlargement; do not claim true 300 DPI there.

## Checks
`python3 gen.py --check`: ZIP contents, size under 19.8 MB, every JPG's pixel size / 300 DPI tag / ratio, PDF page counts and sizes, listing rules (title, 13 tags, disclosure, taxonomy, price), 4 listing images 3000x2250. Then look: crop at 100%, pages, listing images.

## Listing images (3000x2250)
1. Room mockup, code-drawn (wall, 3 frames showing the real art, shelf, candle, vase), title band. Cheap, honest; an AI lifestyle photo would cost about $0.03 more.
2. What you get (3 prints, file counts). 3. Ratios and sizes. 4. Close-ups.

## Etsy
Art & Collectibles > Prints > Digital Prints, `taxonomy_id` 2078. Digital, who made "i_did", when made "2020_2026", not a supply. Disclosure line: "Designed with the help of digital and AI tools, and checked by hand."
