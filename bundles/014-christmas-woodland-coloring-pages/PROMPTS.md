# Prompts — 014 Christmas woodland coloring pages

Recraft via `tools/imagegen.py`, cheap recipe only (FACTORY.md "Art quality"): one `gen --flash --n 4 --size 896x1152` per page ($0.028), the best draft kept. One page (12, wreath) needed the single allowed standard re-roll ($0.035) because all four flash drafts were too detailed or had grey smudges. No `--pro`, no upscale or vectorize: `process.py` scales, thickens, closes and traces the line art locally for free.

**Spend:** 20 × $0.028 + 1 × $0.035 = **$0.595** (log/image-spend.csv, 5 Oct 2026; about $0.03 per page). Recraft balance before: 5,477 credits.
**QA round 1:** + 1 flash re-roll for page 15 ($0.028, the last line in log/image-spend.csv), so **$0.623** in all. Pages 4, 18 and 19 were fixed in code for free.

Drafts not used were left in the session scratchpad, not committed; the chosen drafts are in `art/raw/` (stored as greyscale PNG).

## Base prompt (style bible line for coloring pages, shop-profile/STYLE.md)

> Coloring book page, bold and easy style for kids and adults: thick smooth uniform black outlines on pure white, line art only, no shading, no gray, no solid black areas, no hatching, no texture, no text, no border, large simple closed shapes with big spaces to color, no tiny details. Cozy, a little whimsical woodland in winter.

Each prompt = base + ` Subject: ` + the subject below.

| Page | Subject | Draft kept |
|---|---|---|
| 01 Fox in a scarf | a cute fox sitting in the snow wearing a knitted striped scarf, two pine trees and a few big simple snowflakes behind, snowy ground, full page composition | #1 of 4 (flash) |
| 02 Owl on a snowy pine | a round fluffy owl perched on a snowy pine branch with pine cones, a big crescent moon and a few chunky stars behind, full page composition | #3 of 4 (flash) |
| 03 Moonlit deer | a gentle deer stag with simple antlers standing in a snowy forest clearing under a big full moon, a few pine trees and chunky stars, full page composition | #3 of 4 (flash) |
| 04 Mushrooms in snow | a cluster of big spotted toadstool mushrooms with snow on their caps, small ferns and a few fallen leaves around them on snowy ground, chunky snowflakes, full page composition | #3 of 4 (flash) |
| 05 Lantern-lit cabin | a small cozy log cabin in the snowy woods with a glowing lantern hanging by the door, smoke curling from the chimney, a pine tree on each side, full page composition | #1 of 4 (flash) |
| 06 Hedgehog with a mug | a cute hedgehog wrapped in a blanket holding a big mug of hot cocoa with marshmallows, sitting on a snowy log, full page composition | #4 of 4 (flash) |
| 07 Robin on holly | a plump robin bird perched on a sprig of holly with big leaves and round berries, a few chunky snowflakes around, full page composition | #4 of 4 (flash) |
| 08 Bunny and sled | a fluffy bunny rabbit wearing mittens and a knitted hat pulling a wooden sled with a small pine tree on it through the snow, full page composition | #4 of 4 (flash) |
| 09 Bear with a gift | a friendly round bear sitting in the snow hugging a big wrapped gift box with a bow, pine trees behind, full page composition | #2 of 4 (flash) |
| 10 Squirrel and pinecones | a cheerful squirrel with a big fluffy tail sitting on a snowy branch holding an acorn, large pinecones hanging nearby, full page composition | #2 of 4 (flash) |
| 11 Walking home with a tree | a cute badger in a knitted hat carrying a small Christmas tree home through a snowy forest path, full page composition | #3 of 4 (flash) |
| 12 Woodland wreath | a round Christmas wreath made of big pine branches, large pinecones, holly leaves, berries and a big ribbon bow at the bottom, centered, full page composition | standard re-roll (flash drafts too detailed) |
| 13 Snowman and birds | a happy snowman with a scarf and a knitted hat in the woods, two little birds sitting on his stick arm, pine trees behind, full page composition | #2 of 4 (flash) |
| 14 Mouse by candlelight | a little mouse in a nightcap reading a big book beside a candle inside a cozy tree hollow, a few acorns on the floor, full page composition | #1 of 4 (flash) |
| 15 Birdhouse in snow | a wooden birdhouse on a post with a snowy roof, two small round chickadee birds, a pine branch and berries, chunky snowflakes, full page composition | round-1 flash re-roll (was #3 of 4) |
| 16 Tree in the clearing | a decorated Christmas tree standing in a snowy forest clearing with a big star on top, large round ornaments and gift boxes underneath, full page composition | #4 of 4 (flash) |
| 17 Fireplace stockings | a cozy stone fireplace with a crackling fire, three Christmas stockings hanging from the mantel, pine garland and a candle on top, full page composition | #4 of 4 (flash) |
| 18 Reindeer with a wreath | a sweet reindeer with big antlers wearing a holly wreath around its neck, standing in snow with pine trees behind, full page composition | #2 of 4 (flash) |
| 19 Hare under the moon | a wild hare sitting in a snowy meadow looking up at a big crescent moon and chunky stars, frosted grass and a pine tree, full page composition | #2 of 4 (flash) |
| 20 Woodland gnome | a cute woodland gnome with a long beard and tall pointed hat holding a lantern, sitting beside big snowy mushrooms, full page composition | #2 of 4 (flash) |

Page 12 standard re-roll subject: "a simple round Christmas wreath with a few big smooth pine bough shapes, three large simple pinecones drawn as big rounded scales, big holly leaves, a few large round berries and a big ribbon bow at the bottom, centered, full page composition".

## Checked by hand
Every kept draft was viewed at full size before processing and every final page after (both pdfs): no text, letters or signatures, no watermarks, no extra limbs, no grey shading left. Draft #2 of page 11 was swapped for #3 (the badger's face was hidden behind the tree it carried) and draft #4 of page 15 for #3 after the first full render: its pine needles were too fine for bold & easy. Page 4's five small snowflakes filled solid during cleanup and looked like ink stains, so they were erased and replaced by five chunky code-drawn snowflakes (`SHAPES` in process.py).

QA round 1: page 15's draft #3 had 1 mm pine needles, an odd mask-like eye on the right-hand bird and a lamppost-like post, so it was re-rolled once with flash: the new draft has two matching round birds on a snowy birdhouse, a holly sprig with big berries and a plain post. Its two AI snowflakes filled solid and were replaced by code-drawn ones. Page 4's three tight snowflakes were redrawn larger (≥ 3 mm between the arms), and a crowded fern clump beside the right mushroom was cleared to one stem with big leaves. Page 18's stray antler stroke, the tick that closed a black wedge and the lone ink tick in the tree were wiped and the cut lines redrawn. Page 19's four grass-tuft splats were wiped, the hill line behind them redrawn, and two outlined snow mounds drawn in code.
