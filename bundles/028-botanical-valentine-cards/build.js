// Builds the buyer PDFs: 5 pages each in US Letter and A4.
//   1-2: 8 cards (4 per page), 3-4: 18 gift tags (9 per page), 5: print and cut guide.
// Run from this folder: NODE_PATH=$(npm root -g) node build.js
const { chromium } = require('playwright'); const fs = require('fs');
const T = require('./cards.js');
const { PLUM, PINE, BERRY, GOLD, CREAM, ROSE, BLUSH, fontCSS, CW, CH, TW, TH, CARDS, TAGS, cardSVG, tagSVG, motifDefs } = T;
const SHOP = 'Duskwood Designs Co', SLUG = 'botanical-valentine-cards', N = 5;
const PAPER = { 'US-Letter': [215.9, 279.4], A4: [210, 297] };
const css = (W, H) => `${fontCSS}
@page{size:${W}mm ${H}mm;margin:0}*{box-sizing:border-box}
body{margin:0;font-family:Nu;color:${PLUM};-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:${W}mm;height:${H}mm;position:relative;overflow:hidden;page-break-after:always;background:#fff}
.tag{position:absolute}
.top{position:absolute;left:0;right:0;top:4.5mm;text-align:center;font-weight:800;font-size:2.8mm;letter-spacing:.9mm;text-transform:uppercase;color:${PINE}}
.top i{font-style:normal;color:${ROSE}}
.foot{position:absolute;left:0;right:0;bottom:4mm;text-align:center;font-size:2.6mm;color:#6d5f73}
.guide{background:${CREAM}}
.frame{position:absolute;inset:9mm;border:.55mm solid ${PLUM};border-radius:5mm}.frame::after{content:'';position:absolute;inset:1.4mm;border:.22mm solid ${BERRY};border-radius:3.8mm}
.g{position:absolute;left:24mm;right:24mm;top:19mm;text-align:center}
h1{font-family:Fr;font-weight:900;font-size:10.4mm;line-height:1.15;margin:1.6mm 0 0;white-space:nowrap}h1 em{font-style:normal;color:${ROSE}}
.kick{font-weight:800;font-size:3.1mm;letter-spacing:1.1mm;color:${PINE};text-transform:uppercase}
.sub{font-size:3.6mm;font-weight:700;color:${PINE};margin-top:2.4mm}
.steps{position:absolute;left:24mm;right:24mm;top:58mm;display:flex;flex-direction:column;gap:6mm}
.st{display:flex;gap:4.5mm;align-items:flex-start}.st b{flex:none;width:9mm;height:9mm;border-radius:50%;background:${ROSE};color:${CREAM};font-family:Fr;font-weight:700;font-size:5mm;display:flex;align-items:center;justify-content:center}
.st h3{font-family:Fr;font-weight:700;font-size:4.7mm;margin:0 0 .6mm;color:${BERRY}}.st p{margin:0;font-size:3.9mm;line-height:1.36;text-wrap:pretty}
.sz{position:absolute;left:24mm;right:24mm;display:grid;grid-template-columns:1fr 1fr;gap:6mm}
.sz div{background:#fff;border:.35mm solid ${PLUM};border-radius:3mm;padding:3.5mm 4.5mm;font-size:3.5mm;line-height:1.4}.sz b{font-family:Fr;font-weight:700;font-size:4.6mm;color:${BERRY};display:block}
`;
function grid(W, H, items, cols, rows, w, h, gx, gy, fn, title, start, foot) {
  const gw = cols * w + (cols - 1) * gx, gh = rows * h + (rows - 1) * gy, x0 = (W - gw) / 2, y0 = (H - gh) / 2;
  const els = items.map((d, i) => `<div class=tag style="left:${x0 + (i % cols) * (w + gx)}mm;top:${y0 + Math.floor(i / cols) * (h + gy)}mm">${fn(d, start + i)}</div>`).join('');
  return `<div class=page><div class=top>${title}</div>${els}<div class=foot>${foot} · print at 100% (actual size) · © ${SHOP} · personal use only</div></div>`;
}
function guidePage() {
  const sz = `<div class=sz style="top:160mm"><div><b>Cards · 8</b>3.75 × 5 in (95.25 × 127 mm)<br>Pages 1 and 2 · 4 per page · To and From lines</div><div><b>Gift tags · 18</b>2.25 × 3.25 in (57.15 × 82.55 mm)<br>Pages 3 and 4 · 9 per page · punch the hole</div><div style="grid-column:1/3"><b>Ideas</b>Tie a tag to a treat bag, a jar of cookies, a bunch of flowers or a bottle. Slip a card in a lunchbox, a school bag or the mail. Both sizes suit class Valentine swaps, galentine and family gifts.</div></div>`;
  return `<div class="page guide"><div class=frame></div><div class=g><div class=kick>Print and cut</div><h1>Botanical <em>Valentine</em> Set</h1><div class=sub>Four steps from your printer to the gift</div></div>
  <div class=steps>
   <div class=st><b>1</b><div><h3>Print at actual size</h3><p>Choose 100% or "actual size" in the print dialog, not "fit to page". Use white or cream card stock, about 160 to 250 gsm (65 to 110 lb), so the cards and tags hold their shape.</p></div></div>
   <div class=st><b>2</b><div><h3>Cut along the grey line</h3><p>Scissors work well, and a paper trimmer is quick for the straight sides. Snip the corners round or angled to follow the grey line.</p></div></div>
   <div class=st><b>3</b><div><h3>Punch the tag hole</h3><p>Punch the small grey circle at the top of each tag with a hole punch, then thread on baker's twine, ribbon or thin string. The cards need no folding: they stand alone as flat Valentine cards.</p></div></div>
   <div class=st><b>4</b><div><h3>Write your note</h3><p>Fill in the To and From lines with a pen, gel pen or paint pen, and use the blank back of a card for a longer message. Print again whenever you need more.</p></div></div>
  </div>${sz}<div class=foot style="bottom:13mm">© ${SHOP} · personal use only · printing, card stock and twine not included</div></div>`;
}
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  fs.mkdirSync('bundle', { recursive: true });
  for (const [key, [W, H]] of Object.entries(PAPER)) {
    const t = n => `Botanical Valentine · <i>${n}</i>`;
    const card = (d, i) => cardSVG(d, i), tag = (d, i) => tagSVG(d, i);
    const pages = [
      grid(W, H, CARDS.slice(0, 4), 2, 2, CW, CH, 4, 4, card, `${t('Cards')} · 1 of ${N}`, 0, 'Cut on the grey line'),
      grid(W, H, CARDS.slice(4), 2, 2, CW, CH, 4, 4, card, `${t('Cards')} · 2 of ${N}`, 4, 'Cut on the grey line'),
      grid(W, H, TAGS.slice(0, 9), 3, 3, TW, TH, 4, 4, tag, `${t('Gift tags')} · 3 of ${N}`, 8, 'Cut on the grey line · punch the circle'),
      grid(W, H, TAGS.slice(9), 3, 3, TW, TH, 4, 4, tag, `${t('Gift tags')} · 4 of ${N}`, 17, 'Cut on the grey line · punch the circle'),
      guidePage()];
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
