# TpT factory (lean), started 12 Nov 2026

The owner's order (12 Nov 2026): **TpT only.** Etsy, Printify, AI art, the dashboard, the watchdog, research/scout/analyst/trend
agents, status.json and weekly reports are all gone. `FACTORY.md`, `queue.md`, `office/` and `log/` are an archive: never read
or update them. This file, `tpt/QUEUE.md` and `tpt/LOG.md` are the whole system.

Store: Hudson Beat by Brian Lotze on Teachers Pay Teachers. What sells, per the owner: color-by-note sets and the Logic Pro
project kits.

## Daily output (Eastern day)
- **3 classroom products** (2 is acceptable if one fails QA), from `tpt/QUEUE.md` "Classroom".
- **1 holiday-themed Logic Pro project kit**, from `tpt/QUEUE.md` "Holiday Logic kits". Every day.
- Bundles from `tpt/QUEUE.md` "Bundles" when their condition is met. A bundle takes a classroom slot.

Two shifts: **5:42am** builds 2 classroom products. **1:42pm** builds the Logic kit first, then classroom products until the
day has 3 (at most 3 builds in one shift, so a missed morning is partly caught up). Count today's builds from `tpt/LOG.md`.

## A shift, step by step
The dispatcher (the session that receives the shift prompt) stays small. It reads only this file's sections it needs, the top
of `tpt/QUEUE.md`, the last 6 lines of `tpt/LOG.md` and `tpt/UPLOADER-STATUS.json`. All building and checking happens in
subagents, **all on Sonnet** (`model: "sonnet"`), run in the **foreground, one at a time**.

1. `git fetch origin shop-factory && git checkout -B shop-factory origin/shop-factory`
2. Uploader check (see "The Mac uploader"). One line in LOG if something is wrong.
   Then **fixes first**: take unchecked `- [ ] [fix]` lines at the top of `tpt/QUEUE.md`, at most 3 per shift, before the day's builds; they
   do not count toward them. Lines marked `- [~]` belong to the fix crew (`tpt/FIX-CREW.md`): never touch them. Procedure for a defect in a LIVE product (owner reports it, or QA/the live check finds it):
   1. Fresh Sonnet agent. First read that item's section of `tpt/AUDIT-2026-11-15.md` (or the owner's report) and **look at each
      listed defect yourself in the current files**; a defect you cannot see is a false alarm: say so and leave it. Fix the real
      ones in the item's `gen.py` (the source, never only the output), rebuild with `python3 gen.py`, run `python3 gen.py --check`.
      Fix P1 and P2 items; fix P3 ones only if cheap. A drawing flaw shared with other kits (same function copied around) is fixed
      in each affected kit in the same run when it is listed. Reply in 8 lines: fixed, false alarms, not fixed and why.
   2. Fresh Sonnet agent as **Visual inspector** (brief above, on that folder, covering every image and every PDF page the fix
      touched, at full size). It must also confirm each defect listed for that item is gone and nothing new appeared. Only then
      rewrite `QA.md` with `**Verdict: APPROVED**`; DEFECTS means one more fix round, then leave it and log it HELD.
   3. Write `tpt/NNN-slug/reupload` (date and one-line reason). Your Mac's next run replaces the files in the live listing
      (`tools/tpt.js reupload-pending`; title, price, description and tags are never touched) and writes `reuploaded`, or
      `reupload-failed` with the reason. Next shift, read which; on `reupload-failed` treat it like a held upload.
      While `tpt/REUPLOAD-PAUSED` exists the marker waits (see "The Mac uploader": canary rule). For product 001 only `reupload`
      is ever allowed; for the others the canary rule may turn the marker into `republish` (a new listing, old one deactivated).
   4. Tick the `[fix]` line, add one LOG line, commit and push.
