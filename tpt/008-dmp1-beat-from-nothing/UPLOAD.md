# UPLOAD: Beat From Nothing, DMP1 Unit 1 (TpT 008)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `beat-from-nothing.zip`. It holds three files in a folder "Beat From Nothing - Hudson Beat":
  - `beat-from-nothing.pdf`: the teacher and student resource, 21 pages, US Letter portrait.
  - `beat-from-nothing-intro-deck.pptx`: the teacher-presented intro deck, 15 slides (16:9), speaker notes on every slide.
  - `beat-from-nothing-intro-deck.pdf`: a PDF copy of the deck, 15 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `beat-from-nothing-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside).

## 1. Title

```
Beat Making in Logic Pro | Drum Programming | High School Music Technology
```
(74 characters; the limit is 80.)

## 2. Description

```
Beat making for high school music technology: students program an original drum beat from nothing in Logic Pro, with no loops and no pre-made grooves. This 4-day drum programming unit opens my Digital Music Production 1 course; the steps are written for Logic Pro, while the music ideas carry over to GarageBand, Ableton Live and BandLab. Students name the parts of the kit, learn what a loop is, count beats and measures by ear, copy one famous drum pattern, then build, mix and present their own 16-measure beat in AABA form.

WHAT'S INCLUDED (ZIP: 21-page PDF + 15-slide intro deck as .pptx and PDF)
• How to use, unit overview and setup page with a Logic quick reference (3 pages)
• 4-day pacing guide and minute-by-minute day plans (3 pages)
• Teacher notes: what the unit reinforces, the five most common student struggles and how to fix them, variations for more support or more challenge, grading tips (2 pages)
• Student pages: Day 1 classroom post, Parts of the Drum Set worksheet, drumbeat listening grids, Famous Drum Patterns, a 2-page project sheet, key vocabulary (14 terms), submission checklist, and the /25 rubric (9 pages)
• Answer key and a worked example beat with A and B sections, an AABA map and a sample mix (2 pages)
• Teacher-presented intro deck, 15 slides with speaker notes on every slide: pop-culture hook, plain-English definition of a loop, guided listening questions, a worked example in Logic, the steps, deliverables and rubric

THE FOUR DAYS
• Day 1, Learning: name the kit, hear how loops build an intro, clap beats and count measures, map three drumbeat examples on a 16-step grid
• Day 2, Learning + first time in Logic: first pattern region, Cycle, tracks and tempo, copy one famous pattern exactly, project launch
• Day 3, Work day: build an A section, a B section with one change, arrange A A B A, mix with volume and panning, export and submit
• Day 4, Presenting: students share their beats and give specific feedback to two classmates

WHAT STUDENTS LEARN
• Kick, snare and hi-hat by name, sound and function
• Subdivision: eighth notes vs. sixteenth notes on the step grid, and why they feel different
• AABA form, heard in their own work before they define it
• A first mixing lesson: volume and panning, and why you turn things down before you turn things up

GOOD TO KNOW
• Requires Logic Pro on a Mac (Logic Pro X 10.5 or later for the Step Sequencer and pattern regions). A small MIDI keyboard is optional.
• Built for about 53-minute periods; a note shows how to stretch it to 5 days.
• For grades 9–12 beginners; no music reading needed
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); the PDF copy shows the intended look
• Songs are named by title and artist only (Billie Jean by Michael Jackson is the listening hook). Play them from your own YouTube or Spotify access. No audio, video, lyrics or album art are included.
• Every student page prints well in black and white

Logic Pro is a trademark of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Designed with the help of digital and AI tools, and checked by hand.
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json). These are the first high-school slugs in the shop; they follow the `1st-grade … 12th-grade` pattern in tpt/README.md. Run the dry run first to confirm TpT accepts them.

## 4. Subjects

Per tpt/METADATA-GUIDE.md. Already live on TpT: tpt.json holds what the owner sets by hand (the uploader cannot edit a live listing and does not run on this item again).
- Subjects: Music; Career and Technical Education; Computer Science - Technology
- Tags: High School, Project Based Learning, Technology, Back to School (replaces the weak "Autumn"; use whichever of these the Tag list offers)
- Formats: PDF (add PowerPoint or ZIP if TpT offers it, since the product includes a .pptx)

## 5. Resource type

- Unit Plans
- Projects
- PowerPoint Presentations

(`tools/tpt.js` does not set resource type; pick these by hand if TpT asks.)

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr2.1 (organizing musical ideas), MU:Cr3.1 (refining work through feedback), MU:Pr6.1 (presenting), MU:Re7.2 (analyzing what is heard). Tag only if it matches how the owner teaches it; it can be left blank.

## 7. Price

**$9.00** (paid), multiple-license price $9.00. At Basic seller rates this nets about $4.65 per sale (55% minus $0.30).

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 pages, watermarked "PREVIEW"): the 4-day pacing guide, project sheet page 1, the drumbeat listening worksheet, and the /25 rubric. "Number of pages or slides" is 36 (21 PDF pages + 15 slides).

## 9. Before you click publish

- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo or student work anywhere (gen.py --check scans every output for the school name).
- [ ] Run `node tools/tpt.js publish tpt/008-dmp1-beat-from-nothing --dry-run` first: it is the first item with high-school grade slugs and a ZIP product file.
- [ ] Optional (Manager): a Google Slides copy of the deck can go in a NEW Drive folder "DMP Sale Decks"; never edit the owner's original "Looping in Logic".
