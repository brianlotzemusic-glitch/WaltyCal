# Prompts: 006 Moth and holly tee

Style block from shop-profile/STYLE.md (Prints/POD), light colours for dark shirts. Cheap recipe, no --pro.

## Batch 1: `gen --flash --n 2` (recraftv4_1_flash, 2 x $0.007 = $0.014 est.)
> Flat vector illustration style with fine linework and subtle grain, crisp edges, centred composition, no text, no lettering. Cozy, a little whimsical winter woodland. Limited palette: cream #f1e6cf, moon gold #e8c97a, soft sage green #a8c3a0 and bright berry red #d4506a on a solid flat pure black background. Subject: a single large luna moth with spread wings and feathery antennae, seen straight on, symmetrical, long tail points on the lower wings, wings softly patterned with cream and gold with small round wing spots, a sprig of sage-green holly leaves with three round red berries tucked at each side of its body, a few tiny gold stars, gentle and pretty, no skull, bold clear shape that reads from across a room, generous empty margin on all sides

`candidates/moth-2.png` **kept**: cream moth, holly sprigs with berries above the wings, clean edges. (1: wings a flat yellow-orange that looks dull on Asphalt, holly and berries tiny.)

## Upscale and print file
- `imagegen.py upscale` -> `candidates/moth-2-up.png` 4096 px ($0.004 est.).
- `pod/make_art.py` (006 line): black keyed out (lo 25 / hi 80), design 3600 px = 12 in wide (1.31x upsample, flat art), 1 in below the top of 4500x5100. Checked on black, navy, dark heather and asphalt composites and on the Printify mockups.
- Total: 2 flash images + 1 upscale, about $0.018 (about 18 credits). No text in the art.
