// Listing images (3000x2250) + uses the real PDF pages, rasterised with pdftoppm.
// Run from this folder after build.js: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const os = require('os');
const { execFileSync } = require('child_process');
const { icons } = JSON.parse(fs.readFileSync('icons.json', 'utf8'));
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf';
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'bingo-'));
const PDF = 'bundle/woodland-christmas-bingo-US-Letter.pdf', PDFA4 = 'bundle/woodland-christmas-bingo-A4.pdf';
execFileSync('pdftoppm', ['-r', '200', '-png', PDF, path.join(tmp, 'L')]);
execFileSync('pdftoppm', ['-r', '120', '-png', '-f', '2', '-l', '2', PDFA4, path.join(tmp, 'A')]);
const B64 = f => `data:image/png;base64,${fs.readFileSync(path.join(tmp, f)).toString('base64')}`;
const pg = n => B64(`L-${String(n).padStart(2, '0')}.png`);
const font = f => `data:font/ttf;base64,${fs.readFileSync(path.join('fonts', f)).toString('base64')}`;
const I = id => `<svg viewBox="0 0 1000 1000" style="width:100%;height:100%;display:block">${icons[id].svg}</svg>`;
// Card crops (mm on US Letter at 200 dpi): card frame x 9..206.9, y 9..133.2 (top) / 146.2..270.4 (bottom)
const MM = 200 / 25.4;
const cardImg = (page, half) => `background-image:url(${pg(page)});background-size:${215.9 * MM}px ${279.4 * MM}px;background-position:-${9 * MM}px -${(half ? 146.2 : 9) * MM}px`;
const CW = 197.9 * MM, CH = 124.2 * MM; // card px at 200 dpi
// grid area inside a card crop, as fractions (from build.js CSS)
const GX0 = 42.1 / 197.9, GX1 = 194 / 197.9, GY0 = 3.9 / 124.2, GY1 = 120.3 / 124.2;
const card = (page, half, w, rot, x, y, marks = []) => {
  const s = w / CW, h = CH * s;
  const tokens = marks.map(([c, r]) => {
    const cx = (GX0 + (GX1 - GX0) * (c + 0.5) / 5) * w, cy = (GY0 + (GY1 - GY0) * (r + 0.5) / 5) * h, d = (GY1 - GY0) * h / 5 * 0.82;
    return `<div class=tok style="left:${cx - d / 2}px;top:${cy - d / 2}px;width:${d}px;height:${d}px"></div>`; }).join('');
  return `<div class=card style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;transform:rotate(${rot}deg)">
    <div style="width:${CW}px;height:${CH}px;transform:scale(${s});transform-origin:0 0;${cardImg(page, half)}"></div>${tokens}</div>`;
};
const base = `@font-face{font-family:Fr;font-weight:900;src:url(${font('Fraunces-900.ttf')})}
@font-face{font-family:Fr;font-weight:700;src:url(${font('Fraunces-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${font('Nunito-800.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${font('Nunito-700.ttf')})}
body{margin:0;width:1500px;height:1125px;overflow:hidden;position:relative;font-family:Nu;color:${PLUM}}
.card{position:absolute;background:#fff;border-radius:10px;box-shadow:0 18px 40px rgba(0,0,0,.45),0 3px 8px rgba(0,0,0,.3);transform-origin:50% 50%;overflow:hidden}
.tok{position:absolute;border-radius:50%;background:${GOLD};border:solid ${PLUM};border-width:max(2px,2.7%);box-shadow:inset 0 0 0 7.5px ${GOLD},inset 0 0 0 9px ${CREAM},0 3px 6px rgba(0,0,0,.35)}
.wood{background:
  repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 3px,transparent 3px 11px),
  repeating-linear-gradient(90deg,rgba(0,0,0,.10) 0 1px,transparent 1px 47px,rgba(0,0,0,.06) 47px 49px,transparent 49px 121px),
  linear-gradient(90deg,#3a2a24,#4a352b 30%,#3d2c25 55%,#4b372d 80%,#392922)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 55%,transparent 45%,rgba(20,10,20,.55));pointer-events:none}
.paper{position:absolute;background:#fff;box-shadow:0 14px 30px rgba(0,0,0,.4);background-size:cover}`;

