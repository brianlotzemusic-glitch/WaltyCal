# QA: 024 Mushroom & Woodland Coloring Pages (round 1)

## Summary

APPROVED. The files, listing and listing images are clean. All 20 pages are bold, closed and kid-safe, and the AI spend is within the cheap-recipe limits. Only optional polish is noted.

## Technical checks

| Check | Result |
|---|---|
| `python3 gen.py --check` | ALL CHECKS PASS. Median stroke is at least 1.63 mm, the smallest space is 10 mm², the worst page has 14 nooks (0.11%), the margin is 17 mm on Letter and 14 mm on A4, and the closest pair of pages differs by 167 bits |
| ZIP (unpacked by QA) | Holds exactly the Letter PDF, the A4 PDF and README-LICENSE.txt |
| PDFs | 20 pages each, no fonts and no text on the pages, 0.8 MB each |
| listing.json | Title is 130 chars with one "&". 13 unique tags, the longest is 19 chars. Price 3.99, taxonomy 339, and the description ends with the exact non-cut-file disclosure line |
| Listing images | 4 images at 3000×2250 |
| IP | None. Every subject is a generic woodland animal or mushroom, with no characters, brands or text |

## AI cost

The log has 21 flash calls at $0.028 on 13 Oct, so $0.588 in total. That is $0.029 per page, under the $0.05 cap per design. The $0.59 figure is for the whole 20-page bundle, not per design. The recipe was the cheap one: `gen --flash --n 4` only, with no standard re-roll, no `--pro`, and no upscale or vectorize (process.py scales locally). The one extra batch was page 20, redone with a new subject.

## Page review (contact sheet, 100 dpi rows of 5, and 100% crops of 16, 17 and 18)

Outlines are thick and even, every shape is closed, and the rounded frame closes the background. There is no grey, text or signature. Animals and mushrooms are well formed, with no extra limbs and no odd faces.

- **01 to 15, 19, 20**: good. Each reads at thumbnail size.
- **16 Mushroom meadow**: the busiest page, with 127 spaces and a dense cluster of caps. The gaps are narrow but closed and at least 12 mm². Acceptable.
- **17 Wren**: clean. The bird is simple and the eye, wing and tail are closed.
- **18 Bear cub**: the cub is good. The stacked caps at top right look a little like fir tiers, and there is a tiny black wedge at the right frame edge near (670, 315) in the 100 dpi crop. Both are cosmetic.
- **14 Fawn**: two dark mushroom undersides are accepted shade, as recorded in `CLUMP_OK`.
- **Print-safe margins**: pass on both papers.
- **Consistency**: stroke, frame and style match across all 20 pages.

## Listing images (honest)

- **1 Thumbnail**: strong. It shows real pages 2, 4 and 15, coloured from their own regions, and the "20 pages" badge is true.
- **2 Page grid**: all 20 real pages, numbered and named to match the PDFs.
- **3 Coloured mockup**: shows real pages 4 and 2, plus a close-up of page 13. The copy says the files are black and white.
- **4 Formats**: Letter and A4, 2 PDFs, a digital download. Accurate.

## Optional polish (not blocking)

- Page 18: remove the tiny black wedge at the right frame edge.
- Page 16: nothing needed, but do not add more detail.

**Verdict: APPROVED**
