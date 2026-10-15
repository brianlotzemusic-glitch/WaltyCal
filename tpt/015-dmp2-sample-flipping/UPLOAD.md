# UPLOAD: Sample Flipping, DMP2 project (TpT 015)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `sample-flipping.zip`. It holds three files in a folder "Sample Flipping - Hudson Beat":
  - `sample-flipping.pdf`: the teacher and student resource, 21 pages, US Letter portrait.
  - `sample-flipping-intro-deck.pptx`: the teacher-presented intro deck, 17 slides (16:9), speaker notes and a Class badge on every slide.
  - `sample-flipping-intro-deck.pdf`: a PDF copy of the deck, 17 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `sample-flipping-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No samples, audio, video, lyrics, songs or Logic sessions are in the ZIP.** The owner's provided sample set is deliberately left out (see Open question below); the kit tells teachers how to supply their own cleared sample set.

## 1. Title

```
Sample Flipping in Logic Pro | Quick Sampler Project | High School Music Tech
```
(77 characters; the limit is 80.)

## 2. Description

```
Sampling and Quick Sampler for high school music technology: students pick one sample, chop, pitch and reverse it in Logic Pro's Quick Sampler, program their own drums and build an original track around it. This Sample Flipping project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the music ideas (chopping, pitching, drum patterns, arrangement, mixing) carry over to GarageBand, Ableton Live and BandLab.

WHAT'S INCLUDED (ZIP: 21-page PDF + 17-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup with a guide to building your own cleared sample set, a sampling ethics and copyright page with discussion questions, a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a "What changed from the original" page, a Logic quick reference and a worked example (an original practice sample on paper, with slice, flip and drum grids) (11 pages)
• Student pages: Sample log, Chop map, drum plan grids, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page and a presentation and feedback planner (9 pages)
• Teacher-presented intro deck, 17 slides with speaker notes on every slide: a before-and-after hook, a plain-English definition of flipping, sampling ethics, worked examples, three Logic demos, the steps, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: intro to sample flipping and Quick Sampler, choose a sample
• Class 2: Quick Sampler deep dive, begin building
• Classes 3-5: working days: build the beat, layer and arrange, refine
• Class 6: final mix and bounce, rubric self-score, three feedback questions
• Class 7: presentations with peer feedback

WHAT STUDENTS LEARN
• Quick Sampler: Classic, One Shot and Slice modes, slicing, reversing and pitching
• Chopping: slice a sample and rearrange the pieces into a new idea
• Drum programming: self-made patterns that fit the style, with velocity for a human feel
• Sampling ethics: where a sound comes from, and who owns it
• Arrangement and mixing: layers that fit the style, EQ, panning and plug-ins

GOOD TO KNOW
• There are no samples in this resource. You supply your own cleared sample set (you record it, or use public-domain, CC0 or properly licensed sounds); the setup page shows how
• Requires Logic Pro 10.5 or later on a Mac. A MIDI keyboard helps but is not required
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
- Tags in tpt.json: Autumn (proven; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Creativity (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr2.1, MU:Cr3.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the owner teaches it.

## 7. Price

**$12.00** (paid), multiple-license price $12.00.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 7-class pacing guide, the Chop map, the project sheet requirements and steps, and the /25 rubric. "Number of pages or slides" is 38 (21 pages + 17 slides).

## 9. Before you click publish

- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student work, samples, audio or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Open question for the owner (inventory question 7):** the provided sample set in Drive (a folder of .wav files and a 109 MB ZIP) has file names that look like commercial sample-pack loops, not the owner's own recordings. Who made them and under what license? Until the owner confirms they are his own or licensed for redistribution, they stay out of the product. Also: the rubric's "reflection" wording has no reflection task on the sheet (the kit leaves it as written and says so on the grading page); the older 2023 "Project Outline" doc is a 10-class version with a different 4-row rubric and was not used.
