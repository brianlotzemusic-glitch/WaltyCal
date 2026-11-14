# QA: 040 Trap Nutcracker (independent review, round 2)

## Checks run
- `python3 gen.py --check`: CHECK OK (27 pages, deck bounds, notation, answer keys, zip current, no banned strings). `tools/tpt-validate.py`: OK. `git status --short`: only `tpt/040-trap-nutcracker-logic/` is new.
- Rendered all 15 deck slides and all 27 PDF pages at low resolution and looked at each: nothing clipped, blank or overlapping, no regressions from the rebuild. Cover reads at thumbnail size; preview PNGs 1-3 are 2000x2000 with watermarks; preview PDF has 4 pages.
- Read every slide bullet (from the .pptx): no truncation or typos. Slide 14's 4th bullet now reads "Answer at least 2 of each classmate's questions" in both the pptx and the deck PDF. The pptx text matches the deck PDF text.
- Zip holds exactly 3 files (guide PDF, deck PPTX, deck PDF) and each is byte-identical to the folder copy.
- Round-1 verification stands: notation and note counts (Sugar Plum 40, Trepak 43), rubric /25, worked example 64 s, hat timings, public-domain source (Tchaikovsky, The Nutcracker, 1892), real Logic Pro features, title 74 characters, disclosure line present, tags and subjects valid.

## Findings
- None that a buyer would notice or that break a rule. (Minor, not blocking: slide 5 has some empty space between the flow graphic and bullets.)

**Verdict: APPROVED**
