# UPLOAD: Song Form, DMP1 Unit 5 (TpT 010)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `song-form.zip`. It holds three files in a folder "Song Form - Hudson Beat":
  - `song-form.pdf`: the teacher and student resource, 27 pages, US Letter portrait.
  - `song-form-intro-deck.pptx`: the teacher-presented intro deck, 17 slides (16:9), speaker notes and a Day badge on every slide.
  - `song-form-intro-deck.pdf`: a PDF copy of the deck, 17 pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `song-form-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). No audio or video is in the ZIP: songs are named by title and artist only.

## 1. Title

```
Song Structure in Logic Pro | Pop Song Form Unit | High School Music Technology
```
(79 characters; the limit is 80.)

## 2. Description

```
Song structure for high school music technology: students map the verse, chorus and bridge of real pop songs on a song form sheet, then arrange their own chords, bass and melody into a song with at least four sections in Logic Pro. This 4-day song form and arrangement unit is Unit 5 of my Digital Music Production 1 course; the steps are written for Logic Pro, while the ideas (verse chorus bridge form, texture, transitions, arrangement as mix) carry over to GarageBand, Ableton Live and BandLab.

WHAT'S INCLUDED (ZIP: 27-page PDF + 17-slide intro deck as .pptx and PDF)
• How to use, unit overview, setup page and a one-page Logic quick reference (4 pages)
• 4-day pacing guide and minute-by-minute day plans, with the deck slides for each block (3 pages)
• Teacher notes: the big idea, how to run the class listening analysis, suggested songs and why each works, the 5-minute chord layer demo, callbacks, common student struggles, variations and grading tips (4 pages)
• Student pages: Day 1 classroom post, a 4-page project sheet with the planning table, three Song Form sheets (six songs, two as a class and two of four by choice), a Compare the Forms page with the written response, key vocabulary (10 terms), submission checklist and the /25 rubric (12 pages)
• Answer key with form maps for all six songs (section names and measure counts) and a worked 32-measure skeleton with a filled-in planning table (2 pages)
• Teacher-presented intro deck, 17 slides with speaker notes on every slide: a pop-culture hook, a plain-English definition of song form, guided listening questions, what each section does, the chord layer in Logic, a worked 32-measure skeleton, the four transitions, the steps, deliverables and rubric

THE FOUR DAYS
• Day 1, Listening: two songs as a class (feel the change, label the sections, count the measures), two songs on their own, then a share-out and a written response
• Day 2, Plan and build: chord layer demo, the planning table on paper first, add the melody, build the skeleton with arrangement markers
• Day 3, Differentiate: chord layer, melody only where it belongs, a drum transition at every section change
• Day 4, Finish and present: final mix, export and submit, then every student points to their chorus and explains why it feels bigger

WHAT STUDENTS LEARN
• Intro, verse, pre-chorus, chorus, bridge and outro, and the job each one does
• Sections are almost always 4 or 8 bars, and the chorus is fuller than the verse
• Texture and arrangement: sections feel different because of what is playing, not because of a label
• Transitions (fill, breakdown, cut, build) and arrangement as mix

GOOD TO KNOW
• Requires Logic Pro on a Mac. Students arrange a short chord progression and bassline they already have; if they have none, the setup page shows a quick way to make one (the worked example uses I–V–vi–IV in C)
• Built for about 53-minute periods, grades 9–12; no music reading needed. Runs in 3 days if you are short on time (the pacing page explains how)
• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present the PDF copy, which shows the intended look
• Songs are named by title and artist only (Crazy, Blinding Lights, Anti-Hero, good 4 u, Levitating, Uptown Funk). Play them from your own YouTube or Spotify access. No audio, video, lyrics or album art are included; the answer key lists only section names and measure counts.
• Every student page prints well in black and white

Logic Pro is a trademark of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Designed with the help of digital and AI tools, and checked by hand.
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), the same slugs as items 008 and 009.

## 4. Subjects

Per tpt/METADATA-GUIDE.md. `tpt.json` keeps only values TpT has accepted so far, so the nightly upload cannot fail on an unknown option.
- Subjects in tpt.json: Music. After the dry run, add by hand (or into tpt.json if accepted): Career and Technical Education; Computer Science - Technology
- Tags in tpt.json: Autumn (proven on 002 and 004; this unit is taught in November). After the dry run, add High School, Project Based Learning, Technology and Creativity if the Tag list offers them (max 6), and drop Autumn once they are accepted
- Formats: PDF (add PowerPoint or ZIP if TpT offers it, since the product includes a .pptx)

## 5. Resource type

- Unit Plans
- Projects
- PowerPoint Presentations

(`tools/tpt.js` does not set resource type; pick these by hand if TpT asks.)

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Re7.2 (analyzing structure), MU:Cr2.1 (organizing and developing ideas), MU:Cr3.1 (refining), MU:Pr6.1 (presenting). Tag only if it matches how the owner teaches it; it can be left blank.

## 7. Price

**$10.00** (paid), multiple-license price $10.00. At Basic seller rates this nets about $5.20 per sale (55% minus $0.30).

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 pages, watermarked "PREVIEW"): the 4-day pacing guide, the planning table, the class Song Form sheet (songs 1 and 2) and the /25 rubric. "Number of pages or slides" is 44 (27 pages + 17 slides).

## 9. Before you click publish

- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student work or audio anywhere (gen.py --check scans every output and every file in this folder).
- [ ] Owner questions in the Designer's report answered (unit number, 3 vs 4 days, the 32-measure skeleton, the "Uptown Funk" artist credit, the "Bridge/Chorus?" label).
- [ ] Optional (Manager): a Google Slides copy of the deck can go in a NEW Drive folder "DMP Sale Decks"; never edit the owner's originals.
