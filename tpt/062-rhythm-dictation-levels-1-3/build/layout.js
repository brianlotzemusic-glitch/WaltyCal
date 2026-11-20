
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
      const BOX = '.sc, .sp, .kb, .box, .step, .exbox, .top, .nd, .doc table, .trk, .cols, .stp, .doc p, .doc ul';
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        if (!ft) return;
        const ftop = ft.getBoundingClientRect().top;
        const skip = el => ft.contains(el) || el.closest('.wm');
        const boxes = [];
        pg.querySelectorAll(BOX + ', svg, img').forEach(el => {
          if (skip(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} too close to the page edge`);
          if (el.matches('.sc, .sp, .kb, .box, .step, .exbox')) boxes.push([el, r]);
        });
        pg.querySelectorAll('*').forEach(el => {
          if (skip(el) || el.children.length || !(el.textContent || '').trim()) return;
          if (el.closest('svg')) return;
          const r = el.getBoundingClientRect();
          if (r.height && r.bottom > ftop - 8) res.push(`page ${i + 1}: text "${el.textContent.trim().slice(0, 30)}" ends ${(r.bottom - ftop).toFixed(1)}px from the footer rule`);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 8 && gy < 8) res.push(`page ${i + 1}: two boxes lack a gutter of 8px`);
        }
        pg.querySelectorAll('.sc, .sp, .kb, .box, .step, .exbox').forEach(bx => {
          if (bx.scrollWidth > bx.clientWidth + 1 || bx.scrollHeight > bx.clientHeight + 1) res.push(`page ${i + 1}: content overflows a ${bx.className} box`);
          const br = bx.getBoundingClientRect();
          bx.querySelectorAll('svg').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 4 || s.right > br.right - 4 || s.top < br.top + 2 || s.bottom > br.bottom - 2) res.push(`page ${i + 1}: a drawing is too close to its box edge`);
          });
        });
        pg.querySelectorAll('.syt td').forEach(td => {
          const br = td.getBoundingClientRect();
          td.querySelectorAll('svg').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 2 || s.right > br.right - 2 || s.top < br.top + 1 || s.bottom > br.bottom - 1) res.push(`page ${i + 1}: a chart drawing is too close to its cell edge`);
          });
        });
        pg.querySelectorAll('.sylbar, .cntbar').forEach(el => {
          const lh = parseFloat(getComputedStyle(el).lineHeight);
          if (el.getBoundingClientRect().height > lh * 1.4) res.push(`page ${i + 1}: script line wraps: "${el.textContent.slice(0, 30)}"`);
        });
        pg.querySelectorAll('svg.ns').forEach(sv => {
          const vb = sv.viewBox.baseVal;
          const texts = [...sv.querySelectorAll('text')].filter(t => t.getAttribute('font-family') !== 'Bravura').map(t => ({ t, b: t.getBBox() }));
          texts.forEach(({ t, b }) => {
            if (b.x < 1 || b.y < 1 || b.x + b.width > vb.width - 1 || b.y + b.height > vb.height - 1) res.push(`page ${i + 1}: svg text "${t.textContent}" outside its drawing`);
          });
          for (let a = 0; a < texts.length; a++) for (let c = a + 1; c < texts.length; c++) {
            const A = texts[a].b, C = texts[c].b;
            if (A.x < C.x + C.width + 0.8 && C.x < A.x + A.width + 0.8 && A.y < C.y + C.height && C.y < A.y + A.height) res.push(`page ${i + 1}: labels "${texts[a].t.textContent}" and "${texts[c].t.textContent}" overlap`);
          }
        });
        pg.querySelectorAll('.doc p, .doc li').forEach(el => {
          if (el.classList.contains('small')) return;
          const range = document.createRange(); range.selectNodeContents(el);
          const rects = [...range.getClientRects()].filter(q => q.width > 1);
          const lines = {};
          rects.forEach(q => { const k = Math.round(q.top / 3); lines[k] = lines[k] ? [Math.min(lines[k][0], q.left), Math.max(lines[k][1], q.right)] : [q.left, q.right]; });
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length >= 2) {
            const last = lines[ks[ks.length - 1]];
            const w = el.getBoundingClientRect().width;
            if (last[1] - last[0] < 0.12 * w && el.innerText.trim().split(/\s+/).length > 6) res.push(`page ${i + 1}: short last line in "${el.innerText.trim().slice(0, 40)}..."`);
          }
        });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (skip(el)) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && ((el.children.length === 0 && ((el.textContent || '').trim() || el.matches('svg, img'))) || el.matches('.sc, .sp, .kb, .box, table'))) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 105) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer (over 10% of the page)`);
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
        sq.querySelectorAll('.lbl, .lbl span, .pill, .sub, .hd').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.bottom > btop - 8) res.push(`square ${i + 1}: text "${el.textContent.trim().slice(0, 24)}" within 8px of the band`);
          if (r.left < sr.left + 24 || r.right > sr.right - 24) res.push(`square ${i + 1}: text "${el.textContent.trim().slice(0, 24)}" too close to the side edge`);
        });
        sq.querySelectorAll('.pill').forEach(el => { if (el.scrollWidth > el.clientWidth + 1) res.push(`square ${i + 1}: pill text overflows`); });
        const sh = sq.querySelectorAll('.shot img');
        sh.forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
      });
      document.querySelectorAll('.cover').forEach((pg, i) => {
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
