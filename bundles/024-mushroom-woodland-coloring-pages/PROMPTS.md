# Prompts — 024 Mushroom & woodland coloring pages

Recraft via `tools/imagegen.py`, cheap recipe only (FACTORY.md "Art quality", formats/coloring.md): one `gen --flash --n 4 --size 896x1152` per page ($0.028), the best draft kept. Page 20 needed one more flash batch with a new subject (the four "mushroom lantern" drafts were odd: a creature on the cap, a cap with little hands), so it became a mushroom teapot. No standard re-rolls, no `--pro`, no upscale or vectorize: `process.py` scales, thickens, closes and traces the line art locally for free.

**Spend:** 21 × $0.028 = **$0.588** (log/image-spend.csv, 13 Oct 2026; about $0.03 per page, under the $0.05-a-design cap). Recraft balance: 2,732 credits before, about 2,144 after.

Drafts not used were left in the session scratchpad, not committed; the chosen drafts are in `art/raw/` (stored as greyscale PNG).

## Base prompt (style bible line for coloring pages, shop-profile/STYLE.md, plus the mood)

> Coloring book page, bold and easy style for kids and adults: thick smooth uniform black outlines on pure white, line art only, no shading, no gray, no solid black areas, no hatching, no texture, no text, no border, large simple closed shapes with big spaces to color, no tiny details. Cozy, a little whimsical mushroom woodland, cottagecore, summer and autumn, no snow.

Each prompt = base + ` Subject: ` + the subject below.

| Page | Subject | Draft kept |
|---|---|---|
| 01 Mushroom cottage | a cozy cottage made from one big spotted toadstool mushroom with a round door, two round windows and a little path, ferns and small mushrooms beside it, full page composition | #3 of 4 (flash) |
| 02 Frog on a toadstool | a happy round frog sitting on top of a big spotted toadstool mushroom, a few smaller mushrooms and broad leaves around the stem, full page composition | #1 of 4 (flash) |
| 03 Snail and mushrooms | a cute snail with a big spiral shell crawling past a cluster of tall mushrooms with smooth caps, a few clover leaves on the ground, full page composition | #1 of 4 (flash) |
| 04 Fox in the ferns | a cute fox curled up asleep among big simple fern fronds and two spotted mushrooms, full page composition | #1 of 4 (flash) |
| 05 Hedgehog and mushrooms | a round hedgehog with simple big spikes walking beside a cluster of chunky mushrooms and fallen autumn leaves, full page composition | #3 of 4 (flash) |
| 06 Moth and moon | a big moth with wide rounded wings and simple large wing patterns flying above tall mushrooms, a crescent moon and a few chunky stars, full page composition | #4 of 4 (flash) |
| 07 Mushrooms on a log | a cluster of big shelf mushrooms and round-capped mushrooms growing on a fallen mossy log, a few big leaves, full page composition | #3 of 4 (flash) |
| 08 Owl and toadstools | a round fluffy owl perched on a tree stump surrounded by big spotted toadstools, a crescent moon behind, full page composition | #2 of 4 (flash) |
| 09 Bunny under a mushroom | a fluffy bunny rabbit sheltering from the rain under a big mushroom cap like an umbrella, big simple raindrops, small puddle, full page composition | #3 of 4 (flash) |
| 10 Toadstool trio | three big spotted toadstool mushrooms of different heights with large round spots, big simple fern leaves and grass at their base, full page composition | #2 of 4 (flash) |
| 11 Foraging basket | a woven wicker basket full of big mushrooms of different kinds, a few large oak leaves and acorns beside it, full page composition | #1 of 4 (flash) |
| 12 Ladybugs on a toadstool | two big ladybugs climbing on a large toadstool mushroom, a daisy and broad leaves around it, full page composition | #2 of 4 (flash) |
| 13 Mouse under a toadstool | a little mouse sitting under a spotted toadstool holding an acorn, a small mushroom and a few big leaves beside it, full page composition | #3 of 4 (flash) |
| 14 Fawn in the glade | a sweet baby deer fawn with big simple spots lying in a forest glade among big mushrooms and ferns, full page composition | #3 of 4 (flash) |
| 15 Squirrel on a mushroom | a cheerful squirrel with a big fluffy tail standing on a huge flat mushroom cap holding an acorn, oak leaves around, full page composition | #3 of 4 (flash) |
| 16 Mushroom meadow | a ring of small round mushrooms in a meadow with a few big daisies and bluebell flowers, two butterflies above, full page composition | 3 of 4 (flash; #1 was picked first, but its bluebells and one daisy filled into black clumps) |
| 17 Wren on a mushroom | a small round wren bird perched on a big mushroom cap, berries and broad leaves around, full page composition | #2 of 4 (flash) |
| 18 Bear cub forager | a friendly round bear cub sitting in the forest holding a big mushroom, more mushrooms and ferns around, full page composition | #4 of 4 (flash) |
| 19 Mushroom jar | a big glass jar terrarium with a few mushrooms and ferns growing inside, sitting on a wooden table, simple shapes, full page composition | #1 of 4 (flash) |
| 20 Mushroom teapot | a cozy round teapot shaped like a big spotted mushroom with a teacup and saucer beside it on a small table, a few big leaves and small mushrooms, full page composition | 1 of 4 (flash re-roll with a new subject: the 4 'mushroom lantern' drafts were odd) |

Page 20's first batch used the subject "a tall glowing mushroom lamp lantern standing in the forest at night with fireflies drawn as simple round dots with rays, ferns and smaller mushrooms around, full page composition" (4 flash drafts, none kept). Page 16 was asked for as a "fairy ring"; the kept draft is a mound of mushrooms with daisies and bluebells, so it is named "Mushroom meadow".

## Checked by hand
Every draft was viewed in 4-up sheets and every processed page after cleanup at about 1/2 to 1/1 size: no text, letters or signatures, no watermarks, no extra limbs, no grey shading left. Draft choices favoured big shapes and few fine details (e.g. page 05's dotted-quill hedgehog over a spiky one whose quills were hair-thin).

Per-page fixes in `process.py` (all free, in code):
- 01 Mushroom cottage: two fern sprigs and the grass round their stems filled solid black, so they were wiped, the scraps erased, and the remaining outlined fern given a small outlined mound (`SHAPES`).
- 10 Toadstool trio: three curly ferns filled into black silhouettes and the spiky grass held fern scraps. Ferns and grass wiped; the stems carried down to a new ground line and 4 tufts of outlined grass blades drawn in code (each blade a closed shape, smallest space 54 mm²).
- 14 Fawn in the glade: a fern by the fawn's tail filled into a black splat; wiped, and the mushroom stem edge it hid redrawn. The two dark mushroom undersides (dense gills that filled) are accepted in `CLUMP_OK` as shade.
- 16 Mushroom meadow: draft #1 was picked first, but its bluebells and one daisy filled into black clumps; draft #3 (bigger daisies) has no clump.
- 19 Mushroom jar: a wire hook on the lid read as a drinking straw; wiped and the lid lines it crossed redrawn.
