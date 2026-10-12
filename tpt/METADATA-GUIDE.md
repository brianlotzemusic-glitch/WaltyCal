# TpT metadata guide for DMP (Digital Music Production) products

Goal: high-school music production / music technology teachers find Hudson Beat DMP products. Written 12 Oct 2026. Search patterns come from TpT and other sites' public search pages (teachers search "music production", "beat making", "GarageBand project", "BandLab", "Ableton", "film score project", "music technology"); no seller text is copied.

## (a) Fields and best values
TpT's form (tpt/FORM-FIELDS.json) has: Grade (up to 4), Subject Area (up to 3), Tag (Theme/Audience/Language, up to 6), Format (up to 3), Custom Category, Standards pickers, pages, answer key, duration. Subject Area and Tag are react-select lists of **approved terms only**: the repo has proven only these exact texts: Subject "Music"; Tags "Halloween", "Autumn", "Winter", "Thanksgiving"; Format "PDF". The option lists themselves are not in the repo, and TpT states Subject/Tag use an approved list. Resource Type is not in the form's discovered fields (the uploader can't set it).
- **Grades:** 9th, 10th, 11th, 12th (4 is the limit). Do not add 8th.
- **Subjects (best 3, in order):** 1) Music (proven). 2) Career and Technical Education (TpT lists it under "Specialty"). 3) Computer Science - Technology (or whichever "technology" option the dropdown shows). Type each in the dropdown; if it is absent, use "Instrumental Music"/"Music Composition" if offered, else leave Music alone.
- **Tags (max 6; real tags only, no free text):** type these in the Tag box in order and keep what TpT offers: High School, Project Based Learning, Technology, Back to School (units 1-2), Halloween (Spooky Tunes only), Careers/Career Exploration, Creativity. Drop seasonal tags that do not fit (Autumn is weak for a year-round course).
- **Resource type (by hand):** Unit Plans, Projects, PowerPoint Presentations (the ZIP holds a .pptx). **Formats:** PDF, plus PowerPoint/ZIP if offered. **Standards:** optional NCAS Music Tech codes in UPLOAD.md.
- **Uploader rule:** `tools/tpt.js` fails a value not in the list. Keep tpt.json to values a dry run accepted. Run `--dry-run` on the owner's Mac: for each rejected value it prints what TpT offers when you type it; copy those into tpt.json.

## (b) Title and description formula
**Title (<=80 chars):** `[Search phrase] in Logic Pro | [Unit topic] | High School Music Technology` Lead with the phrase teachers type: Beat Making, Drum Programming, Film Scoring, Music Production, Sound Design. Put "Logic Pro" in the first 30 chars (few listings name it). Skip the brand, the course number and season words in the title unless the season is the hook.

**Description, first 2 lines** (these show in search results): line 1 = search phrase + audience + what students make ("Beat making for high school music technology: students ... in Logic Pro"). Line 2 = course tie-in and compatibility. Then the existing WHAT'S INCLUDED / DAYS / LEARN / GOOD TO KNOW blocks.

**DAW wording (true to the content):** the click-by-click steps are Logic Pro only (Step Sequencer, Cycle, Space Designer, buses). Say: "Steps are written for Logic Pro; the music concepts (...) transfer to GarageBand, Ableton Live and BandLab." Never say "works in any DAW". Name those DAWs only in the description and tags, not as a compatibility promise in the title. Keep the Apple trademark line.

## (c) Keyword bank (use 2-4 per listing in the title, first 2 lines and Good to Know)
- DMP1 U1 Beat From Nothing: beat making, drum programming, step sequencer, drum machine, kick snare hi-hat, tempo, 16-step grid, AABA, volume and panning.
- U2 Stems & Grooves: drum fills, transitions, stems, gain staging, groove, bus reverb.
- U3 Chords by Ear: chord progression, I-IV-V-I, Roman numerals, ear training, major and minor.
- U4 Bass & Melody: bassline, melody writing, scale, MIDI keyboard, frequency separation.
- U5 Song Form: song structure, verse chorus bridge, pop song form, arrangement.
- U6 Spooky Tunes: film scoring, scoring to picture, minor key, reverb, delay, bus, sound design, Halloween.
- U7 Loops Unlocked: Apple Loops, looping, EQ, equalizer, arrangement, remix.
- U8 EDM: EDM, electronic music production, build and drop, automation, sidechain.
- U9 Game Audio: video game music, game audio, sound design, foley, SFX recording, compression.
- U10 Final: capstone, student-led project, portfolio, release project.
- DMP2 themes: sample flipping, sampling, synthesis, synthesizer, FX / effects, mixing, mastering, Billboard song analysis, genre study, ambient music, field recording, found sound, music for visual media, session player, royalty free music, step sequencer patterns, artist release, music business.
- Umbrella phrases for every item: music production, music technology, digital music production, DAW, Logic Pro, high school music, secondary music, general music, CTE music, music lab, project-based.

## (d) Recommended replacements
**008 Beat From Nothing (live)** (title is 74 chars)
- Title: `Beat Making in Logic Pro | Drum Programming | High School Music Technology`
- Subjects: Music; Career and Technical Education; Computer Science - Technology. Grades 9-12. Tags: High School, Project Based Learning, Technology, Back to School (replace "Autumn"). Formats: PDF (+ PowerPoint if offered).
- Lines 1-2: "Beat making for high school music technology: students program an original drum beat from nothing in Logic Pro, with no loops and no pre-made grooves. This 4-day drum programming unit opens my Digital Music Production 1 course, and the steps are written for Logic Pro while the music ideas carry over to GarageBand, Ableton Live and BandLab."

**009 Spooky Tunes (unreleased)** (title is 76 chars)
- Title: `Film Scoring in Logic Pro | Halloween Music Production Project | High School`
- Subjects: Music; Career and Technical Education; Computer Science - Technology. Grades 9-12. Tags: Halloween, High School, Project Based Learning, Technology (Autumn dropped when TpT offers the others).
- Lines 1-2: "Film scoring for high school music production: students score a one-minute video of a night walk in Logic Pro, with two minor keys and shared reverb and delay buses. This 6-day scoring-to-picture project is a Halloween favorite, and it works any time you teach music for media; the steps are written for Logic Pro while the ideas carry over to GarageBand, Ableton Live and BandLab."

## Edits to make on TpT by hand (008, live)
`tools/tpt.js` only has login, discover, publish (create) and publish-pending; it **cannot edit an existing listing**, and `publish` refuses an item with an `uploaded` file. So edit 008 by hand: My Products > Beat From Nothing > Edit.
1. Title: paste the new title above.
2. Description: replace only the first paragraph with the new lines 1-2 (UPLOAD.md has the full text).
3. Subject Area: add Career and Technical Education and the technology subject (Music stays).
4. Tags: remove "Autumn"; add High School, Project Based Learning, Technology, Back to School, using whichever the dropdown offers.
5. Resource type: Unit Plans, Projects, PowerPoint Presentations. Format: add PowerPoint/ZIP if offered. Save.
(Adding an `edit` command to the uploader is possible later; ask the owner first. It must run on the Mac, not here.)

## Process
New DMP items copy this guide's title formula, first-2-lines pattern, and keyword bank. Re-check the tag and subject lists after each dry run and record accepted texts at the top of (a).
