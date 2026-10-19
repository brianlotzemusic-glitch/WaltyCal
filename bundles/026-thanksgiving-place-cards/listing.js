// Listing photos (3000x2250) from the real card artwork and PDF pages. Run: NODE_PATH=$(npm root -g) node listing.js
// needs art/pg-1..5.png (pdftoppm -r 110 -png of the US Letter PDF)
const { chromium } = require('playwright'); const fs = require('fs');
const T = require('./cards.js');
const { PLUM, PINE, BERRY, GOLD, CREAM, RUSSET, OCHRE, fontCSS, W: CW, H: CH, FOLD, DESIGNS, MENUS, cardSVG, motifDefs } = T;
let uid = 100;
const sized = (svg, wpx, hpx) => svg.replace(/width="[\d.]+mm" height="[\d.]+mm"/, `width="${wpx}" height="${hpx.toFixed(1)}"`);
const front = (d, kind, wpx, style, shadow = true) => { // standing tent, front view
  const h = CH - FOLD; let s = cardSVG(d, kind, uid++, { cut: false }).replace(`viewBox="0 0 ${CW} ${CH}"`, `viewBox="0 ${FOLD} ${CW} ${h}"`).replace('overflow:visible', 'overflow:hidden');
  const hp = wpx * h / CW;
  return `<div class=ab style="${style};width:${wpx}px;height:${hp}px">
   ${shadow ? `<div class=ab style="left:4%;right:4%;bottom:-${hp * .05}px;height:${hp * .12}px;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,.6),rgba(0,0,0,0) 70%)"></div>` : ''}
   <div class=ab style="inset:0;filter:drop-shadow(0 ${wpx / 60}px ${wpx / 40}px rgba(0,0,0,.4))">${sized(s, wpx, hp)}</div>
   <div class=ab style="left:0;right:0;top:0;height:${hp * .05}px;background:linear-gradient(rgba(255,255,255,.35),rgba(255,255,255,0))"></div></div>`;
};
const flat = (d, kind, wpx, style) => `<div class=ab style="${style};filter:drop-shadow(0 ${wpx / 40}px ${wpx / 25}px rgba(44,27,54,.35))">${sized(cardSVG(d, kind, uid++, { cut: true }), wpx, wpx * CH / CW)}</div>`;
const mo = (m, w, style) => `<div class=ab style="${style};filter:drop-shadow(0 6px 10px rgba(0,0,0,.45))"><svg width="${w}" height="${w}" viewBox="0 0 100 100"><use href="#m-${m}" transform="scale(${100 / Math.max(...require('child_process').execSync(`python3 -c "from PIL import Image;print(*Image.open('art/motifs/${m}.png').size)"`).toString().trim().split(' ').map(Number))})"/></svg></div>`;
const pg = n => `data:image/png;base64,${fs.readFileSync(`art/pg-${n}.png`).toString('base64')}`;

