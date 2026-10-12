# QA: TpT 009 DMP1 Unit 6, Spooky Tunes (round 1)

QA reviewed this item on 12 Oct 2026, independently of the Designer. I read the full text layer of the 31-page PDF, the 16-slide deck (every text box and speaker note, extracted from the .pptx, plus the 16-page deck PDF) and the 4-page preview PDF. I rendered the PDF at 40 dpi, the deck PDF at 50 dpi, the preview PDF at 40 dpi, and cover.png plus preview-1..3.png as a sheet. I checked .pptx font sizes with python-pptx. I compared the content with the owner's Drive docs in "5 - Spooky Project" (Project Sheet & Rubric, Teacher Notes and Day 1 post were found and read; the How to Bus doc ID in the inventory is truncated, so I checked its content only through the product). Drive was read-only. I changed no item files.

## 1. Faithful to the owner's content and voice: pass

- Requirements, 11-item vocabulary (plus 3 added terms: minor key, half step, scoring to picture), the "Composing to Picture" table, tips, Day 1 post and the 5 x 5 rubric text follow the owner's docs closely. The rubric is intact: 5 categories, scored 2-5, total / 25.
- Deliberate changes, all reasonable and disclosed on page 10 ("How this kit differs from my classroom version"): Scarlett Solo, Pixabay and Google Classroom/Padlet became "a microphone", "a free sound-effects site" and "your class page / feedback board" (equipment kept as named examples); the two-minor-keys rule, 32 measures and written reflection come from the owner's restructure doc and the older Spooky Tunes sheet, and the rubric's Composition row now grades the key change.
- Teacher notes (struggles, demo sequence, variations, grading tips) are the owner's, in the owner's voice ("permission to be weird", "Celebrate the strange ones").

## 2. Usable by a teacher: pass, with small notes

