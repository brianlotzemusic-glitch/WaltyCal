# QA: TpT 017 DMP2 Music for Visual Media (round 2, rebuilt v2)

QA re-reviewed the rebuild on 17 Oct 2026, independently of the Designer, following QA-v1.md, FACTORY.md "Teachers Pay Teachers" and tpt/METADATA-GUIDE.md. I changed no item files and wrote no release file.

## gen.py --check: FAILS (the only failure)
`python3 gen.py --check` prints CHECK FAILED with exactly three errors, all from the superseded QA-v1.md (the check scans every .md in the folder except QA.md): it contains the banned strings for the school name, the school's initials and the learning-platform name (they appear there as "none found" statements). The stale-ZIP error from the earlier run is gone. Same fix was needed for 018 (commit 54842a9).

## Everything else passes
- Committed files: all 13 deliverables are tracked at HEAD, working tree clean after the check. The ZIP holds the three files and each is byte-identical to the folder copy (PDF, pptx, deck PDF). tpt.json pages 42 = 24 + 18; cover and previews say 24 pages + 18 slides.
- Rendered all 24 PDF pages, 18 deck slides, 4 preview pages, cover.png and preview-1..3.png: no overflow, clipping, empty pages or typos. Page 11 "Composing to picture" is the owner's five-row table, credited as from the teacher's own materials, with a Try this in Class 1 box, a Where it connects box (slide 8, slide 11, Sync guide page 10 are correct) and Ask your students; about 15 percent blank at the foot, acceptable.
- Page 8 "What changed from the original" discloses that page 11's last sentence (about reverb buses) is left out, lists the added page numbers and shortened deck slides, and says "kept as I wrote it". No "word for word" or "verbatim" in PDF, deck, notes, UPLOAD.md or tpt.json.
- Rubric is the owner's /25 (5 x 1-5, average of student and teacher); kit tips sit under "Suggestions from this kit, not part of my rubric".
- Speaker notes on all 18 slides (271-430 characters). No school branding, student names, URLs, audio, video, lyrics or linked clips; the kit says it neither contains nor links any clip.
- tpt.json valid: $12/$12, tax code set, 4 grades, 1 subject, 1 tag, all six files exist. UPLOAD.md title 78 characters (limit 80), description and disclosure line present, open questions recorded.

## Required fix
1. Reword QA-v1.md (or otherwise remove the three banned strings) so `gen.py --check` prints CHECK OK, then re-run it. No other change needed; content and layout are approved.

## Open questions (owner, not blocking)
Pre-selected clip list for the easier variation; film scoring examples and markers tutorial not in Drive; whether the two older DMP1 Unit 5 videos may be shared as links; "reflection" wording in the rubric.

**Verdict: REJECTED**
