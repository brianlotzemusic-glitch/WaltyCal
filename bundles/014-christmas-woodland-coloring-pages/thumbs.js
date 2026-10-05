// Listing images (3000x2250) from the real pages: the PDF pages (pdftoppm) and art/colored
// (the real pages' own regions filled by colorize.py). Props (wood, pencils, mug) are drawn in code.
// Run from this folder after build.js: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const os = require('os');
const { execFileSync } = require('child_process');
const S = JSON.parse(fs.readFileSync('subjects.json', 'utf8')).pages;
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf';
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'cwc-'));
const PL = 'bundle/christmas-woodland-coloring-pages-US-Letter.pdf', PA = 'bundle/christmas-woodland-coloring-pages-A4.pdf';
execFileSync('pdftoppm', ['-r', '110', '-png', PL, path.join(tmp, 'L')]);
execFileSync('pdftoppm', ['-r', '90', '-png', '-f', '6', '-l', '6', PA, path.join(tmp, 'A')]);
const B64 = (f, t = 'png') => `data:image/${t};base64,${fs.readFileSync(f).toString('base64')}`;
const pg = n => B64(path.join(tmp, `L-${String(n).padStart(2, '0')}.png`));
const col = f => B64(path.join('art', 'colored', f + '.jpg'), 'jpeg');
const font = f => `data:font/ttf;base64,${fs.readFileSync(path.join('fonts', f)).toString('base64')}`;
// a printed US Letter page holding a coloured-in version of the art (art box 182 x 234 mm, centred)
const LW = 215.9, LH = 279.4, AW = 182, AH = 182 * 1152 / 896;
const colPage = (img, x, y, w, rot, z = 1) => {
  const k = w / LW;
  return `<div class=paper style="left:${x}px;top:${y}px;width:${w}px;height:${LH * k}px;transform:rotate(${rot}deg);z-index:${z}">
    <img src="${img}" style="position:absolute;left:${(LW - AW) / 2 * k}px;top:${(LH - AH) / 2 * k}px;width:${AW * k}px;height:${AH * k}px"></div>`;
};
const pdfPage = (n, x, y, w, rot, z = 1) =>
  `<div class=paper style="left:${x}px;top:${y}px;width:${w}px;height:${w * LH / LW}px;background-image:url(${pg(n)});transform:rotate(${rot}deg);z-index:${z}"></div>`;
const pencil = (x, y, len, rot, c, z = 4) => `<div class=prop style="left:${x}px;top:${y}px;width:${len}px;height:${len * 0.075}px;transform:rotate(${rot}deg);z-index:${z}">
  <svg viewBox="0 0 200 15" style="width:100%;height:100%;display:block"><polygon points="0,7.5 26,0 26,15" fill="#ecd3a8"/><polygon points="0,7.5 10,4.6 10,10.4" fill="${c}"/>
  <rect x="26" y="0" width="174" height="15" fill="${c}"/><rect x="26" y="5" width="174" height="2.5" fill="rgba(255,255,255,.22)"/><rect x="26" y="11" width="174" height="2" fill="rgba(0,0,0,.15)"/>
  <rect x="190" y="0" width="10" height="15" fill="rgba(0,0,0,.25)"/></svg></div>`;
const mugTop = (x, y, d) => `<div class=prop style="left:${x}px;top:${y}px;width:${d * 1.35}px;height:${d}px;z-index:3">
  <svg viewBox="0 0 135 100" style="width:100%;height:100%"><rect x="88" y="40" width="44" height="20" rx="10" fill="${CREAM}" stroke="${PLUM}" stroke-width="3"/>
  <circle cx="50" cy="50" r="47" fill="${CREAM}" stroke="${PLUM}" stroke-width="3"/><circle cx="50" cy="50" r="38" fill="#5a3a2a"/>
  <circle cx="40" cy="44" r="7" fill="#fbf4ea"/><circle cx="58" cy="52" r="6" fill="#fbf4ea"/><circle cx="48" cy="61" r="5.5" fill="#fbf4ea"/>
  <circle cx="50" cy="50" r="38" fill="none" stroke="${BERRY}" stroke-width="4"/></svg></div>`;
const sprig = (x, y, s, rot) => `<div class=prop style="left:${x}px;top:${y}px;width:${s}px;height:${s}px;transform:rotate(${rot}deg);z-index:2">
  <svg viewBox="0 0 100 100" style="width:100%;height:100%">${[0, 1, 2, 3, 4, 5, 6].map(i => `<path d="M50 ${92 - i * 12} l-${26 - i * 2} -10 M50 ${92 - i * 12} l${26 - i * 2} -10" stroke="#3f6a4e" stroke-width="4" stroke-linecap="round"/>`).join('')}
  <path d="M50 96 L50 10" stroke="#5a4030" stroke-width="4"/><circle cx="34" cy="20" r="6" fill="${BERRY}"/><circle cx="44" cy="14" r="6" fill="${BERRY}"/></svg></div>`;
