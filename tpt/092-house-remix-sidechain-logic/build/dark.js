
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.emulateMedia({ media: 'print' });
  const res = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('section.page').forEach((s, i) => {
      s.querySelectorAll('*').forEach(el => {
        const cs = getComputedStyle(el);
        const m = cs.backgroundColor.match(/rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?\)/);
        if (!m || (m[4] !== undefined && parseFloat(m[4]) < 0.5)) return;
        if (['TH', 'TD', 'TR', 'TABLE'].includes(el.tagName) || /\blv\b/.test(el.className)) return;
        if (+m[1] > 60 || +m[2] > 60 || +m[3] > 60) return;
        const r = el.getBoundingClientRect();
        if (r.height < 20 || r.width < 60) return;
        let low = -1e9;
        const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        let n;
        while ((n = w.nextNode())) {
          if (!n.textContent.trim()) continue;
          const rg = document.createRange(); rg.selectNodeContents(n);
          Array.from(rg.getClientRects()).forEach(q => { if (q.bottom > low) low = q.bottom; });
        }
        if (low > -1e8) out.push({ page: i + 1, key: s.dataset.key, gap: r.bottom - low, cls: el.className });
      });
    });
    return out;
  });
  require('fs').writeFileSync(process.argv[3], JSON.stringify(res));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
