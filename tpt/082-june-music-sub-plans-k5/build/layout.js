
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
      const BOX = '.part, .top, .name, .box, .bx, .cut, .doc table, table.t, .grid4, .meta, .steps li, .doc p, .doc ul';
      document.querySelectorAll('.page').forEach((pg, i) => {
        if (pg.classList.contains('cover')) return;
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        if (!ft) { res.push(`page ${i + 1}: no footer`); return; }
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
          if (r.height && (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5)) res.push(`page ${i + 1}: text "${el.textContent.trim().slice(0, 30)}" too close to the page edge`);
        });
        pg.querySelectorAll('.main *').forEach(el => {
          if (skip(el) || el.closest('svg') || el.tagName === 'tspan') return;
          const r = el.getBoundingClientRect();
          if (r.height > 0 && r.width > 0 && r.bottom > ftop - 8) res.push(`page ${i + 1}: element ${el.tagName}.${el.getAttribute('class') || ''} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
        });
        pg.querySelectorAll('.box, .cut, .bx, .part').forEach(bx => {
          if (bx.scrollWidth > bx.clientWidth + 1 || bx.scrollHeight > bx.clientHeight + 1) res.push(`page ${i + 1}: content overflows a ${bx.className} box`);
          const br = bx.getBoundingClientRect();
          bx.querySelectorAll('svg, img').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 3 || s.right > br.right - 3 || s.top < br.top + 3 || s.bottom > br.bottom - 3) res.push(`page ${i + 1}: a drawing is too close to its ${bx.className} box edge`);
          });
        });
        pg.querySelectorAll('.top .t').forEach(t => { if (t.getBoundingClientRect().right > pg.querySelector('.top .tag').getBoundingClientRect().left - 8) res.push(`page ${i + 1}: title crowds the tag`); });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (skip(el)) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && ((el.children.length === 0 && ((el.textContent || '').trim() || el.matches('svg, img'))) || el.matches('.part, .box, table, .cut, .ln2, .fl'))) maxb = Math.max(maxb, r.bottom); });
        if (!pg.classList.contains('doc') && !pg.querySelector('.keepblank') && ftop - maxb > 105) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer (over 10% of the page)`);
      });
      document.querySelectorAll('.sq').forEach((sq, i) => {
        const sr = sq.getBoundingClientRect();
        const bandEl = sq.querySelector('.band');
        const btop = bandEl.getBoundingClientRect().top;
        const full = el => el.matches('.cv-block, .cv-series, .band');
        sq.querySelectorAll('.shot, .card, .rib, .num, .lbl, .sub, .hd, .store, img').forEach(el => {
          if (full(el) || el.closest('.cv-block')) return;
          const r = el.getBoundingClientRect();
          const w = el.classList.contains('shot') || el.classList.contains('card') ? 8 : 0;
          if (r.left < sr.left + 24 || r.right + w > sr.right - 24) res.push(`square ${i + 1}: ${el.className || el.tagName} within 24px of a side edge`);
          if (r.top < sr.top + 16) res.push(`square ${i + 1}: ${el.className || el.tagName} within 16px of the top`);
          if (!el.closest('.cv-block') && el.className !== 'cv-series' && r.bottom + w > btop - 8 && !el.matches('.cv-block *')) res.push(`square ${i + 1}: ${el.className || el.tagName} within 8px of the band`);
        });
        sq.querySelectorAll('img').forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
        const els = [...sq.querySelectorAll('.store, .hd, .sub, .lbl, .shot, .card, .rib, .cv-hero')].filter(e => !e.closest('.cv-block'))
          .map(e => ({ e, r: e.getBoundingClientRect() }));
        for (let a = 0; a < els.length; a++) for (let c = a + 1; c < els.length; c++) {
          const A = els[a].r, B = els[c].r;
          const pad = 6;
          const ov = A.left < B.right + (els[c].e.matches('.shot, .card') ? 8 : 0) - 0 && B.left < A.right + (els[a].e.matches('.shot, .card') ? 8 : 0) && A.top < B.bottom && B.top < A.bottom;
          if (ov) {
            const allowed = (els[a].e.matches('.cv-mock') && els[c].e.matches('.cv-hero')) || (els[c].e.matches('.cv-mock') && els[a].e.matches('.cv-hero'));
            const inside = (els[a].e.matches('.lbl, .num') || els[c].e.matches('.lbl, .num')) && false;
            if (!allowed && !inside) res.push(`square ${i + 1}: ${els[a].e.className || els[a].e.tagName} overlaps ${els[c].e.className || els[c].e.tagName}`);
          }
        }
      });
      document.querySelectorAll('svg text.trace').forEach(t => {
        const sv = t.ownerSVGElement, vb = sv.viewBox.baseVal, bb = t.getBBox(), sw = parseFloat(t.getAttribute('stroke-width'));
        const l = bb.x - sw / 2, r = vb.width - (bb.x + bb.width + sw / 2);
        if (l < sw || r < sw) res.push(`trace word "${t.textContent}" ink padding ${Math.min(l, r).toFixed(1)} < stroke ${sw}`);
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
