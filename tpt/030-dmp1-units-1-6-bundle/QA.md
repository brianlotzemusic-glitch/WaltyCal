# QA: TpT 030 DMP1 Units 1-6 Bundle (round 1)

QA reviewed this item on 23 Oct 2026, independently of the Designer. Compared with the QA.md files of 008 and 013, FACTORY.md (TpT section, owner decisions 21 Oct 2026) and tpt/STYLE.md.

**Verdict: APPROVED**

## Checks
- **ZIP**: 19 entries (guide + 6 x PDF, .pptx, deck PDF), testzip clean, no extra files. SHA-256 of all 18 kit files equals the sources in tpt/008-013. Folder order and names: Unit 1 Beat From Nothing (008), 2 Stems and Grooves (013), 3 Chords by Ear (011), 4 Bass and Melody Writing (012), 5 Song Form (010), 6 Spooky Tunes (009). Matches UPLOAD.md.
- **bundle-guide.pdf**: 4 pages (cover, unit order and 29-period pacing table, folder map, terms), Letter, fonts embedded. Checked against the kits: days 4/6/5/4/4/6 = 29 and periods 1-4, 5-10, 11-15, 16-19, 20-23, 24-29 are right; each kit's pacing page says ~53-minute periods; page and slide counts (21+15, 28+22, 35+21, 30+22, 27+17, 31+16 = 172 + 113) match pdfinfo and python-pptx; the "Unit 1 can stretch to 5 days" and "Unit 5 can run in 3 days" notes exist in 008 and 010; the dependency claims (Unit 2 builds on Unit 1, Unit 4 on Unit 3 or a recipe file, Unit 5 arranges existing material, Unit 6 needs no key or form) match the kits' text. No Blind Brook or school branding, no audio, no third-party artist or album names in guide or preview (grep clean). Terms page follows STYLE.md section 6 with the disclosure line.
- **Look**: cover, preview-1..3 (2000x2000) and the 4-page preview PDF rendered at 100 dpi: Hudson Beat store line, Oswald caps, black band, single gold accent, white-to-grey fade (allowed for high school). Title readable at thumbnail size. Preview pages carry the PREVIEW watermark. No problems.
- **Price**: kit prices read from each tpt.json and UPLOAD.md: 9 + 12 + 10 + 12 + 10 + 10 = $63 (008 $9, 009 $12, 010 $10, 011 $12, 012 $10, 013 $10). $49 is $14 off, 22.2%, inside the 20-25% target. license_price 49.00.
- **Title** (78 chars) and description do not overclaim: Logic Pro stated as the platform, other DAWs only as "ideas carry over", no audio or sessions included, dependencies and "same files as the individual listings" disclosed, Apple trademark line and disclosure line present.
- **tpt.json**: valid; 4 grades, 3 subjects, 4 tags, price/license/tax_code set, all five `files` exist, `zip_contents` matches the ZIP, pages 289 = 4 + 172 + 113.
- **gen.py --check**: CHECK OK. **git**: no diff in tpt/008-013 (last commit touching them is older than the bundle commit).

## Flags (none blocking)
1. **"Back to School" tag**: weak for a late-October upload (the bundle includes a Halloween unit) and unproven. tools/tpt.js `pick` fails the whole publish if a tag is not an option, and the live kits only ever proved "Autumn" (013's QA). The Manager may drop it (keep High School, Project Based Learning, Technology); that costs nothing and removes a failure point. If tags fail on the first night, the fix is a tpt.json edit, not a rebuild.
2. The live kit listings use different (older) tags; harmless.

## Live status of the six kits
All six have an `uploaded` file with a TpT URL: 008 (12 Oct, confirmed by owner), 009 and 010 and 011 (14 Oct), 012 and 013 (15 Oct). The bundle does not need to wait. A live check of the six URLs (HTTP 200) was not done here (cloud proxy); the Manager's verify step covers it.

## Open owner questions (do not block)
- Native TpT Bundle of Resources later (tools/tpt.js cannot drive it yet). Optional: logo file for the store line.
