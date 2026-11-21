# QA: 066 Music Symbols Scavenger Hunt

**Checks run**
- `gen.py --check` passes (before and after fixes). `tools/tpt-validate.py` OK.
- Independent recount from the rendered resource.html (own script): scene totals 21, 21, 21, 23, 22, 22 = 130. Per-type counts on the student pages, hunt lists and answer keys match the scene definitions. I also counted scenes 4 and 5 by eye on the 110 dpi renders.
- Score page: 7+7+7+8+10+10 = 49, plus tempo 15 and dynamics 18 = 82. Review key total 33 = 15 + 18. Rubric bands cover 0-82.
- Review keys are correct. Tempo: largo = very slow, andante = walking, moderato = medium, allegro = fast and lively, presto = very fast, order 1-5 correct, BPM ranges are standard. Dynamics: p, mp, mf, f order 1-4, hairpins louder/softer, letters f/p/mf/mp.
- Viewed all 21 pages at 110 dpi, the 4 preview-PDF pages, cover.png and preview-1..3.png. Notation: stems on the right going up and on the left going down, clefs, rests, fermata, accidentals and hairpins are correct. No symbols are clipped by the scene boxes.
- Listing rules: UPLOAD.md says 21 pages, matching the PDF. Title is 63 characters with no seasonal word. Tags, subject and grades (3) are valid. The disclosure line is present. US spelling is used.

**Defects found and fixed in gen.py**
1. Dynamics review part B said "under" the symbol, but the boxes sit beside it. It now reads "in the box by".
2. The cover subtitle (PDF and cover.png) said "Find, count and color". It now says "Find, circle and color". The UPLOAD description and teacher notes already said "circle it in a color", so the "Find & Color" title stays accurate because students also color the hunt-list circle and the scene.

**Notes (not blocking)**
- Some hidden symbols sit on line art (sleds, snowman arms, hill lines in scenes 4 and 6). They stay findable and countable.
- There is a blank band between the instructions and the scene box on the scene pages.

**Verdict: APPROVED**
