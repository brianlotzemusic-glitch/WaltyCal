const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
const D=path.join(__dirname,'bundle/SVG'), OUT=path.join(__dirname,'listing-images');
const svgs = fs.readdirSync(D).filter(f=>f.endsWith('.svg')).sort().map(f=>fs.readFileSync(path.join(D,f),'utf8').replace(/width="[^"]*" height="[^"]*"/,'width="100%" height="100%"'));
const names=['Bat Wing Tree','Santa Hat Bat','Candy Cane Bat','Bat Garland','Holly Bat Wreath','Bat Wing Star'];
const tint=(s,c)=>s.replace('fill="#000"',`fill="${c}"`);
const base=`body{margin:0;width:1500px;height:1125px;font-family:Georgia,'DejaVu Serif',serif;overflow:hidden}`;
const thumbCols=['#f2ece0','#e0384b','#f2ece0','#7fd19a','#7fd19a','#f2c94c'];
const pages = {
 '1-thumbnail': `<style>${base} body{background:radial-gradient(circle at 50% 40%,#1f3a2e,#0c1611);color:#f4efe4}
  .g{display:grid;grid-template-columns:repeat(3,330px);gap:40px 60px;position:absolute;left:195px;top:240px}
  h1{position:absolute;top:36px;width:100%;text-align:center;font-size:92px;margin:0;letter-spacing:2px;font-weight:normal}
  h1 span{color:#e0384b}
  .s{position:absolute;top:150px;width:100%;text-align:center;font-size:36px;color:#9fd8b0;letter-spacing:6px}
  .b{position:absolute;bottom:36px;width:100%;text-align:center;font-size:34px;color:#e8e2d4}</style>
  <h1>Bat <span>Christmas</span></h1><div class=s>6 SVG CUT FILES · GOTHIC HOLIDAY</div>
  <div class=g>${svgs.map((s,i)=>`<div style="height:340px">${tint(s,thumbCols[i])}</div>`).join('')}</div>
  <div class=b>SVG · DXF · PNG &nbsp;|&nbsp; Cricut &amp; Silhouette ready</div>`,
 '2-whats-included': `<style>${base} body{background:#f6f3ee;color:#222}
  .g{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;padding:150px 80px 0}
  .c{text-align:center;font-size:28px} .c div{height:360px;padding:10px}
  h1{position:absolute;top:35px;width:100%;text-align:center;font-size:60px;margin:0;font-weight:normal}</style>
  <h1>What's included</h1><div class=g>${svgs.map((s,i)=>`<div class=c><div>${s}</div>${names[i]}</div>`).join('')}</div>`,
 '3-formats': `<style>${base} body{background:#13201a;color:#f4efe4;display:flex;flex-direction:column;justify-content:center;align-items:center}
  h1{font-size:64px;font-weight:normal;margin:0 0 50px} li{font-size:38px;margin:18px 0;list-style:none} b{color:#e0384b}</style>
  <h1>Instant digital download</h1><ul>
  <li><b>SVG</b> — Cricut Design Space, Silhouette Designer Edition</li>
  <li><b>DXF</b> — Silhouette Basic Edition, laser software</li>
  <li><b>PNG</b> — 1800 × 1800, transparent background (6 in at 300 DPI)</li>
  <li>Single-layer, one clean cut path per design</li>
  <li>No physical item will be shipped</li></ul>`,
 '4-color-ideas': `<style>${base} body{background:#fff}
  .g{display:grid;grid-template-columns:repeat(3,1fr);height:100%}
  .g div{padding:70px;display:flex;align-items:center}</style><div class=g>
  ${[['#0f2a1f','#f4efe4'],['#ffffff','#b3132b'],['#1a1a1a','#c9a227'],['#b3132b','#111111'],['#f4efe4','#145a32'],['#0b1530','#f2c94c']].map(([bg,fg],i)=>`<div style="background:${bg}">${tint(svgs[i],fg)}</div>`).join('')}</div>`,
};
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1500,height:1125},deviceScaleFactor:2});
for(const [n,h] of Object.entries(pages)){await p.setContent(h);await p.screenshot({path:path.join(OUT,`${n}.png`)});}
await b.close();})();
