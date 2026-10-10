// Builds the printable PDFs (US Letter + A4) from icons.json + clues.json.
// Run from this folder: NODE_PATH=$(npm root -g) node build.js
// Pages: 1 how to play, 2 answer key + hunt planner, 3-6 clue cards (15 clues + the
// "Hooray" treasure card, 4 per page), 7 write-your-own cards, 8 hunt tracker = 8 pages.
// Stops with an error if any text box overflows or any rhyme line would wrap.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const { icons } = JSON.parse(fs.readFileSync('icons.json', 'utf8'));
const { clues, treasure } = JSON.parse(fs.readFileSync('clues.json', 'utf8'));
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf';
const FONT = f => `data:font/ttf;base64,${fs.readFileSync(path.join('fonts', f)).toString('base64')}`;
const SHOP = 'Duskwood Designs Co';
const BLANK = [{ code: 'P', icon: 13 }, { code: 'Q', icon: 14 }, { code: 'R', icon: 8 }, { code: 'S', icon: 6 }];

const defs = `<svg width="0" height="0" style="position:absolute"><defs>${icons.map(i => `<symbol id="i${i.id}" viewBox="0 0 1000 1000">${i.svg}</symbol>`).join('')}</defs></svg>`;
const I = (id, cls = '') => `<svg class="ic ${cls}" viewBox="0 0 1000 1000"><use href="#i${id}"/></svg>`;

