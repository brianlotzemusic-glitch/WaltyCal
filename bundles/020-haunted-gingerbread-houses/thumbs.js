// Listing images (3000x2250). Run from this folder: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs');
const dir = 'bundle/SVG';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort();
const raw = files.map(f => fs.readFileSync(`${dir}/${f}`, 'utf8'));
const svgs = raw.map(s => s.replace(/width="[^"]*" height="[^"]*"/, 'width="100%" height="100%"'));
const ar = raw.map(s => { const v = s.match(/viewBox="([^"]*)"/)[1].split(/\s+/).map(Number); return v[2] / v[3]; });
const names = ['Crooked Haunted House', 'Manor with Witch-Hat Tower', 'Spiderweb House', 'Haunted Gingerbread Village', 'Skull-Topped House', 'Haunted Ornament'];
const kinds = ['stands on its base', 'stands on its base', 'stands on its base', 'wide panel', 'stands on its base', 'hanging ornament'];
// exterior outline only (first subpath): used as the glow layer behind the cut-outs
const outer = s => s.replace(/ d="(M[^M]*)[^"]*"/, ' d="$1"');
const tint = (s, c) => s.replace('fill="#000"', `fill="${c}"`);
// a design at a given height (css px), keeping its aspect ratio
const D = (i, h, c, extra = '') => `<div style="height:${h}px;width:${(h * ar[i]).toFixed(1)}px;${extra}">${tint(svgs[i], c)}</div>`;
// "lit" piece: gingerbread-brown cut shape with a warm glow showing through the cut-outs
const LIT = (i, h, c = '#4a2c1a') => `<div style="position:relative;height:${h}px;width:${(h * ar[i]).toFixed(1)}px">
  <div style="position:absolute;inset:0">${tint(outer(svgs[i]), '#ffa940')}</div>
  <div style="position:absolute;inset:0;filter:drop-shadow(0 10px 14px rgba(0,0,0,.55))">${tint(svgs[i], c)}</div></div>`;
const base = `body{margin:0;width:1500px;height:1125px;font-family:Georgia,'DejaVu Serif',serif;overflow:hidden}`;
const CREAM = '#f4ead4', GOLD = '#f2b45a', PLUM = '#2a1a33';
const pages = {
 '1-thumbnail': `<style>${base} body{background:radial-gradient(ellipse at 50% 40%,#432a52,#1d1226 68%,#120b18);color:${CREAM}}
  h1{position:absolute;top:28px;width:100%;text-align:center;font-size:88px;margin:0;letter-spacing:1px;font-weight:normal}
  .s{position:absolute;top:136px;width:100%;text-align:center;font-size:32px;color:${GOLD};letter-spacing:6px}
  .shelf{position:absolute;left:40px;right:40px;top:880px;height:44px;background:linear-gradient(#6b4528,#4a2d18);border-radius:6px;box-shadow:0 14px 26px rgba(0,0,0,.6)}
  .hero{position:absolute;top:400px;left:0;width:100%;display:flex;justify-content:center;align-items:flex-end;gap:10px}
  .b{position:absolute;bottom:36px;width:100%;text-align:center;font-size:32px;color:#e6dcef}</style>
  <h1>Haunted Gingerbread Houses</h1><div class=s>6 SVG CUT FILES · GOTHMAS &amp; HALLOWEEN DECOR</div>
  <div class=shelf></div>
  <div class=hero style="top:auto;bottom:196px">${LIT(1, 540)}${LIT(0, 500)}${LIT(4, 540)}</div>
  <div class=b>SVG · DXF · PNG &nbsp;|&nbsp; Cricut, Silhouette &amp; laser ready</div>`,
 '2-whats-included': `<style>${base} body{background:#f4efe6;color:${PLUM}}
  h1{position:absolute;top:26px;width:100%;text-align:center;font-size:60px;margin:0;font-weight:normal}
  .g{position:absolute;top:130px;left:40px;right:40px;display:grid;grid-template-columns:repeat(3,1fr);row-gap:26px}
  .c{text-align:center;font-size:25px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:460px}
  .c>div:first-child{margin-bottom:12px} small{color:#7a6a80;font-size:21px}</style>
  <h1>What's included: 6 designs</h1>
  <div class=g>${[0, 1, 2, 3, 4, 5].map(i => `<div class=c>${i === 3 ? D(i, 175, PLUM, 'margin-bottom:100px') : D(i, 360, PLUM)}<div>${names[i]}<br><small>${kinds[i]}</small></div></div>`).join('')}</div>`,
 '3-formats': `<style>${base} body{background:#21162d;color:${CREAM};display:flex;flex-direction:column;justify-content:center;align-items:center}
  .strip{display:flex;align-items:flex-end;gap:26px;margin:0 0 40px}
  h1{font-size:64px;font-weight:normal;margin:0 0 26px} li{font-size:36px;margin:15px 0;list-style:none} b{color:${GOLD}}</style>
  <div class=strip>${D(0, 210, GOLD)}${D(1, 210, CREAM)}${D(2, 210, GOLD)}${D(4, 210, CREAM)}${D(5, 210, GOLD)}</div>
  <h1>Instant digital download</h1><ul style="margin:0">
  <li><b>6 designs</b> — 4 standing houses, 1 village panel, 1 ornament</li>
  <li><b>SVG</b> — Cricut Design Space, Silhouette Designer Edition</li>
  <li><b>DXF</b> — Silhouette Basic Edition, laser software (inches)</li>
  <li><b>PNG</b> — transparent background, 1800 px on the longest side</li>
  <li>Single-layer, one clean cut path per design</li>
  <li>Standing pieces sit on a flat base strip (3 mm wood, acrylic or heavy card)</li>
  <li>No physical item will be shipped</li></ul>`,
 '4-color-ideas': `<style>${base} body{background:#fff}
  .g{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;height:100%}
  .g>div{display:flex;align-items:center;justify-content:center;overflow:hidden}</style><div class=g>
  ${[[0, 'radial-gradient(circle at 50% 60%,#ffcf85,#f08a3c 78%)', '#2a1a33', 430],
     [1, '#2c1d3a', '#f2b45a', 430],
     [2, '#f3e3c8', '#7a4524', 430],
     [3, 'radial-gradient(circle at 50% 55%,#fff1c9,#f2b45a 85%)', '#2a1a33', 230],
     [4, '#1f2b26', '#d8e8c8', 430],
     [5, '#7d2433', '#f6eedf', 430]].map(([i, bg, fg, h]) => `<div style="background:${bg}">${D(i, h, fg)}</div>`).join('')}</div>`,
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  fs.mkdirSync('listing-images', { recursive: true });
  for (const [n, h] of Object.entries(pages)) { await p.setContent(h); await p.screenshot({ path: `listing-images/${n}.png` }); }
  await b.close();
})();
