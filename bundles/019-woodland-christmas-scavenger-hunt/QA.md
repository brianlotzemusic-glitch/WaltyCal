# QA: 019 Woodland Christmas Scavenger Hunt (round 1)

**Verdict summary:** the pack is close: clue logic, rhymes, layout and listing copy are sound. One real defect: three clue cards print a picture that gives the answer away, which contradicts the "No spoilers" promise, LISTING.md notes and image 3/4 copy.

## Checked myself (OK)
- `python3 gen.py --check`: ALL CHECKS PASS (no files changed in git afterwards).
- ZIP: only 2 PDFs + README-LICENSE.txt. Both PDFs 8 pages (Letter 612x792, A4 594.96x841.92), all fonts embedded, 0.3 MB each. README page map matches pages (1 how to play, 2 key, 3-6 cards, 7 blanks, 8 tracker).
- Contact sheet (70 dpi, all 8 Letter pages) and listing images 1-4 (3000x2250): nothing clipped, margins safe, cut lines present, white card backgrounds (low ink). 100% crop of the answer key: text is legible. Thumbnail is strong (plum band, wood, real cards, "15 rhyming clues" badge) and passes the scroller bar.
- Clue logic: 15 distinct spots A-O, each key row matches its card's rhyme (tree, oven, fridge, mitten drawer, bed, bathtub, boots, couch, bookshelf, washing machine, window sill, doormat, pantry, toy box, stockings). The chain rule (hide each clue where the previous clue points; clue 1 handed out; treasure at last spot) is consistent between page 1, README, key and description. No rhyme names its own answer. Rhymes scan; only N ("in / in") is a weak identical rhyme (optional). Safety copy present (oven handle, bathtub dry, washing machine on top).
- Listing: title 136 chars, leads with "Christmas Scavenger Hunt"; 13 unique tags, longest 19; correct non-cut-file disclosure line is last; taxonomy 1350, price 3.5, digital_file, who/when fields right. LISTING.md matches listing.json. Counts in copy (15 cards, 1 treasure, 4 blanks, 8 pages x 2 sizes) match the files.
- No IP: original rhymes and reused approved code-drawn icons; no brands, characters or lyrics.

## Must fix
1. **Answer-revealing icons.** The icon on three cards is a picture of the answer: **A** (Christmas tree card shows a pine tree), **D** (mitten and hat drawer card shows a red mitten), **O** (stockings card shows a red stocking). Pre-readers can solve these from the picture alone, so "no spoilers / big pictures that don't give it away" (LISTING.md notes, images 2 and 3 "No spoilers: answers only on the key page") is false for them. Reassign those three to non-literal woodland icons (e.g. A: robin or hedgehog, D: lantern or pinecone, O: acorn or wreath, keeping all 15 icons distinct and none literal to any other card's spot; the tree/mitten/stocking icons can go on other cards that do not match them, or onto the blank cards). Rebuild both PDFs, answer-key icons, ZIP, and re-render listing images 1, 3 and 4 (image 1 hero card A shows the tree; images 3 and 4 show A, D, O).
2. Add a check to `gen.py` that no card's icon name appears in its own spot name (it would have caught this).

## Optional
- Card N rhyme: replace "dig right on in / welcome you in" with a true rhyme.
- Spec: add to `formats/bingo.md` that scavenger-hunt icons must not depict the hiding spot.

## Would I pay $3.50?
After fix 1, yes. Cute, well-laid-out, easy to run.

**Verdict: REJECTED**

---

# Round 2

Re-review after the Designer's fix commit 0fcba35 (cards A, D, O reassigned, checks added to `gen.py`).

## Checked myself (OK)
- `python3 gen.py --check`: ALL CHECKS PASS, including the new "no card's icon pictures its own hiding spot" and "no printed icon (cards, blanks, treasure) pictures any hiding spot" checks (no files changed by the check).
- Icon audit, all 15 + treasure + blanks (from clues.json and the contact sheet): A tree = hedgehog, B oven = cocoa mug, C fridge = snowman, D mitten drawer = acorn, E bed = moon, F bathtub = robin, G boots = sled, H couch = fox, I bookshelf = owl, J washing machine = scarf, K window sill = bird house, L doormat = cabin, M pantry = squirrel, N toy box = rabbit, O stockings = bear; treasure = gift; blanks P-S = holly, pinecone, star, lantern. All 15 distinct, none pictures its own or any other hiding spot (tree, mitten and stocking icons are no longer used on clue cards). Pictures are no longer literal answers; the spoiler defect from round 1 is fixed.
- Rebuilt after the fix: clues.json 22:27; ZIP, both PDFs inside it, contact sheet and all four listing images 22:28; ZIP holds exactly Letter PDF, A4 PDF and README. Both PDFs 8 pages, correct sizes, fonts embedded, every clue's first line and spot present in the text.
- Low-res contact sheet (card icons): new A hedgehog, D acorn, O bear render cleanly. Listing image 1 (hero card A now a hedgehog, other cards fox and owl), image 3 (A hedgehog, D acorn on the A4 sample) and image 4 (all 15 plus treasure, hedgehog/acorn/bear on A/D/O): no tree, mitten or stocking left, nothing clipped, text legible, thumbnail still strong.
- Everything else from round 1 (clue logic, rhyme scansion, safety copy, listing fields, no IP) is unchanged by the fix.

## Optional (not blocking, carried over)
- Card N rhyme "in / in" is a weak identical rhyme.
- Add the "icons must not depict the hiding spot" rule to `formats/bingo.md`.

## Would I pay $3.50?
Yes. Cute, well-laid-out, easy to run, and the no-spoiler promise now holds.

**Verdict: APPROVED**