const css = (W, H) => {
  const short = H < 290; // US Letter is 17.6 mm shorter than A4
  return `
@font-face{font-family:Fr;font-weight:700;src:url(${FONT('Fraunces-700.ttf')})}
@font-face{font-family:Fr;font-weight:900;src:url(${FONT('Fraunces-900.ttf')})}
@font-face{font-family:Nu;font-weight:400;src:url(${FONT('Nunito-400.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${FONT('Nunito-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${FONT('Nunito-800.ttf')})}
@page{size:${W}mm ${H}mm;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:Nu;color:${PLUM};-webkit-print-color-adjust:exact;print-color-adjust:exact;text-wrap:pretty}
.page{width:${W}mm;height:${H}mm;position:relative;overflow:hidden;page-break-after:always;background:#fff}
.ic{display:block;width:100%;height:100%}
/* ---- clue cards: 2 x 2 per page ---- */
.slot{position:absolute;width:${(W - 26) / 2}mm;height:${(H - 26) / 2}mm}
.s0{left:9mm;top:9mm}.s1{left:${W / 2 + 4}mm;top:9mm}.s2{left:9mm;top:${H / 2 + 4}mm}.s3{left:${W / 2 + 4}mm;top:${H / 2 + 4}mm}
.card{position:absolute;inset:0;border:0.7mm solid ${PLUM};border-radius:5mm;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:6mm 5mm 7mm}
.card::after{content:'';position:absolute;inset:1.3mm;border:0.25mm solid ${PINE};border-radius:3.8mm;pointer-events:none}
.card .no{position:absolute;top:4.5mm;right:4.5mm;width:13mm;height:13mm;border:0.4mm solid ${PINE};border-radius:50%;display:flex;align-items:flex-start;justify-content:center;padding-top:1.3mm;font-size:2.5mm;font-weight:800;color:${PINE};letter-spacing:.2mm}
.card .code{position:absolute;bottom:3.6mm;left:5mm;font-size:2.6mm;font-weight:800;color:#8c8193}
.card .sprig{position:absolute;bottom:3mm;right:4.5mm;width:7mm;height:7mm}
.card .art{width:${short ? 33 : 37}mm;height:${short ? 33 : 37}mm;flex:none}
.card .kick{font-size:2.7mm;font-weight:800;letter-spacing:.55mm;color:${PINE};margin-top:${short ? 2 : 3}mm}
.card h3{font-family:Fr;font-weight:900;font-size:9.5mm;line-height:1;margin:.6mm 0 0;color:${BERRY}}
.card .rhyme{margin-top:${short ? 2.6 : 4}mm;text-align:center;overflow:hidden}
.card .ln{white-space:nowrap;font-size:${short ? 4.45 : 4.6}mm;line-height:1.36;font-weight:700;overflow:hidden}
.card .gap{height:${short ? 2 : 3}mm}
.card.blank{justify-content:flex-start}.card .rule{width:100%;flex:1;margin-top:3mm;display:flex;flex-direction:column;justify-content:space-evenly;padding:0 2mm 7mm}
.card .rule i{display:block;border-bottom:0.3mm solid #b9afbe}
.card.treasure{background:#fbf6ea}
.vcut{position:absolute;top:4mm;bottom:4mm;left:${W / 2}mm;border-left:0.3mm dashed #9a8fa0}
.hcut{position:absolute;left:4mm;right:4mm;top:${H / 2}mm;border-top:0.3mm dashed #9a8fa0}
.hcut span{position:absolute;left:4mm;top:-2.3mm;background:#fff;padding:0 1.2mm;font-size:3mm;color:#7d7183}
/* ---- shared page furniture ---- */
.head{position:absolute;top:${short ? 10 : 12}mm;left:12mm;right:12mm;text-align:center}
.head .k{font-size:3.3mm;font-weight:800;letter-spacing:.9mm;color:${PINE}}
.head h1{font-family:Fr;font-weight:900;font-size:10.5mm;margin:.6mm 0 0;color:${PLUM};line-height:1.05}
.head h1 em{font-style:normal;color:${BERRY}}
.head p{margin:1.4mm 0 0;font-size:3.9mm;color:${PINE};font-weight:700}
.foot{position:absolute;bottom:6mm;left:0;right:0;text-align:center;font-size:2.7mm;color:#7d7183}
.strip{position:absolute;left:16mm;right:16mm;display:flex;justify-content:space-between}
.strip .ic{width:13mm;height:13mm}
.ground{position:absolute;left:14mm;right:14mm;bottom:12mm;height:${short ? 20 : 22}mm;display:flex;align-items:flex-end;justify-content:space-between;border-bottom:0.45mm solid ${PINE}}
.ground .ic{height:100%;width:auto;aspect-ratio:1}.ground .sm{height:58%}
/* instructions */
.ins{position:absolute;top:${short ? 48 : 52}mm;left:15mm;right:15mm;bottom:${short ? 34 : 35}mm;display:grid;grid-template-columns:1fr 1fr;gap:${short ? 4.5 : 5.5}mm 7mm;align-content:start}
.ins h2{font-family:Fr;font-weight:900;font-size:6.4mm;color:${BERRY};margin:0 0 1.6mm}
.ins p,.ins li{font-size:${short ? 3.75 : 3.8}mm;line-height:1.45;margin:0 0 1.1mm}
.ins ol,.ins ul{margin:0;padding-left:5mm}
.box{border:0.35mm solid ${PINE};border-radius:3mm;padding:2.6mm 4mm}
.wide{grid-column:1/3}
/* answer key */
.key{position:absolute;top:${short ? 35 : 39}mm;left:12mm;right:12mm;border-collapse:collapse;font-size:${short ? 3.05 : 3.25}mm}
.key th{font-family:Nu;font-weight:800;font-size:2.7mm;letter-spacing:.3mm;color:${PINE};text-align:left;padding:0 1.6mm 1.4mm;border-bottom:0.45mm solid ${PLUM}}
.key td{padding:0 1.6mm;height:${short ? 10.1 : 11}mm;border-bottom:0.25mm solid #cbc3cf;vertical-align:middle}
.key td.ord i,.key td.ok i{display:block;width:7mm;height:7mm;border:0.35mm solid ${PINE};border-radius:1.5mm}
.key td.ok i{border-radius:50%;width:5.5mm;height:5.5mm;margin:0 auto}
.key td.cd{white-space:nowrap}.key td.cd b{display:inline-block;width:4mm;font-weight:800;color:${BERRY}}
.key td.cd .ic{display:inline-block;vertical-align:middle;width:7mm;height:7mm}
.key td.sp{font-weight:800}.key td.fl{color:#5c4f63;font-style:italic}.key td.tp{color:${PINE}}
.key td.line{border-bottom:0.25mm solid #cbc3cf}
.key tr.tr td{background:#fbf6ea}
.warn{position:absolute;bottom:${short ? 12 : 14}mm;left:12mm;right:12mm;font-size:3.1mm;line-height:1.4;color:${PINE};text-align:center}
/* tracker */
.trk{position:absolute;top:${short ? 44 : 48}mm;left:12mm;right:12mm;bottom:${short ? 14 : 16}mm}
.trk svg.map{width:100%;height:100%}
.name{position:absolute;top:${short ? 35 : 38}mm;left:40mm;right:40mm;font-size:4.2mm;font-weight:800;display:flex;gap:2mm;align-items:flex-end}
.name i{flex:1;border-bottom:0.35mm solid ${PLUM};height:4mm}
`;
};

