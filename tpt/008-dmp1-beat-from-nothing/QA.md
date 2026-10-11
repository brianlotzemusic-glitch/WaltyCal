# QA: TpT 008 DMP1 Unit 1, Beat From Nothing (round 1)

QA reviewed this item on 11 Oct 2026, independently of the Designer. I read the full text layer of the 21-page PDF, the 15-slide deck (every text box and speaker note, extracted from the .pptx) and the 4-page preview PDF. I rendered the PDF at 40 dpi, the deck PDF at 50 dpi, the .pptx through LibreOffice at 50 dpi (this machine has no Oswald, so it shows fallback-font behaviour), the preview PDF at 40 dpi, and cover.png plus preview-1..3.png as a sheet. I compared the content with the owner's Drive docs (Project Sheet & Rubric, Teacher Notes, Day 1 post, read-only). I ran `gen.py --check` (CHECK OK). I changed no item files.

## 1. Faithful to the owner's content and voice: pass

- The 14-term vocabulary, requirements, 8 steps, tips, 9-item submission checklist and the 5 x 4 rubric text match the owner's Drive docs nearly word for word. The "Score 2-5 per category, total / 25" rubric is intact.
- Teacher notes (reinforces, five struggles, variations, resources) and the "What is a loop / feel it before you name it" Day 1 flow are the owner's, in the owner's voice ("What the heck is a loop?", "Can you nod your head to it?", "turn things down, not up").
- Deliberate changes, all reasonable: the owner's docs say 5 days and the Restructure doc says 4, and the product is 4 days with a stated 5-day split of Day 3; Google Classroom and Padlet became "your class page" and "Padlet or any feedback board"; Day 3 and Day 4 were merged. The owner's "layering rules" line (one bass sound, don't stack full drum beats) was dropped. That is minor and optional to restore.
- Added material (4-day minute blocks, listening key, worked example beat, sample mix, NCAS codes) is plausible, modest and labelled "one possible answer".

## 2. Usable by a teacher: pass

- Each day has minute blocks that add to 53, a goal, what to show and which student page to use. A fifth-day option, circulating prompts, a setup checklist and a "before Day 1" list are included. Page cross-references are right (the check confirms them).
- Rubric /25 is intact with Self and Teacher columns; the answer key (kit labels, listening grids, vocabulary quick check) agrees with the worksheets.
- Logic Pro steps are correct and not overclaimed. Checked: Electronic Drum Kit in the Library loads Drum Machine Designer; Control-click then Create Pattern Region; double-click opens the Step Sequencer; C toggles Cycle; Command-D, Command-R, X for the Mixer, Y for the Library and Command-B for Bounce are right. Step Sequencer needs 10.5 or later, which the setup page says. A footnote says menu names may differ by version, and Logic is described as a trademark used only for compatibility.
- Slide-level grids and the Billie Jean grid (hat eighths, snare 2 and 4, kick 1 and 3, 116 BPM) are labelled "simplified teaching charts, not transcriptions", which is the right claim.

## 3. No school branding, student names or copyrighted media: pass

- Grep of the resource PDF, deck PDF, preview PDF and every .pptx text box and note for Blind Brook, BBHS, blindbrook, logo: no hits. No student names or work (the Drive folders do hold student files; none were used).
- The only media in the .pptx is `ppt/media/image1.png`, the drawn drum-kit illustration (original art). No audio, video, lyrics or album art anywhere.
- Billie Jean (Michael Jackson), Closer (The Chainsmokers) and When the Levee Breaks (Led Zeppelin) appear by title and artist only, with a find-it-on-YouTube/Spotify note on deck slides 2 and 9, in the Setup page, in the pattern page footer and on the terms page. Padlet, YouTube and Spotify are named only as examples.

## 4. Deck pattern, notes and look: pass, with a font-fallback caveat

- Pattern is complete: hook (slide 1-2, "Feat. Billie Jean"), definition (3), guided listening questions (2, 5), worked example (6, 9), steps (10, 12), deliverables (13), rubric (14), plus the owner's "One last thing" closer. 15 slides, 16:9, text-light with grids and a drum-kit drawing.
- Speaker notes are present on all 15 slides and are real teaching notes (pacing, what students will say, what to reveal).
- Hudson Beat look: HUDSON BEAT line on every slide, Oswald caps titles, Source Sans body, black, white and one red accent. The deck PDF reads cleanly at 50 dpi with no clipping.
- Caveat (not blocking): the .pptx does not embed fonts. In my LibreOffice render without Oswald, slide 4 "PERCUSSION" wraps to "PERCUSSIO / N", slide 15's "Closed hi-hat" and "Open hi-hat" row labels collide, slide 1's title runs to both slide edges, and slide 14 labels wrap tightly. A teacher opening the .pptx in PowerPoint without Oswald will see the same. The description and page 2 already tell them to install the fonts or use the PDF copy.

## 5. Cover and previews: pass, with polish notes

- cover.png and preview-1..3.png are 2000 x 2000 with the HUDSON BEAT line, a heavy caps headline and a black band. Art is original (drum machine grid, page shots of the real resource). The title is readable at thumbnail size. Preview PDF has 4 watermarked pages (pacing, project sheet 1, listening grid, rubric), matching UPLOAD.md.
- Polish (not blocking): cover.png and preview-1 leave about the bottom quarter of the frame empty above the black band, so they look lighter than the other items. The PDF cover (page 1) orphans the word "PRO" on its own line ("DRUM PROGRAMMING IN LOGIC / PRO"); cover.png has it on one line.

## 6. tpt.json and UPLOAD.md: pass

- Title "Beat From Nothing | Logic Pro Drum Programming Unit | High School Music Tech" is **76 characters** by my own count (UPLOAD.md says 76, limit 80) and matches the code block.
- price and license_price "9.00"; tax_code "Other Digital Goods - No Physical Media" (same as 006/007); grades 9th, 10th, 11th, 12th (4); subjects Music (1); tags 1 ("Autumn"); formats PDF; `pages` 36 = 21 + 15. All six `files` exist. The ZIP holds exactly the three files, byte-identical to the item folder ones (cmp checked).
- Description proofread: no typos; the page counts (3+3+2+9+2 = 19, plus cover and terms = 21) and claims match the PDF. The disclosure line closes the description and is printed on page 21. The Logic trademark line is present.
- Notes: the grade slugs `9th-grade` to `12th-grade` and the PDF-only format are unproven against TpT's form; UPLOAD.md already says to run `--dry-run` first. "Autumn" is a loose tag; fine.

## Recommended fixes (all optional, do not block release)

1. gen.py: shorten or reduce the PDF cover line so "PRO" does not orphan.
2. Deck: widen the "PERCUSSION" tile and the slide 15 grid label column, and keep slide 1's title inside the margins, so the .pptx survives font fallback.
3. Cover and preview-1: move the art down or enlarge it to fill the dead space.
4. Optional: slide 8's note says "Day 1 close or Day 2 launch" while the Day 2 plan teaches the grid at launch; one sentence in the Day 2 plan pointing to slide 8 would tie them together. Restore the owner's layering-rules line if wanted.

**Verdict: APPROVED**
