# UPLOAD: Infinite Horizon, DMP2 project (TpT 023)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `infinite-horizon.zip`. It holds three files in a folder "Infinite Horizon - Hudson Beat":
  - `infinite-horizon.pdf`: the teacher and student resource, 23 pages, US Letter portrait.
  - `infinite-horizon-intro-deck.pptx`: the teacher-presented intro deck, 20 slides (16:9), speaker notes and a Class badge on every slide.
  - `infinite-horizon-intro-deck.pdf`: a PDF copy of the deck, 20 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `infinite-horizon-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, songs, presets, screenshots, student work or Logic sessions are in the ZIP.**

## 1. Title

```
Infinite Horizon in Logic Pro | Ambient Soundscape Project | High School
```
(72 characters; the limit is 80.)

## 2. Description

```
Ambient soundscape and automation project for high school: students build an evolving 60-90 second piece in Logic Pro with no beat and no song form, using a drone, layered textures and automation on filters, reverb, volume and panning. This Infinite Horizon project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the ideas (layering, automation, space and pacing) carry over to GarageBand and other music software.

WHAT'S INCLUDED (ZIP: 23-page PDF + 20-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup, a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a "What changed from the original" page, a Logic quick reference, a starter-template recipe with the Harder variation laid out, and a worked example (an invented 75-second piece on paper: four phases, five layers and five automation lanes) (10 pages)
• Student pages: Listening log, Phase plan, Automation plan, Listen-back sheet, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a presentation and feedback planner and a Reflection page (written or oral) (11 pages)
• Teacher-presented intro deck, 20 slides with speaker notes on every slide: a "music with no beat" hook, what Infinite Horizon is, the steps, four phases, "automate everything", a worked-example map, refining with your eyes closed, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: introduction, listen to ambient examples, begin a drone or pad foundation
• Class 2: layer additional textures and atmospheric elements
• Classes 3-5: working days: automate, refine, evolve the soundscape
• Class 6: final mix and bounce; prepare presentations and write 3 Padlet feedback questions
• Class 7: presentations with Padlet Q&A peer feedback

WHAT STUDENTS LEARN
• Building a soundscape from a drone, layers and effects
• Drawing automation on filters, reverb, volume and panning so a sound evolves
• Thinking in phases (opening, evolution, climax, fade) instead of a song form
• Listening closely, and refining a piece until nothing feels static
• Presenting their work and giving and getting feedback

GOOD TO KNOW
• There is no audio in this resource and no student work. You choose the ambient examples to play, and students make every sound in their projects themselves
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
- Tags in tpt.json: Autumn (proven; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Music Production, Ambient, Sound Design (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the owner teaches it.

## 7. Price

**$10.00** (paid), multiple-license price $10.00. Why $10 within the queue's $9-12 range: the kit matches its neighbours in size (23 pages + 20 slides, a worked example and a four-page set of student planning sheets), and the project teaches one specific, searchable skill (automation and ambient sound design) like the $10 kits Alchemy Architect, FX Deep Dive and Found Sound. It is priced above Free Play ($9, the lightest sheet) and below Billboard Top 10, Sample Flipping and Music for Visual Media ($12), which add current-hit analysis, a provided sample or video scoring.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 7-class pacing guide, the worked example, the project sheet requirements and steps, and the /25 rubric. "Number of pages or slides" is 43 (23 pages + 20 slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [x] **Reflection added (owner, 17 Oct 2026).** The owner's rubric (Documentation & Presentation) mentions reflection, but the Infinite Horizon sheet has no reflection task. By the owner's definition (a written or oral conversation about how the student did on the project and what they would do differently next time) the kit has the shared Reflection student page (written or oral, 4 prompts), a teacher note, a pacing line and a line on the closing slide. The /25 rubric is untouched and the page adds no points. Shared builder: `tpt/_dmp2_common/dmp2.py`.
- [ ] **Sources (owner's DMP2 sources rule, 17 Oct 2026).** Project text, steps and the /25 rubric come from Drive DMP2 > Projects (New) (Infinite Horizon: Project Sheet & Rubric; TEACHER NOTES: Infinite Horizon - Teacher Notes); the menu entry is quoted from the June 2026 Project Menu. The Teacher Notes name no supporting file. The older Projects > Infinite Horizon (Soundscape project) folder holds only a 2025 .docx outline, which is not a source. Drive holds no starter template, example piece or other artifact for this project.
- [ ] **Left out on purpose:** the Teacher Notes name an ambient album and three artists for reference listening (individual third-party authors). The kit names none and includes no audio; the teacher chooses what to play. The "What changed" page says so.
- [ ] **Invented additions (all labelled in the PDF):** the starter-template recipe (the Easier variation on paper) and the Harder variation laid out, the worked example "Slow Tide" (an invented 75-second piece: weak and clear plans, a map with four phases, five layers and five automation lanes, three sample Padlet questions), the Listening log, Phase plan, Automation plan and Listen-back sheet, the Logic quick reference, the setup suggestions (including a suggested minimum of three automation lanes), and the drawings. None adds a requirement or a rubric row. The owner's LMS name is written "your class page" (listed on the "What changed" page).
- [ ] **Open question for the owner:** (1) The Easier variation asks for a starter template with one drone layer and basic automation. Drive holds no such file, so the kit has a recipe on paper. If you have a small Logic starter project you made yourself (no Apple Loops, no third-party samples), it could be added to the ZIP (under 90 MB) in a later version. (2) Your Teacher Notes name an album and three artists for reference listening. They are left out so the kit names no individual third-party artist; say if you would like them listed in the description or on the setup page.
