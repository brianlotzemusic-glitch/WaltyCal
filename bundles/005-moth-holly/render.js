const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = process.argv[2], size = +(process.argv[3]||800), outdir = process.argv[4]||dir;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: size, height: size } });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8').replace(/width="[^"]*" height="[^"]*"/, 'width="100%" height="100%"');
    await p.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await p.screenshot({ path: path.join(outdir, f.replace('.svg', '.png')), omitBackground: true });
  }
  await b.close();
})();
