# UPLOAD: Winter Concert Planner + Program Kit (TpT 005)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `winter-concert-planner.pdf`, 20 pages, US Letter portrait.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `winter-concert-planner-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
Winter Concert Planner + Program Kit | Programs, Seating Charts, Parent Letter
```
(78 characters; the limit is 80.)

## 2. Description

```
Plan and run your winter concert from one printable file. This kit covers the whole job: an 8-week planning timeline, repertoire and rehearsal trackers, choir riser and seated-ensemble charts, a stage and tech checklist with a volunteer sign-up, a concert-day run of show, a parent letter with a return slip, reminder notes, three program layouts, eight thank-you notes and a student reflection page. It is non-denominational (snowflakes, mittens, cocoa, music stands and drums), so it works for any school.

WHAT'S INCLUDED (20 pages, PDF, US Letter)
• Teacher notes with a page guide (1 page)
• Planning timeline: 8 weeks out, 6, 4, 2, concert week, concert day and after, with checkboxes and target dates (1 page)
• Concert at a glance: date, snow date, call time, room, attire, contacts, photo policy (1 page)
• Repertoire planner: concert order, composer/arranger, group, featured students, minutes and total time (1 page)
• Rehearsal tracker: 10 pieces × 12 rehearsals, marked read-through / learning / polishing / stage-ready (1 page)
• Rehearsal plans, 2 per page (1 page)
• Riser chart for choirs: 27 staggered spots on 3 steps (1 page)
• Stage setup for band, orchestra, recorders or Orff: 27 chairs in 3 arcs (1 page)
• Stage & tech checklist + volunteer sign-up (1 page)
• Run of show for concert day (1 page)
• Parent letter with fill-in blanks and a return slip (1 page)
• Reminder notes, 2 per page (1 page)
• 3 program layouts: full page, half page (2 per sheet), and a program with a performer name list (3 pages)
• 8 thank-you note designs, 4 per page, for volunteers, staff, accompanists and families (2 pages)
• Student concert reflection (1 page)
• Terms of use and credits (1 page)

EASY TO USE
• Print and write by hand, or type onto any page with your PDF reader's add-text tool before printing
• Prints well in black and white; programs look great on colored paper
• Piece titles are left blank, so it works for choir, band, orchestra, general music and whole-school concerts
• For K–8 music teachers; the reflection page works for students of any age

All layouts, wording and art are original. No songs, lyrics or copyrighted characters.

Designed with the help of digital and AI tools, and checked by hand.
```

## 3. Grades

Not Grade Specific (`not-grade-specific` in tpt.json). It is a teacher resource for any K–8 concert, and TpT allows at most 4 grade boxes, so K–8 can't be ticked in full. The checkbox id is in `tpt/FORM-FIELDS.json` (discover run), but no earlier item has used it, so confirm it in the dry run.

## 4. Subjects

- Music
- Tags: Winter ("Winter" was accepted on item 003)

## 5. Resource type

- Printables
- Classroom Forms
- Teacher Tools / Planners (whichever TpT offers)

(`tools/tpt.js` does not set resource type; pick these by hand if TpT asks.)

## 6. Standards (optional)

National Core Arts Standards, Music: MU:Pr5.1 (refine work for presentation: the rehearsal pages) and MU:Pr6.1 (present work to an audience: the reflection page). These are a loose fit for a planner; leaving them blank is fine.

## 7. Price

**$4.50** (paid), multiple-license price $4.50. At Basic seller rates this nets about $2.18 per sale (55% minus $0.30).

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 pages, watermarked "PREVIEW"): Program A, the planning timeline, the riser chart and the first page of thank-you notes.

## 9. Before you click publish

- [ ] Cover and previews show "HUDSON BEAT" in type; footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] Run `node tools/tpt.js publish tpt/005-winter-concert-planner --dry-run` first to confirm the "Not Grade Specific" grade box. No answer key is included, so `answer_key` is left out of tpt.json.
- [ ] List by **10 Nov 2026**, before concert planning starts.