function lines(ls) { return ls.map((l, k) => (k === 4 ? '<div class=gap></div>' : '') + `<div class=ln>${l}</div>`).join(''); }

function clueCard(c) {
  return `<div class=card><div class=no>No.</div>${I(c.icon, 'art')}
   <div class=kick>WOODLAND CHRISTMAS HUNT</div><h3>Clue</h3>
   <div class=rhyme>${lines(c.lines)}</div>
   <div class=code>${c.code}</div>${I(13, 'sprig')}</div>`;
}
function treasureCard() {
  return `<div class="card treasure">${I(treasure.icon, 'art')}
   <div class=kick>YOU FOUND THE TREASURE</div><h3>Hooray!</h3>
   <div class=rhyme>${lines(treasure.lines)}</div>${I(8, 'sprig')}</div>`;
}
function blankCard(b) {
  return `<div class="card blank"><div class=no>No.</div>${I(b.icon, 'art')}
   <div class=kick>WOODLAND CHRISTMAS HUNT</div><h3>Clue</h3>
   <div class=rule>${'<i></i>'.repeat(7)}</div>
   <div class=code>${b.code}</div>${I(13, 'sprig')}</div>`;
}
const cardPage = cards => `<div class=page>${cards.map((c, k) => `<div class="slot s${k}">${c}</div>`).join('')}
  <div class=vcut></div><div class=hcut><span>✂</span></div></div>`;

function tracker() {
  // 15 stepping stones on a winding woodland path, START (fox) to TREASURE (gift). Units: mm.
  const VW = 192, VH = 200;
  const xs = [26, 61, 96, 131, 166], ys = [42, 98, 154];
  const pts = [];
  ys.forEach((y, r) => (r % 2 ? [...xs].reverse() : xs).forEach((x, k) => pts.push([x, y + (k % 2 ? 5 : -5)])));
  const start = [14, 10], end = [166, 190];
  let d = `M${start[0] + 12},${start[1] + 4} Q${pts[0][0]},${start[1]} ${pts[0][0]},${pts[0][1]}`;
  for (let k = 1; k < pts.length; k++) {
    const [a, b] = [pts[k - 1], pts[k]];
    if (Math.abs(a[1] - b[1]) > 30) { const bx = a[0] < 96 ? a[0] - 24 : a[0] + 24; d += ` C${bx},${a[1]} ${bx},${b[1]} ${b[0]},${b[1]}`; }
    else d += ` L${b[0]},${b[1]}`;
  }
  d += ` L${end[0]},${end[1] - 14}`;
  const deco = [[96, 14, 4, 11], [150, 12, 5, 12], [182, 70, 14, 11], [8, 125, 5, 12], [96, 126, 11, 10], [50, 186, 5, 13], [84, 184, 15, 10], [140, 68, 22, 9], [52, 70, 12, 9], [182, 128, 5, 12], [10, 182, 23, 11], [186, 22, 11, 8]];
  const use = (id, x, y, s) => `<svg x="${x - s / 2}" y="${y - s / 2}" width="${s}" height="${s}" viewBox="0 0 1000 1000"><use href="#i${id}"/></svg>`;
  return `<svg class=map viewBox="0 0 ${VW} ${VH}" preserveAspectRatio="xMidYMin meet">
   <path d="${d}" fill="none" stroke="${GOLD}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" opacity=".55"/>
   <path d="${d}" fill="none" stroke="${PLUM}" stroke-width=".5" stroke-dasharray="2 2"/>
   ${deco.map(([x, y, id, s]) => use(id, x, y, s)).join('')}
   ${use(0, start[0], start[1] + 2, 20)}<text x="${start[0]}" y="${start[1] + 17}" text-anchor="middle" font-family="Nu" font-weight="800" font-size="4" fill="${PINE}" letter-spacing=".6">START</text>
   ${pts.map(([x, y], k) => `<circle cx="${x}" cy="${y}" r="10.5" fill="#fff" stroke="${PLUM}" stroke-width=".7"/><circle cx="${x}" cy="${y}" r="9" fill="none" stroke="${PINE}" stroke-width=".25"/>
     <text x="${x}" y="${y + 3.3}" text-anchor="middle" font-family="Fr" font-weight="900" font-size="9.5" fill="${BERRY}">${k + 1}</text>`).join('')}
   ${use(21, end[0], end[1] - 3, 22)}<text x="${end[0] - 16}" y="${end[1] + 1}" text-anchor="end" font-family="Fr" font-weight="900" font-size="7" fill="${BERRY}">TREASURE!</text>
  </svg>`;
}

