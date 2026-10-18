# UPLOAD: Found Sound, DMP2 project (TpT 020)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `found-sound.zip`. It holds three files in a folder "Found Sound - Hudson Beat":
  - `found-sound.pdf`: the teacher and student resource, 22 pages, US Letter portrait.
  - `found-sound-intro-deck.pptx`: the teacher-presented intro deck, 19 slides (16:9), speaker notes and a Class badge on every slide.
  - `found-sound-intro-deck.pdf`: a PDF copy of the deck, 19 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `found-sound-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, songs, presets, screenshots or Logic sessions are in the ZIP.** Students record every sound themselves.

## 1. Title

```
Found Sound in Logic Pro | Quick Sampler Sound Design Project | High School
```
(75 characters; the limit is 80.)

## 2. Description

```
Sound design project for high school music technology: students record at least five everyday sounds, trim and normalize them in Logic Pro, turn them into playable instruments with Quick Sampler, and compose a 30-60 second piece with at least three layers (percussion, bass, texture) built entirely from found sounds. This Found Sound project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the ideas (recording and editing real-world sounds, sampling, layering, mixing) carry over to GarageBand and other music software.

WHAT'S INCLUDED (ZIP: 22-page PDF + 19-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup (clean recordings, a way to build a sound bank), a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, my three suggested resources, grading), a "What changed from the original" page, a Logic quick reference, a Quick Sampler modes page (Classic, One Shot and Slice drawn), and a worked example (an invented 45-second piece on paper) (10 pages)
• Student pages: Sound log, Instrument builder, Layer plan, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a presentation and feedback planner and a Reflection page (written or oral) (10 pages)
• Teacher-presented intro deck, 19 slides with speaker notes on every slide: a "name that sound" listening hook, what found sound is, the path from sound to song, live demos of Quick Sampler, the three modes drawn, the steps, a worked-example timeline, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: introduction; demo Quick Sampler with a live recording; students begin collecting sounds
• Class 2: edit and prep recordings; begin building instruments in Quick Sampler
• Classes 3-5: working days: compose, layer and mix
• Class 6: final mix, bounce; prepare presentations
• Class 7: presentations with Padlet Q&A peer feedback

WHAT STUDENTS LEARN
• Recording clean audio with a phone or a microphone, then trimming and normalizing it
• Turning any sound into a playable instrument with Quick Sampler (Classic, One Shot and Slice)
• Sound design: layering percussion, bass and texture from found sounds
• Effects, automation and mixing for a polished piece
• Presenting their work and giving and getting feedback

GOOD TO KNOW
• There is no audio in this resource. Students record every sound themselves, so every piece is original
• Requires Logic Pro on a Mac (Quick Sampler is part of Logic Pro) and a phone or microphone to record with. A MIDI keyboard is not needed
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
- Tags in tpt.json: Autumn (proven; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Music Production, Sound Design, Quick Sampler (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the owner teaches it.

## 7. Price

**$10.00** (paid), multiple-license price $10.00. Why $10 within the queue's $9-12 range: the kit has the same size and structure as Alchemy Architect and Anti-Music Manifesto (22 pages + 19 slides, 7 classes, a worked example, three student working pages), and it needs no outside media. The $12 kits in the plan (Music for Visual Media, Sample Flipping) rest on a clip or sample workflow that this open-ended project does not have. The DMP-INVENTORY plan says "remaining at $9-12".

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 7-class pacing guide, the worked example, the project sheet requirements and steps, and the /25 rubric. "Number of pages or slides" is 41 (22 pages + 19 slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student work, audio, video or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [x] **Reflection added (owner, 17 Oct 2026).** The owner's rubric (Documentation & Presentation) mentions reflection, but the project sheet has no reflection task. By the owner's definition (a written or oral conversation about how the student did on the project and what they would do differently next time) the kit has a Reflection student page (written or oral, 4 prompts), a teacher note, a pacing line and a line on the closing slide. The /25 rubric is untouched and the page adds no points. Shared builder: `tpt/_dmp2_common/dmp2.py`.
- [ ] **Sources (owner's DMP2 sources rule, 17 Oct 2026).** Project text, steps and the /25 rubric come from Drive DMP2 > Projects (New) (Found Sound: Project Sheet & Rubric; TEACHER NOTES: Teacher Notes); the menu entry is quoted from the June 2026 Project Menu. The Teacher Notes name three suggested resources (two Quick Sampler tutorials and an example editing session, all on YouTube). They are third-party videos and no owner-made copy exists in the other DMP2 folders (the older Projects > Found Sound Project folder holds only the 2025 outline and a list of YouTube links, which are not a source), so the kit prints them as the owner wrote them, with nothing included: no link, audio or video.
- [ ] **Invented additions (all labelled in the PDF):** the Quick Sampler modes page and drawing, the worked example "Passing Period" (a 45-second piece on paper at 96 BPM) with three sample Padlet questions, the recording tips and twelve sound ideas on the setup page, the Instrument builder, Layer plan and Sound log, the Logic quick reference, and the live-demo outlines on slides 6 and 9. None adds a requirement or a rubric row.
- [ ] **Open questions for the owner:** (1) Do you have your own links or videos for the three suggested resources (Quick Sampler tutorials, a found-sound editing session)? None is in Drive; if you send them, they can be added. (2) The kit describes Quick Sampler's Classic, One Shot and Slice modes in general terms from your notes; please glance at page 10 to confirm it matches how you teach them.
