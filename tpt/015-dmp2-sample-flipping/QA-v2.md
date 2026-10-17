# QA: TpT 015 DMP2 Sample Flipping (round 1)

**Superseded: this file is the review of the earlier build and is no longer current. The kit was rebuilt on 17 Oct 2026 (Reflection page added to every DMP2 kit). It needs a new QA pass; no approval is on record.**

QA reviewed this item on 15 Oct 2026, independently of the Designer. I ran `gen.py --check` (CHECK OK; `git status` shows it rewrote nothing), extracted the text of the 21-page PDF, the 17-page deck PDF and the 4-page preview PDF, read every slide's text and speaker note from the .pptx (python-pptx), rendered all 21 PDF pages and all 17 deck pages as contact sheets (40 dpi) and viewed cover.png and preview-1.png at full size. I compared the owner's text with the Drive docs (read-only): "Sample Flipping - Project Sheet & Rubric" (modified 26 Mar 2026) and "Sample Flipping - Teacher Notes". I changed no item files.

## 1. Faithful to the owner's content: pass
- **Rubric is the owner's, /25.** All 25 descriptors, the scoring line, the score lines and "Final Grade = Average of Student + Teacher = ___ / 25" match the Drive text (page 18; checked by string match, the one miss was a hyphen line wrap). The owner's "no reflection" descriptor is kept; the Designer notes on page 8 that the sheet has no reflection task and raised it as an owner question.
- **Kit tips are labelled separately.** Page 8 "How to grade": the owner's rubric line comes first, then the three tips under the italic label "Suggestions from this kit, not part of my rubric:". Page 8 "New in this kit" lists the grading suggestions.
- Overview, 4 goals, 4 vocabulary terms, 6 requirements, 7 steps, 4 tips, 5 checklist items, 4 struggles, variations, resources, pacing and closing note match Drive except for the disclosed changes.
- **"What changed from the original" (page 9) lists the changes**: LMS name to "your class page", requirement 1 and the sample-set resource reworded because no samples are included, page numbers added to steps 1-3, YouTube resources by title only, "Classes 3-5" row split, rubric layout, and the deck's shortened wording (slides 8, 11, 12, 13). It has a "Kept as I wrote it" list that is true. The phrases "word for word", "word by word" and "verbatim" appear nowhere (PDF, deck, notes, UPLOAD.md, tpt.json).
- The older 2023 "Project Outline" (10 classes, 4-row /20 rubric) was correctly not used; the 7-class, /25 sheet is the current one.

## 2. Third-party media and the 50 samples: pass
- **No samples bundled.** The ZIP holds exactly three files (PDF, .pptx, deck PDF), each byte-identical to the file in the folder. The .pptx media is three original PNG drawings (no audio, video, fonts). The repo has no .wav/.mp3/.aif/.m4a/.flac files. The only ".wav" hits in the PDF/deck are the student submission format (".mp3 or .wav"). the owner's unsellable sample-pack title appears nowhere in the product.
- The kit's page 4 tells teachers to build their own cleared sample set (record it, public domain, CC0, licensed), with a "Is it cleared?" table and sampling-ethics page. The wording "my class set has 50" is disclosed on page 9. No song, lyrics, chart data or commercial audio is named; the tip line "J Dilla, Kanye, Madlib" is the owner's own tip (artist names only). Apple trademark and Padlet/YouTube named as tools only.
- No the school name and initials, school branding, student names or the LMS name (grep of PDF text, deck, notes, UPLOAD.md, tpt.json). Footers: "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".

## 3. Music facts and logic: pass
Practice sample 9.6 s = 4 bars at 100 BPM (2.4 s per bar), 8 slices of 1.2 s = 2 beats each; start times 0.0-8.4 s correct; the flip order 1,1,4,2R,6,3R,5,8-down-12 gives 8 slots in 4 bars with bar starts 0.0/2.4/4.8/7.2 s; the drum grid (kick on 1, "and" of 2... as drawn, snare 2 and 4, eighth hi-hats) matches page 11 and slide 9. Logic steps (Quick Sampler Classic/One Shot/Slice, Reverse, Drum Machine Designer, Step Sequencer, EQ, bounce) are right for Logic Pro 10.5+. "Logic" is stated as the tool; other DAWs only as "ideas carry over".

## 4. Layout and text fit: pass
All 21 pages and 17 slides rendered with no overflow, clipping, empty pages or typos found. Deck text reads cleanly at all sizes; every slide has a CLASS badge (slide 1 reads CLASS 1 in its band, slide 5 has the working-day Class 5 black badge). Polish only: slide 2's black box has a large empty area below its headline; page 12 student sample log and pages 13-14 have empty lower space (normal for fill-in pages); slides 9 and 17 have small captions. Not blocking.

## 5. Deck: pass
Hook (before-and-after), plain-English definition (slide 3), ethics (slide 5), two worked examples (7, 9), three demos (8, 10 plus the step slides), steps, what to turn in and rubric (14-15), presentation day and a close. Speaker notes on all 17 slides (243-367 characters), real teaching notes. 16:9. Hudson Beat look; the gold accent is a single accent, as STYLE.md requires.

## 6. Cover and previews: pass
cover.png, preview-1..3.png are all 2000 x 2000. Cover has the HUDSON BEAT line, the waveform art in black and the one accent, a large two-line SAMPLE FLIPPING title and a black band "GRADES 9-12 · 7 CLASSES · 21 PAGES + 17 SLIDES". preview-1 uses watermarked pages with deliberate crops. Preview PDF has 4 watermarked pages.

## 7. tpt.json and UPLOAD.md: pass
- Valid JSON. price and license_price "12.00"; tax_code "Other Digital Goods - No Physical Media"; grades 9th-12th (4, as METADATA-GUIDE prescribes); 1 subject (Music); 1 tag (Autumn, proven value); formats PDF; pages 38 = 21 + 17; all six `files` exist; `zip_contents` matches the ZIP exactly. No `release` or `uploaded` file.
- Title "Sample Flipping in Logic Pro | Quick Sampler Project | High School Music Tech" = 77 characters (limit 80); "Logic Pro" is within the first 30 characters of the keyword block. Description follows the guide's SEO opening, trademark line and the disclosure line last. Page counts in the description (11 teacher + 9 student + cover/terms = 21) are right.
- UPLOAD.md says plainly that no samples are in the ZIP.

## Open questions for the owner (not blocking release, product contains no samples)
1. Who made the 50 samples in Drive, and under what license? (If they are the owner's own, a later version could add them.)
2. The rubric's "reflection" wording has no reflection task on the sheet (kit leaves it as written, page 8 says so).

No required fix remains.

Previous verdict (before the Reflection page was added): approved.
