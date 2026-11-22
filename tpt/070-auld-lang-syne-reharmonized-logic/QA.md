# QA: 070 Auld Lang Syne Reharmonized (Logic Pro)

Independent QA (not the builder). The builder's earlier QA.md was ignored and is replaced by this file.

## Sources fetched by QA on 22 Nov 2026
1. English Wikipedia "Auld Lang Syne", raw wikitext (action=raw): the LilyPond score (F major, 4/4, pickup). Recomputed with my own relative-mode parser: 56 notes, pitches and lengths identical to the chart after moving it up 5 semitones.
2. CPDL, Brigid Baker edition (CPDL no. 21485, "Public Domain", MusicXML, F major): my own MusicXML parser compared the melody pitch at the start of every beat of the pickup and all 16 bars: 0 differences (it splits two beat-4 quarter notes into two eighths).
3. CPDL, Philip Rice edition (no. 37897, Public Domain, MusicXML): 1 difference, tune bar 12 beat 4 is F5 (in F major) where the chart has D5. The builder had claimed this edition agreed on every beat; that claim was wrong (see defect 1).
4. Mutopia Project, Horetzky "No. 31 Auld Lang Syne" (.ly header "Public Domain"): in 2/4 and D major, so it cannot be a beat-for-beat source.
Not fetched or verified: Beethoven WoO 156 (the builder's claim about it was removed). hymnary.org returned 403.

Public domain: traditional tune, Burns 1788, tune with the words 1799; pre-1930. Wikipedia also gives the title as "old long since" / "long long ago" / "days gone by" and says the chorus line "might be loosely translated as 'for the sake of old times'": the kit's wording ("often put into English as", "often rendered") is accurate and hedged.

## Checks
- `gen.py --check` passes (before and after my edits); `tools/tpt-validate.py` OK.
- Melody: every chart bar sums to 16 sixteenths (pickup bar plus bar 16 make one bar); G major equals C major + 7 semitones for all 56 notes; piano-roll images match the tables (viewed at 250 dpi, pages 12 and 13). The chart page says it follows the plain 4/4 version and that other editions vary some pickup notes and rhythms.
- Chords: my own script recomputed all 48 rows (pop, ballad, EDM, both keys): downbeat note, letter name, Roman numeral, chord tones (7ths stacked on the key's scale, sus4 and add9 by interval), passing notes, all matching the printed tables (0 mismatches). Every downbeat is a chord tone. Chord key (13 chords) and worked-example G major table also correct.
- Math: tempo table at 8 tempos (60/BPM, 240/BPM, 16 and 40 bars), section starts at 72/100/128 BPM, worked example (133.33 s, 13.33/66.67/120.00), 4+16+16+4=40, map element counts 2/6/7/3 (=18), rubric 5 x 5 = 25 all verified.
- Wording: no alcohol imagery, no religious or holiday words, no lyrics (poem not reproduced), US spelling, Logic Pro claims hedged ("if your version has it"); only File > New and File > Bounce paths, Command-B, X, A are named (real Logic shortcuts); Transpose in the Region inspector is real.
- Listing: title 70 chars, "Logic Pro" in first 30, no seasonal words; 4 grades; subjects Music / Computer Science - Technology / Music Composition and tags New Year / Project-based Learning / Projects / Activities each found individually in the option lists and none is a heading; disclosure line in description and terms page; UPLOAD.md counts 26 + 14 = 40 agree with the PDFs (26, 14, preview 4); Step N, class badges and page cross-references agree with the pacing page.
- Viewed: all 26 PDF pages at 110 dpi (pages 12-13 also at 250 dpi, groove cards cropped at 250 dpi), all 14 deck slides at 110 dpi, all 4 preview-PDF pages, cover.png and preview-1..3.png at full size. No notation defects, no clipping or overlap besides defect 2.

## Defects found and fixed in gen.py (rebuilt, --check and validator OK)
1. Wrong source claim: Rice's CPDL edition was cited as agreeing on every beat but differs at tune bar 12 beat 4. Fixed: source 2 is now Baker's edition (CPDL 21485, 0 beat differences) on the chart page, credits page and UPLOAD.md; Rice's variant is disclosed; the unverified Beethoven/downbeat-agreement sentence was replaced by a verified statement (Horetzky is 2/4 in D major); chart-page wording now says "Other editions vary some pickup notes and rhythms".
2. Deck slide 2: the second line of the teacher text in the black "Think, then share" box touched and clipped at the box's bottom edge. Fixed by shortening the line so it fits on one line.

## Notes (not blocking)
- Wikipedia's LilyPond score is the only source that matches the chart note for note and length for length; Baker matches at beat level. This is stated.

**Verdict: APPROVED**
