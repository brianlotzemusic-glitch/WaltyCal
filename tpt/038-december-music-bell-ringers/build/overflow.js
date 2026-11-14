
const { chromium } = require('playwright'); const url = require('url');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const res = await p.evaluate(() => [...document.querySelectorAll('section.page')].map((s, i) => {
    const r = s.getBoundingClientRect(); let worst = 0, wide = 0;
    for (const c of s.querySelectorAll('*')) {
      if (c.closest('.wm') || c.closest('.dots')) continue;
      const q = c.getBoundingClientRect(); if (q.width === 0 && q.height === 0) continue;
      worst = Math.max(worst, q.bottom - r.bottom); wide = Math.max(wide, q.right - r.right, r.left - q.left);
    }
    return [i + 1, worst, wide];
  }));
  console.log(JSON.stringify(res)); await b.close();
})();