const PEN = ['#d9773a', '#4f7a5c', '#a8384a', '#e8c97a', '#5b4470', '#8a5a3c', '#7fa3c4'];
const base = `@font-face{font-family:Fr;font-weight:900;src:url(${font('Fraunces-900.ttf')})}
@font-face{font-family:Fr;font-weight:700;src:url(${font('Fraunces-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${font('Nunito-800.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${font('Nunito-700.ttf')})}
body{margin:0;width:1500px;height:1125px;overflow:hidden;position:relative;font-family:Nu;color:${PLUM}}
.paper{position:absolute;background:#fff;box-shadow:0 16px 36px rgba(0,0,0,.45),0 3px 8px rgba(0,0,0,.3);background-size:cover;transform-origin:50% 50%}
.prop{position:absolute;filter:drop-shadow(0 8px 10px rgba(0,0,0,.5));transform-origin:50% 50%}
.wood{position:absolute;inset:0;background:
  repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 3px,transparent 3px 11px),
  repeating-linear-gradient(90deg,rgba(0,0,0,.10) 0 1px,transparent 1px 47px,rgba(0,0,0,.06) 47px 49px,transparent 49px 121px),
  linear-gradient(90deg,#3a2a24,#4a352b 30%,#3d2c25 55%,#4b372d 80%,#392922)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 55%,transparent 40%,rgba(28,12,32,.6));pointer-events:none}
.tagp{position:absolute;font-family:Fr;font-weight:900;font-size:30px;color:${PLUM};background:${GOLD};padding:6px 20px;border-radius:30px;z-index:9;white-space:nowrap}`;

