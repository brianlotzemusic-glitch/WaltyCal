// Contact sheet for QA: NODE_PATH=$(npm root -g) node contact.js
// Every icon used in the hunt (15 clue cards, the treasure card, 4 blank cards) at 250 px,
// at its printed card size (US Letter: 33 mm = 125 px at 96 DPI) and at its answer-key size (7 mm = 26 px).
const { chromium } = require('playwright'); const fs = require('fs');
const { icons } = JSON.parse(fs.readFileSync('icons.json', 'utf8'));
const { clues, treasure } = JSON.parse(fs.readFileSync('clues.json', 'utf8'));
const used = [...clues.map(c => [c.icon, `${c.code}. ${c.spot}`]), [treasure.icon, 'Hooray! (treasure)'],
  [13, 'P. blank card'], [14, 'Q. blank card'], [8, 'R. blank card'], [6, 'S. blank card']];
const sv = (svg, px) => `<svg viewBox="0 0 1000 1000" style="width:${px}px;height:${px}px">${svg}</svg>`;
const cell = ([id, label]) => `<div class=c>${sv(icons[id].svg, 250)}${sv(icons[id].svg, 125)}${sv(icons[id].svg, 26)}<div class=n>${label} <i>(${icons[id].name})</i></div></div>`;
const html = `<style>@font-face{font-family:N;src:url(data:font/ttf;base64,${fs.readFileSync('fonts/Nunito-700.ttf').toString('base64')})}
body{margin:0;width:2400px;background:#fff;font-family:N;color:#2c1b36}
h1{margin:30px 40px 10px;font-size:44px} p{margin:0 40px 20px;font-size:24px}
.g{display:grid;grid-template-columns:repeat(5,1fr);gap:18px;padding:0 40px 40px}
.c{border:2px solid #ddd;border-radius:14px;padding:12px;display:flex;align-items:flex-end;gap:14px;flex-wrap:wrap}
.n{width:100%;font-size:24px}.n i{color:#7d7183}</style>
<h1>Woodland Christmas Scavenger Hunt: card icons (reused from the approved 010 bingo set)</h1>
<p>Each: 250 px; 125 px (33 mm, the printed size on a US Letter clue card); 26 px (7 mm, answer key)</p>
<div class=g>${used.map(cell).join('')}</div>`;
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2400, height: 1000 } });
  await p.setContent(html); await p.screenshot({ path: 'contact-sheet.png', fullPage: true }); await b.close(); })();
