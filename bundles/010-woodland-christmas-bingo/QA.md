# QA: 010 Woodland Christmas Bingo (round 1 of 2)

**Verdict: SEND BACK.** The bundle is close. The cards, icons and thumbnail are strong. Three things a buyer would notice need fixing first: the markers don't work and don't match the photos, "ties are rare" isn't true, and there is no tie rule. All of them are quick to fix.

## What I checked myself (all OK)
- **PDFs** (pdfinfo, pdffonts, pdfplumber): both files have 20 pages. Letter is 612×792 and A4 is 594.96×841.92. All fonts are embedded and subset: Fraunces, Nunito, plus a DejaVuSans fallback for the ✂ glyph, which is embedded and fine. Each file is 1.6 MB. Card numbers run 01–30 in order, 2 per page.
- **Cards** (my own check of `cards.json`, not just `gen.py --check`): 30 distinct icon sets and 30 distinct layouts. FREE is at index 12. Every card has 24 distinct icons and every icon is on exactly 24 cards. 0 of the 360 winning lines are shared. Spot checks of Card 01 (PDF) and Card 07 (image 4) against `cards.json` match cell for cell. `gen.py --check` prints ALL CHECKS PASS.
- **ZIP**: holds only the 2 PDFs and README-LICENSE.txt. The README page map matches the PDFs.
- **listing.json**: title is 134 characters, leads with "Christmas Bingo", and has 0 words starting with 2 capitals. It has 13 unique tags, the longest 20 characters. There are no HTML entities, and the disclosure line is the exact last line. `taxonomy_id` is 1350, price is 3.5, `digital_file` is the ZIP, and the who/when/supply fields are right.
- **Images**: all 4 are 3000×2250 and `contact-sheet.png` is present.
- **Rendered pages** (Letter and A4, pages 1, 2, 17, 18, 19, 20): nothing is clipped. The cut line is centred, the margins are safe, and page 1 fits on Letter. All 30 icons are original and read clearly at about 1 in. FREE (3 stars) is clearly not the moon. Ink use is light: white page, thin frames.
- **Thumbnail**: it passes the scroller bar. The dark plum band on wood stands out against the flat red/green results, and the "30 unique cards" badge reads at thumbnail size.

## Fixes (numbered, all required unless marked optional)
1. **Redo the markers (page 20).** They are white circles with thin rings, each showing a star, moon, snowflake or holly. Three of those four are game pictures (star #9, moon #23, holly #14). The snowflake is too: it is icon #12. So a covered cell still shows a game picture. On a white card, white markers also make covered cells hard to tell apart from open ones, for the player and for the caller checking a win. Make each marker an opaque solid disc in gold #e8c97a with a plum ring and no game picture on it, matching what the thumbnail shows. A small non-icon mark is fine, such as a dot or a tiny "✓". Rebuild both PDFs and image 2.
2. **The listing images currently misrepresent the markers.** Images 1 and 4 show solid gold token discs, but the markers in the file look nothing like that. Fix 1 solves this. If you keep the current markers instead, the images must show the real printed markers.
3. **Remove "so ties are rare"** from page 1, the description and the README, and **add a tie rule** to the "How to play" box on page 1. I simulated 20,000 games per setting with the real cards:
   - "Any line" with 30 players: about 22% of games have 2 or more winners on the same call. With 10 players it is about 17%.
   - Blackout with 30 players: about 54% of games tie, with an average of 2.9 winners.

   No shared line only stops two players winning on the *same* line. It doesn't stop ties. Suggested copy: "No two cards share a winning row, column or diagonal. If two players call BINGO on the same picture, both win (or play a quick tie-break round)." Also add a "Ties" line under Ways to win, at least for blackout.
4. **Marker count.** 80 markers covers about 3 players for a blackout, while the listing says "2 to 30 players". In the description and on page 1, say "80 markers (print page 20 once for every 3 players, or use candy or buttons)".
5. **Image 4 small mismatch.** The calling card shown is "Owl", but the owl on Card 07 (row 2, column 4) is uncovered, and the covered diagonal is bird house, fox, FREE and two others. Either cover the owl or show a calling card for a picture that is covered.
6. *(optional)* **Snowman (#29)** is the weakest icon at card size: mostly white with thin outlines, it looks lighter and smaller than its neighbours. Thicken the outline or give it a pine scarf or hat so it carries the same visual weight. At 96 px the scarf (#21) leans toward "candy cane". Consider straightening one end.

## Spec (`formats/bingo.md`) fixes
- **S1.** Rule 3 is fine as a check, but the spec presents it as making ties rare. Change that to: "Ties still happen (about 1 in 5 line games with 30 players, more than half of blackouts). The instructions must include a tie rule. Never claim ties are rare."
- **S2.** Markers: "80 circles of 20 mm, so one covers a cell" is wrong. A 20 mm disc does not cover a cell of about 30×23 mm; it covers the picture. Specify: "opaque, high-contrast filled discs, about 22 mm, with no game icons on them; the listing images must show these same markers."
- **S3.** Add to "Then look" checks: "the listing images show only what the file contains (markers, page layouts)" and "any calling card shown in an image matches the covered cells".
- **S4.** Add the per-player marker maths to the copy rules: blackout needs 24 markers per player.
- **S5.** Minor: the spec says icons must read at "about 0.8 in", but the contact sheet checks at 96 px (1 in). Pick one size (the real Letter cell is about 1.2 × 0.9 in).

## Would I pay $3.50?
After fixes 1–4, yes. The cards and art are better than most "christmas bingo" results. As shipped, a buyer who prints page 20 would get markers that don't look like the photos and don't work well in play.
