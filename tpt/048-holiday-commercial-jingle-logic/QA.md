# QA 048 Commercial Jingle (independent review, round after rescue edits)

Checks run: `gen.py --check` OK; `tools/tpt-validate.py` OK; git status shows only this folder modified (regeneration). All 28 PDF pages (110 dpi), all 15 slides, cover, preview-1..3 and 4 preview-PDF pages viewed at full size.

Findings
- Step numbering vs 7-step project sheet (p21: 1 Choose p11, 2 Plan pp12-13, 3 Build pp14-15, 4 Script p16, 5 Record and mix pp17-18, 6 Bounce p19, 7 Present p25): p13 "Step 2", p15 "Step 3", p16 "Step 4", p17 "Step 5", p18 "Step 5, continued", p19 "Step 6", p25 "Step 7", p26 "FROM YOUR PROJECT SHEET, STEP 7" all match. No stray Step N in deck text, speaker notes, previews, or UPLOAD.md. The previews show only "Step 5, continued" (p18), correct.
- Minor, not blocking: deck slide 5 uses a separate 5-box overview (brief/plan/build/voice/mix) and says "five steps"; it carries no "Step N" label, so no contradiction.
- Caption "VOICE-OVER LINES" fits, centred between the first two pills, not clipped on cover (four edges clean: white top/sides, black bottom bar), p1, slide 1, slide 15.
- p22 NOTES lines clear of footer rule; slides 1 and 15 have no grey box; all slides/pages render cleanly, no overflow.
- Counts: PDF 28, deck 15, preview 4, tpt.json pages 43; zip holds the 3 files.
- UPLOAD.md/tpt.json: grades 9-12 (4 entries), tags Winter/Project-based Learning/Projects/Rubrics, subjects Music/Computer Science - Technology/Music Composition, title 78 chars with "Logic Pro" at start, disclosure line present.
- Maths unchanged: 15 bars at 120 BPM = 30 s, 2+4+6+3, 12-word script, tempo table 80-128, chord tables (7 keys), ducking points; client Fluffwick Snug Wool Socks.

**Verdict: APPROVED**

Required fixes: none.

## Rescue 2026-11-18
Held rescue (step 2b): the four BLOCKING items were fixed in gen.py: step numbers aligned to the 7-step project sheet (p25 'Step 7', plan Step 2, duck 'Step 5, continued', bounce Step 6; --check now fails on a 'Step N' not on the sheet), p22 NOTES lines clear of the footer rule, deck art made transparent (grey box gone on slides 1 and 15), red pills captioned 'VOICE-OVER LINES'. QA re-checked every page, slide and image: APPROVED. Fresh Visual inspector re-checked cover, preview-1..3, all 28 pages, 15 slides and the 4 preview-PDF pages: OK, no BLOCKING item. NOTES (not changed): deck/p5 say 'five steps ... then feedback' while the sheet lists 7 steps (labelled as five steps then finish), cover pill 1 slightly right of the INTRO/VERSE boundary, blank space at the bottom of p3, p4, p14, p17, p28.
**Verdict: APPROVED**