function pages(W, H, sizeName) {
  const short = H < 290;
  const out = [];
  const strip = [0, 4, 1, 21, 24, 13, 3, 28, 16, 7, 22].map(i => I(i)).join('');
  out.push(`<div class=page>
  <div class=head><div class=k>WOODLAND CHRISTMAS</div><h1>Scavenger <em>Hunt</em></h1><p>15 rhyming clues around the house · ages 3 to 10</p></div>
  <div class=strip style="top:${short ? 33 : 38}mm">${strip}</div>
  <div class=ins>
   <div><h2>What's inside</h2><ul>
    <li>Page 1: how to play (this page)</li>
    <li>Page 2: answer key and hunt planner (grown-ups only)</li>
    <li>Pages 3 to 6: 15 clue cards and a "Hooray!" treasure card, 4 per page</li>
    <li>Page 7: 4 blank cards to write your own clues</li>
    <li>Page 8: hunt tracker for the kids to colour in</li></ul>
    <h2 style="margin-top:3mm">How to play</h2><ol>
    <li>Hand the hunters clue No. 1 and read it out loud together.</li>
    <li>Guess the spot, hurry there and find the next clue.</li>
    <li>Colour a stepping stone on the tracker for every clue you find.</li>
    <li>The last clue leads to the treasure!</li></ol></div>
   <div><h2>Setting up (grown-ups)</h2><ol>
    <li>Print the clue pages and cut along the dashed lines.</li>
    <li>Choose the clues that fit your home. Skip any spot you don't have, or write your own on page 7.</li>
    <li>Put them in any order. Write 1, 2, 3 and so on in the "No." circle of each card and in the Order column of the answer key.</li>
    <li>Keep clue No. 1 to hand out. Hide every other clue at the spot the clue before it describes. Example: if No. 1 is the couch rhyme, hide No. 2 under a couch cushion.</li>
    <li>Hide the treasure (a small gift or treat) with the "Hooray!" card at the spot your last clue describes.</li></ol>
    <p>The small letter on each card matches the answer key, so the answers never show on the cards.</p></div>
   <div class="box wide"><h2>Good to know</h2><p>All 15 clues take about 20 to 30 minutes. For little ones (ages 3 to 5), use 5 or 6 clues and read them aloud. For older kids, add a timer, or print two sets and race in teams with different hiding spots. Keep it safe: the oven clue goes on the handle, never inside, and the bathtub must be empty and dry.</p></div>
   <div class=box><h2>Printing tips</h2><p>Print at 100% or "actual size" (not "fit to page") on ${sizeName} paper. Card stock (65 to 110 lb, 176 to 300 gsm) makes sturdy cards to reuse next year. White backgrounds are kind to your ink.</p></div>
   <div class=box><h2>Party ideas</h2><p>Make it a Christmas Eve tradition, a classroom party game or a way to hand over one special gift. Fill the treasure box with cocoa packets, candy canes, stickers or a new book.</p></div>
  </div>
  <div class=ground>${[[4],[5,1],[0],[14,1],[4],[10],[16],[13,1],[4],[28],[24,1],[4]].map(([i,s])=>I(i,s?'sm':'')).join('')}</div>
  <div class=foot>© ${SHOP} · For personal use: print as many copies as you like for your own family, party or classroom. Please don't share or resell the files.</div></div>`);

  const row = c => `<tr><td class=ord><i></i></td><td class=cd><b>${c.code}</b>${I(c.icon)}</td><td class=fl>${c.lines[0]} ${c.lines[1].replace(/[,;:.!]$/, '')}…</td><td class=sp>${c.spot}</td><td class=tp>${c.tip}</td><td class=ok><i></i></td></tr>`;
  out.push(`<div class=page><div class=head><div class=k>GROWN-UPS ONLY</div><h1>Answer <em>Key</em></h1><p>Fill in the order, hide each card, then tick it off</p></div>
  <table class=key><thead><tr><th style="width:11mm">ORDER</th><th style="width:15mm">CARD</th><th>CLUE BEGINS</th><th>ANSWER: THE SPOT</th><th>HIDING TIP</th><th style="width:12mm;text-align:center">HIDDEN</th></tr></thead><tbody>
  ${clues.map(row).join('')}
  ${BLANK.map(b => `<tr><td class=ord><i></i></td><td class=cd><b>${b.code}</b>${I(b.icon)}</td><td class=fl>Your own clue</td><td class=line></td><td class=line></td><td class=ok><i></i></td></tr>`).join('')}
  <tr class=tr><td class=ord></td><td class=cd><b>★</b>${I(treasure.icon)}</td><td class=fl>Hooray! card</td><td class=sp>The treasure</td><td class=tp>At the spot your last clue describes</td><td class=ok><i></i></td></tr>
  </tbody></table>
  <div class=warn>Hide this page from little hunters! Each clue describes a spot, and the NEXT card is hidden there.</div>
  <div class=foot>Woodland Christmas Scavenger Hunt · ${SHOP}</div></div>`);

  const all = [...clues.map(clueCard), treasureCard()];
  for (let i = 0; i < all.length; i += 4) out.push(cardPage(all.slice(i, i + 4)));
  out.push(cardPage(BLANK.map(blankCard)));
  out.push(`<div class=page><div class=head><div class=k>WOODLAND CHRISTMAS HUNT</div><h1>My Hunt <em>Tracker</em></h1><p>Colour a stepping stone every time you find a clue!</p></div>
  <div class=name>Hunter:<i></i></div>
  <div class=trk>${tracker()}</div>
  <div class=foot>Woodland Christmas Scavenger Hunt · ${SHOP}</div></div>`);
  return out;
}

