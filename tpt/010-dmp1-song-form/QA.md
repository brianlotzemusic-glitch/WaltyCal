# QA: TpT 010 DMP1 Unit 5, Song Form (round 1)

QA reviewed this item on 12 Oct 2026, independently of the Designer. I read the full text layer of the 27-page PDF, the 17-slide deck (every text box and speaker note, extracted from the .pptx, plus the 17-page deck PDF) and the 4-page preview PDF. I rendered the PDF at 40 dpi (all pages) and 110 dpi (page 25), the deck PDF at 45 dpi, the preview PDF at 40 dpi, and cover.png plus preview-1..3.png as a sheet. I checked .pptx font sizes with python-pptx. I compared the content with the owner's Drive docs in "4 - Song Form": Project Sheet & Rubric, Teacher Notes, Day 1 Classroom Post, and the Song Form "Complete" and "Blank" sheets. Drive was read-only. I changed no item files.

## 1. Faithful to the owner's content and voice: pass

- Rubric is intact: 5 categories, scored 2-5, total / 25. Every level descriptor matches the owner's text word for word; only "spreadsheet" became "sheet" and "Padlet questions" became "feedback questions". Self and Teacher columns are added. No requirement is added: the 12 requirements, the 12-item submission checklist, the goals, the 10 vocabulary terms, "What each section does", the five tips and the six steps all match the owner's Project Sheet.
- Teacher notes (big idea, how to run the class analysis, suggested songs and why each works, planning-table enforcement, chord layer demo, callbacks, struggles, variations) are the owner's, in the owner's voice. The Day 1 post matches. The deck's closer ("what you just heard ... You understood it well enough to build it yourself") is the owner's close.
- Deliberate changes are disclosed on page 9 ("How this kit differs from my classroom version") and page 6: 3 days become 4 (building gets its own day), Google Classroom and Padlet become "your class page" and "feedback board", "Unit 3 Part 4 file" becomes "your chords-and-bassline file" with a setup fallback on page 4, and the 32-measure skeleton is new (the inventory flagged it missing). The "Unit 3 / Unit 4" numbering is dropped; callbacks name Beat From Nothing, Stems & Grooves and Building Blocks without unit numbers. None of this changes what is graded.

## 2. Usable by a teacher: pass, with notes

- Every day has minute blocks that add to 53 (Day 1: 12+13+20+8; Day 2: 5+7+13+25+3; Day 3: 5+40+8; Day 4: 20+30+3). Page cross-references check out (page 4 setup, 16 planning table, 17 steps, 18-20 song sheets, 21 compare, 24 rubric, 25 key, 26 skeleton).
- Pacing consistency: guide, day plans, Day 1 post, project steps and deck agree. Every deck slide has a day slot: Day 1 slides 1-7, Day 2 slides 8-16, Day 4 slide 17, Day 3 "No slides"; every slide carries a DAY badge matching that mapping, and page 2, the pacing table and both day-plan pages say the same thing. The chord layer demo is Day 2 (slides 8-9) in the guide, Teacher Notes and deck; students add the chord layer on Day 3 (step 5), as slide 9's notes say. The worked-skeleton arithmetic is right: 4+4+8+4+8+4 = 32, 128 beats, about a minute at 120-128 BPM; m. 1/5/9/17/21/29 starts match; transitions at m. 4, 8, 16, 20, 28, 30 fall inside the right sections; 1/3/5/3/5/2 elements tally with the track grid.
- Logic steps are correct and not overclaimed: G global tracks and Arrangement track markers, Option-drag to copy a region, Command-R repeat, Option-Command-N new track, Y Library, M mute, C Cycle, X Mixer, A automation, Drummer Fills knob, File > Bounce > Project or Section (Command-B), Control-click > Compress. A version note and trademark line are present. Nothing says "works in any DAW".
- Notes, not blocking:
  1. Day 2 block "5-12 THE PROJECT [slides 10-16]" covers seven slides in seven minutes (worked skeleton, planning, four transitions, project, steps, turn-in, rubric). It is workable because slides 13-16 are mostly the handouts, but a teacher may want a line saying so (for example "slides 14-16 can be read from the handouts").
  2. Teacher notes (page 10) call Anti-Hero a good way to introduce the pre-chorus (owner's wording), yet the answer key lists no pre-chorus for Anti-Hero (also the owner's data: Intro, Verse, Chorus, Post chorus ...). A teacher who checks the key will see the conflict. One sentence ("my analysis labels it a post chorus; accept a pre-chorus call") or a wording change would close it.

## 3. Song and form facts: pass on content, one layout defect (see section 7)

