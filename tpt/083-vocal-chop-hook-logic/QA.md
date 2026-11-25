# QA: 083 Winter Vocal Chop (Logic Pro)

## Findings
- `gen.py --check` passes (before and after fixes). `tools/tpt-validate.py` OK. 26 + 17 = 43 pages agree (UPLOAD.md, tpt.json, cover, text); preview PDF is 4 watermarked pages.
- Math recomputed independently: bar = 240/T and step = 15/T at 80/90/100/110/120/128 BPM (all table cells match, incl. rounding); slice 3 s / 8 = 0.375 s = 3 steps; 16 slices 0.1875 s; hum table 2 to 4 s; pitch ratios 2^(n/12) (+12 2.000, +7 1.498, -5 0.749, +5 1.335, +4 1.260, +3 1.189, -7 0.667, -12 0.500), Hz and durations match, interval names correct; 16-bar arrangement 4 sections x 8 s = 32 s at 120 BPM and the 8/16-bar columns at every tempo; rubric 5 x 5 = /25.
- Drawn grid counted from a 250 dpi crop: bars of 6, 6, 6, 8 = 26 hits; per slice 5,4,4,3,2,2,3,3 = 26, equal to the table; drum grid kick 3, snare 2, hat 8 = 13 matches text; waveform shows 7 slice lines, 8 slices; keyboard maps slices 1 to 8 to 8 neighboring keys; pitch keyboard labels (-12 to +12) correct.
- Class badges and pacing page: Class 1 slides 1-8, Class 2 slides 9-11, Class 3 slides 12-17; every slide badge matches; the three-classes slide carries "Classes 1-3". Step N, page and slide cross-references agree.
- Listing: title 72 chars, "Logic Pro" in first 30, no seasonal word; 4 grades; subjects and tags each checked individually against SUBJECT-OPTIONS.json / TAG-OPTIONS.json (all exact, none are headings); disclosure line in description and terms page; secular theme; no commercial recordings sampled, students use own voice (copyright note honest).
- Viewed: all 26 pages at 110 dpi, all 17 deck slides (60 dpi render), 4 preview-PDF pages, cover.png and preview-1..3.png at full size, 250 dpi crops of waveform and step grid (keyboard map and pitch table viewed on pages 13, 15 at 110 dpi and in preview-3). Cover edges and margins clear.

## Defects found and fixed in gen.py
1. Deck slide 5 (equal slices drawing) said "Slice lines sit at the start of a sound", which is transient slicing and contradicted the drawing; now "Equal slices: lines the same distance apart".
2. Deck slide 12 said "Fewer layers when the hook starts", contradicting the arrangement (the hook has more layers than the intro); now "Add layers as the hook builds".
3. Unsupported Quick Sampler control claims reworded: Logic quick reference no longer says Slice mode "shows a control for how many slices" (now "may offer a way to set how many slices (for transients, a sensitivity control)"); slice map "Equal" row no longer says "you choose how many" (now "aim for 8 or 16; set the number with whatever control your version offers"); slide-9 notes matched.
4. Mic distance "a common starting point" reworded to "this kit's starting range" (source gives 10-30 cm; see below).

## Sources actually fetched
- WebSearch result with Apple Support "Quick Sampler Slice mode in Logic Pro for Mac" (support.apple.com/guide/logicpro/slice-mode-lgcp18515788/mac): search summary supports Quick Sampler Slice mode with Transient, Beat, Equal and Manual placement and a Sensitivity slider. Direct fetch of the Apple page (and of the 10.6.2 copy and the Quick Sampler overview) returned only navigation, so the article body could not be read; the kit keeps "if your version has it" and generic wording, and no specific control name beyond "sensitivity" for transients.
- sampleroll.com "Logic Pro Quick Sampler: Slice and Flip" (fetched): Slice mode splits a sample into slices played from the keyboard, each slice maps across the keys, slices can be reversed individually; supports "slices play from neighboring keys" and the hedged reverse option.
- musosoup.com "How to Record Vocals at Home" (fetched): microphone 10-30 cm from the mouth; peaks near -10 dBFS (consistent with the kit's -12 to -6 dBFS starting point, which a WebSearch of several gain-staging guides also supports as the majority view). The kit words both as starting points to set by ear.
- audeobox.com tutorial: 403, not read. No sample-rate or bit-depth statements appear in the kit. No invented menu paths found (File > New, File > Bounce > Project or Section, X for Mixer, Command-B, Compress are real Logic features; Drummer, Drum Machine Designer, Loop Browser, Step Sequencer, Piano Roll hedged "if your version has it").

## Notes (not blocking)
- Deck slide 17: the reflection box sits close above the footer rule.

**Verdict: APPROVED**
