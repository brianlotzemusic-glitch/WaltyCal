# QA: 063 Eight Nights, Eight Layers (Logic Pro kit)

Independent QA agent (not the builder), second pass with live web checks.

- Festival facts (eight nights; rededication of the Second Temple, 164 BCE = 2nd century BCE; 25 Kislev; nine-branch hanukkiah with shamash; one candle added each night) confirmed on live Wikipedia and Britannica search results and My Jewish Learning (eight nights, 164 BCE, one candle per night). Wording is neutral, framed as inspiration, not a religious activity; no Christmas imagery; dates given only as "late November or December".
- Math recomputed: seconds per bar = 240/BPM, 32-bar totals at 80/90/100/110/120/128 BPM, worked example at 100 BPM (76.8 s; entrances 0, 9.6 ... 67.2 s), 8x8 staircase (36 cells, 144 layer-bars). `gen.py --check` prints CHECK OK; `tools/tpt-validate.py` prints OK.
- Menorah counted as 4 + shamash + 4 = 9 on cover, previews, PDF cover and deck slides.
- Logic Pro claims hedged ("if your version has it"); only File > New and File > Bounce named as menu paths.
- Page counts: PDF 23 pages, deck 14 slides, preview PDF 4, listing 37 total; matches UPLOAD.md. Title 77 characters, "Logic Pro" in the first 30, no seasonal words. Tags and subjects valid.
- No Maoz Tzur melody chart (two public-domain transcriptions could not be verified); the kit is melody-optional and says so.
- All 23 PDF pages, 14 slides, 4 preview pages, cover and 3 previews viewed; Visual inspector (third agent) replied OK.

**Verdict: APPROVED**
