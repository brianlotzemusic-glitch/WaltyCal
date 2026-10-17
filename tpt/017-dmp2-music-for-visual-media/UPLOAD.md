# UPLOAD: Music for Visual Media, DMP2 project (TpT 017)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `music-for-visual-media.zip`. It holds three files in a folder "Music for Visual Media - Hudson Beat":
  - `music-for-visual-media.pdf`: the teacher and student resource, 26 pages, US Letter portrait.
  - `music-for-visual-media-intro-deck.pptx`: the teacher-presented intro deck, 18 slides (16:9), speaker notes and a Class badge on every slide.
  - `music-for-visual-media-intro-deck.pdf`: a PDF copy of the deck, 18 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `music-for-visual-media-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No video, audio, lyrics, songs, screenshots or Logic sessions are in the ZIP.** The two DMP1 Unit 5 videos (244 MB and 209 MB) are too big for TpT and git, so they are named on the kit's Videos page instead. Video clips belong to their makers, so the kit neither contains nor links to any clip; students use their own footage or a clip they may use, and the setup page explains how to choose one.

## 1. Title

```
Film Scoring in Logic Pro | Music for Visual Media Project | High School Music
```
(78 characters; the limit is 80.)

## 2. Description

```
Film scoring and sync for high school music technology: students choose a 2-3 minute video clip and compose an original soundtrack in Logic Pro that matches its mood and pacing, with key moments timed to the picture. This Music for Visual Media project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the ideas (mood, tempo, hit points, markers, dynamics) carry over to GarageBand, Ableton Live and BandLab.

WHAT'S INCLUDED (ZIP: 26-page PDF + 18-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup with a guide to choosing a clip students may use, a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a "What changed from the original" page, a Logic quick reference, a sync and timing guide (seconds, bars, tempo and frames), my own "Composing to Picture" advice page (watch, mark your moments, silence, match the energy), and a worked example (an invented 90-second scene on paper, with a timeline, a cue sheet and a loudness plan) and a Videos page naming my two Unit 5 tutorial videos (12 pages)
• Student pages: Clip log, Watch notes, Score plan, Cue sheet, Sync log, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page and a presentation and feedback planner and a Reflection page (written or oral) (12 pages)
• Teacher-presented intro deck, 18 slides with speaker notes on every slide: a sound-off-then-on hook, what a score does, choosing a clip, a markers demo in Logic, bars and seconds, planning the score, shaping the dynamics, the steps, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: introduction; students select and import their video and study the clip
• Class 2: plan the score: mark key moments, decide on mood and instrumentation
• Classes 3-5: working days: compose, layer and sync the score
• Class 6: final mix, bounce, sync audio to video, prepare presentations
• Class 7: presentations with peer feedback

WHAT STUDENTS LEARN
• Scoring: composing music that serves a visual story
• Sync: finding each hit point, reading time in seconds, bars and frames, and landing the music on the moment
• Mood, atmosphere and pacing through musical choices
• Dynamics: using quiet and silence as well as loud
• Presenting their work and giving and getting feedback

GOOD TO KNOW
• There is no video or audio in this resource (two tutorial videos from my course are named on a Videos page; they are too large to include). Students use their own clip, or one they may use; the setup page shows five checks for any clip and how to keep a log of where it came from
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
- Tags in tpt.json: Autumn (proven; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Music Production, Film Scoring (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr3.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the owner teaches it.

## 7. Price

**$12.00** (paid), multiple-license price $12.00.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 7-class pacing guide, the Cue sheet, the project sheet requirements and steps, and the /25 rubric. "Number of pages or slides" is 44 (26 pages + 18 slides).

## 9. Before you click publish

- [ ] **Already live on TpT: the rebuilt PDF, ZIP, deck and images add the Reflection page and are for the owner's later re-upload.** The `uploaded` and `release` files are untouched; the new files need a fresh QA pass (QA-v3.md) before any re-upload.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student work, video, audio or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Rebuilt 17 Oct 2026 (v2) with the DMP2 sources rule.** Wording, steps and rubric are still the Projects (New) versions. New: page 11 "Composing to picture", the owner's own advice from the DMP1 Spooky Tunes project sheet (credited "from the teacher's own materials"). Searched DMP2 (Projects (New), Projects, root), the older Music for Visual Media folder and DMP1 (New) Unit 5. Not found, so left out (the owner confirmed on 17 Oct 2026 there is nothing to add): a list of film scoring examples, a Logic markers tutorial document, and the 3-5 pre-selected clips for the easier variation. Price stays $12 (one added page does not justify a change).
- [x] **Closed (owner, 17 Oct 2026):** no clip list for the easier variation and no film-scoring or markers-tutorial links; the kit stays without them.
- [x] **Reflection added (owner, 17 Oct 2026).** The owner's rubric (Documentation & Presentation) mentions reflection, but the project sheet has no reflection task. By the owner's definition (a written or oral conversation about how the student did on the project and what they would do differently next time) the kit now has a Reflection student page (written or oral, 4 prompts), a teacher note, a pacing line and a line on the closing slide. The /25 rubric is untouched and the page adds no points. Shared builder: `tpt/_dmp2_common/dmp2.py`.
- [ ] **Open question for the owner: the two DMP1 Unit 5 videos could not go in the ZIP.** Drive > 5 - Spooky Project holds "How to import a movie into Logic.mov" (243,604,831 bytes, 244 MB) and "Walking Through the Woods at Night.mp4" (209,166,623 bytes, 209 MB). Each is far over the ~90 MB per-file ceiling for git and for a TpT download, git LFS is not set up in this repo, and files that size cannot be pulled through the Drive connector, so neither was downloaded or committed. Fallback in the PDF: the Videos page names both files with their sizes, says they are not included in this download and that teachers can use their own copies; it makes no promise to buyers. Please (1) decide how the files will be supplied, or give compressed copies under 90 MB each (then list them in `ZIP_EXTRA` in gen.py and the ZIP check will pick them up), and (2) confirm the "Walking Through the Woods at Night" video is yours to share (only its title is known here).
