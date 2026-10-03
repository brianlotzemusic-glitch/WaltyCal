# Prompts: 004 bat-wing tree tee

Source design: Bat Wing Tree from bundle 004 (bat-christmas). Style block from shop-profile/STYLE.md (Prints/POD).

## Batch 1: `--pro --n 4 --size 2048x2048` (recraftv4_1_pro, 4 x $0.21 = $0.84)
> Flat vector illustration style with fine linework and subtle grain, crisp edges, centred composition, no text. Moody, cozy, a little whimsical dark holiday, elegant not scary. Limited palette: deep plum #2c1b36, dusk violet #4a2c55, moon gold #e8c97a and berry red #8b2f3c on a solid flat pure white background, no white inside the design. Subject: a Christmas tree built from stacked tiers of spread bat wings, wider at the bottom, a small bat with open wings perched on top as the tree topper, round gold baubles and tiny gold stars on the wing tiers, short trunk, bold clear silhouette that reads from across a room, generous empty margin on all sides

`candidates/battree-1..4.png`. **Kept: battree-3**: each tier is a whole bat, a clear tree silhouette with a red bat topper and a clean trunk. (1: good but muddy red speckle; 2: grungy spray texture that prints poorly; 4: narrow and small.)

## Upscale and print file
- `imagegen.py upscale` → `candidates/battree-3-up.png` 4096 px ($0.004). The second pass was capped at 4096 and discarded ($0.004).
- `make_art.py`: white keyed out locally (soft ramp, unpremultiplied against white), so the gaps between tiers show the shirt colour. Design 3000 x 3402 px = 10 x 11.3 in at native resolution (0.98x), centred 1 in below the top of the 4500x5100 transparent PNG.
