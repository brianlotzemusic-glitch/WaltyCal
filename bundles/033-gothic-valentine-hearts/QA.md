# QA 033 Gothic Valentine Hearts (round 1, 24 Oct 2026)

**Verdict: REJECTED.** Two designs are below the B bar (01, 05); small polish on 02, 03, 06. Packaging, copy and images are sound.

## Must fix
1. **01 Anatomical heart (B-/C+ FAIL).** The two vessels are fat uniform tubes (about 0.55 in wide) that read as fingers or a "rock-on" hand sign, not an aorta and vena cava; the left one bends like a bent finger. Redraw the top: a thick aortic arch curving over and down, a pulmonary trunk behind it, and a vena cava stub on the right, with tapering, differently sized stumps (largest about 0.45 in, smallest about 0.25 in), plus one or two short branch stubs; keep every part joined and every slot at 0.10 in or more. Make the groove lines taper/branch (coronary-artery look) instead of four plain parallel slits, and keep the bottom apex. Keep the heart body.
2. **05 Skeleton key (B- FAIL).** (a) The heart bow is lopsided: left lobe bulges, outer outline lumpy, inner heart cutout tilted and unequal wall (about 0.5 in at left, 0.15 in at right); redraw a symmetric heart bow (rotate a symmetric heart, even wall about 0.25 in). (b) The tip end of the shaft (PNG ~x 1330-1430, y 1590-1700) has an accidental nub/notch; end it with one clean rounded or squared end. Teeth and slots (about 0.12 in) are fine.

## Should fix (do in the same pass)
- 02 bat: the notch between the ears is an odd arrow-shaped blob (PNG ~x 810-990, y 620-760); smooth to a simple V. Reads as a bat first, heart second (pointed heart base); B.
- 03 wreath: thorn at left (x 200-330, y 470-540) is a fat leaf-like blob and the right one (x 1340-1450, y 1100-1230) the same; make thorns slim tapered triangles. Heart is slightly lopsided; B-/B.
- 04 padlock: the two small rivet holes plus keyhole read as a face. Move rivets to the shoulders or drop them. Otherwise strong: A-.
- 06 window: small kink on the upper-right shoulder (x 1410, y 500) and slight lumps on the left roof edge; smooth. B.

## Per-design grades (100% crops, white-flattened PNG)
01 C+ FAIL, 02 B, 03 B-, 04 B+ (A- without the face effect), 05 B- FAIL, 06 B. 03 is borderline: slim the thorns or it will fail round 2.

## Checked and passing
- gen.py --check ALL CHECKS PASS (1 part each; holes 01:5, 02:4, 03:4 (min 1011), 04:4 (min 833), 05:1, 06:3).
- Min width measured by morphological opening on the 300 DPI PNGs: no black feature is lost at 0.08 in (tips, thorns, slits all >= 0.08 in), so the stated 0.08 in at 6 in is true. No accidental weapons or horror-film couples; key and padlock are the intended symbols.
- SVG: 6 valid XML, 1 path each, 6.000in, closed subpaths. DXF: 6 files, INSUNITS inches, re-open in ezdxf, counts = holes+1. PNG: 1800x1800 RGBA, transparent corners, clean edges.
- ZIP: 22 entries, byte-identical to bundle/; matches LISTING.md. README: formats, sizes, software, licence only, includes the exact min-size sentence.
- Listing images 1-4: 3000x2250 RGB, opaque, no text overlap; image 1 is a flat preview of the six files (no scene); 2-4 show only included files. All four must be regenerated after 01 and 05 change.
- Title 138 chars, no IP phrases (no "Galentine"), 13 tags <= 20 chars, taxonomy 12394, price $4.00; disclosure line last, mockup sentence present, size sentence consistent across LISTING.md, listing.json, README; description identical in LISTING.md and listing.json. No functional-guide content.
- No paid actions, no live Etsy edits. Seasonal: not due on Etsy before mid-Dec, so there is time for round 2.

## Open questions
- Lister: does it tick Etsy's AI checkbox and "Designed by"? (unchanged)

## Round 2 fixes applied (24 Oct, Designer; awaiting re-QA)
- 01: aortic arch (about 0.55 in base tapering), pulmonary trunk and slim vena cava stub of different sizes, two short branch stubs; coronary-style tapering/branching grooves (slots 0.12 in+). Self-grade B+.
- 05: exactly symmetric heart bow with an even wall (about 0.29 in), shaft ends in one squared end, accidental nub removed. Self-grade B+.
- 02 smooth V between the ears; 03 slimmer thorns/leaves; 04 rivet holes dropped; 06 smooth shoulders (mirrored outline).
- gen.py --check ALL CHECKS PASS (hole counts now 01:3 02:4 03:4 04:2 05:1 06:3; added 01 slot width and 05 wall checks). SVG/DXF/PNG, ZIP (22 entries) and all 4 listing images (3000x2250 RGB) regenerated.
