# QA (round 2): 045 Winter Soundscape (Logic Pro kit)

## Checks run
- `gen.py --check` OK; `tools/tpt-validate.py` OK; `git status --short` shows only `tpt/045-winter-soundscape-logic/` as new.
- Rendered all 28 PDF pages (110 dpi) and all 15 slides and looked at each at full size; also cover, preview-1/2/3 (2000 px) and the 4-page PREVIEW PDF. Nothing clipped, overlapping or behind footers. One watermark per preview page; cover reads at thumbnail size. No music notation anywhere (waveform, snowflake, curves, frequency map only).
- Round-1 defects now fixed: p4 sentence reads correctly; p9 Fade row says "the wind, the pad and a few quiet chimes are left" (matches the map); p13 and p27 clear the footer; p19 layer-map columns and borders are clean; p20 has bar numbers on all four lanes; p22 and p23 file name is "Your Name - Winter Soundscape - Scene" (matches p26 and slide 12); p25 vocabulary boxes are evenly spaced; p26 rules are evenly spaced; rubric score 4 now says "Alchemy used for at least two" (matches the requirements); slide 2 box has no gap. Slide 15 reflection box sits just above the footer rule, not touching.
- Worked example recomputed: 240/120 = 2 s a bar; 30 bars = 60 s; sections 4+10+8+8 = 30 (8+20+16+16 s); moments bar 5 = 0:08, 9 = 0:16, 15 = 0:28, 23 = 0:44, 27 = 0:52 (time = (bar-1) x 2). Layers: hush 3, peak 7 (chimes absent), last four bars 3. Lane points on p16 (bars 5/14/15/22/30 = 0:08/0:26/0:28/0:42/0:58) correct. Length helper values correct.
- Rubric 5 categories x 1-5 = /25 on p24, slide 13, p2, p3, p5 and the preview.
- Zip holds the 3 files, each byte-identical to the folder copy (cmp). tpt.json: grades 9-12, subjects Music / Computer Science - Technology / Music Composition, tags Winter / Project-based Learning / Projects / Rubrics (no headings), pages 43, files exist. UPLOAD.md: title 79 chars, no seasonal word, disclosure line present, 1+9+17+1 = 28 pages + 15 slides = 43, matches tpt.json, cover text "28 pages + 15 slides", PDF/deck/preview counts. Page references (pp. 9-10 example, 14, 15-17, 18, 19, 20, 24, 27; slides 1-6/7-8/9-11/12-15) agree with the pacing page.
- Logic features unchanged from round 1 and real (Alchemy, Quick Sampler, Retro Synth, Auto Filter, ChromaVerb, Space Designer, Channel EQ, A for automation, Y Library, X mixer, Command-B bounce); Step FX and Stereo Spread are hedged.

## Minor, non-blocking
- Page 9 boxes "1 - A weak plan" and "6 - Checking the numbers" have empty space inside (cosmetic).
- Slide 1 art has a faint off-white rectangle behind it on the white slide; barely visible.

**Verdict: APPROVED**

Required fixes: none.

## Fix round 16 Nov 2026 (HELD, not released)
Two fix rounds spent. Fixed: frequency caption and arrows explained, cover waveform now Hush/Build/Peak/Fade, credits line, "3 or 4 classes", step numbering, rubric Layers/Automation/Storm Arc cells differentiated, whiteout-hiss and shimmer cards consistent with the worked example, ice-crackle loop wording, brief page lines, spacing on p13/p19/p27, deck slide 8 caption and slide 13 line, deck order Scene-Arc-Layers-Automate-Space.
Still listed by the last inspector (real): deck slide 8 bottom-left bullet "High-pass every layer; the rumble gets a very low one" wraps into the footer rule (also preview-2 tile); p6 "slide 7 shows layers entering and leaving" should cite slide 10; p5 three-class merge advice overloads Class 3; p6 "every layer except the rumble" contradicts the rumble high-pass (25 Hz) elsewhere. Nits: worked example has 4 lanes but rubric 5 needs five; p13 intro says cards 5-8 appear at the peak but chimes do not.

## Fix round 16 Nov 2026 (final, new inspector brief)
Further fixes after the earlier rounds: deck slide 8 bullet shortened (no longer runs into the footer rule); teacher-notes slide reference now slide 10; three-class advice made realistic (two automation lanes, short presentations, reflection as homework); rumble high-pass wording made consistent (every layer, rumble very low). Fresh inspector with the BLOCKING/NOTES brief (cover, previews, 28 pages, 15 slides, 4 preview pages): no BLOCKING item. NOTES: three-class box relaxes the four-parameter requirement; ice pan values 50-80 do not widen on the last swing; small chart text on slides 8 and 10; blank band on slide 9.

**Verdict: APPROVED**
