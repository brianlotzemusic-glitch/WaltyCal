# QA: TpT 005 Winter Concert Planner + Program Kit (round 1)

QA reviewed this item on 10 Oct 2026, independently of the Designer. I rendered all 20 pages at 60 dpi as two contact sheets, the 4-page preview PDF at 40 dpi, `cover.png` and `preview-1..3.png` as a 2x2 sheet, and pages 8, 14 and 15 at 90 dpi crops. I changed no item files.

## 1. Usefulness and completeness for a K-8 music teacher: pass
- The kit covers the whole job: 8-week timeline, concert-at-a-glance, repertoire planner with minutes, a 10x12 rehearsal tracker, rehearsal plans, choir riser chart (18-27 back, 9-17 middle, 1-8 front = 27 spots), 27-chair arc chart for band/orchestra/Orff, stage and tech checklist with volunteer sign-up, run of show, parent letter with return slip, reminders, 3 program layouts, 8 thank-you notes and a student reflection.
- Page cross-references in the teacher notes and timeline (pages 3-11, 12, 13, 8-9, 5, 11, 17-18, 19) all point to the right pages. Piece titles are blank, so it works for choir, band, orchestra and general music.
- No fillable form fields (`pdfinfo` says Form: none). The description is honest about this: "print and write by hand, or type with your PDF reader's add-text tool". That is clear enough.

## 2. Wording and rights: pass
- Non-denominational: snowflakes, mittens, cocoa, stands, drum, hat. A text search for Christmas, Hanukkah, Kwanzaa, Santa, carol, jingle, Rudolph, holiday finds nothing.
- No song titles or lyrics anywhere. The only notation is a decorative 4/4 bar on programs (eighth pair, eighth pair, half = 4 beats).
- The parent letter and thank-you wording are polite and generic.

## 3. Layout, legibility, print: pass with one nit
- 20 pages, all US Letter, all fonts embedded (Oswald, Source Sans 3, Bravura). Nothing overflows or clips; footers sit consistently; cut lines are marked ("CUT HERE", "CUT ON THE DASHED LINES"). The riser and arc charts fit the margins, and the numbers in the spots are small but readable.
- Prints in black and white; the only colour is the icy-blue accent.
- Nit (not blocking): on programs A, B and C the "PIECE" and "PERFORMED BY" captions are about 4 pt light grey, and on line 1 they sit under the dotted rule. They are too faint to help a teacher. Make them about 6 pt and darker, or drop them.

## 4. Cover, previews, brand: pass
- `cover.png` and `preview-1..3.png` are 2000x2000. They have the HUDSON BEAT store line, a big caps title, a subtitle and a black band, on flat white with no border, as STYLE.md asks. The cover reads at thumbnail size and shows the product (program and checklist, stand, drum, mittens).
- The preview shots carry one PREVIEW watermark each; preview-2's parent letter is cropped by the thank-you page, which reads as a stacked look.
- The preview PDF has 4 pages (14, 3, 8, 17), matching UPLOAD.md except that it says "Program A, timeline, riser chart, first thank-you page". That is correct.
- The footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use". Terms page (p20) follows STYLE.md section 6, and the disclosure line is printed there.

## 5. tpt.json and UPLOAD.md: pass with one nit
- Title: I counted "Winter Concert Planner + Program Kit | Programs, Seating Charts, Parent Letter" = 78 characters. UPLOAD.md says 78. Correct, and under 80.
- price and license_price are both "4.50"; tax_code is "Other Digital Goods - No Physical Media"; grades 1 (not-grade-specific); subjects 1 (Music); tags 1 (Winter); all 6 `files` exist; pages 20 matches the PDF; the net $2.18 is right (4.50 x 0.55 - 0.30 = 2.175).
- The disclosure line is the last line of the description.
- Nit: the description's per-page list adds up to 19 pages and does not mention the cover, while it says "20 pages". Add "Cover (1 page)" or write "19 pages plus cover". Also tag "Winter" only; add a second tag if the dry run offers one (for example "Concert" or "Music"). Neither is blocking.
- The `not-grade-specific` grade is untested; UPLOAD.md already says to confirm in the dry run.

## Optional (not blocking)
1. Enlarge or darken the program captions (section 3).
2. Fix the page count in the description.
3. Add a second tag.

**Verdict: APPROVED**
