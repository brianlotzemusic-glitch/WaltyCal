# UPLOAD: Genre Exploration, DMP2 project (TpT 022)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `genre-exploration.zip`. It holds three files in a folder "Genre Exploration - Hudson Beat":
  - `genre-exploration.pdf`: the teacher and student resource, 23 pages, US Letter portrait.
  - `genre-exploration-intro-deck.pptx`: the teacher-presented intro deck, 19 slides (16:9), speaker notes and a Class badge on every slide.
  - `genre-exploration-intro-deck.pdf`: a PDF copy of the deck, 19 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `genre-exploration-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, songs, artists, genres, presets, screenshots, student work or Logic sessions are in the ZIP.**

## 1. Title

```
Genre Exploration in Logic Pro | Production Research Project | High School
```
(74 characters; the limit is 80.)

## 2. Description

```
Genre research and music production project for high school: students pick a genre they do not know, research what defines it, study reference tracks, then compose, mix, reflect on and present an original track in Logic Pro. This Genre Exploration project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the ideas (researching, listening analytically, song form, genre-appropriate mixing, presenting) carry over to GarageBand and other music software.

WHAT'S INCLUDED (ZIP: 23-page PDF + 19-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup, a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a "What changed from the original" page, a Logic quick reference, a blank Genre shortlist for the Easier variation with the Harder variation laid out, and a worked example (an invented genre with three invented reference tracks, a 2:36 arrangement map and two mixing techniques, all on paper) (10 pages)
• Student pages: Genre research sheet, Reference track log, Loop and form sketch, Work plan, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a presentation and feedback planner and reflection prompts (11 pages)
• Teacher-presented intro deck, 19 slides with speaker notes on every slide: a "genre you would skip" hook, the five steps, a genre's fingerprint (rhythm, sound, form, production), why instruments are not enough, a worked-example arrangement map, using reference tracks, mix time, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: introduction, select a genre and begin the research
• Class 2: finish research, begin sketching an 8-16 bar loop
• Classes 3-5: working days: expand the composition, refine the arrangement and mix
• Class 6: final mix, bounce, write the reflection; prepare presentations
• Class 7: presentations with Padlet Q&A peer feedback

WHAT STUDENTS LEARN
• Researching and naming what defines a genre: rhythm, instrumentation, song form and production style
• Listening analytically to 2-3 reference tracks and breaking down their elements
• Composing to a genre's conventions and mixing to match its sound
• Reflecting on the process and what they learned
• Presenting their work and giving and getting feedback

GOOD TO KNOW
• There is no audio in this resource, no named genres, artists or songs, and no student work. Students choose their own genre and reference tracks and make every sound in their projects themselves
• Your own Genre Research Google Form is not included (it is yours to share); the kit has a paper research sheet to go with it
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
- Tags in tpt.json: Autumn (proven; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Music Production, Research Project, Genre Study (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the owner teaches it.

## 7. Price

**$11.00** (paid), multiple-license price $11.00. Why $11 within the queue's $9-12 range: Genre Exploration is a structured project with the heaviest student-page set of the recent DMP2 kits (a research sheet, a three-track reference log, a loop and form sketch, a work plan and reflection prompts) and a worked example that includes a genre card, reference breakdowns and a mix technique pair. It asks for more teacher support than Free Play ($9), but it teaches no new tool, so it sits below Billboard Top 10 and Sample Flipping ($12), which carry a specific analysis or tool workflow. The kit matches its neighbours in size (23 pages + 19 slides).

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 7-class pacing guide, the worked example, the project sheet requirements and steps, and the /25 rubric. "Number of pages or slides" is 42 (23 pages + 19 slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [x] **Reflection (owner, 17 Oct 2026).** Unlike the other DMP2 sheets, the Genre Exploration sheet already asks for a written reflection (requirement 6, step 6, checklist), so the shared Reflection element is switched off and nothing is added as a task. The kit has one student page of prompts (the owner's fourth struggle: "Reflections are thin. Give specific prompts."), stated as following the owner's definition (a written or oral conversation about how the student did and what they would do differently next time). No points, no rubric row. The page and the reasoning are listed on the "What changed" page.
- [ ] **Sources (owner's DMP2 sources rule, 17 Oct 2026).** Project text, steps and the /25 rubric come from Drive DMP2 > Projects (New) (Genre Exploration: Project Sheet & Rubric; TEACHER NOTES: Genre Exploration - Teacher Notes); the menu entry is quoted from the June 2026 Project Menu. The older Projects > Genre Exploration folder holds the owner's Genre exploration form and a 2025 outline doc; the outline is not a source.
- [ ] **Invented additions (all labelled in the PDF):** the Genre shortlist blank (the Easier variation as a template, the Harder variation laid out), the worked example "Harbor Drift" (an invented genre: a genre card, three invented reference tracks, an 80 BPM, 52-bar, 2:36 arrangement map, a weak and a strong production check, two mixing techniques, three sample Padlet questions), the Genre research sheet, Reference track log, Loop and form sketch and Work plan, the reflection prompts with a thin and a useful invented example, the Logic quick reference, the setup suggestions, and the four drawings. None adds a requirement or a rubric row. The owner's LMS name is written "your class page" (listed on the "What changed" page).
- [ ] **Open questions for the owner:** (1) The Genre Research Google Form is named in the sheet (requirement 2, step 1) and Teacher Notes, but Drive's connector cannot read a Form's questions, so it is not included and the kit has a paper research sheet beside it. If you want your form's questions in the kit, share them as a Doc. (2) The Easier variation asks for 5-8 genres with starter tracks and cheat sheets; your sheets name no genre, so the kit prints a blank and names none. Tell us if you want a genre list added.
