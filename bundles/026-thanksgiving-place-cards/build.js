// Builds the buyer PDFs: 5 pages each in US Letter and A4.
//   1-3: 12 place cards (4 per page), 4: 4 menu/buffet tent cards, 5: print, cut, fold guide.
// Run from this folder: NODE_PATH=$(npm root -g) node build.js
const { chromium } = require('playwright'); const fs = require('fs');
const T = require('./cards.js');
const { PLUM, PINE, BERRY, GOLD, CREAM, RUSSET, fontCSS, W: CW, H: CH, DESIGNS, MENUS, cardSVG, motifDefs } = T;
const SHOP = 'Duskwood Designs Co', SLUG = 'thanksgiving-place-cards', N = 5;
const PAPER = { 'US-Letter': [215.9, 279.4], A4: [210, 297] };
const css = (W, H) => `${fontCSS}
@page{size:${W}mm ${H}mm;margin:0}*{box-sizing:border-box}
body{margin:0;font-family:Nu;color:${PLUM};-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:${W}mm;height:${H}mm;position:relative;overflow:hidden;page-break-after:always;background:#fff}
.tag{position:absolute}
.top{position:absolute;left:0;right:0;top:11mm;text-align:center;font-weight:800;font-size:3mm;letter-spacing:.9mm;text-transform:uppercase;color:${PINE}}
.top i{font-style:normal;color:${RUSSET}}
.foot{position:absolute;left:0;right:0;bottom:10mm;text-align:center;font-size:2.6mm;color:#6d5f73}
.guide{background:${CREAM}}
.frame{position:absolute;inset:9mm;border:.55mm solid ${PLUM};border-radius:5mm}.frame::after{content:'';position:absolute;inset:1.4mm;border:.22mm solid ${PINE};border-radius:3.8mm}
.g{position:absolute;left:24mm;right:24mm;top:19mm;text-align:center}
h1{font-family:Fr;font-weight:900;font-size:10.4mm;line-height:1.15;margin:1.6mm 0 0;white-space:nowrap}h1 em{font-style:normal;color:${RUSSET}}
.kick{font-weight:800;font-size:3.1mm;letter-spacing:1.1mm;color:${PINE};text-transform:uppercase}
.sub{font-size:3.6mm;font-weight:700;color:${PINE};margin-top:2.4mm}
.steps{position:absolute;left:24mm;right:24mm;top:58mm;display:flex;flex-direction:column;gap:6mm}
.st{display:flex;gap:4.5mm;align-items:flex-start}.st b{flex:none;width:9mm;height:9mm;border-radius:50%;background:${RUSSET};color:${CREAM};font-family:Fr;font-weight:700;font-size:5mm;display:flex;align-items:center;justify-content:center}
.st h3{font-family:Fr;font-weight:700;font-size:4.7mm;margin:0 0 .6mm;color:${BERRY}}.st p{margin:0;font-size:3.9mm;line-height:1.36;text-wrap:pretty}
.sz{position:absolute;left:24mm;right:24mm;display:grid;grid-template-columns:1fr 1fr;gap:6mm}
.sz div{background:#fff;border:.35mm solid ${PLUM};border-radius:3mm;padding:3.5mm 4.5mm;font-size:3.5mm;line-height:1.4}.sz b{font-family:Fr;font-weight:700;font-size:4.6mm;color:${BERRY};display:block}
`;
function cardsPage(W, H, items, kind, title, start) {
  const gx = 8, gy = 8, gw = 2 * CW + gx, gh = 2 * CH + gy, x0 = (W - gw) / 2, y0 = (H - gh) / 2 + 2;
  const cards = items.map((d, i) => `<div class=tag style="left:${x0 + (i % 2) * (CW + gx)}mm;top:${y0 + Math.floor(i / 2) * (CH + gy)}mm">${cardSVG(d, kind, start + i)}</div>`).join('');
  return `<div class=page><div class=top>${title}</div>${cards}<div class=foot>Cut on the grey line · fold on the dashed line · print at 100% (actual size) · © ${SHOP} · personal use only</div></div>`;
}
function guidePage(W, H) {
  const sz = `<div class=sz style="top:178mm"><div><b>Place cards · 12</b>3.5 × 2 in folded (88.9 × 50.8 mm)<br>Pages 1 to 3 · 4 per page · name line on both sides</div><div><b>Menu tents · 4</b>3.5 × 2 in folded (88.9 × 50.8 mm)<br>Page 4 · Mains, Sides, Desserts, Drinks · write-in lines</div></div>`;
  return `<div class="page guide"><div class=frame></div><div class=g><div class=kick>Print, cut and fold</div><h1>Thanksgiving <em>Place</em> Cards</h1><div class=sub>Four steps from your printer to the table</div></div>
  <div class=steps>
   <div class=st><b>1</b><div><h3>Print at actual size</h3><p>Choose 100% or "actual size" in the print dialog, not "fit to page", so each card comes out 3.5 × 4 in flat. Use white or cream card stock, about 160 to 250 gsm (65 to 110 lb), so the cards stand up.</p></div></div>
   <div class=st><b>2</b><div><h3>Cut along the grey line</h3><p>Scissors work well, and a paper trimmer is quick for the straight sides. Snip the corners round to follow the grey line. The small grey ticks beside each card mark the fold.</p></div></div>
   <div class=st><b>3</b><div><h3>Fold on the dashed line</h3><p>Run a ruler and an empty pen along the dashed line to score it, then fold in half with the pattern band on the fold. Press the crease flat with a ruler edge for a crisp tent.</p></div></div>
   <div class=st><b>4</b><div><h3>Write the name and stand it up</h3><p>Write the guest's name on the line with a pen, gel pen or paint pen. Both sides are the same, so write on both and guests across the table can read it too. Print again whenever you need more.</p></div></div>
  </div>${sz}<div class=foot style="bottom:13mm">© ${SHOP} · personal use only · printing and card stock not included</div></div>`;
}
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  fs.mkdirSync('bundle', { recursive: true });
  for (const [key, [W, H]] of Object.entries(PAPER)) {
    const t = n => `Woodland Thanksgiving · <i>${n}</i>`;
    const pages = [
      cardsPage(W, H, DESIGNS.slice(0, 4), 'place', `${t('Place cards')} · 1 of ${N}`, 0),
      cardsPage(W, H, DESIGNS.slice(4, 8), 'place', `${t('Place cards')} · 2 of ${N}`, 4),
      cardsPage(W, H, DESIGNS.slice(8), 'place', `${t('Place cards')} · 3 of ${N}`, 8),
      cardsPage(W, H, MENUS, 'menu', `${t('Menu tents')} · 4 of ${N}`, 12),
      guidePage(W, H)];
    await p.setContent(`<!doctype html><html><head><meta charset=utf-8><style>${css(W, H)}</style></head><body>${motifDefs()}${pages.join('')}</body></html>`, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const o = await p.evaluate(() => [...document.querySelectorAll('.st,.g,.steps,.sz')].filter(e => e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1).map(e => e.className));
    const gap = await p.evaluate(() => { const s = document.querySelector('.steps').getBoundingClientRect(), z = document.querySelector('.sz').getBoundingClientRect(); return (z.top - s.bottom) / 96 * 25.4; });
    console.log(key, 'steps-to-boxes gap mm', gap.toFixed(1), o.length ? 'OVERFLOW ' + o : '');
    if (gap < 4 || o.length) process.exitCode = 1;
    await p.pdf({ path: `bundle/${SLUG}-${key}.pdf`, width: `${W}mm`, height: `${H}mm`, printBackground: true, preferCSSPageSize: true });
  }
  await b.close();
})();
