# QA 068 Music Production Vocabulary Word Wall

Checked: `gen.py --check` (OK before and after fixes), `tools/tpt-validate.py` (OK). UPLOAD.md page counts (37) agree with the PDF, index, teacher notes, terms page, cover and tpt.json. Preview pages 20, 22, 30, 34 are correct. 27 cards over 3 sheets (26 terms plus a blank card) agree. Title is 75 characters with no seasonal words. tpt.json has 4 grades, subjects Music and Music Composition, and the six tags Posters, Word Walls, Bulletin Board Ideas, Printables, Assessment, Study Guides, all validated against the option lists. Disclosure line present in the description and on the teacher and terms pages. US spelling throughout. No software or brand names.

Independent recomputation: compressor 1:1 below -20 dBFS and 4:1 above (-12 gives -18, 0 gives -15); seconds per beat 1.0, 0.667, 0.5, 0.4 at 60/90/120/150 BPM; 120 BPM is 2 s per bar and 16 s per 8 bars; 2^16 = 65,536 and 2^24 = 16,777,216; about 96 and 144 dB (6.02 dB per bit; the exact 16-bit figure is 98 dB, and "about 96" is the usual rounded figure); Nyquist 22,050 and 24,000 Hz; 500 ms = 1 beat at 120 BPM; -6 dB = 0.501 amplitude; high-pass and low-pass at -3 dB at cutoff with 12 dB per octave; piano roll C, E, G, C at semitones 0, 4, 7, 12 (rows and black keys correct); automation fades span 2 bars each (1 to 3, 11 to 13); fader positions at -4, -6 and 0 dB match the tick scale; headroom meter scale linear. Quiz key re-derived: 15 matching letters and 15 short-answer points = 30, all answers follow from the term pages.

Sources fetched: Wikipedia DBFS (0 dBFS = full scale, negative below, 6 dB per bit), Wikipedia MIDI (notes 0 to 127, middle C = 60). The compression article fetch failed (404); the ratio definition is standard and was recomputed.

Viewed: all 37 PDF pages at 110 dpi, the 4 preview PDF pages, cover.png, preview-1, 2 and 3 at full size, and a 250 dpi crop of the Sample poster after the fix.

## Defects found and fixed in source
1. Poster 10 (Sample): the arrow ran through the "Timeline" heading text. Arrow shortened.
2. Poster 14 (Bit depth): labels under the 3-bit and 4-bit drawings read "16 bits = 65,536 levels" and "24 bits = 16,777,216 levels", which looked like captions for the drawings. Replaced by one line "Real audio: 16 bits = ... and 24 bits = ...".
3. Poster 19 (Compression): "every 4 dB in gives 1 dB out" and the matching fact were literally wrong. Now "4 dB over comes out 1 dB over" and "4 dB over the threshold comes out 1 dB over".
4. Poster 20 (Limiter): "so the exported song never clips" overclaimed. Now "no peak in the exported song goes above -3 dBFS".
5. Poster 25 (Mixer): the vocal's pan knob pointed right, which contradicted the Pan poster (vocal at center). Now centered.

## Notes (not blocking)
- Poster 1: the TIMELINE label sits close to the ruler numbers.
- Poster 20: a gridline passes through the "ceiling -3 dBFS" label.
- Word wall sheet 3: column widths are slightly uneven.

**Verdict: APPROVED**
