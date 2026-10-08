// Listing images (3000x2250) from the real files: art/png (the buyer's PNGs), art/svg (the buyer's SVGs)
// and mockup/flatlay.jpg (mockup.py: the real PNGs printed onto a blank AI flat-lay photo).
// Run from this folder after process.py and mockup.py: NODE_PATH=$(npm root -g) node thumbs.js
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const S = JSON.parse(fs.readFileSync('subjects.json', 'utf8')).designs;
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf';
const B64 = (f, t) => `data:${t};base64,${fs.readFileSync(f).toString('base64')}`;
const png = slug => B64(path.join('art', 'png', slug + '.png'), 'image/png');
const svg = slug => B64(path.join('art', 'svg', slug + '.svg'), 'image/svg+xml');
const font = f => `data:font/ttf;base64,${fs.readFileSync(path.join('fonts', f)).toString('base64')}`;
const slug = n => S[n - 1][0];
const img = (src, x, y, h, rot = 0, z = 2, extra = '') =>
  `<img src="${src}" style="position:absolute;left:${x}px;top:${y}px;height:${h}px;transform:rotate(${rot}deg);z-index:${z};${extra}">`;
const flakes = (n, seed) => { let s = seed, out = ''; const r = () => (s = (s * 9301 + 49297) % 233280) / 233280;
  for (let i = 0; i < n; i++) out += `<div style="position:absolute;left:${r() * 1500}px;top:${r() * 1125}px;width:${4 + r() * 8}px;height:${4 + r() * 8}px;border-radius:50%;background:rgba(241,230,207,${0.10 + r() * 0.18})"></div>`;
  return out; };
const checker = `background-color:#fff;background-image:linear-gradient(45deg,#e4e0e8 25%,transparent 25%),linear-gradient(-45deg,#e4e0e8 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#e4e0e8 75%),linear-gradient(-45deg,transparent 75%,#e4e0e8 75%);background-size:36px 36px;background-position:0 0,0 18px,18px -18px,-18px 0`;
const base = `@font-face{font-family:Fr;font-weight:900;src:url(${font('Fraunces-900.ttf')})}
@font-face{font-family:Fr;font-weight:700;src:url(${font('Fraunces-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${font('Nunito-800.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${font('Nunito-700.ttf')})}
body{margin:0;width:1500px;height:1125px;overflow:hidden;position:relative;font-family:Nu;color:${PLUM}}
.drop{filter:drop-shadow(0 10px 14px rgba(0,0,0,.45))}`;

