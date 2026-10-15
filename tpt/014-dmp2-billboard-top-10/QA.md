# QA: TpT 014 DMP2 Billboard Top 10 (round 1)

QA reviewed this item on 15 Oct 2026, independently of the Designer. I read the full text of the 20-page PDF, all 17 slides of the .pptx (every text box, minimum font size and speaker note, via python-pptx), the deck PDF and the preview PDF. I rendered all 20 PDF pages and all 17 deck pages at 100 dpi (looked closely at pages 2, 5, 10, 17 and slides 7, 9, 15) and viewed cover.png and preview-1..3.png. I compared the content with the owner's Drive docs (read-only): Project Sheet & Rubric (id 1kw1__GA, modified 26 Mar 2026), Teacher Notes (108-lz57T, TEACHER NOTES folder) and the DMP2 Project Menu entry. I reviewed the shared builder tpt/_dmp2_common/. I ran `gen.py --check` (CHECK OK; it rewrote nothing). I changed no item files.

## 1. Faithful to the owner's content: pass

- **Rubric is the owner's, /25.** Five categories (Creativity & Originality, Technical Skill / DAW Use, Composition & Structure, Sound Design & Mix Quality, Documentation & Presentation), scored 1-5, all 25 descriptors match the Drive text exactly, "Final Grade = Average of Student + Teacher = ___ / 25" kept. Total is /25 on page 17, page 2, page 7, the deck (slide 15) and UPLOAD.md. The owner's descriptor "no reflection" (Documentation row) has no matching task on the sheet; the Designer left it unchanged and raised it as an owner question (UPLOAD.md section 9). Correct handling.
- **No added requirements.** Overview, 4 goals, 5 vocabulary terms, 6 requirements, 7 steps, 4 tips, 7 checklist items and the title line match the Drive sheet word for word except for the changes below. The Teacher Notes (big idea, 4 struggles, 2 variations, resources, pacing, closing note) match. The Project Menu line "Analyze and recreate a current Billboard hit. Study song form, production techniques, and drum programming." and "Structured / Song Form & Drums" are quoted correctly (page 3).
- **Disclosure page 8 is accurate and complete for the wording changes I found:** LMS name to "your class page" (checklist items 3-4, resource list), Google Form to "the Top 10 analysis" (step 1, checklist 1, Class 1 plan), Song Form spreadsheet to "Song Form map" (step 2, struggle 2), page numbers added to steps 1-3, the closing note, the Classes 3-5 row split, layout-only rubric/notes changes. I diffed each against Drive; nothing else differs. The page never claims "word for word" (the builder bans the phrase), and its "kept as I wrote it" list is true.
- Two small gaps in disclosure, see Required fixes 2 and 3.

## 2. Third-party claims, chart facts, media: pass

- No songs, audio, video, lyrics, album art or chart data anywhere. The cover and slide 1 chart is an abstract drawing of ten bars with no titles. The one song named is the owner's resource-list entry "Sorry by Justin Bieber" (title and artist only, page 7). Billboard/Hot 100 trademark line appears on page 2, page 20 and in the description. The only chart fact is in the slide 2 notes: "The Hot 100 is published every week and has been since 1958; it ranks songs by streaming, sales and radio airplay." That is accurate (first chart August 1958; current methodology is streaming, sales, airplay) and generic.
- No Thunderstruck, LondonBounce, Falling For U or other non-sellable media: grep of PDF, deck PDF, preview PDF, pptx XML and notes, UPLOAD.md, tpt.json and dmp2.py returns nothing (dmp2.py only holds them in a built-from-parts BANNED list). The .pptx media is three original PNG drawings; no audio, video or embedded fonts.

## 3. Logic steps and music facts: pass

Practice map arithmetic verified: 25 beats in 15 s x 4 = 100 BPM; 4/4 bar = 240/100 = 2.4 s; sections 4+16+8+16+8+8+8+4 = 72 bars = 172.8 s (2:53); start times (bar - 1) x 2.4 for bars 5, 21, 29, 45, 53, 61, 69 = 0:10, 0:48, 1:07, 1:46, 2:05, 2:24, 2:43 (all correct, and deck slide 7 and its notes agree). Drum grids: verse kick on 1, 3 and the "and" of 3, snare on 2 and 4, eighth hi-hats; chorus kick on every beat, clap with snare, open hi-hat on the off-beats; the text grids on page 10 match the drawing and slide 9. Logic steps (Global Tracks G, Arrangement markers, Electronic Drum Kit loads Drum Machine Designer, Create Pattern Region, Step Sequencer velocity mode, Command-R, Mixer X, Channel EQ, Command-B bounce, Compress in Finder) are right for Logic Pro 10.5+, and the Step Sequencer "came in 10.5" note is true. The "Logic only" wording with the version note is honest; no "any DAW" claim.

## 4. Pacing: pass

