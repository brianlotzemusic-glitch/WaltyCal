# QA: TpT 017 DMP2 Music for Visual Media (round 1)

QA reviewed this item on 16 Oct 2026, independently of the Designer, following the format of 015 and 016. I ran `gen.py --check` (CHECK OK). I rendered all 23 PDF pages, all 18 deck pages and the 4 preview pages at 40 dpi (contact sheets), viewed cover.png and preview-1..3.png, read all 18 speaker notes via python-pptx, and grepped the PDF text, pptx XML and UPLOAD.md. I did not re-compare with the owner's Drive docs this round (I relied on the Designer's gen.py checks of the owner's lists and on the page 7-8 disclosures). I changed no item files.

## 1. Faithful to the owner's content: pass
- Rubric is the owner's /25 (5 categories, 1-5, "Final Grade = Average of Student + Teacher = ___ / 25") on page 20; slide 16 shows only the top descriptor per row.
- Page 7 "How to grade": the owner's rubric line comes first; the grading tips sit under "Suggestions from this kit, not part of my rubric". Pass.
- Page 8 "What changed from the original" is present, with Wording changes, "Kept as I wrote it" and "New in this kit". No "word for word" or "verbatim" anywhere (PDFs, pptx text, notes, UPLOAD.md, tpt.json).

## 2. Third-party and branding: pass
No audio, video, lyrics, songs, chart data or linked clips; the kit says it neither contains nor links any clip and tells teachers to check the site's terms. YouTube/Vimeo/Padlet named as examples only; Logic trademark line present. No Blind Brook, BBHS, school or Google Classroom text, no student names, no URLs (the only "http" strings in the pptx are XML namespaces). Footers: "(c) 2026 Brian Lotze, Hudson Beat".

## 3. Logic and facts: pass
Bar math checks out (120 BPM = 2 s a bar, 100 BPM = 2.4 s; hit 17.5 s = bar 9 beat 4 = 00:00:17:12 at 24 fps; 90 s scene = 45 bars), as does the worked example. Invented scene only.

## 4. Pacing and deck: pass
Seven classes; each of the 18 slides sits in one class slot with a visible CLASS badge. Speaker notes on all 18 slides (271-430 characters). Deck PDF is 18 pages. Hudson Beat look; Oswald and Source Sans 3 only.

## 5. Layout: pass
No overflow, clipping, empty pages or typos seen in any render. Some deck slides (3, 12, 13, 17) are sparse text-only, and a few student pages have spare space: acceptable.

## 6. Cover and previews: pass
cover.png and preview-1..3.png are 2000 x 2000, HUDSON BEAT line, readable headline, band "GRADES 9-12 / 7 CLASSES / 23 PAGES + 18 SLIDES". Preview PDF has 4 watermarked pages. Cosmetic: preview-1 shows pages cropped at the edges by design.

## 7. tpt.json and UPLOAD.md: pass
Valid JSON. price and license_price 12.00, tax_code "Other Digital Goods - No Physical Media", grades 9th-12th (4), subjects Music (1), tags Autumn (1), all six `files` exist, `pages` 41 = 23 + 18. ZIP holds exactly the three files in `zip_contents`; the PDF inside is byte-identical to the folder copy; no audio or video. UPLOAD.md title is 78 characters (limit 80), "Film Scoring in Logic Pro" leads; SEO opening and disclosure line present; says 9-12.

## Notes (not blocking)
1. Owner questions in the Designer's log entry (clip rights approach, 4 Sep vs June project menu wording, "reflection" in the rubric, film scoring examples and markers tutorial not in Drive) do not block release.
2. Extra subjects/tags remain candidates until proven by a dry run.

**Verdict: APPROVED**
