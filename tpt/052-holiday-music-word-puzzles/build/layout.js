
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
        pg.querySelectorAll('svg.wsgrid, svg.cwgrid, svg.exws, svg.excw, svg.icon, .wlist, .cluebox, .keyblock, .klist, .doc table, .doc p, .doc ul, .how, .name, .top, .tbox, .step, .howsec, .stp').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${cls(el)} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${cls(el)} too close to the page edge`);
          if (el.matches('svg.wsgrid, svg.cwgrid, svg.exws, svg.excw, .wlist, .cluebox, .keyblock, .tbox, .step')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 8 && gy < 8) res.push(`page ${i + 1}: two boxes closer than 8px (${cls(boxes[a][0])} / ${cls(boxes[c][0])})`);
        }
        // title versus the icons next to it
        const tt = pg.querySelector('.top .tt'), ic = pg.querySelector('.top .icons'), tg = pg.querySelector('.top .tag');
        if (tt && ic && tg) {
          const rg = document.createRange(); rg.selectNodeContents(tt);
          const sub = pg.querySelector('.top .t small'); const rs = document.createRange(); rs.selectNodeContents(sub);
          const tr = Math.max(rg.getBoundingClientRect().right, rs.getBoundingClientRect().right);
          const ir = ic.getBoundingClientRect(), gr = tg.getBoundingClientRect();
          if (ir.left - tr < 22) res.push(`page ${i + 1}: title is ${(ir.left - tr).toFixed(1)}px from the header icons (needs >= 22)`);
          if (gr.left - ir.right < 22) res.push(`page ${i + 1}: header icons are ${(gr.left - ir.right).toFixed(1)}px from the tag (needs >= 22)`);
        }
        // a one-word last line in a paragraph or instruction
        pg.querySelectorAll('.how, .doc p, .doc li, .stp p, .cluebox li').forEach(el => {
          const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          const tops = [];
          let node;
          while ((node = w.nextNode())) {
            const t = node.nodeValue; const re = /\S+/g; let m;
            while ((m = re.exec(t))) {
              const rg = document.createRange(); rg.setStart(node, m.index); rg.setEnd(node, m.index + m[0].length);
              const rc = rg.getClientRects()[0]; if (rc) tops.push([Math.round(rc.top), m[0]]);
            }
          }
          if (!tops.length) return;
          const lastTop = tops[tops.length - 1][0];
          const lines = new Set(tops.map(x => x[0]));
          const lastLine = tops.filter(x => Math.abs(x[0] - lastTop) < 3);
          if (lines.size > 1 && lastLine.length === 1 && !el.closest('.cluebox')) res.push(`page ${i + 1}: one-word last line "${lastLine[0][1]}" in ${el.tagName}.${cls(el)}`);
        });
        // text that does not fit its box
        pg.querySelectorAll('.tag .ln, .tag .lv, .kt, .kr, .w, th, td').forEach(el => {
          if (el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).display !== 'inline') res.push(`page ${i + 1}: ${el.tagName}.${cls(el)} text wider than its box`);
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
