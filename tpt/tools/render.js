// Render HTML pages to PDF or PNG with Playwright + Chromium (fonts are embedded as subsets).
// Usage: NODE_PATH=$(npm root -g) node render.js jobs.json
// jobs.json: [{"html": "/abs/page.html", "pdf": "/abs/out.pdf"}
//             | {"html": "...", "png": "/abs/out.png", "width": 1000, "height": 1000, "scale": 2}]
const { chromium } = require('playwright');
const fs = require('fs'), url = require('url');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  for (const j of jobs) {
    const ctx = await browser.newContext(j.png ? { viewport: { width: j.width, height: j.height }, deviceScaleFactor: j.scale || 1 } : {});
    const page = await ctx.newPage();
    await page.goto(url.pathToFileURL(j.html).href, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const missing = await page.evaluate(() => [...document.fonts].filter(f => f.status !== 'loaded' && f.status !== 'unloaded').map(f => f.family));
    if (missing.length) throw new Error('fonts failed: ' + missing.join(', '));
    if (j.pdf) await page.pdf({ path: j.pdf, preferCSSPageSize: true, printBackground: true });
    else await page.screenshot({ path: j.png, clip: { x: 0, y: 0, width: j.width, height: j.height } });
    await ctx.close();
    console.log('wrote', j.pdf || j.png);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
