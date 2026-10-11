# QA: TpT 007 Music Sub Plans K-5 (round 1)

QA reviewed this item on 11 Oct 2026, independently of the Designer. I rendered all 25 resource pages at 60 dpi as two contact sheets, pages 5, 10, 11 and 22 at 90 dpi, one 130 dpi crop (p11 Part B bar 4), the 4-page preview PDF at 40 dpi, and `cover.png` plus `preview-1..3.png` as a 2x2 sheet. I read the full text layer with `pdftotext`. I did not run `gen.py --check` and changed no item files.

## 1. Usefulness for a substitute with no music training: pass

- Each day plan has a Goal / You need / Copies header, timed steps (5/10/15/10 min) and italic "Say:" lines, so the sub never has to improvise. Each plan also has "Extra time?" and "Short class?" fallbacks.
- The sub-tub setup (teacher notes, p2), welcome sheet (p3), days-at-a-glance with a 7-game bank (p4), and a sub report form (p24) cover the practical side.
- No tech: the only materials are pencils, worksheets, an eraser and everyday objects. A text search for video, app, QR, speaker and similar words finds nothing.
- Every rhythm on the chart and on the sub plans has ta / ti-ti / shh / ta-a syllables under the notes, with a key line, so the sub can lead echo clapping without reading music.
- Cross-page references are right. Day plans point to pages 7/8, 10/11, 13/14, 16/17 and 19/20, and these are the real worksheet pages. Key pointers (pages 22 and 23) are right.
- No copyrighted songs or lyrics. The only poem-like text is an original four-line thunder/raindrops chant. Terms page follows STYLE.md section 6.

## 2. Musical accuracy: pass

I checked every rhythm by hand from the renders, not only from the Designer's data.

- **Rhythm chart (p5), 8 lines.** Every bar is 4 beats: lines 1-4 are 3+1 rest, 1+1+1+1 types, and lines 5-8 are two-bar lines that each add to 4 (half+q+q | 4 eighths+half, q+2 eighths+q+2 eighths... all checked). Syllables match the notes (ti-ti = two beamed eighths, shh = quarter rest, ta-a = half, ta-a-a-a = whole). Beaming and stems are correct.
- **Readers (p10), Part A.** Claps 4, 5, 2, 6, 8, 4 match the drawn bars and the key. Rests are correctly not counted. Part B: dog = quarter (C), tur-tle = eighth pair (A), shh = rest (B), sun = quarter (C). The key matches.
- **Rhythm Math (p11) Part A.** Sums are 4, 4, 5, 3, 4, 7 and the key matches. Part B: YES/NO answers are YES 4, NO 3, YES 4, NO 5 (bar 4 is 1+1+1+2, confirmed at 130 dpi), NO 5, YES 4, and the key matches. Part C: "ta ti-ti ta-a" and "ti-ti ta shh ta" are correct, and both bars are 4 beats.
- **Day 4 word rhythms.** cat = ta, piz-za = ti-ti, shh, dog = ta, ap-ple = ti-ti. The syllable counts match the words. Composer page example (ta, ti-ti, shh, ta-a, ta-a-a-a) uses correct beat counts.
- **Dynamics (Day 3).** pp to ff meanings (D F B H G A), crescendo and decrescendo (E C) are right. Tempo ladder is largo 1, adagio 2, andante 3, moderato 4, allegro 5, presto 6, which is right.
- **Word search (p20).** Grid is 12 x 12. I traced CRESCENDO, FORTE, PIANO, TEMPO, MELODY, TREBLE, BEAT and DYNAMICS against the key positions and all are correct.
- All music is in 4/4 with quarter, eighth-pair, quarter-rest, half and whole values only, which suits K-5. No keys or clef issues arise (rhythm only, one-line staff).

## 3. Age fit K-5: pass

- K-2 sheets use tracing, circling, counting and word-matching. 3-5 sheets use rhythm math, composing, word search and short written answers. The split is sensible and gives the sub two levels per class.
- Content is calm and generic: no scary themes, no characters or brands. Games such as Poison Rhythm are ordinary classroom games with original directions (the "poison" is just a rhythm line the class does not echo).

## 4. Layout, legibility and print: pass

- 25 pages, all US Letter. Oswald, Source Sans 3 and Bravura are embedded (`pdffonts`).
- Nothing overflows or clips. Footers are normal on every page. At 60 dpi the plans, tables and notation read well. At 90 dpi the notation, syllables and answer boxes are crisp.
- Black-and-white friendly. The accent teal is used only for syllables, tags and key answers.
- Answer-key pages 22 and 23 are dense but legible and not clipped.

## 5. Cover and preview images: pass

- `cover.png` and `preview-1..3.png` are 2000 x 2000. All show the HUDSON BEAT store line, a heavy caps headline, a light subtitle and a black band. The title is readable at thumbnail size.
- Cover art (clipboard, pencil, f and p, a rhythm line) uses only teal and black on white, with no borders or photos, so it matches STYLE.md and the owner's store look.
- Previews: what is inside, two levels side by side, and the contents grid. The watermarks are clean and the black borders and hard shadows follow STYLE.md. (Image art is code-drawn, which is the rule for TpT.)
- Preview PDF has 4 pages (Day 2 plan, rhythm chart, Day 3 Dynamics and Tempo 3-5, Day 2 key), each watermarked, and matches UPLOAD.md.

## 6. tpt.json and UPLOAD.md: pass

- Title: "Music Sub Plans K-5 | 5 No-Prep Emergency Days | No Tech Worksheets & Games" is **75 characters** by my own count, and UPLOAD.md says 75. Limit is 80.
- price and license_price are both "7.00". The net of about $3.55 (7.00 x 55% - 0.30) is right.
- tax_code is "Other Digital Goods - No Physical Media", the same as item 006.
- Grades: 4 (kindergarten, 2nd, 3rd, 5th). K-5 spans six grades, so TpT's 4-box limit forces a choice, and the selection is valid (1-4). It marks both ends and the K-2 / 3-5 split, and UPLOAD.md explains this. Subjects: 1 (Music). Tags: 1 (Winter). Formats: PDF.
- All 6 `files` exist. `pages: 25` matches the PDF. The description page breakdown adds up (2+1+1+1+5+10+1+2+1+1 = 25).
- Description proofread: no typos found. The claims (5 days, 8 echo lines, 7 games, 10 worksheets, 12-word search, keys for Days 2, 3, 5) all match the PDF. The disclosure line is the last line of the description and is also printed on p25. The standards claims are modest.

## Optional, not blocking

- Grades: 1st and 4th are not ticked, so a search filtered to those grades will miss it. The UPLOAD.md note already says to tick them by hand if the form allows. Consider 1st, 3rd, 5th plus kindergarten only if the owner wants to test other combinations.
- Tag "Winter" is a loose fit for a year-round sub pack. UPLOAD.md explains the choice and says it can change if TpT offers a sub-plans tag.
- preview-2: the "GRADES 3-5" page overlaps the right edge of the K-2 page. This is cosmetic.

**Verdict: APPROVED**
