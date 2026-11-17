# Art library (Higgsfield, house style)

Added 17 Nov 2026 on the owner's order ("have the designer use Higgsfield; house line art; new products first").
42 decorative illustrations in the store's house look: black line art, white fills, ONE accent colour (icy blue #4FA3D9),
transparent background, 1400 x 1400 PNG with alpha. Made once with Higgsfield `gpt_image_2_6` (medium quality, 2k, about 1 credit
each). Shift sessions have no Higgsfield connector: builders only USE these files. New art is requested from the owner's session
(say so in the builder reply: "needs art: <subject>").

## Use
- Hero art on `cover.png`, the PDF cover and preview images: place a library PNG in the hero area of the cover layout in
  `tpt/STYLE.md` (about 55-60% of the height). In `gen.py`: `<img src="../_art/library/snowman-conductor.png">` (HTML to Chromium) or
  PIL `Image.open(...)` and `alpha_composite`. Keep padding around it; scale proportionally; never crop it.
- Small spot art on interior pages (headers, answer-key corners, certificates) is fine at any size from 0.6 in up.
- Winter and holiday items use the icy blue already in the art (matches the `ACCENT` for winter). The art keeps its own blue even
  if a product's accent differs; for another season ask for a recoloured set.
- The disclosure line already on every listing covers AI-made art. Nothing needs to be added.

## Never
- No AI art for music notation, staves, note names, rhythm syllables, text, numbers, grids, puzzles, charts or anything an answer
  key depends on, and not for the colour-by-note pictures (their regions and keys are computed in code).
- No generating images from a shift (no Higgsfield, Recraft or other image tools there).
- The Visual inspector looks at library art like everything else: a malformed detail (extra fingers, a wrong instrument, stray
  marks) is BLOCKING on a cover or preview; report it and the library item is replaced.

## Index
Winter and holiday: snowman-conductor, snowflakes, jingle-bells-holly, kids-winter-band, carolers, penguin-singing, reindeer,
cardinal, gingerbread-person, candy-canes, gift-boxes, mittens-scarf, hot-cocoa, pine-tree, menorah (nine lights; for Hanukkah
items), dreidel (plain pattern, no letters; the perspective is a little odd: prefer small sizes).
Classroom instruments: recorder, bucket-drums, boomwhackers, handbells, glockenspiel, hand-drum, percussion-trio (tambourine,
triangle, maracas), snare-drum, ukulele, acoustic-guitar, trumpet, violin, flute, clarinet.
Music room: music-stand (blank), metronome (no numbers), stopwatch (plain dial: speed drills), trophy, dice (two dice with pips;
use for Roll and Compose), books-pencil.
Logic and studio: headphones, laptop-daw, midi-pad-controller, microphone, studio-monitors, mixing-console.

`samples/` holds the first comparison images (house line art vs full colour) and the owner's pick.
