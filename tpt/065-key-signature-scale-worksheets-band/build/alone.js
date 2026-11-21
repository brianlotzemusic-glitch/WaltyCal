
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 900, height: 600 }, deviceScaleFactor: 4 });
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const hs = await p.$$('svg');
  let n = 0;
  for (const h of hs) { await h.screenshot({ path: process.argv[3] + '/a' + String(n++).padStart(4, '0') + '.png', omitBackground: true }); }
  await b.close();
  console.log(n);
})().catch(e => { console.error(e); process.exit(1); });
