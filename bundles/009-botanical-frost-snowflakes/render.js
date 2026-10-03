// PNG export: node render.js <svg dir> <long side px> <out dir>. Keeps each SVG's aspect ratio.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = process.argv[2], size = +(process.argv[3]||800), outdir = process.argv[4]||dir;
  const b = await chromium.launch();
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
    let svg = fs.readFileSync(path.join(dir, f), 'utf8');
    const [, , w, h] = svg.match(/viewBox="([^"]*)"/)[1].split(/\s+/).map(Number);
    const W = w >= h ? size : Math.round(size * w / h), H = h >= w ? size : Math.round(size * h / w);
    svg = svg.replace(/width="[^"]*" height="[^"]*"/, 'width="100%" height="100%"');
    const p = await b.newPage({ viewport: { width: W, height: H } });
    await p.setContent(`<html><body style="margin:0;background:transparent;overflow:hidden"><div style="width:${W}px;height:${H}px">${svg}</div></body></html>`);
    await p.screenshot({ path: path.join(outdir, f.replace('.svg', '.png')), omitBackground: true });
    await p.close();
  }
  await b.close();
})();
