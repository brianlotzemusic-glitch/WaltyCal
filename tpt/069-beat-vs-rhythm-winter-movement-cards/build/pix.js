
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  // every pictogram and every notation drawing alone on a transparent ground at 4x: the page lists one svg per entry
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 700, height: 500 }, deviceScaleFactor: 4 });
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const hs = await p.$$('svg');
  let n = 0;
  for (const h of hs) await h.screenshot({ path: process.argv[3] + '/s' + String(n++).padStart(3, '0') + '.png', omitBackground: true });
  await b.close();
  console.log(n);
})().catch(e => { console.error(e); process.exit(1); });
