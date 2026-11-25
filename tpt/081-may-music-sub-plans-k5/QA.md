# QA: 081 May Music Sub Plans K-5 (independent review, 25 Nov 2026)

## Result
`python3 gen.py --check` passes (before and after my fixes); `python3 tools/tpt-validate.py tpt/081-may-music-sub-plans-k5` prints OK.

## Defects found and fixed (in gen.py, rebuilt)
1. **Koto drawing read as a plain striped board** (flat rectangle, thin strings, a dotted diagonal). Redrawn with a curved body, a thick side band, two feet, end blocks, 13 strings and 13 triangular bridges on a slant; it is labeled KOTO on every page that shows it (cards, Day 4 sheet, Day 5 match and key). At 250 dpi it now reads as a zither; the label still carries it at small sizes.
2. **SOURCES.md was stale**: it said no person is named on the pages, but the facts page names President Jimmy Carter as signer of the 1978 resolution. Corrected, with the statute (Pub. L. 95-419, signed Oct. 5, 1978). Added the QA re-check of the heritage-month steps and the new koto description.

## Hard rules scan (read all text of the 48 pages with pdftotext, plus the 4 preview pages)
- No device, recording, projector, speaker, QR code, video, website or app is needed; "microphone" appears only as a pretend mime in Day 6.
- The sub never reads notation, sings, plays or names a pitch. The only "rhythm" tools are words, dots and clapping; "ta / ti-ti / shh" are spoken syllables.
- No lyrics, no quotes. The four-line poem is original.
- Mother's Day: every mention carries "special grown-up" (grandparent, aunt, dad, coach, guardian); Day 3 tells the sub not every student has a mom at home. Memorial Day: one reading sentence, one facts row, one optional 20-second quiet moment; no war names or stories, clearly skippable.
- AAPI wording: five instruments, each tied to one place, with the line "No one instrument stands for a whole region"; no costume, food or stereotype imagery. Note (not blocking): the cover hero art is cherry blossoms, a fan and a drum, which leans Japanese; it is generic spring art and the cover text names AAPI Heritage, so I accepted it.

## Facts (checked live on 25 Nov 2026 by me, not from memory)
- Heritage month: web search of the Library of Congress heritage site (asianpacificheritage.gov/About; the direct page returned 403 to WebFetch) and the govinfo statute pages. Pub. L. 95-419, signed Oct. 5, 1978, set the week beginning May 4, 1979; Proclamation 6130 (May 7, 1990) made May 1990 the first month; Pub. L. 102-450 (Oct. 23, 1992) designates May each year. The pages say only "a heritage week in May", "a 1990 law stretched it to a month" and "a 1992 law made May ... every year": no overclaim. The official name is Asian/Pacific American Heritage Month and the pages say so, calling AAPI the common name.
- WebFetch of en.wikipedia.org: Koto (Japan; most common 13 strings, 17 also common; three fingerpicks on the right hand; movable bridges), Erhu (China; two strings; bow hair passes between them; sound box hexagonal, octagonal or round, so "often six-sided" is fair), Ukulele (developed in Hawaii in the 1880s from Portuguese machete, cavaquinho and rajao brought by immigrants; four nylon strings), Janggu (Korean hourglass drum, two heads; bare hand on the low head, bamboo yeolchae stick on the high head), Sitar (Indian subcontinent; Hindustani classical music; calabash gourd; curved movable frets; 6 or 7 played strings and the rest sympathetic). All page statements match; the sitar's 18th-century origin story is correctly left out.
- Mother's Day: web search (presidency.ucsb.edu proclamation 1268, history.com, woodrowwilsonhouse.org): joint resolution May 8, 1914 and proclamation May 9, 1914 set the second Sunday in May. The page prints only "made official in 1914". May 9, 2027 is the second Sunday (computed).
- Memorial Day: web search (va.gov, census.gov, govinfo): last Monday in May, honors those who died in military service; May 31, 2027 is the last Monday (computed).
- Hemisphere and spring: May is meteorological spring in the north, autumn in the south; the pages say exactly that.
- Music jobs: web search of bls.gov music directors and conductors ("lead orchestras and other musical groups"), sound engineering technicians (set up and operate equipment for concerts); luthier and radio host rest on the sources in SOURCES.md items 13 and 15 (the luthier search returned nothing new; wording stays generic and accurate). Pronunciations are labeled "say ..." as one common way; they are reasonable English renderings (the ukulele one follows the Hawaiian-influenced form).

