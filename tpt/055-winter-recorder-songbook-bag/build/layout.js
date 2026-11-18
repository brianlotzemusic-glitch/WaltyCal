
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = [];
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 816, height: 1056 } });
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
        pg.querySelectorAll('svg.ns, svg.fg, .tune, .fgcol, .q, .doc table, .doc p, .doc ul, .name, .top, .steps').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: element too close to the page edge`);
          if (el.matches('.tune, .fgcol, .q')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 6 && gy < 6) res.push(`page ${i + 1}: two boxes lack a gutter`);
        }
        // each svg must fit inside its enclosing box with padding
        pg.querySelectorAll('.tune svg, .fgcol svg, .q svg').forEach(sv => {
          const box = sv.closest('.tune, .fgcol, .q').getBoundingClientRect();
          const s = sv.getBoundingClientRect();
          if (s.left < box.left + 4 || s.right > box.right - 4 || s.top < box.top + 3 || s.bottom > box.bottom - 2) res.push(`page ${i + 1}: a drawing is too close to its box edge`);
        });
        pg.querySelectorAll('svg.ns').forEach(sv => {
          const ts = [...sv.querySelectorAll('text.let')].map(t => t.getBoundingClientRect());
          for (let a = 0; a < ts.length; a++) for (let c = a + 1; c < ts.length; c++) {
            const A = ts[a], C = ts[c];
            if (Math.min(A.right, C.right) - Math.max(A.left, C.left) > -0.5 && Math.min(A.bottom, C.bottom) - Math.max(A.top, C.top) > 0) res.push(`page ${i + 1}: two note letters touch in ${sv.getAttribute('data-id')}`);
          }
          // letters / blank lines must clear the stems above them
          const stems = [...sv.querySelectorAll('line.stem')].map(t => t.getBoundingClientRect());
          [...sv.querySelectorAll('text.let, line.blank')].forEach(t => {
            const T = t.getBoundingClientRect();
            stems.forEach(S => { if (Math.min(T.right, S.right) - Math.max(T.left, S.left) > 0 && Math.min(T.bottom, S.bottom) - Math.max(T.top, S.top) > 0) res.push(`page ${i + 1}: a stem runs into a note letter in ${sv.getAttribute('data-id')}`); });
          });
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
        // blank band at the bottom: the last content block must end within 10% (79 px) of the footer rule
        const kids = [...pg.children].filter(c => !c.classList.contains('foot') && !c.classList.contains('wm') && c.getBoundingClientRect().height > 0);
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (ft && ft.contains(el)) return; if (el.closest('.wm')) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && el.children.length === 0) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 90) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer`);
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
