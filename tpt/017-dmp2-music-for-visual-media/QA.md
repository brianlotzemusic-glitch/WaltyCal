# QA: Music for Visual Media (TpT 017), review of the rebuilt kit

- `gen.py --check`: CHECK OK. Folder PDF, pptx and deck PDF are byte-identical to the ZIP copies; tpt.json pages match.
- Reflection page (written or oral, 4 prompts, teacher box) uses the owner's definition; teacher notes, pacing, What changed and the closing slide (Class 7) all say the kit added it because the rubric mentions reflection but the sheet has no task; adds no points. The /25 rubric is untouched (5 x 1-5).
- Rendered and viewed pacing, teacher notes 1-2, What changed, Reflection and closing slide: no overflow, clipping, empty pages or typos. Shrunk text is still readable. No school or Blind Brook branding, student names, "word for word"/"verbatim" or commercial media found.
- UPLOAD.md title within 80 characters.
- tpt.json pages 44 = 26 + 18. Videos page (page 5) layout is clean and names both videos with sizes as not in the ZIP.
- **Unauthorized promise present:** Videos page section "Where to get them" says "Ask for the download link in the Q&A tab ..." (gen.py line ~686). The What changed page (gen.py line 188) also says "and where to get them", and UPLOAD.md section 9 repeats the Q&A fallback. The Videos page also says the videos "go with this unit".
- Missing: UPLOAD.md has no note that this is a re-upload replacing the LIVE version (the old file stays on TpT until the owner replaces it).

Required fixes:
1. Remove the "Where to get them" section from the Videos page (or reword to state only what the videos are and that they are not included in this download); make no promise to buyers. Also drop "and where to get them" from the What changed page and the Q&A wording in UPLOAD.md, and reword "go with this unit". Rebuild, rerun gen.py --check.
2. Add the re-upload note to UPLOAD.md (kit is LIVE as its previous version).

**Verdict: REJECTED**
