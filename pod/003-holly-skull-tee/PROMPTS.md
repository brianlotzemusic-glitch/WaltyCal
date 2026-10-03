# Prompts: 003 holly skull tee

Source design: Holly Sprig Skull from bundle 003 (skull-holiday). Style block from shop-profile/STYLE.md (Prints/POD).

## Batch 1: `--pro --n 4 --size 2048x2048` (4 x $0.21 = $0.84): all rejected
> Flat vector illustration style with fine linework and subtle grain, crisp edges, centred composition, no text. Cozy and a little whimsical dark holiday, elegant not gory. Limited palette: cream #f1e6cf, moon gold #e8c97a, berry red #8b2f3c and soft sage green on a solid flat pure black background. Subject: a friendly stylised skull in front view with big rounded eye sockets and a small heart-shaped nose, a crown of glossy holly leaves with three round red berries on top of its head, two small pine sprigs and a few tiny stars around it, bold clear shape that reads from across a room, generous empty margin on all sides

`candidates/skull-1..4.png`. Rejected: 1 red goggle-like eyes; 2 realistic toothy skull, too grim; 3 odd ringed lines inside the eye sockets; 4 lopsided, skewed cranium.

## Batch 2: `--pro --n 4 --size 2048x2048` (4 x $0.21 = $0.84)
> Flat vector illustration style with fine linework and subtle grain, crisp edges, centred composition, no text. Cozy and a little whimsical dark holiday, elegant not gory. Limited palette: cream #f1e6cf, moon gold #e8c97a, berry red #8b2f3c and soft sage green on a solid flat pure black background. Subject: a cute stylised skull, perfectly symmetrical straight-on front view, rounded cranium, two large plain oval eye sockets filled solid black, a small berry-red heart-shaped nose, a neat row of square teeth, a sprig of three sage-green holly leaves with three round red berries sitting on top of the head, a gold crescent moon above, two cream pine sprigs either side and a few tiny gold stars, bold clear shape that reads from across a room, generous empty margin on all sides

`candidates/skullB-1..4.png`. **Kept: skullB-2**: symmetrical and bold, with a heart nose like the original Duskwood skull; clean at 100%. (1: small; 3: navy background, blocky teeth; 4: fuzzy pine sprigs.)

## Upscale and print file
- `imagegen.py upscale` → `candidates/skullB-2-up.png` 4096 px ($0.004). A second pass also returned 4096 px (Recraft's output cap), so it was discarded ($0.004).
- `make_art.py`: black keyed out locally (soft ramp on the brightest channel, so the eye sockets and linework show the shirt colour), cropped, design 3000 px = 10 in wide, centred 1 in below the top of the 4500x5100 transparent PNG. Upsampled 1.11x from the 4096 px source (about 270 effective DPI on flat art).
