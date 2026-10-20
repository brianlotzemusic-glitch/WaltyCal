# UPLOAD: Pattern Prodigy, DMP2 project (TpT 024)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `pattern-prodigy.zip`. It holds three files in a folder "Pattern Prodigy - Hudson Beat":
  - `pattern-prodigy.pdf`: the teacher and student resource, 24 pages, US Letter portrait.
  - `pattern-prodigy-intro-deck.pptx`: the teacher-presented intro deck, 20 slides (16:9), speaker notes and a Class badge on every slide.
  - `pattern-prodigy-intro-deck.pdf`: a PDF copy of the deck, 20 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `pattern-prodigy-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, songs, presets, screenshots, student work or Logic sessions are in the ZIP.**

## 1. Title

```
Pattern Prodigy in Logic Pro | Step Sequencer Beat Project | High School
```
(72 characters; the limit is 80.)

## 2. Description

```
Step Sequencer groove project for high school: students build an original 30-60 second loop-based piece in Logic Pro with Pattern Regions for drums, bass and synths, then make it evolve with probability, velocity and automation. This Pattern Prodigy project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the ideas (step patterns, variation, layering and arrangement) carry over to GarageBand and other music software.

WHAT'S INCLUDED (ZIP: 24-page PDF + 20-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup (with a hi-hat probability demo), a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a "What changed from the original" page, a Logic quick reference, a pre-built drum pattern chart with the Harder variation laid out, and a two-page worked example (an invented 50-second piece on paper: 16-step patterns, four sections, five layers, five Step Sequencer features and four automation lanes) (12 pages)
• Student pages: Pattern grids, Feature tracker, Arrangement plan with a length helper, Listen-back sheet, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a presentation and feedback planner and a Reflection page (written or oral) (12 pages)
• Teacher-presented intro deck, 20 slides with speaker notes on every slide: a "beat that changes" hook, what Pattern Prodigy is, the steps, how to read a pattern grid, four ways to make a pattern evolve, a worked-example map, probability, mixing and refining, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: introduction to the Step Sequencer and Pattern Regions, guided exploration
• Class 2: build drum and percussion patterns, begin adding melodic layers
• Classes 3-5: working days: explore automation, probability and variation
• Class 6: final mix and bounce; prepare presentations and write 3 Padlet feedback questions
• Class 7: presentations with Padlet Q&A peer feedback

WHAT STUDENTS LEARN
• Programming drum, bass and synth patterns on a 16-step grid
• Using probability, velocity and step automation so a loop never sounds the same twice
• Using mute and unmute to build an arrangement from patterns
• Balancing a mix with EQ, panning and plug-ins
• Presenting their work and giving and getting feedback

GOOD TO KNOW
• There is no audio in this resource and no student work. Students make every sound in their projects themselves, from the instruments and kits in Logic
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
- Tags in tpt.json: Autumn (proven; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Music Production, Beat Making, Drum Programming (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the owner teaches it.

## 7. Price

**$10.00** (paid), multiple-license price $10.00. Why $10 within the queue's $9-12 range: the kit matches its neighbours in size (24 pages + 20 slides, a two-page worked example and four student planning sheets), and it teaches one specific, searchable skill (Step Sequencer beat programming) like the $10 kits Infinite Horizon, Alchemy Architect, FX Deep Dive and Found Sound. It is priced above Free Play ($9, the lightest sheet) and below Billboard Top 10, Sample Flipping and Music for Visual Media ($12), which add current-hit analysis, a provided sample or video scoring.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 7-class pacing guide, the worked example, the project sheet requirements and steps, and the /25 rubric. "Number of pages or slides" is 44 (24 pages + 20 slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [x] **Reflection added (owner, 17 Oct 2026).** The owner's rubric (Documentation & Presentation) mentions reflection, but the Pattern Prodigy sheet has no reflection task. By the owner's definition (a written or oral conversation about how the student did on the project and what they would do differently next time) the kit has the shared Reflection student page (written or oral, 4 prompts), a teacher note, a pacing line and a line on the closing slide. The /25 rubric is untouched and the page adds no points. Shared builder: `tpt/_dmp2_common/dmp2.py`.
- [ ] **Sources (owner's DMP2 sources rule, 17 Oct 2026).** Project text, steps and the /25 rubric come from Drive DMP2 > Projects (New) (Pattern Prodigy: Project Sheet & Rubric; TEACHER NOTES: Pattern Prodigy - Teacher Notes); the menu entry is quoted from the June 2026 Project Menu. The older Projects > Pattern Prodigy folder (a 2025 outline .docx, a doc of YouTube links and two tutorial videos) is not a source.
- [ ] **Left out on purpose:** no video, link or audio. The Teacher Notes list three YouTube tutorials; the kit lists them as written and includes none.
- [ ] **Invented additions (all labelled in the PDF):** the pre-built drum pattern chart (the Easier variation on paper) and the Harder variation laid out, the worked example "Night Shift" (an invented 50-second, 96 BPM piece: weak and clear plans, one bar of 16-step patterns, five features, a map with four sections, five layers and four automation lanes, three sample Padlet questions), the Pattern grids, Feature tracker, Arrangement plan and Listen-back sheet, the Logic quick reference, the hi-hat demo and the suggested list of features that count, and the drawings. None adds a requirement or a rubric row. The owner's LMS name is written "your class page" (listed on the "What changed" page).
- [ ] **Open question for the owner:** (1) The Easier variation asks for a pre-built drum pattern. Drive holds no such Logic project, so the kit has a 16-step chart on paper. If you have a small Logic project you made yourself (no Apple Loops, no third-party samples) it could be added to the ZIP (under 90 MB) in a later version. (2) The older Pattern Prodigy folder holds two tutorial videos you recorded ("Logic Step Sequencer - Getting Started", 38 MB, and "Logic Pro - Live Pattern Recording", 15 MB). The kit does not include them. Say if you want them in the ZIP or linked from the setup page. (3) The sheet says "at least 3 different Step Sequencer features" without listing them; the kit suggests probability, velocity, step automation, mute/unmute and pattern alternates (the ones your notes and tips name). Say if you count others.
