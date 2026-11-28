# QA: 093 Color by Note Growing Bundle

Independent review. `gen.py --check` and `tools/tpt-validate.py` OK before and after my fix.

## Recomputed myself (own script: each member's tpt.json, UPLOAD.md, PDF; ZIP unzipped by script)
- Members 001 027 029 032 035 039, all with `uploaded`. 001 has no `release` file (it predates the marker, went live by hand); acceptable for a bundle member since it is live (uploaded) and nothing in the uploader needs `release` here.
- Prices 3.50+3.75+3.75+4.00+3.50+4.00 = $22.50; bundle $15.00 = 33.3% off, saving $7.50; chip SAVE 33% (rounded down, within 30-35%). Each member PDF 58 pages (pdfinfo), 27 worksheets + 27 keys each (UPLOAD.md): 162 + 162; 348 + 4 guide = 352 (guide 4 pp, preview 4 pp).
- Numbered list in UPLOAD.md and the guide: grades match each member's UPLOAD.md (1-5, 1-5, 1-5, 2-6, 2-6, 2-5; union 1-6). Title "Gr 1-6" is therefore the real range of the members, not an overclaim; tpt.json has four boxes (2nd-5th) because TpT allows four, explained in UPLOAD.md section 3. Left as is. Names in the list are the themes (Fall, Christmas...), not the live store titles of 032/035/039 (which avoid holiday words); fine, the guide/folder names make them identifiable.
- ZIP: 7 files (guide + 6 folders, one PDF each), all six PDFs sha256-identical to the member folders' PDFs, clean names, no work files, 9.8 MB decimal (9.5 MiB). Each member's UPLOAD.md lists the PDF as its only customer file; nothing omitted.
- Listing: title 77 chars, starts "Color by Note Growing Bundle" (theme + Bundle first, per the factory manual), no holiday/season word. Price "15.00". Tags Halloween, Thanksgiving, Christmas-Chanukah-Kwanzaa, Winter, Printables, Activities each checked individually as exact entries in TAG-OPTIONS.json. Description: buyer's problem first, numbered members with pages and grade, $7.50 saving, "also sold separately", US spelling, disclosure line.
- Growing wording. Sources: TpT Help Center article "How do I notify Buyers when I update or revise a resource?" (help.teacherspayteachers.com/hc/en-us/articles/360042472592; direct fetch returned HTTP 403, content confirmed through web search result: upload a revised file, tick "Notify Buyers", describe the change; past buyers see a notification on My Purchases). Seller blogs (shaynavohs.com "What is a growing bundle on TpT?", fetched) confirm buyers re-download updates free from My Purchases and the price rises as items are added. The UPLOAD.md re-upload note matches the article.

## Defects found and fixed in gen.py
1. The listing, guide and cover over-promised: "new sets will be added", "planned", and "we use Notify Buyers" contradicted "no specific sets or dates are promised". Reworded to "We plan to add more color-by-note sets over time, but no set or date is promised. If a set is added, the price goes up... Today's price is the lowest the bundle will be", "can use Notify Buyers"; cover chip now "More sets may follow. Price rises as sets are added." Check needles updated. Nothing promises future sets at today's price.

## Viewed
Guide pages 1-4 at 110 dpi; the 4 preview-PDF pages (guide 1, guide 2, Winter Level B cardinal, Hanukkah Level C answer key; one PREVIEW watermark each); cover.png (edges clean, six member covers readable and uncropped, chips legible); preview-1, -2, -3 at full size. Notes only: cover says "348 PAGES" (member pages; 352 with guide, stated in the listing); preview-1 grid has uneven vertical spacing and preview-2 has empty space at the bottom; guide pages 2-4 have blank lower areas.

**Verdict: APPROVED**
