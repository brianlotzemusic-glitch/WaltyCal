# Prompts — 030 Mushroom Clipart

Recraft via `tools/imagegen.py`, cheap recipe only (FACTORY.md "Art quality", formats/clipart.md): one `gen --flash --n 4 --size 1024x1024` per design ($0.028), the best draft kept, then `removebg` ($0.01) and `upscale` ($0.004) on the kept draft. No standard re-rolls, no `--pro`, no `vectorize`, no mockup photo (Etsy 22 Oct 2026 rules: photo 1 is a flat preview of the real files).

**Spend (log/image-spend.csv, 22 Oct 2026):** 12 flash sets $0.336 + 12 removebg $0.120 + 12 upscale $0.048 = **$0.504** (504 credits, $0.042 per design). Recraft balance before 1,884 credits, after 1,380.

Drafts not used were left in the session scratchpad. Committed: kept drafts (`art/raw/`) and their removebg masks (`art/alpha/`, alpha channel only). `art/up/` is not committed; rebuilding costs 12 x $0.004.

No per-design colour fixes or boxes were needed in process.py (all dicts empty). Note for the next clipart set: removebg returns RGBA; keep only its alpha channel (`getchannel("A")`) in `art/alpha/` because process.py reads it as mode L.

## Base prompt (style bible clipart line, year-round, mushroom colours)

> Woodland mushroom clipart, flat vector illustration style with clean dark plum outlines and flat colours, true-to-life mushroom colours, limited palette: fly agaric red, golden chanterelle orange, warm brown, tan, lilac, moss green, fern green, cream, soft gold, deep plum; crisp edges, one isolated subject centred on a plain pure white background, no text, no lettering, no frame, no ground shadow, no background scenery, cozy and a little whimsical.

Each prompt = base + ` Subject: ` + the subject below. Original designs only: no brand, character or text.

| Design | Subject | Draft kept |
|---|---|---|
| 01 Fly agaric toadstool | a single fly agaric toadstool, bright red domed cap with white warty spots, white gills under the cap edge, a thick pale cream stem with a white skirt ring, a small bulbous base | #4 of 4 (flash) |
| 02 Morel | a single morel mushroom, an upright honeycomb-pitted conical cap in warm tan-brown with dark pits, a short pale cream hollow stem | #2 of 4 (flash) |
| 03 Chanterelle cluster | a cluster of three golden-orange chanterelle mushrooms, funnel-shaped wavy caps with ridged forked undersides, apricot yellow-orange, tapering stems | #3 of 4 (flash) |
| 04 Porcini | a single porcini mushroom, a plump smooth chestnut-brown cap, a thick cream-coloured swollen stem with a faint net pattern, a pale sponge underside at the cap edge | #2 of 4 (flash) |
| 05 Oyster mushroom cluster | a shelf-like cluster of overlapping oyster mushrooms, smooth fan-shaped caps in soft grey-lilac and dove grey with cream gills underneath, joined at a short stub | #4 of 4 (flash) |
| 06 Puffball | a round puffball mushroom with a short stem base, creamy tan skin covered in tiny soft brown speckled warts, with one small puffball beside it | #4 of 4 (flash) |
| 07 Amethyst deceiver trio | three small amethyst deceiver mushrooms of different sizes, rich lilac-purple caps and slender lilac stems, fading to paler lilac at the cap centres | #4 of 4 (flash) |
| 08 Turkey tail bracket | a stack of overlapping turkey tail bracket fungi, thin wavy fan-shaped shelves with concentric bands of rust brown, teal blue-grey, tan and cream, cream edges | #3 of 4 (flash) |
| 09 Mushroom with ferns | a small brown-capped mushroom with a cream stem standing between two curling green fern fronds and a tiny moss tuft at its base | #3 of 4 (flash) |
| 10 Toadstools with oak leaves | two red spotted toadstools, one tall and one small, with two green oak leaves and two brown acorns tucked at their base, arranged as a compact group | #3 of 4 (flash) |
| 11 Honey fungus cluster | a tight cluster of five honey fungus mushrooms of different sizes, honey-yellow and amber caps with tiny dark scales at their centres, slim cream stems with rings, joined at the base | #3 of 4 (flash) |
| 12 Parasol mushroom | a single tall parasol mushroom, a wide umbrella-shaped cap in cream with warm brown shaggy scales and a brown centre knob, a long slender stem with a double ring, a bulbous base | #4 of 4 (flash) |
