// Listing images (3000x2250) built from the real PDF pages (pdftoppm) and the real sticker SVGs.
// Run from this folder after build.js: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const os = require('os');
const { execFileSync } = require('child_process');
const { icons } = JSON.parse(fs.readFileSync('icons.json', 'utf8'));
const ST = JSON.parse(fs.readFileSync('stickers.json', 'utf8'));
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf';
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'sam-'));
const CL = 'bundle/small-autumn-moments-checklist-US-Letter.pdf', CA = 'bundle/small-autumn-moments-checklist-A4.pdf';
const SL = 'bundle/small-autumn-moments-stickers-US-Letter.pdf';
execFileSync('pdftoppm', ['-r', '200', '-png', CL, path.join(tmp, 'L')]);
execFileSync('pdftoppm', ['-r', '130', '-png', '-f', '1', '-l', '1', CA, path.join(tmp, 'A')]);
execFileSync('pdftoppm', ['-r', '130', '-png', SL, path.join(tmp, 'S')]);
const B64 = f => `data:image/png;base64,${fs.readFileSync(path.join(tmp, f)).toString('base64')}`;
const pg = n => B64(`L-${n}.png`);
const PNGSHEET = `data:image/png;base64,${fs.readFileSync('bundle/small-autumn-moments-stickers-print-then-cut.png').toString('base64')}`;
const font = f => `data:font/ttf;base64,${fs.readFileSync(path.join('fonts', f)).toString('base64')}`;
const byName = Object.fromEntries(icons.map(i => [i.name, i]));
const I = name => `<svg viewBox="0 0 1000 1000" style="width:100%;height:100%;display:block">${byName[name].svg}</svg>`;
const sByPhrase = Object.fromEntries(ST.stickers.map(s => [s.phrase, s]));
// one sticker as an absolutely placed element; scale = px per sheet px (300 dpi)
const vb = s => s.svg.match(/viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"/).slice(1).map(Number);
const loose = (phrase, x, y, w, rot) => `<div class=stk style="left:${x}px;top:${y}px;width:${w}px;transform:rotate(${rot}deg)">${sByPhrase[phrase].svg}</div>`;
// sticker sheet on white paper, minus the peeled ones (they lie on the table)
const sheet = (x, y, w, rot, peeled = []) => {
  const k = w / ST.sheet_px[0], h = ST.sheet_px[1] * k;
  const pad = 0.05 * w;
  const items = ST.stickers.filter(s => !peeled.includes(s.phrase)).map(s => {
    const [x0, y0, vw, vh] = vb(s);
    return `<div style="position:absolute;left:${(s.x + x0) * k + pad}px;top:${(s.y + y0) * k + pad}px;width:${vw * k}px;height:${vh * k}px">${s.svg.replace('<svg ', '<svg style="width:100%;height:100%;display:block" ')}</div>`;
  }).join('');
  return `<div class=paper style="left:${x}px;top:${y}px;width:${w + 2 * pad}px;height:${h + 2 * pad}px;transform:rotate(${rot}deg)">${items}</div>`;
};
const base = `@font-face{font-family:Fr;font-weight:900;src:url(${font('Fraunces-900.ttf')})}
@font-face{font-family:Fr;font-weight:700;src:url(${font('Fraunces-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${font('Nunito-800.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${font('Nunito-700.ttf')})}
body{margin:0;width:1500px;height:1125px;overflow:hidden;position:relative;font-family:Nu;color:${PLUM}}
.paper{position:absolute;background:#fff;box-shadow:0 16px 36px rgba(0,0,0,.45),0 3px 8px rgba(0,0,0,.3);background-size:cover;transform-origin:50% 50%}
.stk{position:absolute;filter:drop-shadow(0 6px 8px rgba(0,0,0,.45));transform-origin:50% 50%}.stk svg{display:block;width:100%}
.prop{position:absolute;filter:drop-shadow(0 8px 10px rgba(0,0,0,.5));transform-origin:50% 50%}
.wood{position:absolute;inset:0;background:
  repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 3px,transparent 3px 11px),
  repeating-linear-gradient(90deg,rgba(0,0,0,.10) 0 1px,transparent 1px 47px,rgba(0,0,0,.06) 47px 49px,transparent 49px 121px),
  linear-gradient(90deg,#3a2a24,#4a352b 30%,#3d2c25 55%,#4b372d 80%,#392922)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 55%,transparent 40%,rgba(28,12,32,.6));pointer-events:none}
.tagp{position:absolute;font-family:Fr;font-weight:900;font-size:30px;color:${PLUM};background:${GOLD};padding:6px 20px;border-radius:30px;z-index:3;white-space:nowrap}`;

// top-view mug of tea, drawn in code
const mugTop = (x, y, d) => `<div class=prop style="left:${x}px;top:${y}px;width:${d * 1.35}px;height:${d}px">
  <svg viewBox="0 0 135 100" style="width:100%;height:100%"><rect x="88" y="40" width="44" height="20" rx="10" fill="${CREAM}" stroke="${PLUM}" stroke-width="3"/>
  <circle cx="50" cy="50" r="47" fill="${CREAM}" stroke="${PLUM}" stroke-width="3"/><circle cx="50" cy="50" r="38" fill="#5a3a2a"/>
  <circle cx="50" cy="50" r="38" fill="none" stroke="${BERRY}" stroke-width="4"/><ellipse cx="38" cy="40" rx="12" ry="6" fill="rgba(255,255,255,.18)"/></svg></div>`;
const pencil = (x, y, len, rot) => `<div class=prop style="left:${x}px;top:${y}px;width:${len}px;height:${len * 0.06}px;transform:rotate(${rot}deg)">
  <svg viewBox="0 0 200 12" style="width:100%;height:100%"><polygon points="0,6 22,0 22,12" fill="#e9d2a8"/><polygon points="0,6 8,4 8,8" fill="${PLUM}"/>
  <rect x="22" y="0" width="150" height="12" fill="${PINE}"/><rect x="22" y="4" width="150" height="2" fill="rgba(255,255,255,.18)"/><rect x="172" y="0" width="12" height="12" fill="${GOLD}"/><rect x="184" y="0" width="16" height="12" rx="3" fill="${BERRY}"/></svg></div>`;
const prop = (name, x, y, w, rot) => `<div class=prop style="left:${x}px;top:${y}px;width:${w}px;height:${w}px;transform:rotate(${rot}deg)">${I(name)}</div>`;

const pages = {
  '1-thumbnail': `<style>${base}
   .band{position:absolute;left:0;right:0;top:0;height:228px;background:linear-gradient(${PLUM},#3a2447);display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 8px 24px rgba(0,0,0,.45);z-index:5}
   .band h1{margin:0;font-family:Fr;font-weight:900;font-size:124px;line-height:1;color:${CREAM}}.band h1 em{font-style:normal;color:${GOLD}}
   .band p{margin:12px 0 0;font-size:31px;letter-spacing:5px;color:${GOLD};font-weight:800}
   .badge{position:absolute;z-index:6;right:40px;bottom:36px;width:236px;height:236px;border-radius:50%;background:${BERRY};color:${CREAM};display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 10px 26px rgba(0,0,0,.45);border:6px solid ${GOLD};transform:rotate(-8deg)}
   .badge b{font-family:Fr;font-weight:900;font-size:92px;line-height:.9}.badge span{font-size:27px;font-weight:800;letter-spacing:2px;text-align:center;line-height:1.1}</style>
   <div class=wood></div><div class=vig></div>
   ${prop('oak leaf', 30, 900, 170, -30)}${prop('acorns', 1310, 250, 150, 15)}
   <div class=paper style="left:95px;top:262px;width:648px;height:838px;background-image:url(${pg(1)});transform:rotate(-3.5deg)"></div>
   ${sheet(800, 300, 470, 4, ['first soup', 'candle season', 'first frost'])}
   ${loose('first soup', 640, 900, 205, -12)}${loose('candle season', 905, 865, 185, 9)}${loose('first frost', 1290, 560, 175, -6)}
   ${mugTop(-40, 330, 160)}${pencil(560, 1060, 300, -8)}
   <div class=band><h1>Fall <em>Bucket List</em></h1><p>SMALL AUTUMN MOMENTS · PRINTABLE CHECKLIST</p></div>
   <div class=badge><b>+20</b><span>STICKERS</span></div>`,

  '2-whats-included': `<style>${base} body{background:${CREAM}}
   h1{position:absolute;top:28px;width:100%;text-align:center;margin:0;font-family:Fr;font-weight:900;font-size:74px}
   h1 em{font-style:normal;color:${BERRY}}
   .sub{position:absolute;top:122px;width:100%;text-align:center;font-size:29px;color:${PINE};font-weight:800;letter-spacing:1px}
   .row{position:absolute;top:200px;left:36px;right:36px;display:flex;justify-content:space-between;align-items:flex-start}
   .it{width:270px;text-align:center}.it .paper{position:relative;width:270px;height:349px;border-radius:3px;box-shadow:0 10px 24px rgba(44,27,54,.28)}
   .it b{display:block;font-family:Fr;font-size:32px;margin-top:22px;line-height:1.1}.it span{display:block;font-size:23px;color:${PINE};margin-top:6px;font-weight:700;line-height:1.25}
   .chk{background-color:#fff;background-image:linear-gradient(45deg,#e4dde8 25%,transparent 25%,transparent 75%,#e4dde8 75%),linear-gradient(45deg,#e4dde8 25%,transparent 25%,transparent 75%,#e4dde8 75%);background-size:22px 22px;background-position:0 0,11px 11px}
   .feat{position:absolute;top:760px;left:36px;right:36px;display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
   .feat>div{background:#fff;border:3px solid ${PLUM};border-radius:22px;display:flex;align-items:center;gap:22px;padding:34px 24px}
   .tail{position:absolute;top:1040px;width:100%;text-align:center;font-size:26px;color:${PINE};font-weight:700}
   .fi{width:110px;height:110px;flex:none}.feat b{display:block;font-family:Fr;font-weight:900;font-size:36px;color:${BERRY};line-height:1.05}
   .feat span{font-size:24px;font-weight:700;color:${PINE}}</style>
   <h1>What's <em>included</em></h1><div class=sub>4 pdf files + 1 PNG · US Letter and A4 · instant download</div>
   <div class=row>
    ${[[pg(1), '30 small moments', 'the checklist, cream page'], [pg(2), 'Write your own', '15 blank lines + "when"'],
       [pg(3), 'Ink saver', 'both pages on white'], [B64('S-1.png'), 'Sticker sheet', '20 stickers, pdf with cut guides']]
      .map(([u, t, s]) => `<div class=it><div class=paper style="background-image:url(${u})"></div><b>${t}</b><span>${s}</span></div>`).join('')}
    <div class=it><div class="paper chk" style="display:flex;align-items:center;justify-content:center"><img src="${PNGSHEET}" style="width:238px"></div><b>Print Then Cut</b><span>transparent PNG, 300 DPI</span></div>
   </div>
   <div class=feat>${[['sleeping fox', 'Real, small moments', 'not another list of big plans'], ['oak sprig', 'Moody woodland art', 'fox, mushrooms, lantern, oak'], ['candle', 'Print at home', 'tonight, as many as you need']]
     .map(([i, t, d]) => `<div><div class=fi>${I(i)}</div><div><b>${t}</b><span>${d}</span></div></div>`).join('')}</div>
   <div class=tail>Personal use: print as many copies as you like for your own home · Duskwood Designs Co</div>`,

  '3-formats': `<style>${base} body{background:${PLUM};color:${CREAM}}
   h1{position:absolute;left:800px;top:120px;margin:0;font-family:Fr;font-weight:900;font-size:66px;line-height:1.05;color:${CREAM}}
   h1 em{font-style:normal;color:${GOLD}}
   ul{position:absolute;left:800px;top:300px;margin:0;padding:0;list-style:none;width:660px}
   li{font-size:30px;margin:0 0 22px;line-height:1.25;padding-left:44px;position:relative}
   li::before{content:'';position:absolute;left:0;top:9px;width:22px;height:22px;border-radius:50%;background:${GOLD}}
   li b{color:${GOLD}}
   .dim{position:absolute;font-size:24px;font-weight:800;color:${GOLD};letter-spacing:1px}</style>
   <div class=paper style="left:50px;top:110px;width:330px;height:427px;background-image:url(${pg(1)});transform:rotate(-4deg)"></div>
   <div class=paper style="left:330px;top:150px;width:330px;height:467px;background-image:url(${B64('A-1.png')});transform:rotate(4deg)"></div>
   <div class=tagp style="left:56px;top:76px;transform:rotate(-4deg)">US LETTER</div>
   <div class=tagp style="left:570px;top:122px;transform:rotate(4deg)">A4</div>
   <div class=paper style="left:80px;top:665px;width:285px;height:368px;background:none;box-shadow:none;border:3px dashed ${GOLD};border-radius:6px"><img src="${PNGSHEET}" style="width:100%;display:block"></div>
   <div class=dim style="left:132px;top:1045px">6.75 × 9.25 in</div>
   <div class=dim style="left:395px;top:800px;width:340px;line-height:1.3;color:${CREAM};font-weight:700">← Cricut Print Then Cut sheet, transparent PNG at 300 DPI</div>
   <h1>Print at home,<br><em>tick as you go</em></h1>
   <ul><li><b>Checklist pdf</b> in US Letter (8.5 × 11 in) and A4: 4 pages each</li>
   <li><b>Cream or ink saver:</b> every page also comes on plain white</li>
   <li><b>Sticker sheet pdf</b> (Letter and A4) for sticker paper and scissors</li>
   <li><b>Print Then Cut PNG:</b> 2025 × 2775 px, 300 DPI, fits Cricut's 6.75 × 9.25 in area</li>
   <li>Fonts embedded; print at 100% (actual size)</li>
   <li>Digital download: no physical item is shipped</li></ul>`,

  '4-sticker-closeup': `<style>${base} body{background:#fbf6ea}
   h1{position:absolute;top:40px;left:60px;margin:0;font-family:Fr;font-weight:900;font-size:58px;line-height:1.05}
   h1 em{font-style:normal;color:${BERRY}}
   .note{position:absolute;left:60px;top:200px;width:520px;font-size:28px;line-height:1.4;color:${PINE};font-weight:700}
   .call{position:absolute;font-size:24px;font-weight:800;color:${BERRY};width:330px;line-height:1.3}
   .wood{left:640px}.vig{left:640px}
   .mini{position:absolute;left:60px;top:400px;width:520px;display:grid;grid-template-columns:repeat(5,1fr);gap:10px 8px}
   .mini svg{width:100%;display:block}</style>
   <div class=wood></div><div class=vig></div>
   <h1>Little stickers<br><em>for little moments</em></h1>
   <div class=note>20 stickers, each about 1.4 to 1.5 in, with a clean white offset border: the outer edge is the cut line.</div>
   <div class=mini>${ST.stickers.map(s => s.svg).join('')}</div>
   ${loose('candle season', 700, 80, 380, -6)}${loose('first soup', 1080, 120, 360, 7)}
   ${loose('do nothing day', 690, 560, 400, 5)}${loose('mushroom hunt', 1080, 590, 380, -5)}`,
};

(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  fs.mkdirSync('listing-images', { recursive: true });
  for (const [n, h] of Object.entries(pages)) {
    await p.setContent(`<!doctype html><meta charset=utf-8><style>@font-face{font-family:Fr;font-weight:700;src:url(${font('Fraunces-700.ttf')})}</style>${h}`, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: `listing-images/${n}.png` });
  }
  await b.close(); fs.rmSync(tmp, { recursive: true });
})();
