# Fix crew instructions (owner, 16 Nov 2026: "fix all the defects the audit finds")

Six sessions run in parallel, each with its own list of products (given in your prompt). The defects are in `tpt/AUDIT-2026-11-15.md`
(one section per product). They are raw inspector findings: confirm each one yourself. Everything is drawn in code; no AI image tools.

## Setup
`git fetch origin shop-factory && git checkout -B shop-factory origin/shop-factory`. Install any missing Python module with `pip install`
(pillow, pypdf, fonttools, brotli, python-pptx, shapely, numpy, reportlab, pyyaml...). Node, Playwright and poppler are already there.

## For each product, in the order given
1. **Verify.** Look at each listed defect yourself, at full size, with the Read tool. Image defects: open the named image. A defect on a
   PDF page: render it (`pdftoppm -r 110 -f N -l N -png file.pdf /tmp/p`). If you cannot see it, it is a false alarm: write that down
   and leave it alone.
2. **Fix the source**, never only the output: the product's `gen.py` and its sibling modules (`notation.py`, `pictures.py`,
   `regions.py`). The same flaw copied into other kits is fixed in each kit that lists it. **P1** (wrong content) and **P2** (visible
   flaw) always; **P3** (polish) too, unless it needs a redesign. Do not edit `tpt/_dmp2_common/dmp2.py`, `TPT-FACTORY.md`, `tpt/QUEUE.md`,
   `tpt/LOG.md` or any product that is not yours. If a fix seems to need `dmp2.py`, patch inside the kit instead.
3. **Rebuild**: `python3 gen.py`, then `python3 gen.py --check` (must pass). `python3 tools/tpt-validate.py tpt/NNN-slug` must print OK.
4. **Inspect, with a different agent.** Spawn a fresh Sonnet subagent (Agent tool, `model: "sonnet"`) with the "Visual inspector brief"
   (`sed -n '/^### Visual inspector brief/,/^## Product rules/p' TPT-FACTORY.md`) for that folder. It must cover every image
   and every PDF page you changed, and confirm each defect you fixed is gone and nothing new appeared. DEFECTS -> one more fix round
   and a fresh inspector. Still failing -> do not queue the replacement; report it as HELD.
5. **Queue the replacement on the live listing.** Add a section to `QA.md` titled "Fix round 16 Nov 2026" (what changed, what the
   inspector confirmed) ending in `**Verdict: APPROVED**`. Then write `tpt/NNN-slug/reupload` containing the date and a one-line
   reason (`2026-11-16 fix: <summary>`). Your owner's Mac replaces the files in the live listing on its next run; it never touches the
   title, price, description, tags or grades, so a listing-text defect is fixed in `UPLOAD.md` for the record only.
   Never write or edit `release`, `uploaded`, `reuploaded` or `reupload-failed`.
6. **Commit and push** only that product's folder (`git add tpt/NNN-slug`; commit message ends with the Co-Authored-By and Claude-Session
   lines your environment gives you). Push; on rejection `git fetch origin shop-factory && git merge --no-edit origin/shop-factory`
   (no rebase), then push again. Never force-push. Push after EACH product so nothing is lost if you stop.

## Rules
- Never run `tools/tpt.js` (the Mac does the uploading) and never touch `main`.
- Keep your own context small: do the viewing inside the product, one product at a time, and don't paste long output.
- If a usage limit, a build failure you cannot resolve in two tries, or a missing tool stops you, write one line saying which product
  and why in your reply, then continue with the next product.

## Your reply (at most 12 lines)
Per product: FIXED (replacement queued) / PARTIAL / HELD / FALSE ALARM only, with what is left. Then one line on anything shared the next
session should know (a fix that applies to other kits).

## Notes for particular items
- **DMP2-style kits (014-026, 031, 036, 040, 045), deck slide "How it's scored":** in the kit's `gen.py` change `RUBRIC_SLIDE_LINE` to
  `"Scored 1–5 · final grade = average of your score and mine, out of 25"` (no stray dot before "/ 25") and raise `RUBRIC_LINE_Y` so
  the line sits clear of the footer rule (>= 0.12 inch). Rebuild the deck and inspect that slide.
- **Blank bands at the bottom of preview images (P3):** re-flow the preview image builder in the kit (larger thumbnails or one more
  row) so the image is filled; check all three previews.
- **Doubled PREVIEW watermark (027, 028, 029, 032, 035, 037):** find why the stamp is drawn twice (offset) in the preview pages of 027
  first, fix it, and apply the same patch to the other kits in your list.

## State at launch (16 Nov 2026, 12:45pm ET)
Already done by the daily shift: 043, 007, 002, 011, 012, 042 (replacements queued; the Mac's replace-files step was repaired in
`tools/tpt.js` and four were re-armed). 026 is HELD: its P1 fixes are in `gen.py`, spacing fixes remain (read the 026 line in `tpt/LOG.md`).
**045, 046, 047 are NEW products that were HELD** (QA approved, the Visual inspector found defects after the fix round was spent; read
their lines with `grep -n "04[567]" tpt/LOG.md`). For those three: fix what the log lists, have a fresh inspector confirm, and when it
reports OK and `tools/tpt-validate.py` prints OK, write `tpt/NNN-slug/release` (date and "released") instead of a `reupload` marker.
Everything else is a LIVE product, so it gets a `reupload` marker.
