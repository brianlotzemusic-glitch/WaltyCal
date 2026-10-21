// Listing photos (3000x2250) from the real card artwork and PDF pages. Run: NODE_PATH=$(npm root -g) node listing.js
// needs art/pg-1..5.png (pdftoppm -r 110 -png of the US Letter PDF)
const { chromium } = require('playwright'); const fs = require('fs');
const T = require('./cards.js');
const { PLUM, PINE, BERRY, GOLD, CREAM, ROSE, BLUSH, PINK, fontCSS, CW, CH, TW, TH, CARDS, TAGS, cardSVG, tagSVG, motifDefs } = T;
let uid = 100;
const sized = (svg, w, h) => svg.replace(/width="[\d.]+mm" height="[\d.]+mm"/, `width="${w}" height="${h.toFixed(1)}"`);
const card = (d, w, style) => `<div class=ab style="${style};width:${w}px;filter:drop-shadow(0 ${w / 45}px ${w / 28}px rgba(44,27,54,.38))">${sized(cardSVG(d, uid++, { cut: false }), w, w * CH / CW)}</div>`;
const tag = (d, w, style, cut = false, string = true) => `<div class=ab style="${style};width:${w}px;filter:drop-shadow(0 ${w / 45}px ${w / 28}px rgba(44,27,54,.38))">${sized(tagSVG(d, uid++, { cut }), w, w * TH / TW)}${string ? `<div class=ab style="left:${w * .5 - 2}px;top:${w * 7.2 / TW * 1 - 40}px;width:4px;height:70px;background:${GOLD};border-radius:2px;transform:rotate(14deg);transform-origin:50% 100%;opacity:.95"></div>` : ''}</div>`;
const pg = n => `data:image/png;base64,${fs.readFileSync(`art/pg-${n}.png`).toString('base64')}`;
const base = `${fontCSS}
*{box-sizing:border-box}html,body{margin:0}body{width:1500px;height:1125px;position:relative;overflow:hidden;font-family:Nu;color:${PLUM}}
.ab{position:absolute}
.linen{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,#fbf1e4 0%,#f2dfd0 70%,#e8cdbf 100%)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 55%,rgba(90,31,58,.28) 100%)}
.band{position:absolute;background:${BERRY};color:${CREAM};border-radius:22px;box-shadow:0 14px 30px rgba(44,27,54,.4);border:3px solid ${GOLD}}
.band h1{font-family:Fr;font-weight:900;margin:0;line-height:1.04}.band h1 em{font-style:normal;color:${PINK}}
.band .s{font-weight:800;letter-spacing:3px;text-transform:uppercase}
.badge{position:absolute;background:${PINE};color:${CREAM};font-weight:800;text-align:center;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-direction:column;box-shadow:0 8px 18px rgba(0,0,0,.4);border:4px solid ${GOLD};line-height:1.05}
.badge b{font-family:Fr;font-weight:900}
.hd{font-weight:800;letter-spacing:6px;font-size:22px;color:${PINE}}.h1{font-family:Fr;font-weight:900;font-size:66px;margin-top:6px}.h1 span{color:${ROSE}}
`;
const frame = `<div class=ab style="inset:0;background:${CREAM}"></div><div class=ab style="left:24px;top:24px;right:24px;bottom:24px;border:4px solid ${PLUM};border-radius:30px"></div>`;
const scenes = {
'1-thumbnail': `
 <div class=linen></div><div class=vig></div>
 ${card(CARDS[0], 330, 'left:60px;top:395px;transform:rotate(-7deg)')}
 ${card(CARDS[3], 330, 'left:690px;top:430px;transform:rotate(6deg)')}
 ${card(CARDS[2], 330, 'left:375px;top:470px;transform:rotate(-1deg)')}
 ${tag(TAGS[1], 190, 'left:1060px;top:420px;transform:rotate(9deg)')}
 ${tag(TAGS[11], 190, 'left:1250px;top:470px;transform:rotate(-6deg)')}
 ${tag(TAGS[7], 190, 'left:1100px;top:720px;transform:rotate(-10deg)')}
 ${tag(TAGS[5], 190, 'left:1290px;top:760px;transform:rotate(7deg)')}
 ${tag(TAGS[2], 190, 'left:40px;top:150px;transform:rotate(-8deg)')}
 <div class=band style="left:300px;top:36px;width:900px;height:290px;padding:24px 40px;text-align:center">
  <h1 style="font-size:78px">Botanical <em>Valentine</em><br>Cards &amp; Gift Tags</h1>
  <div class=s style="font-size:26px;margin-top:14px">Printable · woodland animals &amp; roses</div></div>
 <div class=badge style="left:1230px;top:40px;width:230px;height:230px;font-size:24px;transform:rotate(8deg)"><b style="font-size:84px">26</b>cards &amp; tags<br>Letter + A4</div>`,
'2-whats-included': `
 ${frame}
 <div class=ab style="left:0;right:0;top:56px;text-align:center"><div class=hd>WHAT YOU GET</div><div class=h1>8 cards <span>+ 18 gift tags</span></div></div>
 ${[[1, 'Valentine cards, page 1', '4 cards per page · 2 pages'], [2, 'Valentine cards, page 2', '8 designs · To and From lines'], [3, 'Gift tags, page 3', '9 tags per page · 2 pages'], [5, 'Print and cut guide', '4 simple steps']].map((p, i) => `<div class=ab style="left:${70 + i * 345}px;top:215px;width:320px"><img src="${pg(p[0])}" style="width:320px;display:block;border:3px solid ${PLUM};border-radius:6px;box-shadow:0 12px 24px rgba(44,27,54,.35);background:#fff"><div style="font-family:Fr;font-weight:700;font-size:27px;color:${BERRY};margin-top:16px">${p[1]}</div><div style="font-weight:700;font-size:22px;margin-top:3px">${p[2]}</div></div>`).join('')}
 ${[['2 file sizes', 'PDF in US Letter (8.5 x 11 in) and A4, 5 pages each'], ['Cards 3.75 x 5 in', 'lovebirds, dove, rose heart wreath, fox, bunny, peony, hedgehog, tulips'], ['Tags 2.25 x 3.25 in', '12 designs plus 6 in a second colorway, with hole circle and To / From']].map((p, i) => `<div class=ab style="left:${70 + i * 460}px;top:810px;width:430px;height:190px;background:#fff;border:3px solid ${PLUM};border-radius:20px;padding:22px 26px"><div style="font-family:Fr;font-weight:900;font-size:34px;color:${BERRY}">${p[0]}</div><div style="font-weight:700;font-size:24px;line-height:1.35;margin-top:8px">${p[1]}</div></div>`).join('')}`,
'3-all-designs': `
 <div class=linen></div>
 ${TAGS.map((d, i) => { const c = i % 6, r = Math.floor(i / 6); return tag(d, 185, `left:${52 + c * 235}px;top:${185 + r * 290}px`, false, false); }).join('')}
 <div class=vig></div>
 <div class=band style="left:40px;top:30px;width:1420px;height:120px;padding:18px 40px;display:flex;align-items:center;justify-content:space-between"><h1 style="font-size:52px">Gift tags &amp; cards, <em>every pattern</em></h1><div class=s style="font-size:21px;text-align:right">gingham · tartan · stripes · dots<br>animals, roses, tulips &amp; peonies</div></div>`,
'4-fold-and-stand': `
 ${frame}
 <div class=ab style="left:0;right:0;top:56px;text-align:center"><div class=hd>PRINT AT HOME</div><div class=h1>Print, cut, <span>give</span></div></div>
 ${card(CARDS[0], 330, 'left:90px;top:225px;transform:rotate(-3deg)')}
 ${tag(TAGS[3], 190, 'left:490px;top:290px;transform:rotate(5deg)', true, true)}
 ${tag(TAGS[9], 190, 'left:660px;top:330px;transform:rotate(-4deg)', true, true)}
 <div class=ab style="left:70px;top:800px;width:760px;text-align:center;font-family:Fr;font-weight:700;font-size:27px;color:${BERRY}">Cards 3.75 x 5 in · tags 2.25 x 3.25 in<div style="font-family:Nu;font-weight:800;font-size:21px;color:${PLUM};margin-top:4px">grey cut lines · punch the tag circle</div></div>
 ${[['1', 'Print at 100%', 'Actual size on card stock'], ['2', 'Cut on the grey line', 'Scissors or a paper trimmer'], ['3', 'Punch the tag hole', 'Add twine or ribbon'], ['4', 'Write your note', 'To and From lines on every piece']].map((p, i) => `<div class=ab style="left:850px;top:${235 + i * 150}px;width:610px;display:flex;gap:26px;align-items:center"><div style="flex:none;width:92px;height:92px;border-radius:50%;background:${ROSE};color:${CREAM};font-family:Fr;font-weight:900;font-size:50px;display:flex;align-items:center;justify-content:center">${p[0]}</div><div><div style="font-family:Fr;font-weight:900;font-size:38px">${p[1]}</div><div style="font-weight:700;font-size:25px;margin-top:4px">${p[2]}</div></div></div>`).join('')}
 <div class=ab style="left:70px;top:1010px;width:1360px;text-align:center;font-weight:800;font-size:25px;color:${PINE}">US Letter and A4 PDFs · printable at home · digital download, no physical item shipped</div>`,
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
