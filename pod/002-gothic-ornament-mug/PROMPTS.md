# Prompts: 002 gothic ornament mug

Source design: Gothic Window / Moon & Bat ornaments from bundle 002 (gothic-ornaments). Style block from shop-profile/STYLE.md (Prints/POD).

## Batch 1: `imagegen.py gen ... --pro --n 4 --size 2048x2048` (recraftv4_1_pro, 4 x $0.21 = $0.84)
> Flat vector illustration style with fine linework and subtle grain, crisp edges, centred composition, no text. Moody, cozy, a little whimsical, elegant gothic winter. Limited palette: deep plum #2c1b36, dusk violet #4a2c55, moon gold #e8c97a and berry red #8b2f3c on a solid flat cream #f1e6cf background. Subject: a single ornate gothic Christmas bauble ornament hanging from a short loop, round body with a pointed-arch window cut-out showing a crescent moon and a small bat in flight, delicate filigree scrollwork and tiny stars around the rim, small holly sprig at the cap, elegant not scary, generous empty margin on all sides

Candidates: `candidates/ornament-1..4.png`. **Kept: ornament-3**: bold gothic arched window, gold moon and bat, the closest to the original 002 Gothic Window design. (1: thin, busy sparkles; 2: muddy, low contrast; 4: rich but greyish background and a photo-textured moon.)

## Fixes
- A small stray drip under the bottom tip (source px ~1018–1026, 1577–1590) was painted out with the background colour in `make_art.py` (`fix=`).

## Print file
`mug-wrap-2700x1120.png`: cream background (#fbf6ed, sampled), three ornaments 960 px tall at 1/4, 1/2 and 3/4 of the wrap, so Printify's left, front and right views each centre on one bauble (it reads as a row of hanging ornaments). Downsampled 0.82x from the Pro source, so true 300 DPI; no upscale needed.