- Every day has minute blocks that add to 53. The setup page lists what to supply, a before-Day-1 checklist is included, and there are circulating prompts, an answer key and a worked 32-measure example.
- Arithmetic checked: 128 BPM x 32 measures = 60 s; 1.875 s per measure; 7680 / seconds; 0:12 = m. 7, 0:30 = m. 17, 0:45 = m. 25; 75 s = 102.4, rounded to 102; m. 16 starts at 0:28.1. Example tally (6 sources = 3 library, 2 recordings, 1 download; 6 reverb sends, 2 delay sends) matches the track table.
- Minor-key content is accurate: the W-H-W-W-H-W-W recipe, half steps between notes 2-3 and 5-6, A minor / D minor share 6 of 7 notes, all eight key signatures and chords on the reference card (A, E, B, D, G, C, F, Bb minor), B-C and E-F in A minor.
- Bus and reverb/delay content is accurate and not overclaimed: send from a track creates the Aux; Aux input must match the bus number; Space Designer and Tape Delay at Dry 0 / Wet 100 on a bus; the track still plays dry and the bus adds wet; far = more send, near = less; delay 600-900 ms with feedback for eerie, tempo sync off for free-running; a delay bus can feed the reverb bus. Logic commands are right (X Mixer, O Loop Browser, G global tracks, Option-' marker, File > Movie > Open Movie, Export Audio to Movie, Command-B Bounce, Control-click Compress). A version note and a trademark line are present.
- Notes, none blocking:
  1. Day 1 post step 5 and the Day 1 demo script (step 7) have students/teacher set up the delay bus on Day 1, while the pacing guide and Day 1 plan say "delay bus setup begins on Day 2". One sentence reconciling these (for example "Day 1 post step 5 is optional if time runs short") would help.
  2. Page 2 says deck slides 10-16 go with Day 2, but the Day 2 plan only lists slides 10-11. Slides 12-16 (project, steps, deliverables, rubric) have no explicit slot; add "slides 12-16 at the end of Day 2" to the plan.
  3. Slide 9 says students set up the delay bus "at the start of Day 2" yet it sits in the Day 1 slide range (1-9). Same root cause as note 1.

## 3. No school branding, student names or copyrighted media: pass

- Grep of the resource PDF, deck PDF, preview PDF, every .pptx text box and note for Blind Brook, BBHS, brook, logo, school: no hits (the only "school" hits are "high school" and "whole school" in the terms). No student names or work.
- The .pptx media is four images, all original drawings (woods and sun, signal-flow diagram, keyboard diagram, score map). No audio, video, lyrics or album art; no video file in the ZIP. The ZIP holds exactly the three listed files, byte-identical to the item folder files (cmp).
- The product tells the teacher to supply the video: three options (film your own, a free stock clip with a licence check, a short menu), with trim instructions. This appears on page 2, page 4, the description and the terms page.
- Halloween theme (John Carpenter) and Stranger Things main theme (Kyle Dixon & Michael Stein) appear by title and artist only, with "play from YouTube or Spotify" on deck slides 2-3, page 2, page 4, page 13, the terms page and the description. The owner's YouTube links were not copied. "Spooky hip-hop instrumentals" is a generic search tip.

## 4. Deck pattern, notes and look: pass, with polish notes

- Pattern is complete: pop-culture hook and guided listening (slides 1-3), definitions of reverb, delay, dry and wet (5), what a bus is (6), near-or-far listening (7), worked example in Logic (8-9, plus the score map on 11), steps (13), deliverables (14), rubric (15), then the owner's "One last thing" closer.
- Speaker notes are present on all 16 slides (280-485 characters each) and are real teaching notes. The Halloween theme's 5/4 piano pattern remark is correct.
- Hudson Beat look: HUDSON BEAT line on every slide, Oswald caps titles, Source Sans body, black, white and one orange accent. Body text is 13-40 pt on slides; the footer is 10 pt. No clipping or overflow in the deck PDF. The .pptx does not embed fonts; page 2 and the description say to install Oswald and Source Sans 3 or use the PDF (same caveat as item 008).
- Polish, not blocking: slides 4, 12 and 16 leave the lower third empty; slide 5's four tiles are tall with the text in the top half; the slide 10 and 11 diagram labels (images) are small for projection, though readable at full size.

## 5. Cover and previews: pass

- cover.png and preview-1..3.png are 2000 x 2000 with the HUDSON BEAT line, a heavy caps headline and a black band. The cover art (bare trees, orange moon, waveform) is original, fills the frame with no dead space, and "SPOOKY TUNES" is readable at thumbnail size. The previews show real watermarked pages and the deck with no orphaned words.
- The preview PDF has 4 watermarked pages (pacing, project sheet page 2, How to Bus Part 1, rubric) as UPLOAD.md says. PDF cover page has no orphaned line ("SCORING TO PICTURE IN LOGIC PRO / SPOOKY TUNES").

## 6. tpt.json and UPLOAD.md: pass

- Title "Spooky Tunes | Halloween Film Scoring in Logic Pro | High School Music Tech" is **75 characters** by my own count (limit 80), and matches UPLOAD.md.
- price and license_price "12.00"; tax_code "Other Digital Goods - No Physical Media" (as 006-008); grades 9th-12th (4); subjects Music; tags Halloween (accepted on 001) and Autumn (accepted on 002, 004); formats PDF; pages 47 = 31 + 16. All six `files` exist; `zip_contents` matches the ZIP. 9th-12th grade checkboxes exist in FORM-FIELDS.json. 008's first publish was interrupted, so the ZIP upload and PDF-only format are still unproven on a live run; UPLOAD.md says to dry-run first.
- Description proofread: no typos; page counts (4 + 4 + 4 + 15 + 2, plus cover and terms = 31) match the PDF; the six-day summary matches the pacing guide. The trademark line and the disclosure line ("Designed with the help of digital and AI tools, and checked by hand.") close the description and the disclosure is printed on page 31.

## Recommended fixes (all optional, do not block release)

1. Reconcile the Day 1 delay-bus wording (notes 1 and 3 in section 2) and give slides 12-16 a slot in the Day 2 plan (note 2).
2. Deck: tighten slides 4, 5, 12 and 16 (bigger type or shorter tiles) so the lower third is not empty; enlarge the slide 10 and 11 labels.
3. Consider adding "PowerPoint" or "ZIP" to `formats` only if the dry run lists it.

**Verdict: APPROVED**
