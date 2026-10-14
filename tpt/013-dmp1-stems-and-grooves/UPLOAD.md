# UPLOAD: Stems & Grooves, DMP1 Unit 2 (TpT 013)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `stems-and-grooves.zip`. It holds three files in a folder "Stems and Grooves - Hudson Beat":
  - `stems-and-grooves.pdf`: the teacher and student resource, 28 pages, US Letter portrait.
  - `stems-and-grooves-intro-deck.pptx`: the teacher-presented intro deck, 22 slides (16:9), speaker notes and a Day badge on every slide.
  - `stems-and-grooves-intro-deck.pdf`: a PDF copy of the deck, 22 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `stems-and-grooves-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). No stems, audio, video or Logic sessions are in the ZIP: the owner's classroom stems are third-party audio, so the kit tells the teacher where to find stems they may use and gives a recipe for making two in Logic. The one song is named by title and artist only.

## 1. Title

```
Drum Fills in Logic Pro | Stems & Transitions | High School Music Technology
```
(76 characters; the limit is 80.)

## 2. Description

```
Drum fills and transitions for high school music technology: students write drums over a stem (a song with the drums taken out), first two contrasting grooves, then a full song with a fill, breakdown, cut or build at every section change, all in Logic Pro. This 6-day unit is Unit 2 of my Digital Music Production 1 course; the steps are written for Logic Pro, while the music ideas (listening for sections, groove contrast, transitions, gain staging) carry over to GarageBand, Ableton Live and BandLab.

WHAT'S INCLUDED (ZIP: 28-page PDF + 22-slide intro deck as .pptx and PDF)
• How to use, unit overview, setup, a Logic quick reference, and two pages on the stems: where to find stems you may use in class, and a 30-minute recipe for making your own two stems in Logic (6 pages)
• 6-day pacing guide and minute-by-minute day plans, with the deck slides for each block (4 pages)
• Teacher notes: the big idea, five common student struggles, variations, the gain staging mini-lesson and grading tips (3 pages)
• Student pages: the Day 1 classroom post, the four transitions with drum grids, gain staging, a section map worksheet, the 4-page project sheet with requirements, steps, tips and submission checklist, the /25 rubric, and a "name that transition" quick check (10 pages)
• Answer keys and worked examples: A and B patterns ready to program, the four transitions step by step with the quiz answers, and a fully mapped full song (3 pages)
• Teacher-presented intro deck, 22 slides with speaker notes on every slide: a pop-culture hook, a plain-English definition of a stem, guided listening questions, worked examples, the steps, deliverables and rubric

THE SIX DAYS
• Day 1, Listen first: hear the stem with no drums, meet the four transitions, map the sections, start the A pattern
• Day 2, Foundation: build a contrasting B pattern, place both, then gain staging: nothing in the red
• Day 3, Transition workshop: map every section change in a full song and build transitions in 64-step mode
• Day 4, Full working day: finish every transition and play it all the way through
• Day 5, Submit: checklists, rubric and three feedback questions
• Day 6, Present: play the drums with the stem and explain each transition

WHAT STUDENTS LEARN
• Listen first, then respond: drums that belong to the music, not just on top of it
• Two grooves with real contrast, placed where the sections change
• Drum fill, breakdown, cut and build, and which one fits each moment
• Gain staging: turn other things down instead of turning one thing up

GOOD TO KNOW
• Requires Logic Pro on a Mac (10.5 or later). No MIDI keyboard needed: everything is clicked into the Step Sequencer. Builds on Unit 1, Beat From Nothing (sold separately)
• The stems are not included. You supply them: make your own with the recipe in the kit, or use audio you have the right to use in class
• Built for about 53-minute periods, grades 9-12; no music reading needed
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present the PDF copy, which shows the intended look
• One song is named by title and artist (In the Air Tonight by Phil Collins); play it from your own YouTube or Spotify access. No audio, video, lyrics or album art are included
• Every student page prints well in black and white

Logic Pro is a trademark of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Designed with the help of digital and AI tools, and checked by hand.
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), the same slugs as items 008-012.

## 4. Subjects

Per tpt/METADATA-GUIDE.md. `tpt.json` keeps only values TpT has accepted so far, so the nightly upload cannot fail on an unknown option.
- Subjects in tpt.json: Music. After the dry run, add by hand (or into tpt.json if accepted): Career and Technical Education; Computer Science - Technology
- Tags in tpt.json: Autumn (proven on 002, 004, 009-011; this unit is taught in September and October). After the dry run, add High School, Project Based Learning, Technology and Back to School if the Tag list offers them (max 6), and drop Autumn once they are accepted
- Formats: PDF (add PowerPoint or ZIP if TpT offers it, since the product includes a .pptx)

## 5. Resource type

- Unit Plans
- Projects
- PowerPoint Presentations

(`tools/tpt.js` does not set resource type; pick these by hand if TpT asks.)

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr2.1 (developing musical ideas), MU:Cr3.1 (refining work), MU:Pr6.1 (presenting). Tag only if it matches how the owner teaches it; it can be left blank.

## 7. Price

**$10.00** (paid), multiple-license price $10.00. At Basic seller rates this nets about $5.20 per sale (55% minus $0.30).

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 pages, watermarked "PREVIEW"): the 6-day pacing guide, the four transitions page, the project requirements page and the /25 rubric. "Number of pages or slides" is 50 (28 pages + 22 slides).

## 9. Before you click publish

- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student work, stems, audio or Logic session anywhere (gen.py --check scans every output and every file in this folder, including the names of the owner's third-party stems).
- [ ] Owner questions in the Designer's report answered (newest project sheet vs the Restructure's Group 1/Group 2 version with AABA and reverb; checklist "Your Name - Foundations" for both projects; Day 1 post "A, B, A, B, etc." vs AABA; "a real professional recording" with teacher-made stems; the 48-minute Days 1 and 3; whether to name the Cambridge-MT library).
- [ ] Optional (Manager): a Google Slides copy of the deck can go in a NEW Drive folder "DMP Sale Decks"; never edit the owner's originals.
