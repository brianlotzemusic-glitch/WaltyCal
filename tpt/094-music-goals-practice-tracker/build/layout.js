
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
      const BOX = '.wbox, .fb, .gk, .tile, .box, .top, .doc table, .doc p, .doc ul, .doc ol, .fbox, .draw, .ticket, .tempo, .chips, .scale, .cell, .tb, .bnote, .leg, .certf, .gsv, .pbar';
      const FILL = '.wbox, .fb, .gk, .tile, .box, .fbox, .draw, .ticket, .tempo, table, .wl, .chips, .scale, .fam, .cell, .tb, .bnote, .leg, .certf, .gsv, .pbar, .lgrid, .trow';
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        if (!ft) return;
        const ftop = ft.getBoundingClientRect().top;
        const skip = el => ft.contains(el) || el.closest('.wm');
        pg.querySelectorAll(BOX + ', svg, img').forEach(el => {
          if (skip(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} too close to the page edge`);
        });
        pg.querySelectorAll('*').forEach(el => {
          if (skip(el) || el.children.length || !(el.textContent || '').trim() || el.closest('svg')) return;
          const r = el.getBoundingClientRect();
          if (r.height && r.bottom > ftop - 8) res.push(`page ${i + 1}: text "${el.textContent.trim().slice(0, 30)}" ends ${(r.bottom - ftop).toFixed(1)}px from the footer rule`);
        });
        pg.querySelectorAll('.wbox, .fb, .gk, .tile, .box, .ticket, .tempo, .fbox, .cell, .bnote, .certf, .tb').forEach(bx => {
          if (bx.scrollWidth > bx.clientWidth + 1 || bx.scrollHeight > bx.clientHeight + 1) res.push(`page ${i + 1}: content overflows a ${bx.className} box`);
          const br = bx.getBoundingClientRect();
          bx.querySelectorAll(':scope > *').forEach(ch => { const r = ch.getBoundingClientRect(); if (r.height && r.bottom > br.bottom + 0.5) res.push(`page ${i + 1}: a child spills out of a ${bx.className} box`); });
        });
        pg.querySelectorAll('.tile').forEach(c => {
          const cr = c.getBoundingClientRect();
          c.querySelectorAll('.tt, svg').forEach(e => { const r = e.getBoundingClientRect(); if (r.bottom > cr.bottom - 4 || r.right > cr.right - 4) res.push(`page ${i + 1}: stamp content too close to the cut line`); });
        });
        pg.querySelectorAll('.gk').forEach(g => { const s = g.querySelector('svg').getBoundingClientRect(), gr = g.getBoundingClientRect(); if (s.top < gr.top + 6 || s.bottom > gr.bottom - 6) res.push(`page ${i + 1}: glyph too close to its box edge`); });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (skip(el)) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && ((el.children.length === 0 && ((el.textContent || '').trim() || el.matches('svg, img'))) || el.matches(FILL))) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 105) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer (over 10% of the page)`);
        const ys = [];
        pg.querySelectorAll('.rb > *, .lgrid > *, .doc > table, .doc > h2, .doc > p, .doc > ul, .doc > ol, .doc > .cols, .sg').forEach(e => { const r = e.getBoundingClientRect(); if (r.height) ys.push([r.top, r.bottom]); });
        ys.sort((a, c) => a[0] - c[0]);
        for (let k = 1; k < ys.length; k++) if (ys[k][0] - ys[k - 1][1] > 105) res.push(`page ${i + 1}: blank band of ${(ys[k][0] - ys[k - 1][1]).toFixed(0)}px between blocks`);
      });
      document.querySelectorAll('.sq').forEach((sq, i) => {
        const sr = sq.getBoundingClientRect();
        const band = sq.querySelector('.band');
        const btop = band.getBoundingClientRect().top;
        const shots = [];
        sq.querySelectorAll('.shot').forEach(sh => {
          const r = sh.getBoundingClientRect();
          shots.push(r);
          if (r.left < sr.left + 24 || r.right + 8 > sr.right - 24) res.push(`square ${i + 1}: a page shot is too close to the side edge`);
          if (r.bottom + 8 > btop - 8) res.push(`square ${i + 1}: a page shot shadow is within 8px of the band`);
        });
        for (let a = 0; a < shots.length; a++) for (let c = a + 1; c < shots.length; c++) if (shots[a].right + 8 + 8 > shots[c].left && shots[a].left < shots[c].left && shots[a].bottom > shots[c].top) res.push(`square ${i + 1}: page shots lack a gutter`);
        sq.querySelectorAll('.lbl, .lbl span, .pill, .sub, .hd, .tg, .gtl').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.bottom > btop - 8) res.push(`square ${i + 1}: ${el.className} "${el.textContent.trim().slice(0, 24)}" within 8px of the band`);
          if (r.left < sr.left + 24 || r.right > sr.right - 24) res.push(`square ${i + 1}: text "${el.textContent.trim().slice(0, 24)}" too close to the side edge`);
        });
        sq.querySelectorAll('.tc').forEach(el => { if (el.scrollWidth > el.clientWidth + 1) res.push(`square ${i + 1}: a chip overflows`); });
        sq.querySelectorAll('img').forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
        sq.querySelectorAll('svg').forEach(sv => { const r = sv.getBoundingClientRect(); if (r.left < sr.left + 24 || r.right > sr.right - 24) res.push(`square ${i + 1}: a glyph is too close to the side edge`); });
      });
      document.querySelectorAll('.cover').forEach(pg => {
        const pr = pg.getBoundingClientRect();
        pg.querySelectorAll('.ctitle .b, .cband, .ctitle .c, img').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.left < pr.left + 0.45 * 96 || r.right > pr.right - 0.45 * 96) res.push(`cover: ${el.className || el.tagName} too close to the side edge`);
        });
        const kids = [...pg.children].map(c => c.getBoundingClientRect());
        for (let a = 0; a < kids.length - 1; a++) if (kids[a].bottom + 8 > kids[a + 1].top) res.push('cover: blocks lack a gutter');
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
