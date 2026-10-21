# UPLOAD: Session Player's Studio, DMP2 project (TpT 026)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `session-players-studio.zip`. It holds three files in a folder "Session Players Studio - Hudson Beat":
  - `session-players-studio.pdf`: the teacher and student resource, 25 pages, US Letter portrait.
  - `session-players-studio-intro-deck.pptx`: the teacher-presented intro deck, 19 slides (16:9), speaker notes and a Class badge on every slide.
  - `session-players-studio-intro-deck.pdf`: a PDF copy of the deck, 19 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 x 2000).
- Preview file: `session-players-studio-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, songs, presets, screenshots, student work or Logic sessions are in the ZIP.**

## 1. Title

```
Logic Pro Session Players Project | Session Player's Studio | High School
```
(73 characters; the limit is 80.)

## 2. Description

```
Logic Pro Session Players project for high school: students build a realistic one-minute, live-style band arrangement with Logic's Drummer, Bass Player and Keyboard Player, customize each player's style, groove and complexity, then add their own original melody. This Session Player's Studio project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the ideas (choosing a chord progression, arranging sections, varying energy and mixing) carry over to GarageBand and other music software that has virtual players.

WHAT'S INCLUDED (ZIP: 25-page PDF + 19-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup, a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a "What changed from the original" page, a Logic quick reference, a page laying out the Easier variation (a given chord progression and a plan to fill in) and the Harder variation (planning an original progression, a B-section and a live-recorded element), and a two-page worked example (an invented 24-bar piece on paper: weak and clear plans, a chord for every bar, three Session Players with different complexity in four sections, and an original melody of chord tones) (12 pages)
• Student pages: a Chord cheat sheet (six common progressions in five major keys), Players sheet, Arrangement plan with a length helper, Melody planner, Mix sheet, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a presentation and feedback planner and a Reflection page (13 pages)
• Teacher-presented intro deck, 19 slides with speaker notes on every slide: a "band without the band" hook, what the project is, the steps, a four-bar chord loop, how settings change a section, energy over one minute, a worked-example map, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: introduction; demo Session Players; set up and choose a chord progression
• Class 2: customize the session players; begin arranging sections
• Classes 3-5: working days: arrange, add melody, refine
• Class 6: final mix and bounce; prepare presentations and write 3 Padlet feedback questions
• Class 7: presentations with Padlet Q&A peer feedback

WHAT STUDENTS LEARN
• Using Logic's Session Players (Drummer, Bass Player, Keyboard Player) and changing their style, groove and complexity
• Choosing and using a chord progression
• Arranging an intro, groove section and ending, and varying the energy between sections
• Writing an original melody that sits on top of the band
• Balancing a mix with EQ and effects, then presenting and giving and getting feedback

GOOD TO KNOW
• There is no audio in this resource and no student work. Students make every sound in their projects themselves, from the Session Players and instruments in Logic
• Requires a current Logic Pro on a Mac that includes Session Players. A MIDI keyboard is not needed
• Rubric: 5 categories scored 1-5, /25; the final grade is the average of the student's and the teacher's score
• Grades 9-12 (the second year of my music production course); no music reading or instrument playing needed
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present the PDF copy, which shows the intended look
• A "What changed from the original" page lists every change to my classroom wording
• Every student page prints well in black and white

Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Designed with the help of digital and AI tools, and checked by hand.
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every DMP item. DMP2 is the owner's second-year course (the PDF and description say so); some schools take it in 9th grade.

## 4. Subjects and tags

Per tpt/METADATA-GUIDE.md, `tpt.json` keeps only values TpT has accepted so far.
- Subjects in tpt.json: Music. Candidate extras: Career and Technical Education; Computer Science - Technology
- Tags in tpt.json: Autumn (proven; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Music Production, Music Arrangement, Logic Pro (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the owner teaches it.

## 7. Price

**$10.00** (paid), multiple-license price $10.00. Why $10 within the queue's $9-12 range: the kit matches its neighbours in size (25 pages + 19 slides, a two-page worked example, a chord cheat sheet and four planning sheets), and it teaches one specific, searchable skill (arranging with Logic's Session Players) like the $10 kits Royalty Free, Pattern Prodigy, Infinite Horizon, Alchemy Architect, FX Deep Dive and Found Sound. It is priced above Free Play ($9, the lightest sheet) and below Billboard Top 10, Sample Flipping, Genre Exploration and Music for Visual Media ($11-12), which add current-hit analysis, a provided sample, a research task or video scoring.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 7-class pacing guide, the worked example, the Chord cheat sheet and the /25 rubric. "Number of pages or slides" is 44 (25 pages + 19 slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "(c) 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Reflection (owner, 17 Oct 2026).** The sheet has no reflection task (only the rubric mentions reflection), so the shared Reflection page is on: your definition (a written or oral conversation about how the student did and what they would do differently), no points, no rubric row. The /25 rubric is untouched.
- [ ] **Sources (owner's DMP2 sources rule, 17 Oct 2026).** Project text, steps and the /25 rubric come from Drive DMP2 > Projects (New) (Session Player's Studio: Project Sheet & Rubric; TEACHER NOTES: Session Player's Studio - Teacher Notes); the menu entry is quoted from the June 2026 Project Menu. The 2025 Project Outline is not used.
- [ ] **Invented additions (all labelled in the PDF):** the worked example "Porch Light" (24 bars, 96 BPM, key of C, a chord for every bar, three Session Players with complexity 1-5 by section, an original melody of chord tones, three sample Padlet questions), the Chord cheat sheet (written from music theory), the Easier and Harder planning page, the Players sheet, Arrangement plan, Melody planner and Mix sheet, the Logic quick reference and the drawings. None adds a requirement or a rubric row. The 1-5 complexity scale is the kit's own, so settings can be talked about; Logic shows them with its own controls.
- [ ] **Open question for the owner:** (1) **Your chord cheat sheet.** Your teacher notes list "Common chord progressions cheat sheet" as a resource but it was not in Projects (New). The kit supplies its own (six progressions as Roman numerals, in C, G, D, F and A). Send yours if you want it used instead. (2) **The two YouTube videos.** They are written as "a YouTube video on..." with no title, creator or link. Say if you want the exact titles or links printed. (3) **Tip 2** names two third-party products; the kit says "a search engine or an AI chatbot". (4) **Logic version.** Session Players need a recent Logic Pro; the setup page says to check yours. Say which version your class uses, if you want it stated. (5) **Live-recorded element.** The Harder variation is a planning page only; no recording or audio is included.
