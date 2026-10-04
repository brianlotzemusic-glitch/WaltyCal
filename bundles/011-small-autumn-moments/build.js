// Builds the buyer files from icons.json, moments.json and stickers.json.
// Run from this folder: NODE_PATH=$(npm root -g) node build.js
//   bundle/small-autumn-moments-checklist-{US-Letter,A4}.pdf  4 pages:
//     1 checklist (cream), 2 write-your-own (cream), 3 checklist (ink saver, white), 4 write-your-own (ink saver)
//   bundle/small-autumn-moments-stickers-{US-Letter,A4}.pdf   1 page: the 6.75 x 9.25 in sheet, centred, with cut guides
//   bundle/small-autumn-moments-stickers-print-then-cut.png   2025 x 2775 px, transparent (DPI tag set by gen.py)
// Fails if any text block overflows its box.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const { icons } = JSON.parse(fs.readFileSync('icons.json', 'utf8'));
const M = JSON.parse(fs.readFileSync('moments.json', 'utf8'));
const ST = JSON.parse(fs.readFileSync('stickers.json', 'utf8'));
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf';
const FONT = f => `data:font/ttf;base64,${fs.readFileSync(path.join('fonts', f)).toString('base64')}`;
const SHOP = 'Duskwood Designs Co';
const byName = Object.fromEntries(icons.map(i => [i.name, i.id]));
const defs = `<svg width="0" height="0" style="position:absolute"><defs>${icons.map(i => `<symbol id="i${i.id}" viewBox="0 0 1000 1000">${i.svg}</symbol>`).join('')}</defs></svg>`;
const I = (name, style = '') => `<svg class=ic style="${style}" viewBox="0 0 1000 1000"><use href="#i${byName[name]}"/></svg>`;

const fontCSS = `
@font-face{font-family:Fr;font-weight:700;src:url(${FONT('Fraunces-700.ttf')})}
@font-face{font-family:Fr;font-weight:900;src:url(${FONT('Fraunces-900.ttf')})}
@font-face{font-family:Nu;font-weight:400;src:url(${FONT('Nunito-400.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${FONT('Nunito-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${FONT('Nunito-800.ttf')})}`;

