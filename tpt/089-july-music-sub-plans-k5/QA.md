# QA: 089 July Music Sub Plans K-5 (independent review, 27 Nov 2026)

## Checks run
- `python3 gen.py --check` OK before and after fixes; `python3 tools/tpt-validate.py tpt/089-july-music-sub-plans-k5` OK.
- Hard rules: read the text of all 48 pages (pdftotext). No device, recording, projector, speaker, QR, video, website or app. The sub never sings, plays, reads notation or names a pitch (chants are words and claps; "buzz your lips with no sound" is a mime). No lyrics, no quotes. Every sheet that names Independence Day (Day 1 K-2, Day 1 3-5) carries the Summer choice line; teacher notes and the facts page say some families do not celebrate it; no flags or politics; fireworks are only pictures and the word BOOM (may be whispered).
- Recomputed independently: word search grid parsed from the PDF text, all 12 words found once each, only across/down/diagonal-down, positions equal the key; decode 12 9 19 20 5 14 / 20 15 / 19 21 13 13 5 18 / 19 15 21 14 4 19 = LISTEN TO SUMMER SOUNDS; every syllable count (K-2 and 3-5, incl. musician 3, celebration 4); poem lines each 4 claps; chant words all 1-2 syllables; bingo K-2 bank 12 = clues 1-12 (3 x 4 board), 3-5 bank 16 = all 16 clues (4 x 4), winning-line wording agrees on pages 34, 35, 36, 37; K-2 match key lines agree with picture order; Day 6 match D/B/E/A/C correct; Day 1 K-2 "sentence 7 / question 5" and 3-5 "last 3 sentences / question 6" are right.
- Timings: Day 1 40, Day 2 35, Day 3 35, Day 4 35, Day 5 40, Day 6 40, Day 7 40, Day 8 35 minutes (all 30-45); Quick Start materials cover every day; "Day 3 is open-ended" on pages 2 and 5 matches page 43; all page references (answer keys 41/42/43, plan pages, page 6/7/8/9/38/44/45) agree with the 48-page layout; cards complete (8 move cards, 12 word cards = word bank); trace words whole.
- Listing: UPLOAD.md page-count list totals 48; title 68 chars; price 15.00; tags exactly July 4/Independence Day, Summer, Worksheets, Printables, Activities (each present as a non-heading option in tpt/TAG-OPTIONS.json, validator OK); subject Music; grades K, 2, 3, 5 as 088; US spelling; disclosure line verbatim on the terms page and in the description.

## Sources fetched by QA (WebFetch, 27 Nov 2026)
- archives.gov/founding-docs/declaration-history: Congress finished revising and the Declaration "was officially adopted" July 4, 1776; signing was Aug 2, 1776. Page says "approved": fine, and nowhere says signed July 4.
- en.wikipedia.org/wiki/The_Star-Spangled_Banner: Key wrote the words in 1814; national anthem 1931 by joint resolution signed by Hoover (March 3 or 4 given): pages print only 1931.
- en.wikipedia.org/wiki/The_Stars_and_Stripes_Forever: Sousa, 1896; national march by Act of Congress 1987. Matches.
- en.wikipedia.org/wiki/Sousaphone: brass, tuba family, named for Sousa, wraps around the body, widely used in marching bands (first built c. 1893: not printed).
- en.wikipedia.org/wiki/Drum_major_(marching_band): "usually positioned at the head of the band". Matches "usually at the front".
- en.wikipedia.org/wiki/Marching_band: brass, woodwind, percussion; parades, sporting events. Matches ("usually", "often").
- en.wikipedia.org/wiki/Cricket_(insect): males chirp by stridulation with the front wings. Matches "rubbing parts of its wings together".
- timeanddate.com/calendar/aboutseasons.html: July is summer in the Northern and winter in the Southern Hemisphere. Matches.
- onetonline.org/link/summary/49-9063.00 (replaces the unfetchable BLS page): "Repair percussion, stringed, reed, or wind instruments." Matches "fixes instruments that are damaged".
- bls.gov broadcast-and-sound-engineering-technicians: "assemble and operate sound equipment"; "set up and take down equipment for events and live performances". bls.gov announcers: radio hosts take calls, interview guests, discuss issues with listeners. Both match.
- Not fetched by QA: park-concert custom (summary-level claim, worded "many parks and towns"); Wikipedia Beach_ball; fine.

## Defects found and fixed
1. The ocean wave drawing (page 9, 17, 18, 20, 22, 24, cards, key page, previews) was a scalloped blob that read as a crown or cloud, not a wave. Redrew it in gen.py as a swell with a curling crest and a white foam line; checked at 250 dpi on the Day 4 card: reads clearly as a wave. Sun, cricket (antennae, wing, bent back leg), firework burst, kite, flip-flop (V strap), popsicle, drum and star checked at 250 dpi: recognizable and consistent with the text.
2. SOURCES.md fact 9 (instrument repairer) rested on a 403 BLS page plus search snippets; replaced with the fetched O*NET page; terms-page credits now also name onetonline.org; SOURCES.md drawing note updated (done in gen.py because SOURCES.md is generated).

## Viewed
All 48 pages at 110 dpi one at a time (including 4, 7, 10, 13, 19, 23, 26, 29, 31, 33, 34, 40, 44, 45, 47, 48); the 4 preview-PDF pages; cover.png (all four edges clean, JULY fits the band, accent navy #1A5694 is the deeper shade of the hero's sky blue), preview-1, -2, -3 at full size; Day 4 card page and Day 3 page at 250 dpi; the word search cropped from the 110 dpi page and parsed from text. Rebuilt PDFs after the wave fix: 48 pages, check OK. (After the redraw the previews re-rendered; the wave on preview-3 is only a thumbnail-size icon.)

No remaining blocking issue.

**Verdict: APPROVED**
