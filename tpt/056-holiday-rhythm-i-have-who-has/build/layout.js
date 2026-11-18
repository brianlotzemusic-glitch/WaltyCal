
const { chromium } = require('playwright');
const url = require('url');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const out = [];
  const shotDir = process.argv[2];
  fs.mkdirSync(shotDir, { recursive: true });
  let shotN = 0;
  for (const f of process.argv.slice(3)) {
    const p = await b.newPage({ viewport: { width: 816, height: 1056 }, deviceScaleFactor: 4 });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const res = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        const boxes = [];
        pg.querySelectorAll('svg.ns, .card, .box, .step, .doc table, .doc p, .doc ul, .top, .cinstr, .exbox, .loop').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 6) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -6)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: element ${el.tagName}.${el.getAttribute('class')} too close to the page edge`);
          if (el.matches('.card, .box, .step')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 8 && gy < 8) res.push(`page ${i + 1}: two boxes lack a gutter`);
        }
        // cards: everything inside a card keeps padding from the dashed cut line
        pg.querySelectorAll('.card').forEach(cd => {
          const box = cd.getBoundingClientRect();
          if (cd.scrollHeight > cd.clientHeight + 1 || cd.scrollWidth > cd.clientWidth + 1) res.push(`page ${i + 1}: card ${cd.dataset.n} content overflows its card`);
          cd.querySelectorAll('svg, .cn, .mk, .wh, .lab, .lvt').forEach(ch => {
            const s = ch.getBoundingClientRect();
            if (s.left < box.left + 6 || s.right > box.right - 6 || s.top < box.top + 4 || s.bottom > box.bottom - 3) res.push(`page ${i + 1}: card ${cd.dataset.n} ${ch.tagName}.${ch.getAttribute('class')} too close to the cut line`);
          });
          const kids = [...cd.querySelectorAll('.ch, .lab, svg.ns, .wh')].map(e => e.getBoundingClientRect());
          for (let a = 0; a < kids.length - 1; a++) if (kids[a].bottom > kids[a + 1].top + 0.5) res.push(`page ${i + 1}: card ${cd.dataset.n} parts overlap`);
        });
        pg.querySelectorAll('.box svg, .exbox svg, .syt svg').forEach(sv => {
          const box = sv.closest('.box, .exbox, td').getBoundingClientRect();
          const s = sv.getBoundingClientRect();
          if (s.left < box.left + 4 || s.right > box.right - 4 || s.top < box.top + 2 || s.bottom > box.bottom - 2) res.push(`page ${i + 1}: a drawing is too close to its box edge`);
        });
        pg.querySelectorAll('.doc p, .doc li').forEach(el => {
          const range = document.createRange(); range.selectNodeContents(el);
          const rects = [...range.getClientRects()].filter(q => q.width > 1);
          const lines = {};
          rects.forEach(q => { const k = Math.round(q.top / 3); lines[k] = lines[k] ? [Math.min(lines[k][0], q.left), Math.max(lines[k][1], q.right)] : [q.left, q.right]; });
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length >= 2) {
            const last = lines[ks[ks.length - 1]];
            const w = el.getBoundingClientRect().width;
            const txt = el.innerText.trim().split(/\s+/);
            if (last[1] - last[0] < 0.12 * w && txt.length > 6) res.push(`page ${i + 1}: short last line in "${el.innerText.trim().slice(0, 40)}..."`);
          }
        });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (ft && ft.contains(el)) return; if (el.closest('.wm')) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && el.children.length === 0) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 90) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer`);
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    // rendered-pixel check input: screenshot every notation staff and corner icon on its own
    if (f.endsWith('resource.html')) {
      const handles = await p.$$('svg.ns, svg.ic');
      for (const h of handles) {
        const name = shotDir + '/s' + String(shotN++).padStart(4, '0') + '.png';
        await h.screenshot({ path: name });
      }
    }
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
