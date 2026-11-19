# QA: 061 Snow Day Film Score (independent review)

## Checks run
- `gen.py --check`: CHECK OK. `tools/tpt-validate.py`: OK. `git status`: 061 folder plus tpt/_art bookkeeping only (USAGE.md, next/INDEX.md, next/snow-day-film-score removed); dmp2.py untouched.
- Viewed all 25 pages and all 14 slides at 110 dpi, the cover and the 3 preview PNGs (edges are clean: white top, black band bottom, hero art is transparent RGBA with no box), all 4 preview-PDF pages (watermarked), and 250 dpi crops of the 3 storyboards (15 frames), the timelines and the worked-example map. Nothing clipped, overlapping or truncated.
- Hit-point calculator: recomputed all 60 cells (bar number to 2 decimals half-up, bar . beat via the nearest-sixteenth rule) at 80/96/100/120/128 BPM for 2,4,5,6,8,10,12,14,15,16,18,20 s. All match. Seconds per beat/bar, beats and bars in 20 s all match. The rounding rules and the beat numbering (beat 1.25 = a sixteenth after beat 1) are stated on pp. 15-16.
- Worked example (invented skating scene, 96 BPM, 2.5 s/bar): 2.5 s = bar 2 beat 1, 6.25 s = bar 3 beat 3, 12.5 s = bar 6 beat 1, 17.5 s = bar 8 beat 1; 4/10/20/28 beats; 20 s = 8 bars. The five-tempo table (off-by 63/50/39 ms, 120 BPM beat/half/beat/beat) is correct. Mood sections 2.5/10/5/2.5 s = 1/4/2/1 bars match the map. Deck slides 7 and 10 and their notes agree.
- Storyboards: 3 x 5 frames x 4 s = 20 s, with matching timelines. Rubric: 5 x 1-5 = /25 on p. 21, slide 12, pp. 2, 3, 7 and UPLOAD.md. Pacing: 3 classes (slides 1-6 / 7-9 / 10-14) agree with the slide badges, the page badges and the pacing table. The 2- and 4-class options are stated on p. 5 and in the notes.
- Step N: Steps 1/2/3/5/7 on the student pages agree with the 7-step project sheet. Page cross-references checked (11-13, 14, 15, 16, 17, 21, 24, 8, 9-10): all correct.
- Logic Pro wording: File > Open Movie (confirmed in Apple's manual, hedged with "wording can differ by version"), the Movie global track, marker track and plus button (hedged "if your version has one"), Alchemy/Retro Synth, Quick Sampler, Drum Machine Designer, A for automation, X for Mixer, Command-B Bounce: all real or hedged. No invented menu paths. Phone .mov/.mp4 import is stated as "usually import; convert in a video app first if not", which is acceptable.
- No copyrighted film, character or melody. US spelling. No internal QA wording in buyer-facing text (the AI disclosure line is present).
- tpt.json: grades 9th-12th (4), subjects and tags are exact non-heading entries, all files exist. The zip holds the 3 files. UPLOAD.md: title 74 characters, "Logic Pro" at character 0, no seasonal word, disclosure line present, 25 + 14 = 39.

## Minor nits (not blocking)
- Page 9 and the bottom of page 25 have some blank space. Slide 2 has a gap inside the black box.
- The wording "Four classes: keep Classes 1 and 2" is fine as written.

**Verdict: APPROVED**

No required fixes.

## Inspector 2026-11-19
First inspector pass found one BLOCKING item (p24 'Oral reflection' box fused to the footer rule); fixed in one round (10px padding above the footer rule on every page, new --check that fails on any content box closer than 8px to the footer rule; it had flagged pages 7, 20, 24 and 25). Second, complete inspection (every one of 4 images, 25 pages, 14 slides and 4 preview pages viewed at full size, with 250 dpi crops of the footer gaps, storyboards and timelines): OK, no BLOCKING item. NOTES (not changed): slide 14 reflection box ~25px above the rule, slide 10 'Mood changes at the hit points' is a loose summary (HP2 sits inside JOY), storyboard 2 frame 3 middle tree trunk floats above the ground line, half-empty pages/slides, uneven ruled-line thickness from anti-aliasing, p20 last notes line close to the footer rule.
**Verdict: APPROVED**