const scatter = (list) => list.map(([x, y, d, rot]) => `<div class=tok style="left:${x}px;top:${y}px;width:${d}px;height:${d}px;transform:rotate(${rot}deg)"></div>`).join('');
const cc = (id, x, y, w, rot) => `<div class=paper style="left:${x}px;top:${y}px;width:${w}px;height:${w * 0.78}px;transform:rotate(${rot}deg);border-radius:6px;display:flex;flex-direction:column;align-items:center;justify-content:center">
  <div style="width:${w * 0.52}px;height:${w * 0.52}px">${I(id)}</div><b style="font-family:Fr;font-weight:700;font-size:${w * 0.1}px;margin-top:${w * 0.03}px">${icons[id].name.replace(/(^|\s)\S/g, m => m.toUpperCase())}</b></div>`;

const pages = {
  '1-thumbnail': `<style>${base}
   .title{position:absolute;left:0;right:0;top:0;height:250px;background:linear-gradient(${PLUM},#3a2447);display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 8px 24px rgba(0,0,0,.4);z-index:5}
   .title h1{margin:0;font-family:Fr;font-weight:900;font-size:132px;line-height:1;color:${CREAM};letter-spacing:1px}
   .title h1 em{font-style:normal;color:${GOLD}}
   .title p{margin:10px 0 0;font-size:34px;letter-spacing:5px;color:${GOLD};font-weight:800}
   .badge{position:absolute;z-index:6;right:44px;bottom:40px;width:250px;height:250px;border-radius:50%;background:${BERRY};color:${CREAM};display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 10px 26px rgba(0,0,0,.45);border:6px solid ${GOLD};transform:rotate(-8deg)}
   .badge b{font-family:Fr;font-weight:900;font-size:110px;line-height:.9}.badge span{font-size:28px;font-weight:800;letter-spacing:2px;text-align:center;line-height:1.1}</style>
   <div class=wood style="position:absolute;inset:0"></div><div class=vig></div>
   <div style="position:absolute;left:1150px;top:250px;width:150px;height:150px;transform:rotate(25deg);filter:drop-shadow(0 8px 10px rgba(0,0,0,.5))">${I(13)}</div>
   ${cc(24, 30, 760, 270, -14)}${cc(11, 0, 330, 215, 6)}
   ${card(3, 1, 840, 5, 600, 370)}
   ${card(2, 0, 900, -4, 230, 300, [[0, 2], [1, 2], [2, 2], [3, 2], [4, 2]])}
   ${scatter([[560, 1000, 64, 0], [640, 1040, 62, 0], [720, 995, 60, 0], [190, 1000, 60, 0], [270, 1040, 58, 0]])}
   <div class=title><h1>Christmas <em>Bingo</em></h1><p>WOODLAND PICTURE GAME · PRINTABLE</p></div>
   <div class=badge><b>30</b><span>UNIQUE<br>CARDS</span></div>`,

  '2-whats-included': `<style>${base} body{background:${CREAM}}
   h1{position:absolute;top:30px;width:100%;text-align:center;margin:0;font-family:Fr;font-weight:900;font-size:76px}
   h1 em{font-style:normal;color:${BERRY}}
   .sub{position:absolute;top:128px;width:100%;text-align:center;font-size:30px;color:${PINE};font-weight:800;letter-spacing:1px}
   .row{position:absolute;top:195px;left:40px;right:40px;display:flex;justify-content:space-between}
   .it{width:268px;text-align:center}.it .paper{position:relative;width:268px;height:347px;border-radius:4px}
   .it b{display:block;font-family:Fr;font-size:34px;margin-top:22px;line-height:1.1}.it span{display:block;font-size:24px;color:${PINE};margin-top:6px;font-weight:700}
   .feat{position:absolute;top:640px;left:40px;right:40px;display:grid;grid-template-columns:repeat(2,1fr);gap:26px}
   .feat>div{background:#fff;border:3px solid ${PLUM};border-radius:22px;display:flex;align-items:center;gap:26px;padding:20px 28px}
   .fi{width:110px;height:110px;flex:none}.feat b{display:block;font-family:Fr;font-weight:900;font-size:40px;color:${BERRY}}
   .feat span{font-size:26px;font-weight:700;color:${PINE}}</style>
   <h1>What's <em>included</em></h1><div class=sub>20 printable pages · US Letter + A4 pdf · instant download</div>
   <div class=row>
    ${[[1, 'How to play', 'rules + 5 ways to win'], [2, '30 bingo cards', 'all different, 2 per page'], [17, '30 calling cards', 'cut apart and draw'],
       [19, 'Caller checklist', 'tick as you call'], [20, '72 markers', 'for 3 at blackout']]
      .map(([n, t, s]) => `<div class=it><div class=paper style="background-image:url(${pg(n)})"></div><b>${t}</b><span>${s}</span></div>`).join('')}
   </div>
   <div class=feat>${[[16, '2 to 30 players', 'family night, parties, classrooms'], [25, 'Ages 3 and up', 'pictures, no reading needed'],
     [3, 'Fair every game', 'each picture is on 24 of 30 cards'], [17, 'Reusable', 'sheet protectors + dry-erase']]
     .map(([i, t, d]) => `<div><div class=fi>${I(i)}</div><div><b>${t}</b><span>${d}</span></div></div>`).join('')}</div>`,

  '3-formats': `<style>${base} body{background:${PLUM};color:${CREAM}}
   .wood{position:absolute;inset:0;opacity:0}
   h1{position:absolute;left:740px;top:150px;margin:0;font-family:Fr;font-weight:900;font-size:70px;line-height:1.05;color:${CREAM}}
   h1 em{font-style:normal;color:${GOLD}}
   ul{position:absolute;left:740px;top:340px;margin:0;padding:0;list-style:none;width:700px}
   li{font-size:33px;margin:0 0 24px;line-height:1.25;padding-left:46px;position:relative}
   li::before{content:'';position:absolute;left:0;top:10px;width:22px;height:22px;border-radius:50%;background:${GOLD}}
   li b{color:${GOLD}}
   .tag{position:absolute;font-family:Fr;font-weight:900;font-size:30px;color:${PLUM};background:${GOLD};padding:6px 18px;border-radius:30px;z-index:3}</style>
   <div class=paper style="left:70px;top:150px;width:470px;height:608px;background-image:url(${pg(2)});transform:rotate(-4deg)"></div>
   <div class=paper style="left:250px;top:330px;width:440px;height:622px;background-image:url(${B64('A-02.png')});transform:rotate(5deg)"></div>
   <div class=tag style="left:90px;top:110px;transform:rotate(-4deg)">US LETTER</div>
   <div class=tag style="left:520px;top:300px;transform:rotate(5deg)">A4</div>
   <h1>Print at home,<br><em>play tonight</em></h1>
   <ul><li><b>2 pdf files:</b> US Letter (8.5 × 11 in) and A4</li>
   <li><b>2 cards per page:</b> print, cut in half, play</li>
   <li><b>Light backgrounds</b> that are easy on your ink</li>
   <li><b>Big, clear pictures</b> for kids who can't read yet</li>
   <li>Print as many copies as you need for your own party or classroom</li>
   <li>Digital download: no physical item is shipped</li></ul>`,

  '4-color-ideas': `<style>${base} body{background:#fbf6ea}
   h1{position:absolute;top:40px;left:60px;width:640px;margin:0;font-family:Fr;font-weight:900;font-size:66px;line-height:1.02}
   h1 em{font-style:normal;color:${BERRY}}
   .g{position:absolute;left:50px;top:250px;width:670px;display:grid;grid-template-columns:repeat(6,1fr);gap:22px 6px}
   .g div{text-align:center;font-size:17px;font-weight:800;color:${PINE}}.g div div{width:96px;height:96px;margin:0 auto 3px}
   .wood{position:absolute;left:760px;top:0;right:0;bottom:0}
   .steps{position:absolute;left:800px;top:820px;width:660px;color:${CREAM};font-size:30px;line-height:1.5;font-weight:700}
   .steps b{display:inline-block;width:46px;height:46px;border-radius:50%;background:${GOLD};color:${PLUM};text-align:center;line-height:46px;font-family:Fr;font-weight:900;margin-right:14px}
   .steps h2{margin:0 0 8px;font-family:Fr;font-weight:900;font-size:44px;color:${GOLD}}</style>
   <h1>30 woodland<br><em>pictures</em></h1>
   <div class=g>${icons.map(i => `<div><div>${I(i.id)}</div>${i.name}</div>`).join('')}</div>
   <div class=wood></div><div class=vig style="left:760px"></div>
   ${cc(4, 1220, 50, 230, 7)}
   ${card(5, 0, 650, -3, 800, 310, [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]])}
   <div class=steps><h2>How to play</h2><div><b>1</b>Draw a calling card</div><div><b>2</b>Cover the picture</div><div><b>3</b>Fill a line, shout BINGO!</div></div>`,
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
