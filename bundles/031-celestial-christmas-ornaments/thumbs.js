// Listing images (3000x2250, opaque). Flat previews of the real SVG files only. Run here: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs');
const dir = 'bundle/SVG';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort();
const svgs = files.map(f => fs.readFileSync(`${dir}/${f}`, 'utf8').replace(/width="[^"]*" height="[^"]*"/, 'width="100%" height="100%"'));
const names = ['Crescent Moon & Stars', 'Star & Moon Bauble', 'Celestial Wreath', 'Moon Phases', 'Starburst', 'Moon Over Pines'];
const tint = (s, c) => s.replace('fill="#000"', `fill="${c}"`);
const D = (i, h, c) => `<div style="height:${h}px;width:${h}px">${tint(svgs[i], c)}</div>`;
const base = `body{margin:0;width:1500px;height:1125px;font-family:Georgia,'DejaVu Serif',serif;overflow:hidden}`;
const CREAM = '#f1e6cf', GOLD = '#e8c97a', NAVY = '#14213d';
const pages = {
 '1-all-designs': `<style>${base} body{background:${NAVY};color:${CREAM};display:flex;flex-direction:column;align-items:center}
  h1{font-size:68px;font-weight:normal;margin:34px 0 4px;white-space:nowrap} .s{font-size:30px;color:${GOLD};letter-spacing:5px;margin-bottom:12px}
  .g{display:grid;grid-template-columns:repeat(3,1fr);column-gap:30px;row-gap:40px;width:1440px;margin-top:24px}
  .g>div{display:flex;justify-content:center}</style>
  <h1>Celestial Christmas Ornaments</h1><div class=s>6 SVG CUT FILES · SVG · DXF · PNG</div>
  <div class=g>${[0, 1, 2, 3, 4, 5].map(i => `<div>${D(i, 415, GOLD)}</div>`).join('')}</div>`,
 '2-designs-named': `<style>${base} body{background:#f3ece2;color:${NAVY}}
  h1{position:absolute;top:26px;width:100%;text-align:center;font-size:60px;margin:0;font-weight:normal}
  .g{position:absolute;top:130px;left:40px;right:40px;display:grid;grid-template-columns:repeat(3,1fr);row-gap:20px}
  .c{text-align:center;font-size:27px;display:flex;flex-direction:column;align-items:center}
  .c>div:first-child{margin-bottom:8px}</style>
  <h1>What's included: 6 ornament designs</h1>
  <div class=g>${[0, 1, 2, 3, 4, 5].map(i => `<div class=c>${D(i, 400, NAVY)}<div>${String(i + 1).padStart(2, '0')} ${names[i]}</div></div>`).join('')}</div>`,
 '3-formats': `<style>${base} body{background:${NAVY};color:${CREAM};display:flex;flex-direction:column;justify-content:center;align-items:center}
  .strip{display:flex;gap:26px;margin:0 0 40px}
  h1{font-size:64px;font-weight:normal;margin:0 0 26px} li{font-size:36px;margin:15px 0;list-style:none} b{color:${GOLD}}</style>
  <div class=strip>${[0, 1, 2, 3, 4, 5].map(i => D(i, 200, i % 2 ? CREAM : GOLD)).join('')}</div>
  <h1>Instant digital download</h1><ul style="margin:0">
  <li><b>6 designs</b>, each with a hanging loop built in</li>
  <li><b>SVG</b>: Cricut Design Space, Silhouette Designer Edition</li>
  <li><b>DXF</b>: Silhouette Basic Edition, laser software (inches)</li>
  <li><b>PNG</b>: transparent background, 1800 px on the longest side</li>
  <li>Single layer, one cut path per design, about 6 in</li>
  <li>No physical item will be shipped</li></ul>`,
 '4-color-ideas': `<style>${base} body{background:#fff}
  .g{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;height:100%}
  .g>div{display:flex;align-items:center;justify-content:center;overflow:hidden}</style><div class=g>
  ${[[0, '#f1e6cf', '#14213d'], [1, '#14213d', '#e8c97a'], [2, '#f7f3ec', '#111111'],
     [3, '#1c2333', '#f1e6cf'], [4, '#f1e6cf', '#8b2f3c'], [5, '#e8eef3', '#2f4a3a']]
     .map(([i, bg, fg]) => `<div style="background:${bg}">${D(i, 440, fg)}</div>`).join('')}</div>`,
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  fs.mkdirSync('listing-images', { recursive: true });
  for (const [n, h] of Object.entries(pages)) { await p.setContent(h); await p.screenshot({ path: `listing-images/${n}.png` }); }
  await b.close();
})();
