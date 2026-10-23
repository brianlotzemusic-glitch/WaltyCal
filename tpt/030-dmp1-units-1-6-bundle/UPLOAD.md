# UPLOAD: DMP1 Units 1-6 Bundle (TpT 030)

Fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This is a **fallback ZIP bundle** sold as an ordinary Digital Download. **A native TpT "Bundle of Resources" is a later upgrade**: tools/tpt.js cannot start one (its picker option has no URL, `tpt/DISCOVER-REPORT.md`; FORM-FIELDS.json only has the single-item "Bundle Discount Price" box) and the bundle form has never been recorded. Once `discover` records it, the owner may swap this for a native bundle of the six live listings. The six kit listings are not touched, re-uploaded or changed.

**Files to attach**
- Resource (digital download): `dmp1-units-1-6-bundle.zip` (6.3 MB, 19 files, folder "DMP1 Units 1-6 Bundle - Hudson Beat"): `00 START HERE - Bundle Guide.pdf` (4 pages, built here) plus one folder per unit, each holding that kit's PDF, intro deck (.pptx) and deck PDF, copied unchanged from tpt/008-013 (`gen.py --check` proves them byte-identical by SHA-256).
- Thumbnails, in order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 x 2000).
- Preview file: `dmp1-units-1-6-bundle-PREVIEW.pdf`, 4 watermarked pages (guide: unit order and pacing, folder map; two real unit pages).
- ZIP folder order: Unit 1 Beat From Nothing (008), Unit 2 Stems and Grooves (013), Unit 3 Chords by Ear (011), Unit 4 Bass and Melody Writing (012), Unit 5 Song Form (010), Unit 6 Spooky Tunes (009).

## 1. Title

```
Digital Music Production Bundle | Logic Pro Units 1-6 | High School Music Tech
```
(78 characters; the limit is 80.)

## 2. Description

```
Digital Music Production 1 for high school music technology: six complete Logic Pro units in one bundle, from programming a first drum beat to scoring a short video. Every unit has a teacher PDF (day plans, teacher notes, student pages, rubric, answer key) and a teacher-presented intro deck with speaker notes. The steps are written for Logic Pro; the music ideas carry over to GarageBand, Ableton Live and BandLab.

THE SIX UNITS, IN ORDER (29 class periods in all)
• Unit 1, Beat From Nothing (4 days): an original 16-measure drum beat in AABA form, programmed from nothing
• Unit 2, Stems and Grooves (6 days): drums over a stem, two contrasting grooves, then a full song with a transition at each section change
• Unit 3, Chords by Ear (5 days): hear chords first, then build major and minor chords, label them with Roman numerals and lay a chord layer over a bassline
• Unit 4, Bass and Melody Writing (4 days): a short melody from a scale, then a bassline over four chosen chords
• Unit 5, Song Form (4 days): arrange chords, bass and melody into a song with at least four sections
• Unit 6, Spooky Tunes (6 days): score a one-minute video with 32 measures of atmosphere, with reverb and delay on shared buses

WHAT'S INCLUDED (one ZIP, one folder per unit)
• A 4-page start-here guide: unit order, a day-by-day pacing table for all 29 periods, why the units run in this order, a folder map and what you supply
• 172 pages of teacher and student PDFs across the six units: how-to-use and setup pages, pacing and minute-by-minute day plans, teacher notes, student pages, /25 or /15 rubrics, answer keys and worked examples
• 113 slides of teacher-presented intro decks (.pptx plus a PDF copy of each), with speaker notes on every slide
• The same files as the six individual Hudson Beat units, in one download

GOOD TO KNOW
• Requires Logic Pro on a Mac. No audio, video, stems or Logic sessions are included; the units' setup pages show how to make or find the one or two files a unit needs (stems for Unit 2, a short bassline file for Units 3 and 4, a one-minute video for Unit 6).
• Built for about 53-minute periods, grades 9-12; no music reading needed.
• Units 2, 4 and 5 build on earlier units (see the guide); Unit 6 can be taught on its own.
• The decks use the free Oswald and Source Sans 3 fonts; the PDF copies show the intended look.
• Songs are named in some units by title and artist for reference only; play them from your own streaming access.
• Every student page prints well in black and white.
• If you already own some of these units, they are the same files as the individual listings.

Logic Pro is a trademark of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.

Designed with the help of digital and AI tools, and checked by hand.
```

## 3. Grades

9th, 10th, 11th, 12th (as kit 008).

## 4. Subjects, tags, formats

Same as kit 008 (tpt/METADATA-GUIDE.md): Subjects Music; Career and Technical Education; Computer Science - Technology. Tags High School, Project Based Learning, Technology, Back to School (use what the Tag list offers; consider Halloween only if offered, since Unit 6 is the Halloween unit). Formats PDF (add PowerPoint or ZIP if offered). Resource types by hand: Unit Plans, Projects, PowerPoint Presentations.

## 5. Price (arithmetic)

Sum of the six kit prices: Unit 1 $9 + Unit 2 $10 + Unit 3 $12 + Unit 4 $10 + Unit 5 $10 + Unit 6 $12 = **$63**.
Bundle price **$49.00**: $14 off, 22.2% (target 20-25%; $63 x 0.78 = $49.14, rounded down to a whole dollar). Multiple-license price $49.00 (same as the kits, where it equals the price). Net per sale at Basic seller rates about $26.65 (55% minus $0.30).

## 6. Free preview and pages

Paid. Preview PDF 4 pages. "Number of pages or slides": 289 (4 guide + 172 PDF pages + 113 slides).

## 7. Before you click publish

- [ ] Run `node tools/tpt.js publish tpt/030-dmp1-units-1-6-bundle --dry-run` on the Mac first; the ZIP is the largest product file so far but far under TpT's 4 GB limit; preview 30 MB limit and 4 MB thumbnails are met.
- [ ] Optional: delist/keep the six individual listings as they are (this bundle does not change them). Check that the six are live first, since the bundle is only useful when buyers can compare.
- [ ] Release: no `release` file was written; the Manager releases after QA.
