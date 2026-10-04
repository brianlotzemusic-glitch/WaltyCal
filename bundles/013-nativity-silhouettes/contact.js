// Contact sheet for QA: every design big (black on white) and at thumbnail size.
// Run from this folder: NODE_PATH=$(npm root -g) node contact.js
const { chromium } = require('playwright'); const fs = require('fs');
const dir = 'bundle/SVG';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort();
const svg = f => fs.readFileSync(`${dir}/${f}`, 'utf8').replace(/width="[^"]*" height="[^"]*"/, 'width="100%" height="100%"');
const html = `<style>body{margin:0;width:2400px;background:#fff;font-family:Georgia,'DejaVu Serif',serif;color:#1d2540}
h1{margin:30px 40px 10px;font-size:44px;font-weight:normal} p{margin:0 40px 20px;font-size:24px}
.g{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;padding:0 40px 40px}
.c{border:2px solid #ddd;border-radius:14px;padding:16px;display:flex;align-items:flex-end;gap:18px;flex-wrap:wrap}
.big{width:600px;height:600px}.small{width:90px;height:90px}.n{width:100%;font-size:26px}</style>
<h1>Nativity Silhouettes: 6 designs</h1><p>Big = 600 px; small = 90 px (about a search-grid thumbnail)</p>
<div class=g>${files.map(f => `<div class=c><div class=big>${svg(f)}</div><div class=small>${svg(f)}</div><div class=n>${f.replace('.svg', '')}</div></div>`).join('')}</div>`;
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2400, height: 1000 } });
  await p.setContent(html); await p.screenshot({ path: 'contact-sheet.png', fullPage: true }); await b.close(); })();
