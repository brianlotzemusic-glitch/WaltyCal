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
3. For each product this shift owes:
   1. Take the top unchecked queue item that is in season (see "Season rule"). Its id is the highest `tpt/NNN-*` number + 1.
   2. **Builder agent**, brief below.
   3. **QA agent** (a different agent), brief below.
   4. If QA rejects: one **fix agent** (fresh, gets only QA.md's required fixes and the folder), then QA again. If it is
      rejected a second time, leave it unreleased, log it as HELD and move on. No third round, no Opus.
   5. If approved: write `tpt/NNN-slug/release` containing the date and "released". Tick the queue line. Add one LOG line.
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
- **Titles** ≤ 80 characters, plain search words first (holiday, format, clefs or grades). **Tags** 1–6 exact entries from `tpt/TAG-OPTIONS.json` (the uploader rejects anything else; the old guide's "High School" and "Technology" are not tags),
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
3. Nothing clipped, overlapping, unreadably small or blank; the preview is watermarked; the cover reads at thumbnail size.
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
