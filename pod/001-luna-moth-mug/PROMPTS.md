# Prompts: 001 luna moth mug

Source design: Luna Moon Moth from bundle 005 (moth-holly). Style block from shop-profile/STYLE.md (Prints/POD).

## Batch 1: `imagegen.py gen ... --pro --n 4 --size 2048x2048` (recraftv4_1_pro, 4 x $0.21 = $0.84)
> Flat vector illustration style with fine linework and subtle grain, crisp edges, centred composition, no text. Moody, cozy, a little whimsical woodland at dusk. Limited palette: cream #f1e6cf, moon gold #e8c97a, dusk violet #4a2c55 and pine green #2f4a3a on a solid flat deep plum #2c1b36 background. Subject: a single elegant luna moth seen from directly above, perfectly symmetrical, long curved swallow tails on the hind wings, a crescent moon marking on each wing, delicate wing veins, feathery antennae, two small pine sprigs and a few tiny stars around it, generous empty margin on all sides

Candidates: `candidates/moth-1..4.png`. **Kept: moth-3**: symmetrical, gold crescent moons on all four wings, gold antennae; no artefacts at 100%. (1: curled tails look odd; 2: fewer moons, plain; 4: good but small and the hind wings are muddled.)

## Centre accent (attempted AI, then code-drawn)
Printify's default "front" mockup looks at the middle of the wrap, which was empty in the first build (half moths at the edges), so the front needed its own motif.
- Tried: `imagegen.py gen "... Subject: a single gold crescent moon with fine linework, tall vertical composition, a few tiny four-pointed gold stars around it and one small pine sprig curving beneath it, small and simple accent motif, lots of empty background around it" --pro --n 4`. Recraft refused with `not_enough_credits` (HTTP 400): nothing was generated or charged.
- Used instead: `moon_accent()` in `pod/make_art.py` draws a crescent (opening upper right, like the wing markings) and 7 four-pointed sparkles in the moth art's sampled gold (#fac268), supersampled 4x. These are simple geometric shapes; no AI.

## Print file
`python3 pod/make_art.py` → `mug-wrap-2700x1120.png`: background fill sampled from the art (#280727). The moth is 920 px tall at 1/4 and 3/4 of the wrap (the left/right mockup views) and the crescent is at 1/2 (the front view). The moth is downsampled 0.67x from the 2048 px Pro source, so true 300 DPI at 9 x 3.73 in; no upscale needed.
