# AI images used in bundle 012 (QA round 1, 4 Oct 2026)

Only the background of listing image 1 is AI-made. The stitched hoops on it are rendered in code from the real chart grids (`stitch.py`), so the photo shows exactly what the charts make. No AI image is in the buyer files.

**Command (cheap recipe, flash drafts only):**
`python3 tools/imagegen.py gen "<prompt>" art/bg.png --flash --n 4` → art/bg-1.png … bg-4.png, $0.028 in total (Recraft V4.1 Flash, 1024×1024). A first attempt with `--size 1365x1024` was rejected by the API (400, size unsupported) before generation, so it was not charged; the spend log moved from $4.49 to $4.52.

**Prompt** (starts from the mockup block in shop-profile/STYLE.md):
Realistic product photo, soft natural window light, cozy wooden table, shallow depth of field. Top-down flat lay of a dark walnut wooden table at dusk with fresh pine sprigs and a few red winter berries along the top and left edges, a loose spool of red twine, a pair of small brass embroidery scissors and softly glowing warm fairy lights in the corners, large empty clear area of plain wood in the centre and right, moody palette of deep plum, pine green, berry red and warm gold, no embroidery, no hoops, no fabric, no text, no logos

**Chosen:** bg-1 (pine, berries and lights top-left, open wood in the centre; no artefacts in the visible area). It was cropped to 4:3 (`art/bg-scene.png`, rows 60–828) and shown at 3000×2250 as a soft-focus backdrop; the hoops and title band cover the centre. bg-2 to bg-4 were not used (curtain/glare, broken scissors in bg-4).
