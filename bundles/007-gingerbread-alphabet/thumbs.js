// Listing images (3000x2250). Run from this folder: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs');
const dir = 'bundle/SVG';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort();
const B = JSON.parse(fs.readFileSync('bundle/bounds.json', 'utf8'));
const [bx, by, side] = B.box;
const paths = {};
files.forEach((f, i) => { paths[String.fromCharCode(65 + i)] = fs.readFileSync(`${dir}/${f}`, 'utf8').match(/ d="([^"]*)"/)[1]; });
// one letter, cropped to its own width, drawn at height h (css px); all letters share one scale
const L = (c, h, col) => {
  const [x0, x1] = B.x[c], pad = 14, w = x1 - x0 + 2 * pad;
  return `<svg viewBox="${x0 - pad} ${by} ${w} ${side}" height="${h}" width="${(h * w / side).toFixed(1)}"><path fill="${col}" fill-rule="evenodd" d="${paths[c]}"/></svg>`;
};
const word = (s, h, cols, gap = 6) => `<div style="display:flex;justify-content:center;align-items:flex-end;gap:${gap}px">${[...s].map((c, i) => L(c, h, cols[i % cols.length])).join('')}</div>`;
const AZ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
const GB = ['#99552a', '#ad6834'];   // gingerbread browns
const base = `body{margin:0;width:1500px;height:1125px;font-family:Georgia,'DejaVu Serif',serif;overflow:hidden}`;
const pages = {
 '1-thumbnail': `<style>${base} body{background:radial-gradient(circle at 50% 50%,#fbf3e6,#efdcc0);color:#7c1c22}
  h1{position:absolute;top:34px;width:100%;text-align:center;font-size:84px;margin:0;letter-spacing:2px;font-weight:normal}
  .s{position:absolute;top:145px;width:100%;text-align:center;font-size:34px;color:#2f5b3e;letter-spacing:6px}
  .w{position:absolute;top:238px;width:100%}
  .r{position:absolute;top:765px;width:100%}
  .b{position:absolute;bottom:34px;width:100%;text-align:center;font-size:34px;color:#5a3a22}</style>
  <h1>Gingerbread Letter Ornaments</h1><div class=s>FULL A–Z ALPHABET · 26 SVG CUT FILES</div>
  <div class=w>${word('NOEL', 480, GB, 10)}</div>
  <div class=r>${word('ABCDEFGHIJ', 210, ['#ad6834', '#7c1c22', '#2f5b3e'], 2)}</div>
  <div class=b>Spell any name · SVG · DXF · PNG &nbsp;|&nbsp; Cricut, Silhouette &amp; laser ready</div>`,
 '2-whats-included': `<style>${base} body{background:#f6efe3;color:#3b2616}
  h1{position:absolute;top:30px;width:100%;text-align:center;font-size:60px;margin:0;font-weight:normal}
  .g{position:absolute;top:140px;width:100%;display:flex;flex-direction:column;gap:22px}
  .f{position:absolute;bottom:22px;width:100%;text-align:center;font-size:28px;color:#6b4a30}</style>
  <h1>What's included: 26 letters, A to Z</h1><div class=g>
  ${[AZ.slice(0, 7), AZ.slice(7, 14), AZ.slice(14, 20), AZ.slice(20)].map(r => word(r, 205, ['#3b2616'], 26)).join('')}</div>
  <div class=f>Every letter is the same height, so names line up</div>`,
 '3-formats': `<style>${base} body{background:#3a2416;color:#f8eedf;display:flex;flex-direction:column;justify-content:center;align-items:center}
  h1{font-size:64px;font-weight:normal;margin:0 0 50px} li{font-size:38px;margin:18px 0;list-style:none} b{color:#f0c27b}</style>
  <h1>Instant digital download</h1><ul>
  <li><b>26 letters</b> — A to Z, one file per letter in each format</li>
  <li><b>SVG</b> — Cricut Design Space, Silhouette Designer Edition</li>
  <li><b>DXF</b> — Silhouette Basic Edition, laser software (inches)</li>
  <li><b>PNG</b> — 1800 × 1800, transparent background (6 in at 300 DPI)</li>
  <li>Single-layer, one clean cut path per letter, hanging loop built in</li>
  <li>No physical item will be shipped</li></ul>`,
 '4-color-ideas': `<style>${base} body{background:#fff}
  .g{display:grid;grid-template-columns:repeat(3,1fr);height:100%}
  .g div{display:flex;align-items:center;justify-content:center}</style><div class=g>
  ${[['#f4e6cf', '#9a552a', 'J'], ['#7c1c22', '#f7efe2', 'E'], ['#173f2c', '#e3c27e', 'S'], ['#f7f3ec', '#a41f2a', 'M'], ['#d9c3a2', '#5b3a22', 'K'], ['#1d2a3a', '#f1e7d6', 'A']].map(([bg, fg, c]) => `<div style="background:${bg}">${L(c, 410, fg)}</div>`).join('')}</div>`,
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  fs.mkdirSync('listing-images', { recursive: true });
  for (const [n, h] of Object.entries(pages)) { await p.setContent(h); await p.screenshot({ path: `listing-images/${n}.png` }); }
  await b.close();
})();
