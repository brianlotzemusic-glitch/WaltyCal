# QA: TpT 003 Winter Rhythm Bingo (round 1)

QA reviewed this item on 8 Oct 2026, independently of the Designer. I rendered all 40 resource pages at 60 dpi as a contact sheet. I looked at the front matter (p1–5) at 100 dpi and at bingo cards 1, 14 and 30 (p6, p19, p35) in full at 130 dpi. The calling cards (p36–38) were checked at 150 dpi, with every notation strip re-rendered at 300 dpi. I also looked at the 4 preview-PDF pages, `cover.png` and `preview-1..3.png`. I checked uniqueness with my own script (scratchpad), which imports only `gen.CARDS`/`gen.POOL`. I did not use `gen.py --check`, and I changed no item files.

## 1. Musical accuracy: pass

- **All 36 calling cards (p36–38), recounted from the printed notes.** Each one totals exactly 4 beats in 4/4:
  - #1–12: q ee q q · ee ee q r · q q h · h ee ee · ee q r ee · r q ee q · q r q ee · ee ee ee ee · h ee q · h q r · q ee ee r · ee r q q
  - #13–24: 16×4 q ee q · q 16×4 q r · 16×4 16×4 h · h 16×4 16×4 · ee 16×4 r q · q q ee 16×4 · (e+ss) q (e+ss) q · (ss+e) q (ss+e) q · (e+ss)(ss+e) h · h q (e+ss) · ee (e+ss) q r · q (ss+e) 16×4 r
  - #25–36: q. e q q · q. e ee ee · q q q. e · q. e q. e · q. e h · h q. e · h. q · h. r · q. e 16×4 q · ee r q. e · q. e (ss+e) q · q (e+ss) q. e
- **Beaming.**
  - Every group is beamed by the beat. Eighth pairs have one beam, and groups of four sixteenths have two.
  - In e+ss the secondary beam covers only the last two notes; in ss+e it covers only the first two. Both are correct.
  - The eighth after a dotted quarter takes a flag and is not beamed across the beat, which is correct.
  - No half note or dotted quarter hides beat 3: every one starts on beat 1 or 3, as p2 says.
- **Rests and dots.** All rests are the Bravura quarter-rest glyph, the right shape. The dots on dotted halves and dotted quarters sit in the space above the line, which is correct on a one-line staff.
- **Heads and stems.** Half and dotted-half heads are open, and stems go up on the right.
- **Counts and syllables.** The counts on every card match the notes, for example #20 "1 e &" and #36 "1 2 & a 3 (4) &". Syllables are marked optional.
- **Other pages.** The caller's checklist (p5) and preview-3 match the calling cards one for one. The p4 reference shows 9 values with correct beats and counts. Its example (16×4 q q. e = 4) is correct.
- **No patterns sound alike.** I computed the clapped attack points of all 36 patterns, and no two are the same, so a pattern called by clapping or on a drum is never ambiguous.

## 2. Uniqueness and card ↔ calling-card match: pass

- Independent script results:
  - The 30 pattern sets are distinct.
  - Each card has 24 patterns around a FREE centre.
  - Each pattern appears on exactly 20 cards.
  - Every card holds at least 5 patterns from each group.
  - No two cards share a winning row, column or diagonal (0 shared lines).
- I read cards 1, 14 and 30 by eye, square by square, against the deal data and the calling cards. All 72 squares match.
- Note (not an overclaim): one 4-square line through the FREE centre is a subset of a 5-square line on another card. So on one call two cards could both reach bingo, on different lines. The listing only says they can't win on "the very same line", which is true.

## 3. Age fit for grades 3–6, judged at actual print size: FAIL

The Designer's worry is justified.
- On the bingo cards the staff space is `SQ_S` = 4.72 pt (1.67 mm). That is smaller than standard printed instrumental parts (about 1.75–1.9 mm), and well below the large notation in children's method books. At 100% size:
  - A notehead is about 1.7 mm tall.
  - The augmentation dot is about 0.7 mm across.
  - The gap between the two sixteenth beams is 1.2 pt (0.4 mm).
