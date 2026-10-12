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

---

# Round 2 (12 Oct 2026, fresh QA after two owner decisions)

Owner decisions under review: (1) the corrected How-to-Bus send levels stay (about -15 dB reverb, -20 to -25 dB delay); (2) the product must not require two minor keys: no key or form required (owner's May project sheet), minor keys only as an optional tip. I read the 31-page PDF, the deck PDF, the preview PDF and every .pptx text box and speaker note (extracted with python-pptx), UPLOAD.md, tpt.json and gen.py. I rendered the PDF and deck at 40 dpi as contact sheets and looked for overflow. I changed no item files.

## 1. No leftover key requirement: pass
- Grep of the PDF, deck, preview, notes, UPLOAD.md, tpt.json and gen.py for two keys, key change, second key, modulate, required key: every hit is optional wording ("Minor keys are optional. No key is required", "any key, or none", "A second key (only if I change key)", "If you change key: pairs to try", "an extra challenge", "this example happens to change key... a choice, not a rule"). No requirement, checklist item, goal, day plan, teacher note or deck slide asks for a key or a key change.
- Rubric is /25, five categories scored 2-5, and Composition & Pacing is now about key moments, silence and fit to the picture: no key criterion. Page 10 says the rubric has "no key criteria". Deck slide 15 matches the PDF. Checklist, requirements page and deck slide 14 list no key item.
- Worked example (A minor, D minor at m. 17) is labelled optional/"a choice, not a rule". gen.py --check also scans outputs for the old phrases.
- Wording notes, not blocking: (a) page 3 "What students learn" still says "Minor keys feel different from major keys, and now they know why", and deck slide 4 lists "Minor keys: darker than major" among the four spooky tools, which reads as taught to everyone; "optional" would match the rest. (b) The vocabulary page (page 26) Quick Check asks "In A minor, the half steps are B-C and ____" although minor keys are optional; ungraded, but a student who skipped the Minor Key Map cannot answer it. Consider "(optional)".

## 2. Send levels: pass
Reverb start around -15 dB (page 3 reference table, How to Bus Part 1, deck slide 8); delay -20 to -25 dB (reference table, Part 2, deck slide 9); troubleshooting "try -20 dB". Teacher-demo and worked-example track tables use varied per-track levels (-6 to -30 dB for reverb, -18 to -22 dB for delay), consistent with the guidance.

## 3. No Blind Brook / student content: pass
Grep for blind, bbhs, brook, logo, student name across the PDF, deck, preview, notes, UPLOAD.md and tpt.json: no hits. The .pptx media is four original drawings. Songs by title and artist only.

## 4. Deck: pass
16 slides, speaker notes on all 16 (280-545 characters). Contact sheets of the deck (16) and PDF (31 pages) show no clipping or overflow. Polish only, as in round 1: slide 5's tiles are tall and mostly empty, slides 8-9 step text is small for projection.

## 5. ZIP and metadata: pass
- The ZIP holds exactly one folder with spooky-tunes.pdf, the deck .pptx and the deck PDF; all three are byte-identical (cmp) to the item files, which carry the current build.
- Title: "Film Scoring in Logic Pro | Halloween Music Production Project | High School" is **76 characters** by my own count (limit 80) and identical in UPLOAD.md and tpt.json-driven publish (title is read from UPLOAD.md).
- tpt.json: price and license_price "12.00", tax_code set, grades 9th-12th (4), subjects Music only, tags Halloween and Autumn (both proven on 001/002/004), format PDF, all six files exist. No unproven form values; the Career/Technology subjects and extra tags are correctly left as manual post-dry-run steps in UPLOAD.md.
- SEO opening: "Film scoring for high school music production: students score a one-minute video of a walk through the woods at night in Logic Pro, with 32 measures of atmosphere and reverb and delay on shared buses. No key, chord progression or song form is required..." leads with the phrase teachers search, names the audience, what students make, and the free-choice promise. The second line covers the 6-day schedule, the Halloween and year-round use, and the Logic-specific steps with GarageBand/Ableton/BandLab transfer (not a compatibility promise). Reads well for high-school music-production teachers.
- Description proofread: no typos; counts (31-page PDF, 16 slides, 14 vocabulary terms, 8 minor keys, /25) match the files; the learn bullets and Good to Know are consistent with "no key required".

## 6. Round-1 non-blocking items: not fixed
1. Day 1 delay-bus wording: **not fixed.** Day 1 post step 5 (student page 14, "SET UP YOUR DELAY BUS ... Just get it set up") and the teacher demo step 7 (page 12, "Walk through setting up Bus 2 with Tape Delay") still put the delay bus on Day 1, while the pacing guide and Day 1 plan say "Delay bus setup begins on Day 2". Deck slide 9 notes say students set up the delay bus "at the start of Day 2" but the slide is in the Day 1 range (1-9).
2. Slides 12-16: **not fixed.** Page 2 says slides 10-16 go with Day 2, but the Day 2 plan and pacing guide list only "Slides 10-11". Slides 12-16 (project, steps, deliverables, rubric) still have no slot.

## Optional fixes
1. Add one sentence reconciling the Day 1 delay-bus mentions (for example, mark Day 1 post step 5 and demo step 7 "optional, if time allows; otherwise Day 2"), and give slides 12-16 a Day 2 slot (for example at the end of the 22-30 block or after the delay bus).
2. Mark the page 3 / slide 4 minor-key lines and the page 26 Quick Check item "optional".
3. Deck polish as in round 1 (slides 4, 5, 12, 16 lower third; slide 10-11 labels).

None of these blocks release: all content decisions from the owner are implemented, nothing requires a key or two keys, and the metadata is within the proven values.

**Verdict: APPROVED**

