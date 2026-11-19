
// Render every distinct drawing alone on a transparent ground, so its pixels can be checked against the image edge.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 900, height: 700 }, deviceScaleFactor: 3 });
  const p = await ctx.newPage();
  await p.goto(require('url').pathToFileURL(spec.page).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  for (const id of spec.ids) await p.locator('#' + id).screenshot({ path: spec.dir + '/' + id + '.png', omitBackground: true });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
