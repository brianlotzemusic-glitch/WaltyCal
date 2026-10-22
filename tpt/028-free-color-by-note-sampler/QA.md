# QA: TpT 028 FREE Color by Note Sampler

QA date: 22 Oct 2026. Independent review of the built files (not released).

**Verdict: REJECTED** (one small, mechanical fix; everything else passes)

## Required fix
1. `tpt.json` has `"tags": []`. `tools/tpt.js` `checkItem` and the Manager's release gate both require 1-6 tags, so the item can never pass the gate or the uploader's validation. Set at least one TpT-approved tag. The only tags proven on TpT's list are Halloween, Autumn, Winter, Thanksgiving. The pictures (sunflower, acorn, apple basket) are autumn imagery, so `"tags": ["Autumn"]` is honest. Update UPLOAD.md section 9 item 5 and section 4 text to match. No other change needed; re-QA is a 1-minute check.

## Free-listing blocker (tools/tpt.js): CONFIRMED, publishing a free item is NOT possible by the nightly uploader today
- `tools/tpt.js` never references `free`/`item-free`. The "prices" step does `page.locator(F.price).fill(...)` then `F.license_price.fill(...)` from `tpt.json` and nothing else. `tpt/FORM.json` has no selector for the Free checkbox; it exists only in `tpt/FORM-FIELDS.json` (button `#item-free`, hidden checkbox `data[Item][free]`, label "Free Resource").
- `checkItem` accepts price "0.00" (regex `^\d+(\.\d{2})?$`), so validation would pass, and the run would reach the form. Whether TpT then rejects a 0.00 typed price or disables the price boxes once Free is unticked cannot be told from the repo; either way the listing would not be created as a Free Resource and could fail or be priced wrongly. `tpt.json` `"free": true` is ignored.
- Minimum fix (not made, tools/tpt.js untouched): add `free: "#item-free"` to FORM.json and, before the prices step, if `it.free` click `#item-free` and skip filling price/license_price (check `aria-checked`), else behave as now. Otherwise the owner uploads 028 by hand (~5 min, UPLOAD.md is in form order). The Manager should not release 028 for the nightly until that is fixed, or should accept that the owner uploads it manually. No `release` file was written; the uploader was not run.
- Last run (`tpt/UPLOADER-STATUS.json`, 22 Oct 00:30Z): ok false; 027 failed on TpT's "Seasonal Titles" notice (it may exist on TpT; check My Products before retrying). Not 028's problem, but it confirms why 027 has no URL.

## Checks passed
- **Colour-by-code.** `gen.py --check` passes (3 worksheets, 3 keys, 34 regions, 49 symbols; keys derived from printed symbols). I re-decoded independently, computing each note's letter from its staff step (treble bottom line E4; bass bottom line G2) rather than the stored letter: every symbol in a region maps to one key entry; 0 mismatches.
  - A sunflower: eighth=orange (5 petals), quarter=yellow (5), half=blue (sky), whole=brown (centre), quarter rest=green (4: leaves, stem, grass). Matches the key page.
  - B acorn (treble): A orange, G green, D yellow, C brown, E blue. Matches.
  - C basket (bass): F green, B yellow, D brown, C blue, E red (2 apples). Matches.
- **Notation.** Clef placement, ledger lines (middle C etc.), stem direction (up below the middle line, down on/above) and rhythm glyphs are correct. Helper lines "E G B D F / F A C E" and "G B D F A / A C E G" are right. Every colour is also written as a word, so B/W printing works.
- **Layout (viewed at 70-80 dpi and the cover).** Header, tag, key cells, symbols and cover are legible and clean; cover title is large at thumbnail size; grades/levels band is on one line. Style follows STYLE.md.
- **"See the full set" page (page 5).** 001 links its real live URL, identical to `001-halloween-color-by-note/uploaded` (…-17837169). 027 links only the store page https://www.teacherspayteachers.com/store/brian-lotze, with no invented product URL (honest, since 027's upload failed). "58-page download" matches 001's 58 pages (and 027's). "Winter ... are coming" is a soft claim, acceptable. Terms (single classroom, password-protected class site, no public posting/resale/editing), credits (Bravura, Oswald, Source Sans 3, OFL), Q&A-tab contact (no email) and the AI disclosure line are all present and match STYLE.md section 6.
- **Trademarks.** None; no songs or characters. Page-count claims are consistent (5 pages, 3 worksheets, 1 key page, 1 info page).
- **tpt.json.** Valid JSON, price/license_price "0.00", `free: true`, 4 grades, 1 subject, tax_code set, all 7 files exist, title under 80 chars (apart from the tags problem above).

## Nits (not blocking)
- Answer-key page 4: the Level C picture runs down to the footer rule (the picture's bottom frame touches it), and the three keys sit in a narrow left column with empty space on the right. Shrinking the keys slightly or putting two columns would look cleaner. Optional.
- Description says "grades 1-5" while tpt.json lists 1-4 (TpT limit); UPLOAD.md already explains this.

## Open owner questions (do not block)
Free checkbox in the uploader (above); 027 product URL for page 5 once live (then rebuild and re-upload); logo beside HUDSON BEAT; eyeball the three keys.
