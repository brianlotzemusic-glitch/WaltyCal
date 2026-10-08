# Prompts — 015 Highland cow Christmas clipart

Recraft via `tools/imagegen.py`, cheap recipe only (FACTORY.md "Art quality"): one `gen --flash --n 4 --size 1024x1024` per design ($0.028), the best draft kept, then `removebg` ($0.01) on the kept draft for the cut-out mask and `upscale` ($0.004) on the kept draft for print size. No standard re-rolls were needed, no `--pro`, no `vectorize`. Everything after that (cut-out, white-paper cleanup, trim to 3600 px, palette PNG, SVG line art, mockup compositing, listing images) is local and free.

**Spend (log/image-spend.csv, 8 Oct 2026):**
| Item | Calls | Cost |
|---|---|---|
| Flash drafts, 12 designs × 4 | 12 | $0.336 |
| `removebg` on the 12 kept drafts | 12 | $0.120 |
| `upscale` on the 12 kept drafts | 12 | $0.048 |
| Mockup photo: flash drafts × 4 + `upscale` of the kept one | 2 | $0.032 |
| **Total** | | **$0.536** (536 credits) |

That is **$0.042 per design** (under the $0.05 target) plus $0.032 for the listing mockup. Recraft balance before: 4,854 credits; after: 4,318.

Drafts not used were left in the session scratchpad, not committed. Committed: the kept drafts (`art/raw/`, 1024 × 1024) and their removebg masks (`art/alpha/`). The 4096 px upscales (`art/up/`, ~12 MB each) are not committed; `process.py` needs them, so rebuilding the art from scratch costs 12 × $0.004 (`imagegen.py upscale art/raw/X.png art/up/X.png`). The finished PNGs are in the ZIP.

## Base prompt (style bible clipart line, shop-profile/STYLE.md)

> Christmas clipart, flat vector illustration style with clean dark plum outlines and flat colours, limited palette: warm ginger and rust fur, cream, pine green, berry red, soft gold, deep plum; crisp edges, one isolated subject centred on a plain pure white background, no text, no lettering, no frame, no ground shadow, no background scenery, cozy and a little whimsical.

Each prompt = base + ` Subject: ` + the subject below. "Santa-free" by design: no Santa hats, no red-and-white Santa trim, no characters, no text.

| Design | Subject | Draft kept |
|---|---|---|
| 01 Holly crown | the head of a cute shaggy Scottish highland cow, front view, long ginger fringe falling over its eyes, curved cream horns, soft pink nose, a sprig of holly with three red berries tucked on top of its fringe | #1 of 4 (flash) |
| 02 Cozy scarf | the head and shoulders of a cute shaggy Scottish highland cow, front view, long ginger fringe, curved cream horns, soft pink nose, wearing a chunky knitted scarf in berry red and cream stripes wrapped around its neck | #4 of 4 (flash) |
| 03 Pine wreath | the head of a cute shaggy Scottish highland cow, front view, long ginger fringe, curved cream horns, soft pink nose, framed by a round pine wreath with red berries and pinecones behind its head, the horns poking out over the wreath | #3 of 4 (flash) |
| 04 Bobble hat | the head of a cute shaggy Scottish highland cow, front view, long ginger fringe, curved cream horns, soft pink nose, wearing a pine green knitted beanie hat with a cream pompom and a cream knitted band, the horns poking out on each side | #4 of 4 (flash) |
| 05 Winter stroll | a full body cute shaggy Scottish highland cow standing side view, long ginger shaggy coat, curved cream horns, wearing a berry red knitted scarf with fringed ends, standing on a small patch of snow | #1 of 4 (flash) |
| 06 Sleepy calf | a cute fluffy Scottish highland calf lying down curled up and sleeping, small ginger fluffy coat, tiny cream horn buds, a holly sprig with red berries beside it | #3 of 4 (flash) |
| 07 Tree carrier | a full body cute shaggy Scottish highland cow walking side view, long ginger coat, curved cream horns, carrying a small fresh-cut Christmas pine tree tied on its back with a red ribbon | #2 of 4 (flash) |
| 08 Fairy lights | the head of a cute shaggy Scottish highland cow, front view, long ginger fringe, curved cream horns, soft pink nose, a string of glowing gold Christmas fairy lights draped around its horns | #4 of 4 (flash) |
| 09 Bauble horn | the head of a cute shaggy Scottish highland cow, three-quarter view, long ginger fringe, curved cream horns, soft pink nose, a round berry red Christmas bauble ornament with a gold cap hanging from one horn by a ribbon | #2 of 4 (flash) |
| 10 Wreath collar | a full body cute shaggy Scottish highland cow sitting down, front view, long ginger coat, curved cream horns, wearing a small green holly and pine wreath around its neck like a collar with a red bow | #2 of 4 (flash) |
| 11 Mistletoe | the head of a cute shaggy Scottish highland cow looking up, front view, long ginger fringe, curved cream horns, soft pink nose, a sprig of mistletoe with white berries and a red ribbon hanging above its head | #2 of 4 (flash) |
| 12 Gift box | a cute shaggy Scottish highland calf sitting front view, ginger fluffy coat, small cream horns, holding a wrapped Christmas gift box with a berry red ribbon and bow between its front legs | #2 of 4 (flash) |

## Mockup photo (listing image 3 only)

> Realistic product photo, soft natural window light, cozy wooden table, shallow depth of field. Top-down flat lay on a warm dark wooden table: a plain blank white crew-neck t-shirt laid flat in the centre with a large empty chest area, beside it a plain blank white square greeting card and a plain blank cream canvas tote bag laid flat, a few pine sprigs, pinecones and red berries at the edges, everything blank and unprinted, no print, no pattern, no text, no logos, no people

`--flash --n 4 --size 1152x896` (flash refuses 1536x1024); draft #4 kept (`mockup/blank-flatlay-raw.png`), upscaled to `mockup/blank-flatlay.jpg`. `mockup.py` prints the real PNGs onto it.

## Checked by hand
Every kept draft was looked at full size before processing, and every finished PNG on a dark background at full size and in 100% crops: no text, letters, signatures or watermarks; four legs on every full-body cow; two eyes or a fringe covering them; no extra horns or ears. Draft choices: 02 #4 (the #1 draft had a green patch round the muzzle), 04 #4 (#1's eyes looked sad), 08 #4 (#1 was cropped at the chin), 09 #2 (three-quarter view, for variety), 12 #2 (smiling calf).

Fixes found by looking, all in code (`process.py`):
- **11 Mistletoe:** removebg took the six white mistletoe berries as background, so they showed the fabric through them. Enclosed holes under 12,000 px are put back (`FILL_HOLES`); the ribbon loops stay transparent.
- **All designs:** removebg left white paper between fine pine needles and fringe, which showed as white specks on dark fabric (05, 03, 10 most). Near-white pixels joined to the background are made transparent and their edges softened (`clear_white`).
- **05 Winter stroll:** the left pine sprig's tip dissolved into grey snow-shadow texture. The left sprig is erased (`ERASE_BOX`); the two sprigs by the front legs stay. Renamed from "Snowy stroll" because removebg also took away the white snow patch.
