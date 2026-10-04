// Listing images (3000x2250) from the real PDF pages (pdftoppm) and the stitched renders in art/ (stitch.py).
// Run from this folder after build.js and stitch.py: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const os = require('os');
const { execFileSync } = require('child_process');
const D = JSON.parse(fs.readFileSync('motifs.json', 'utf8'));
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf';
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'wcx-'));
const L = 'bundle/woodland-christmas-cross-stitch-US-Letter.pdf', A = 'bundle/woodland-christmas-cross-stitch-A4.pdf';
execFileSync('pdftoppm', ['-r', '110', '-png', '-f', '1', '-l', '7', L, path.join(tmp, 'L')]);
execFileSync('pdftoppm', ['-r', '110', '-png', '-f', '17', '-l', '17', L, path.join(tmp, 'L')]);
execFileSync('pdftoppm', ['-r', '110', '-png', '-f', '1', '-l', '1', A, path.join(tmp, 'A')]);
execFileSync('pdftoppm', ['-r', '300', '-png', '-f', '5', '-l', '5', L, path.join(tmp, 'Z')]);
const B64 = f => `data:image/png;base64,${fs.readFileSync(f).toString('base64')}`;
const pg = n => B64(path.join(tmp, `L-${String(n).padStart(2, '0')}.png`));
const hoop = (k, mono) => B64(`art/hoop-${k}-${mono ? 'mono' : 'colour'}.png`);
const font = f => `data:font/ttf;base64,${fs.readFileSync(path.join('fonts', f)).toString('base64')}`;
const base = `@font-face{font-family:Fr;font-weight:900;src:url(${font('Fraunces-900.ttf')})}
@font-face{font-family:Fr;font-weight:700;src:url(${font('Fraunces-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${font('Nunito-800.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${font('Nunito-700.ttf')})}
body{margin:0;width:1500px;height:1125px;overflow:hidden;position:relative;font-family:Nu;color:${PLUM}}
.paper{position:absolute;background:#fff;box-shadow:0 16px 36px rgba(0,0,0,.45),0 3px 8px rgba(0,0,0,.3);background-size:cover}
.h{position:absolute;filter:drop-shadow(0 14px 18px rgba(0,0,0,.5))}
.h img{width:100%;display:block}
.rib{position:absolute;width:5px;background:${BERRY};box-shadow:0 0 0 1px rgba(0,0,0,.25)}
.wood{position:absolute;inset:0;background:
  repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 3px,transparent 3px 11px),
  repeating-linear-gradient(90deg,rgba(0,0,0,.10) 0 1px,transparent 1px 47px,rgba(0,0,0,.06) 47px 49px,transparent 49px 121px),
  linear-gradient(90deg,#3a2a24,#4a352b 30%,#3d2c25 55%,#4b372d 80%,#392922)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 55%,transparent 40%,rgba(28,12,32,.6));pointer-events:none}
.tagp{position:absolute;font-family:Fr;font-weight:900;font-size:30px;color:${PLUM};background:${GOLD};padding:6px 20px;border-radius:30px;z-index:3;white-space:nowrap}`;
// a hoop hanging from a ribbon: x,y = top-left of the hoop, d = diameter
const hang = (k, x, y, d, mono = false, rot = 0, rib = 0) => `${rib ? `<div class=rib style="left:${x + d / 2 - 2.5}px;top:${y - rib}px;height:${rib + 6}px"></div>` : ''}
  <div class=h style="left:${x}px;top:${y}px;width:${d}px;transform:rotate(${rot}deg)"><img src="${hoop(k, mono)}"></div>`;
// small code-drawn props: pine sprig and a skein of floss
const sprig = (x, y, w, rot) => `<svg class=h style="left:${x}px;top:${y}px;width:${w}px;transform:rotate(${rot}deg)" viewBox="0 0 200 80">
  <path d="M5 40 L195 40" stroke="#5b3a26" stroke-width="5"/>${Array.from({ length: 18 }, (_, i) => { const xx = 15 + i * 10; return `<path d="M${xx} 40 L${xx + 14} ${18 + (i % 3) * 3}M${xx} 40 L${xx + 14} ${62 - (i % 3) * 3}" stroke="#2f5a3e" stroke-width="4" stroke-linecap="round"/>`; }).join('')}
  <circle cx="60" cy="52" r="7" fill="${BERRY}"/><circle cx="72" cy="48" r="7" fill="#a3243a"/></svg>`;