const css = (W, H) => `${fontCSS}
@page{size:${W}mm ${H}mm;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:Nu;color:${PLUM};-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:${W}mm;height:${H}mm;position:relative;overflow:hidden;page-break-after:always;background:${CREAM}}
.page.light{background:#fff}
.ic{position:absolute;display:block}
.frame{position:absolute;inset:8mm;border:0.55mm solid ${PLUM};border-radius:5mm}
.frame::after{content:'';position:absolute;inset:1.4mm;border:0.22mm solid ${PINE};border-radius:3.8mm}
.head{position:absolute;top:14.5mm;left:36mm;right:36mm;text-align:center}
.kick{font-weight:800;font-size:3.1mm;letter-spacing:1.1mm;color:${PINE};text-transform:uppercase}
h1{font-family:Fr;font-weight:900;font-size:10.4mm;white-space:nowrap;line-height:1.15;margin:1.6mm 0 0;color:${PLUM};letter-spacing:-.1mm}
h1 em{font-style:normal;color:${BERRY}}
.sub{font-size:3.5mm;line-height:1.4;margin:2.4mm auto 0;color:${PINE};font-weight:700;max-width:128mm}
.cols{position:absolute;left:19mm;right:19mm;top:${H > 290 ? 56 : 54}mm;bottom:${H > 290 ? 49 : 50}mm;display:grid;grid-template-columns:1fr 1fr;column-gap:11mm}
.col{display:flex;flex-direction:column;justify-content:space-between;min-height:0;overflow:hidden}
.sec{display:flex;align-items:center;gap:2.2mm;margin:0 0 .6mm;padding-bottom:1.1mm;border-bottom:0.3mm dotted ${PINE}}
.sec .si{position:static;width:8mm;height:8mm;flex:none}
.sec b{font-family:Fr;font-weight:700;font-size:5.3mm;color:${BERRY};line-height:1}
.sec.second{margin-top:${H > 290 ? 5 : 3}mm}
.it{display:flex;align-items:flex-start;gap:2.6mm;font-size:3.72mm;line-height:1.3}
.box{flex:none;width:4.4mm;height:4.4mm;border:0.42mm solid ${PLUM};border-radius:1.1mm;background:#fff;margin-top:.15mm}
.light .box{background:none}
.foot{position:absolute;left:0;right:0;bottom:10.6mm;text-align:center;font-size:2.5mm;color:#6d5f73}
.ground{position:absolute;left:13mm;height:6mm}
/* write your own */
.rows{position:absolute;left:21mm;right:21mm;padding-bottom:4mm;display:flex;flex-direction:column;justify-content:space-between}
.row{display:flex;align-items:flex-end;gap:3mm}
.row .box{margin:0 0 .4mm}
.row .ln{flex:1;border-bottom:0.3mm solid ${PLUM};height:5.5mm;opacity:.75}
.row .dt{width:24mm;border-bottom:0.3mm solid ${PLUM};height:5.5mm;opacity:.75;position:relative}
.row .dt span{position:absolute;left:0;bottom:-3.6mm;font-size:2.2mm;color:#6d5f73;letter-spacing:.3mm}
/* sticker page */
.spage{background:#fff}
.sheet{position:absolute;width:171.45mm;height:234.95mm;left:${(W - 171.45) / 2}mm;top:${(H - 234.95) / 2 + (H > 290 ? 3 : 0)}mm}
.sheet>svg{width:100%;height:100%;display:block}
.sheet .cut{stroke:#b3a8b8;stroke-width:2.2}
.area{position:absolute;inset:0;border:0.2mm dashed #cfc6d3}
.shead{position:absolute;left:0;right:0;text-align:center}
.shead b{font-family:Fr;font-weight:700;font-size:4.6mm}.shead b em{font-style:normal;color:${BERRY}}
.shead span{display:block;font-size:2.7mm;color:#6d5f73;margin-top:.6mm}
`;

function header(kick, title, sub) {
  return `<div class=frame></div>
  ${I('oak sprig', 'left:11mm;top:10.5mm;width:27mm;height:27mm;transform:rotate(-8deg)')}
  ${I('moon', 'right:13mm;top:12.5mm;width:22mm;height:22mm')}
  <div class=head><div class=kick>${kick}</div><h1>${title}</h1><div class=sub>${sub}</div></div>`;
}

function footerArt(W, H) {
  const b = H - 15; // ground line y (mm)
  const at = (name, x, w, rise = 0, extra = '') => I(name, `left:${x}mm;top:${b - w + rise}mm;width:${w}mm;height:${w}mm;${extra}`);
  return `<svg class=ground style="top:${b - 3.2}mm;width:${W - 26}mm" viewBox="0 0 1000 30" preserveAspectRatio="none"><path d="M0 18 C150 8 300 26 500 16 S850 8 1000 18" fill="none" stroke="${PINE}" stroke-width="2.2" vector-effect="non-scaling-stroke"/></svg>
  ${at('mushrooms', 14, 25, 1.5)}${at('acorns', 41, 15, 1)}${at('rain boots', 59, 19, 1.2)}
  ${at('sleeping fox', W / 2 - 17, 34, 7)}
  ${at('lantern', W - 72, 22, 1.2)}${at('mug', W - 52, 16, 1)}${at('candle', W - 35, 21, 1.3)}
  <div class=foot>© ${SHOP} · personal use only · print at 100%</div>`;
}

function checklist(W, H, light) {
  const secs = M.sections.map((s, k) => `<div class="sec${k % 2 ? ' second' : ''}">${I(s.icon).replace('class=ic', 'class="ic si"')}<b>${s.name}</b></div>
    ${s.items.map(t => `<div class=it><i class=box></i><span>${t}</span></div>`).join('')}`);
  return `<div class="page${light ? ' light' : ''}">${header('A fall checklist', `Small <em>Autumn</em> Moments`,
    'Not a list of big plans: the small, real things that make the season. Tick each one off when it happens.')}
  <div class=cols><div class=col>${secs[0]}${secs[1]}</div><div class=col>${secs[2]}${secs[3]}</div></div>
  ${footerArt(W, H)}</div>`;
}

