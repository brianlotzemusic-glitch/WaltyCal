# UPLOAD: Free Play, DMP2 project (TpT 021)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `free-play.zip`. It holds three files in a folder "Free Play - Hudson Beat":
  - `free-play.pdf`: the teacher and student resource, 22 pages, US Letter portrait.
  - `free-play-intro-deck.pptx`: the teacher-presented intro deck, 19 slides (16:9), speaker notes and a Class badge on every slide.
  - `free-play-intro-deck.pdf`: a PDF copy of the deck, 19 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `free-play-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, songs, presets, screenshots, student work or Logic sessions are in the ZIP.**

## 1. Title

```
Free Play Project in Logic Pro | Open-Ended Music Production | High School
```
(74 characters; the limit is 80.)

## 2. Description

```
Open-ended music production project for high school: students choose any style, technique or idea, write a project proposal, then build, mix, bounce and present an original track in Logic Pro. This Free Play project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the ideas (planning, arranging, basic mixing with EQ and panning, presenting) carry over to GarageBand and other music software.

WHAT'S INCLUDED (ZIP: 22-page PDF + 19-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup, a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a "What changed from the original" page, a Logic quick reference, an idea-starters page for the Easier variation, and a worked example (an invented 2:30 piece on paper: a vague and a clear proposal, an arrangement map and a mix plan) (10 pages)
• Student pages: Idea sketchpad, Proposal planner, Work plan, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a presentation and feedback planner and a Reflection page (written or oral) (10 pages)
• Teacher-presented intro deck, 19 slides with speaker notes on every slide: a "what would you make?" hook, what Free Play is, the production cycle, the three parts of a proposal, a worked-example arrangement map, mix time, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: introduction, project overview, explore Logic, brainstorm ideas
• Class 2: write and submit project proposals
• Classes 3-5: working days: compose, build, refine
• Class 6: final mix, bounce; prepare presentations and write 3 Padlet feedback questions
• Class 7: presentations with Padlet Q&A peer feedback

WHAT STUDENTS LEARN
• Planning a project: committing to an idea and writing a clear proposal
• Running the full production cycle: idea, composition, mix, presentation
• Basic mixing: EQ, panning and volume balancing on every track
• Managing their own time across a multi-day project
• Presenting their work and giving and getting feedback

GOOD TO KNOW
• There is no audio in this resource and no student work. Students make every sound in their projects themselves
• Requires Logic Pro on a Mac. A MIDI keyboard is not needed
• Rubric: 5 categories scored 1-5, /25; the final grade is the average of the student's and the teacher's score
• Grades 9-12 (the second year of my music production course); no music reading needed
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
- Tags in tpt.json: Autumn (proven; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Music Production, Open-Ended Project, Free Choice (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the owner teaches it.

## 7. Price

**$9.00** (paid), multiple-license price $9.00. Why $9 within the queue's $9-12 range: Free Play has the lightest project sheet of the DMP2 set (4 goals, 4 vocabulary terms, 4 requirements, no new tool to learn and no outside media), so it asks the buyer for the least. It is also the natural first project of the semester and so a low-risk way for a new buyer to try a DMP2 kit before the $10 and $12 ones and the bundle. The kit itself matches its neighbours in size (22 pages + 19 slides). The $10 kits (Alchemy Architect, Anti-Music Manifesto, Found Sound) each teach a specific tool or concept; this one does not.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 7-class pacing guide, the worked example, the project sheet requirements and steps, and the /25 rubric. "Number of pages or slides" is 41 (22 pages + 19 slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [x] **Reflection added (owner, 17 Oct 2026).** The owner's rubric (Documentation & Presentation) mentions reflection, but the project sheet has no reflection task. By the owner's definition (a written or oral conversation about how the student did on the project and what they would do differently next time) the kit has a Reflection student page (written or oral, 4 prompts), a teacher note, a pacing line and a line on the closing slide. The /25 rubric is untouched and the page adds no points. Shared builder: `tpt/_dmp2_common/dmp2.py`.
- [ ] **Sources (owner's DMP2 sources rule, 17 Oct 2026).** Project text, steps and the /25 rubric come from Drive DMP2 > Projects (New) (Free Play: Project Sheet & Rubric; TEACHER NOTES: Free Play - Teacher Notes); the menu entry is quoted from the June 2026 Project Menu. The Teacher Notes name no tutorial, suggest playing past student work (not used: nothing included, an invented example on paper instead) and ask the teacher to set up the Presentation Padlet (nothing included). The older Projects > Free Play folder holds only a 2024 outline, which is not a source.
- [ ] **Invented additions (all labelled in the PDF):** the Idea starters page (twelve prompts for the Easier variation), the worked example "Late Bus Home" (a 2:30 piece on paper at 96 BPM: a vague and a clear proposal, an arrangement map, a mix plan, three sample Padlet questions), the Idea sketchpad, Proposal planner and Work plan, the Logic quick reference, the setup suggestions, and the three drawings. None adds a requirement or a rubric row. The owner's LMS name is written "your class page" (listed on the "What changed" page).
- [ ] **Open questions for the owner:** (1) Are Apple Loops allowed in Free Play? Your sheets do not forbid them and the Harder variation asks for none, so the kit tells teachers to decide; say if you want a fixed rule. (2) Your Teacher Notes suggest playing 2-3 examples of past student work. None is used (no student work is ever sold); if you have an example you made yourself, it could be described on paper.
