// Listing images (3000x2250). Run from this folder: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs');
const dir = 'bundle/SVG';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort();
const raw = files.map(f => fs.readFileSync(`${dir}/${f}`, 'utf8'));
const svgs = raw.map(s => s.replace(/width="[^"]*" height="[^"]*"/, 'width="100%" height="100%"'));
const ar = raw.map(s => { const v = s.match(/viewBox="([^"]*)"/)[1].split(/\s+/).map(Number); return v[2] / v[3]; });
const names = ['Holy Family in the Stable', 'Manger Under the Star', 'Three Magi on Camels', 'The Good Shepherd', 'Star of Bethlehem', 'Herald Angel'];
const tint = (s, c) => s.replace('fill="#000"', `fill="${c}"`);
// a design at a given height (css px), keeping its aspect ratio
const D = (i, h, c) => `<div style="height:${h}px;width:${(h * ar[i]).toFixed(1)}px">${tint(svgs[i], c)}</div>`;
const base = `body{margin:0;width:1500px;height:1125px;font-family:Georgia,'DejaVu Serif',serif;overflow:hidden}`;
const CREAM = '#f4ead4', GOLD = '#e8c97a', NIGHT = '#16203a', INK = '#1d2540';
const pages = {
 '1-thumbnail': `<style>${base} body{background:radial-gradient(ellipse at 50% 42%,#2e3f66,#18223d 62%,#0f1629);color:${CREAM}}
  h1{position:absolute;top:28px;width:100%;text-align:center;font-size:88px;margin:0;letter-spacing:2px;font-weight:normal}
  .s{position:absolute;top:140px;width:100%;text-align:center;font-size:32px;color:${GOLD};letter-spacing:6px}
  .r{position:absolute;width:100%;display:flex;justify-content:center;align-items:flex-end;gap:46px}
  .b{position:absolute;bottom:24px;width:100%;text-align:center;font-size:31px;color:#dfe3ef}</style>
  <h1>Nativity SVG Bundle</h1><div class=s>6 SILHOUETTE CUT FILES · CHRISTMAS</div>
  <div class=r style="top:214px">${D(3, 380, CREAM)}${D(0, 470, GOLD)}${D(5, 380, CREAM)}</div>
  <div class=r style="top:716px;gap:60px">${D(1, 300, GOLD)}${D(2, 230, CREAM)}${D(4, 300, GOLD)}</div>
  <div class=b>SVG · DXF · PNG &nbsp;|&nbsp; Cricut, Silhouette &amp; laser ready</div>`,
 '2-whats-included': `<style>${base} body{background:#f4efe4;color:${INK}}
  h1{position:absolute;top:28px;width:100%;text-align:center;font-size:60px;margin:0;font-weight:normal}
  .r{position:absolute;width:100%;display:flex;justify-content:center;align-items:flex-end;gap:70px}
  .c{text-align:center;font-size:25px} .c>div{margin:0 auto 12px}</style>
  <h1>What's included: 6 designs</h1>
  <div class=r style="top:130px">${[0, 1, 2].map(i => `<div class=c>${D(i, i == 2 ? 250 : 400, INK)}${names[i]}</div>`).join('')}</div>
  <div class=r style="top:600px">${[3, 4, 5].map(i => `<div class=c>${D(i, 420, INK)}${names[i]}</div>`).join('')}</div>`,
 '3-formats': `<style>${base} body{background:${NIGHT};color:${CREAM};display:flex;flex-direction:column;justify-content:center;align-items:center}
  .strip{display:flex;align-items:flex-end;gap:30px;margin:0 0 40px}
  h1{font-size:64px;font-weight:normal;margin:0 0 26px} li{font-size:36px;margin:14px 0;list-style:none} b{color:${GOLD}}</style>
  <div class=strip>${[0, 1, 3, 4, 5].map((i, k) => D(i, 190, k % 2 ? GOLD : CREAM)).join('')}</div>
  <h1>Instant digital download</h1><ul style="margin:0">
  <li><b>6 designs</b> — Holy Family, manger, magi, shepherd, star &amp; angel</li>
  <li><b>SVG</b> — Cricut Design Space, Silhouette Designer Edition</li>
  <li><b>DXF</b> — Silhouette Basic Edition, laser software (inches)</li>
  <li><b>PNG</b> — transparent background, 1800 px on the longest side</li>
  <li>Single-layer, one clean cut path per design</li>
  <li>No physical item will be shipped</li></ul>`,
 '4-color-ideas': `<style>${base} body{background:#fff}
  .g{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;height:100%}
  .g>div{display:flex;align-items:center;justify-content:center;overflow:hidden}</style><div class=g>
  ${[[0, 'radial-gradient(circle at 50% 40%,#ffe7b0,#eeb862 80%)', INK, 430],
     [2, NIGHT, GOLD, 270],
     [5, '#f6eedf', '#8b2f3c', 430],
     [4, '#1d2a3a', '#e8c97a', 430],
     [3, '#e9e1cf', '#2f4a3a', 430],
     [1, '#8b2f3c', '#f6eedf', 430]].map(([i, bg, fg, h]) => `<div style="background:${bg}">${D(i, h, fg)}</div>`).join('')}</div>`,
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  fs.mkdirSync('listing-images', { recursive: true });
  for (const [n, h] of Object.entries(pages)) { await p.setContent(h); await p.screenshot({ path: `listing-images/${n}.png` }); }
  await b.close();
})();
