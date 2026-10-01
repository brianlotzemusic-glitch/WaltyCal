const { chromium } = require('playwright'); const fs=require('fs');
const svgs = fs.readdirSync('bundle/SVG').filter(f=>f.endsWith('.svg')).map(f=>fs.readFileSync('bundle/SVG/'+f,'utf8').replace(/width="[^"]*" height="[^"]*"/,'width="100%" height="100%"'));
const tint=(s,c)=>s.replace('fill="#000"',`fill="${c}"`);
const base=`body{margin:0;width:1500px;height:1125px;font-family:Georgia,'DejaVu Serif',serif;overflow:hidden}`;
const pages = {
 '1-thumbnail': `<style>${base} body{background:radial-gradient(circle at 50% 40%,#3d1427,#120a10);color:#eef}
  .g{display:grid;grid-template-columns:repeat(3,300px);gap:40px 70px;position:absolute;left:225px;top:250px}
  h1{position:absolute;top:40px;width:100%;text-align:center;font-size:84px;margin:0;letter-spacing:2px;font-weight:normal}
  .s{position:absolute;top:150px;width:100%;text-align:center;font-size:36px;color:#e9a9bf;letter-spacing:6px}
  .b{position:absolute;bottom:40px;width:100%;text-align:center;font-size:34px;color:#f0cfd9}</style>
  <h1>Gothic Christmas Ornaments</h1><div class=s>6 SVG CUT FILES · DARK HOLIDAY DECOR</div>
  <div class=g>${svgs.map(s=>`<div style="height:300px">${tint(s,'#f3e9ee')}</div>`).join('')}</div>
  <div class=b>SVG · DXF · PNG &nbsp;|&nbsp; Cricut &amp; Silhouette ready</div>`,
 '2-whats-included': `<style>${base} body{background:#f6f3ee;color:#222}
  .g{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;padding:150px 80px 0}
  .c{text-align:center;font-size:26px} .c div{height:360px;padding:10px}
  h1{position:absolute;top:35px;width:100%;text-align:center;font-size:60px;margin:0;font-weight:normal}</style>
  <h1>What's included</h1><div class=g>${svgs.map((s,i)=>`<div class=c><div>${s}</div>${['Moon &amp; Bat','Spiderweb','Coffin','Gothic Window','Bat Wing','Rose Window'][i]}</div>`).join('')}</div>`,
 '3-formats': `<style>${base} body{background:#1d1117;color:#f6eef2;display:flex;flex-direction:column;justify-content:center;align-items:center}
  h1{font-size:64px;font-weight:normal;margin:0 0 50px} li{font-size:38px;margin:18px 0;list-style:none} b{color:#e9a9bf}</style>
  <h1>Instant digital download</h1><ul>
  <li><b>SVG</b> — Cricut Design Space, Silhouette Designer Edition</li>
  <li><b>DXF</b> — Silhouette Basic Edition, laser software</li>
  <li><b>PNG</b> — 1800 × 1800, transparent background (6 in at 300 DPI)</li>
  <li>Single-layer, one clean cut path per design</li>
  <li>No physical item will be shipped</li></ul>`,
 '4-color-ideas': `<style>${base} body{background:#fff}
  .g{display:grid;grid-template-columns:repeat(3,1fr);height:100%}
  .g div{padding:70px}</style><div class=g>
  ${[['#120a10','#d9c7a0'],['#ffffff','#7a0f1e'],['#0d3b2e','#e6f2ea'],['#2a0d36','#d9c2ff'],['#c8ccd4','#14121a'],['#7a0f1e','#f2e6d0']].map(([bg,fg],i)=>`<div style="background:${bg}">${tint(svgs[i],fg)}</div>`).join('')}</div>`,
};
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1500,height:1125},deviceScaleFactor:2});
for(const [n,h] of Object.entries(pages)){await p.setContent(h);await p.screenshot({path:`listing-images/${n}.png`});}
await b.close();})();