3. For each product this shift owes:
   1. Take the top unchecked queue item that is in season (see "Season rule"). Its id is the highest `tpt/NNN-*` number + 1.
   2. **Builder agent**, brief below.
   3. **QA agent** (a different agent), brief below.
   3b. **Visual inspector** (a third fresh Sonnet agent that did not build or QA it; brief "Visual inspector" below). It must reply
      `OK` before release. `DEFECTS` counts as a QA rejection: same single fix round, then the inspector again, then HELD.
   4. If QA rejects: one **fix agent** (fresh, gets only QA.md's required fixes and the folder), then QA again. If it is
      rejected a second time, leave it unreleased, log it as HELD and move on. No third round, no Opus.
   5. If approved: run `python3 tools/tpt-validate.py tpt/NNN-slug`. It must print OK; if not, one fresh Sonnet agent fixes
      `tpt.json` (and the `TAGS`/`SUBJECTS` lines in `gen.py`), then run it again. Only then write `tpt/NNN-slug/release`
      containing the date and "released". Tick the queue line. Add one LOG line.
   6. Commit and push (message ends with the Co-Authored-By and Claude-Session lines your environment gives you).
      Push rejected as non-fast-forward: fetch, merge (no rebase), push. Never force-push.
4. Reply in 3 lines: built, held, what's next. Nothing else.

Push notifications to the owner: only the three cases under "The Mac uploader", only 8am–8pm Eastern, at most one a day.

### Builder brief (copy, fill in the brackets)
> Build TpT product `tpt/[NNN-slug]/`: [queue line]. Read `TPT-FACTORY.md` "Product rules" and `tpt/STYLE.md` first.
> Start from the closest existing item and copy its `gen.py` structure: color by note → `tpt/029-winter-color-by-note`;
> bingo → `003`; task cards → `006`; worksheets → `027`; sub plans → `007`; planner/trackers → `005`; Logic kit →
> `tpt/025-dmp2-royalty-free` + `tpt/_dmp2_common/README.md`.
> Deliver in the folder: `gen.py` (builds everything; `--check` verifies every answer and the layout), the product PDF, a
> 4-page watermarked preview PDF, `cover.png` (2000×2000), `preview-1..3.png`, `UPLOAD.md` and `tpt.json` (formats in
> `tpt/README.md`). Everything is drawn in code: no AI image tools, no downloaded art. Missing Python module: pip install it.
> Run `gen.py` and `gen.py --check` until clean, then look once at low-resolution renders (60–100 dpi) of every page.
> Don't commit. Don't touch other folders, except that a Logic kit may extend `tpt/_dmp2_common/dmp2.py`.
> Reply in at most 8 lines: what you made, page count, price, open questions.

### QA brief
> Review `tpt/[NNN-slug]/` independently; you did not build it. Read `TPT-FACTORY.md` "QA checklist".
> Run `python3 gen.py --check`. Render every page at low resolution and look at all of them. Recompute every answer key
> yourself. Read `UPLOAD.md` and `tpt.json`. Write `QA.md`: findings, then one line `**Verdict: APPROVED**` or
> `**Verdict: REJECTED**` followed by the numbered required fixes. Only reject for things a buyer would notice or that break
> a rule. Don't fix anything yourself. Reply in at most 8 lines.

### Visual inspector brief (copy, fill in the folder)
> You inspect the artwork of TpT product `tpt/[NNN-slug]/`. You did not build it and you did not do its content QA: do NOT read
> `QA.md` or `gen.py` first, because their claims would bias you.
> 1. With the Read tool, look at EVERY image at full size, one at a time: `cover.png`, `preview-1.png`, `preview-2.png`,
>    `preview-3.png`. For a new build also render the product PDF at 110 dpi (`pdftoppm -r 110 -png file.pdf /tmp/x`) and look at
>    every page, and at all 4 pages of the `-PREVIEW.pdf`. Never judge from a thumbnail or a contact sheet.
> 2. For each image write an INVENTORY line saying exactly what is on it: the title text as printed, every drawn object, and every
>    piece of music notation (clef; each note and rest by type and staff position; stems; flags and beams; barlines; time
>    signature). If you cannot describe it exactly, look again.
> 3. Then list DEFECTS. Assume at least one exists and hunt for it. Check (a) notation: stems on the correct side of the head (right
>    edge going up, left edge going down), stem direction (down for notes on or above the middle line, up below it), heads filled
>    or open to match the note named, flags and beams, rests, bars that add up to the time signature wherever one is shown;
>    (b) anything overlapping, touching or colliding (a dot on a clef, text on art); (c) clipped or cut-off text or art, text too
>    small to read at thumbnail size, typos, claims that disagree with the product (page, puzzle or grade counts; check
>    `UPLOAD.md` only now); (d) blank areas, broken images, artefacts; (e) anything a teacher would find odd or unprofessional.
> 4. Reply `OK` only if every image has an inventory line and you found nothing. Otherwise reply `DEFECTS:` with the image, where on
>    it (top-left, centre...) and what is wrong. At most 12 lines.

## Product rules
- **Brand and look:** `tpt/STYLE.md`. Footer and terms page as written there.
- **Disclosure line**, in the description and on the terms page: "Created with the help of digital and AI tools. Notation and
  answer keys are verified before release." Never say handmade, hand-checked or classroom-tested about a new product.
  The templates and `dmp2.py` still carry the old line ("…and checked by hand"): replace it in every new product, and make
  `dmp2.py` use the new line when `ORIGINAL` is set. Don't edit or rebuild live products for this.
- **Music must be right.** Note values add up to the time signature; stems, beams, clefs and staff positions are correct;
  rhythm syllables match; every answer key is computed in code and verified by `--check`.
- **Tunes: public domain only.** In 2026 that means first published in the US in 1930 or earlier (1931 from 1 Jan 2027).
  Write the tune's year and source in QA.md. No lyrics unless they are public domain too. Never: Rudolph, Frosty, the Grinch,
  Santa Claus Is Comin' to Town, Jingle Bell Rock, Feliz Navidad, any film or pop song, any character or brand. "Carol of the
  Bells": the 1916 melody only, no English lyrics.
- **Public schools buy these.** Winter and secular options alongside Christmas, Hanukkah and Kwanzaa ones; describe religious
  and cultural holidays accurately and respectfully, and keep facts checkable.
- **Never copy another seller's product.** Take the format and subject only.
- **Titles** ≤ 80 characters, plain search words first (holiday, format, clefs or grades). **Headings are not choices.** TpT's Subject and Tag menus mix category headings in with the real entries, and picking a heading wipes the field and stops the upload (13 Nov 2026: subject "Performing Arts", tags "Holiday" and "Student Practice"). Safe subjects: Music, Instrumental Music, Music Composition, Computer Science - Technology. Safe tags that have published: Winter, Autumn, Thanksgiving, Halloween, Christmas-Chanukah-Kwanzaa, Worksheets, Printables, Activities, Unit Plans, Project-based Learning, Projects, Career and Technical Education. `tools/tpt-validate.py` rejects headings. **Tags** 1–6 exact entries from `tpt/TAG-OPTIONS.json` (the uploader rejects anything else; the old guide's "High School" and "Technology" are not tags),
  **grades** 1–4, **subjects** 1–3 from `tpt/SUBJECT-OPTIONS.json`.
