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
| Product | `HERE`, `SLUG`, `TITLE`, `ACCENT`, `ACC_LIGHT` (one accent per product), `PRICE`, `CLASSES` (7), `GRADES_TEXT`, `GRADE_SLUGS`, `TAGS`, `ANSWER_KEY` (`"Included"` or `None`), `ZIP_DIR`, `ZIP_DATE` |
| Listing | `LISTING_TITLE` (<= 80, "Logic Pro" in the first 30), `DESC_START` (first words of the description), `DESC_MUST` |
| Owner's sheet | `PROJ_LINE`, `TYPE`, `OVERVIEW`, `GOALS`, `VOCAB`, `REQS`, `STEPS`, `TIPS`, `CHECK`, `RUBRIC` (category, [descriptor per level]), `LEVELS`, `RUBRIC_TOTAL`, `RUBRIC_NOTE`, `RUBRIC_SHORT` (deck) |
| Owner's teacher notes | `TN_REINFORCES`, `STRUGGLES`, `VAR_EASY`, `VAR_HARD`, `RESOURCES` (owner item, what the kit gives instead), `TN_NOTE`, `PACING` |
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

## What --check enforces (for every kit)

- PDF: page count, US Letter, footers and page numbers, no overflow, no clipped text, no dead space (> 200 px), page and slide
  references exist, no unfilled `@KEY`, cover lines whole (no orphaned word), never "word for word".
- The owner's words are printed on their pages (every word of 6+ letters of every list item), the rubric total appears three times.
- Pacing: classes 1..N; every slide in exactly one class slot that matches the slide's Class badge; teacher moves only name slides in
  their own slot.
- Deck: notes (120+ characters) and a visible "Class N" on every slide, shapes inside the slide, Oswald and Source Sans text fits its
  box, no overlapping text boxes, text clear of filled boxes and pictures; deck PDF 16:9 with the right page count.
- Drawings: every label fits its room; labels on one row do not overlap.
- Files: ZIP holds exactly the PDF, .pptx and deck PDF (current copies, no audio or sessions); preview 4 watermarked pages; images
  2000 x 2000; only Oswald/Source Sans 3, embedded.
- Banned strings anywhere (school name and initials, the LMS name, the owner's unsellable audio titles) plus `BANNED_EXTRA`.
- `tpt.json`: current, proven values only (grades 9th-12th slugs, tags from 001-013, format PDF, answer key "Included" or absent);
  `UPLOAD.md`: title block and exact character count, SEO opening, disclosure line last; no `release` or `uploaded` file.

Each kit adds its own checks in `verify_content()` (owner list counts, music arithmetic, songs named) and `verify_outputs()`.
