// Listing images (3000x2250). Run from this folder: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs');
const dir = 'bundle/SVG';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort();
const svgs = files.map(f => fs.readFileSync(`${dir}/${f}`, 'utf8').replace(/width="[^"]*" height="[^"]*"/, 'width="100%" height="100%"'));
const names = ['Pine Bough', 'Fern Frond', 'Berry Sprig', 'Holly Crystal', 'Acorn &amp; Oak', 'Frosted Twig'];
const tint = (s, c) => s.replace('fill="#000"', `fill="${c}"`);
const F = (i, h, c) => `<div style="height:${h}px;width:${h}px">${tint(svgs[i], c)}</div>`;
const base = `body{margin:0;width:1500px;height:1125px;font-family:Georgia,'DejaVu Serif',serif;overflow:hidden}`;
const FROST = '#eef3f1', CREAM = '#f1e6cf', SAGE = '#d8ebe1', GOLD = '#e8c97a', PINE = '#2f4a3a', BERRY = '#8b2f3c';
const pages = {
 '1-thumbnail': `<style>${base} body{background:radial-gradient(ellipse at 50% 48%,#30524a,#17302b 62%,#0e1f1c);color:${FROST}}
  h1{position:absolute;top:34px;width:100%;text-align:center;font-size:78px;margin:0;letter-spacing:1px;white-space:nowrap;font-weight:normal}
  .s{position:absolute;top:142px;width:100%;text-align:center;font-size:29px;color:${GOLD};letter-spacing:6px}
  .g{display:grid;grid-template-columns:repeat(3,330px);gap:22px 90px;position:absolute;left:150px;top:222px}
  .b{position:absolute;bottom:30px;width:100%;text-align:center;font-size:32px;color:#dfe8e3}</style>
  <h1>Botanical Snowflake SVG Bundle</h1><div class=s>6 CUT FILES · PINE, FERN, BERRY, HOLLY, ACORN &amp; TWIG</div>
  <div class=g>${[0, 1, 2, 3, 4, 5].map(i => F(i, 330, i % 2 ? SAGE : FROST)).join('')}</div>
  <div class=b>SVG · DXF · PNG &nbsp;|&nbsp; Cricut, Silhouette &amp; laser ready</div>`,
 '2-whats-included': `<style>${base} body{background:#f2f5f2;color:#1d332e}
  .g{display:grid;grid-template-columns:repeat(3,1fr);gap:16px 20px;padding:140px 90px 0}
  .c{text-align:center;font-size:27px} .c>div{margin:0 auto 10px}
  h1{position:absolute;top:32px;width:100%;text-align:center;font-size:60px;margin:0;font-weight:normal}</style>
  <h1>What's included: 6 snowflakes</h1><div class=g>${names.map((n, i) => `<div class=c>${F(i, 400, '#1d332e')}${n}</div>`).join('')}</div>`,
 '3-formats': `<style>${base} body{background:#17302b;color:${FROST};display:flex;flex-direction:column;justify-content:center;align-items:center}
  .strip{display:flex;gap:34px;margin:0 0 44px}
  h1{font-size:64px;font-weight:normal;margin:0 0 26px} li{font-size:36px;margin:15px 0;list-style:none} b{color:${GOLD}}</style>
  <div class=strip>${[0, 1, 2, 3, 4, 5].map(i => F(i, 180, i % 2 ? SAGE : FROST)).join('')}</div>
  <h1>Instant digital download</h1><ul style="margin:0">
  <li><b>6 designs</b> — pine, fern, berry, holly, acorn &amp; twig snowflakes</li>
  <li><b>SVG</b> — Cricut Design Space, Silhouette Designer Edition</li>
  <li><b>DXF</b> — Silhouette Basic Edition, laser software (inches)</li>
  <li><b>PNG</b> — 1800 × 1800, transparent background (6 in at 300 DPI)</li>
  <li>Single-layer, one clean cut path per design</li>
  <li>No physical item will be shipped</li></ul>`,
 '4-color-ideas': `<style>${base} body{background:#fff}
  .g{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;height:100%}
  .g>div{display:flex;align-items:center;justify-content:center}</style><div class=g>
  ${[[0, PINE, FROST], [2, '#f4ecdc', BERRY], [3, '#dce9ec', '#1f3b4d'],
     [4, '#c9a77c', '#3b2a1c'], [1, BERRY, CREAM], [5, '#1d2a3a', GOLD]]
    .map(([i, bg, fg]) => `<div style="background:${bg}">${F(i, 440, fg)}</div>`).join('')}</div>`,
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  fs.mkdirSync('listing-images', { recursive: true });
  for (const [n, h] of Object.entries(pages)) { await p.setContent(h); await p.screenshot({ path: `listing-images/${n}.png` }); }
  await b.close();
})();
