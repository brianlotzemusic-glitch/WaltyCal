// Listing images (3000x2250). Run from this folder: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs');
const dir = 'bundle/SVG';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort();
const svgs = files.map(f => fs.readFileSync(`${dir}/${f}`, 'utf8').replace(/width="[^"]*" height="[^"]*"/, 'width="100%" height="100%"'));
const names = ['Snowflake Moth', 'Luna Moon Moth', 'Holly Wreath Moth', 'Moth Over Star', 'Holly &amp; Moon Corner', 'Moth Ornament'];
const tint = (s, c) => s.replace('fill="#000"', `fill="${c}"`);
const base = `body{margin:0;width:1500px;height:1125px;font-family:Georgia,'DejaVu Serif',serif;overflow:hidden}`;
const pages = {
 '1-thumbnail': `<style>${base} body{background:radial-gradient(circle at 50% 42%,#24372d,#0c1410);color:#f1e7cf}
  .g{display:grid;grid-template-columns:repeat(3,300px);gap:40px 70px;position:absolute;left:225px;top:250px}
  h1{position:absolute;top:40px;width:100%;text-align:center;font-size:84px;margin:0;letter-spacing:2px;font-weight:normal}
  .s{position:absolute;top:150px;width:100%;text-align:center;font-size:34px;color:#d4b46a;letter-spacing:6px}
  .b{position:absolute;bottom:40px;width:100%;text-align:center;font-size:34px;color:#e6dcc2}</style>
  <h1>Winter Moths &amp; Holly</h1><div class=s>6 SVG CUT FILES · DARK BOTANICAL CHRISTMAS</div>
  <div class=g>${svgs.map((s, i) => `<div style="height:300px">${tint(s, i % 2 ? '#e9c98a' : '#f1e7cf')}</div>`).join('')}</div>
  <div class=b>SVG · DXF · PNG &nbsp;|&nbsp; Cricut &amp; Silhouette ready</div>`,
 '2-whats-included': `<style>${base} body{background:#f4efe4;color:#1f2a22}
  .g{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;padding:150px 80px 0}
  .c{text-align:center;font-size:26px} .c div{height:360px;padding:10px}
  h1{position:absolute;top:35px;width:100%;text-align:center;font-size:60px;margin:0;font-weight:normal}</style>
  <h1>What's included</h1><div class=g>${svgs.map((s, i) => `<div class=c><div>${tint(s, '#1d2b22')}</div>${names[i]}</div>`).join('')}</div>`,
 '3-formats': `<style>${base} body{background:#132019;color:#f1e7cf;display:flex;flex-direction:column;justify-content:center;align-items:center}
  h1{font-size:64px;font-weight:normal;margin:0 0 50px} li{font-size:38px;margin:18px 0;list-style:none} b{color:#d4b46a}</style>
  <h1>Instant digital download</h1><ul>
  <li><b>SVG</b> — Cricut Design Space, Silhouette Designer Edition</li>
  <li><b>DXF</b> — Silhouette Basic Edition, laser software</li>
  <li><b>PNG</b> — 1800 × 1800, transparent background (6 in at 300 DPI)</li>
  <li>Single-layer, one clean cut path per design</li>
  <li>No physical item will be shipped</li></ul>`,
 '4-color-ideas': `<style>${base} body{background:#fff}
  .g{display:grid;grid-template-columns:repeat(3,1fr);height:100%}
  .g div{padding:70px}</style><div class=g>
  ${[['#14201a', '#efe4c8'], ['#ffffff', '#7a0f1e'], ['#0d3b2e', '#f1e9d8'], ['#2a1830', '#e6c9a8'], ['#e9e1cf', '#1d3a2a'], ['#5a0f1a', '#f3e7d3']].map(([bg, fg], i) => `<div style="background:${bg}">${tint(svgs[i], fg)}</div>`).join('')}</div>`,
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  for (const [n, h] of Object.entries(pages)) { await p.setContent(h); await p.screenshot({ path: `listing-images/${n}.png` }); }
  await b.close();
})();
