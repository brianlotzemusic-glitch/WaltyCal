# QA: 027 Winter Botanical Wall Art, set of 3 ($5.00)
Designer self-check only; QA still to do. mk.py needs the 4x originals (deleted to save space; regenerate or run it from the zip contents).
- `python3 gen.py --check` prints ALL CHECKS PASS (zip 19.2 MB, 15 JPG + 5 PDF + README; pixel sizes, 300 DPI tag, ratios, PDF page sizes, listing rules).
- Looked at: the three unified images side by side (clean, no artefacts, matching navy), 100% crop of the 24x36 fern (slightly crystalline AI detail, fine), a PDF page strip, all 4 listing images.
- Known limits for QA to weigh: native art about 3186x4096, so 24x36 is an enlargement (stated in listing and README); PDFs are lower resolution (about 80-130 DPI at the largest size) to keep the ZIP under Etsy's 20 MB; the lead image is a code-drawn room, not an AI lifestyle photo (saved credits). Only one digital file per listing is supported by tools/etsy.py.
