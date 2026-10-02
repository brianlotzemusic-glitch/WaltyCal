// Listing images (3000x2250). Run from this folder: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs');
const dir = 'bundle/SVG';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort();
const raw = files.map(f => fs.readFileSync(`${dir}/${f}`, 'utf8'));
const svgs = raw.map(s => s.replace(/width="[^"]*" height="[^"]*"/, 'width="100%" height="100%"'));
const ar = raw.map(s => { const v = s.match(/viewBox="([^"]*)"/)[1].split(/\s+/).map(Number); return v[2] / v[3]; });
const names = ['Village Street Skyline', 'Moonlit Cottages Light Box', 'Cottage with Smoking Chimney', 'Starlit Chapel', 'Gingerbread House', 'Cabin Among Pines'];
const tint = (s, c) => s.replace('fill="#000"', `fill="${c}"`);
// a design at a given height (css px), keeping its aspect ratio
const D = (i, h, c) => `<div style="height:${h}px;width:${(h * ar[i]).toFixed(1)}px">${tint(svgs[i], c)}</div>`;
const base = `body{margin:0;width:1500px;height:1125px;font-family:Georgia,'DejaVu Serif',serif;overflow:hidden}`;
const CREAM = '#f4ead4', GOLD = '#e8c97a';
const pages = {
 '1-thumbnail': `<style>${base} body{background:radial-gradient(ellipse at 50% 45%,#3d2c55,#1b1229 70%,#130c1d);color:${CREAM}}
  h1{position:absolute;top:30px;width:100%;text-align:center;font-size:86px;margin:0;letter-spacing:2px;font-weight:normal}
  .s{position:absolute;top:140px;width:100%;text-align:center;font-size:33px;color:${GOLD};letter-spacing:6px}
  .hero{position:absolute;top:236px;left:0;width:100%;display:flex;justify-content:center}
  .row{position:absolute;top:790px;width:100%;display:flex;justify-content:center;align-items:flex-end;gap:34px}
  .b{position:absolute;bottom:26px;width:100%;text-align:center;font-size:32px;color:#e6dcef}</style>
  <h1>Christmas Village Silhouettes</h1><div class=s>6 SVG CUT FILES · PANELS &amp; STANDING HOUSES</div>
  <div class=hero>${D(0, 520, CREAM)}</div>
  <div class=row>${D(1, 215, GOLD)}${D(2, 235, CREAM)}${D(3, 235, GOLD)}${D(4, 235, CREAM)}${D(5, 235, GOLD)}</div>
  <div class=b>SVG · DXF · PNG &nbsp;|&nbsp; Cricut, Silhouette &amp; laser ready</div>`,
 '2-whats-included': `<style>${base} body{background:#f4efe6;color:#2c1b36}
  h1{position:absolute;top:30px;width:100%;text-align:center;font-size:60px;margin:0;font-weight:normal}
  .r{position:absolute;width:100%;display:flex;justify-content:center;align-items:flex-end;gap:60px}
  .c{text-align:center;font-size:25px} .c>div{margin:0 auto 12px}</style>
  <h1>What's included: 6 designs</h1>
  <div class=r style="top:150px">${[0, 1].map(i => `<div class=c>${D(i, i ? 380 : 330, '#2c1b36')}${names[i]}<br><span style="color:#7a6a80;font-size:21px">wide panel</span></div>`).join('')}</div>
  <div class=r style="top:650px;gap:40px">${[2, 3, 4, 5].map(i => `<div class=c>${D(i, 330, '#2c1b36')}${names[i]}<br><span style="color:#7a6a80;font-size:21px">stands on its base</span></div>`).join('')}</div>`,
 '3-formats': `<style>${base} body{background:#21162d;color:${CREAM};display:flex;flex-direction:column;justify-content:center;align-items:center}
  h1{font-size:64px;font-weight:normal;margin:0 0 44px} li{font-size:36px;margin:17px 0;list-style:none} b{color:${GOLD}}</style>
  <h1>Instant digital download</h1><ul>
  <li><b>6 designs</b> — 2 wide panels + 4 standing buildings</li>
  <li><b>SVG</b> — Cricut Design Space, Silhouette Designer Edition</li>
  <li><b>DXF</b> — Silhouette Basic Edition, laser software (inches)</li>
  <li><b>PNG</b> — transparent background, 1800 px on the longest side</li>
  <li>Single-layer, one clean cut path per design</li>
  <li>Standing pieces sit on a flat base strip (3 mm wood, acrylic or heavy card)</li>
  <li>No physical item will be shipped</li></ul>`,
 '4-color-ideas': `<style>${base} body{background:#fff}
  .g{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;height:100%}
  .g>div{display:flex;align-items:center;justify-content:center;overflow:hidden}</style><div class=g>
  ${[[0, 'radial-gradient(circle at 50% 60%,#ffe2a3,#f0b866 75%)', '#2c1b36', 210],
     [1, 'radial-gradient(circle at 50% 55%,#fff1c9,#f2c46f 80%)', '#2c1b36', 280],
     [2, '#2f4a3a', '#f1e6cf', 430],
     [3, '#1d2a3a', '#e8c97a', 430],
     [4, '#f3e3c8', '#8b4a26', 430],
     [5, '#8b2f3c', '#f6eedf', 430]].map(([i, bg, fg, h]) => `<div style="background:${bg}">${D(i, h, fg)}</div>`).join('')}</div>`,
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  fs.mkdirSync('listing-images', { recursive: true });
  for (const [n, h] of Object.entries(pages)) { await p.setContent(h); await p.screenshot({ path: `listing-images/${n}.png` }); }
  await b.close();
})();
