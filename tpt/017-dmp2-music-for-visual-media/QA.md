# QA: Music for Visual Media (fix-round re-review, 17 Oct 2026)

- git pull done; gen.py --check prints CHECK OK (title within 80 chars).
- The Q&A-tab video-link promise is gone from 017 (PDF, deck, notes, UPLOAD.md, gen.py); the only Q&A-tab text left is the standard last-page line about reporting a problem. Page 5 (viewed at 100 dpi) says only what the two videos are, that they are not in this download, and that teachers can use their own copies.
- UPLOAD.md section 9 carries the re-upload note (Reflection page, for the owner's later re-upload; uploaded files untouched).
- ZIP contents byte-identical to the folder PDF, deck and deck PDF; HEAD contains the final PDF, ZIP, deck, previews and cover; working tree clean.
- No school or Blind Brello branding, student names, "word for word"/"verbatim" or commercial media found; no release files added; the `uploaded` files are unchanged since the fix round.

Required fixes: none.

**Verdict: APPROVED**

## Fix round 16 Nov 2026
Audit P2: preview-2 "Bars and seconds" 100 BPM ruler numbered only bars 1-7; the rule that skipped bars not ending inside the 18 s window is changed to number every bar that starts inside it, so bars 1-8 are numbered like the 120 BPM ruler (also in the sync guide). Deck "How it's scored" line now reads "...average of your score and mine, out of 25" (no stray dot) and sits clear of the footer rule (RUBRIC_LINE_Y 6.3, row pitch 0.84). Rebuilt; `gen.py --check` and tpt-validate pass. A fresh Sonnet inspector confirmed both fixes and found no defects.
**Verdict: APPROVED**
