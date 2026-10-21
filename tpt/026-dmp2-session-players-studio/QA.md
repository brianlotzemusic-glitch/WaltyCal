# QA: Session Player's Studio (TpT 026, DMP2, $10), 21 Oct 2026

Reviewer did not build this. Branch shop-factory, working tree clean at start; `gen.py --check` prints CHECK OK.

## Checks
- **Render review (low-res contact sheets, 30 dpi pages / 25 dpi slides):** all 25 PDF pages and all 19 slides, plus the cover. No overflow, clipping, empty pages or layout defects seen. US Letter; deck 16:9 (960 x 540 pt), 19 pages. Fonts Oswald and Source Sans 3, all embedded (pdffonts). Preview PDF is 4 pages (pacing, worked example, chord cheat sheet, rubric; watermark div present in source). Cover is 2000 x 2000, HUDSON BEAT store line, big title readable at thumbnail size.
- **Drive verification (read-only):** Projects (New) "Session Player's Studio - Project Sheet & Rubric" and "Teacher Notes" compared with the PDF/deck. Overview, 4 goals, 5 vocabulary terms, 5 requirements, 7 steps (incl. Padlet step 7), 4 tips, 6 checklist items, 4 struggles, Easier/More Advanced variations, 3 resources and the 7-class pacing guide match. Rubric: 5 categories x 1-5 = /25; all cell texts match the sheet (spot-checked every row in the rendered HTML); average of student and teacher kept. The 2025 Project Outline is not used (only the June 2026 menu line is quoted).
- **Reflection handling: correct.** The sheet has no reflection task (checklist, requirements and steps contain none), but the rubric's Documentation & Presentation row mentions reflection at levels 1, 3 and 4. So the shared Reflection page is rightly ON: it is labelled "added by this kit", adds no points and no rubric row, and the rubric is untouched. Deck slide 19 points to it modestly. This differs from 025, where the sheet had its own reflection paragraph and the page was off.
- **Disclosed changes (page 8 "What changed"):** LMS name written "your class page"; tip 2 "a search engine or an AI chatbot" (Google/ChatGPT removed); YouTube resources kept untitled, unlinked. Invented additions ("Porch Light" 24 bars at 96 BPM = 60 s with a chord for every bar, chord cheat sheet in five keys computed from scales, Players/Arrangement/Melody/Mix sheets, Logic quick reference, drawings, grading tips) are labelled; none adds a requirement or rubric row. Cheat sheet content is music-theory correct (I-V-vi-IV etc. in C, G, D, F, A).
- **Third-party names:** greps of PDF text, deck text/notes and UPLOAD.md find no artist, album or song names, no Blind Brook or school branding, no links, no email. Only Logic Pro/Apple, GarageBand (UPLOAD.md compatibility line), Padlet (owner's own step), YouTube (as where the teacher finds videos), Google Fonts/Slides (font note). Compatibility use only. Disclosure line present.
- **No audio/video:** none in the ZIP or folder; PDF says so.
- **tpt.json:** price and license_price $10.00; tax_code set; 4 grades (9th-12th); 1 subject (Music); 1 tag (Autumn, proven value); formats PDF; pages 44 = 25 + 19; every file in `files` exists. Deck: 19 slides, speaker notes on 19/19 (python-pptx).
- **ZIP:** exactly the 3 files in `zip_contents`, each byte-identical (cmp) to the folder copy, 1.15 MB.
- **UPLOAD.md:** title 73 chars (<= 80); follows form order; description has the disclosure line and no brand claims beyond compatibility; price $10 with rationale; owner questions listed.

Minor, not blocking: UPLOAD.md and the pacing page put "3 Padlet questions" in Class 6, which the owner's pacing line ("Final mix, bounce. Prepare presentations.") does not state; it is consistent with step 7 and labelled as the kit's pacing note.

Open owner questions (do not block): own chord cheat sheet (not in Projects (New)); exact titles/links of the two YouTube videos; whether to name ChatGPT/Google in tip 2; which Logic version the class uses; Harder variation's live-recorded element is a planning page only.

Required fixes: none.

**Verdict: APPROVED**
