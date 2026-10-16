# QA: TpT 018 DMP2 Alchemy Architect (round 1)

QA reviewed this item on 16 Oct 2026, independently of the Designer, following the format of 016 and 017. I ran `gen.py --check` (CHECK OK). I rendered all 23 PDF pages, all 18 deck pages and the 4 preview pages as contact sheets, viewed cover.png and preview-1..3.png at full size, read all 18 speaker notes via python-pptx, and grepped the PDF text and UPLOAD.md/tpt.json. I did not re-compare with the owner's Drive docs. I changed no item files.

## 1. Faithful to the owner's content: pass
- Rubric is the owner's /25 (5 categories, 1-5, "Final Grade = Average of Student + Teacher = ___ / 25") on page 20; slide 16 shows only the top descriptor per row.
- Grading tips sit under "Suggestions from this kit, not part of my rubric" (page 7). Pass.
- Page 8 "What changed from the original" present (Wording changes, Kept as I wrote it, New in this kit). No "word for word" or "verbatim" in the PDF, UPLOAD.md or tpt.json.

## 2. Third-party and branding: pass
No audio, video, lyrics, songs or chart data. YouTube appears only in the owner's resource list, marked "not included"; no links. Logic/Alchemy trademark line present. No Blind Brook or school text, no student names. Footers "(c) 2026 Brian Lotze, Hudson Beat".

## 3. Logic and facts: pass
Harmonics math (110 Hz saw under a 1000 Hz cutoff keeps 9; 55 Hz sub with 400 Hz keeps 7), 0.5 Hz LFO = one cycle per 2 s bar at 120 BPM, 26 bars = 52 s (inside 45-60 s), quarter-note delay 500 ms all check out. Invented patches only.

## 4. Deck: pass
18 slides, seven classes, CLASS badge on slides 2-18 (title slide is Class 1 by the check). Speaker notes on all 18 (248-499 characters). Deck PDF is 18 pages. Waveform, filter, envelope, LFO and track-plan drawings render cleanly.

## 5. Layout: pass
No overflow, clipping, empty pages or typos seen in any render. Several student pages and slides 3, 12, 14 have spare space: acceptable.

## 6. Cover and previews: pass
cover.png and preview-1..3.png are 2000 x 2000, HUDSON BEAT line, readable. Cosmetic only: the cover has a large empty gap between the waveform strip and the title. Preview PDF has 4 watermarked pages (pages cropped by design).

## 7. tpt.json and UPLOAD.md: pass
Valid JSON; price and license_price 10.00; tax_code "Other Digital Goods - No Physical Media"; grades 9th-12th (4); subjects Music (1); tags Autumn (1); all six files exist; pages 41 = 23 + 18. ZIP holds exactly the three listed files; its PDF is byte-identical to the folder copy. UPLOAD.md title is 79 characters (limit 80), SEO opening and disclosure line present.

## Notes (not blocking)
1. Owner questions in UPLOAD.md section 9 (Simple view label, tutorial links, 4 Sep vs June menu wording, "reflection" in the rubric, older rubric unused) do not block release.
2. Extra subjects and tags remain candidates until proven by a dry run.

**Verdict: APPROVED**