const pages = {
  '1-thumbnail': `<style>${base}
   .band{position:absolute;left:0;right:0;top:0;height:250px;background:linear-gradient(${PLUM},#3a2447);display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 8px 24px rgba(0,0,0,.45);z-index:8}
   .band h1{margin:0;font-family:Fr;font-weight:900;font-size:112px;line-height:1;color:${CREAM};white-space:nowrap}.band h1 em{font-style:normal;color:${GOLD}}
   .band p{margin:14px 0 0;font-size:33px;letter-spacing:5px;color:${GOLD};font-weight:800}
   .badge{position:absolute;z-index:9;right:44px;bottom:40px;width:250px;height:250px;border-radius:50%;background:${BERRY};color:${CREAM};display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 10px 26px rgba(0,0,0,.45);border:7px solid ${GOLD};transform:rotate(-8deg)}
   .badge b{font-family:Fr;font-weight:900;font-size:120px;line-height:.85}.badge span{font-size:31px;font-weight:800;letter-spacing:3px}</style>
   <div class=wood></div><div class=vig></div>
   ${pdfPage(6, 1010, 300, 450, 7, 1)}${pdfPage(18, 70, 330, 430, -8, 1)}
   ${colPage(col('02-owl-on-snowy-pine'), 840, 270, 520, 3, 2)}
   ${colPage(col('01-fox-in-scarf-partial'), 330, 262, 620, -2.5, 3)}
   ${pencil(560, 1030, 380, -12, PEN[0], 5)}${pencil(250, 1075, 360, 6, PEN[1], 5)}${pencil(-40, 760, 340, 64, PEN[2], 5)}
   ${mugTop(-40, 290, 170)}${sprig(1300, 740, 210, 30)}
   <div class=band><h1>Christmas <em>Coloring Pages</em></h1><p>20 BOLD &amp; EASY COZY WOODLAND PAGES</p></div>
   <div class=badge><b>20</b><span>PAGES</span></div>`,

  '2-page-grid': `<style>${base} body{background:${CREAM}}
   h1{position:absolute;top:22px;width:100%;text-align:center;margin:0;font-family:Fr;font-weight:900;font-size:66px}
   h1 em{font-style:normal;color:${BERRY}}
   .sub{position:absolute;top:106px;width:100%;text-align:center;font-size:26px;color:${PINE};font-weight:800;letter-spacing:1px}
   .g{position:absolute;top:172px;left:60px;display:grid;grid-template-columns:repeat(5,160px);gap:20px 18px}
   .g div{width:160px;height:207px;background-size:cover;box-shadow:0 5px 12px rgba(44,27,54,.25);border-radius:2px;position:relative}
   .g span{position:absolute;left:-4px;top:-8px;background:${PLUM};color:${CREAM};font-size:16px;font-weight:800;border-radius:12px;padding:1px 8px}
   .names{position:absolute;top:190px;left:980px;right:40px;columns:1;font-size:25px;line-height:1.6;font-weight:700;color:${PLUM}}
   .names b{color:${BERRY};font-weight:800;display:inline-block;width:44px}
   .tail{position:absolute;bottom:22px;width:100%;text-align:center;font-size:22px;color:${PINE};font-weight:800}</style>
   <h1>All <em>20 pages</em></h1><div class=sub>one design per page · no text on the pages · US Letter and A4</div>
   <div class=g>${S.map((s, i) => `<div style="background-image:url(${pg(i + 1)})"><span>${i + 1}</span></div>`).join('')}</div>
   <div class=names>${S.map((s, i) => `<div><b>${i + 1}</b>${s[1]}</div>`).join('')}</div>
   <div class=tail>Original designs by Duskwood Designs Co · print as many as you like at home</div>`,

  '3-colored-mockup': `<style>${base}
   .card{position:absolute;right:46px;top:60px;width:470px;background:rgba(44,27,54,.92);color:${CREAM};border-radius:26px;padding:40px 40px 34px;z-index:9;box-shadow:0 14px 30px rgba(0,0,0,.45)}
   .card h2{margin:0 0 18px;font-family:Fr;font-weight:900;font-size:58px;line-height:1.02}.card h2 em{font-style:normal;color:${GOLD}}
   .card li{font-size:27px;line-height:1.3;margin:0 0 14px;font-weight:700}.card ul{margin:0;padding-left:28px}
   .zoom{position:absolute;right:120px;bottom:60px;width:330px;height:330px;border-radius:50%;border:8px solid ${GOLD};overflow:hidden;z-index:9;box-shadow:0 12px 28px rgba(0,0,0,.5);background:#fff}
   .zoom img{position:absolute;width:1300px;left:-430px;top:-560px}
   .zl{position:absolute;right:140px;bottom:20px;z-index:9;font-size:22px;font-weight:800;color:${GOLD};width:290px;text-align:center}</style>
   <div class=wood></div><div class=vig></div>
   ${colPage(col('02-owl-on-snowy-pine'), 60, 60, 560, -4, 2)}
   ${colPage(col('01-fox-in-scarf'), 450, 390, 440, 5, 3)}
   ${pencil(200, 1010, 400, -8, PEN[4])}${pencil(640, 1050, 360, 4, PEN[3])}${pencil(-60, 640, 330, 70, PEN[1])}${pencil(700, 140, 300, 20, PEN[0])}
   <div class=card><h2>Bold lines,<br><em>big spaces</em></h2><ul>
   <li>Thick outlines, about 2 mm</li><li>Every space closed and big enough for crayons, pencils and markers</li><li>Easy for kids, relaxing for adults</li></ul></div>
   <div class=zoom><img src="${pg(6)}"></div><div class=zl>close-up of page 6</div>`,

  '4-formats': `<style>${base} body{background:${PLUM};color:${CREAM}}
   h1{position:absolute;left:800px;top:110px;margin:0;font-family:Fr;font-weight:900;font-size:66px;line-height:1.05;color:${CREAM}}
   h1 em{font-style:normal;color:${GOLD}}
   ul{position:absolute;left:800px;top:290px;margin:0;padding:0;list-style:none;width:650px}
   li{font-size:30px;margin:0 0 22px;line-height:1.25;padding-left:44px;position:relative}
   li::before{content:'';position:absolute;left:0;top:9px;width:22px;height:22px;border-radius:50%;background:${GOLD}}
   li b{color:${GOLD}}</style>
   <div style="position:absolute;left:60px;top:150px;width:330px;height:427px">${pdfPage(13, 0, 0, 330, -4)}</div>
   <div class=paper style="left:340px;top:200px;width:330px;height:466.7px;background-image:url(${B64(path.join(tmp, 'A-06.png'))});transform:rotate(4deg)"></div>
   <div class=tagp style="left:60px;top:110px;transform:rotate(-4deg)">US LETTER</div>
   <div class=tagp style="left:590px;top:170px;transform:rotate(4deg)">A4</div>
   ${pencil(120, 820, 420, -6, PEN[2])}${pencil(260, 900, 380, 3, PEN[3])}${pencil(80, 980, 400, -2, PEN[1])}
   <h1>Print at home,<br><em>color tonight</em></h1>
   <ul><li><b>20 coloring pages,</b> one design per page, no text</li>
   <li><b>2 pdf files:</b> US Letter (8.5 × 11 in) and A4, 20 pages each</li>
   <li>Same art size on both papers, with a safe white margin</li>
   <li>Print one page or all 20, as often as you like</li>
   <li>Crayons, colored pencils, markers or paint</li>
   <li>Digital download: no physical item is shipped</li></ul>`,
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
