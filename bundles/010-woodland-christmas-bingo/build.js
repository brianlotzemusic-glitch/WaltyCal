// Builds the printable PDFs (US Letter + A4) from icons.json + cards.json.
// Run from this folder: NODE_PATH=$(npm root -g) node build.js
// Pages: 1 instructions, 15 card pages (2 cards each), 2 calling-card pages,
// 1 caller checklist, 1 markers sheet (72 solid gold discs) = 20 pages.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const { icons, free } = JSON.parse(fs.readFileSync('icons.json', 'utf8'));
const { cards } = JSON.parse(fs.readFileSync('cards.json', 'utf8'));
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf';
const FONT = f => `data:font/ttf;base64,${fs.readFileSync(path.join('fonts', f)).toString('base64')}`;
const SHOP = 'Duskwood Designs Co';

const defs = `<svg width="0" height="0" style="position:absolute"><defs>${icons.map(i => `<symbol id="i${i.id}" viewBox="0 0 1000 1000">${i.svg}</symbol>`).join('')}
<symbol id="free" viewBox="0 0 1000 1000">${free}</symbol></defs></svg>`;
const I = (id, cls = '') => `<svg class="ic ${cls}" viewBox="0 0 1000 1000"><use href="#i${id}"/></svg>`;
const cap = s => s.replace(/(^|\s)\S/g, m => m.toUpperCase());

const css = (W, H) => `
@font-face{font-family:Fr;font-weight:700;src:url(${FONT('Fraunces-700.ttf')})}
@font-face{font-family:Fr;font-weight:900;src:url(${FONT('Fraunces-900.ttf')})}
@font-face{font-family:Nu;font-weight:400;src:url(${FONT('Nunito-400.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${FONT('Nunito-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${FONT('Nunito-800.ttf')})}
@page{size:${W}mm ${H}mm;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:Nu;color:${PLUM};-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:${W}mm;height:${H}mm;position:relative;overflow:hidden;page-break-after:always;background:#fff}
.ic{display:block;width:100%;height:100%}
/* ---- bingo card (one half page) ---- */
.half{position:absolute;left:0;width:${W}mm;height:${H / 2}mm}
.half.top{top:0}.half.bot{top:${H / 2}mm}
.card{position:absolute;left:9mm;right:9mm;border:0.7mm solid ${PLUM};border-radius:5mm;display:flex;padding:3.2mm;gap:3.2mm}
.card::after{content:'';position:absolute;inset:1.3mm;border:0.25mm solid ${PINE};border-radius:3.8mm;pointer-events:none}
.half.top .card{top:9mm;bottom:6.5mm}.half.bot .card{top:6.5mm;bottom:9mm}
.side{width:35mm;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:2.5mm 0 1.5mm}
.side .wc{font-family:Fr;font-weight:700;font-size:3.9mm;line-height:1.05;text-align:center;color:${PINE};letter-spacing:.15mm}
.side .bingo{display:flex;flex-direction:column;align-items:center;line-height:.86}
.side .bingo span{font-family:Fr;font-weight:900;font-size:${(H / 2 - 15.5) * 0.118}mm}
.side .bingo span:nth-child(odd){color:${BERRY}}.side .bingo span:nth-child(even){color:${PINE}}
.side .no{font-family:Fr;font-weight:700;font-size:3.6mm;color:${PLUM};border:0.35mm solid ${PLUM};border-radius:2.5mm;padding:.5mm 2.4mm}
.side .sprig{width:13mm;height:13mm}
.grid{flex:1;display:grid;grid-template-columns:repeat(5,1fr);grid-template-rows:repeat(5,1fr);border:0.5mm solid ${PLUM};border-radius:2mm;overflow:hidden;position:relative;z-index:1}
.cell{border-right:0.35mm solid ${PLUM};border-bottom:0.35mm solid ${PLUM};display:flex;align-items:center;justify-content:center;padding:1.6mm;min-width:0;min-height:0}
.cell:nth-child(5n){border-right:0}.cell:nth-child(n+21){border-bottom:0}
.cell .ic{width:auto;height:100%;aspect-ratio:1}
.cell.free{background:#fbf6ea;flex-direction:column;padding:1mm}
.cell.free .ic{height:48%;margin-bottom:.8mm}
.cell.free b{font-family:Fr;font-weight:900;font-size:4.6mm;color:${BERRY};letter-spacing:.4mm;line-height:1}
.cut{position:absolute;left:4mm;right:4mm;top:${H / 2}mm;border-top:0.3mm dashed #9a8fa0}
.cut span{position:absolute;left:50%;top:-2.2mm;transform:translateX(-50%);background:#fff;padding:0 2mm;font-size:2.8mm;color:#7d7183;font-family:Nu}
/* ---- shared page furniture ---- */
.head{position:absolute;top:10mm;left:12mm;right:12mm;text-align:center}
.head h1{font-family:Fr;font-weight:900;font-size:10mm;margin:0;color:${PLUM};line-height:1.05}
.head h1 em{font-style:normal;color:${BERRY}}
.head p{margin:1.5mm 0 0;font-size:4.2mm;color:${PINE};font-weight:700}
.foot{position:absolute;bottom:6mm;left:0;right:0;text-align:center;font-size:2.7mm;color:#7d7183}
/* calling cards */
.cc{position:absolute;top:29mm;bottom:13mm;left:10mm;right:10mm;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-rows:repeat(5,minmax(0,1fr))}
.cc>div{border:0.3mm dashed #9a8fa0;margin:-0.15mm;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1.2mm;padding:2.5mm}
.cc .ic{height:31mm;width:31mm}
.cc b{font-family:Fr;font-weight:700;font-size:5mm;color:${PLUM}}
/* checklist */
.ck{position:absolute;top:31mm;bottom:16mm;left:12mm;right:12mm;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));grid-template-rows:repeat(6,minmax(0,1fr));gap:2.4mm}
.ck>div{border:0.35mm solid ${PLUM};border-radius:3mm;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;padding:2mm}
.ck .ic{height:21mm;width:21mm}
.ck b{font-family:Nu;font-weight:800;font-size:4mm;margin-top:1mm}
.ck i{position:absolute;top:2mm;right:2mm;width:5mm;height:5mm;border:0.4mm solid ${PINE};border-radius:50%}
/* markers */
.mk{position:absolute;top:33mm;left:0;right:0;display:grid;justify-content:center;gap:2.2mm}
.mk>div{width:22mm;height:22mm;border-radius:50%;background:${GOLD};border:0.6mm solid ${PLUM};box-shadow:inset 0 0 0 1.6mm ${GOLD},inset 0 0 0 1.9mm ${CREAM}}
/* instructions */
.ins{position:absolute;top:${H < 290 ? 44 : 48}mm;left:16mm;right:16mm;bottom:14mm;display:grid;grid-template-columns:1fr 1fr;gap:4mm 7mm;align-content:start}
.ins h2{font-family:Fr;font-weight:900;font-size:6.2mm;color:${BERRY};margin:0 0 2mm}
.ins p,.ins li{font-size:${H < 290 ? 3.5 : 3.75}mm;line-height:1.45;margin:0 0 1.4mm}
.ins ol,.ins ul{margin:0;padding-left:5mm}
.ways{display:grid;grid-template-columns:repeat(5,1fr);gap:3mm;grid-column:1/3}
.way{text-align:center;font-size:3.6mm;font-weight:800}
.mini{display:grid;grid-template-columns:repeat(5,1fr);gap:.6mm;width:25mm;height:25mm;margin:0 auto 1.5mm}
.mini i{border:0.25mm solid ${PLUM};border-radius:.6mm}.mini i.on{background:${GOLD}}.mini i.fr{background:${CREAM}}
.strip{position:absolute;top:${H < 290 ? 28 : 30}mm;left:16mm;right:16mm;display:flex;justify-content:space-between}
.strip .ic{width:14mm;height:14mm}
.box{border:0.35mm solid ${PINE};border-radius:3mm;padding:3mm 4mm}
`;

