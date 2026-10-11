# Listing — Woodland Reindeer & Stag Ornaments SVG bundle

**Title (≤140 chars, 126, one '&')**
Reindeer Ornament SVG Bundle, Woodland Stag & Deer Christmas Ornaments, Laser Cut Files for Cricut, Silhouette (svg, dxf, png)

**Price:** $4.00 (standard 6-design bundle price until stats exist)

**Category:** Craft Supplies & Tools > Patterns & How To > Craft Machine Files > Cutting Machine Files (taxonomy 12394)
**Type:** Digital · **Who made it:** I did · **When:** 2020–2026 · **What is it:** A finished product
**Creation method:** tick the AI-assisted / generative AI disclosure if Etsy shows it

**Description**
Cosy woodland Christmas: six original reindeer and stag ornament cut files for the tree, gift tags and the window.

Each ornament has a deer as the star: a front-facing stag head with a holly sprig, a reindeer leaping over snowy pines under a crescent moon and a hanging star, a stag standing in a pine wood, a reindeer head wrapped in a knitted scarf, a classic bauble with a stag cut out of it among snowflakes, and two reindeer facing each other across a snowy pine in a scalloped frame. Big branching antlers keep every design easy to read, even small on the tree.

Each design is a single-layer, single-path cut file with a hanging loop built in, so no slicing, welding or cleanup is needed. Stars, moons and trees are attached, so nothing falls out.

WHAT'S INCLUDED
• 6 designs: Stag Head Ornament, Leaping Reindeer Ornament, Woodland Stag Ornament, Reindeer with Scarf Ornament, Stag Bauble Ornament, Reindeer Pair Ornament
• SVG — Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
• DXF — Silhouette Studio Basic Edition, laser software (inches)
• PNG — transparent background, 1800 px on the longest side (6 in at 300 DPI)

SIZING TIP
Default size is about 6 in on the longest side; resize freely with the proportions locked. The antler tines and legs are the thinnest parts (about 0.08 in at 6 in), so we recommend 4 in or larger for cardstock, felt and vinyl and 4.5 in or larger for laser-cut wood or acrylic. Do a test cut on a new material first.

LICENSE
Personal use, plus small-business use on up to 500 finished physical items per design. Please don't share or resell the digital files.

THIS IS A DIGITAL DOWNLOAD
No physical item will be shipped. Files are available right after purchase in a single ZIP.

Designed with the help of digital and AI tools, and checked by hand for clean cuts.

**13 tags (each ≤20 chars)**
reindeer svg, stag svg, deer svg, christmas ornament, reindeer ornament, deer ornament svg, antler svg, laser cut ornament, cricut files, woodland christmas, stag head svg, christmas svg, ornament svg

**Images (upload in this order):** listing-images/1-thumbnail.png, listing-images/2-whats-included.png, listing-images/3-formats.png, listing-images/4-color-ideas.png
**Digital file:** woodland-reindeer-stag-ornaments-svg.zip

## Notes / checks before publishing
- Original designs drawn in code (gen.py: our own deer, antler, holly, pine and frame geometry; helpers reused from 020, 008 and 006). AI cost $0, no Recraft calls. Subject only (reindeer / stag Christmas ornaments) from the research brief; no other seller's design, text, brand or character. No text in any design; no named reindeer (no Rudolph, red nose or sleigh-team references).
- Files are scaled to about 5.98 in on the longest side (viewBox pad cut from 12 to 2 units after QA's 020 note); copy says "about 6 in".
- Thinnest material is about 13 units (0.08 in at 6 in): antler tines and legs, enforced by MINW and finish(). Smallest cut-out 679 units² (scarf stripe in 04); every cut-out is at least 600.
- Round 2 (QA fixes): 01 redrawn (round eyes, muzzle line, holly sprig of two big spiky leaves and three berries cut into the chest, star between the antlers); 04 redrawn as a round-frame ornament with a hanging loop (reindeer head in profile, ribbed scarf knotted at the throat with a fringed end blowing out); 06 redrawn (deer smaller and fully inside the frame, legs spread and thicker, a pine between them, snowflakes cut into the snow). All six now hang from a loop. Lead image recomposed with 05, 02 and 03 filling the frame.
- Lead photo is a code-drawn "hanging on a bough" scene, not a photo or an AI mockup; a real lifestyle mockup is still missing (same as 008 and 020).
- Rebuild: `python3 gen.py` → `node render.js bundle/SVG 1800 bundle/PNG` → zip `bundle/` → `NODE_PATH=$(npm root -g) node thumbs.js`; verify with `python3 gen.py --check` (unzips the ZIP into bundle/ if it is missing). `preview.py <out.png>` makes a low-res contact sheet.
- Do a test cut of 06 (smallest antlers) at 4 in in cardstock when hardware allows.
