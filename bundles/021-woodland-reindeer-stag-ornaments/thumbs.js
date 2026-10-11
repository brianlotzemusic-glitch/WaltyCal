// Listing images (3000x2250). Run from this folder: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs');
const dir = 'bundle/SVG';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort();
const svgs = files.map(f => fs.readFileSync(`${dir}/${f}`, 'utf8').replace(/width="[^"]*" height="[^"]*"/, 'width="100%" height="100%"'));
const names = ['Stag Head', 'Leaping Reindeer', 'Woodland Stag', 'Reindeer with Scarf', 'Stag Bauble', 'Reindeer Pair'];
const tint = (s, c) => s.replace('fill="#000"', `fill="${c}"`);
const D = (i, h, c, extra = '') => `<div style="height:${h}px;width:${h}px;${extra}">${tint(svgs[i], c)}</div>`;
// "hanging" ornament: wood-tone piece on a ribbon with a soft shadow
const HANG = (i, h, x, ribbon, c = '#c8935a') => `<div style="position:absolute;left:${x}px;top:0;width:${h}px;height:${ribbon + h}px">
  <div style="position:absolute;left:${h / 2 - 2}px;top:0;width:4px;height:${ribbon + h * 0.06}px;background:#b23a3a"></div>
  <div style="position:absolute;top:${ribbon}px;width:${h}px;height:${h}px;filter:drop-shadow(0 14px 16px rgba(0,0,0,.55))">${tint(svgs[i], c)}</div></div>`;
const base = `body{margin:0;width:1500px;height:1125px;font-family:Georgia,'DejaVu Serif',serif;overflow:hidden;position:relative}`;
const CREAM = '#f3ead8', GOLD = '#e7b866', PINE = '#1d3328';
const sprig = (x, y, r, flip) => `<div style="position:absolute;left:${x}px;top:${y}px;width:${r}px;height:${r * 0.4}px;border-radius:50%;background:radial-gradient(ellipse,#2f5a3f,#1b3a29 70%,transparent 72%);transform:rotate(${flip}deg)"></div>`;
const pages = {
 '1-thumbnail': `<style>${base} body{background:radial-gradient(ellipse at 50% 45%,#2e4a3a,#16271e 70%,#0e1a14);color:${CREAM}}
  h1{position:absolute;top:902px;width:100%;text-align:center;font-size:66px;margin:0;font-weight:normal;white-space:nowrap}
  .s{position:absolute;top:996px;width:100%;text-align:center;font-size:31px;color:${GOLD};letter-spacing:5px}
  .badge{position:absolute;width:190px;height:190px;border-radius:50%;background:${GOLD};color:${PINE};display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;box-shadow:0 10px 24px rgba(0,0,0,.5);transform:rotate(-8deg)}
  .badge b{font-size:78px;line-height:.9;font-weight:normal} .badge span{font-size:25px;letter-spacing:2px}
  .bough{position:absolute;top:-40px;left:-40px;right:-40px;height:120px;background:repeating-linear-gradient(100deg,#1c3a2a 0 14px,#25503a 14px 22px,#16301f 22px 34px);border-radius:0 0 50% 50%/0 0 60% 60%;box-shadow:0 10px 30px rgba(0,0,0,.6)}
  </style>
  ${HANG(1, 545, -6, 66, '#e2b77a')}${HANG(2, 545, 961, 66, '#e2b77a')}${HANG(4, 560, 470, 262)}
  <div class=bough></div>
  ${[[140, 60], [430, 70], [700, 55], [1000, 72], [1280, 60]].map(([x, y]) => `<div style="position:absolute;left:${x}px;top:${y}px;width:22px;height:22px;border-radius:50%;background:#b23a3a;box-shadow:26px 6px 0 #b23a3a,12px 22px 0 #9c2f2f"></div>`).join('')}
  <div class=badge style="left:150px;top:660px"><b>6</b><span>ORNAMENT<br>DESIGNS</span></div>
  <div class=badge style="left:1160px;top:660px;transform:rotate(8deg)"><span style="font-size:30px;line-height:1.35">SVG<br>DXF<br>PNG</span></div>
  <h1>Woodland Reindeer &amp; Stag Ornaments</h1><div class=s>SVG CUT FILES · CRICUT · SILHOUETTE · LASER</div>`,
 '2-whats-included': `<style>${base} body{background:#f4efe6;color:${PINE}}
  h1{position:absolute;top:26px;width:100%;text-align:center;font-size:60px;margin:0;font-weight:normal}
  .g{position:absolute;top:130px;left:40px;right:40px;display:grid;grid-template-columns:repeat(3,1fr);row-gap:20px}
  .c{text-align:center;font-size:27px;display:flex;flex-direction:column;align-items:center}
  .c>div:first-child{margin-bottom:8px}</style>
  <h1>What's included: 6 ornament designs</h1>
  <div class=g>${[0, 1, 2, 3, 4, 5].map(i => `<div class=c>${D(i, 400, PINE)}<div>${String(i + 1).padStart(2, '0')} ${names[i]}</div></div>`).join('')}</div>`,
 '3-formats': `<style>${base} body{background:${PINE};color:${CREAM};display:flex;flex-direction:column;justify-content:center;align-items:center}
  .strip{display:flex;gap:26px;margin:0 0 40px}
  h1{font-size:64px;font-weight:normal;margin:0 0 26px} li{font-size:36px;margin:15px 0;list-style:none} b{color:${GOLD}}</style>
  <div class=strip>${[0, 1, 2, 3, 4, 5].map(i => D(i, 200, i % 2 ? CREAM : GOLD)).join('')}</div>
  <h1>Instant digital download</h1><ul style="margin:0">
  <li><b>6 designs</b>, each with a hanging loop built in</li>
  <li><b>SVG</b> — Cricut Design Space, Silhouette Designer Edition</li>
  <li><b>DXF</b> — Silhouette Basic Edition, laser software (inches)</li>
  <li><b>PNG</b> — transparent background, 1800 px on the longest side</li>
  <li>Single-layer, one clean cut path per design, about 6 in</li>
  <li>Cardstock, felt, vinyl, or 3 mm wood and acrylic</li>
  <li>No physical item will be shipped</li></ul>`,
 '4-color-ideas': `<style>${base} body{background:#fff}
  .g{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;height:100%}
  .g>div{display:flex;align-items:center;justify-content:center;overflow:hidden}</style><div class=g>
  ${[[0, '#f3e6cf', '#7a4524'], [1, '#1d3328', '#e7b866'], [2, '#f7f3ec', '#2a4a3a'],
     [3, '#8e2a2e', '#f6eedf'], [4, 'radial-gradient(circle at 50% 50%,#fff4d6,#e7b866 90%)', '#3a2414'], [5, '#24324a', '#e9eef5']]
     .map(([i, bg, fg]) => `<div style="background:${bg}">${D(i, 440, fg)}</div>`).join('')}</div>`,
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  fs.mkdirSync('listing-images', { recursive: true });
  for (const [n, h] of Object.entries(pages)) { await p.setContent(h); await p.screenshot({ path: `listing-images/${n}.png` }); }
  await b.close();
})();