## Answer keys recomputed independently
- Word search: my own 8-direction scan of the printed 12 x 12 grid found each of the 12 words exactly once, in the stated place and direction (KOTO r5c3 down, ERHU r7c2 down, SITAR r3c3, JANGGU r1c5, UKULELE r10c2, HAWAII r11c3, JAPAN r6c6, CHINA r9c3, INDIA r8c8 diagonal, KOREA r2c4, HERITAGE r5c4 diagonal, PACIFIC r2c11 down).
- Decode: MUSIC BRINGS US TOGETHER = 13 21 19 9 3 / 2 18 9 14 7 19 / 21 19 / 20 15 7 5 20 8 5 18 (matches the sheet).
- Syllables: every clapped word (drum 1, koto 2, janggu 2, sitar 2, heritage 3, Hawaii 3, sun 1, erhu 2, Pacific 3, bloom 1, bow 1, strum 1, ukulele 4, Memorial 4, bouquet 2, instrument 3, musician 3) and every chant word and poem line (4 syllables each) match; the rhythm chart's 8 lines are 4 beats each.
- Bingo: K-2 board is 3 x 4 = 12 squares with a 12-word bank equal to clues 1-12; 3-5 board is 4 x 4 = 16 with all 16 words; each clue's answer is on the board; winning-line wording (3 across for K-2; row, column or corner-to-corner for 3-5) agrees on the plan, both sheets and the quiz page.
- Quiz and keys: Day 1 (May, Japan, drum, Hawaii; May, a heritage week, 1992, Japan, Hawaii), Day 6 (instrument maker, conductor, music teacher; B E D A C) are supported by the readings. Koto drawn with 13 strings.
- Timings: Day 1 40, Day 2 40, Day 3 35, Day 4 40, Day 5 40, Day 6 40, Day 7 40, Day 8 35 minutes (all 30-45). The Quick Start supplies sentence covers crayons (Days 1, 2, 3, 6; optional 5 and 7), clear space (Day 4) and scrap paper (Day 8); each plan's "You need" box agrees.
- Page references checked against the 48 pages: keys 41 (Days 1, 2), 42 (Days 5, 6), 43 (Days 3, 4, 7, 8); plans 10, 13, 16, 19, 23, 26, 29, 34; sheets 11-12, 14-15, 17-18, 20-21, 24-25, 27-28, 30-31, 35-36; cards 22, word cards 32, chant book 33, quiz 37; facts 8; chart 7; games 6; sign 9; early finishers 38-39; labels 45; report 44. All agree. Cut-out sets are complete (8 move cards, 12 word cards that match the 12-word bank, 8 exit tickets, 8 folder labels plus the tub label, 2 awards). Trace words KOTO, ERHU, SITAR, BLOOM are whole.

## Listing
Title 79 characters (limit 80); the month stays and "AAPI Heritage" is the month's own name; the holiday words Mother's Day and Memorial Day are kept out of the title, with a fallback retitle noted (consistent with 073/079). Price 15.00. Subject Music. Grades kindergarten, 2nd, 3rd, 5th as 079. Tags exactly AAPI History Month, Mother's Day, Memorial Day, End of Year, Spring, all present in TAG-OPTIONS.json. UPLOAD.md page-count list totals 48 (2+7+3+3+3+4+3+3+5+4+3+3+5). Disclosure line verbatim in description and on page 47. US spelling and complete sentences.

## What I looked at
All 48 pages of the PDF at 110 dpi, one at a time (after the koto fix); all 4 preview-PDF pages; cover.png at full size, including all four edges (clean, nothing clipped); preview-1, preview-2 and preview-3 at full size. Drawings at 250 dpi: koto (before and after the fix), erhu, sitar, janggu, ukulele, flower, heart, sun (star and flower also on page 46 and 48). Erhu (pole, two strings, bow, six-sided box), sitar (neck with frets, small gourd, big gourd), janggu (hourglass with lacing and two heads), ukulele, flower, heart and sun are recognizable and respectful. Preview watermarks present on all 4 preview pages.

**Verdict: APPROVED**