const SIZES = { letter: [215.9, 279.4, 'US Letter'], a4: [210, 297, 'A4'] };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  fs.mkdirSync('bundle', { recursive: true });
  let bad = [];
  for (const [key, [W, H, name]] of Object.entries(SIZES)) {
    const html = `<!doctype html><html><head><meta charset=utf-8><style>${css(W, H)}</style></head><body>${defs}${pages(W, H, name).join('')}</body></html>`;
    await p.setContent(html, { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready);
    const issues = await p.evaluate(() => {
      const r = [];
      document.querySelectorAll('.ln').forEach(e => { if (e.scrollWidth > e.clientWidth + 1) r.push('rhyme line too wide: ' + e.textContent); });
      document.querySelectorAll('.card,.rhyme,.ins>div,.box').forEach(e => { if (e.scrollHeight > e.clientHeight + 1) r.push('overflow in ' + e.className + ': ' + e.textContent.slice(0, 40)); });
      document.querySelectorAll('.page').forEach((pg, n) => {
        const pb = pg.getBoundingClientRect();
        pg.querySelectorAll('.ins,.key,.trk,.warn,.slot').forEach(e => { const b = e.getBoundingClientRect(); if (b.bottom > pb.bottom - 9 * 3.78 + 1 && !e.classList.contains('slot')) r.push(`page ${n + 1}: ${e.className} reaches the bottom margin`); });
        const ins = pg.querySelector('.ins'); if (ins) { const last = [...ins.children].reduce((m, c) => Math.max(m, c.getBoundingClientRect().bottom), 0); if (last > ins.getBoundingClientRect().bottom + 1) r.push(`page ${n + 1}: instructions run past their area`); }
      });
      return r;
    });
    if (issues.length) bad.push(...issues.map(i => `${key}: ${i}`));
    const file = `bundle/woodland-christmas-scavenger-hunt-${key === 'a4' ? 'A4' : 'US-Letter'}.pdf`;
    await p.pdf({ path: file, width: `${W}mm`, height: `${H}mm`, printBackground: true, preferCSSPageSize: true });
    console.log(file);
  }
  await b.close();
  if (bad.length) { console.error('LAYOUT PROBLEMS:\n' + bad.join('\n')); process.exit(1); }
  console.log('layout OK: no overflow, no wrapped rhyme lines');
})();
