# QA: 062 Rhythm Dictation Levels 1-3

Independent review. Everything below was read from the rendered pages, not taken from `--check`.

## Commands
- `python3 gen.py --check`: CHECK OK.
- `python3 tools/tpt-validate.py tpt/062-rhythm-dictation-levels-1-3`: OK.
- `git status --short`: only `tpt/_art/USAGE.md` (two usage lines for 062) and the 062 folder.

## What I looked at
- All 26 PDF pages at 110 dpi, full size, one at a time.
- Notation crops at 250 dpi on the Level 3 key pages (23, 24) and the Level 2 key pages. These cover 6/8 groups, sixteenth groups, dotted quarter + eighth, syncopation, whole and dotted half notes, and rests.
- cover.png at full size. All four edges are clean: white top, and the full-bleed black band at the bottom with no cut-off art.
- preview-1, preview-2 and preview-3, and all 4 pages of the PREVIEW PDF.

## Exercise-by-exercise recheck (all 30)
For each exercise I compared script, key notation, student page and bar sum.
- Bar sums: every bar adds to its meter. 4/4 = 4 beats, 3/4 = 3 beats, 6/8 = six eighths. Bar counts are correct.
- Bar counts: Level 1 has 10 x 2 = 20 bars. Level 2 has 2,2,2,3,3,2,4,4,3,4 = 29 bars. Level 3 has 40 bars. That is 89 bars x 2 = 178 points.
- Scoring page (40 / 58 / 80, the 90% and 70% bands) and the tracker totals and per-exercise /4, /6, /8 values all match.
- Script syllables and counts equal the key notation exactly. Examples checked:
  - Level 1: ta, ti-ti, shh, ta-a.
  - Level 2: ta-a-a, ta-a-a-a, ti-ta-ti.
  - Level 3: ti-ka-ti-ka, ti-ti-ka, ti-ka-ti, tam-ti, and the 6/8 syllables ta (dotted quarter), ti-ti-ti, ta-ti, ti-ta.
- The syllable system is consistent. It is defined on the chart pages 5-6, and the 6/8 "ta = dotted quarter" use is explained on page 6.
- Student pages: same time signature and bar count as the key. The blank staves, barlines, final barline and /4 /6 /8 score boxes are correct.
- Level limits are respected:
  - Level 1 uses only 4/4, quarter, quarter rest, eighth pair and half.
  - Level 2 adds 3/4, whole, dotted half and syncopation.
  - Level 3 is four bars each and adds 6/8, sixteenths and dotted quarter + eighth. It also reuses 4/4 and 3/4, which is reasonable.
- No two exercises repeat. Beaming is correct: eighths single-beamed, sixteenths double-beamed, 6/8 in threes. Stems are all up on the one-line staff and attach on the right of the heads. Dots, flags and rests are correct.
- Page headers ("teacher scripts (exercises 1-5)" etc.) match the content. The page, student-page and key cross-references in the footers match the real pages. Tempo and count-in instructions are sensible. 6/8 counts in "1 2 1 2" with the BPM on the dotted quarter, and this is explained.
- US spelling, complete sentences, no internal QA wording. The disclosure line is present on page 26.

## Previews
- Cover and previews agree: 30 exercises, 26 pages, 178 points, and the stated page numbers.
- The preview PDF is watermarked on all 4 pages. The keys shown are the Level 3 exercises 21-25 only, and they are watermarked through the notation. Previews are acceptable.

## Listing
- `tpt.json`:
  - Grades are 4th to 7th, and UPLOAD.md section 3 explains this (the TpT limit is 4 grades; the listing says 3-8).
  - Subjects "Music" and "Instrumental Music" exist in the options file.
  - Tags Worksheets, Printables, Activities, Assessment and Bell Ringers are exact entries.
  - All the files exist.
- UPLOAD.md:
  - The title is 77 characters, with no seasonal words.
  - The page list totals 26 (1+1+1+1+2+6+6+6+1+1).
  - The description matches the PDF.

## Notes (not blocking)
- Syncopation (ti-ta-ti) is drawn with separate flagged eighths. This is accepted practice, and the chart shows the same form.
- The preview keys are small but readable through the watermark. That is by design.

**Verdict: APPROVED**

Required fixes: none.

## Inspector 2026-11-20
Visual inspector (fresh agent, BLOCKING-only brief, complete inventory: 4 of 4 images, 26 of 26 pages, 4 of 4 preview pages viewed at full size, 250 dpi crops of the Level 2 and Level 3 notation): OK, no BLOCKING item. All 30 exercises: bars sum to the meter, scripts match the notation, stems consistent, beaming correct (6/8 in threes). NOTES (not changed): p2 pacing Week 4 says 'three- and four-bar exercises' while Ex16 is two bars, 'Your Turn' bar leaves the box half empty, first barline slightly heavier on some student pages (rasterisation), preview watermark runs behind some captions, blank space under content on p3, p4, p26.
**Verdict: APPROVED**
