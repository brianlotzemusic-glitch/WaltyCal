# Prompts: 004 bat-wing tree tee

Source design: Bat Wing Tree from bundle 004 (bat-christmas). Style block from shop-profile/STYLE.md (Prints/POD).

## Batch 1: `--pro --n 4 --size 2048x2048` (recraftv4_1_pro, 4 x $0.21 = $0.84)
> Flat vector illustration style with fine linework and subtle grain, crisp edges, centred composition, no text. Moody, cozy, a little whimsical dark holiday, elegant not scary. Limited palette: deep plum #2c1b36, dusk violet #4a2c55, moon gold #e8c97a and berry red #8b2f3c on a solid flat pure white background, no white inside the design. Subject: a Christmas tree built from stacked tiers of spread bat wings, wider at the bottom, a small bat with open wings perched on top as the tree topper, round gold baubles and tiny gold stars on the wing tiers, short trunk, bold clear silhouette that reads from across a room, generous empty margin on all sides

`candidates/battree-1..4.png`. **Kept: battree-3**: each tier is a whole bat, a clear tree silhouette with a red bat topper and a clean trunk. (1: good but muddy red speckle; 2: grungy spray texture that prints poorly; 4: narrow and small.)

## Upscale and print file
- `imagegen.py upscale` → `candidates/battree-3-up.png` 4096 px ($0.004). The second pass was capped at 4096 and discarded ($0.004).
- `make_art.py`: white keyed out locally (soft ramp, unpremultiplied against white), so the gaps between tiers show the shirt colour. Design 3000 x 3402 px = 10 x 11.3 in at native resolution (0.98x), centred 1 in below the top of the 4500x5100 transparent PNG.

## QA round 1 fixes (3 Oct 2026), all local and free, in `pod/make_art.py`
QA found AI artefacts in the top tiers (garbled squiggle "stars", a smudged gold blob in a gap, an off-white patch at a wing tip that was not keyed out, and a pale smear).
- `clean_stars()` (runs on the 4096 px source before keying): finds every gold mark. The 15 round baubles (fill >= 0.72) are kept. The other 147 marks (stars, squiggles, smudges) are erased with an onion-peel inpaint and redrawn as clean upright 5-point stars of the same size in the sampled gold #e6b776. Specks under 20 px are erased.
- White key raised to lo=45/hi=95 (was 20/70): the off-white patch (234,226,217) is now transparent. Gold (minimum channel about 122) stays opaque.
- `fix_004()` (tee space, after layout): inpaints a pale streak, a grey smudge and a three-star cluster with a brown smear (redrawn as 2 separate stars), plus a pink halo beside one redrawn star. It clears a red speck in the gap to transparent, then decontaminates the anti-aliased fringe (semi-transparent pixels take the nearest opaque colour), which removes the light halo along gap edges.
- Checked at 100% on Ash grey (#b2b2af) over the whole design, and in the Printify Ash mockup (`mockups/front-ash.jpg`). A trace about 6 px across beside one redrawn star on tier 4 (around 2070,1486) is still faintly visible at 800% zoom, but not at print size.
