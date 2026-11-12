# QA: 031 Carol Flip (second-round review)

## Findings
- `python3 gen.py --check`: CHECK OK (26 Letter pages, 15 slides, 4-page watermarked preview, zip current and audio-free, UPLOAD.md and tpt.json validated).
- Page counts match reality: `pdfinfo` gives 26 pages (carol-flip.pdf), 15 (deck PDF), 4 (preview). Description now reads "26-page PDF = 1 cover + 10 teacher + 14 student + 1 terms page", with teacher (10) and student (14) parts correct (pages 2-11, 12-25). UPLOAD.md says 26 pages / 15 slides / 4 preview pages; tpt.json `pages` 41 = 26 + 15. Cover says "26 PAGES + 15 SLIDES"; page 1 says 26 pages + 15-slide deck. The stale "15 pages" is gone.
- Rendered all 26 pages, 15 slides, the 4-page preview at 40 dpi and viewed cover.png at full size. Nothing clipped, overlapping or blank; preview watermarked; the cover is legible at thumbnail size (large title, three genre pills, grades/page strip). Preview PNGs are 2000x2000.
- Answers spot-checked against round 1 and re-confirmed by `--check`: worked example 40 bars at 128 BPM = 75 s, sections 8x5, 8 layers; rubric 5 x 1-5 = /25; pacing 15 slides across 4 classes; note charts add up bar by bar; the flip changes only E to Eb.
- Tunes public domain: Jingle Bells (Pierpont, Boston 1857), Deck the Halls (Welsh "Nos Galan", traditional; English words not used), Silent Night (Gruber 1818, melody only). No lyrics, brands, characters or audio. Disclosure line present. Title 72 chars with "Logic Pro" in the first 30; price $9; grades 9-12; subjects and tag as proven; zip holds exactly the three listed files.

**Verdict: APPROVED**

Required fixes:
(none)