function cardHTML(n, grid, pos) {
  const cells = grid.map(id => id === null
    ? `<div class="cell free"><svg class=ic viewBox="0 0 1000 1000"><use href="#free"/></svg><b>FREE</b></div>`
    : `<div class=cell>${I(id)}</div>`).join('');
  return `<div class="half ${pos}"><div class=card><div class=side>
    <div class=wc>Woodland<br>Christmas</div>
    <div class=bingo>${'BINGO'.split('').map(c => `<span>${c}</span>`).join('')}</div>
    <svg class=sprig viewBox="0 0 1000 1000"><use href="#i13"/></svg>
    <div class=no>Card ${String(n).padStart(2, '0')}</div></div>
    <div class=grid>${cells}</div></div></div>`;
}

function mini(on) {
  return `<div class=mini>${Array.from({ length: 25 }, (_, k) => `<i class="${on(k % 5, Math.floor(k / 5)) ? 'on' : k === 12 ? 'fr' : ''}"></i>`).join('')}</div>`;
}

function pages(W, H, sizeName) {
  const out = [];
  const strip = [0, 4, 1, 22, 2, 13, 3, 6, 25, 10, 15].map(i => I(i)).join('');
  out.push(`<div class=page>
  <div class=head><h1>Woodland <em>Christmas</em> Bingo</h1><p>30 picture cards for 2 to 30 players · ages 3 and up</p></div>
  <div class=strip>${strip}</div>
  <div class=ins>
   <div><h2>What's inside</h2><ul>
    <li>Page 1: how to play (this page)</li><li>Pages 2 to 16: 30 different bingo cards, 2 per page</li>
    <li>Pages 17 and 18: 30 calling cards to cut apart</li><li>Page 19: caller's checklist</li><li>Page 20: 72 markers (enough for 3 players at blackout)</li></ul>
    <h2 style="margin-top:4mm">Getting ready</h2><ol>
    <li>Print the cards and cut each page in half along the dashed line.</li>
    <li>Cut apart the calling cards and put them in a bowl, hat or stocking.</li>
    <li>Cut out the markers, or use buttons, mini marshmallows, candies or acorns.</li></ol></div>
   <div><h2>How to play</h2><ol>
    <li>Give each player a bingo card and a handful of markers.</li>
    <li>Everyone covers the FREE space in the middle.</li>
    <li>The caller draws one calling card at a time, shows the picture and says its name, then ticks it on the checklist.</li>
    <li>If that picture is on your card, cover it with a marker.</li>
    <li>When you complete the pattern for the round, shout "BINGO!"</li>
    <li>The caller checks your card against the checklist. If every picture was called, you win the round.</li></ol>
    <p style="margin-top:2mm">Each card has 24 of the 30 pictures, no two cards are the same, and no two cards share a winning row, column or diagonal.</p></div>
   <div class=box style="grid-column:1/3"><h2>Ways to win</h2><div class=ways>
    <div class=way>${mini((x, y) => y === 2)}Any line</div>
    <div class=way>${mini((x, y) => (x === 0 || x === 4) && (y === 0 || y === 4))}Four corners</div>
    <div class=way>${mini((x, y) => x === y || x + y === 4)}Snowy X</div>
    <div class=way>${mini((x, y) => x === 0 || x === 4 || y === 0 || y === 4)}Picture frame</div>
    <div class=way>${mini(() => true)}Blackout</div></div><p style="margin:2.5mm 0 0;text-align:center"><b>Tie?</b> Two BINGOs on the same call: both win, or play one quick "any line" round.</p></div>
   <div class=box><h2>Printing tips</h2><p>Print at 100% or "actual size" (not "fit to page") on ${sizeName} paper. Card stock (65 to 110 lb, 176 to 300 gsm) makes sturdy cards you can reuse year after year. The light backgrounds are kind to your ink. Slip cards into sheet protectors and use dry-erase markers to play again and again.</p></div>
   <div class=box><h2>Party ideas</h2><p>Play a quick round with "any line", then finish with a blackout round for the big prize. Let little ones take turns as the caller; they can read the pictures before they can read words. Small prizes that work well: candy canes, stickers, hot cocoa packets or first pick of the cookie plate.</p></div>
  </div>
  <div class=foot>© ${SHOP} · For personal use: print as many copies as you like for your own family, party or classroom. Please don't share or resell the files.</div></div>`);
  for (let i = 0; i < cards.length; i += 2) {
    out.push(`<div class=page>${cardHTML(i + 1, cards[i], 'top')}<div class=cut><span>✂ cut here</span></div>${cardHTML(i + 2, cards[i + 1], 'bot')}</div>`);
  }
  for (let p = 0; p < 2; p++) {
    const ids = icons.slice(p * 15, p * 15 + 15);
    out.push(`<div class=page><div class=head><h1>Calling <em>Cards</em></h1><p>Cut apart along the dashed lines · sheet ${p + 1} of 2</p></div>
    <div class=cc>${ids.map(i => `<div>${I(i.id)}<b>${cap(i.name)}</b></div>`).join('')}</div>
    <div class=foot>Woodland Christmas Bingo · ${SHOP}</div></div>`);
  }
  out.push(`<div class=page><div class=head><h1>Caller's <em>Checklist</em></h1><p>Tick each picture as you call it, then check winning cards against this list</p></div>
  <div class=ck>${icons.map(i => `<div><i></i>${I(i.id)}<b>${cap(i.name)}</b></div>`).join('')}</div>
  <div class=foot>Tip: slip this page into a sheet protector and tick with a dry-erase marker to reuse it every round · ${SHOP}</div></div>`);
  const cols = 8, rows = 9;
  const tok = () => '<div></div>';
  out.push(`<div class=page><div class=head><h1>Bingo <em>Markers</em></h1><p>${cols * rows} markers, enough for 3 players at blackout · print this page again for every 3 more players</p></div>
  <div class=mk style="grid-template-columns:repeat(${cols},22mm)">${Array.from({ length: cols * rows }, (_, k) => tok(k)).join('')}</div>
  <div class=foot>Woodland Christmas Bingo · ${SHOP}</div></div>`);
  return out;
}

const SIZES = { letter: [215.9, 279.4, 'US Letter'], a4: [210, 297, 'A4'] };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  fs.mkdirSync('bundle', { recursive: true });
  for (const [key, [W, H, name]] of Object.entries(SIZES)) {
    const html = `<!doctype html><html><head><meta charset=utf-8><style>${css(W, H)}</style></head><body>${defs}${pages(W, H, name).join('')}</body></html>`;
    await p.setContent(html, { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready);
    const file = `bundle/woodland-christmas-bingo-${key === 'a4' ? 'A4' : 'US-Letter'}.pdf`;
    await p.pdf({ path: file, width: `${W}mm`, height: `${H}mm`, printBackground: true, preferCSSPageSize: true });
    console.log(file);
  }
  await b.close();
})();