const skein = (x, y, w, col, rot) => `<svg class=h style="left:${x}px;top:${y}px;width:${w}px;transform:rotate(${rot}deg)" viewBox="0 0 120 60">
  <rect x="4" y="12" width="112" height="36" rx="16" fill="${col}"/>${Array.from({ length: 12 }, (_, i) => `<path d="M${12 + i * 8.5} 14 L${12 + i * 8.5} 46" stroke="rgba(255,255,255,.18)" stroke-width="2.5"/>`).join('')}
  <rect x="44" y="8" width="32" height="44" rx="3" fill="#f4efe4"/><rect x="44" y="20" width="32" height="5" fill="${BERRY}"/></svg>`;

const pages = {
  '1-thumbnail': `<style>${base}
   .bg{position:absolute;inset:0;background:url(${B64('art/bg-scene.png')}) center/cover}
   .h{filter:drop-shadow(0 18px 22px rgba(0,0,0,.55)) drop-shadow(0 4px 6px rgba(0,0,0,.4))}
   .band{position:absolute;left:0;right:0;bottom:0;height:200px;background:linear-gradient(rgba(44,27,54,.94),#2c1b36);display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 -8px 24px rgba(0,0,0,.45);z-index:5}
   .band h1{margin:0;font-family:Fr;font-weight:900;font-size:96px;line-height:1;color:${CREAM}}.band h1 em{font-style:normal;color:${GOLD}}
   .band p{margin:12px 0 0;font-size:29px;letter-spacing:5px;color:${GOLD};font-weight:800}
   .badge{position:absolute;z-index:6;right:40px;top:36px;width:220px;height:220px;border-radius:50%;background:${BERRY};color:${CREAM};display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 10px 26px rgba(0,0,0,.45);border:6px solid ${GOLD};transform:rotate(8deg)}
   .badge b{font-family:Fr;font-weight:900;font-size:90px;line-height:.9}.badge span{font-size:24px;font-weight:800;letter-spacing:2px;text-align:center;line-height:1.15}</style>
   <div class=bg></div>
   ${hang('stag', 470, 60, 500, false, -2)}${hang('fox', 990, 250, 420, false, 5)}${hang('owl', 80, 420, 420, false, -6)}
   ${hang('pine', 560, 560, 330, false, 4)}
   <div class=band><h1>Christmas <em>Cross Stitch</em></h1><p>12 WOODLAND MINI ORNAMENTS · PDF PATTERN</p></div>
   <div class=badge><b>12</b><span>CHARTS<br>× 2 VERSIONS</span></div>`,

  '2-whats-included': `<style>${base} body{background:${CREAM}}
   h1{position:absolute;top:26px;width:100%;text-align:center;margin:0;font-family:Fr;font-weight:900;font-size:72px}
   h1 em{font-style:normal;color:${BERRY}}
   .sub{position:absolute;top:118px;width:100%;text-align:center;font-size:29px;color:${PINE};font-weight:800;letter-spacing:1px}
   .row{position:absolute;top:190px;left:34px;right:34px;display:flex;justify-content:space-between}
   .it{width:225px;text-align:center}.it .paper{position:relative;width:225px;height:291px;border-radius:3px;box-shadow:0 10px 24px rgba(44,27,54,.28)}
   .it b{display:block;font-family:Fr;font-size:27px;margin-top:16px;line-height:1.1}.it span{display:block;font-size:20px;color:${PINE};margin-top:5px;font-weight:700;line-height:1.25}
   .feat{position:absolute;top:640px;left:34px;right:34px;display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
   .feat>div{background:#fff;border:3px solid ${PLUM};border-radius:22px;display:flex;align-items:center;gap:18px;padding:22px 22px}
   .feat img{width:150px;height:150px;flex:none}
   .feat b{display:block;font-family:Fr;font-weight:900;font-size:33px;color:${BERRY};line-height:1.05}
   .feat span{font-size:23px;font-weight:700;color:${PINE}}
   .strip{position:absolute;top:900px;left:34px;right:34px;display:flex;justify-content:space-between}
   .strip img{width:110px;height:110px}
   .tail{position:absolute;top:1050px;width:100%;text-align:center;font-size:25px;color:${PINE};font-weight:700}</style>
   <h1>What's <em>included</em></h1><div class=sub>28-page pdf pattern · US Letter and A4 · instant download</div>
   <div class=row>
    ${[[pg(1), 'Cover', 'all 12 ornaments'], [pg(2), 'Contents', 'every motif, both versions'], [pg(3), 'How to', 'stitch + finish ornaments'],
       [pg(4), 'Shopping list', '10 DMC colours'], [pg(5), '12 colour charts', 'symbols + colour, key'], [pg(17), '12 one-colour', 'all in one floss']]
      .map(([u, t, s]) => `<div class=it><div class=paper style="background-image:url(${u})"></div><b>${t}</b><span>${s}</span></div>`).join('')}
   </div>
   <div class=feat>${[['robin', 'Mini ornaments', `about ${D.ranges.in14} on 14-count`], ['lantern', 'Easy to read', 'big grid, symbols, centre arrows'], ['snowflake', 'Full stitches only', '2 strands, no backstitch']]
     .map(([k, t, s]) => `<div><img src="${hoop(k, false)}"><div><b>${t}</b><span>${s}</span></div></div>`).join('')}</div>
   <div class=strip>${D.motifs.map(m => `<img src="${hoop(m.key, false)}">`).join('')}</div>
   <div class=tail>fox · owl · stag · robin · toadstool · pine · moon & star · holly · snowflake · lantern · cottage · acorn</div>`,

  '3-chart-closeup': `<style>${base} body{background:${PLUM};color:${CREAM}}
   .zoom{position:absolute;left:330px;top:500px;width:560px;height:560px;border-radius:50%;overflow:hidden;border:12px solid ${GOLD};box-shadow:0 18px 40px rgba(0,0,0,.6);background:#fff url(${B64(path.join(tmp, 'Z-05.png'))}) no-repeat;background-size:2000px auto;background-position:-500px -230px}
   h1{position:absolute;left:950px;top:60px;margin:0;font-family:Fr;font-weight:900;font-size:62px;line-height:1.05;color:${CREAM}}
   h1 em{font-style:normal;color:${GOLD}}
   ul{position:absolute;left:950px;top:250px;margin:0;padding:0;list-style:none;width:510px}
   li{font-size:29px;margin:0 0 24px;line-height:1.28;padding-left:44px;position:relative}
   li::before{content:'';position:absolute;left:0;top:9px;width:22px;height:22px;border-radius:50%;background:${GOLD}}
   li b{color:${GOLD}}</style>
   <div class=paper style="left:50px;top:40px;width:640px;height:828px;background-image:url(${pg(5)})"></div><div class=zoom></div>
   <h1>Big, clear<br><em>charts</em></h1>
   <ul><li><b>One page per ornament</b>, the grid as large as the page allows</li>
   <li><b>A symbol in every square</b>, plus the colour fill</li>
   <li><b>Bold lines every 10</b>, row and column numbers</li>
   <li><b>Centre arrows</b> on all four sides</li>
   <li><b>Floss key</b> with DMC numbers, stitch counts, skeins, and the finished size on 14 and 18-count</li></ul>`,

  '4-colour-vs-one-colour': `<style>${base} body{background:#fbf6ea}
   h1{position:absolute;top:34px;width:100%;text-align:center;margin:0;font-family:Fr;font-weight:900;font-size:66px}
   h1 em{font-style:normal;color:${BERRY}}
   .sub{position:absolute;top:122px;width:100%;text-align:center;font-size:29px;color:${PINE};font-weight:800}
   .col{position:absolute;top:200px;width:700px;text-align:center}
   .col b{display:block;font-family:Fr;font-weight:900;font-size:40px;margin-bottom:10px}
   .col span{display:block;font-size:24px;color:${PINE};font-weight:700}
   .pair{position:absolute;top:290px;display:grid;grid-template-columns:repeat(2,1fr);gap:16px;width:690px}
   .pair img{width:100%;display:block;filter:drop-shadow(0 8px 10px rgba(0,0,0,.3))}
   .vs{position:absolute;left:705px;top:560px;width:90px;height:90px;border-radius:50%;background:${PLUM};color:${GOLD};font-family:Fr;font-weight:900;font-size:38px;display:flex;align-items:center;justify-content:center}</style>
   <h1>Colour <em>or one colour</em></h1>
   <div class=sub>every ornament comes as both charts: pick one, or stitch a matching set</div>
   <div class=col style="left:40px"><b>Colour</b><span>3 to 6 DMC colours each, 10 in all</span></div>
   <div class=col style="left:760px"><b>One colour</b><span>DMC 3371, or any single shade you love</span></div>
   <div class=pair style="left:45px">${['fox', 'cottage', 'holly', 'acorn'].map(k => `<img src="${hoop(k, false)}">`).join('')}</div>
   <div class=pair style="left:765px">${['fox', 'cottage', 'holly', 'acorn'].map(k => `<img src="${hoop(k, true)}">`).join('')}</div>
   <div class=vs>vs</div>`,
};

(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  fs.mkdirSync('listing-images', { recursive: true });
  for (const [n, h] of Object.entries(pages)) {
    await p.setContent(`<!doctype html><meta charset=utf-8>${h}`, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: `listing-images/${n}.png` });
  }
  await b.close(); fs.rmSync(tmp, { recursive: true });
})();
