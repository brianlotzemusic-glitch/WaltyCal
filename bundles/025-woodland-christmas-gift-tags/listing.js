// Listing photos (3000x2250) from the real tag artwork. Run: NODE_PATH=$(npm root -g) node listing.js
const { chromium } = require('playwright'); const fs = require('fs');
const T = require('./tags.js');
const { PLUM, VIOLET, PINE, BERRY, GOLD, CREAM, KRAFT, fontCSS, SIZES, DESIGNS, smallDesigns, tagSVG, motifDefs } = T;
const px = (svg, wpx) => { const m = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/); const h = wpx * m[2] / m[1]; return svg.replace(/width="[\d.]+mm" height="[\d.]+mm"/, `width="${wpx}" height="${h.toFixed(1)}"`); };
let uid = 100;
const tag = (i, kind, wpx, style, cut = false) => `<div class=ab style="${style};filter:drop-shadow(0 ${wpx / 22}px ${wpx / 14}px rgba(0,0,0,.5))">${px(tagSVG((kind === 'large' ? DESIGNS : smallDesigns)[i], kind, uid++, { cut }), wpx)}</div>`;
const mo = (m, w, style) => `<div class=ab style="${style};filter:drop-shadow(0 6px 10px rgba(0,0,0,.45))"><svg width="${w}" viewBox="0 0 100 100"><use href="#m-${m}" transform="scale(${100 / Math.max(...require('child_process').execSync(`python3 -c "from PIL import Image;print(*Image.open('art/motifs/${m}.png').size)"`).toString().trim().split(' ').map(Number))})"/></svg></div>`;

const base = `${fontCSS}
*{box-sizing:border-box}html,body{margin:0}body{width:1500px;height:1125px;position:relative;overflow:hidden;font-family:Nu;color:${PLUM}}
.ab{position:absolute}
.wood{position:absolute;inset:0;background:
 repeating-linear-gradient(92deg,rgba(255,255,255,.035) 0 2px,rgba(0,0,0,0) 2px 9px,rgba(0,0,0,.08) 9px 11px,rgba(0,0,0,0) 11px 23px),
 repeating-linear-gradient(0deg,rgba(0,0,0,.0) 0 150px,rgba(0,0,0,.35) 150px 154px),
 linear-gradient(100deg,#3b2a26,#4a3329 40%,#34251f 70%,#47322a)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 45%,rgba(0,0,0,.55) 100%)}
.band{position:absolute;background:${PLUM};color:${CREAM};border-radius:22px;box-shadow:0 14px 30px rgba(0,0,0,.45);border:3px solid ${GOLD}}
.band h1{font-family:Fr;font-weight:900;margin:0;line-height:1.04}
.band h1 em{font-style:normal;color:${GOLD}}
.band .s{font-weight:800;letter-spacing:3px;text-transform:uppercase;color:${CREAM}}
.badge{position:absolute;background:${BERRY};color:${CREAM};font-weight:800;text-align:center;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-direction:column;box-shadow:0 8px 18px rgba(0,0,0,.45);border:4px solid ${GOLD};line-height:1.05}
.badge b{font-family:Fr;font-weight:900}
`;
function gift(x, y, w, h, rot, paper, ribbon, twine) {
  const k = `g${x}`;
  return `<div class=ab style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;transform:rotate(${rot}deg);filter:drop-shadow(0 22px 24px rgba(0,0,0,.55))">
  <svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"><defs><pattern id="${k}" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="14" height="14" fill="${paper}"/><path d="M0 14L14 0" stroke="rgba(255,255,255,.07)" stroke-width="2"/></pattern>
   <linearGradient id="${k}s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="#000" stop-opacity=".18"/></linearGradient></defs>
   <rect width="${w}" height="${h}" rx="6" fill="url(#${k})"/><rect width="${w}" height="${h}" rx="6" fill="url(#${k}s)"/>
   <rect x="${w / 2 - 22}" y="0" width="44" height="${h}" fill="${ribbon}"/><rect x="0" y="${h / 2 - 22}" width="${w}" height="44" fill="${ribbon}"/>
   <rect x="${w / 2 - 22}" y="0" width="44" height="${h}" fill="url(#${k}s)"/>
   <g transform="translate(${w / 2} ${h / 2})"><ellipse cx="-46" cy="-8" rx="46" ry="26" transform="rotate(-18 -46 -8)" fill="${ribbon}" stroke="rgba(0,0,0,.25)" stroke-width="2"/><ellipse cx="46" cy="-8" rx="46" ry="26" transform="rotate(18 46 -8)" fill="${ribbon}" stroke="rgba(0,0,0,.25)" stroke-width="2"/><rect x="-18" y="-18" width="36" height="36" rx="9" fill="${ribbon}" stroke="rgba(0,0,0,.3)" stroke-width="2"/></g>
  </svg></div>`;
}
const twine = (d, c = '#d9c08f') => `<svg class=ab style="left:0;top:0" width="1500" height="1125"><path d="${d}" fill="none" stroke="rgba(0,0,0,.35)" stroke-width="7" transform="translate(3 6)" stroke-linecap="round"/><path d="${d}" fill="none" stroke="${c}" stroke-width="5" stroke-linecap="round" stroke-dasharray="14 3"/></svg>`;