- The details that tell the patterns apart are exactly these: a dot (#25 vs #1-type rhythms), which half of a group has the second beam (#19 e+ss vs #20 ss+e), and an open or filled head. A 3rd grader has to find them by scanning 24 squares while listening. On a school photocopier or a laminated sheet, the 0.4 mm beam gap fills in and e+ss starts to look like two eighths.
- There is room to fix it.
  - The notation uses only about 33 pt of each 104 pt cell height, so about two-thirds of every square is empty.
  - The width limit comes from `PAD` (0.75 space either side of every token, which is 6 of the 19.9 spaces in the widest pattern, `eeee`) and from the 108 pt portrait cell.
- Everything else fits the age: the language, the counts on the calling cards, the rules and the range of rhythms are right for grades 3–6. The cut-out markers (about 0.95 in) fit the 1.5 × 1.44 in squares.

## 4. Art and print: two defects

- **Art and style: pass.**
  - The art is non-denominational: snowflake, mitten, sled, hat, cocoa and skate. There are no holiday or religious images.
  - It is original line art in black plus the icy-blue accent.
  - The Hudson Beat cover stack is correct: store line, art, two-line title, subtitle and black band.
  - The page header style follows `tpt/STYLE.md`.
- **Fonts and B&W printing: pass.** All pages are US Letter, and all fonts are embedded subsets (`pdffonts`). Everything is black on white, and the only accent use (the FREE snowflake and the cover band dots) prints as mid-grey.
- **Footer text: pass on p2–35 and p40.** It reads "© 2026 Brian Lotze · Hudson Beat · For single-classroom use" plus the page number.
- **DEFECT: footer pushed off the page on the calling-card pages (p36, p37, p38).**
  - The 3×4 card grid overflows the page by about 29 pt.
  - The footer text sits at y = 781.8–793.9 pt on a 792 pt page, so its bottom is cut off by the page edge.
  - The 0.8 pt footer rule is lost under the grid's dashed bottom line, and the dashed cut line itself is only about 0.2 in from the edge.
  - Every home or school printer will clip this.
  - p39 (markers) also runs about 8 pt long: its footer ink comes to 0.26 in from the bottom edge, inside STYLE.md's 0.35 in safe zone.
- **DEFECT: doubled "PREVIEW" watermark on the TpT thumbnails.**
  - preview-1.png (all three page shots) and preview-2.png (card 1) show two offset watermarks that read as "PPRREVIEW".
  - The shots come from pages that already carry the page watermark (`render_page(..., watermark=True)` / the preview PDF), and then the `.swm` overlay is added on top.
  - Card 2 in preview-2 has only one watermark, so the difference is visible side by side.
  - These are thumbnails 2 and 3 on TpT, so buyers see them.
- **Cover: pass, with a cosmetic note.** On the cover's mini card the marker discs are translucent, and the rhythm's staff line and stems poke out on both sides of the bottom-right disc. Making the discs opaque, or blanking the square under them, would look cleaner.
- **Nothing else is clipped.** All other pages keep ink at least 0.42 in from the edges.

## 5. tpt.json and UPLOAD.md: pass

- The title is 79 characters (limit 80).
- Price and license_price are both "5.00", and tax_code is "Other Digital Goods - No Physical Media".
- Grades: 4 (3rd–6th). Subjects: 1 (Music). Tags: 1 ("Winter").
- All 6 files in `files` exist. The PNGs are 2000×2000, the PDF has 40 pages and the preview PDF has 4.
- The description is accurate, with no overclaims:
  - The page breakdown is correct: 1 + 2 + 1 + 1 + 30 + 3 + 1 + 1 = 40.
  - These claims are verified: 36 calling cards at 12 per page, 9 rhythm values, each pattern on exactly 20 cards, no shared winning line, and every pattern exactly 4 beats.
  - The listed variations match p3, and the pattern groups match the cards.
- The disclosure line "Designed with the help of digital and AI tools, and checked by hand." is the last line of the description and is also printed on p40.
- There are no songs, lyrics or brands. The standards claim (MU:Pr4.2, reading and performing rhythm in standard notation) is modest and fits. The $2.45 net figure is correct (5.00 × 55% − 0.30).
- The p40 terms and credits follow STYLE.md §6.

## Required fixes

1. **Make the bingo-card notation bigger (p6–35, then the cover mini card and the previews).**
   - Aim for a staff space of at least about 6 pt (2.1 mm), roughly 27% larger. Keep it uniform across all squares.
   - Option A: landscape card pages. A 5×5 grid about 10 in wide gives cells about 144 pt wide, which allows s ≈ 6.5 pt, and the cell height still holds about 7 spaces.
   - Option B: stay portrait. Cut `PAD` to about 0.4, cut the cell inset from 14 to about 8 pt, and narrow the side margins to about 0.4 in. That gives s ≈ 5.9–6 pt.
   - Either way:
     - Centre the notation vertically in the square.
     - Confirm that the widest patterns (`eeee`, `qbsr`, `ssh`, `hss`) keep at least about 5 pt clear of the cell lines.
     - Check that the secondary-beam gap is at least about 1.5 pt.
2. **Fit the calling-card pages (p36–38) on the page.** Shorten the 3×4 card grid (the card height or `CARD_AREA`) so the footer rule and text sit in the normal footer position (y ≈ 752 pt, as on p6). Keep the dashed cut lines at least 0.35 in from the page edge. Also pull p39 back to the normal footer position.
3. **Watermark each preview PNG only once.** Either build the page shots from un-watermarked renders and keep the `.swm` overlay, or keep the page watermark and drop the overlay. Then rebuild preview-1.png and preview-2.png.

## Optional (not blocking)

- Make the cover's marker discs opaque, or hide the rhythm under them.
- The preview PDF includes the full caller's checklist, and preview-3 shows all 36 patterns, so a buyer can see every rhythm before purchase. That is acceptable for a bingo game, but you could swap the checklist for p3 (How to Play).

**Verdict: REJECTED**
