// Contact sheet of all icons + all stickers for QA: NODE_PATH=$(npm root -g) node contact.js
const { chromium } = require('playwright'); const fs = require('fs');
const { icons } = JSON.parse(fs.readFileSync('icons.json', 'utf8'));
const st = fs.existsSync('stickers.json') ? JSON.parse(fs.readFileSync('stickers.json', 'utf8')) : null;
const F = f => `data:font/ttf;base64,${fs.readFileSync('fonts/' + f).toString('base64')}`;
const cell = (svg, name) => `<div class=c><div class=big><svg viewBox="0 0 1000 1000">${svg}</svg></div>
  <div class=small><svg viewBox="0 0 1000 1000">${svg}</svg></div><div class=n>${name}</div></div>`;
const html = `<style>@font-face{font-family:N;src:url(${F('Nunito-700.ttf')})}@font-face{font-family:Fr;font-weight:700;src:url(${F('Fraunces-700.ttf')})}
body{margin:0;width:2400px;background:#fff;font-family:N;color:#2c1b36}
h1{margin:30px 40px 10px;font-size:44px} p{margin:0 40px 20px;font-size:24px}
.g{display:grid;grid-template-columns:repeat(6,1fr);gap:18px;padding:0 40px 40px}
.c{border:2px solid #ddd;border-radius:14px;padding:12px;display:flex;align-items:flex-end;gap:14px;flex-wrap:wrap}
.big svg{width:250px;height:250px}.small svg{width:48px;height:48px}.n{width:100%;font-size:26px}
.s{display:grid;grid-template-columns:repeat(10,1fr);gap:16px;padding:0 40px 40px;background:#cfc6d4;padding-top:20px}
.s svg{width:100%;display:block}</style>
<h1>Small Autumn Moments: ${icons.length} icons</h1><p>Big = 250 px; small = 48 px (0.5 in at 96 DPI, about the size of the page decorations)</p>
<div class=g>${icons.map(i => cell(i.svg, `${i.id + 1}. ${i.name}${i.phrase ? ' · "' + i.phrase + '"' : ''}`)).join('')}</div>
${st ? `<h1>${st.stickers.length} stickers (on grey, to show the white offset border)</h1><div class=s>${st.stickers.map(s => s.svg).join('')}</div>` : ''}`;
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2400, height: 1000 } });
  await p.setContent(html); await p.evaluate(() => document.fonts.ready); await p.screenshot({ path: 'contact-sheet.png', fullPage: true }); await b.close(); })();
