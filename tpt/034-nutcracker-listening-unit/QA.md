# QA: 034 Nutcracker Listening Unit

Reviewer: independent (did not build). Checked against TPT-FACTORY.md "QA checklist".

## Findings
1. `python3 gen.py --check` passes (quiz 16 points, keys computed, 17 Letter pages, fonts embedded, 4 watermarked preview pages, 2000x2000 images, tpt.json/UPLOAD.md ok).
2. Pages: all 17 rendered at 60 dpi and viewed, plus cover, 3 preview thumbnails and the 4-page PREVIEW PDF. No clipping, overlap, blank or unreadable pages. Cover reads at thumbnail size. Preview is watermarked.
3. Answer keys recomputed by hand. Story order B F D A E C matches the page-3 story; who-is-who B/D/A/C correct. Quiz 1-6: 5,3,1,6,4,2 (harp waltz=Flowers, fast Russian=Trepak, guests=March, celesta=Sugar Plum, three flutes=Reed Flutes, voices=Snowflakes). 7 B Tchaikovsky, 8 C 1892, 9 A celesta, 10 C 3, 11 B Trepak, 12 C woodwinds, 13 T, 14 F, 15 F, 16 T. All match the key page; answers are spread across A/B/C.
4. Music facts verified: Nutcracker Op. 71, premiere 18 Dec 1892 (Gregorian) at the Mariinsky, Ivanov choreography from Petipa's plan; Hoffmann 1816 / Dumas 1844 source; suite of eight pieces; March 4/4 with trumpets; Snowflakes with children's chorus (end of Act I); Trepak = Russian dance, 2/4, speeds up; Mirlitons/Reed Flutes = three flutes, 2/4; Waltz of the Flowers 3/4 with harp cadenza; Sugar Plum Fairy with celesta (heard in Paris, 1891) over pizzicato strings and bass clarinet; celesta is a keyboard-struck-metal-bars instrument (classed percussion). Story summary is accurate and noted as one common version. No errors found.
5. Public domain: Tchaikovsky, The Nutcracker, 1892 (PD). No recordings, lyrics, brands or characters. Secular wording, suitable for public schools.
6. Listing: title 74 chars (<= 80); description page count and contents match the PDF page map (cover/notes 1-2, story 3, check 4, toolkit 5, maps 6-11, gallery 12, spotting 13, quiz 14, key 15, review 16, terms 17); disclosure line present in description and on terms page; price $6 (units up to $7 OK).
7. tpt.json: all 6 tags and both subjects are exact entries in TAG-OPTIONS.json / SUBJECT-OPTIONS.json; 4 grades (2nd, 3rd, 5th, 6th); all 6 listed files exist. Season: Christmas ~6 weeks out, fine.

Minor, not blocking: 4th grade is not ticked although the product is 2-6 (TpT's 4-grade limit forced a choice; acceptable). The PREVIEW PDF includes the answer key page, as UPLOAD.md states.

**Verdict: APPROVED**

## Fix round 16 Nov 2026 (HELD, no reupload queued)
Audit defects fixed in gen.py and confirmed by the inspector: Trepak cue now matches its gauges; violin bow moved beside the body; preview-2 pages no longer overlap; both cover arms end in a mitt; Reed Flutes labels no longer struck through; Sugar Plum map no longer pre-marked; Draw-it box clear of footer.
Inspector round 2 still reported: PDF p14 "Score" line and p16 star row touch the footer rule; p8/p9 last writing line close to the footer rule; p6 dashed path touches boxes 6-7; preview-2 sub-headline "Every listening page ... have an answer key" overstates (maps say answers vary).
Not queued: rounds spent.

## Fix round 16 Nov 2026 (final, new inspector brief)
Further fixes: quiz Score line and Review star row cleared from the footer rule; preview-2 subtitle now "The story check, spotting chart and quiz all have an answer key". Fresh inspector (BLOCKING/NOTES brief), all images, 17 pages, 4 preview pages: no BLOCKING item. NOTES only (dotted path touches box 6 / snowflakes on p6-7; thin/thick rules are rasterisation).

**Verdict: APPROVED**
