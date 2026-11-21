
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  // each scene rendered with only its hidden symbols and rings on a transparent ground, at 2x: report the ink box in scene units
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 760, height: 500 }, deviceScaleFactor: 2 });
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const hs = await p.$$('svg.scene');
  let n = 0;
  for (const h of hs) {
    await h.evaluate(sv => { sv.querySelectorAll('g[clip-path], .frame').forEach(e => e.style.display = 'none'); sv.setAttribute('width', '720'); sv.setAttribute('height', '450'); document.body.style.background = 'transparent'; });
    await h.screenshot({ path: process.argv[3] + '/s' + String(n++).padStart(2, '0') + '.png', omitBackground: true });
  }
  await b.close();
  console.log(n);
})().catch(e => { console.error(e); process.exit(1); });
