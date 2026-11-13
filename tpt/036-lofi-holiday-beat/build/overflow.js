
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.emulateMedia({ media: 'print' });
  const res = await page.evaluate(() => [...document.querySelectorAll('section.page')].map((s, i) => {
    const m = s.querySelector('.main');
    const out = { page: i + 1, key: s.dataset.key, main_over: m ? Math.max(0, m.scrollHeight - m.clientHeight) : 0, cells: [], clipped: [] };
    if (m) {
      const mb = m.getBoundingClientRect();
      m.querySelectorAll('*').forEach(el => {
        if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') return;
        const r = el.getBoundingClientRect();
        if (r.width && (r.right > mb.right + 1 || r.bottom > mb.bottom + 1 || r.left < mb.left - 1))
          out.cells.push((el.tagName + ': ' + (el.textContent || '').trim()).slice(0, 50));
        if (el.children.length === 0 && el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).overflow !== 'visible')
          out.clipped.push((el.tagName + ': ' + (el.textContent || '').trim()).slice(0, 50));
      });
      let maxb = mb.top;
      m.querySelectorAll('*').forEach(el => { const r = el.getBoundingClientRect(); if (r.height && !el.classList.contains('lines')) maxb = Math.max(maxb, r.bottom); });
      out.free = Math.round(mb.bottom - maxb);
      if (m.querySelector('.lines')) out.free = 0;
    }
    return out;
  }));
  require('fs').writeFileSync(process.argv[3], JSON.stringify(res, null, 1));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
