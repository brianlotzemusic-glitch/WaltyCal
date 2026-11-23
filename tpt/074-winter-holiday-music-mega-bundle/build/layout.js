
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = [];
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 1000, height: 1056 }, deviceScaleFactor: 1 });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const res = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        if (!ft) { res.push(`page ${i + 1}: no footer`); return; }
        const ftop = ft.getBoundingClientRect().top;
        const skip = el => ft.contains(el) || el.closest('.wm');
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => {
          if (skip(el)) return;
          const r = el.getBoundingClientRect();
          if (!r.height || !r.width) return;
          if (!el.matches('.main') && r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${el.className} too close to the page edge`);
          if (el.matches('table, .box, p, ul, ol, .hero3')) maxb = Math.max(maxb, r.bottom);
        });
        if (!pg.classList.contains('terms') && ftop - maxb > 230) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer`);
        pg.querySelectorAll('td, th').forEach(td => { if (td.scrollWidth > td.clientWidth + 1) res.push(`page ${i + 1}: a table cell overflows`); });
      });
      document.querySelectorAll('.sq').forEach((sq, i) => {
        const sr = sq.getBoundingClientRect();
        const btop = sq.querySelector('.band').getBoundingClientRect().top;
        sq.querySelectorAll('.shot, .tile, .cnt, .row, .lbl, .sub, .hd, .store').forEach(el => {
          if (el.closest('.cv-block')) return;
          const r = el.getBoundingClientRect();
          const w = el.classList.contains('shot') ? 8 : 0;
          if (r.left < sr.left + 24 || r.right + w > sr.right - 24) res.push(`square ${i + 1}: ${el.className} within 24px of a side edge`);
          if (r.top < sr.top + 16) res.push(`square ${i + 1}: ${el.className} within 16px of the top`);
          if (r.bottom + w > btop - 8 && !el.matches('.cv-block *')) res.push(`square ${i + 1}: ${el.className} within 8px of the band`);
        });
        sq.querySelectorAll('.row .t').forEach(t => { if (t.scrollWidth > t.clientWidth + 1) res.push(`square ${i + 1}: row title clipped: ${t.textContent}`); });
        sq.querySelectorAll('.cnt > div').forEach(t => { const g = document.createRange(); g.selectNodeContents(t); if (g.getBoundingClientRect().width > t.parentElement.clientWidth - 12) res.push(`square ${i + 1}: count card text too wide`); });
        sq.querySelectorAll('img').forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
        const els = [...sq.querySelectorAll('.store, .hd, .sub, .lbl, .shot, .tile, .cnt, .row')].filter(e => !e.closest('.cv-block')).map(e => ({ e, r: e.getBoundingClientRect() }));
        for (let a = 0; a < els.length; a++) for (let c = a + 1; c < els.length; c++) {
          const A = els[a].r, B = els[c].r;
          const sa = els[a].e.matches('.shot') ? 8 : 0, sb = els[c].e.matches('.shot') ? 8 : 0;
          if (A.left < B.right + sb && B.left < A.right + sa && A.top < B.bottom + sb && B.top < A.bottom + sa) res.push(`square ${i + 1}: ${els[a].e.className} overlaps ${els[c].e.className}`);
        }
        const blk = sq.querySelector('.cv-block');
        if (blk) {
          blk.querySelectorAll('.hd').forEach(h => { if ((() => { const g = document.createRange(); g.selectNodeContents(h); const q = g.getBoundingClientRect(); return q.right > sr.right - 24 || q.left < sr.left + 24; })()) res.push('cover title line too wide for the block'); });
        }
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
