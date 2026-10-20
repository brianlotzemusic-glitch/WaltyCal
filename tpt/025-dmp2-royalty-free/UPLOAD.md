# UPLOAD: Royalty Free, DMP2 project (TpT 025)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `royalty-free.zip`. It holds three files in a folder "Royalty Free - Hudson Beat":
  - `royalty-free.pdf`: the teacher and student resource, 25 pages, US Letter portrait.
  - `royalty-free-intro-deck.pptx`: the teacher-presented intro deck, 19 slides (16:9), speaker notes and a Class badge on every slide.
  - `royalty-free-intro-deck.pdf`: a PDF copy of the deck, 19 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `royalty-free-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, songs, presets, screenshots, student work or Logic sessions are in the ZIP.**

## 1. Title

```
Royalty Free in Logic Pro | Compose to a Creative Brief | High School
```
(69 characters; the limit is 80.)

## 2. Description

```
Functional composition project for high school: students compose an original one-minute piece of royalty-free music in Logic Pro, as if for a school video, guided by 3 descriptive words they choose from a list of 160. This Royalty Free project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the ideas (working from a creative brief, layering, build-peak-resolve form and mixing) carry over to GarageBand and other music software.

WHAT'S INCLUDED (ZIP: 25-page PDF + 19-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup, a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a "What changed from the original" page, a Logic quick reference, a page laying out the Easier variation (a structural template) and the Harder variation (a hit-point sheet for scoring to a video), and a two-page worked example (an invented one-minute piece on paper: three words turned into sound, a chord for every bar, four sections, seven layers with two Apple Loops rearranged, and four automation lanes) (12 pages)
• Student pages: the 160-word Word list, Creative brief, Listening log, Arrangement plan with a length helper, Layers and mix sheet, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a presentation and feedback planner and a Reflection planner for the paragraph (13 pages)
• Teacher-presented intro deck, 19 slides with speaker notes on every slide: a "music with a job" hook, what Royalty Free is, the steps, how words become sound, build-peak-resolve, a worked-example map, one minute goes fast, mixing, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: introduction and word list; choose 3 words, brainstorm, begin composing
• Classes 2-4: working days: compose and refine the 1-minute piece
• Class 5: mix and finalize; write the reflection paragraph
• Class 6: final bounce; prepare presentations and write 3 Padlet feedback questions
• Class 7: presentations with Padlet Q&A peer feedback

WHAT STUDENTS LEARN
• Composing from descriptive words, a creative brief, instead of personal preference
• What makes music functional for media use
• Planning a one-minute piece with a build, a peak and a resolve
• Using Apple Loops without letting them do the arranging
• Balancing a mix with EQ, panning and plug-ins, then explaining their choices in a paragraph
• Presenting their work and giving and getting feedback

GOOD TO KNOW
• There is no audio in this resource and no student work. Students make every sound in their projects themselves, from the instruments, kits and Apple Loops in Logic
• Requires Logic Pro on a Mac. A MIDI keyboard is not needed
• Rubric: 5 categories scored 1-5, /25; the final grade is the average of the student's and the teacher's score
• Grades 9-12 (the second year of my music production course); no music reading needed
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present the PDF copy, which shows the intended look
• A "What changed from the original" page lists every change to my classroom wording
• Every student page prints well in black and white

Logic Pro and Apple Loops are products of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Designed with the help of digital and AI tools, and checked by hand.
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every DMP item. DMP2 is the owner's second-year course (the PDF and description say so); some schools take it in 9th grade.

## 4. Subjects and tags

Per tpt/METADATA-GUIDE.md, `tpt.json` keeps only values TpT has accepted so far.
- Subjects in tpt.json: Music. Candidate extras: Career and Technical Education; Computer Science - Technology
- Tags in tpt.json: Autumn (proven; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Music Production, Music Composition, Media Literacy (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the owner teaches it.

## 7. Price

**$10.00** (paid), multiple-license price $10.00. Why $10 within the queue's $9-12 range: the kit matches its neighbours in size (25 pages + 19 slides, a two-page worked example, a 160-word list and five student planning sheets), and it teaches one specific, searchable skill (composing music for media from a creative brief) like the $10 kits Pattern Prodigy, Infinite Horizon, Alchemy Architect, FX Deep Dive and Found Sound. It is priced above Free Play ($9, the lightest sheet) and below Billboard Top 10, Sample Flipping, Genre Exploration and Music for Visual Media ($11-12), which add current-hit analysis, a provided sample, a research task or video scoring.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 7-class pacing guide, the worked example, the 160-word Word list and the /25 rubric. "Number of pages or slides" is 44 (25 pages + 19 slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Reflection (owner, 17 Oct 2026).** The Royalty Free sheet already requires a reflection paragraph (requirement 6, step 5, checklist), so, as in Genre Exploration (022), the shared Reflection element is off. The kit adds a Reflection planner page (prompts for the three words plus two looking-back prompts that follow the owner's definition: a written or oral conversation about how the student did and what they would do differently). It adds no task, no points and no rubric row; the /25 rubric is untouched.
- [ ] **Sources (owner's DMP2 sources rule, 17 Oct 2026).** Project text, steps and the /25 rubric come from Drive DMP2 > Projects (New) (Royalty Free: Project Sheet & Rubric; TEACHER NOTES: Royalty Free - Teacher Notes); the menu entry is quoted from the June 2026 Project Menu. Supporting artifacts taken from the older Projects > Royalty Free folder: the "Groups of Words" sheet (the Word list) and the six "What to Dissect" headings of the sources doc. The 2025 outline, the folder of student mp3s and zips, and the sources doc's track list are not used.
- [ ] **Invented additions (all labelled in the PDF):** the structural template and the hit-point sheet (the Easier and Harder variations on paper), the worked example "Open Doors" (an invented 60-second, 120 BPM piece for an invented library-tour video: weak and clear plans, three words turned into sound, a chord for every bar, four sections, seven layers with two Apple Loops rearranged, four automation lanes, three sample Padlet questions), the Creative brief, Listening log, Arrangement plan, Layers and mix sheet and Reflection planner, the Logic quick reference and the drawings. None adds a requirement or a rubric row. The owner's LMS name is written "your class page" and tip 4's website name is written "a free music library" (both listed on the "What changed" page).
- [ ] **Open question for the owner:** (1) **The word list.** The sheet says "choose 3 descriptive words from the provided list" and the notes say the list is on the class page. The kit prints your "Groups of Words" sheet (160 words, A to Z, spellings kept: both Mesmerizing and Mesmerising, "Wonderous") as the Word list. That sheet was edited on 19 Oct 2026; say if the list has changed or if its 16 numbered groups matter (for example, one word from each group, or a wheel you spin). (2) **Tip 4 and the sources doc.** Tip 4 says "YouTube or BenSound"; the kit says "YouTube or a free music library" and includes no site, track, artist or link, because the sources doc names real tracks and artists. Say if you want the sources doc, or just the site names, in the ZIP. (3) **Real district videos.** Your notes say the project pairs well with them. No video is included; the Harder variation is a hit-point sheet for a clip the teacher chooses. If you have a district video you made and can share, it could be added in a later version. (4) **Apple Loops rule.** The sheet says loops are allowed but the arrangement must be original and gives no test. The kit suggests "no loop untouched for the whole piece" and a layer log; say if you use a different rule.
