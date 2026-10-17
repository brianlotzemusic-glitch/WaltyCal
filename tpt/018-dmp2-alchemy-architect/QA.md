# QA: TpT 018 DMP2 Alchemy Architect (round 2, rebuild of 17 Oct 2026)

QA reviewed this rebuild on 17 Oct 2026, independently of the Designer, following QA-v1.md, FACTORY.md "Teachers Pay Teachers" and tpt/METADATA-GUIDE. I did not re-compare with the owner's Drive docs. I changed no item files and wrote no release file.

## 1. Checks run
- `gen.py --check` for 018: CHECK OK.
- Shared change: `tpt/_dmp2_common/dmp2.py` `cover_square()` now reads an optional `gap` from `SQ_COVER` and wraps the cover in a flex column only if it is set; with no `gap` the markup is unchanged. `git diff` shows no other change to the file. `gen.py --check` for 016: CHECK OK. 014 and 015: only the expected "release exists / uploaded exists" lines (Manager markers, not build problems). 017: "zip copy of music-for-visual-media.pdf is stale" is that kit's own in-progress rebuild by another Designer (its files are modified in the working tree), not caused by the gap setting. I ran only --check.
- Rendered all 23 PDF pages, all 18 deck pages (contact sheets) and the 4 preview pages; viewed cover.png at full size; checked preview PNG sizes (all 2000 x 2000).

## 2. Owner's content and tutorial links page: pass
- Page 7 (Teacher notes 2 of 2) lists the owner's three resources as links/titles only, with the owner's one-line notes quoted as hers/his; the two YouTube videos are credited as from the teacher's own resource list, "a link only; the video is not included and belongs to its maker". Logic's documentation is named only. Page 8 and the credits page repeat that no video is included, copied or embedded.
- The .pptx holds only six PNG drawings (waveform, filter, envelope, LFO, track plan etc.); no media, audio or video parts.
- Rubric is the owner's /25 (5 x 1-5, Final Grade = Average of Student + Teacher = ___ / 25, page 20). Kit grading tips sit under "Suggestions from this kit, not part of my rubric".
- "What changed from the original" (page 8) is updated: it now covers the resources list and the tutorial-link treatment under wording changes / new in this kit.

## 3. Third-party, branding, wording: pass
No "word for word" or "verbatim", no Blind Brook or school branding, no student names, no audio, video, lyrics or chart data in the PDF, deck PDF, UPLOAD.md or tpt.json. Apple trademark line present. Footers "(c) 2026 Brian Lotze, Hudson Beat".

## 4. Deck: pass
18 slides, seven classes, CLASS badge on every slide, speaker notes on all 18 (248-499 characters), deck PDF is 18 pages. No overflow, clipping or typos.

## 5. Layout: pass
No overflow, clipping, empty pages or typos in any page. Page 7 is full but fits. Preview PDF has 4 watermarked pages.

## 6. Cover and previews: pass
Cover is readable with HUDSON BEAT at the top. The gap fix works (title and waveforms now closer, bottom band intact). Cosmetic only: a large empty space still sits between the HUDSON BEAT line and the waveform strip (about 250 px of 2000); not blocking.

## 7. tpt.json, ZIP, UPLOAD.md: pass
Valid JSON; price and license_price 10.00; tax_code set; 4 grades; 1 subject; 1 tag; all six files exist; pages 41 = 23 + 18. ZIP holds exactly the three listed files and each is byte-identical to the folder copy. UPLOAD.md title is 79 characters; SEO opening and disclosure line present; section 9 lists the owner questions.

## Required fixes
None.

## Notes (not blocking)
1. Owner questions in UPLOAD.md section 9 stand ("Simple view" label, the two third-party .mp4 videos and Alchemy presets not used, "reflection" in the rubric).
2. Cover empty band under HUDSON BEAT could be tightened with a smaller `gap`/top padding in a later pass.

**Verdict: APPROVED**
