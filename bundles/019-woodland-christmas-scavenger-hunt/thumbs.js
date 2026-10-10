// Listing images (3000x2250) from the real PDF pages, rasterised with pdftoppm.
// Run from this folder after build.js: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const os = require('os');
const { execFileSync } = require('child_process');
const { icons } = JSON.parse(fs.readFileSync('icons.json', 'utf8'));
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf';
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'hunt-'));
const PDF = 'bundle/woodland-christmas-scavenger-hunt-US-Letter.pdf', PDFA4 = 'bundle/woodland-christmas-scavenger-hunt-A4.pdf';
execFileSync('pdftoppm', ['-r', '200', '-png', PDF, path.join(tmp, 'L')]);
execFileSync('pdftoppm', ['-r', '120', '-png', '-f', '3', '-l', '3', PDFA4, path.join(tmp, 'A')]);
const B64 = f => `data:image/png;base64,${fs.readFileSync(path.join(tmp, f)).toString('base64')}`;
const pg = n => B64(`L-${n}.png`);
const font = f => `data:font/ttf;base64,${fs.readFileSync(path.join('fonts', f)).toString('base64')}`;
const I = id => `<svg viewBox="0 0 1000 1000" style="width:100%;height:100%;display:block">${icons[id].svg}</svg>`;
// Card crops from the US Letter pages (mm, from build.js): slots at x 9 / 111.95, y 9 / 143.7, card 94.95 x 126.7.
const MM = 200 / 25.4, PW = 215.9, PH = 279.4, CWm = (PW - 26) / 2, CHm = (PH - 26) / 2;
const CW = CWm * MM, CH = CHm * MM;
const card = (k, w, rot, x, y, z = 1) => { // k = 0..15 (15 = Hooray card), 16..19 = blank cards
  const page = 3 + Math.floor(k / 4), s = k % 4, sx = s % 2 ? PW / 2 + 4 : 9, sy = s > 1 ? PH / 2 + 4 : 9, sc = w / CW;
  return `<div class=card style="left:${x}px;top:${y}px;width:${w}px;height:${CH * sc}px;transform:rotate(${rot}deg);z-index:${z}">
    <div style="width:${CW}px;height:${CH}px;transform:scale(${sc});transform-origin:0 0;background-image:url(${pg(page)});background-size:${PW * MM}px ${PH * MM}px;background-position:-${sx * MM}px -${sy * MM}px"></div></div>`;
};
const base = `@font-face{font-family:Fr;font-weight:900;src:url(${font('Fraunces-900.ttf')})}
@font-face{font-family:Fr;font-weight:700;src:url(${font('Fraunces-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${font('Nunito-800.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${font('Nunito-700.ttf')})}
body{margin:0;width:1500px;height:1125px;overflow:hidden;position:relative;font-family:Nu;color:${PLUM}}
.card{position:absolute;background:#fff;border-radius:12px;box-shadow:0 18px 40px rgba(0,0,0,.45),0 3px 8px rgba(0,0,0,.3);transform-origin:50% 50%;overflow:hidden}
.wood{background:
  repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 3px,transparent 3px 11px),
  repeating-linear-gradient(90deg,rgba(0,0,0,.10) 0 1px,transparent 1px 47px,rgba(0,0,0,.06) 47px 49px,transparent 49px 121px),
  linear-gradient(90deg,#3a2a24,#4a352b 30%,#3d2c25 55%,#4b372d 80%,#392922)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 55%,transparent 45%,rgba(20,10,20,.55));pointer-events:none}
.paper{position:absolute;background:#fff;box-shadow:0 14px 30px rgba(0,0,0,.4);background-size:cover}
.prop{position:absolute;filter:drop-shadow(0 10px 12px rgba(0,0,0,.5))}`;

