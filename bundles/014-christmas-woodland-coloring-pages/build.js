// Buyer PDFs from art/svg: 20 coloring pages, one per page, no text.
// Run from this folder: NODE_PATH=$(npm root -g) node build.js
//   bundle/christmas-woodland-coloring-pages-US-Letter.pdf  20 pages, 8.5 x 11 in
//   bundle/christmas-woodland-coloring-pages-A4.pdf         20 pages, 210 x 297 mm
// The art box is the same physical size on both papers (182 x 234 mm), so line weights match;
// it sits centred, at least 17 mm from every edge on Letter and 14 mm on A4 (home printers clip ~6 mm).
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const S = JSON.parse(fs.readFileSync('subjects.json', 'utf8')).pages;
const ART_W = 182, ART_H = 182 * 1152 / 896;
const SIZES = { 'US-Letter': [215.9, 279.4, 'Letter'], 'A4': [210, 297, 'A4'] };
(async () => {
  fs.mkdirSync('bundle', { recursive: true });
  const b = await chromium.launch(); const p = await b.newPage();
  for (const [name, [W, H, FMT]] of Object.entries(SIZES)) {
    const pages = S.map(([slug]) => {
      const svg = fs.readFileSync(path.join('art', 'svg', slug + '.svg'), 'utf8')
        .replace('<svg ', `<svg width="${ART_W}mm" height="${ART_H.toFixed(2)}mm" `);
      return `<div class=page>${svg}</div>`;
    }).join('');
    const html = `<!doctype html><meta charset=utf-8><title>Christmas Woodland Coloring Pages</title><style>
      @page{size:${W}mm ${H}mm;margin:0}*{box-sizing:border-box}body{margin:0}
      .page{width:${W}mm;height:${H - 0.3}mm;display:flex;align-items:center;justify-content:center;page-break-after:always;overflow:hidden;background:#fff}
      .page svg{display:block}</style>${pages}`;
    await p.setContent(html, { waitUntil: 'load' });
    await p.pdf({ path: `bundle/christmas-woodland-coloring-pages-${name}.pdf`, format: FMT, printBackground: true, preferCSSPageSize: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 } });
    console.log('built', name);
  }
  await b.close();
})();
