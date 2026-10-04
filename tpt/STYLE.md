# TpT style: Hudson Beat (Brian Lotze's store)

This is the house look for every item in the owner's TpT music line. It comes from the four covers on https://www.teacherspayteachers.com/store/brian-lotze (see research/tpt-music-2026-10-04.md, section 5). Those covers are monochrome: black line art on white, a tall condensed bold all-caps title stacked and centred under the logo, a light condensed subtitle, lots of white space, no borders and no photos.

We copy the look, not the artwork. The speaker/helmet logo belongs to the owner, and we don't have the file. Never redraw it. The owner named the music brand **Hudson Beat** (4 Oct 2026). The brand mark is "HUDSON BEAT" set in type. The copyright holder stays Brian Lotze.

The reference build is `tpt/001-halloween-color-by-note/gen.py`. Reuse its CSS and page functions.

## 1. Fonts

All fonts are SIL OFL 1.1 and live in `tpt/fonts/`, with their licences. Load them with `@font-face` from those files; never use system fonts. Chromium embeds subsets in every PDF, and `gen.py --check` confirms this with `pdffonts`.

| Use | Font | Notes |
|---|---|---|
| Titles, labels, tags, bands | **Oswald 700**, ALL CAPS | Close to the owner's condensed caps (Bebas/Oswald look). Tracking +0.01em for titles, +0.08–0.32em for small caps lines. |
| Subtitles | **Oswald 300**, sentence case | Matches the owner's light condensed subtitle ("Presentation"). |
| Small caps labels (colour names, table heads) | Oswald 500, caps | |
| Body text, instructions | **Source Sans 3** 400/600/700, plus italic | Readable at 9–12 pt for teachers and students. |
| Music notation | **Bravura** (SMuFL, Steinberg) | 1 em = 4 staff spaces. Use the glyph metrics in `001-…/notation.py`. Draw staff lines, stems and ledger lines as SVG lines. |

The machine has no condensed system fonts (fc-list shows only DejaVu, Liberation, Free*, Noto Emoji and others), so the woff2 files above are the source of truth.

## 2. Colour

