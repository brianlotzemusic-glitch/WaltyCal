// Builds the buyer PDFs: 4 pages each in US Letter and A4.
//   1-2: 12 Large tags (2.5 x 4 in), 3: 12 Small tags (1.75 x 2.75 in), 4: print and make guide.
// Run from this folder: NODE_PATH=$(npm root -g) node build.js
const { chromium } = require('playwright'); const fs = require('fs');
const T = require('./tags.js');
const { PLUM, PINE, BERRY, GOLD, CREAM, fontCSS, SIZES, DESIGNS, smallDesigns, tagSVG, motifDefs } = T;
const SHOP = 'Duskwood Designs Co';
const PAPER = { 'US-Letter': [215.9, 279.4, 'US Letter'], A4: [210, 297, 'A4'] };
const css = (W, H) => `${fontCSS}
@page{size:${W}mm ${H}mm;margin:0}*{box-sizing:border-box}
body{margin:0;font-family:Nu;color:${PLUM};-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:${W}mm;height:${H}mm;position:relative;overflow:hidden;page-break-after:always;background:#fff}
.tag{position:absolute}
.top{position:absolute;left:0;right:0;top:11mm;text-align:center;font-weight:800;font-size:3mm;letter-spacing:.9mm;text-transform:uppercase;color:${PINE}}
.top i{font-style:normal;color:${BERRY}}
.foot{position:absolute;left:0;right:0;bottom:10mm;text-align:center;font-size:2.6mm;color:#6d5f73}
.guide{background:${CREAM}}
.frame{position:absolute;inset:9mm;border:.55mm solid ${PLUM};border-radius:5mm}.frame::after{content:'';position:absolute;inset:1.4mm;border:.22mm solid ${PINE};border-radius:3.8mm}
.g{position:absolute;left:24mm;right:24mm;top:19mm;text-align:center}
h1{font-family:Fr;font-weight:900;font-size:10.4mm;line-height:1.15;margin:1.6mm 0 0;white-space:nowrap}h1 em{font-style:normal;color:${BERRY}}
.kick{font-weight:800;font-size:3.1mm;letter-spacing:1.1mm;color:${PINE};text-transform:uppercase}
.sub{font-size:3.6mm;font-weight:700;color:${PINE};margin-top:2.4mm}
.steps{position:absolute;left:24mm;right:24mm;top:60mm;display:flex;flex-direction:column;gap:7mm}
.st{display:flex;gap:4.5mm;align-items:flex-start}.st b{flex:none;width:9mm;height:9mm;border-radius:50%;background:${BERRY};color:${CREAM};font-family:Fr;font-weight:700;font-size:5mm;display:flex;align-items:center;justify-content:center}
.st h3{font-family:Fr;font-weight:700;font-size:4.7mm;margin:0 0 .6mm;color:${BERRY}}.st p{margin:0;font-size:4mm;line-height:1.38;text-wrap:pretty}
.sz{position:absolute;left:24mm;right:24mm;display:grid;grid-template-columns:1fr 1fr;gap:6mm}
.sz div{background:#fff;border:.35mm solid ${PLUM};border-radius:3mm;padding:3.5mm 4.5mm;font-size:3.5mm;line-height:1.4}.sz b{font-family:Fr;font-weight:700;font-size:4.6mm;color:${BERRY};display:block}
`;
function tagsPage(W, H, designs, kind, title, start) {
  const { w, h } = SIZES[kind]; const cols = kind === 'large' ? 3 : 4, rows = kind === 'large' ? 2 : 3, gx = 5, gy = kind === 'large' ? 6 : 5;
  const gw = cols * w + (cols - 1) * gx, gh = rows * h + (rows - 1) * gy;
  const x0 = (W - gw) / 2, y0 = (H - gh) / 2 + 1;
  const tags = designs.map((d, i) => `<div class=tag style="left:${x0 + (i % cols) * (w + gx)}mm;top:${y0 + Math.floor(i / cols) * (h + gy)}mm">${tagSVG(d, kind, start + i)}</div>`).join('');
  return `<div class=page><div class=top>${title}</div>${tags}<div class=foot>Cut on the grey line · print at 100% (actual size) · © ${SHOP} · personal use only</div></div>`;
}
function guidePage(W, H) {
  const sz = `<div class=sz style="top:182mm"><div><b>Large tags · 12</b>2.5 × 4 in (63.5 × 101.6 mm)<br>Pages 1 and 2 · greeting, To and From lines</div><div><b>Small tags · 12</b>1.75 × 2.75 in (44.5 × 69.9 mm)<br>Page 3 · To and From lines</div></div>`;
  return `<div class="page guide"><div class=frame></div><div class=g><div class=kick>Print and make</div><h1>Woodland <em>Gift</em> Tags</h1><div class=sub>Four steps from your printer to the tree</div></div>
  <div class=steps>
   <div class=st><b>1</b><div><h3>Print at actual size</h3><p>Choose 100% or "actual size" in the print dialog, not "fit to page", so the tags come out 2.5 × 4 in and 1.75 × 2.75 in. Use white or cream card stock (about 160 to 250 gsm, 65 to 110 lb) for tags that stand up to string.</p></div></div>
   <div class=st><b>2</b><div><h3>Cut along the grey line</h3><p>Scissors work for every shape. For the straight-sided tags a paper trimmer or a craft knife and ruler is quick. The grey line is the cut line and sits right at the edge of the pattern.</p></div></div>
   <div class=st><b>3</b><div><h3>Punch the hole</h3><p>The cream ring with the dotted circle shows where to punch. A 1/4 in (6 mm) hole punch is ideal. The ring gives the hole a little extra strength.</p></div></div>
   <div class=st><b>4</b><div><h3>Write, thread, tie</h3><p>Fill in To and From with a pen or pencil, thread twine, ribbon or baker's string through the hole and tie it on. Print again whenever you need more.</p></div></div>
  </div>${sz}<div class=foot style="bottom:13mm">© ${SHOP} · personal use only · printing, card stock and string not included</div></div>`;
}
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  fs.mkdirSync('bundle', { recursive: true });
  for (const [key, [W, H, name]] of Object.entries(PAPER)) {
    const pages = [
      tagsPage(W, H, DESIGNS.slice(0, 6), 'large', 'Woodland Christmas gift tags · <i>Large</i> · 1 of 3', 0),
      tagsPage(W, H, DESIGNS.slice(6), 'large', 'Woodland Christmas gift tags · <i>Large</i> · 2 of 3', 6),
      tagsPage(W, H, smallDesigns, 'small', 'Woodland Christmas gift tags · <i>Small</i> · 3 of 3', 12),
      guidePage(W, H)];
    await p.setContent(`<!doctype html><html><head><meta charset=utf-8><style>${css(W, H)}</style></head><body>${motifDefs()}${pages.join('')}</body></html>`, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const o = await p.evaluate(() => [...document.querySelectorAll('.st,.g,.steps,.sz')].filter(e => e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1).map(e => e.className));
    // guide must not collide: steps bottom above size boxes top
    const gap = await p.evaluate(() => { const s = document.querySelector('.steps').getBoundingClientRect(), z = document.querySelector('.sz').getBoundingClientRect(); return (z.top - s.bottom) / 96 * 25.4; });
    console.log(key, 'steps-to-boxes gap mm', gap.toFixed(1), o.length ? 'OVERFLOW ' + o : '');
    if (gap < 4) process.exitCode = 1;
    await p.pdf({ path: `bundle/woodland-christmas-gift-tags-${key}.pdf`, width: `${W}mm`, height: `${H}mm`, printBackground: true, preferCSSPageSize: true });
  }
  await b.close();
})();
