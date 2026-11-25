# QA: 082 June Music Sub Plans K-5 (independent QA, 25 Nov 2026)

## Defects found and fixed in gen.py (then rebuilt; `gen.py --check` OK; `tools/tpt-validate.py` OK)
1. Facts page claimed "June is African American Music Appreciation Month". Sources fetched show the observance began as Black Music Month (Carter, 1979), was renamed African American Music Appreciation Month in 2009 and returned to Black Music Month in 2023, so "current name" was not supportable. Now: "celebrated in the United States as Black Music Month, also called African American Music Appreciation Month."
2. Teacher notes (page 2) had a comma-spliced run-on about the 1866 celebration, parades, 1980 and 2021. Split into proper sentences.
3. UPLOAD.md description said "the words for saying each instrument's name are on the facts page" (untrue: the facts page describes the instruments). Changed to "the facts page answers common questions".
4. SOURCES.md items 7 and the disagreement note updated to match.

## Facts (fetched live 25 Nov 2026)
- 19 June 1865, Galveston, Granger, General Order No. 3, first 1866 celebration (Jubilee Day), Texas state holiday from 1 Jan 1980: National Archives https://rediscovering-black-history.blogs.archives.gov/2021/06/16/juneteenth-the-celebration-of-a-new-freedom-in-america ; Texas State Library https://www.tsl.texas.gov/ref/abouttx/juneteenth (Granger read General Order No. 3 on 19 June 1865; HB 1016, state holiday starting 1980). Pages print "an order was read": consistent.
- Federal holiday: Congress.gov https://www.congress.gov/117/plaws/publ17/PLAW-117publ17.htm (Public Law 117-17, approved 17 June 2021, adds Juneteenth National Independence Day, June 19, to 5 U.S.C. 6103(a)). Pages print 2021 and Biden signed: OK (date not printed).
- Black Music Month: https://en.wikipedia.org/wiki/Black_Music_Month plus web search (see fix 1).
- Solstice: https://earthsky.org/earth/everything-you-need-to-know-june-solstice (21 June 2027 14:11 UTC; can fall June 20-22; sun's northernmost point; start of summer north, winter south). "June 20 or 21" accepted for the current era; 2027 = June 21: OK.
- Father's Day: https://history.house.gov/Historical-Highlights/1951-2000/Father-s-Day-Becomes-a-National-Holiday/ (P.L. 92-278, signed 24 April 1972, third Sunday in June). The 1910 claim is not printed. 20 June 2027 is the third Sunday: OK.
- Instruments: Wikipedia Triangle (metal bent into a triangle with one open end, hung from a loop, struck with a metal "beater"), Tambourine (frame with pairs of small metal jingles, drumhead, shaken or struck), Maraca (shaken by a handle, usually a pair): all match.
- Jobs: BLS conductors "lead orchestras and other musical groups during performances" (music-directors-and-composers); BLS sound technicians set up and operate sound equipment for live events and concerts; BLS announcers/hosts present news, take calls, interview guests; luthier builds string instruments (guitars; ukulele is a plucked string instrument, our inference, wording "such as" is safe).
- End of school: general ("many", dates vary): fine.

## Content and hard rules
All 48 pages read as text and viewed. No device, recording, projector, speaker, QR, video, website or app needed. The sub never reads notation, sings, plays or names a pitch (only tapping a pencil, clapping, patting, saying words). No lyrics or quoted speeches; the four-line poem is original. Juneteenth is factual, non-graphic, uses "enslaved people", has a "Teaching Juneteenth with care" note, bans role-play of slavery and accents, and routes hard questions to the classroom teacher. Father's Day is "dad or special grown-up" everywhere (reading, Day 7 cards, facts page, keys). Secular, US spelling, complete sentences.

## Recomputed keys (own script)
- Word search: 12x12 grid parsed from the PDF; each of the 12 words occurs exactly once, positions and directions equal the key (JUNETEENTH r9c1 across, GALVESTON r3c12 down, SOLSTICE r5c5 diag, FREEDOM r1c1 down, PARADE r1c7, SUMMER r4c11 down, PICNIC r2c5 diag, TEXAS r3c2 down, MARACAS r1c4 down, CHEER r2c3 down, DRUM r11c2, KITE r10c3).
- Decode 13 21 19 9 3 / 6 9 12 12 19 / 20 8 5 / 19 21 13 13 5 18 = MUSIC FILLS THE SUMMER (matches key).
- Syllables: drum 1, summer 2, parade 2, maracas 3, freedom 2, Galveston 3, sun 1, Texas 2, tambourine 3, splash 1; march 1, Juneteenth 2, solstice 2, triangle 3, watermelon 4, graduate 3; sort: drum/cheer/sun; summer/parade/freedom; tambourine/celebrate/vacation. Poem lines each 4 syllables. Chart/cards ta and ti-ti correct for every word.
- Bingo: K-2 word bank 12 = clues 1-12 answers; 3-5 bank 16 = all 16; boards 3x4 (12) and 4x4 (16); K-2 win "three across in one row" matches the 3-wide board; 3-5 row/column/corner-to-corner.
- Day timings: 40, 40, 35, 40, 40, 40, 40, 35 minutes (steps sum exactly; all within 30-45) and match each plan's "about N min".
- Quick Start materials (pencils; crayons Days 1,2,3,6, optional 5,7; clear space Day 4; scrap paper Day 8) cover every day. Page references (plans 10,13,16,19,23,26,29,34; sheets 11-12,14-15,17-18,20-22,24-25,27-28,30-33,35-37; extras 38-40; keys 41-43; report 44; labels 45; awards 46; terms 47; thanks 48) all agree with the 48-page layout. Move cards 8/8 and chant cards 12/12 complete; trace words DRUM, SUN, KITE, WAVE whole.

## Listing
UPLOAD.md page list totals 48; title 74 characters with month; price 15.00; tags exactly Juneteenth, Father's Day, Summer, End of Year (all present as non-heading entries in TAG-OPTIONS.json); subject Music; grades kindergarten, 2nd, 3rd, 5th; disclosure line verbatim in description and on page 47.

## Visual
Viewed every page at 110 dpi (1-48), all 4 preview-PDF pages (one PREVIEW watermark each), cover.png and preview-1..3.png at full size (cover edges clean, nothing clipped; callouts and band readable). Cropped at 250 dpi: word search (all letters legible), trace words, and each drawing on the move cards (sun, drum, tambourine, maracas, triangle, kite, wave, banner) plus star and heart on the awards page: all recognizable and unclipped. Tambourine reads as a jingle ring with ribbons (acceptable, labeled). No blocking visual defects.

**Verdict: APPROVED**