Page 5, page 2, the deck badges and UPLOAD.md agree: Class 1 slides 1-6, Class 2 slides 7-10, Class 3 slide 11, Class 4 slide 12, Class 5 no new slide (a working day, disclosed on pages 2 and 5 and slide 12's notes), Class 6 slides 13-15, Class 7 slides 16-17. Every one of the 17 slides is in exactly one class slot and carries a visible CLASS badge (slide 1 reads "CLASS 1" in its strap). Student-page references are right (p. 11-19). 20 pages + 17 slides = 37 matches tpt.json.

## 5. Text fit and layout: pass

No clipped or overlapping text in any render. Deck minimum font 10 pt (footer; body 16+). Polish only: page 2 leaves the lower third of the left column empty; slide 7 has a large gap between the timeline and the bullets (enlarge the timeline); slide 9's velocity lane shows only the verse (the chorus half is a blank white box, which reads as missing). Not blocking.

## 6. No school branding or student content: pass

Grep of all PDFs, pptx XML and notes, UPLOAD.md, tpt.json for Blind Brook, BBHS, brook, Google Classroom, student names: no hits. "Padlet", "YouTube", "Spotify" are named as tools only and the credits say so. Footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".

## 7. Deck: pass

Pop-culture hook (this week's No. 1, slides 1-2), plain-English definition (slide 3), guided listening questions (slide 2), worked examples (slides 7 and 9), two Logic demos (8, 10), the steps, what to turn in and the rubric (13-15), then presentation day and a close. Speaker notes on all 17 slides (265-361 characters), real teaching notes. Hudson Beat look: HUDSON BEAT line, Oswald caps, black/white with one magenta accent. 16:9; deck PDF 17 pages; fonts embedded, only Oswald and Source Sans 3. Notes cite the owner's own words correctly (struggles, tips, close).

## 8. Cover and previews: pass

cover.png and preview-1..3.png are 2000 x 2000 with the HUDSON BEAT line, heavy caps headline and black band. The cover has no dead space and no orphaned words ("BILLBOARD / TOP 10" under "RECREATE A HIT IN LOGIC PRO"), the big line is readable at thumbnail size, and the cover art uses the one accent plus black. Previews use watermarked real pages and slides; page shots overlap deliberately in preview-1 (the right-hand rubric and left pacing pages are cropped on purpose). Preview PDF: 4 watermarked pages matching UPLOAD.md.

## 9. tpt.json and UPLOAD.md

- Valid JSON. Price and license_price "12.00"; tax_code "Other Digital Goods - No Physical Media"; subjects Music; tag Autumn (proven); format PDF; pages 37; no answer_key (correct, none exists); all six `files` exist; `zip_contents` lists exactly the three files in the ZIP and I confirmed each is byte-identical to the file in the folder (ZIP holds no audio or sessions). No `release` or `uploaded` file.
- **Title** "Song Form in Logic Pro | Billboard Top 10 Remake | High School Music Technology" is **79 characters** by my own count (limit 80); it matches the UPLOAD.md code block; "Logic Pro" starts at character 14 (inside the first 30). The guide's formula is followed.
- **SEO opening** follows METADATA-GUIDE: line 1 "Song form and drum programming for high school music technology: students study the current Billboard Top 10, pick one song ... recreate it in Logic Pro"; line 2 gives the course tie-in and the Logic-only steps with the GarageBand/Ableton Live/BandLab wording. Description proofread: no typos; page counts (9 + 9 + cover + terms = 20) are right; the seven-class summary matches the guide; Logic and Billboard trademark lines and the disclosure line "Designed with the help of digital and AI tools, and checked by hand." are present, the disclosure last.
- **Grades are 10th-12th, not the 9th-12th that METADATA-GUIDE (a) prescribes** for every DMP item. The Designer chose this deliberately and explains it (DMP2 is year two; "Grades 10-12" is also printed on the cover, pages 2-3 and the description). See Required fix 1.
- Only one tag (Autumn) and one subject (Music) are used. This is allowed (only proven options) and UPLOAD.md lists the candidate extras; the SEO value is low until they are proven. Not blocking.

## 10. Shared builder tpt/_dmp2_common/: pass

dmp2.py (77 KB) and README.md are committed (no __pycache__ tracked). README documents the kit contract (every content name, the standard pages, `PACING` structure, hooks) and exactly what `--check` enforces, and says to copy 014's gen.py for the next kit. The builder holds no project-specific or school content: grep for Billboard, Sorry, Bieber, Blind Brook finds only the BANNED list, which is assembled from split strings so the names are not literal in the file. All Billboard content lives in the kit's gen.py.

## Required fixes (block release)

1. **Grades.** Either set `grades` to 9th, 10th, 11th, 12th in tpt.json and change "Grades 10-12" to "Grades 9-12" on the cover, PDF pages 1-3, the deck-related text, preview images and the description (then rebuild all outputs and the ZIP), or record an explicit owner exception for 10th-12th in UPLOAD.md and METADATA-GUIDE. As written, the item contradicts the guide the Manager releases against.
2. **Slide 13 speaker note:** "Step 6 of the sheet, word by word on the slide." is a word-for-word claim, but the slide shortens the owner's step 6 ("EQ every track, pan for width, adjust levels, and add plug-ins for authenticity" becomes four fragments). Reword to "the four parts of step 6 of the sheet". Rebuild the .pptx, deck PDF and ZIP.
3. **Page 7, "How to grade":** "nothing clipping on the loudest section" and "EQ on every track" are presented next to the owner's rubric as what to check, but the owner's Sound Design & Mix rubric and struggle list do not say "nothing clipping". Either label the three bullets as the kit's suggestions ("My rubric rows are on page 17; these are suggestions for looking at each row") or drop "nothing clipping". Page 8 "New in this kit" already lists "the grading tips", so the label is the only change needed.
4. Rebuild billboard-top-10.pdf, the ZIP (and the preview PDF only if a previewed page changes; page 7 is not one of the four previewed pages) and run `gen.py --check`.

## Optional fixes

1. Slide 7: enlarge the timeline into the gap; page 2: balance the lower-left space.
2. Slide 9: add chorus velocity bars (or say the chorus is fixed at 100) so the lane is not half empty.
3. Add Project Based Learning, Technology, High School and extra subjects once a dry run proves the option text (METADATA-GUIDE process).

**Verdict: REJECTED**