const pages = {
  '1-thumbnail': `<style>${base} body{background:radial-gradient(ellipse at 50% 62%,#3d5e4b,${PINE} 55%,#1f3328)}
   .band{position:absolute;left:0;right:0;top:0;height:205px;background:${CREAM};display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 8px 24px rgba(0,0,0,.4);z-index:8}
   .band h1{margin:0;font-family:Fr;font-weight:900;font-size:84px;line-height:1;color:${PLUM};white-space:nowrap}.band h1 em{font-style:normal;color:${BERRY}}
   .band p{margin:12px 0 0;font-size:31px;letter-spacing:5px;color:${PINE};font-weight:800}
   .badge{position:absolute;z-index:9;right:40px;bottom:36px;width:230px;height:230px;border-radius:50%;background:${BERRY};color:${CREAM};display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 10px 26px rgba(0,0,0,.45);border:7px solid ${GOLD};transform:rotate(-8deg)}
   .badge b{font-family:Fr;font-weight:900;font-size:112px;line-height:.85}.badge span{font-size:28px;font-weight:800;letter-spacing:3px}</style>
   ${flakes(70, 7)}
   ${img(png(slug(3)), 417, 225, 700, 0, 2, 'filter:drop-shadow(0 14px 20px rgba(0,0,0,.5))')}
   ${img(png(slug(4)), 34, 340, 465, -5, 3, 'filter:drop-shadow(0 12px 16px rgba(0,0,0,.45))')}
   ${img(png(slug(1)), 1030, 340, 465, 5, 3, 'filter:drop-shadow(0 12px 16px rgba(0,0,0,.45))')}
   ${img(png(slug(12)), 70, 805, 300, -4, 4, 'filter:drop-shadow(0 10px 14px rgba(0,0,0,.45))')}
   ${img(png(slug(6)), 560, 905, 200, 0, 4, 'filter:drop-shadow(0 10px 14px rgba(0,0,0,.45))')}
   <div class=band><h1>Highland Cow <em>Christmas Clipart</em></h1><p>PNG + SVG · TRANSPARENT · 300 DPI</p></div>
   <div class=badge><b>12</b><span>DESIGNS</span></div>`,

  '2-all-designs': `<style>${base} body{background:${CREAM}}
   h1{position:absolute;top:20px;width:100%;text-align:center;margin:0;font-family:Fr;font-weight:900;font-size:64px}
   h1 em{font-style:normal;color:${BERRY}}
   .sub{position:absolute;top:100px;width:100%;text-align:center;font-size:25px;color:${PINE};font-weight:800;letter-spacing:1px}
   .g{position:absolute;top:148px;left:50px;right:50px;display:grid;grid-template-columns:repeat(4,1fr);gap:6px 30px}
   .c{height:316px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;position:relative}
   .c img{max-width:330px;max-height:272px;object-fit:contain;filter:drop-shadow(0 6px 8px rgba(44,27,54,.25))}
   .c div{margin-top:4px;font-size:22px;font-weight:800;color:${PLUM};white-space:nowrap}.c div b{color:${BERRY}}</style>
   <h1>All <em>12 designs</em></h1><div class=sub>full-color PNG with transparent background · matching one-color SVG</div>
   <div class=g>${S.map((s, i) => `<div class=c><img src="${png(s[0])}"><div><b>${i + 1}</b> ${s[1]}</div></div>`).join('')}</div>`,

  '3-mockup': `<style>${base}
   .card{position:absolute;right:36px;top:36px;background:rgba(44,27,54,.9);color:${CREAM};border-radius:24px;padding:26px 34px;z-index:9;box-shadow:0 12px 26px rgba(0,0,0,.45)}
   .card h2{margin:0 0 6px;font-family:Fr;font-weight:900;font-size:46px;line-height:1.05}.card h2 em{font-style:normal;color:${GOLD}}
   .card p{margin:0;font-size:24px;font-weight:700}</style>
   <img src="${B64(path.join('mockup', 'flatlay.jpg'), 'image/jpeg')}" style="position:absolute;left:0;top:-28px;width:1500px">
   <div class=card><h2>Tees, totes, <em>cards</em></h2><p>mugs, tumblers, tags and stickers too</p></div>`,

  '4-png-and-svg': `<style>${base} body{background:${PLUM};color:${CREAM}}
   h1{position:absolute;top:26px;width:100%;text-align:center;margin:0;font-family:Fr;font-weight:900;font-size:58px}h1 em{font-style:normal;color:${GOLD}}
   .p{position:absolute;border-radius:22px;overflow:hidden;box-shadow:0 10px 24px rgba(0,0,0,.4)}
   .p img{position:absolute;inset:0;margin:auto;max-width:86%;max-height:80%}
   .lab{position:absolute;font-size:25px;font-weight:800;color:${GOLD};text-align:center}
   .s{position:absolute;top:620px;width:300px;height:330px;background:#fff;border-radius:18px;box-shadow:0 10px 24px rgba(0,0,0,.4)}
   .s img{position:absolute;inset:0;margin:auto;max-width:86%;max-height:86%}</style>
   <h1>Every design as <em>PNG + SVG</em></h1>
   <div class=p style="left:60px;top:130px;width:430px;height:430px;${checker}"><img src="${png(slug(2))}"></div>
   <div class=lab style="left:60px;top:568px;width:430px">PNG: transparent background</div>
   <div class=p style="left:535px;top:130px;width:430px;height:430px;background:#5b2b35"><img src="${png(slug(2))}"></div>
   <div class=lab style="left:535px;top:568px;width:430px">sits cleanly on dark colors</div>
   <div class=p style="left:1010px;top:130px;width:430px;height:430px;background:#fff"><img src="${svg(slug(2))}"></div>
   <div class=lab style="left:1010px;top:568px;width:430px">SVG: one-color line art</div>
   ${[4, 8, 11, 12].map((n, i) => `<div class=s style="left:${60 + i * 350}px"><img src="${svg(slug(n))}"></div>`).join('')}
   <div class=lab style="left:0;top:1000px;width:1500px;color:${CREAM};font-size:27px">single-layer SVG for one-color prints, stamps and crafts · scales to any size · not a vinyl cut file</div>`,

  '5-whats-included': `<style>${base} body{background:${CREAM}}
   h1{position:absolute;left:720px;top:110px;margin:0;font-family:Fr;font-weight:900;font-size:66px;line-height:1.05}
   h1 em{font-style:normal;color:${BERRY}}
   ul{position:absolute;left:720px;top:290px;margin:0;padding:0;list-style:none;width:730px}
   li{font-size:29px;margin:0 0 20px;line-height:1.25;padding-left:44px;position:relative;font-weight:700}
   li::before{content:'';position:absolute;left:0;top:9px;width:22px;height:22px;border-radius:50%;background:${PINE}}
   li b{color:${BERRY}}</style>
   ${img(png(slug(10)), 90, 150, 800, -3, 2, 'filter:drop-shadow(0 12px 16px rgba(44,27,54,.35))')}
   ${img(png(slug(7)), 900, 820, 260, 0, 3, 'filter:drop-shadow(0 10px 14px rgba(44,27,54,.35))')}
   <h1>Ready for your<br><em>Christmas makes</em></h1>
   <ul><li><b>12 PNG files,</b> transparent background, 300 dpi</li>
   <li><b>3600 px</b> on the longest side (12 in)</li>
   <li><b>12 SVG files:</b> matching one-color line art</li>
   <li>Sublimation, print, print then cut, cards, stickers</li>
   <li>Small-business license: 500 items per design</li>
   <li>Digital download: no physical item is shipped</li></ul>`,
};

(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
  fs.mkdirSync('listing-images', { recursive: true });
  for (const [n, h] of Object.entries(pages)) {
    await p.setContent(`<!doctype html><meta charset=utf-8>${h}`, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot(n === '3-mockup' ? { path: `listing-images/${n}.jpg`, type: 'jpeg', quality: 92 } : { path: `listing-images/${n}.png` });
  }
  await b.close();
})();
