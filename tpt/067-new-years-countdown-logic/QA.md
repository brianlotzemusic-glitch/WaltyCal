# QA: 067 New Year's Countdown (Logic Pro)

## Findings
- `gen.py --check` passes. `tools/tpt-validate.py` OK.
- Independent recomputation (own script) matches everything printed: bar = 240/BPM; 96/120/144 BPM give 4/5/6 countdown bars; totals 44/45/46 bars = 110.00/90.00/76.67 s; section starts and drops (bar 21/22/23 = 50/42/36.67 s; 21 bars x 2 s = 42 s); non-whole tempos (90/100/110/128 = 3.75/4.1667/4.5833/5.3333 bars); snare ladder 500/250/125/62.5 ms at 120 BPM, 625/312.5/156.25/78.13 at 96, 416.67/208.33/104.17/52.08 at 144; 8+16+32+64 = 120 hits; all 33 cue-sheet cells (second, number, bar.beat, 1-based bars and beats) correct; worked example (45 bars, 90 s, countdown bars 17-21, outro at 74 s); section-map element counts 3,6,4,7,4; rubric 5 x 5 = 25.
- Logic Pro claims: no invented menu paths. Marker track, Create Marker, Reverse, Auto Filter, Step Sequencer and Sample Alchemy are hedged ("if your version has it"). Filter sweep, riser, snare roll, pitch-up (12 semitones = octave, frequency doubles) are correct. Secular theme; no alcohol, brands or recordings; Apple named only for compatibility.
- Cross-references: Step 1/2/5/6 badges and page numbers agree with the project sheet, pacing page (slides 1-6, 7-9, 10-14) and class badges; 23 + 14 = 37 in UPLOAD.md and tpt.json.
- Listing: title 74 characters, "Logic Pro" at the start, no seasonal word. Four grades. Subjects Music, Computer Science - Technology and Music Composition are non-heading entries. "New Year" is a real non-heading entry under the Holiday heading; the other tags are valid too. Disclosure line is present.
- Viewed: all 23 PDF pages at 110 dpi, all 14 deck slides, the 4 preview-PDF pages, cover.png and preview-1..3.png. No clipping, overlap or blank pages. No music notation in the product.
- Notes (not blocking): slide 2 has a large gap inside the black box; "Teaches how..." on pages 3 and 6 is a shared sentence fragment.

**Verdict: APPROVED**
