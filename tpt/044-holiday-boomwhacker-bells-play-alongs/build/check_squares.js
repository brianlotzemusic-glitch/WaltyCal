
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const browser = await chromium.launch();
  const out = {};
  for (const name of process.argv.slice(2)) {
    const page = await browser.newPage({ viewport: { width: 1000, height: 1000 } });
    await page.goto(url.pathToFileURL(require('path').join(process.env.BUILD_DIR, name + '.html')).href);
    await page.evaluate(() => document.fonts.ready);
    out[name] = await page.evaluate(() => {
      const band = document.querySelector('.band').getBoundingClientRect();
      const bad = [];
      for (const el of document.querySelectorAll('.sq *')) {
        if (el.closest('.band')) continue;
        if (el.tagName === 'DIV' && el.children.length > 0 && !el.classList.contains('shot') && !el.classList.contains('card')) continue;
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        if (r.bottom > band.top + 0.5) bad.push(el.tagName + '.' + el.className + ' bottom=' + r.bottom.toFixed(0) + ' band=' + band.top.toFixed(0));
        if (r.right > 1001 || r.left < -1) bad.push('outside ' + el.tagName + ' ' + r.left.toFixed(0) + ',' + r.right.toFixed(0));
      }
      return { bad: bad.slice(0, 5), wm: document.querySelectorAll('.swm, .wm').length };
    });
    await page.close();
  }
  console.log(JSON.stringify(out));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
