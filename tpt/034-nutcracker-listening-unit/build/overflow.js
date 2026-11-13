
const { chromium } = require('playwright'); const url = require('url');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const r = await p.evaluate(() => [...document.querySelectorAll('.page')].map((pg, i) => {
    const box = pg.getBoundingClientRect(); const foot = pg.querySelector('.foot'); const fy = foot ? foot.getBoundingClientRect().top : box.bottom;
    const bad = [];
    pg.querySelectorAll('.main *').forEach(e => { const q = e.getBoundingClientRect();
      if (q.width && q.height && (q.bottom > fy + 0.5 || q.right > box.right - 0.4 * 96 + 0.5 || q.left < box.left + 0.4 * 96 - 0.5)) bad.push(e.tagName + ':' + (e.textContent || '').slice(0, 30)); });
    pg.querySelectorAll('*').forEach(e => { if (e.scrollWidth > e.clientWidth + 2 && getComputedStyle(e).overflow !== 'visible') bad.push('clip:' + e.tagName); });
    return [i + 1, bad.slice(0, 3)]; }));
  console.log(JSON.stringify(r)); await b.close();
})();
