# Prompts — 017 Winter Songbirds Clipart

Recraft via `tools/imagegen.py`, cheap recipe only (FACTORY.md "Art quality", formats/clipart.md): one `gen --flash --n 4 --size 1024x1024` per design ($0.028), the best draft kept, then `removebg` ($0.01) and `upscale` ($0.004) on the kept draft. No standard re-rolls, no `--pro`, no `vectorize`. The mockup reuses 015's blank flat-lay photo (`mockup/blank-flatlay.jpg`), so it cost nothing. Everything after the AI calls is local and free.

**Spend (log/image-spend.csv, 9 Oct 2026):**
| Item | Calls | Cost |
|---|---|---|
| Flash drafts, 12 designs × 4 | 12 | $0.336 |
| `removebg` on the kept drafts | 12 | $0.120 |
| `upscale` on the kept drafts | 12 | $0.048 |
| Mockup photo | 0 | $0 (015's blank flat-lay reused) |
| **Total** | | **$0.504** (504 credits) |

That is **$0.042 per design**, under the $0.05 target. Recraft balance before: 3,800 credits; after: 3,296.

Drafts not used were left in the session scratchpad, not committed. Committed: the kept drafts (`art/raw/`) and their removebg masks (`art/alpha/`, alpha channel only). The 4096 px upscales (`art/up/`) are not committed; rebuilding from scratch costs 12 × $0.004 (`imagegen.py upscale art/raw/X.png art/up/X.png`).

## Base prompt (style bible clipart line, shop-profile/STYLE.md, with "no snow" added)

> Winter Christmas clipart, flat vector illustration style with clean dark plum outlines and flat colours, limited palette: cardinal red, robin orange, bluebird blue, warm brown, cream, pine green, berry red, soft gold, deep plum; crisp edges, one isolated subject centred on a plain pure white background, no text, no lettering, no frame, no ground shadow, no snow, no background scenery, cozy and a little whimsical.

Each prompt = base + ` Subject: ` + the subject below. Original designs only: no brand, mascot, sports-team or field-guide artwork, no text. "No snow" was added because white snow on white paper would be cut away by removebg and leave grey fringes.

| Design | Subject | Draft kept |
|---|---|---|
| 01 Cardinal on holly | a plump male northern cardinal songbird perched on a sprig of holly with glossy green leaves and red berries, side view, bright cardinal red feathers, a black mask round the orange beak, crest raised, one dark eye with a small highlight | #3 of 4 (flash) |
| 02 Chickadee on pine | a round little black-capped chickadee songbird perched on a short pine branch with a brown pine cone, side view, black cap and bib, cream cheeks, soft grey-blue wings, warm buff belly | #1 of 4 (flash) |
| 03 Robin with berries | a round little European robin songbird standing on a short twig with a cluster of red berries, side view, warm robin orange face and breast, warm brown back and wings, cream belly, thin legs | #1 of 4 (flash) |
| 04 Winter wren | a tiny round wren songbird with a cocked-up tail perched on a large brown pine cone with a small sprig of pine needles, side view, warm brown barred feathers, cream eyebrow stripe | #3 of 4 (flash) |
| 05 Little owl | a cute small brown owl perched on a short pine branch, front view, big round golden eyes, warm brown and cream speckled feathers, wearing a cozy berry red knitted scarf | #1 of 4 (flash) |
| 06 Blue jay | a blue jay songbird perched on a short bare twig with a few red berries, side view, bluebird blue crest, back and wings with black and white bars on the wings, cream throat and belly, a black necklace stripe | #4 of 4 (flash) |
| 07 Bluebird on berries | a plump eastern bluebird songbird perched on a winterberry branch with clusters of bright red berries, side view, bright bluebird blue head and wings, warm robin orange breast, cream belly | #3 of 4 (flash) |
| 08 Flying cardinal | a male northern cardinal songbird flying with wings spread wide, carrying a small sprig of holly with red berries in its beak, side view, bright cardinal red feathers, black mask round the beak | #1 of 4 (flash) |
| 09 Birdhouse | a cute wooden birdhouse on a short post, berry red walls, a pine green roof, a round entrance hole with a tiny perch, a sprig of holly with red berries on the roof, a little brown songbird sitting on the perch | #2 of 4 (flash) |
| 10 Holly sprig | a sprig of three glossy pine green holly leaves with a cluster of bright red berries and a small soft gold ribbon bow | #2 of 4 (flash) |
| 11 Pine cone sprig | a pine branch sprig with two warm brown pine cones and a few small red berries, neat flat pine green needles grouped in clumps | #2 of 4 (flash) |
| 12 Cardinal in a hat | a plump round male northern cardinal songbird, front three-quarter view, bright cardinal red feathers, black mask round the orange beak, wearing a cozy cream and pine green striped knitted bobble hat, sitting on a small holly sprig | #3 of 4 (flash) |

## Designer's notes for QA (not an approval)
Every draft was looked at on a low-res contact sheet before picking; every finished PNG on dark green and checkerboard in `contact-sheet.png`, plus crops of the flagged areas below. No text, letters or signatures seen; no extra legs, wings or eyes seen.

Draft choices:
- **Stylized colours, on purpose or accepted:** 03 Robin has a blue-grey crown (a stylized European robin, not field-accurate). The other robin drafts were weaker (#2 had a loose grass stroke and detached floating berries). 01 #3 was kept over #2/#4 because those gave the cardinal a blue wing.
- **11 Pine cone sprig** (draft #2) includes three tiny birds (a cardinal, a bluebird and an orange songbird) and a few loose berries/gold dots: it is 7 separate pieces, all over 900 px. 3 smaller dots were dropped as specks. Please judge whether the name still fits or should be "Pine sprig with birds".
- **08 Flying cardinal:** the holly in its beak is cream/beige (the draft's choice), not green; it reads as frosted holly.
- **12 Cardinal in a hat** sits on dark plum-red holly, not green.

Fixes (all local, in `process.py` and `gen.py`):
- **04 Winter wren:** the pale sage pine sprig has no dark outline, so its tips had a 1–2 px pale paper rim (one 32 px halo patch). `CLEAR_BOX` over the sprig fades it.
- **11 Pine cone sprig:** paper slivers between the needles; `CLEAR_BOX` over the whole design except the cream stem, which is real art.
- **02 and 11, opacity (S2):** fine dark pine needles leave so much anti-aliased edge that only ~97% of solid pixels were alpha 255. New per-design `EDGE_SNAP`: palette entries at alpha ≥ 192 snap to 255 (edge colours are already un-mixed from white, so no light fringe; the needle edges are just ~1 px crisper). Now 98.08% (11), just over the 98% bar. Please look at 02/11 needle edges at 100% on dark.
- **Real light art listed in `HALO_OK`:** 08's cream holly leaves (with white highlights) in the beak; 11's cream stem, outlined in plum.
- 03's branch is cream with a plum outline and passed the halo test without an exemption.

`python3 gen.py --check`: ALL CHECKS PASS (ZIP 8.0 MB; closest design pair 05/10 at 260 bits).
