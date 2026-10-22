# QA: TpT 029 Winter Color by Note (round 1)

**Verdict: REJECT (mechanics pass; art below the 027 bar on 3 pictures plus the cover)**

Reviewed 22 Oct 2026, independently of the Designer. Rendered the cover, 3 previews, all 27 worksheets and 27 keys at 100 dpi, with 100% crops of mittens, gingerbread and gifts. No item files were changed.

## Mechanics: pass
- Own decoder (parses build/resource.html; shapely point-in-polygon; Level A by glyph codepoint, B/C by staff-line y and clef glyph, bass/treble checked per level): 385 symbols across 27 worksheets, 0 mismatches against the key fills, 0 symbols outside a region, no uncovered regions, worksheet and key geometry identical. Labels and key cells legible (clef + letter names, key letters match the helper line).
- gen.py --check OK. 58 Letter pages (cover, notes, ref, 27+27, terms), preview 4 pages. Price and license 3.75. tpt.json tags ["Winter"], 4 grades, 1 subject, valid. Title matches the required string. UPLOAD.md complete, no trademarks. tpt/001 and 027 untouched (029 commit changes only tpt/029, queue.md, log).
- Title consistency: art and page text are winter-general with 4 holiday pictures (tree, gingerbread, ornament, gifts); none names Christmas, and the band says "Cozy winter & holiday art". A "Winter" title is consistent; no Seasonal Titles conflict expected.

## Art grades (skeptical buyer)
- 5 Snowflake **A-**. Symmetric, clean, ships.
- 6 Cardinal **B+**. Clear mask, wing, crest, branch. Tail runs past the branch end, fine.
- 3 Snowy Cabin **B+**. Clear. 4 Holiday Tree **B+**. Clear.
- 1 Snowman **B-**. Small in frame, scarf is a flat block floating over the neck, hat has no band, head/body overlap reads awkward. Also the cover hero.
- 8 Ornament **B-**. A wavy band across the whole top of the frame has no meaning (reads as a green stripe, not garland); cap is a plain box.
- 2 Mittens **C+**. Each thumb is a huge flipper hanging off the side, mitten bodies are tall rockets, cuffs are white boxes; reads as penguins. Dot sits between the cuffs.
- 7 Gingerbread House **C+**. Red cone roof with two green discs reads as a face or owl; no gingerbread cues (no candy, icing lines on roof, gumdrops); stray snow dot on the door.
- 9 Gifts **C+/B-**. Bow is two detached oval wings plus a ball; top box floats; snow dots touch/overlap the bow loops.
- Cover **B-** (needs B+). Layout and title are good, but the hero snowman is the weakest-posed picture and has the floating scarf.

## Required fixes
1. Mittens: one rounded mitten each, short curved thumb (about a third of body width) angled up, body shorter and wider, a ribbed cuff band, pair slightly tilted; move the dot off the cuff gap.
2. Gingerbread: roof as a scalloped icing edge plus 2-3 candy-dot regions or stripes (not discs that look like eyes), a gumdrop row, a candy-cane or wreath door detail; remove the dot on the door.
3. Gifts: build the bow from two loops that meet a center knot (loops touching the knot, a tail ribbon each side), seat the top box on the bottom box (no gap), clear dots from the bow.
4. Snowman: larger (fill about 85% of frame height), scarf wrapped around the neck with a dangling tail, hat with a band region, carrot nose, 3 coal buttons; then rebuild the cover with the improved snowman (or a cardinal or snowflake hero; snowflake is the strongest and keeps the 029 look).
5. Ornament: delete the full-width top band (or make it a small branch or garland with clear purpose); add a swirl or star region to the body stripes.
After redraw: rerun gen.py, regenerate all PNG/PDF, run --check, request QA round 2 (re-grade all 9 plus cover).

## Open owner questions (do not block)
1. Logo beside HUDSON BEAT. 2. Owner to flip through some keys so "checked by hand" stays true. 3. Bundle with 027/001 later.
