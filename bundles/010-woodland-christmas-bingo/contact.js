// Contact sheet of all icons for QA: NODE_PATH=$(npm root -g) node contact.js
const { chromium } = require('playwright'); const fs = require('fs');
const { icons, free } = JSON.parse(fs.readFileSync('icons.json', 'utf8'));
const cell = (svg, name) => `<div class=c><div class=big><svg viewBox="0 0 1000 1000">${svg}</svg></div>
  <div class=small><svg viewBox="0 0 1000 1000">${svg}</svg></div><div class=n>${name}</div></div>`;
const html = `<style>@font-face{font-family:N;src:url(data:font/ttf;base64,${fs.readFileSync('fonts/Nunito-700.ttf').toString('base64')})}
body{margin:0;width:2400px;background:#fff;font-family:N;color:#2c1b36}
h1{margin:30px 40px 10px;font-size:44px} p{margin:0 40px 20px;font-size:24px}
.g{display:grid;grid-template-columns:repeat(6,1fr);gap:18px;padding:0 40px 40px}
.c{border:2px solid #ddd;border-radius:14px;padding:12px;display:flex;align-items:flex-end;gap:14px;flex-wrap:wrap}
.big svg{width:250px;height:250px}.small svg{width:77px;height:77px}.n{width:100%;font-size:26px}</style>
<h1>Woodland Christmas Bingo: ${icons.length} icons + free space</h1><p>Big = 250 px; small = 77 px (0.8 in at 96 DPI, the icon size on a printed card)</p>
<div class=g>${icons.map(i => cell(i.svg, `${i.id + 1}. ${i.name}`)).join('')}${cell(free, 'FREE space')}</div>`;
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2400, height: 1000 } });
  await p.setContent(html); await p.screenshot({ path: 'contact-sheet.png', fullPage: true }); await b.close(); })();
