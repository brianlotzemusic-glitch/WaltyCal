# QA: 042 Winter Music Escape Room (round 3: cover art notation fix)

Reviewer: independent (did not build or fix). Scope: the reported defect in the cover globe art (stems floating a head-width right of the heads, a note on the middle line stem-up, a snow dot on the clef) and a regression check of everything else.

## Checks run
- `git status`/`git diff --stat`: touched files are cover.png, winter-music-escape-room.pdf, winter-music-escape-room-PREVIEW.pdf, build/cover.html, build/resource.html, gen.py. Nothing else changed. The working-tree diff to gen.py is one line: a missing `:` on the snow-dot `for` loop (the comment had swallowed it), so the committed gen.py could not run until this fix. It now runs.
- `python3 gen.py --check`: CHECK OK (FACADE, CABBAGE, 12, FROSTING, SNOW GLOBE; lock code 4,2,9,7,1 -> MUSIC; 1 of 243 card combos opens the lock; 16-page PDF, 4-page preview, one watermark, no answers; images 2000x2000; layout clean; UPLOAD.md and tpt.json ok). `tools/tpt-validate.py`: OK.
- cover.png viewed at full 2000 px and zoomed 2x on the staff and notes: both stems touch the right edge of their heads and rise cleanly; both heads solid black; nothing touches the clef, notes, stems or staff.
- Product PDF page 1 rendered at 110 dpi and zoomed: same art, correct, with the PDF's own cover layout (full-bleed footer bar, subtitle with "teacher guide and answer key").
- Pixel diff of product PDF pages 1-16 at 110 dpi against HEAD: only page 1 differs, and only inside the globe's notes area. Pages 2-16 identical.
- PREVIEW PDF: all 4 pages rendered at 110 dpi and viewed (teacher guide p3, Puzzle 1, Puzzle 3, final lock). Pixel-identical to the HEAD preview; the preview contains no cover page, so the file's byte change is only a rebuild. Watermark present, no answers. preview-1..3.png are unchanged in git (identical to HEAD).
- Cover.png vs HEAD: differs only in the box around the two notes.
- Puzzle notation on preview pages (Puzzle 1 staff, Puzzle 3 bars): stems, heads and ledger lines look correct and unchanged.

## INVENTORY (cover.png, globe art, top to bottom)
Black base trapezoid; light-blue stripe on base; white rim plate with black outline; globe circle (pale blue fill, thick black outline); white snow-bank cap at the globe's lower third with black arc; white highlight arc at the upper left; 5-line staff (lines at y=118, 132, 146 [middle], 160, 174); treble clef (G-clef curl on line 2, y=160); note 1: black filled quarter note, head in the space between line 2 and the middle line (A4), stem UP, attached to the head's right edge; note 2: black filled quarter note, head in the space between line 1 and line 2 (F4), stem UP, attached to the head's right edge; 5 blue snowflakes (sizes 20, 14, 13, 17, 10) in the globe; 9 white snow dots (none on the clef, notes, stems or staff; the nearest, at (236,92), is about 7 px above the note-1 stem top and clear); blue padlock (shackle, body, keyhole) over the base; text: HUDSON BEAT, WINTER MUSIC, ESCAPE ROOM, subtitle, footer bar "GRADES 3-6 / 5 PUZZLES / 16 PAGES". No note sits on or above the middle line, so up-stems are correct for both.

## Findings
None blocking. Minor, optional: the snow dot at (236,92) sits directly above the note-1 stem and reads slightly like a stray flag at thumbnail size; moving it a few px sideways would remove any doubt. The "teacher guide and answer key" subtitle appears in the PDF cover but not on the 2000 px cover.png; this was already so before the fix and is not part of the defect.

**Verdict: APPROVED**

Required fixes: none.
