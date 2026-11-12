# QA: 033 Thanksgiving Music Sub Plan K-5 (round 2)

Reviewed independently against the TPT-FACTORY.md QA checklist, after the round 1 fixes and full regeneration.

## Round 1 fixes: verified
- Page 8: the right-hand boxes in Section B (2, 4, 6) now sit inside the right margin and line up with the Section A boxes and the footer rule.
- Page 15: the five thankful bubbles are symmetric and centred. The turkey is fully visible below them and not covered.

## Checks
- `python3 gen.py --check` prints CHECK OK: 26 engraved rhythms, 18 Letter pages, fonts embedded, images 2000x2000, tpt.json and UPLOAD.md ok.
- Rendered all 18 pages at 60 dpi and looked at each one. No clipping, overlap, blank page or tiny text. Headers, footers and page numbers are consistent. Notation is clean on pages 5-8 and 16.
- Answer key (page 16) agrees with the rendered notation on the pages I re-read: K-2 claps 3/5/4/6/8/4, word matches C/A/B/C, 3-5 math 4/4/5/3/4/6, bars NO 3 / YES 4 / NO 5 / YES 4 / NO 5 / YES 4, syllables C1 ti-ti ta ta-a, C2 ta shh ta ti-ti. These were also verified in round 1.
- Cover reads at thumbnail size. Preview thumbnails 1-3 are legible and carry the Hudson Beat branding.
- Preview PDF has 4 pages (Lesson 1 plan, rhythm chart, Gratitude Verse, answer key), all watermarked. This matches UPLOAD.md section 8.
- Page count of 18 matches the cover, the description and tpt.json. Title is 75 characters. Disclosure line is in the description and on the terms page.
- tpt.json: price $4, 4 grades, subject Music, tags Thanksgiving and Autumn, all five files exist. It is consistent with UPLOAD.md.
- No songs, tunes, characters or brands. No public-domain tune is involved.

## Minor (not blocking)
- Thumbnail 2 shows a "Lessons at a glance" page that is not among the 4 preview PDF pages. It is still a real page in the product.
- Page 3: the sentence "...that you may play in class." leaves "class." alone on a line (carried over from round 1).

**Verdict: APPROVED**
