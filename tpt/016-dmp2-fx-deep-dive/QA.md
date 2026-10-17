# QA: TpT 016 DMP2 FX Deep Dive (round 2, rebuilt kit)

Reviewed 17 Oct 2026 by QA, independent of the Designer. Item files were not changed. This round supersedes the stale approval in QA-v1.md. Scope: the rebuild with the owner's 11-FX list (page 14, FX notes) and the owner's Plug-in Links page (page 11).

## Checks run
- `python3 gen.py --check`: **CHECK FAILED**. The only failures are in QA-v1.md, which contains three banned branding strings (the school name, its abbreviation and the LMS name; quoted from the older QA text). Every generated output passed the scan.
- Sync: working tree clean, no diff against origin/shop-factory, HEAD 37b67cc contains the final PDF, ZIP, deck, previews and cover. The three files inside fx-deep-dive.zip are byte-identical (md5) to the loose files. Page counts: PDF 23, deck PDF 18, deck pptx 18 slides, PREVIEW 4; tpt.json "pages" 41 = 23 + 18, matching UPLOAD.md.
- Rendered and looked at all 23 PDF pages, all 18 deck slides, the 4 preview pages, cover.png and preview-1..3.png (2000 x 2000). Page 11 and page 8 viewed at 80 dpi. No overflow, clipping, empty pages or typos seen. Deck: the Class badge is on every slide; speaker notes exist on all 18 slides (248-394 characters).
- No "word for word" / "verbatim" in the PDF text, deck XML, UPLOAD.md or tpt.json; no school or LMS branding, no student names in any output; no audio, video, lyrics, session files or embedded media (pdfimages and pptx show only the kit's own drawn charts). Links are titles plus addresses, as text only; no hyperlinked embeds or video.
- UPLOAD.md title is 80 characters (limit 80). tpt.json valid: price and license_price 10.00, tax code set, 4 grades, 1 subject, 1 tag, all six `files` exist, zip_contents matches the ZIP.
- Owner's rubric kept as /25 (page 20; "Final Grade = Average of Student + Teacher = ___ / 25"); the three kit grading tips on page 7 sit under "Suggestions from this kit, not part of my rubric".
- Page 8 "What changed from the original" is updated: it lists the Plug-in Links page, the 11-FX list on page 14, the page-number additions, and states the EQ Cheatsheet is by another author and is named only. Pages 7, 8, 14 and 23 and UPLOAD.md confirm the third-party EQ Cheatsheet is neither included nor reproduced; the kit's EQ guide (page 10) is original.
- Facts re-checked: delay times at 100 BPM (600/300/450/150 ms) and the compression example (-18 dB threshold, 4:1, -6 dB peak gives -15 dB, 9 dB gain reduction) are correct. Page cross-references (11, 13, 14, 15, 16, 17-19) land on the right pages.

## Required fixes
1. **gen.py --check must pass.** QA-v1.md trips the banned-string scan. Reword or remove the three strings in QA-v1.md (as was done for item 018) and rerun the check; if QA-v1.md is deleted instead, the stale-approval note goes with it.

## Recommended (not blocking on their own)
2. Page 11: the sonicbids address breaks mid-word ("instrume / nt"). Shrink it, shorten it or break it at a slash.
3. Page 7, page 8, page 23 and UPLOAD.md name the EQ Cheatsheet's individual author. Naming the person adds nothing for buyers; "another author" is enough.
4. Page 8 lists "the FX notes page" under "New in this kit" and then says the list of 11 FX comes from the owner's own materials. Say which part is new (the table layout) to avoid the contradiction.
5. UPLOAD.md section 9 still has two open owner questions (EQ Cheatsheet permission; "reflection" wording in the rubric). They do not block release.

Rendered pages are otherwise clean, so once item 1 is fixed and `gen.py --check` prints CHECK OK, this should be approved on a quick re-check of that one command.

**Verdict: REJECTED**
