# QA 049 Practice Log & Practice Bingo

Independent review. Checks run: `gen.py --check` OK; `tools/tpt-validate.py` OK; `git status --short` shows only the 049 folder as new.
All 15 pages (110 dpi), cover, preview-1/2/3 (full size) and all 4 pages of the PREVIEW PDF were looked at.

## Findings
- Bingo boards: read from the rendered pages. Each of the 4 boards has 24 distinct numbered challenges plus FREE in the centre. Boards 1 and 2 share 1-8, 1 and 3 share 9-16, 1 and 4 share 17-24, 2 and 3 share 25-32, 2 and 4 share 33-40, 3 and 4 share 41-48. So every challenge is on exactly 2 boards and any two boards share 8. No two boards are identical.
- Caller sheet "Boards" column matches the squares (spot-checked 12, 15, 25, 33, 41, 47). The small square numbers match the list.
- Tracker: days 1-30 in 5 week rows (7+7+7+7+2) with week totals and a 30-day total. Goal table 10/15/20/30 x 30 = 300/450/600/900 is correct. Teacher "minutes at a glance" x7 and x4 is also correct (70/280, 105/420, 140/560, 210/840).
- Grading ideas: 40 + 30 + 20 + 10 = 100.
- Wording: instrument-neutral, suitable for grades 4-8, challenges safe and sensible. No brands or songs. Parent note is friendly and makes no money demands. US spelling. Step numbers and page references (11-14, 5-8, pages 2-15) are correct. No internal QA wording. The disclosure line is on the terms page and in UPLOAD.md.
- Layout: nothing clipped or overlapping, the preview is watermarked on every page, and the cover and previews read well at full size. The cover has no notation.
- tpt.json: files exist, grades 4th-7th (UPLOAD.md explains that TpT allows four and the product is written for 4-8), subjects Music / Instrumental Music / Vocal Music and 6 tags are valid entries. UPLOAD.md title is 78 characters, and the page list totals 15.
- Minor, not blocking: the tracker header says "weekday" in tiny grey print as a write-in placeholder; the Week 1/Week 2 label cells in the grey column have no divider line.

**Verdict: APPROVED**