const pages = {
  '1-thumbnail': `<style>${base}
   .title{position:absolute;left:0;right:0;top:0;height:250px;background:linear-gradient(${PLUM},#3a2447);display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 8px 24px rgba(0,0,0,.4);z-index:20}
   .title h1{margin:0;font-family:Fr;font-weight:900;font-size:104px;line-height:1;color:${CREAM};letter-spacing:1px}
   .title h1 em{font-style:normal;color:${GOLD}}
   .title p{margin:12px 0 0;font-size:32px;letter-spacing:5px;color:${GOLD};font-weight:800}
   .badge{position:absolute;z-index:21;left:40px;bottom:40px;width:250px;height:250px;border-radius:50%;background:${BERRY};color:${CREAM};display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 10px 26px rgba(0,0,0,.45);border:6px solid ${GOLD};transform:rotate(-8deg)}
   .badge b{font-family:Fr;font-weight:900;font-size:110px;line-height:.9}.badge span{font-size:26px;font-weight:800;letter-spacing:2px;text-align:center;line-height:1.1}</style>
   <div class=wood style="position:absolute;inset:0"></div><div class=vig></div>
   <div class=paper style="left:40px;top:300px;width:420px;height:543px;background-image:url(${pg(8)});transform:rotate(-6deg)"></div>
   ${card(7, 330, -5, 400, 300, 2)}${card(0, 340, 3, 740, 280, 3)}${card(8, 330, 7, 1110, 320, 2)}
   ${card(15, 330, -3, 590, 690, 4)}
   <div class=prop style="left:960px;top:820px;width:230px;height:230px;transform:rotate(6deg);z-index:5">${I(21)}</div>
   <div class=prop style="left:1240px;top:850px;width:150px;height:150px;transform:rotate(-14deg);z-index:5">${I(13)}</div>
   <div class=title><h1>Christmas <em>Scavenger Hunt</em></h1><p>WOODLAND TREASURE HUNT FOR KIDS · PRINTABLE</p></div>
   <div class=badge><b>15</b><span>RHYMING<br>CLUES</span></div>`,

  '2-whats-included': `<style>${base} body{background:${CREAM}}
   h1{position:absolute;top:30px;width:100%;text-align:center;margin:0;font-family:Fr;font-weight:900;font-size:76px}
   h1 em{font-style:normal;color:${BERRY}}
   .sub{position:absolute;top:128px;width:100%;text-align:center;font-size:30px;color:${PINE};font-weight:800;letter-spacing:1px}
   .row{position:absolute;top:195px;left:36px;right:36px;display:flex;justify-content:space-between}
   .it{width:226px;text-align:center}.it .paper{position:relative;width:226px;height:292px;border-radius:4px}
   .it b{display:block;font-family:Fr;font-size:30px;margin-top:20px;line-height:1.1}.it span{display:block;font-size:22px;color:${PINE};margin-top:6px;font-weight:700}
   .feat{position:absolute;top:640px;left:40px;right:40px;display:grid;grid-template-columns:repeat(2,1fr);gap:26px}
   .feat>div{background:#fff;border:3px solid ${PLUM};border-radius:22px;display:flex;align-items:center;gap:26px;padding:20px 28px}
   .fi{width:110px;height:110px;flex:none}.feat b{display:block;font-family:Fr;font-weight:900;font-size:40px;color:${BERRY}}
   .feat span{font-size:26px;font-weight:700;color:${PINE}}</style>
   <h1>What's <em>included</em></h1><div class=sub>8 printable pages · US Letter + A4 pdf · instant download</div>
   <div class=row>
    ${[[1, 'How to play', 'setup in 5 steps'], [2, 'Answer key', 'hunt planner'], [3, '15 clue cards', 'rhymes, 4 per page'],
       [6, 'Hooray! card', 'for the treasure'], [7, '4 blank cards', 'write your own'], [8, 'Hunt tracker', 'colour as you go']]
      .map(([n, t, s]) => `<div class=it><div class=paper style="background-image:url(${pg(n)})"></div><b>${t}</b><span>${s}</span></div>`).join('')}
   </div>
   <div class=feat>${[[16, 'Ages 3 to 10', 'read aloud for little ones'], [10, 'Fits any home', 'skip spots, add your own'],
     [1, 'No spoilers', 'answers only on the key page'], [21, 'Ready in minutes', 'print, cut, hide, play']]
     .map(([i, t, d]) => `<div><div class=fi>${I(i)}</div><div><b>${t}</b><span>${d}</span></div></div>`).join('')}</div>`,

  '3-formats': `<style>${base} body{background:${PLUM};color:${CREAM}}
   h1{position:absolute;left:740px;top:150px;margin:0;font-family:Fr;font-weight:900;font-size:70px;line-height:1.05;color:${CREAM}}
   h1 em{font-style:normal;color:${GOLD}}
   ul{position:absolute;left:740px;top:340px;margin:0;padding:0;list-style:none;width:700px}
   li{font-size:33px;margin:0 0 24px;line-height:1.25;padding-left:46px;position:relative}
   li::before{content:'';position:absolute;left:0;top:10px;width:22px;height:22px;border-radius:50%;background:${GOLD}}
   li b{color:${GOLD}}
   .tag{position:absolute;font-family:Fr;font-weight:900;font-size:30px;color:${PLUM};background:${GOLD};padding:6px 18px;border-radius:30px;z-index:3}</style>
   <div class=paper style="left:70px;top:150px;width:470px;height:608px;background-image:url(${pg(3)});transform:rotate(-4deg)"></div>
   <div class=paper style="left:250px;top:330px;width:440px;height:622px;background-image:url(${B64('A-3.png')});transform:rotate(5deg)"></div>
   <div class=tag style="left:90px;top:110px;transform:rotate(-4deg)">US LETTER</div>
   <div class=tag style="left:520px;top:300px;transform:rotate(5deg)">A4</div>
   <h1>Print, cut, hide,<br><em>hunt tonight</em></h1>
   <ul><li><b>2 pdf files:</b> US Letter (8.5 × 11 in) and A4</li>
   <li><b>4 clue cards per page:</b> cut on the dashed lines</li>
   <li><b>White backgrounds</b> that are easy on your ink</li>
   <li><b>Big pictures</b> on every card for kids who can't read yet</li>
   <li>Print as many copies as you need for your own family or classroom</li>
   <li>Digital download: no physical item is shipped</li></ul>`,

  '4-all-clues': `<style>${base} body{background:#fbf6ea}
   h1{position:absolute;top:36px;left:50px;width:900px;margin:0;font-family:Fr;font-weight:900;font-size:56px;line-height:1.02;white-space:nowrap}
   h1 em{font-style:normal;color:${BERRY}}
   .g{position:absolute;left:44px;top:130px;width:900px;height:960px}
   .wood{position:absolute;left:980px;top:0;right:0;bottom:0}
   .steps{position:absolute;left:1015px;top:520px;width:460px;color:${CREAM};font-size:29px;line-height:1.35;font-weight:700}
   .steps>div{margin-bottom:22px;display:flex;gap:16px;align-items:flex-start}
   .steps b{flex:none;width:46px;height:46px;border-radius:50%;background:${GOLD};color:${PLUM};text-align:center;line-height:46px;font-family:Fr;font-weight:900}
   .steps h2{margin:0 0 22px;font-family:Fr;font-weight:900;font-size:46px;color:${GOLD}}</style>
   <h1>All 15 clues <em>+ treasure card</em></h1>
   <div class=g>${Array.from({ length: 16 }, (_, k) => card(k, 174, 0, (k % 4) * 214 + 30, Math.floor(k / 4) * 240)).join('')}</div>
   <div class=wood></div><div class=vig style="left:980px"></div>
   <div class=prop style="left:1110px;top:60px;width:270px;height:270px;transform:rotate(-6deg)">${I(0)}</div>
   <div class=prop style="left:1340px;top:300px;width:130px;height:130px;transform:rotate(10deg)">${I(21)}</div>
   <div class=steps><h2>How it works</h2>
    <div><b>1</b><span>Hide each clue where the one before it points</span></div>
    <div><b>2</b><span>Hand the kids clue No. 1</span></div>
    <div><b>3</b><span>They solve each rhyme and race to the treasure!</span></div></div>`,
};

(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  fs.mkdirSync('listing-images', { recursive: true });
  for (const [n, h] of Object.entries(pages)) {
    await p.setContent(`<!doctype html><meta charset=utf-8>${h}`, { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: `listing-images/${n}.png` });
  }
  await b.close(); fs.rmSync(tmp, { recursive: true });
})();
