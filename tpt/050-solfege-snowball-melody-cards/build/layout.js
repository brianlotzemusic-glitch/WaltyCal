
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
        pg.querySelectorAll('svg.ns, svg.rc, svg.mat, .keyblock, .doc table, .trk table, .doc p, .doc ul, .how, .name, .top, .box, .steps, .klegend').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: element too close to the page edge`);
          if (el.matches('svg.ns, svg.rc, svg.mat, .keyblock')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 3 && gy < 3) res.push(`page ${i + 1}: two boxes touch or overlap`);
        }
        // syllables must not collide with each other or with other notation text
        pg.querySelectorAll('svg.ns').forEach(sv => {
          const ts = [...sv.querySelectorAll('text.syl, text.rlab, text.let')].map(t => t.getBoundingClientRect());
          for (let a = 0; a < ts.length; a++) for (let c = a + 1; c < ts.length; c++) {
            const A = ts[a], C = ts[c];
            if (Math.min(A.right, C.right) - Math.max(A.left, C.left) > -0.5 && Math.min(A.bottom, C.bottom) - Math.max(A.top, C.top) > 0) res.push(`page ${i + 1}: two syllable labels touch in ${sv.getAttribute('data-id')}`);
          }
        });
        pg.querySelectorAll('svg.rc').forEach(sv => {
          const ts = [...sv.querySelectorAll('text.rw')].map(t => t.getBoundingClientRect());
          for (let a = 0; a < ts.length; a++) for (let c = a + 1; c < ts.length; c++) {
            if (Math.min(ts[a].right, ts[c].right) - Math.max(ts[a].left, ts[c].left) > -0.5) res.push(`page ${i + 1}: two rhythm words touch in ${sv.getAttribute('data-id')}`);
          }
        });
        // table cell text must not wrap awkwardly: no one-word orphan lines in paragraphs/list items
        pg.querySelectorAll('.doc p, .doc li, .how, .step p').forEach(el => {
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
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
