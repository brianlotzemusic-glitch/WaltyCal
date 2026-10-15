# QA: TpT 016 DMP2 FX Deep Dive (round 1)

QA reviewed this item on 15 Oct 2026, independently of the Designer, following the format of 014 and 015. I ran `gen.py --check` (CHECK OK). I rendered all 22 PDF pages, all 18 deck pages and the 4 preview pages at 40 dpi (contact sheets), viewed cover.png and preview-1..3.png, read page 8 as text, read all 18 speaker notes via python-pptx, and compared the content with the owner's Drive docs (read-only): FX Deep Dive Project Sheet & Rubric (1sRyXp3f...) and Teacher Notes (1QWxXqcN...). I changed no item files.

## 1. Faithful to the owner's content: pass
- Rubric is the owner's /25 (5 categories, 1-5, descriptors match Drive, "Final Grade = Average of Student + Teacher = ___ / 25" kept) on page 19; slide 16 quotes only the top descriptor per row, labelled as an excerpt. The old 2025 /20 rubric was not used.
- Overview, 4 goals, 6 vocabulary terms, 5 requirements, 7 steps, 4 tips, 7 checklist items, the 5 struggles, 2 variations, 4 resources, pacing and the notes line match Drive except for the changes on page 8.
- Page 7 "How to grade": the owner's rubric line comes first; the three tips sit under the italic label "Suggestions from this kit, not part of my rubric". Pass.
- Page 8 "What changed from the original" is present, accurate (class page for Google Classroom, page numbers, resources not included, Classes 2-5 split, rubric layout, deck shortening by slide) and has "Kept as I wrote it" and "New in this kit" sections. No "word for word" claim anywhere (grep of PDFs, pptx XML, notes, UPLOAD.md, tpt.json).
- The "11 FX" vs the video title "10 FX" mismatch is left blank for students and raised as an owner question in UPLOAD.md. Correct handling.

## 2. Third-party and branding: pass
No audio, lyrics, songs, chart data or sessions; Cambridge-MT, Native Instruments, Padlet, YouTube named by title only; Logic trademark line present. No Blind Brook, BBHS, school or Google Classroom text, and no student names, in any output. Footers read "(c) 2026 Brian Lotze, Hudson Beat".

## 3. Logic and facts: pass
Delay times at 100 BPM (quarter 600, eighth 300, dotted eighth 450, sixteenth 150 ms) are right. Compression example: threshold -18 dB, 4:1, peak -6 dB gives 12 dB over, 3 dB over after, so -15 dB, 9 dB gain reduction. Correct. The invented session has 8 tracks with balanced pans.

## 4. Pacing and deck: pass
Seven classes; each of the 18 slides is in one class slot with a visible CLASS badge; Class 5 is a working day. Speaker notes exist on all 18 slides (248-394 characters). Deck PDF is 18 pages; Hudson Beat look; Oswald and Source Sans 3 only. 22 pages + 18 slides = 40 matches tpt.json.

## 5. Layout: pass
No overflow, clipping, empty pages or typos seen in any render. Minor polish only: page 11-12 and a few student pages have spare white space, which is fine for worksheets; slides 3, 6, 12 and 13 are sparse text-only slides.

## 6. Cover and previews: pass
cover.png and preview-1..3.png are 2000 x 2000, HUDSON BEAT line, readable headline, "GRADES 9-12 / 7 CLASSES / 22 PAGES + 18 SLIDES" band, no orphaned words. Preview PDF has 4 watermarked pages.

## 7. tpt.json and UPLOAD.md: pass
Valid JSON. Price and license_price 10.00, tax_code "Other Digital Goods - No Physical Media", grades 9th-12th (4), subjects Music (1), tags Autumn (1), all six `files` exist, `zip_contents` lists the three files and each is byte-identical to the file in the folder; no audio in the ZIP. Title is exactly 80 characters (limit 80) and matches tpt.json-independent UPLOAD.md code block; "Logic Pro" is inside the first 30 characters. SEO opening follows METADATA-GUIDE; disclosure line is last in the description. UPLOAD.md says 9-12 as the guide prescribes.

## Notes (not blocking)
1. The title has zero spare characters; any edit must trim elsewhere.
2. Extra subjects/tags remain listed as candidates until proven by a dry run.
3. Owner questions in UPLOAD.md section 9 (which 11 FX; EQ Cheatsheet and Plug-in Links not in Drive; "reflection" wording in the rubric) do not block release.

**Verdict: APPROVED**
