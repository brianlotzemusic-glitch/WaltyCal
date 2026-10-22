# Etsy listing image requirements (Researcher, 22 Oct 2026)

**Source limitation (important).** etsy.com and help.etsy.com return HTTP 403 to our fetch tool, and search never surfaced Etsy's own page text. So everything below is either (V) seen in a search snippet quoting Etsy's help page, or (T) from third-party summaries and unverified. The owner (or a browser session) should open the URLs below once and confirm the T items before we rely on them. Nothing here edits a listing.

## Policy URLs
- Requirements and Best Practices for Images in Your Etsy Shop: https://help.etsy.com/hc/articles/115015663347 (Etsy; fetch blocked, snippet only)
- Seller handbook, "Important updates to AI use on Etsy": article 1522733284810 (cited in FACTORY.md; not retrievable here)
- Etsy Creativity Standards: https://www.etsy.com/legal/creativity-standards/ (blocked)
- Etsy Seller Policy: https://www.etsy.com/legal/seller-policy/ (blocked)
- Our House Rules: https://www.etsy.com/help/article/6128
- Third-party (T): https://www.listadum.com/blog/should-you-disclose-mockups-and-ai-images-in-your-etsy-listings , https://letsenhance.io/blog/all/amazon-etsy-image-requirements/

## Rules found
1. (V) Photos should be the seller's own photos of the actual item, not renderings or stock images; Etsy allows exceptions in certain situations. (T) The exceptions are said to be personalization and production-partner (print-on-demand) items. Exact wording unconfirmed.
2. (V) Size: at least 2000 px on width and height recommended. First photo at least 635 px each side or it may rank lower in search. Files over 1 MB may fail to upload on slow connections.
3. (V) File types .jpg, .gif, .png, .svg, .heic. No animated gif. Transparent PNG areas show black, so use opaque backgrounds.
4. (T) Up to 10 images per listing; sRGB; no white-background requirement; lifestyle images are fine.
5. (T, consistent across sources) AI disclosure: tick the "I used AI-generative technology" style checkbox in the listing form, choose "Designed by" not "Made by" when AI created or altered the item, and say so in the description (policy update dated 14 Jan 2026, tied to the June 2025 Creativity Standards). Exact wording of the field is unconfirmed.
6. (T) No explicit rule found requiring disclosure of mockups or AI-generated photos, but the general rule is that photos must accurately show what the buyer receives. Our own FACTORY.md sentence ("Listing photos include digital mockups; you receive the digital files shown.") already covers this and costs nothing.
7. (T, not Etsy) A New York law reportedly concerns AI-generated people in ads and listing photos. Avoid synthetic human faces or bodies in photos.
8. (FACTORY.md, from the owner's reading of the handbook) First photo is the most realistic one; every photo shows exactly what the buyer gets; bot-generated listings with no human involvement are banned.

## Likely impact on our listing types
- **Printables with room mockups (wall art, planners):** the most exposed. A framed print on a wall is a rendering, not the item. Acceptable only if the mockup is realistic, clearly shows the same art the buyer gets, and the description carries the mockup sentence. Add a plain flat view of the actual file as an image (page preview, sizes, what is included).
- **SVG/clipart bundles:** photos are naturally renderings of the files. Show the real files (contact sheet of the actual designs, file-type list), no invented use-case scenes with items not included, no transparent PNGs.
- **POD tees/mugs with Printify mockups:** POD is the likeliest exception to the real-photo rule, but not confirmed. Use Printify's own realistic mockups, show the true print placement and colors, and keep the first image the most realistic one.
- **Lifestyle composites built in code:** fine only if realistic and truthful. Risk: the first photo is a stylised composite that looks fake, or shows props or products not included. Put the most realistic image first and label composites in the description.
- **AI disclosure field:** all our listings are AI-assisted, so each must have the AI checkbox ticked and "Designed by" (not "Made by"), plus the existing disclosure sentence. Check whether the Lister's API/automation sets the field; if not, that is a gap.
- **Sizes:** check every listing image is at least 2000 px both sides, opaque, under about 1 MB if practical, and the first image 635 px or more.

## Checklist for NEW listings (Designer / QA / Lister)
1. First image: the most realistic image of the actual product (for digital: a true preview of the file; for POD: the realistic Printify mockup). No collage or stylised composite first.
2. Every image shows only what the buyer receives. No extra products, props sold as included, or fake people.
3. Each image at least 2000 px on both sides, opaque background (no transparent PNG), jpg or png, ideally under 1 MB.
4. Digital items: include one image showing file formats and what is in the download, plus one flat view of the real art.
5. Description includes: "Designed with the help of digital and AI tools, and checked by hand." and, when mockups are used, "Listing photos include digital mockups; you receive the digital files shown."
6. AI-generative checkbox ticked and "Designed by" chosen on the listing; never "Made by" or "handmade".
7. No instructions, patterns, tutorials or recipes as the product (see FACTORY.md Etsy AI policy).
8. QA fails a listing if any item above is missing; log the reason.

## Open questions for the owner
- Open the three Etsy URLs in a browser and confirm items 1, 4, 5 above (POD/personalization exception, 10-image limit, exact AI field wording).
- Does Etsy's listing form or API (v3) expose the AI checkbox and "Designed by" field? The Lister must set them if so.
