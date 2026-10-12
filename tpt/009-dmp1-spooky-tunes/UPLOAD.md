# UPLOAD: Spooky Tunes, DMP1 Unit 6 (TpT 009)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `spooky-tunes.zip`. It holds three files in a folder "Spooky Tunes - Hudson Beat":
  - `spooky-tunes.pdf`: the teacher and student resource, 31 pages, US Letter portrait.
  - `spooky-tunes-intro-deck.pptx`: the teacher-presented intro deck, 16 slides (16:9), speaker notes on every slide.
  - `spooky-tunes-intro-deck.pdf`: a PDF copy of the deck, 16 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `spooky-tunes-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). No video or audio is in the ZIP: the teacher supplies the video (the product says so in the description, on page 2 and on the setup page).

## 1. Title

```
Film Scoring in Logic Pro | Halloween Music Production Project | High School
```
(76 characters; the limit is 80.)

## 2. Description

```
Film scoring for high school music production: students score a one-minute video of a walk through the woods at night in Logic Pro, with 32 measures of atmosphere and reverb and delay on shared buses. No key, chord progression or song form is required: students work in any key, or none. This 6-day scoring-to-picture project is a Halloween favorite and works any time you teach music for media; the steps are written for Logic Pro, while the ideas carry over to GarageBand, Ableton Live and BandLab. It is the first open-ended project in my Digital Music Production 1 course, now cleaned up and ready for your classroom.

WHAT'S INCLUDED (ZIP: 31-page PDF + 16-slide intro deck as .pptx and PDF)
• How to use, unit overview, setup page and a one-page Logic quick reference (4 pages)
• 6-day pacing guide and minute-by-minute day plans (4 pages)
• Teacher notes: what the unit does, six common student struggles and how to fix them, a scripted 8-step bus demo, variations and grading tips (4 pages)
• Student pages: Day 1 classroom post, a 4-page project sheet with reflection, a 4-page How to Bus guide (reverb bus, delay bus, troubleshooting, atmosphere ideas), an optional Minor Key Map and minor key reference card (8 keys), cue sheet with tempo math, key vocabulary (14 terms), submission checklist and the /25 rubric (15 pages)
• Answer key and a worked 32-measure example score with send levels (2 pages)
• Teacher-presented intro deck, 16 slides with speaker notes on every slide: pop-culture hook, guided listening questions, plain-English definitions of reverb, delay and a bus, the reverb and delay bus built step by step in Logic, minor keys as an option, a worked score, the steps, deliverables and rubric

THE SIX DAYS
• Day 1, Learning: watch the video, the intro deck, a teacher bus demo, every student builds a working reverb bus
• Day 2, Work: delay bus, collect at least 5 sounds (Logic library, a microphone recording, a free download), map the video's moments
• Day 3, Work: import the video, place markers, experiment with sends, score the first half
• Day 4, Work: score the whole video so the big moments land; rough mix
• Day 5, Finish: final mix, written reflection, export and submit, early presentations
• Day 6, Presenting: students play their score with the video and explain one sound

WHAT STUDENTS LEARN
• What a bus, aux channel and send are, and why one shared reverb beats ten separate ones
• Dry vs. wet signal: near sounds dry, far sounds wet, and how that creates depth
• Optional: the minor scale and its first chord, and half steps, for students who want a darker sound
• Scoring to picture: marking moments, silence as a tool, building and releasing tension

GOOD TO KNOW
• No video is included. You supply a one-minute clip: your own phone footage of a dark trail or hallway, or a free royalty-free stock clip. The setup page explains both options.
• Requires Logic Pro on a Mac (Space Designer and Tape Delay are built in). A microphone (USB mic or audio interface) is needed for one recording; a MIDI keyboard with a pitch-bend wheel is optional.
• Built for about 53-minute periods, grades 9–12; no music reading needed; no key is required (atonal and sound-effect scores are welcome), and the optional Minor Key Map teaches minor keys to students who want one
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); the PDF copy shows the intended look
• Songs are named by title and artist only (the Halloween theme by John Carpenter and the Stranger Things theme by Kyle Dixon & Michael Stein). Play them from your own YouTube or Spotify access. No audio, video, lyrics or album art are included.
• Every student page prints well in black and white

Logic Pro is a trademark of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Designed with the help of digital and AI tools, and checked by hand.
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), the same slugs as item 008.

## 4. Subjects

Per tpt/METADATA-GUIDE.md. `tpt.json` keeps only values TpT has accepted so far, so the nightly upload cannot fail on an unknown option.
- Subjects in tpt.json: Music. After the dry run, add by hand (or into tpt.json if accepted): Career and Technical Education; Computer Science - Technology
- Tags in tpt.json: Halloween, Autumn. After the dry run, add High School, Project Based Learning, Technology if the Tag list offers them (max 6) and drop Autumn
- Formats: PDF (add PowerPoint or ZIP if TpT offers it, since the product includes a .pptx)

## 5. Resource type

- Unit Plans
- Projects
- PowerPoint Presentations

(`tools/tpt.js` does not set resource type; pick these by hand if TpT asks.)

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1 (generating ideas), MU:Cr2.1 (developing and organizing), MU:Cr3.1 (refining through feedback), MU:Pr6.1 (presenting), MU:Cn11.0 (connecting music to other media). Tag only if it matches how the owner teaches it; it can be left blank.

## 7. Price

**$12.00** (paid), multiple-license price $12.00. At Basic seller rates this nets about $6.30 per sale (55% minus $0.30).

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 pages, watermarked "PREVIEW"): the 6-day pacing guide, project sheet page 2 (requirements and sound sources), How to Bus Part 1 (the reverb bus) and the /25 rubric. "Number of pages or slides" is 47 (31 PDF pages + 16 slides).

## 9. Before you click publish

- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student work or the owner's classroom video anywhere (gen.py --check scans every output and every file in this folder).
- [ ] Run `node tools/tpt.js publish tpt/009-dmp1-spooky-tunes --dry-run` first if 008's high-school slugs or ZIP upload are still unproven (008's first run was interrupted).
- [ ] Halloween timing: this is the most seasonal DMP unit; publish before the end of October if possible.
- [ ] Optional (Manager): a Google Slides copy of the deck can go in a NEW Drive folder "DMP Sale Decks"; never edit the owner's originals.
