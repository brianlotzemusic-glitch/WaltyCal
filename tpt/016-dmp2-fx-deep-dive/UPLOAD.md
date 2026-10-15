# UPLOAD: FX Deep Dive, DMP2 project (TpT 016)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `fx-deep-dive.zip`. It holds three files in a folder "FX Deep Dive - Hudson Beat":
  - `fx-deep-dive.pdf`: the teacher and student resource, 22 pages, US Letter portrait.
  - `fx-deep-dive-intro-deck.pptx`: the teacher-presented intro deck, 18 slides (16:9), speaker notes and a Class badge on every slide.
  - `fx-deep-dive-intro-deck.pdf`: a PDF copy of the deck, 18 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `fx-deep-dive-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, songs, multitrack sessions or Logic sessions are in the ZIP.** The Cambridge-MT library is third party and is only named; students download from it themselves.

## 1. Title

```
FX Deep Dive in Logic Pro | EQ, Reverb, Delay Mixing Project | High School Music
```
(80 characters; the limit is 80.)

## 2. Description

```
Mixing and audio effects for high school music technology: students take an existing track, EQ and pan every part, and add at least 5 different effects in Logic Pro, each chosen for a reason. This FX Deep Dive project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the ideas (EQ, compression, reverb, delay, panning, modulation) carry over to GarageBand, Ableton Live and BandLab.

WHAT'S INCLUDED (ZIP: 22-page PDF + 18-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup with a guide to choosing a source track, a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a "What changed from the original" page, a Logic quick reference, an EQ guide with a five-minute live demo plan, and a worked example (an invented eight-track session on paper, with an EQ map, pan map, delay times and a compressor example) (10 pages)
• Student pages: Source log, FX notes, Track map, FX log, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page and a presentation and feedback planner (10 pages)
• Teacher-presented intro deck, 18 slides with speaker notes on every slide: a dry-and-mixed hook, what effects do, choosing a source, a live EQ demo, panning, reverb and delay on a send, compression by the numbers, the steps, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: review the 11 FX from class notes, listen to examples, choose a source
• Classes 2-5: core working days: apply FX, EQ all tracks, set panning
• Class 6: final adjustments, bounce, rubric self-score, three feedback questions
• Class 7: presentations with peer feedback

WHAT STUDENTS LEARN
• EQ: where sounds live in the frequency range, and when to cut or boost
• Panning: placing each instrument in the stereo field
• Effects with a purpose: compression, reverb, delay and modulation, each tested with and without (A/B)
• Matching effects to genre and style
• Presenting their mix and giving and getting feedback

GOOD TO KNOW
• There is no audio in this resource. Students use a project of their own, or download a multitrack from the Cambridge-MT library themselves; the setup page shows how to choose and pre-select sessions
• Requires Logic Pro on a Mac. A MIDI keyboard is not needed
• Rubric: 5 categories scored 1-5, /25; the final grade is the average of the student's and the teacher's score
• Grades 9-12 (the second year of my music production course); no music reading needed
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present the PDF copy, which shows the intended look
• A "What changed from the original" page lists every change to my classroom wording
• Every student page prints well in black and white

Logic Pro is a trademark of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Designed with the help of digital and AI tools, and checked by hand.
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every DMP item. DMP2 is the owner's second-year course (the PDF and description say so); some schools take it in 9th grade.

## 4. Subjects and tags

Per tpt/METADATA-GUIDE.md, `tpt.json` keeps only values TpT has accepted so far.
- Subjects in tpt.json: Music. Candidate extras: Career and Technical Education; Computer Science - Technology
- Tags in tpt.json: Autumn (proven; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Music Production (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr3.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the owner teaches it.

## 7. Price

**$10.00** (paid), multiple-license price $10.00.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 7-class pacing guide, the Track map, the project sheet requirements and steps, and the /25 rubric. "Number of pages or slides" is 40 (22 pages + 18 slides).

## 9. Before you click publish

- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student work, audio or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Open question for the owner:** the sheet says "the 11 FX from your class notes" and "the Native Instruments video", but the video's title in the teacher notes says "10 FX". Which 11 effects do you teach? The kit leaves the list blank for students (page 13) instead of guessing; send the list and a later version can name them. Also: the EQ Cheatsheet PDF and Plug-in Links doc are named in the teacher notes but are not in the Drive folder I read, so they are not included (the kit has its own EQ guide). The rubric's "reflection" wording has no reflection task on the sheet (the kit leaves it as written and says so on the grading page). The older 2025 "Project 4 - FX Deep Dive" doc (/20 rubric, 10 class periods) was not used.
