# Prompts — 016 Nutcracker ballet clipart

Recraft via `tools/imagegen.py`, cheap recipe only (FACTORY.md "Art quality", formats/clipart.md): one `gen --flash --n 4 --size 1024x1024` per design ($0.028), the best draft kept, then `removebg` ($0.01) and `upscale` ($0.004) on the kept draft. No standard re-rolls, no `--pro`, no `vectorize`. The mockup reuses 015's blank flat-lay photo (`mockup/blank-flatlay.jpg`), so it cost nothing. Everything after the AI calls (cut-out, clean-up, trim to 3600 px, palette PNG, SVG line art, mockup compositing, listing images) is local and free.

**Spend (log/image-spend.csv, 9 Oct 2026):**
| Item | Calls | Cost |
|---|---|---|
| Flash drafts, 12 designs × 4 | 12 | $0.336 |
| `removebg` on the kept drafts (13: 04 was swapped from draft #2 to #1 after processing) | 13 | $0.130 |
| `upscale` on the kept drafts (13, same reason) | 13 | $0.052 |
| Mockup photo | 0 | $0 (015's blank flat-lay reused) |
| **Total** | | **$0.518** (518 credits) |

That is **$0.043 per design**, under the $0.05 target. Recraft balance before: 4,318 credits; after: 3,800.

Drafts not used were left in the session scratchpad, not committed. Committed: the kept drafts (`art/raw/`) and their removebg masks (`art/alpha/`, alpha channel only). The 4096 px upscales (`art/up/`) are not committed; rebuilding the art from scratch costs 12 × $0.004 (`imagegen.py upscale art/raw/X.png art/up/X.png`).

## Base prompt (style bible clipart line, shop-profile/STYLE.md)

> Christmas clipart, flat vector illustration style with clean dark plum outlines and flat colours, limited palette: nutcracker red, royal navy blue, dusty rose, cream, pine green, soft gold, deep plum; crisp edges, one isolated subject centred on a plain pure white background, no text, no lettering, no frame, no ground shadow, no background scenery, cozy and a little whimsical.

Each prompt = base + ` Subject: ` + the subject below. Original designs only: no ballet company, film, brand or character artwork, no text, and no sabres or other weapons (the nutcracker holds a sceptre, the mouse king has empty hands).

| Design | Subject | Draft kept |
|---|---|---|
| 01 Classic nutcracker | a full body wooden nutcracker soldier toy standing front view, tall black hat with gold trim, nutcracker red coat with gold buttons and a gold sash, navy blue trousers, black boots, a soft gold beard and moustache, rosy cheeks, holding a gold sceptre with a star on top | #4 of 4 (flash) |
| 02 Nutcracker portrait | the head and shoulders of a wooden nutcracker soldier toy, front view, tall navy blue hat with gold trim and a sprig of holly with red berries, square jaw, soft gold beard and moustache, rosy cheeks, nutcracker red coat with gold epaulettes | #2 of 4 (flash) |
| 03 Navy nutcracker | a full body wooden nutcracker toy standing in a slight three-quarter view, royal navy blue coat with gold buttons and red trim, tall red hat with a gold plume, soft gold beard, red trousers, black boots, holding a small wrapped gift box with a gold bow | #2 of 4 (flash) |
| 04 Sugar plum dancer | a graceful ballerina silhouette in solid deep plum, on pointe in an arabesque pose with arms raised, wearing a dusty rose and soft gold tutu, hair in a neat bun, no facial details | #1 of 4 (flash) |
| 05 Red tutu dancer | a ballerina silhouette in solid deep plum leaping in a split leap, arms outstretched, wearing a flowing berry red tutu skirt, hair in a bun, no facial details | #2 of 4 (flash) |
| 06 Mouse king | a cute plump mouse king standing upright, warm taupe brown fur, a small soft gold crown with red jewels, a berry red velvet cape with gold trim, long curly tail, round ears with dusty rose insides, a friendly mischievous smile, empty hands | #2 of 4 (flash) |
| 07 Gold snowflake | a large ornate six-pointed snowflake in soft gold with frosty teal blue accents and small berry red dots at the tips | #1 of 4 (flash) |
| 08 Toy drum | a toy soldier drum, front view, nutcracker red body with a soft gold zigzag cord pattern, royal navy blue rims, two wooden drumsticks crossed on top, a small sprig of holly with red berries | #1 of 4 (flash) |
| 09 Drummer soldier | a full body wooden toy soldier standing side view, royal navy blue coat with gold buttons, tall black hat with a red plume, red trousers, black boots, playing a small red drum hanging at his waist with two drumsticks, rosy cheeks, no beard | #1 of 4 (flash) |
| 10 Pointe shoes | a pair of dusty rose satin ballet pointe shoes with long dusty rose ribbons tied together in a bow, a small sprig of holly with red berries | #2 of 4 (flash) |
| 11 Sugar plums | three round sugared plums in deep plum purple with soft highlights, two green leaves and a curled soft gold ribbon | #1 of 4 (flash) |
| 12 Music box | an open ballerina music box, a nutcracker red wooden box with soft gold trim and a small gold key on the side, a tiny ballerina in a dusty rose tutu dancing on pointe on top | #1 of 4 (flash) |

## Checked by hand
Every kept draft was looked at before processing; no draft was cropped at the edge (02 #1/#3 and 03 #1/#3/#4 were, so they were skipped). Every finished PNG was looked at on dark green in the contact sheet, with 100% crops of the faces, hands, ribbons and every halo or pinhole spot: no text, letters or signatures; no extra limbs; faces read as intended (the dancers are faceless silhouettes or a small profile).

Draft choices and fixes (all local, in `process.py` and `gen.py`):
- **04 Sugar plum dancer:** draft #2 had a sketchy double outline that broke into loose slivers and cracks once cut out. It was swapped for draft #1 (clean closed outlines), which cost one more `removebg` + `upscale` ($0.014).
- **05 Red tutu dancer:** renamed from "Leaping dancer" because the kept draft is a high leg extension on pointe, not a leap. Its plum silhouette had hairline paper cracks between outline and fill; `CRACK_FILL` repaints them plum before the white clean-up.
- **10 Pointe shoes:** a loose sparkle dot by the holly is dropped (`SPECK_BY_SLUG`).
- **02, 08, 12:** a 1 px paper rim on one edge (02 coat, 08 drum) and grey paper between 12's dancer's fingers are cleared with narrow `CLEAR_BOX` strips, not whole-image boxes (QA 015 S6).
- **All designs (S6):** any transparent hole under 60 px inside the art is closed with its rim's colour, also after quantizing, and crumbs lifted over alpha 127 by the quantizer are dropped. `gen.py --check` now tests for pinholes.
- **03 Navy nutcracker:** its outlines are a lighter plum, so its SVG uses a line threshold of 135 instead of 105 (`LINE_MAX_BY_SLUG`); at 105 the SVG was a bare silhouette.
- **Real light art listed in `HALO_OK`:** 03's white teeth, 04's cream pointe shoe, 05's cream neckline trim, 12's cream ribbon bow.