- **The base is black (#000) on white.** All type, rules, line art and bands use it, as on the owner's covers. The owner's white-to-grey gradient is fine for high-school covers. For K-8 use flat white, which prints cleanly.
- **One accent per product**, used only for small things: the dots in the cover band, the "ANSWER KEY" tag, and section-heading dots. Pick it from the theme: Halloween #E8731A orange, Thanksgiving/fall rust, winter icy blue, and so on. Record it in the item's `gen.py` as `ACCENT`.
- **Activity content can be in full colour** where colour *is* the activity: answer keys, colour keys and preview images of coloured pictures. Store chrome (covers, headers, footers) never goes beyond black, white and the accent. On the cover, art uses only the accent and black, as in item 001, where the jack-o'-lantern is filled orange and black and the rest is left as uncoloured line art.
- Every worksheet must still work in black-and-white printing. Write colour names as words next to each swatch.

## 3. Cover / thumbnail (2000 × 2000 px PNG)

Render at 1000 × 1000 CSS px with deviceScaleFactor 2. The layout is the owner's: centred, mark/art on top, title block below.

```
 ┌───────────────────────────────────────┐
 │            H U D S O N   B E A T      │  store line: Oswald 500, 22px, +0.32em tracking, caps
 │                                       │
 │        ┌──────────────────────┐       │  hero art, ~55–60% of the height,
 │        │   line art (black +  │       │  black line art, at most the accent + black fill
 │        │   accent only)       │       │
 │        └──────────────────────┘       │
 │              HALLOWEEN                │  title line 1: Oswald 700 caps, ~66px
 │           COLOR BY NOTE               │  title line 2: Oswald 700 caps, ~112px (the big line)
 │   Rhythm values · Treble · Bass …     │  subtitle: Oswald 300, ~29px, sentence case
 │███ GRADES 1–5 · 3 LEVELS · 27 PAGES ███│  black band, white Oswald 500 caps, accent dots
 └───────────────────────────────────────┘
```

- No border round the square and no photos or mock-up props. White background.
- **Store line** "HUDSON BEAT" at the top of every cover and preview image. If the owner sends the logo file, it goes next to "HUDSON BEAT" in the same top position; never redraw it.
- The bottom band holds the grade range and the one or two strongest counts. Keep it to one line.
- The title must be readable at TpT's ~350 px thumbnail size: the big line is at least 10% of the image height.

The **PDF cover** (page 1, US Letter) uses the same stack: store line, art, title block, black band.

## 4. Interior pages (US Letter, 8.5 × 11 in)

- Margins are about 0.42 in at the top, 0.5 in at the sides and 0.38 in at the bottom. Nothing important goes within 0.35 in of the edge.
- **Header**: the product title in Oswald 700 caps (~25 pt) on the left with the item/page name under it in Oswald 300. On the right a black rounded tag ("LEVEL A") with a light label under it. Answer keys use the accent tag. A 2.2 pt black rule sits under the header.
- **Name / Date lines** on every student page.
- **Footer**: a 0.8 pt rule, then "© YEAR Brian Lotze · Hudson Beat · For single-classroom use" on the left and the page number on the right (plus cross-references such as "Answer key on page 13").
- Line art: 1.6 pt black outlines and rounded joins. Regions are big enough for crayons, at least about 40 pt across.
- Kid-friendly and not scary. No characters, brands or copyrighted songs.

## 5. Preview format

- **Preview PDF**: 4 pages taken from the real resource, each with a diagonal "PREVIEW" watermark (Oswald 700, 150 pt, 13% black, rotated −38°). Choose pages that show the range: one per level, plus one answer key.
- **3 preview PNGs**, 2000 × 2000, in the same frame as the cover: the store line, an Oswald 700 caps headline (one line, ~70–78px), a light subtitle, the content, and a black band with a short benefit line. Page shots get a 2 px black border and an 8 px hard black offset shadow (no blur), and a watermark when they show real pages. Suggested set:
  1. What's inside or the levels, side by side.
  2. A worksheet next to its answer key.
  3. A grid of every picture or card in the set.
- TpT shows the cover plus up to 3 more images, so the cover is image 1 and these follow in order.

## 6. Teacher pages and credits

Every resource includes:
1. **Cover** (page 1).
2. **Teacher notes**: how to use, a level/grade guide with page ranges, a standards-friendly description (National Core Arts Standards code where it really fits; keep claims modest), what's inside, and "No songs, lyrics or copyrighted characters are used."
3. A **student reference** page where the activity needs one.
4. The **last page, terms of use and credits**:
   - "© YEAR Brian Lotze. Hudson Beat by Brian Lotze. All rights reserved." One teacher's licence for their own students. Questions and credits name "Hudson Beat by Brian Lotze".
   - **You may**: copy for your own classes, post to a password-protected class site, and use with your students when you have a sub.
   - **You may not**: share with other teachers, schools or districts (additional licences are on TpT), post publicly, resell, or edit into a new product.
   - **Questions**: through the store's Q&A tab on TpT. We never print an email address unless the owner gives one.
   - **Credits**: original art; Bravura © Steinberg Media Technologies GmbH (OFL 1.1); Oswald and Source Sans 3 (OFL 1.1); any other font or asset with its licence.
   - The disclosure line: "Designed with the help of digital and AI tools, and checked by hand." It is required in the TpT description and is also printed here.

## 7. Files per item (`tpt/NNN-slug/`)

`<slug>.pdf`, `<slug>-PREVIEW.pdf`, `cover.png`, `preview-1..3.png`, `UPLOAD.md`, and `gen.py`, which builds everything. `gen.py --check` verifies the data, keys, page sizes, embedded fonts and files. `build/` holds intermediate HTML and can be regenerated. The renderer is shared: `tpt/tools/render.js`, run with `NODE_PATH=$(npm root -g)`.

## Open question for the owner

- Should the speaker/helmet logo appear next to "HUDSON BEAT" on covers? If so, send the logo file and we will place it beside the store line.
