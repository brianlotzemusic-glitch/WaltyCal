
const { chromium } = require('playwright'); const url = require('url');
(async () => { const b = await chromium.launch(); const out = {};
  for (const f of process.argv.slice(2)) { const p = await b.newPage({ viewport: { width: 1000, height: 1000 } });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready);
    out[f] = await p.evaluate(() => { const band = document.querySelector('.band').getBoundingClientRect().top; let low = 0;
      for (const e of document.querySelectorAll('.sq *')) { if (e.closest('.band') || e.classList.contains('swm')) continue;
        const r = e.getBoundingClientRect(); if (r.width && r.height) low = Math.max(low, r.bottom); }
      const wide = [...document.querySelectorAll('.sq *')].some(e => { const r = e.getBoundingClientRect(); return r.right > 1000.5 || r.left < -0.5; });
      return { band, low, wide }; });
    await p.close(); }
  await b.close(); console.log(JSON.stringify(out)); })();
