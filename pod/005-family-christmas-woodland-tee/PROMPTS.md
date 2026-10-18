# Prompts: 005 Family Christmas 2026 woodland tee

Style block from shop-profile/STYLE.md (Prints/POD). Cheap recipe, no --pro.

## Batch 1: `gen --flash --n 2` (recraftv4_1_flash, 2 x $0.007 = $0.014 est.)
> Flat vector illustration style with fine linework and subtle grain, crisp edges, centred composition, no text, no lettering. Cozy, a little whimsical woodland Christmas. Limited palette: pine green #2f5d46, deep plum #2c1b36 outlines, russet orange #b5573a, berry red #8b2f3c, moon gold #e6b776 on a solid flat pure white background. Subject: a large round wreath of pine boughs with holly berries and pinecones, a small fox, a deer, an owl and a hedgehog nestled around the wreath, the middle of the wreath completely empty and plain white (open space for a title), bold clear silhouette, generous empty margin on all sides

`candidates/wreath-1.png` **kept**: cohesive wreath with all four animals, a clear empty middle. (2: animals detached from the wreath in the corners, pale green boughs print weakly; kept only as `wreath-2-preview.jpg`.)

## Upscale and print file
- `imagegen.py upscale` wreath-1 -> `candidates/wreath-1-up.png` 4096 px ($0.004 est.).
- `pod/make_art.py` (005 block): white keyed out (lo 45 / hi 95), design cropped to 3000 px wide (0.84x, so no upsampling), 1 in below the top of 4500x5100; fringe decontaminated; "FAMILY / CHRISTMAS / 2026" typeset in code (DejaVu Serif Bold, deep plum #2c1b36) in the wreath's empty middle. Checked on Ash (#b2b2af): no near-white patches, fringe luminance 100 vs 94 for the opaque design.
- Total image credits: 2 flash images + 1 upscale, about $0.018 (about 18 credits). No manual art fixes.
