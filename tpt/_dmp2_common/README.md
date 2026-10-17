# Shared builder for the DMP2 kits

`dmp2.py` builds one DMP2 project kit (the owner's Digital Music Production 2 course) the same way every time. First used by
`tpt/014-dmp2-billboard-top-10/`. Copy that kit's `gen.py` to start the next one.

## What a kit's gen.py holds

Only content, as module-level names, then `dmp2.main(sys.modules[__name__])`. Run it the usual way:

    python3 gen.py            # build everything
    python3 gen.py --lowres   # quick self-check build (small images; --check rejects it)
    python3 gen.py --check    # verify

| Group | Names |
| --- | --- |
| Product | `LIVE` (optional; `True` when the kit is already on TpT, so its `uploaded`/`release` files are allowed), `ZIP_EXTRA` (optional list of extra files for the ZIP, each under 90 MB), `REFLECTION` (optional, default `True`), `HERE`, `SLUG`, `TITLE`, `ACCENT`, `ACC_LIGHT` (one accent per product), `PRICE`, `CLASSES` (7), `GRADES_TEXT` / `GRADE_SLUGS` (optional; default and only accepted value 9–12 / 9th-12th, per METADATA-GUIDE), `TAGS`, `ANSWER_KEY` (`"Included"` or `None`), `ZIP_DIR`, `ZIP_DATE` |
| Listing | `LISTING_TITLE` (<= 80, "Logic Pro" in the first 30), `DESC_START` (first words of the description), `DESC_MUST` |
| Owner's sheet | `PROJ_LINE`, `TYPE`, `OVERVIEW`, `GOALS`, `VOCAB`, `REQS`, `STEPS`, `TIPS`, `CHECK`, `RUBRIC` (category, [descriptor per level]), `LEVELS`, `RUBRIC_TOTAL`, `RUBRIC_NOTE`, `RUBRIC_SHORT` (deck) |
| Owner's teacher notes | `TN_REINFORCES`, `STRUGGLES`, `VAR_EASY`, `VAR_HARD`, `RESOURCES` (owner item, what the kit gives instead), `TN_NOTE`, `PACING`, `GRADING` (only lines about the owner's rubric; each must say "rubric"), optional `GRADING_TIPS` (the kit's own suggestions, printed under the label "Suggestions from this kit, not part of my rubric:") |
| Disclosure | `CHANGES` (every wording change), `CHANGES_MUST_MENTION`, `KEPT`, `NEW_MATERIAL` |
| Deck | `SLIDES` = (class, kind, title, body, notes); kinds: title, listen, bullets, days, steps, pic, check, rubric, closer. `DRAWINGS` (name -> function returning (svg body, w, h); must include `hero`), `DRAWING_PX`, `SIDE`, `DECK_STRAP`, `RUBRIC_SLIDE_LINE` |
| Pages | `PLAN` (page keys, cover first, terms last, must include `changes`), `PAGES` (custom page builders), `PREVIEW_PICKS` (4), `SHOTS1/2/3` (preview images) |
| Cover | `COVER_A`, `COVER_C`, `PDF_COVER`, `SQ_COVER`, `SQ_B_LINES`, `SQ_SUB`, `SQ_HEADS`, `SQ_BANDS` |
| Hooks | `verify_content()`, `verify_outputs(page_texts, slide_texts, notes)`, `check_summary()`, optional `label_extras()` |

`PACING` is a list of dicts: `n` (class), `owner` (the owner's own line, or `None` to share the row above, as in "Classes 3–5"),
`do` (teacher moves, naming its slides), `slides` ((first, last) or `None`), `pages` (student page keys), `deck` (one line for the
"days" slide).

Standard pages: `pacing`, `tn1`, `tn2`, `changes`, `proj1`–`proj3` (the owner's sheet in 3 pages), `rubric`, `vocab`, `present`
(feedback planner), `logicref`, `terms`. Write `@KEY` (a page key in capitals) in any text to print that page's number.

## Reflection (standard element, on by default)

The owner's rubric (Documentation & Presentation) mentions reflection, but the project sheets have no reflection task. The owner's
definition (17 Oct 2026): **reflection is a written or oral conversation about how the student did on the project and what they
would do differently next time.** Every DMP2 kit therefore carries, with no content to write:

- a student page, key `reflect` (`reflect_page`): the definition, a choice of **written** or **oral**, four prompts (what went well,
  what was a struggle, what to do differently next time, which rubric category is strongest and weakest) on ruled lines that fill the
  page, and a box where the teacher notes an oral reflection. Hudson Beat look, the kit's accent. Prompts live in `REFLECT_PROMPTS`.
- a teacher note on teacher notes 2 (`reflect_tn`, headed "Reflection · added by this kit"): no points, no rubric row, evidence for
  Documentation & Presentation, about 10 minutes after the presentations.
- a pacing line in the last class and the page in its "Student pages" column (`reflect_do`).
- a Reflection box and speaker-note sentence on the deck's closing slide (no new slide, so slide numbers do not move).
- a standard sentence on the "What changed" page (`REFLECT_CHANGE`: the rubric mentions reflection, the sheet has no reflection task,
  this kit adds one by the owner's definition) and one in "New in this kit" (`REFLECT_NEW`).

A kit lists `"reflect"` in `PLAN` right after `"present"` (kits that print `len(PLAN)` at import time must, because `main()` only
inserts it before `terms` when it is missing). `REFLECTION = False` turns the whole element off. The kit's own text must not call
the rubric's reflection wording an open question. The /25 rubric is never touched. `--check` verifies every part above. The added
text can push a page over; per-kit knobs: `TN2_SIZE` (teacher notes 2, default 10.9 pt with reflection), `CHANGES_SIZE` (default 11.2 pt),
`PACING_SIZE` (pacing "teacher moves" column, default 10.4 pt).

## What --check enforces (for every kit)

- PDF: page count, US Letter, footers and page numbers, no overflow, no clipped text, no dead space (> 200 px), page and slide
  references exist, no unfilled `@KEY`, cover lines whole (no orphaned word), never "word for word".
- The owner's words are printed on their pages (every word of 6+ letters of every list item), the rubric total appears three times.
- Pacing: classes 1..N; every slide in exactly one class slot that matches the slide's Class badge; teacher moves only name slides in
  their own slot.
- Deck: notes (120+ characters) and a visible "Class N" on every slide, shapes inside the slide, Oswald and Source Sans text fits its
  box, no overlapping text boxes, text clear of filled boxes and pictures; deck PDF 16:9 with the right page count.
- Drawings: every label fits its room; labels on one row do not overlap.
- Files: ZIP holds exactly the PDF, .pptx and deck PDF plus any `ZIP_EXTRA` files (current copies, no audio or sessions, extras under 90 MB); preview 4 watermarked pages; images
  2000 x 2000; only Oswald/Source Sans 3, embedded.
- No unlabeled additions: the kit's grading tips print under their label; never claim "word for word", "word by word",
  "word-for-word" or "verbatim" (PDF, deck text, speaker notes, description). When the deck shortens the owner's wording (a step as short
  slide lines), say "shortened" in the notes and list it in `CHANGES`.
- Banned strings anywhere (school name and initials, the LMS name, the owner's unsellable audio titles) plus `BANNED_EXTRA`.
- `tpt.json`: current, proven values only (grades exactly 9th-12th, tags from 001-013, format PDF, answer key "Included" or absent);
  `UPLOAD.md`: title block and exact character count, SEO opening, disclosure line last; no `release` or `uploaded` file.

Each kit adds its own checks in `verify_content()` (owner list counts, music arithmetic, songs named) and `verify_outputs()`.
