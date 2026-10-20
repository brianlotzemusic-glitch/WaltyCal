# QA: 007 Cozy Winter Reading Mug (independent review, 20 Oct 2026)
**Verdict: REJECTED (round 1).** Nothing is wrong with the mechanics or the money; it fails on distinctness from live 001 and on the weak centre art. Do not publish yet.

## Passed (verified, not taken from the Designer's notes)
- Live Printify product 6ad73fcb5c40fb7fca0af0be matches product.json exactly: title (128 chars), description, 13 tags (all <= 20 chars), blueprint 68, provider 1 (SPOKE), one enabled variant 33719 (11oz) at $16.99, cost $6.44, print file mug-wrap-2700x1120.png at 2700x1120, scale 1, centred. Not published (external is null, no etsy_published file).
- Profit: 16.99 - 6.44 - (1.70 + 0.20) - 0.67 (10% of $6.69 US shipping, from the live shipping profile) = $7.98 (floor $6). Even with shipping fees at 0 it is $8.65, with Etsy fees at 13% it is still about $7.3. PASS. Same price as 001 ($16.99), inside the $15-21 comparable range in PROVIDERS.md.
- Wrap is 2700x1120 RGB at 300 DPI, nothing in the outer 40 px (no bleed/seam clipping), no text, no garbled marks. The moth/holly art is clean at 100% (it is the 006 AI art, slightly soft but fine for a mug).
- Listing text: size "about 3.8 in tall, 3.2 in across, 11 oz" is the standard 11 oz mug and the wrap matches the real 2700x1120 area. No trademark/IP phrases ("Cozy Winter Reading Mug", "dark academia", "cottagecore", "whimsigoth" are generic aesthetic terms; the avoid-list "Cozy Turtle"/"Cozy Reader" is not used). No medical claims. Disclosure line present. Description says "one on each side", which is true of the wrap.

## Failed / fix before re-review
1. **Too close to live pod/001 (Luna Moth Mug, listed 3 Oct, $16.99).** Same layout (moth at 1/4 and 3/4, small motif in the centre, stars), same cream luna moth, same price, same blueprint. Differences are only the black background (001 is plum), holly (001 has pine) and a book (001 a crescent moon). Five of 13 tags are identical to 001 (`moth mug`, `luna moth mug`, `cottagecore mug`, `dark academia mug`, `whimsigoth mug`) and the title also leads with luna moth/cottagecore/dark academia, so the two would compete for the same searches and the same buyer sees a near-duplicate in the shop grid. Fix: make the reader angle the whole design, not a sticker on a moth mug. Options: (a) one large moth reading-lamp scene across the front instead of two moths; or (b) keep the moth but drop `moth mug`, `luna moth mug`, `cottagecore mug`, `dark academia mug`, `whimsigoth mug` from the tags and the title's "Luna Moth ... Cottagecore ... Dark Academia" string, and use reader/winter/bookish terms (e.g. `bookworm gift`, `librarian gift`, `bookish gift`, `reading lover mug`, `winter reading`, `teacher gift`, `tea and books`) so it ranks for a different shopper. Prefer (a)+(b) together.
2. **The book is the weak link.** At 100% it is a flat code-drawn vector (hard polygon pages, four generic dashes, stiff spine bar) next to detailed AI moth illustration; it is also the hero of the front view. It reads as clip-art and does not meet the Art quality bar ("stop a scroller next to the top 10"). Redraw it in the moth's style (fine gold line work, page curl, a few stars or a tiny moth resting on it), or generate one flash image ($0.028) and upscale; the budget rule allows one standard re-roll.
3. **Only one mockup (front).** Needs extra photos (see below) before it can go live with a credible gallery.
4. Minor: "lead and BPA free" is copied from 001 and is not stated by Printify's API; acceptable as it is already live on 001, but confirm in the Printify catalogue or soften to "white glossy ceramic". Also the front mockup is the only proof of placement: the holly/moth sit at the edges and the handle side is not shown (see photos).

## Extra photos needed (Printify returned only the front mockup)
No orders, nothing paid. Photos to produce free from Printify's mockup generator / existing renders, or by the Designer compositing the wrap onto the mug template:
1. **Left and right views** (Printify cameras `left`, `right`) to show the moth on each side and that the handle does not cut the art; these were only in the create response and are lost; re-fetch by `printify.py update` (no-art) or in the Printify UI mockup library.
2. **Lifestyle lead photo** (first Etsy photo, per FACTORY.md "Listing photos"): mug on a wooden table next to an open book, lamp and tea, winter light (AI lifestyle mockup using the mug image as reference).
3. **Flat design photo**: the full wrap laid out flat (the 2700x1120 art), so buyers see both moths and the book at once.
4. **Size/info photo**: 11 oz, about 3.8 x 3.2 in, white glossy ceramic, hand wash recommended.
5. Optional: a gift-context image (mug with a wrapped book).

## Constraints respected
No live Etsy listing or price touched (Ads test runs to 24 Oct); this is a new, unpublished product. No orders created. No new spend.