- Section names and bar counts for all six songs in the answer key (page 25) match the owner's "Song Form - Pop Music (Complete)" sheet exactly: Crazy 8 sections (Intro 1 ... Outro 8), Blinding Lights 12 (Intro (Pop Drop) 12 as 4+8 ... Outro 8), Anti-Hero 11, good 4 u 11, Levitating 12 (ending "Chorus (2x) 16"), Uptown Funk 15 (Bridge 20, Outro 16). The section counts printed on the right of each map (8, 12, 11, 11, 12, 15) are right. The pre-filled labels on the Song Form sheets (pages 18-19) match the owner's Blank sheet.
- Content is limited to title, artist, section names and measure counts, plus the owner's one-line "why it works" notes. No lyrics, no chord charts, no transcribed melody, no album art. The owner's own caveat ("Bridge/Chorus?" is the owner's label, accept both) is kept and explained.
- Note: the "Complete" sheet in the inventory was flagged "sellable only as facts"; it is used here as facts only, and the inventory's older song list (Closer, Bad Guy ...) is not used. The owner confirmed ownership on 11 Oct.

## 4. No school branding, student names or copyrighted media: pass

- Grep of the resource PDF, deck PDF and preview PDF text, every .pptx slide and notes XML, docProps, UPLOAD.md and tpt.json for Blind Brook, BBHS, brook, logo, Google Classroom: no hits (gen.py only holds them in its banned-word list). No student names or work.
- The .pptx media is four images (hero skeleton grid, class-example table, worked-example table, closing grid), all original drawings. No audio, video, lyrics or album art. The ZIP holds exactly the PDF, the .pptx and the deck PDF, byte-identical (cmp) to the item folder files. Songs appear by title and artist only, with "play from YouTube or Spotify" on slides 3, 5 and 6, pages 2, 4, 10 and 27, and the description.

## 5. Deck pattern, notes and look: pass, with polish notes

- Pattern is complete: pop-culture hook (slide 1 "Feat. Blinding Lights", slide 2 question), plain-English definition (2), guided listening questions (3, 5), what each section does (4), worked example in Logic (8-10: the chord layer demo and the 32-measure skeleton), transitions (12), project, steps, deliverables, rubric (13-16), then the owner's closer (17). 17 slides, 16:9.
- Speaker notes are present on all 17 slides (263-424 characters) and are real teaching notes.
- Hudson Beat look: HUDSON BEAT line on every slide, Oswald caps titles, Source Sans body, black, white and one violet accent (used for chorus bars). Body text is 16-40 pt; the footer and tile text are 10 pt. No clipping or overflow in the deck PDF.
- Polish, not blocking: slides 2, 7 and 17 leave the lower third empty; slide 10 is an image of the planning table whose text is small for projection; slide 16's level-5 descriptions are small (about 10-11 pt) for a projector. The .pptx does not embed fonts (same caveat as 008 and 009; page 2 and the description tell the teacher to install the fonts or use the PDF).

## 6. Cover and previews: pass

- cover.png and preview-1..3.png are 2000 x 2000 with the HUDSON BEAT line, a heavy caps headline and a black band. The cover's hero (an arrangement grid with violet chorus bars) is original and "SONG FORM" is readable at thumbnail size. Previews show real watermarked pages and deck slides; no orphaned words.
- The preview PDF has 4 watermarked pages (pacing, planning table, class Song Form sheet, rubric), matching UPLOAD.md. The PDF cover page has no orphaned line.
- Polish: the interior teacher pages (about pages 4-12) end about two-thirds of the way down the page, leaving a blank lower third. It prints fine and does not block.

## 7. Text fit: one defect, REQUIRED fix

Page 25 (answer key, form maps), the bars for the songs' sections: labels are wider than the short bars and are clipped or overprinted. Seen at 110 dpi: Blinding Lights "PRE-CHORU" (twice) and a squeezed "VERSE"; Anti-Hero "VERSE" overlapping "BRIDGE/CHOR" (reads "VERSEBRIDGE/CHOR") and the one-measure intro and post-chorus bars unlabeled; Levitating and Uptown Funk have the same crowding ("BRIDGE A/BRIDGE B", "PRE-CHORUS", "POP DROP"). The text line under each map restates the counts, so no fact is lost, but this is the teacher's answer-key reference and the labels are visibly cut off. Fix in gen.py: shrink or abbreviate the in-bar labels (for example PRE, POP, BR/CH, or a smaller font with a minimum bar width) or drop the in-bar text on bars narrower than the label, then rebuild the PDF and the ZIP.

## 8. tpt.json and UPLOAD.md: pass

- Title "Song Structure in Logic Pro | Pop Song Form Unit | High School Music Technology" is **79 characters** by my own count (limit 80) and matches the UPLOAD.md code block. "Logic Pro" is inside the first 30 characters (it ends at character 27), and the title follows the METADATA-GUIDE formula (search phrase, unit topic, audience).
- price and license_price "10.00"; tax_code "Other Digital Goods - No Physical Media" (as 006-009); grades 9th-12th (4 slugs, same as 008/009); subjects Music; tags Autumn (proven on 002/004); formats PDF; pages 44 = 27 + 17; answer_key "Included". All six `files` exist, and `zip_contents` matches the ZIP. Career/Technology subjects and the extra tags are correctly left as post-dry-run manual steps in UPLOAD.md. (Autumn is a loose tag for a year-round course; same compromise as 008 and 009, and UPLOAD.md says to drop it once better tags are accepted.)
- SEO opening follows METADATA-GUIDE: line 1 leads with "Song structure for high school music technology", names what students make (a song with at least four sections in Logic Pro); line 2 gives the course tie-in (Unit 5 of Digital Music Production 1) and the Logic-specific-steps / GarageBand, Ableton Live and BandLab transfer wording, not a compatibility promise.
- Description proofread: no typos; counts match the files (4 + 3 + 4 + 12 + 2 = 25 pages plus cover and terms = 27; 10 terms; six songs; 17 slides); the four-day summary matches the pacing guide; the "no lyrics, only section names and measure counts" claim is true. The Logic trademark line is present and the disclosure line "Designed with the help of digital and AI tools, and checked by hand." closes the description and is printed on page 27.

## Required fix (blocks release)

1. Page 25 answer-key maps: stop the in-bar labels clipping and overprinting (section 7). Rebuild song-form.pdf, the ZIP (and the preview PDF only if it is affected, which it is not today).

## Optional fixes

1. Add a sentence reconciling the Anti-Hero pre-chorus wording on page 10 with the answer key (section 2, note 2).
2. Tell the teacher which Day 2 slides (13-16) can be read from the handouts to fit the 5-12 block (note 1).
3. Deck polish: fill the lower third of slides 2, 7, 17; enlarge slide 10's table and slide 16's level text.
4. Teacher pages 4-12 could use the blank lower third (larger type or the observation notes box).

**Verdict: REJECTED**


---

# Round 2 (12 Oct 2026)

Scope: commit 131b4e2 changed only page 25 of song-form.pdf (text of pages 1-24, 26-27 is identical to round 1 and their 30 dpi renders are byte-identical), build/key.png, preview-3.png, the ZIP, gen.py and the action log. tpt.json, UPLOAD.md, the deck and the preview PDF are untouched.

- `gen.py --check`: CHECK OK (27 pages, map label check, rubric 5 x (2-5) = /25, no banned strings, zip current). Working tree stayed clean after the run.
- Page 25 rendered at 100 dpi and all 27 pages at 30 dpi. Every bar on all six maps now carries a short code (IN, V, CH, OUT, PRE, POST, DROP, BR, BR A, BR B, BR/CH), 8/12/11/11/12/15 bars matching the section counts. Narrow bars (1-4 measures: Crazy intro, Anti-Hero intro/post chorus/outro, post choruses, Levitating and Uptown Funk pre-chorus/post chorus) use a code above the map with a leader line, with a printed note explaining it. No label is clipped, overlapping or cut off.
- Legend ("Bar codes: IN intro, V verse, PRE pre-chorus, CH chorus, POST post chorus, DROP pop drop, BR bridge, BR A / BR B bridge A / B, BR/CH bridge/chorus?, OUT outro") covers every code used and nothing else. The text line under each map still gives the full section names and bar counts, which match the owner's Complete sheet (title/artist/sections/measures only) for all six songs.
- ZIP: the PDF, .pptx and deck PDF inside are byte-identical to the item folder files (481,813-byte PDF). Preview PDF (4 pages, pacing, planning table, class sheet, rubric) does not include page 25 and is unaffected. preview-3.png ("Everything inside") shows the new key page and is consistent with it.
- Regression: zero Blind Brook/BBHS/brook hits in the resource, preview and deck PDFs; rubric page still /25; tpt.json unchanged from round 1 and valid JSON.
- Anti-Hero: page 25's intro paragraph now reconciles with the teacher notes (notes suggest Anti-Hero for the pre-chorus; analysis lists none; accept a pre-chorus if a student splits one out of a verse). Page 10 wording is unchanged and is now consistent with the key. Optional note 1 (Day 2 slides 13-16) and deck/teacher-page polish were not addressed; they were optional and do not block.

Required fix from round 1 is resolved. No new defects found.

**Verdict: APPROVED**
