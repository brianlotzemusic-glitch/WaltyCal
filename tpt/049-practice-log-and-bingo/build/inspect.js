
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = {};
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 816, height: 1056 } });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    out[f.split('/').pop()] = await p.evaluate(() => {
      const T = el => el ? el.innerText.replace(/\s+/g, ' ').trim() : '';
      const A = (sel, fn) => [...document.querySelectorAll(sel)].map(fn);
      const pageNo = el => { const pg = el.closest('.page'); return pg ? +pg.dataset.page : 0; };
      const d = {};
      d.pages = A('.page', pg => ({ n: +pg.dataset.page, kind: pg.dataset.kind }));
      d.cells = A('[data-board]', e => ({ page: pageNo(e), board: +e.dataset.board, r: +e.dataset.r, c: +e.dataset.c, num: +e.dataset.num,
                                          numTxt: T(e.querySelector('.num')), text: T(e.querySelector('.ct')) }));
      d.calls = A('[data-call]', e => ({ page: pageNo(e), num: +e.dataset.call, numTxt: T(e.querySelector('.cn')), text: T(e.querySelector('.ct')), boards: T(e.querySelector('.cb')) }));
      d.days = A('[data-day]', e => ({ day: +e.dataset.day, txt: T(e.querySelector('.n')), row: +e.closest('[data-weekrow]').dataset.weekrow }));
      d.weeks = A('[data-weekrow]', e => ({ week: +e.dataset.weekrow, label: T(e.querySelector('[data-weeklabel]')), ndays: e.querySelectorAll('[data-day]').length,
                                            hasTot: !!e.querySelector('[data-weektot]'), offs: e.querySelectorAll('td.off').length, cols: e.children.length }));
      d.sumboxes = A('[data-sumbox]', e => ({ week: +e.dataset.sumbox, txt: T(e) }));
      d.grand = A('[data-grand]', e => T(e));
      d.muls = A('[data-mul]', e => ({ a: e.dataset.mul, txt: T(e) }));
      d.pts = A('[data-pts]', e => ({ v: +e.dataset.pts, txt: T(e) }));
      d.ptstotal = A('[data-ptstotal]', e => ({ v: +e.dataset.ptstotal, txt: T(e) }));
      d.logrows = A('[data-logrow]', e => ({ id: e.dataset.logrow, page: pageNo(e), nrate: e.querySelectorAll('.dots i').length, day: T(e.querySelector('.day')),
                                              ncells: e.children.length }));
      d.diags = A('[data-diag]', e => ({ k: e.dataset.diag, cells: e.querySelector('svg').dataset.cells, title: T(e.querySelector('b')) }));
      d.lines = A('[data-lines]', e => T(e));
      d.streaks = A('[data-streak]', e => ({ s: +e.dataset.streak, txt: T(e) }));
      d.goals = A('[data-goal]', e => ({ g: +e.dataset.goal, txt: T(e) }));
      d.steps = A('.step', e => ({ page: pageNo(e), n: T(e.querySelector('.n')) }));
      d.pagetext = A('.page', pg => T(pg));
      const res = [];
      d.gaps = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const n = i + 1, pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${n}: content overflows the page`);
        let low = 0; const boxes = [];
        pg.querySelectorAll('.blk, .rl, .top, .name, .how, .doc p, .doc li, .doc table, .doc h2, .step, .dg, .crow, .cell').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          low = Math.max(low, r.bottom);
          if (r.bottom > ftop - 9) res.push(`page ${n}: ${el.tagName}.${el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -9)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${n}: ${el.tagName}.${el.className} too close to the page edge`);
          if (el.matches('.blk')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 3 && gy < 3) res.push(`page ${n}: ${boxes[a][0].className} and ${boxes[c][0].className} touch or overlap`);
        }
        d.gaps.push(Math.round(ftop - low));
        pg.querySelectorAll('.cell, .crow, .ct, .box, .dg span, .step p, td, .sb, .how, .key').forEach(el => {
          if (getComputedStyle(el).display === 'inline') return;
          if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) res.push(`page ${n}: text clipped in ${el.tagName}.${el.className} (${el.scrollWidth}x${el.scrollHeight} in ${el.clientWidth}x${el.clientHeight}) ${el.innerText.slice(0,30)}`);
        });
        pg.querySelectorAll('p, li, .how, .key, .step p, .dg span').forEach(el => {
          const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          const lines = {}; let node;
          while ((node = walker.nextNode())) {
            const re = /\S+/g; let m;
            while ((m = re.exec(node.textContent))) {
              const rg = document.createRange(); rg.setStart(node, m.index); rg.setEnd(node, m.index + m[0].length);
              const rc = rg.getClientRects()[0]; if (!rc) continue;
              const k = Math.round(rc.top / 4); (lines[k] = lines[k] || []).push(m[0]);
            }
          }
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length > 1 && lines[ks[ks.length - 1]].length === 1)
            res.push(`page ${n}: one-word last line "${lines[ks[ks.length - 1]][0]}" in ${el.tagName}.${el.className}`);
        });
      });
      d.layout = res;
      return d;
    });
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