- **Prices:** classroom $3–5 (sub plans and units up to $7); holiday Logic kits $7–9; free items $0 only when the queue says so.

### Holiday Logic kits
- Same format as the owner's DMP2 kits (`tpt/014`–`026`): project sheet, rubric, vocabulary, teacher notes with pacing,
  reflection page, Logic Pro reference page and a teacher-presented intro deck (PDF + PPTX), zipped. High school, 2–4 class
  periods. No audio or Logic project files ship; students make everything.
- These are **original Hudson Beat projects**, not the owner's course sheets. The first one adds an `ORIGINAL = True` mode to
  `dmp2.py` that drops the "changes to the owner's sheet" page and its checks; later kits just set it.
- Metadata: `tpt/METADATA-GUIDE.md` (grades 9–12; "Logic Pro" in the first 30 characters of the title, as a compatibility word).
- **Logic Pro steps must be real.** Name only features that exist (Session Players/Drummer, Quick Sampler, Alchemy, Step
  Sequencer, Live Loops, Flex Time, Drum Machine Designer, Smart Tempo, automation). If unsure of a menu path, describe the
  action without the path.

### Bundles
One ZIP holding the member kits' files, plus its own cover, preview and a guide page (template: `tpt/030-dmp1-units-1-6-bundle`).
Price 25–35% below the sum. Never change or re-upload the member listings.

