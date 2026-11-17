
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
      const cls = el => (el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className);
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        const boxes = [];
        pg.querySelectorAll('svg.ns, svg.die, table, .box, .step, .idea, .how, .name, .top, .doc p, .doc ul, .comp, .chk, h2, .cap').forEach(el => {
          if (ft && ft.contains(el)) return;
          if (el.closest('.top') && !el.matches('.top')) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 10) res.push(`page ${i + 1}: ${el.tagName}.${cls(el)} bottom is ${(r.bottom - ftop).toFixed(1)}px vs the footer rule (needs <= -10)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${cls(el)} too close to the page edge`);
          if (el.matches('svg.ns, svg.die, table, .box, .step, .idea') && !(el.parentNode.closest && el.parentNode.closest('svg'))) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 4 && gy < 4) res.push(`page ${i + 1}: ${cls(boxes[a][0])} and ${cls(boxes[c][0])} touch or overlap (gap ${Math.max(gx, gy).toFixed(1)}px)`);
        }
        // header: the title keeps >= 20px from the icons and the badge
        const top = pg.querySelector('.top');
        if (top) {
          const t = top.querySelector('.t').getBoundingClientRect();
          const tg = top.querySelector('.tag').getBoundingClientRect();
          const kids = [...top.querySelectorAll('.deco > *')].map(k => k.getBoundingClientRect());
          if (kids.length) {
            const l = Math.min(...kids.map(k => k.left)), rr = Math.max(...kids.map(k => k.right));
            if (l - t.right < 20) res.push(`page ${i + 1}: title is ${(l - t.right).toFixed(1)}px from the header icons`);
            if (tg.left - rr < 20) res.push(`page ${i + 1}: header icons are ${(tg.left - rr).toFixed(1)}px from the badge`);
          } else if (tg.left - t.right < 20) res.push(`page ${i + 1}: title is ${(tg.left - t.right).toFixed(1)}px from the badge`);
        }
        // labels inside one staff must not touch
        pg.querySelectorAll('svg.ns').forEach(sv => {
          const ts = [...sv.querySelectorAll('text.lab, text.lab2, text.bn, text.chd, text.cnt')].map(t => [t, t.getBoundingClientRect()]);
          for (let a = 0; a < ts.length; a++) for (let c = a + 1; c < ts.length; c++) {
            const A = ts[a][1], C = ts[c][1];
            if (Math.min(A.right, C.right) - Math.max(A.left, C.left) > -0.3 && Math.min(A.bottom, C.bottom) - Math.max(A.top, C.top) > 0) res.push(`page ${i + 1}: two labels touch in ${sv.getAttribute('data-id')}`);
          }
        });
        // table text must stay inside its cell and cells must not wrap to one-word orphans
        pg.querySelectorAll('td, th').forEach(td => {
          if (td.scrollWidth > td.clientWidth + 1) res.push(`page ${i + 1}: text overflows a table cell: "${td.innerText.trim().slice(0, 30)}"`);
        });
        pg.querySelectorAll('.doc p, .doc li, .how, .step p, .idea p, .box p').forEach(el => {
          const range = document.createRange(); range.selectNodeContents(el);
          const rects = [...range.getClientRects()].filter(q => q.width > 1);
          const lines = {};
          rects.forEach(q => { const k = Math.round(q.top / 3); lines[k] = lines[k] ? [Math.min(lines[k][0], q.left), Math.max(lines[k][1], q.right)] : [q.left, q.right]; });
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length >= 2) {
            const last = lines[ks[ks.length - 1]];
            const w = el.getBoundingClientRect().width;
            const txt = el.innerText.trim().split(/\s+/);
            const lastWords = (() => { const rg = document.createRange(); return 0; })();
            if (last[1] - last[0] < 0.12 * w && txt.length > 5) res.push(`page ${i + 1}: short last line in "${el.innerText.trim().slice(0, 40)}..."`);
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
