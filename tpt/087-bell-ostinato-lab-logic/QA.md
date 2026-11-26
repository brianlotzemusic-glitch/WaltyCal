# QA: 087 Bell Ostinato Lab (Logic Pro)

## Findings
- `gen.py --check` passes; `tools/tpt-validate.py` OK. PDF 25 pages, deck 17, preview 4; UPLOAD.md says 25 + 17 = 42, matches tpt.json.
- **Motif (verified, my own fetches).** Bb4 A4 Bb4 G4 = quarter, eighth, eighth, quarter, G minor (two flats), 3 beats = one bar of 3/4. Second key G4 F#4 G4 E4 = every note exactly -3 semitones (MIDI 70 69 70 67 -> 67 66 67 64).
- **DEFECT 1 (fixed): the builder's "second source" (Commons JPG of the Wikipedia motif) was not independent.** Replaced in gen.py/UPLOAD.md section 9 by a truly independent source: Wikimedia Commons "Щедрик.pdf" (typeset from the 1970 Kyiv edition, Музична Україна, ed. Gordiychuk; a different typesetter from the Wikipedia LilyPond). I viewed it at 130 and 300 dpi: two flats, same four notes and rhythm, repeated. Caveat stated in UPLOAD.md: that score prints no time-signature numerals in its opening, so 3/4 rests on Wikipedia's score marking plus the note values. The JPG is explicitly not counted. Claim kept at the honest level (four-note motif; sources agree).
- **DEFECT 2 (fixed): UPLOAD.md said 25 Dec was "generally said" as the premiere;** Wikipedia says that claim is incorrect (29 Dec 1916, Kyiv Merchants' Assembly Hall). Reworded.
- **DEFECT 3 (fixed): "Press X for the Mixer"** stated as fact; now "the key command is X by default, if your version has it". Bounce `File > Bounce > Project or Section`, Command-B: confirmed on Apple Support search results. Apple's Automation overview page could not be read; automation stays generic with "if your version has it", no invented menu paths.
- **DEFECT 4 (fixed): deck slide 9 said "A new layer joins every 4 bars"** (build section adds two, answer section one, solo none); now "Each 4-bar section adds or changes a layer".
- Dates: Leontovych 1877-1921 (Wikipedia); first performance 29 Dec 1916 (Wikipedia Shchedryk page); first publication 1921, Kiev: Mystetstvo (IMSLP work page; the Wikipedia Shchedryk article gives no print year). Composition year differs by source (1901/1904/1919): kit says only "first performed December 1916". Good.
- Wilhousky: English lyrics/1936 arrangement copyrighted (IMSLP note on Weymouth score; Wikipedia: Wilhousky "secured a copyright on his lyrics in 1936"). Kit prints no lyrics and no arrangement, tells students not to copy any later arrangement. Layer map and answer phrase use only the motif, its transposition (G4 F#4 G4 E4), octave copies and a held G3 pad; no melodic material beyond the motif, so nothing copies a known arrangement. The optional "make it your own" prompt asks for an original phrase. OK.
- Math recomputed independently: bar = 180/BPM (72 2.5, 80 2.25, 90 2.0, 100 1.8, 120 1.5, 144 1.25 s); 16 bars 40/36/32/28.8/24/20 s; beat 60/BPM; eighth 30/BPM. Intervals: Bb-A = -1 (minor second down; the QA brief's "major second" was wrong, kit is right), A-Bb +1, Bb-G -3, sum -3, span minor third. Transposition -3 checked note by note; other keys -5 (F E F D = 65 64 65 62) and +2 (C B C A = 72 71 72 69) correct. Frequencies 466.2/440.0/392.0/370.0/329.6, Bb5 932.3, Bb3 233.1 correct. Layer map cells counted: bell 14 (bars 1-9, 11, 13-16), celesta 8, pad 12, low bell 4, answer 2 = 40; layers per bar 1/3/2/4 (x4 bars) = 40, matches the drawn blocks and number row. Volume levels 32x5,40,48,56,64,68,72,76,80,88,96,104, never falling, 8 per bar in bars 13-16. Rubric 5 x 5 = /25. Worked example consistent with the student pages.
- Dynamics levels: Wikipedia "Dynamics (music)" table lists Logic Pro 9 defaults as pp 32 ... ff 112 (cited to an archived Apple page; says nothing of later versions). Kit labels them "an example plan ... not a rule"; the buyer pages do not claim they are Logic's current defaults. OK.
- Tags exact in TAG-OPTIONS.json (Winter, Project-based Learning, Projects, Activities), subjects exact (Music, Music Composition, Computer Science - Technology), 4 grades, title 73 chars with "Logic Pro" first, no seasonal words, disclosure line present, US spelling.
- Minor note (not blocking): p. 23 (feedback page) is badged "Classes 2-3" but the pacing page lists it only under Class 3.

## Sources actually fetched (by me, 26 Nov 2026)
- Commons "Щедрик.pdf" (via de.wikipedia file page and upload.wikimedia.org): independent score, viewed.
- IMSLP "Carol of the Bells (Leontovych, Mykola)" work page: 1921 first publication, Wilhousky lyrics copyright note, public-domain notes (Spanish edition).
- en.wikipedia "Shchedryk (song)" (29 Dec 1916, 3/4, ostinato, Wilhousky 1936) and "Dynamics (music)" (Logic Pro 9 table).
- Apple Support search results for Bounce (File > Bounce > Project or Section, Command-B).
- Not reachable: CPDL (403), Commons API/ file pages (429), Pravda article (403), a scan of the 1921 print.

## Rights notes for the owner
1. Public domain: this is a reading of dates (composer died 1921, first print 1921), not legal advice, and the 1921 print was not seen. The score I checked is a modern typesetting of the 1970 edition, tagged public domain on Commons; the kit copies none of it, only the four-note motif.
2. The English title "Carol of the Bells" appears only in the description and on teacher pages (p. 3 and p. 4) as "known in English-speaking countries as" and "the 1936 choral arrangement that made it famous as ...". That is nominative reference to a public-domain tune's common name and is low risk; the title is kept out of the title field and cover. Wilhousky is not named on buyer pages. If you want zero exposure, delete the two mentions.
3. Avoid any claim that the kit includes the arrangement or lyrics; it does not, and says so.

**Verdict: APPROVED**
