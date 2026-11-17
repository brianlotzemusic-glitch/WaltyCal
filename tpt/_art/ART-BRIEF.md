# Art session brief (daily, has the Higgsfield connector)

Owner, 17 Nov 2026: "Feel free to use Higgsfield for future builds. I want these to look as professional as possible."
This session makes the illustrations for the NEXT products so the builders (who cannot generate images) can place them.
It only makes art. It never builds, QAs, releases or touches markers. Never touch `main`. Credits are the owner's: stay inside the caps.

## Steps
1. `git fetch origin shop-factory && git checkout -B shop-factory origin/shop-factory`.
2. Read `tpt/_art/README.md` (rules) and `tpt/_art/next/INDEX.md` (what is already made). Credit guard: call Higgsfield `balance`.
   If under 60 credits, add one LOG line saying so and STOP. Never buy credits, change the plan, start a trial or turn on auto-refill.
3. Work list = ONLY what the next shifts will actually build: count today's builds in `tpt/LOG.md` and take the top unchecked queue lines for
   the build slots still to come in the next 24 hours (the day owes 3 classroom products and 1 Logic kit; at most 4 items). Skip lines
   marked `[!]` or `[~]` and items already in INDEX.md (slug = title lowercased, words joined by `-`, at most 40 characters). Add a held
   product that a rescue is about to rebuild only if its LOG line says "needs art". Nothing for later days, nothing speculative: the owner
   does not want a library of what-ifs.
4. For each item write a one-line CONCEPT: one scene or object group that says what the product is, friendly and classroom-safe
   (Logic kits: studio gear, headphones, a laptop with an abstract waveform, no readable screen text). One subject, centred.
   Not music notation, no staff, no note symbols, no text, no numbers, no brand or character names, no real people.
5. Generate with `generate_image_batch` (jobs_wait, groups of at most 12), model `gpt_image_2_6`, aspect_ratio `1:1`, quality `medium`,
   resolution `2k`, background `transparent`. Per item: 3 variants of the HERO concept (about 3 credits). A SPOT image only when a builder wrote
   `needs art: <subject>` in LOG. Prompt = the STYLE line below + the concept.
   STYLE: "Clean black ink line art illustration in a flat sticker style, uniform bold black outline, <concept>; mostly black outlines with
   white fills, and exactly one accent colour, icy blue (#4FA3D9), on a few shapes; no shading, no gradients, no textures; no text, no
   letters, no numbers, no musical notation, no staff, no musical note symbols; single centered subject with generous empty margin;
   transparent background". Other seasons: change only the accent colour and name the hex (Thanksgiving rust #B5522B, Halloween
   orange #E8731A); winter and everything else icy blue.
6. Download each result (`curl` the result_url), view EVERY image at full size with the Read tool on a mid-pink background
   (`convert in.png -background '#f4d9d9' -flatten out.png`) so transparency and edges show. Reject any image with: text or numbers or
   notation anywhere, a malformed or wrong object (extra limbs or fingers, an instrument that is the wrong shape, fused shapes), art cut
   off by the image edge, a second accent colour, shading or gradients. Pick the best hero. If all three are bad, regenerate once
   (max 3 more); if still bad, record `no usable hero` and move on. Total cap 40 credits per run.
7. Save into `tpt/_art/next/<slug>/`: `hero.png` (and `spot-1.png` only if requested) (convert each with `-resize 1400x1400 -strip`, keep alpha),
   and `NOTES.md` (concept, credits used, what was rejected and why). Add one line per item to `tpt/_art/next/INDEX.md`:
   `- <queue title, first 70 chars> -> tpt/_art/next/<slug>/ (hero)`.
8. USE IT OR LOSE IT, every run before step 3: for each folder in `tpt/_art/next/` (a) whose product has already been built (a
   `tpt/NNN-*` folder with the same title exists) or (b) that is more than 3 days old, `git rm -r` it, delete its INDEX line, and count
   it as "unused" if the built product's folder has no `art/` directory. Say how many were unused in the LOG line. Read `tpt/_art/USAGE.md`:
   if more than a third of the art made in the last 7 days went unused, make art for only 2 items per run until that improves. Never add
   images to `tpt/_art/library/`; that library was a one-time batch and only shrinks.
9. Add one line to `tpt/LOG.md` (items made, credits used, balance left, unused discarded). Commit only `tpt/_art/` and `tpt/LOG.md`, push (fetch,
   merge, push on rejection; never force). Reply in 3 lines: items made, credits used, balance.
