# UPLOAD: Alchemy Architect, DMP2 project (TpT 018)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `alchemy-architect.zip`. It holds three files in a folder "Alchemy Architect - Hudson Beat":
  - `alchemy-architect.pdf`: the teacher and student resource, 23 pages, US Letter portrait.
  - `alchemy-architect-intro-deck.pptx`: the teacher-presented intro deck, 18 slides (16:9), speaker notes and a Class badge on every slide.
  - `alchemy-architect-intro-deck.pdf`: a PDF copy of the deck, 18 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `alchemy-architect-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, songs, Alchemy presets, screenshots or Logic sessions are in the ZIP.** Students make every sound themselves.

## 1. Title

```
Alchemy Synth in Logic Pro | Sound Design Synthesis Project | High School Music
```
(79 characters; the limit is 80.)

## 2. Description

```
Synthesizer sound design for high school music technology: students explore Logic Pro's Alchemy synth, design three patches from scratch using oscillators, filters, envelopes and modulation, and compose a 45-60 second original track that features them. This Alchemy Architect project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the ideas (oscillators, filters, envelopes, LFOs) carry over to other synthesizers, including those in GarageBand and Ableton Live.

WHAT'S INCLUDED (ZIP: 23-page PDF + 18-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup (keeping Alchemy small, a save-as-you-go routine), a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, my two tutorial links with my notes, grading), a "What changed from the original" page, an Alchemy quick reference, a synth guide (waveforms, harmonics, filter, envelope and LFO numbers), and a worked example (three invented patches and a 26-bar track plan on paper) (10 pages)
• Student pages: Explore sheet, Patch cards, Track plan, Mix check, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page and a presentation and feedback planner (11 pages)
• Teacher-presented intro deck, 18 slides with speaker notes on every slide: a "who designed this sound?" hook, the four building blocks, drawings of the four waveforms, a filter, an envelope and an LFO, a build-a-patch demo, the steps, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: introduction to Alchemy; guided exploration of the interface
• Class 2: sound design basics (oscillators, filters, envelopes); begin Patch 1
• Classes 3-5: working days: design the remaining patches and compose the track
• Class 6: final mix and bounce; prepare presentations
• Class 7: presentations with peer feedback

WHAT STUDENTS LEARN
• Synthesis: oscillators, filters, envelopes (ADSR) and modulation, and how to save a patch
• Sound design: shaping a sound from a simple waveform, and layering and effects to thicken it
• Composing with their own three patches, with effects and automation
• Mixing and bouncing a finished track
• Presenting their work and giving and getting feedback

GOOD TO KNOW
• There is no audio in this resource. Students make every sound themselves in Alchemy, so every track is original
• Requires Logic Pro on a Mac (Alchemy comes with it). A MIDI keyboard is not needed
• Rubric: 5 categories scored 1-5, /25; the final grade is the average of the student's and the teacher's score
• Grades 9-12 (the second year of my music production course); no music reading needed
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present the PDF copy, which shows the intended look
• A "What changed from the original" page lists every change to my classroom wording
• Every student page prints well in black and white

Logic Pro and Alchemy are products of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Designed with the help of digital and AI tools, and checked by hand.
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every DMP item. DMP2 is the owner's second-year course (the PDF and description say so); some schools take it in 9th grade.

## 4. Subjects and tags

Per tpt/METADATA-GUIDE.md, `tpt.json` keeps only values TpT has accepted so far.
- Subjects in tpt.json: Music. Candidate extras: Career and Technical Education; Computer Science - Technology
- Tags in tpt.json: Autumn (proven; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Music Production, Synthesizer, Sound Design (max 6)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr3.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the owner teaches it.

## 7. Price

**$10.00** (paid), multiple-license price $10.00. Why $10 within the queue's $9-12 range: it has the same structure and page count as FX Deep Dive (also a structured project, $10), it needs no outside media, and the three-patch scope is lighter than the $12 open-ended kits with a clip or sample workflow. The DMP-INVENTORY plan says "remaining at $9-12". Rebuild of 17 Oct: the only new content is two tutorial links and the owner's notes on them, which does not justify a change, so the price stays $10.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the 7-class pacing guide, the worked example, the project sheet requirements and steps, and the /25 rubric. "Number of pages or slides" is 41 (23 pages + 18 slides).

## 9. Before you click publish

- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student work, audio, video or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Sources (rebuild of 17 Oct 2026, owner's DMP2 sources rule).** Project text, steps and the /25 rubric come from Drive DMP2 > Projects (New) (Project Sheet & Rubric, Teacher Notes). Supporting artifacts found in the other DMP2 folders and now used: the owner's Doc "Youtube tutorials - Alchemy Architect" (Projects (old) > Alchemy Architect (Sound Synthesis)), giving the two tutorial links and the owner's one-line notes, shown on teacher notes page 7 as links/titles only (credited as from the teacher's own materials; no video is included or embedded). Logic's built-in Alchemy documentation: no owner file or link exists, so it is named only.
- [ ] **Open questions for the owner:** (1) "Simple view": the Teacher Notes are the only owner file that uses that label (no other Drive file says "Simple view"); the kit keeps it and tells teachers to check the labels on their version of Logic. Correct? (2) The Alchemy Architect (Sound Synthesis) folder also holds two saved .mp4 copies of third-party YouTube videos ("ALCHEMY - Get the Most of Logic's Powerhouse Synth", "Logic Pro's Most SLEPT ON Instrument") and an "Alchemy Samples" folder of Alchemy presets (.aaz). They are not owner-made, so none is included or named. Say if you want either added. (3) The rubric's "reflection" wording has no reflection task on the sheet (the kit leaves it as written and says so on the grading page).
- Closed (owner, 17 Oct 2026): the June 2026 menu entry is fine; the 2025 Project Outline (different rubric) is not a source.
