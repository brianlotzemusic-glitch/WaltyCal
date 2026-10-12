# Listing — Raven & Mistletoe Ornaments SVG bundle

**Title (≤140 chars, 132, one '&')**
Raven Ornament SVG Bundle, Gothic Christmas Raven & Mistletoe Ornaments, Crow Laser Cut Files for Cricut, Silhouette (svg, dxf, png)

**Price:** $4.00 (standard 6-design bundle price until stats exist)

**Category:** Craft Supplies & Tools > Patterns & How To > Craft Machine Files > Cutting Machine Files (taxonomy 12394)
**Type:** Digital · **Who made it:** I did · **When:** 2020–2026 · **What is it:** A finished product
**Creation method:** tick the AI-assisted / generative AI disclosure if Etsy shows it

**Description**
Gothmas for the tree: six original raven and mistletoe ornament cut files, moody and elegant rather than scary.

Each ornament has a bold raven silhouette as the star: a raven perched on a bare branch under a crescent moon with a sprig of mistletoe, a classic bauble with a perched raven, a crescent moon and stars cut out of it, a raven perched on top of a gothic lantern with a candle glowing in each arched window, two ravens meeting beak to beak under mistletoe in a gothic arched window, a raven sitting on a crescent moon, and a raven perched inside a mistletoe wreath of leaves and berries. Solid bird shapes keep every design easy to read, even small on the tree.

Each design is a single-layer, single-path cut file with a hanging loop built in, so no slicing, welding or cleanup is needed. Stars, moons, mistletoe and candle flames are attached, so nothing falls out.

WHAT'S INCLUDED
• 6 designs: Moonlit Raven Ornament, Raven Bauble Ornament, Raven Lantern Ornament, Gothic Window Ravens Ornament, Raven on the Moon Ornament, Mistletoe Wreath Raven Ornament
• SVG — Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
• DXF — Silhouette Studio Basic Edition, laser software (inches)
• PNG — transparent background, 1800 px on the longest side (6 in at 300 DPI)

SIZING TIP
Default size is about 6 in on the longest side; resize freely with the proportions locked. The raven toes and mistletoe stems are the thinnest parts (about 0.08 in at 6 in), so we recommend 4 in or larger for cardstock, felt and vinyl and 4.5 in or larger for laser-cut wood or acrylic. Do a test cut on a new material first.

LICENSE
Personal use, plus small-business use on up to 500 finished physical items per design. Please don't share or resell the digital files.

THIS IS A DIGITAL DOWNLOAD
No physical item will be shipped. Files are available right after purchase in a single ZIP.

Designed with the help of digital and AI tools, and checked by hand for clean cuts.

**13 tags (each ≤20 chars)**
raven svg, crow svg, mistletoe svg, gothic christmas, raven ornament, christmas ornament, gothmas, laser cut ornament, cricut files, goth christmas svg, creepy christmas, ornament svg, bird svg

**Images (upload in this order):** listing-images/1-thumbnail.png, listing-images/2-whats-included.png, listing-images/3-formats.png, listing-images/4-color-ideas.png
**Digital file:** raven-mistletoe-ornaments-svg.zip

## Notes / checks before publishing
- Original designs drawn in code (gen.py: our own perched raven, mistletoe sprig and leaf wreath, lantern, gothic arch, moon and wreath geometry; helpers reused from 021, 020, 008 and 006). AI cost $0, no Recraft calls. Subject only (raven / gothic Christmas / mistletoe ornaments) from the queue; no other seller's design, text, brand or character. No text in any design; no literary quotes (no "Nevermore").
- Lesson from _rejected/022 (gnome face): no code-drawn faces or figures that rely on thin cut lines. Every raven is a solid silhouette (beak, throat hackles, wedge tail, fingered wingtips carry the read); the only cut detail on a bird is a round eye, about 0.18 in across at 6 in (30 units). Window, star, lantern and loop cut-outs are all wider than 0.12 in. Self-checked at about 20% (120 px cells): all six read as ravens; mistletoe reads as a sprig with berries.
- Round 2 (QA fixes): mistletoe redrawn as a real sprig (stem forking into two pairs of long oval leaves, three round berries clustered in the fork) in 01, 04 and the 06 wreath; the round-1 paddle leaves read as a flower or bow. 01 branch ends trimmed inside the ring and the hanging star dropped (it crowded the sprig). 02 redrawn: the flying bird read as a dove, and a bolder flying raven (profile and seen from below) still read as a generic bird/eagle in self-check, so 02 is now a big perched raven on its branch with a crescent moon and stars cut out (a cut-out sprig was too fussy and was dropped). 03 raven enlarged (x1.42) and the floating sprig dropped (under the roof it read as a bat). 06 redrawn: smooth ring band with evenly spaced oval leaves (alternating out/in, none inside round the bird) and five three-berry clusters, raven perched on a branch across the bottom, clear of every leaf. 05 unchanged (identical SVG/DXF).
- Files are scaled to about 5.98 in on the longest side; copy says "about 6 in".
- Thinnest material is about 13 units (0.08 in at 6 in): raven toes and mistletoe stems, enforced by finish(). Smallest cut-out 807 units² (a star in 02); every cut-out is at least 600.
- Lead photo is a code-drawn "hanging on a bough" scene (05, 04, 01), not a photo or an AI mockup; a real lifestyle mockup is still missing (same as 008, 020, 021).
- Rebuild: `python3 gen.py` → `NODE_PATH=$(npm root -g) node render.js bundle/SVG 1800 bundle/PNG` → zip `bundle/` → `NODE_PATH=$(npm root -g) node thumbs.js`; verify with `python3 gen.py --check` (unzips the ZIP into bundle/ if it is missing). `preview.py <out.png>` makes a low-res contact sheet.
- Do a test cut of 03 (lantern candles and raven toes) at 4 in in cardstock when hardware allows.
