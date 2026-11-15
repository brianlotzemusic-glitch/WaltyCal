
const { chromium } = require('playwright'); const url = require('url');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const res = await p.evaluate(() => [...document.querySelectorAll('section.page')].map((s, i) => {
    const r = s.getBoundingClientRect(); let worst = 0, wide = 0, clear = 1e9;
    const ft = s.querySelector('.foot'); const fy = ft ? ft.getBoundingClientRect().top : null;
    for (const c of s.querySelectorAll('*')) {
      if (c.closest('.wm') || c.closest('.foot') || c.closest('.cvr') || (c.getAttribute('style')||'').startsWith('flex:1')) continue;
      const q = c.getBoundingClientRect(); if (q.width === 0 && q.height === 0) continue;
      worst = Math.max(worst, q.bottom - r.bottom); wide = Math.max(wide, q.right - r.right, r.left - q.left);
      if (fy !== null && c.children.length === 0 && c.textContent.trim().length + 0 >= 0 && q.height > 0) clear = Math.min(clear, fy - q.bottom);
    }
    const tbls = [...s.querySelectorAll('table')].map(t => { const w = t.getBoundingClientRect(); return [w.left - r.left, r.right - w.right]; });
    return [i + 1, worst, wide, clear, fy === null ? -1 : 0];
  }));
  console.log(JSON.stringify(res)); await b.close();
})();