## QA checklist
1. `gen.py --check` passes, and every answer key recomputed by hand matches.
2. Music notation is correct on every page (see "Music must be right").
3. Nothing clipped, overlapping, unreadably small or blank; the preview is watermarked; the cover reads at thumbnail size. (The Visual inspector, step 3b, checks every image and page at full size; QA does not replace it.)
   **Look at the cover and every preview image again at FULL size** (2000 px; crop into any drawing), not only as a thumbnail.
   Any music notation in that artwork (a staff, notes, rests, clefs) gets the same checks as the pages: stems attached to the
   right edge of up-stem heads (left edge, going down, for down-stems), stems up below the middle line and down on or above it,
   flags and beams correct, nothing overlapping the notation. (042's cover shipped on 14 Nov 2026 with stems floating one
   note-width away from their heads: QA had looked at it only at thumbnail size and never checked its notes.)
4. Tunes are public domain, with year and source noted. No brands, characters or copied material.
5. Age and grade fit. Instructions a substitute could follow.
6. Listing: title ≤ 80, description matches the product exactly (page count, what's included), disclosure line present, price
   set, `tpt.json` valid: files exist, grades 1–4, every subject is in `tpt/SUBJECT-OPTIONS.json` and every tag is in `tpt/TAG-OPTIONS.json`, spelled exactly.
7. Logic kits: steps are real Logic Pro features, pacing adds up, the rubric total is right.

## Season rule
Build for holidays 2–8 weeks away. Don't build a holiday item fewer than 6 days before its holiday: mark it `[next year]` and
take the next one. Evergreen items are always in season; take one after every two holiday items so the catalogue isn't all seasonal.

## Queue refill
When fewer than 6 classroom items or fewer than 5 Logic kits are unchecked: one Sonnet agent appends 30 classroom or 15 Logic
ideas in the same one-line format (at most 6 web searches; more of what sells: color by note in new themes, Logic kits).

## The Mac uploader
TpT has no API, so `tools/tpt-nightly.sh` on the owner's Mac does the uploading. The owner wants to do nothing (12 Nov 2026),
so the job is forgiving: it runs at login, at 7:15, 9:45, 12:15, 15:15, 17:45, 20:30 and 22:15 Eastern, and after any wake
that missed one of those times. Each run pulls this branch, publishes every item that has `release` and no `uploaded` (up to
6 a run), and pushes the `uploaded` markers and `tpt/UPLOADER-STATUS.json`. A run with nothing to publish opens no browser.
The status file's `ran_at` is pushed at most once in 20 hours when nothing else changed.
The cloud never runs the uploader. `tpt/PAUSED` stops it; create that file only if the same failure hits 3 items.

Uploads lag whenever the Mac is closed or off. That is expected: don't hold builds back for it and don't tell the owner.

**The Mac's report can go missing.** On 12 Nov all four released products went live but the Mac's push to GitHub failed, so the
repo still said "waiting". So at the start of each shift run `python3 tools/tpt-live-check.py` (reads TpT's public store page,
needs no login). Every item it prints as `LIVE` is on TpT: count it as uploaded for bundle conditions and counts. **Never write
an `uploaded` file yourself**: the Mac owns those files, and one created in both places makes the Mac's next `git pull` fail.
`tools/tpt.js` also checks the store page before each upload and skips anything already live, so a lost marker can't cause a
duplicate listing.

At the start of each shift read `tpt/UPLOADER-STATUS.json` and act only on these:
- `needs_login` true → push the owner once: "TpT login expired. On your Mac run: source ~/.tpt-env && node tools/tpt.js login, then click Log in."
- `held` lists an item (its publish failed twice; `tpt/NNN/publish-failed` has the error) → one Sonnet agent reads the error
  and any screenshot under `tpt/_publish/`, fixes the item or `tools/tpt.js`, then rewrites that item's `release` file with
  new text, which re-arms it for 2 more tries. This replaces one classroom build that shift. If the same item is held a
  second time, leave it held and log it; don't try a third fix.
- `ran_at` is more than 3 days old (the Mac hasn't reported in 3 days) → push the owner once. The usual cause is the Mac's GitHub
  login: it can download but not upload, so its reports stay on the Mac (this happened 7–14 Nov 2026). Message: "The TpT uploader
  hasn't reported in 3 days. If your Mac was on, its GitHub login probably expired: in Terminal run `gh auth login`, then
  `gh auth setup-git`." If instead items are released more than 4 days ago and still `WAITING` in the live check while `ran_at`
  is fresh, the uploads are failing: handle them under `held` above.
- The Mac also shows its own notifications (login expired, can't push) at most once a day.

**Replacing files of live products (`reupload`) and the fallback (`republish`).** Since October the edit form has not taken a new
product file. 16 Nov evidence (007): the file reaches S3 and TpT processes it, then TpT's box shows "99% ... Error during file
upload, please try again" and clears the key. `tools/tpt.js` now retries up to 3 times per file (Cancel, upload again, the third
try through TpT's own Select-file chooser), waits until the box stops saying Processing, and on failure writes
`tpt/_publish/NNN-slug-reupload-<slot>-diag.json` (requests, TpT's upload answers, console errors, the box's HTML; the
`diagnostics` field of `reupload-failed` has the same in short). `tpt/REUPLOAD-PAUSED` stops every replacement; a line
`allow: 043` in it lets only the listed items through (the canary). **Canary rule, every shift while that file exists:** run
`python3 tools/tpt-reupload-canary.py status` and act on its word:
- `PASSED`: run `python3 tools/tpt-reupload-canary.py release` (deletes the pause file), commit and push. All waiting replacements
  run on the Mac's next runs (they stop at the first failure, so a new problem costs one item, not 28).
- `FAILED`, first time: one agent reads the canary's `reupload-failed` (the `diagnostics` field) and the diag file, fixes
  `tools/tpt.js` once, runs the offline tests (`node tools/test-tpt-editupload.js`, `node tools/test-tpt-reupload.js`), and re-arms the
  canary by adding one dated line to its `reupload` marker. Note "canary fix 2 tried" in LOG.md.
- `FAILED` again after that fix (LOG.md says fix 2 was tried): give up on the edit form. Run
  `python3 tools/tpt-reupload-canary.py convert`: every waiting item except 001 gets a `republish` marker (same text) instead of
  `reupload`, and the pause file is deleted. Commit and push. 001 keeps `reupload` (it has a sale; its URL must never change).
- `WAITING`: nothing; the Mac hasn't tried yet.
- `PAUSED-ALL` (no allow line): a person paused everything; leave it.

**`republish`** (`node tools/tpt.js republish-pending`, after reupload-pending, max 3 a run; never product 001): the Mac publishes
the item again as a NEW listing (the proven new-product form), saves the old `uploaded` as `uploaded-previous`, writes the new
`uploaded` and `republished` (JSON: old_url, new_url, old_deactivated), then opens the OLD listing's edit page, checks its title is
exactly the item's title (refuses otherwise), unticks "Make Listing Active", saves and checks. It never deletes a listing.
`republish-failed` with `"stage": "publish"`: nothing new went live (or, if the note says MAY exist, check My Products); write a
new `republish` text after fixing. With `"stage": "deactivate"`: **two listings are live**; the Mac retries only the
deactivation every run and never publishes a third copy. If it still fails after 3 tries (`tries` in the file), push the owner
once: "On TpT, open <old_url>, Edit, untick Make Listing Active, Submit." `UPLOADER-STATUS.json` `republish.two_listings_live` lists
such items. The old listing's reviews and sales stay on the old (inactive) page.

## Rotation (keeps usage low)
The dispatcher re-reads its whole conversation on every step. On the first shift of each month, after the builds, it starts
its replacement: `create_session` (claude-code-remote; load with ToolSearch) with source_url
https://github.com/brianlotzemusic-glitch/WaltyCal, source_revision `shop-factory`, model `claude-sonnet-5-5`, title
"TpT factory (Mon YYYY)", and a prompt that only syncs, pushes one LOG line and replies "ready". When that line is on the
branch, `create_trigger` with the same cron and prompt as the current shift routine (the enabled one named "TpT factory: shifts…" in `list_triggers`; read it with `get_trigger`) and
`persistent_session_id` = the new session, then disable the old routine. Log it.

## Never
Delete products, rewrite history, force-push, touch `main`, spend money, create accounts, handle passwords or tokens, contact
anyone for the owner, or run the uploader from the cloud.