const scenes = {
'1-thumbnail': `
 <div class=wood></div>
 ${mo('pine', 330, 'left:520px;top:690px;transform:rotate(-70deg)')}
 ${gift(70, 430, 520, 470, -3, KRAFT, BERRY)}
 ${gift(640, 360, 500, 420, 3, '#2f4a3a', GOLD)}
 ${gift(930, 760, 470, 300, -2, '#e8dcc3', VIOLET)}
 ${mo('holly', 270, 'left:1190px;top:200px;transform:rotate(20deg)')}
 ${mo('pine', 300, 'left:1100px;top:30px;transform:rotate(100deg)')}
 ${tag(0, 'large', 205, 'left:270px;top:610px;transform:rotate(-9deg)')}
 ${tag(1, 'large', 205, 'left:830px;top:520px;transform:rotate(7deg)')}
 ${tag(3, 'large', 205, 'left:1150px;top:630px;transform:rotate(-12deg)')}
 ${tag(8, 'small', 150, 'left:640px;top:870px;transform:rotate(-24deg)')}
 ${tag(4, 'small', 150, 'left:760px;top:905px;transform:rotate(14deg)')}
 ${tag(11, 'small', 150, 'left:420px;top:915px;transform:rotate(-8deg)')}
 <div class=vig></div>
 <div class=band style="left:50px;top:42px;width:640px;height:370px;padding:30px 44px">
  <h1 style="font-size:74px">Printable<br>Christmas<br><em>Gift Tags</em></h1>
  <div class=s style="font-size:27px;margin-top:14px">Woodland · PDF Letter + A4</div></div>
 <div class=badge style="left:70px;top:905px;width:200px;height:200px;font-size:22px;transform:rotate(-8deg)"><b style="font-size:66px">24</b>tags<br>2 sizes</div>`,
'2-whats-included': `
 <div class=ab style="inset:0;background:${CREAM}"></div><div class=ab style="left:24px;top:24px;right:24px;bottom:24px;border:4px solid ${PLUM};border-radius:30px"></div>
 <div class=ab style="left:0;right:0;top:56px;text-align:center"><div style="font-weight:800;letter-spacing:6px;font-size:22px;color:${PINE}">WHAT YOU GET</div><div style="font-family:Fr;font-weight:900;font-size:66px;margin-top:6px">24 woodland <span style="color:${BERRY}">gift tags</span>, 2 sizes</div></div>
 ${[['pg-1','Large tags, page 1','6 tags · 2.5 x 4 in'],['pg-2','Large tags, page 2','6 tags · 2.5 x 4 in'],['pg-3','Small tags','12 tags · 1.75 x 2.75 in'],['pg-4','Print and make guide','4 simple steps']].map((p, i) => `<div class=ab style="left:${70 + i * 345}px;top:215px;width:320px"><img src="data:image/png;base64,${fs.readFileSync(`art/${p[0]}.png`).toString('base64')}" style="width:320px;display:block;border:3px solid ${PLUM};border-radius:6px;box-shadow:0 12px 24px rgba(44,27,54,.35);background:#fff"><div style="font-family:Fr;font-weight:700;font-size:27px;color:${BERRY};margin-top:16px">${p[1]}</div><div style="font-weight:700;font-size:22px;margin-top:3px">${p[2]}</div></div>`).join('')}
 ${[['2 file sizes','PDF in US Letter (8.5 x 11 in) and A4'],['12 designs','fox, owl, stag, robin, hedgehog, rabbit, toadstools, pine, moth, holly, mistletoe, moon'],['Ready to write','To and From lines, hole-punch marks, cut lines']].map((p, i) => `<div class=ab style="left:${70 + i * 460}px;top:810px;width:430px;height:190px;background:#fff;border:3px solid ${PLUM};border-radius:20px;padding:22px 26px"><div style="font-family:Fr;font-weight:900;font-size:34px;color:${BERRY}">${p[0]}</div><div style="font-weight:700;font-size:24px;line-height:1.35;margin-top:8px">${p[1]}</div></div>`).join('')}`,
'3-all-designs': `
 <div class=wood></div>
 ${DESIGNS.map((d, i) => { const c = i % 6, r = Math.floor(i / 6); return tag(i, 'large', 190, `left:${48 + c * 238}px;top:${210 + r * 330}px;transform:rotate(${[-2.5, 2, -1.5, 2.5, -2, 1.5][c] * (r ? -1 : 1)}deg)`); }).join('')}
 <div class=vig></div>
 <div class=band style="left:50px;top:36px;width:1400px;height:130px;padding:20px 40px;display:flex;align-items:center;justify-content:space-between"><h1 style="font-size:54px">12 designs, <em>no two alike</em></h1><div class=s style="font-size:22px;text-align:right">tartan · gingham · stripes · dots · kraft<br>five tag shapes</div></div>
 <div class=band style="left:50px;top:960px;width:1400px;height:110px;padding:0 40px;display:flex;align-items:center;justify-content:center;border-radius:20px"><div class=s style="font-size:27px">Each design comes as a large tag and a small tag (24 in all)</div></div>`,
'4-sizes-and-print': `
 <div class=ab style="inset:0;background:${CREAM}"></div><div class=ab style="left:24px;top:24px;right:24px;bottom:24px;border:4px solid ${PLUM};border-radius:30px"></div>
 <div class=ab style="left:0;right:0;top:56px;text-align:center"><div style="font-weight:800;letter-spacing:6px;font-size:22px;color:${PINE}">PRINT AT HOME</div><div style="font-family:Fr;font-weight:900;font-size:66px;margin-top:6px">Two sizes, <span style="color:${BERRY}">four steps</span></div></div>
 ${tag(0, 'large', 300, 'left:90px;top:225px', true)}
 ${tag(3, 'small', 210, 'left:470px;top:225px', true)}
 <div class=ab style="left:60px;top:735px;width:380px;text-align:center;font-family:Fr;font-weight:700;font-size:30px;color:${BERRY}">Large<div style="font-family:Nu;font-weight:800;font-size:21px;color:${PLUM};margin-top:4px;white-space:nowrap">2.5 x 4 in · 63.5 x 101.6 mm</div></div>
 <div class=ab style="left:400px;top:735px;width:380px;text-align:center;font-family:Fr;font-weight:700;font-size:30px;color:${BERRY}">Small<div style="font-family:Nu;font-weight:800;font-size:21px;color:${PLUM};margin-top:4px;white-space:nowrap">1.75 x 2.75 in · 44.5 x 69.9 mm</div></div>
 ${[['1','Print at 100%','Actual size on white or cream card stock'],['2','Cut on the grey line','Scissors, or a paper trimmer'],['3','Punch the hole','A 1/4 in (6 mm) punch on the ring mark'],['4','Write and tie','To and From, then twine or ribbon']].map((p, i) => `<div class=ab style="left:820px;top:${235 + i * 150}px;width:640px;display:flex;gap:26px;align-items:center"><div style="flex:none;width:92px;height:92px;border-radius:50%;background:${BERRY};color:${CREAM};font-family:Fr;font-weight:900;font-size:50px;display:flex;align-items:center;justify-content:center">${p[0]}</div><div><div style="font-family:Fr;font-weight:900;font-size:38px">${p[1]}</div><div style="font-weight:700;font-size:25px;margin-top:4px">${p[2]}</div></div></div>`).join('')}
 <div class=ab style="left:70px;top:900px;width:1360px;text-align:center;font-weight:800;font-size:25px;color:${PINE}">US Letter and A4 PDFs · printable at home · digital download, no physical item shipped</div>`,

};
(async () => {
  const b = await chromium.launch(); fs.mkdirSync('listing-images', { recursive: true });
  const only = process.argv[2];
  for (const [name, body] of Object.entries(scenes)) {
    if (only && !name.startsWith(only)) continue;
    const p = await b.newPage({ viewport: { width: 1500, height: 1125 }, deviceScaleFactor: 2 });
    await p.setContent(`<!doctype html><html><head><meta charset=utf-8><style>${base}</style></head><body>${motifDefs()}${body}</body></html>`, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: `listing-images/${name}.png` }); console.log(name); await p.close();
  }
  await b.close();
})();
