
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
      d.pages = A('.page', pg => ({ n: +pg.dataset.page, kind: pg.dataset.kind, name: pg.dataset.name, wms: pg.querySelectorAll('.wm').length }));
      d.refs = A('[data-ref]', e => ({ page: pageNo(e), kind: e.dataset.ref, n: +e.dataset.n, kind2: e.dataset.ref2 || '', n2: +(e.dataset.n2 || 0), txt: T(e) }));
      d.pagetext = A('.page', pg => { const c = pg.cloneNode(true); c.querySelectorAll('.foot,.wm').forEach(x => x.remove()); return c.innerText.replace(/\s+/g, ' ').trim(); });
      d.foottext = A('.page', pg => T(pg.querySelector('.foot')));
      d.rowsWs = A('[data-ws]', e => ({ id: e.dataset.ws, item: +e.dataset.item, page: pageNo(e), blanks: e.querySelectorAll('.wd b').length }));
      d.rid = A('[data-riddle]', e => ({ n: +e.dataset.riddle, page: pageNo(e), clue: T(e.querySelector('.rt p')), blanks: e.querySelectorAll('.wd b').length, clef: T(e.querySelector('.cl')) }));
      d.own = A('[data-own]', e => ({ n: +e.dataset.own, page: pageNo(e), blanks: e.querySelectorAll('.wd b').length }));
      d.spell = A('[data-spell]', e => ({ n: +e.dataset.spell, word: e.dataset.word, page: pageNo(e), shown: T(e.querySelector('.w')) }));
      d.kset = A('[data-kset]', e => ({ id: e.dataset.kset, item: +e.dataset.item, ans: e.dataset.ans, shown: T(e.querySelector('b')), num: T(e.querySelector('i')), page: pageNo(e), txt: T(e) }));
      d.krid = A('[data-krid]', e => ({ n: +e.dataset.krid, ans: e.dataset.ans, shown: T(e.querySelector('b')), page: pageNo(e) }));
      d.kspell = A('[data-kspell]', e => ({ n: +e.dataset.kspell, ans: e.dataset.ans, head: T(e.querySelector('.skh')), page: pageNo(e) }));
      const res = []; d.gaps = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const n = i + 1, pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${n}: content overflows the page`);
        let low = 0; const boxes = [];
        pg.querySelectorAll('.blk, .doc p, .doc li, .doc h2, .tip').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          low = Math.max(low, r.bottom);
          if (r.bottom > ftop - 9) res.push(`page ${n}: ${el.tagName}.${el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -9)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${n}: ${el.tagName}.${el.className} too close to the page edge`);
          if (el.matches('.blk') && !el.matches('.top, .name, .how')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 4 && gy < 4) res.push(`page ${n}: ${boxes[a][0].className} and ${boxes[c][0].className} touch or overlap (no gutter)`);
        }
        d.gaps.push(Math.round(ftop - low));
        pg.querySelectorAll('.rid, .sk, .tip, .kit, .wd, .w, .cap, .cl2, .how, .tag').forEach(el => {
          if (getComputedStyle(el).display === 'inline') return;
          if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) res.push(`page ${n}: text clipped in ${el.tagName}.${el.className} (${el.scrollWidth}x${el.scrollHeight} in ${el.clientWidth}x${el.clientHeight}) ${el.innerText.slice(0,30)}`);
        });
        pg.querySelectorAll('svg.ns').forEach(sv => {
          const br = sv.getBoundingClientRect(); const par = sv.parentElement.getBoundingClientRect();
          if (br.right > par.right + 1 || br.left < par.left - 1) res.push(`page ${n}: a staff sticks out of its box`);
          if (br.right > pr.right - 0.4 * 96 || br.left < pr.left + 0.4 * 96) res.push(`page ${n}: a staff is too close to the page edge`);
        });
        pg.querySelectorAll('img').forEach(im => {
          const r = im.getBoundingClientRect();
          if (r.left < pr.left + 0.2 * 96 || r.right > pr.right - 0.2 * 96 || r.top < pr.top + 0.2 * 96 || r.bottom > ftop) res.push(`page ${n}: an image is too near the page edge`);
          if (!im.complete || im.naturalWidth === 0) res.push(`page ${n}: broken image`);
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