function blank(W, H, light) {
  const top = H > 290 ? 58 : 56, bot = H > 290 ? 49 : 50;
  const rows = Array.from({ length: 15 }, () => `<div class=row><i class=box></i><div class=ln></div><div class=dt><span>WHEN</span></div></div>`).join('');
  return `<div class="page${light ? ' light' : ''}">${header('Write your own', `My <em>Autumn</em> Moments`,
    'The little things you want to notice this season. Write them in, then tick them off as they happen.')}
  <div class=rows style="top:${top}mm;bottom:${bot}mm">${rows}</div>
  ${footerArt(W, H)}</div>`;
}

function stickerPage(W, H, name) {
  const sheetTop = (H - 234.95) / 2 + (H > 290 ? 3 : 0);
  return `<div class="page spage">
  <div class=shead style="top:${Math.max(7.5, sheetTop - 13)}mm"><b>Small <em>Autumn</em> Moments · sticker sheet</b><span>20 stickers · grey lines are cut guides (they sit on the white border)</span></div>
  <div class=sheet><div class=area></div>${ST.sheet_svg}</div>
  <div class=shead style="top:${sheetTop + 234.95 + 2.2}mm"><span>Sticker area 6.75 × 9.25 in (Cricut Print Then Cut size) on ${name} paper. Print at 100%. For Print Then Cut, upload the PNG file instead.</span></div></div>`;
}

const SIZES = { 'US-Letter': [215.9, 279.4, 'US Letter'], A4: [210, 297, 'A4'] };
async function overflow(p) {
  const o = await p.evaluate(() => [...document.querySelectorAll('.col,.head,.rows,.head h1')].filter(e => e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1)
    .map(e => `${e.className || e.tagName} ${e.scrollWidth}x${e.scrollHeight} > ${e.clientWidth}x${e.clientHeight}`));
  if (o.length) console.log(o.join('\n'));
  return o.length;
}
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  fs.mkdirSync('bundle', { recursive: true });
  let bad = 0;
  for (const [key, [W, H, name]] of Object.entries(SIZES)) {
    const docs = {
      [`small-autumn-moments-checklist-${key}.pdf`]: [checklist(W, H, false), blank(W, H, false), checklist(W, H, true), blank(W, H, true)],
      [`small-autumn-moments-stickers-${key}.pdf`]: [stickerPage(W, H, name)],
    };
    for (const [file, pages] of Object.entries(docs)) {
      await p.setContent(`<!doctype html><html><head><meta charset=utf-8><style>${css(W, H)}</style></head><body>${defs}${pages.join('')}</body></html>`, { waitUntil: 'load' });
      await p.evaluate(() => document.fonts.ready);
      const o = await overflow(p); bad += o;
      await p.pdf({ path: `bundle/${file}`, width: `${W}mm`, height: `${H}mm`, printBackground: true, preferCSSPageSize: true });
      console.log(`bundle/${file}${o ? `  OVERFLOW in ${o} boxes` : ''}`);
    }
  }
  // transparent print-then-cut PNG: 6.75 x 9.25 in at 300 DPI = 2025 x 2775 px
  const q = await b.newPage({ viewport: { width: 648, height: 888 }, deviceScaleFactor: 2025 / 648 });
  await q.setContent(`<!doctype html><meta charset=utf-8><style>${fontCSS} html,body{margin:0;background:transparent} svg{display:block;width:648px;height:888px}</style>${ST.sheet_svg}`);
  await q.evaluate(() => document.fonts.ready);
  await q.screenshot({ path: 'bundle/small-autumn-moments-stickers-print-then-cut.png', omitBackground: true });
  await b.close();
  if (bad) { console.error('text overflow'); process.exit(1); }
})();