const base = `${fontCSS}
*{box-sizing:border-box}html,body{margin:0}body{width:1500px;height:1125px;position:relative;overflow:hidden;font-family:Nu;color:${PLUM}}
.ab{position:absolute}
.wall{position:absolute;left:0;right:0;top:0;height:560px;background:radial-gradient(ellipse at 50% 100%,#6b3b3b 0%,#3d2536 55%,#2a1a2b 100%)}
.wood{position:absolute;left:0;right:0;top:560px;bottom:0;background:
 repeating-linear-gradient(92deg,rgba(255,255,255,.04) 0 2px,rgba(0,0,0,0) 2px 9px,rgba(0,0,0,.09) 9px 11px,rgba(0,0,0,0) 11px 23px),
 repeating-linear-gradient(0deg,rgba(0,0,0,.0) 0 150px,rgba(0,0,0,.35) 150px 154px),
 linear-gradient(100deg,#5a3a2a,#6b4631 40%,#503324 70%,#64402d)}
.edge{position:absolute;left:0;right:0;top:552px;height:14px;background:linear-gradient(#2a1a14,#7a5238);box-shadow:0 6px 12px rgba(0,0,0,.5)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 50%,rgba(0,0,0,.5) 100%)}
.band{position:absolute;background:${PLUM};color:${CREAM};border-radius:22px;box-shadow:0 14px 30px rgba(0,0,0,.45);border:3px solid ${GOLD}}
.band h1{font-family:Fr;font-weight:900;margin:0;line-height:1.04}.band h1 em{font-style:normal;color:${OCHRE}}
.band .s{font-weight:800;letter-spacing:3px;text-transform:uppercase;color:${CREAM}}
.badge{position:absolute;background:${RUSSET};color:${CREAM};font-weight:800;text-align:center;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-direction:column;box-shadow:0 8px 18px rgba(0,0,0,.45);border:4px solid ${GOLD};line-height:1.05}
.badge b{font-family:Fr;font-weight:900}
`;
const scenes = {
'1-thumbnail': `
 <div class=wall></div><div class=wood></div><div class=edge></div>
 ${front(DESIGNS[0], 'place', 400, 'left:70px;top:455px')}
 ${front(DESIGNS[4], 'place', 400, 'left:550px;top:455px')}
 ${front(DESIGNS[7], 'place', 400, 'left:1030px;top:455px')}
 ${mo('maple', 190, 'left:20px;top:830px;transform:rotate(-25deg)')}
 ${mo('wheat', 230, 'left:1230px;top:800px;transform:rotate(30deg)')}
 ${front(DESIGNS[1], 'place', 440, 'left:240px;top:800px')}
 ${front(DESIGNS[2], 'place', 440, 'left:790px;top:800px')}
 ${mo('acorns', 200, 'left:700px;top:700px;transform:rotate(-10deg)')}
 <div class=vig></div>
 <div class=band style="left:50px;top:42px;width:860px;height:330px;padding:28px 46px">
  <h1 style="font-size:84px">Thanksgiving<br><em>Place Cards</em></h1>
  <div class=s style="font-size:29px;margin-top:16px">Woodland autumn · fold-and-stand</div></div>
 <div class=badge style="left:1130px;top:60px;width:260px;height:260px;font-size:26px;transform:rotate(8deg)"><b style="font-size:92px">16</b>cards<br>Letter + A4</div>`,
'2-whats-included': `
 <div class=ab style="inset:0;background:${CREAM}"></div><div class=ab style="left:24px;top:24px;right:24px;bottom:24px;border:4px solid ${PLUM};border-radius:30px"></div>
 <div class=ab style="left:0;right:0;top:56px;text-align:center"><div style="font-weight:800;letter-spacing:6px;font-size:22px;color:${PINE}">WHAT YOU GET</div><div style="font-family:Fr;font-weight:900;font-size:66px;margin-top:6px">12 place cards <span style="color:${RUSSET}">+ 4 menu tents</span></div></div>
 ${[[1, 'Place cards, page 1', '4 cards · 3 pages in all'], [3, 'Place cards, page 3', '12 designs · name line'], [4, 'Menu tents', 'Mains, Sides, Desserts, Drinks'], [5, 'Print, cut, fold guide', '4 simple steps']].map((p, i) => `<div class=ab style="left:${70 + i * 345}px;top:215px;width:320px"><img src="${pg(p[0])}" style="width:320px;display:block;border:3px solid ${PLUM};border-radius:6px;box-shadow:0 12px 24px rgba(44,27,54,.35);background:#fff"><div style="font-family:Fr;font-weight:700;font-size:27px;color:${BERRY};margin-top:16px">${p[1]}</div><div style="font-weight:700;font-size:22px;margin-top:3px">${p[2]}</div></div>`).join('')}
 ${[['2 file sizes', 'PDF in US Letter (8.5 x 11 in) and A4, 5 pages each'], ['12 designs', 'fox, hedgehog, squirrel, owl, turkey, deer, acorns, oak leaf, wheat, mushrooms, maple, apple'], ['Fold and stand', '3.5 x 2 in tents with cut lines and fold lines']].map((p, i) => `<div class=ab style="left:${70 + i * 460}px;top:810px;width:430px;height:190px;background:#fff;border:3px solid ${PLUM};border-radius:20px;padding:22px 26px"><div style="font-family:Fr;font-weight:900;font-size:34px;color:${BERRY}">${p[0]}</div><div style="font-weight:700;font-size:24px;line-height:1.35;margin-top:8px">${p[1]}</div></div>`).join('')}`,
'3-all-designs': `
 <div class=wall style="height:100%"></div>
 ${DESIGNS.map((d, i) => { const c = i % 4, r = Math.floor(i / 4); return front(d, 'place', 330, `left:${52 + c * 360}px;top:${232 + r * 230}px`); }).join('')}
 <div class=vig></div>
 <div class=band style="left:50px;top:36px;width:1400px;height:130px;padding:20px 40px;display:flex;align-items:center;justify-content:space-between"><h1 style="font-size:54px">12 designs, <em>no two alike</em></h1><div class=s style="font-size:22px;text-align:right">tartan · gingham · stripes · dots<br>woodland animals and autumn leaves</div></div>
 <div class=band style="left:50px;top:975px;width:1400px;height:100px;padding:0 40px;display:flex;align-items:center;justify-content:center;border-radius:20px"><div class=s style="font-size:26px">Name line on both sides · plus 4 write-in menu tents</div></div>`,
'4-fold-and-stand': `
 <div class=ab style="inset:0;background:${CREAM}"></div><div class=ab style="left:24px;top:24px;right:24px;bottom:24px;border:4px solid ${PLUM};border-radius:30px"></div>
 <div class=ab style="left:0;right:0;top:56px;text-align:center"><div style="font-weight:800;letter-spacing:6px;font-size:22px;color:${PINE}">PRINT AT HOME</div><div style="font-family:Fr;font-weight:900;font-size:66px;margin-top:6px">Cut, fold, <span style="color:${RUSSET}">stand</span></div></div>
 ${flat(DESIGNS[0], 'place', 290, 'left:90px;top:225px')}
 <div class=ab style="left:405px;top:335px;font-family:Fr;font-weight:900;font-size:70px;color:${RUSSET}">&rarr;</div>
 ${front(DESIGNS[0], 'place', 290, 'left:480px;top:360px')}
 <div class=ab style="left:80px;top:700px;width:310px;text-align:center;font-family:Fr;font-weight:700;font-size:29px;color:${BERRY}">Flat · 3.5 x 4 in<div style="font-family:Nu;font-weight:800;font-size:21px;color:${PLUM};margin-top:4px">grey cut line, dashed fold</div></div>
 <div class=ab style="left:440px;top:700px;width:370px;text-align:center;font-family:Fr;font-weight:700;font-size:29px;color:${BERRY}">Folded · 3.5 x 2 in<div style="font-family:Nu;font-weight:800;font-size:21px;color:${PLUM};margin-top:4px">stands on any table</div></div>
 ${[['1', 'Print at 100%', 'Actual size on card stock'], ['2', 'Cut on the grey line', 'Scissors or a paper trimmer'], ['3', 'Score and fold', 'Along the dashed line'], ['4', 'Write the name', 'Pen on the line, then stand it up']].map((p, i) => `<div class=ab style="left:850px;top:${235 + i * 150}px;width:610px;display:flex;gap:26px;align-items:center"><div style="flex:none;width:92px;height:92px;border-radius:50%;background:${RUSSET};color:${CREAM};font-family:Fr;font-weight:900;font-size:50px;display:flex;align-items:center;justify-content:center">${p[0]}</div><div><div style="font-family:Fr;font-weight:900;font-size:38px">${p[1]}</div><div style="font-weight:700;font-size:25px;margin-top:4px">${p[2]}</div></div></div>`).join('')}
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
