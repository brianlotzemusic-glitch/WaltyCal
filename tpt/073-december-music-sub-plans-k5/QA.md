# QA: 073 December Music Sub Plans K-5 (23 Nov 2026, independent QA)

## Checks run
- `python3 gen.py --check`: OK (before and after fixes). `python3 tools/tpt-validate.py tpt/073-december-music-sub-plans-k5`: OK.
- Hard rules: read the text of all 48 pages (pdftotext). No device, recording, projector, speaker, QR code, video, website or app. The sub never reads notation, sings, plays or names a pitch (chants are spoken words with printed clap dots; "open hands" for a silent beat). No songs, lyrics or speeches. No alcohol imagery, no assumptions about families, nothing asks students to take part in a religious practice. Disclosure line verbatim on the terms page and in UPLOAD.md.
- Keys recomputed with my own script: word search grid transcribed from the page; all 12 words appear exactly once in the allowed directions, at the positions listed in the key; the highlight overlay on page 42 matches (checked in a 250 dpi crop). Decode numbers give LIGHT AND MUSIC WARM WINTER NIGHTS. Syllable counts of every clapped word correct (light 1, snowflake 2, winter 2, candle 2, family 3, holiday 3, drum 1, Kwanzaa 2, piñata 3, lantern 2, star 1, midnight 2, Hanukkah 3, solstice 2, celebrate 3, countdown 2, feast 1, kinara 3, glow/night/bell 1, dreidel/winter/music/snowflake 2, posada/radio 3). All 8 chant-chart lines and word cards: ta for one syllable, ti-ti for two, shh for silence; every line has four boxes. Bingo: 16 clues, each answer is on the matching board bank (12 K-2, 16 3-5). Quiz answers (Day 1, Day 6 matching B/E/D/A/C) match the readings.
- Timings: Day 1 40, Day 2 40, Day 3 40, Day 4 40, Day 5 40, Day 6 40, Day 7 40, Day 8 35 minutes (all within 30-45). K-2 and 3-5 sheet present for all 8 days.
- Pages: days at a glance, quick start, teacher notes table, UPLOAD page-count list (2+7+3+3+3+4+3+3+5+4+3+3+5 = 48) and every "page N" reference agree with the 48-page PDF. Cut-out cards complete: 8 move cards (p22), 12 chant word cards (p32), 8 exit tickets, 9 folder labels, 2 awards.
- Listing: title is 75 characters in the required format; price 15.00; subject Music; grades kindergarten, 2nd, 3rd, 5th as 007; tags Winter, Christmas-Chanukah-Kwanzaa, New Year are exact non-heading entries in tpt/TAG-OPTIONS.json (heading "Holiday" is not used); US spelling; complete sentences.
- Looked at (one at a time): all 48 PDF pages at 110 dpi (before the fix, and p35 again after it), the 4 preview-PDF pages (watermark present on each), cover.png and preview-1, -2, -3 at full size; edge pixel scan on all four edges of every PNG (only the intended full-width color/black bands touch the sides). Word searches cropped at 250 dpi (pages 25 and 42).

## Facts verified by live fetch (23 Nov 2026)
- https://en.wikipedia.org/wiki/Kwanzaa : Dec 26 to Jan 1; created 1966 by Maulana Karenga; from Swahili "matunda ya kwanza", first fruits; the seven principles with exactly the Swahili names and meanings printed (Umoja unity, Kujichagulia self-determination, Ujima collective work and responsibility, Ujamaa cooperative economics, Nia purpose, Kuumba creativity, Imani faith); kinara holds seven candles, one lit each day; karamu is a communal feast.
- https://en.wikipedia.org/wiki/Las_Posadas : "between December 16 and December 24", nine nights, "posada" means lodging, house-to-house procession, piñatas, feast; Mexico, Guatemala, El Salvador, Honduras and Hispanic communities in the US (so "mainly in Mexico and other Spanish-speaking communities" is a fair summary).
- https://en.wikipedia.org/wiki/Hanukkah : eight nights, 25 Kislev, Maccabees recovered Jerusalem and the Second Temple, nine-branched candelabrum with a shamash, one more candle each night. https://en.wikipedia.org/wiki/Dreidel : four-sided spinning top played at Hanukkah.
- https://en.wikipedia.org/wiki/Christmas : December 25, birth of Jesus Christ, many non-Christians celebrate culturally, Julian-calendar churches on January 7.
- https://en.wikipedia.org/wiki/Winter_solstice : December solstice 21 or 22 December in the Northern Hemisphere, shortest daylight and longest night, axial tilt, opposite (summer) solstice in the other hemisphere. Web search 23 Nov 2026: 2026 solstice is Monday 21 December (20:50 UTC), Southern Hemisphere summer. Hemisphere wording on the pages is correct.
- https://en.wikipedia.org/wiki/New_Year%27s_Eve : 31 December, last day of the Gregorian year, countdown customs vary, Line Islands, Samoa and Tonga among the first places to welcome the year.
- https://www.bls.gov/ooh/entertainment-and-sports/music-directors-and-composers.htm : music directors (conductors) lead musical groups; give feedback so the ensemble sounds unified.
- https://www.bls.gov/ooh/media-and-communication/announcers.htm : hosts deliver news, sports, traffic, weather and may interview guests; radio DJs usually focus on one music genre. The page text "broadcasts music, news and weather, interviews guests, and often specializes in one kind of music" is an acceptable plain summary.
- https://en.wikipedia.org/wiki/Luthier : builds or repairs string instruments. https://en.wikipedia.org/wiki/Audio_engineer : balances and adjusts sound sources, mixes.
- Standards: https://www.nationalartsstandards.org/node/376 (Connect #11, MU:Cn11.0, "relate musical ideas and works to varied contexts and daily life") and a Common Planner NCAS listing (MU:Cr1.1.2a "Imagine", MU:Cn11.0.2a), via search. The teacher page said "cultural contexts" for Cn11.0; the standard says "varied contexts". Corrected.

## Defects found and fixed in gen.py (rebuilt; `--check` and validator OK)
1. Day 8 K-2 bingo board (p35) had 9 squares but a 12-word bank and the instruction "write the words from the word bank in the squares"; it also had a "B I N G O" banner spread over a 3-column board. Board is now 12 squares (3 x 4) so all 12 words fit, banner replaced by a plain "My bingo board" heading.
2. Quick start (p4) said crayons are needed for "Days 1, 3, 4 and 6"; the plans list crayons on Days 1, 2, 3 and 6 (Day 4 needs none, Day 5 optional). Corrected.
3. Teacher page standards sentence said "cultural contexts" for MU:Cn11.0; now "varied contexts" (matches NCAS wording). Codes kept (they are valid anchor-level codes).
4. SOURCES.md (generated from gen.py): added the QA re-fetch evidence for Hanukkah, dreidel, Christmas, Kwanzaa, Las Posadas, BLS pages and the standards codes; the radio-host quote now matches what the BLS page says.

## Notes (not blocking)
- p38 early finishers: "Circle: SHAKE TAP BLOW PLUCK" wraps onto a second line. preview-2: the subtitle sits close to the step headings (about 10 px gap). p33 "Class" label has no line.
- Las Posadas has a Christian (Nativity) origin; the product states only the customs, which is accurate and modest.

**Verdict: APPROVED**
