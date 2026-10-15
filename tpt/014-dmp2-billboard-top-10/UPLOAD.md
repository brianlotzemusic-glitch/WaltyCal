# UPLOAD: Billboard Top 10, DMP2 project (TpT 014)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `billboard-top-10.zip`. It holds three files in a folder "Billboard Top 10 - Hudson Beat":
  - `billboard-top-10.pdf`: the teacher and student resource, 20 pages, US Letter portrait.
  - `billboard-top-10-intro-deck.pptx`: the teacher-presented intro deck, 17 slides (16:9), speaker notes and a Class badge on every slide.
  - `billboard-top-10-intro-deck.pdf`: a PDF copy of the deck, 17 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `billboard-top-10-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). No songs, audio, video, lyrics, chart data or Logic sessions are in the ZIP. The one song named anywhere (the owner's own song form example in the teacher notes resource list) is named by title and artist only.

## 1. Title

```
Song Form in Logic Pro | Billboard Top 10 Remake | High School Music Technology
```
(79 characters; the limit is 80.)

## 2. Description

```
Song form and drum programming for high school music technology: students study the current Billboard Top 10, pick one song, map its form, program its drums and recreate it in Logic Pro at the original tempo. This project takes 7 class periods and comes from my Digital Music Production 2 course; the steps are written for Logic Pro, while the music ideas (song form, tempo, drum patterns, arrangement, mixing) carry over to GarageBand, Ableton Live and BandLab.

WHAT'S INCLUDED (ZIP: 20-page PDF + 17-slide intro deck as .pptx and PDF)
• Teacher pages: how to use, project overview, setup with a song-choice guide, a 7-class pacing guide with the deck slides for each class, two pages of teacher notes (struggles, variations, resources, grading), a "What changed from the original" page, a Logic quick reference and a worked example (an original practice song map with tempo math and drum grids) (9 pages)
• Student pages: Top 10 analysis, Song Form map, drum pattern analysis grids, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page and a presentation and feedback planner (9 pages)
• Teacher-presented intro deck, 17 slides with speaker notes on every slide: a pop-culture hook (this week's No. 1), a plain-English definition of emulation, guided listening questions, worked examples, two Logic demos, the steps, what to turn in and the rubric

THE SEVEN CLASS PERIODS
• Class 1: explore the Billboard Top 10, complete the Top 10 analysis, begin the song form
• Class 2: finish the Song Form map, analyze the drum patterns, begin programming in Logic
• Classes 3-5: working days: build the foundation, add layers, refine the arrangement
• Class 6: final mix and bounce, rubric self-score, three feedback questions
• Class 7: presentations with peer feedback

WHAT STUDENTS LEARN
• Song form: count bars, map every section and set Arrangement Markers
• Tempo: find the BPM and match it exactly
• Drum programming: hear the kick, snare and hi-hat and program them, with velocity for a human feel
• Arrangement and mixing: instruments that fit the genre, EQ, panning, levels and plug-ins

GOOD TO KNOW
• Requires Logic Pro on a Mac (a current version). A MIDI keyboard helps but is not required
• There are no songs in this resource: students choose from the current Billboard Top 10 (billboard.com) and listen on YouTube or Spotify through your own access. Preview the songs for your school
• Rubric: 5 categories scored 1-5, /25; the final grade is the average of the student's and the teacher's score
• Grades 10-12 (the second year of my music production course); no music reading needed
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present the PDF copy, which shows the intended look
• A "What changed from the original" page lists every change to my classroom wording
• Every student page prints well in black and white

Billboard and Hot 100 are trademarks of their owner, named only to describe the chart students listen to; this resource is not affiliated with Billboard. Logic Pro is a trademark of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Designed with the help of digital and AI tools, and checked by hand.
```

## 3. Grades

10th, 11th, 12th (`10th-grade`, `11th-grade`, `12th-grade` in tpt.json). These slugs are proven on items 008-013. DMP2 is the owner's second-year course, so 9th is left out; add `9th-grade` if the owner wants it (the slug is proven too).

## 4. Subjects and tags

Per tpt/METADATA-GUIDE.md, `tpt.json` keeps only values TpT has accepted so far, so the nightly upload cannot fail on an unknown option.
- Subjects in tpt.json: Music. Candidate extras (add by hand after a dry run, or into tpt.json once accepted): Career and Technical Education; Computer Science - Technology
- Tags in tpt.json: Autumn (proven on 002, 004, 009-013; DMP2 runs as a semester course). Candidate extras: High School, Project Based Learning, Technology, Creativity (max 6); drop Autumn once they are accepted
- Formats: PDF (add PowerPoint or ZIP if TpT offers it, since the product includes a .pptx)
- Answer key: left out of tpt.json (there is no answer key; the worked example is a model, not a key, and "Included" is the only proven option text). Set "Not included" by hand if TpT asks

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

(`tools/tpt.js` does not set resource type; pick these by hand if TpT asks.)

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Re7.2 (analyzing structure), MU:Cr2.1 (developing ideas), MU:Cr3.1 (refining work), MU:Pr6.1 (presenting). Tag only if it matches how the owner teaches it; it can be left blank.

## 7. Price

**$12.00** (paid), multiple-license price $12.00. At Basic seller rates this nets about $6.30 per sale (55% minus $0.30).

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 pages, watermarked "PREVIEW"): the 7-class pacing guide, the Song Form map, the project sheet requirements and steps, and the /25 rubric. "Number of pages or slides" is 37 (20 pages + 17 slides).

## 9. Before you click publish

- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student work, songs, audio or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] Owner questions in the Designer's report answered (see log/ACTION-LOG.md, 15 Oct: "Billboard" in the title and on the cover; the rubric's "reflection" wording with no reflection task on the sheet; the 2023 Billboard doc and form from another teacher's account in Drive; the grade range).
- [ ] Optional (Manager): a Google Slides copy of the deck can go in a NEW Drive folder "DMP Sale Decks"; never edit the owner's originals.
