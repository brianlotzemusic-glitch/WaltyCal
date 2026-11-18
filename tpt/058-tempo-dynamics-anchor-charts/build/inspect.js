
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
      d.posterPages = A('.page.poster', pg => ({
        n: +pg.dataset.page, text: T(pg),
        terms: [...pg.querySelectorAll('[data-term]')].map(e => ({ term: e.dataset.term, abbr: e.dataset.abbr, meaning: e.dataset.meaning, bpm: e.dataset.bpm || '', g: e.dataset.g || '' })),
        pm: T(pg.querySelector('.pm')), tms: A2(pg.querySelectorAll('.tm'), T),
        glyphs: [...pg.querySelectorAll('.symbox .bv')].map(e => e.dataset.g),
        strip: pg.querySelector('[data-strip]') ? pg.querySelector('[data-strip]').dataset.strip : '',
        on: [...pg.querySelectorAll('.strip .s.on')].map(e => e.dataset.s),
        heads: T(pg.querySelector('.pt')),
        icons: [...pg.querySelectorAll('svg.icon')].map(s => s.dataset.icon)
      }));
      function A2(list, fn) { return [...list].map(fn); }
      d.refrows = A('[data-refrow]', e => ({ k: e.dataset.refrow, term: e.dataset.term, abbr: e.dataset.abbr, meaning: e.dataset.meaning, bpm: e.dataset.bpm || '', text: T(e), page: pageNo(e),
                                             g: [...e.querySelectorAll('.bv')].map(x => x.dataset.g), hp: [...e.querySelectorAll('svg.icon')].map(s => s.dataset.icon) }));
      d.orders = A('[data-order]', e => ({ k: e.dataset.order, seq: e.dataset.seq, page: pageNo(e), g: [...e.querySelectorAll('.bv')].map(x => x.dataset.g), txt: T(e) }));
      d.qs = A('[data-qn]', e => ({ n: +e.dataset.qn, type: e.dataset.qtype, ask: e.dataset.ask || '', page: pageNo(e),
        opts: [...e.querySelectorAll('[data-opt]')].map(o => ({ l: o.dataset.opt, val: o.dataset.val })),
        items: [...e.querySelectorAll('[data-item]')].map(o => ({ k: o.dataset.item, blanks: o.querySelectorAll('.bk').length })),
        letters: [...e.querySelectorAll('[data-letter]')].map(o => ({ l: o.dataset.letter, val: o.dataset.val })),
        hp: [...e.querySelectorAll('svg.icon')].map(s => s.dataset.icon), pts: T(e.querySelector('.pt1')) }));
      d.keys = A('[data-keyq]', e => ({ n: +e.dataset.keyq, answer: e.dataset.answer || '', seq: e.dataset.seq || '', page: pageNo(e),
        items: [...e.querySelectorAll('[data-keyitem]')].map(o => ({ k: o.dataset.keyitem, a: o.dataset.answer })),
        ok: [...e.querySelectorAll('.ok')].map(o => T(o)), head: T(e.querySelector('.kh')) }));
      d.refs = A('[data-ref]', e => ({ page: pageNo(e), kind: e.dataset.ref, n: +e.dataset.n, kind2: e.dataset.ref2 || '', n2: +(e.dataset.n2 || 0), txt: T(e) }));
      d.pagetext = A('.page', pg => { const c = pg.cloneNode(true); c.querySelectorAll('.foot,.wm').forEach(x => x.remove()); return c.innerText.replace(/\s+/g, ' ').trim(); });
      d.icons = A('svg.icon', s => {
        const g = s.querySelector('g.art'); const bb = g.getBBox(); const sw = +s.dataset.sw; const vb = s.viewBox.baseVal;
        return { page: pageNo(s), icon: s.dataset.icon, x0: bb.x, y0: bb.y, x1: bb.x + bb.width, y1: bb.y + bb.height, sw, w: vb.width, h: vb.height };
      });
      const res = []; d.gaps = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const n = i + 1, pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${n}: content overflows the page`);
        let low = 0; const boxes = [];
        pg.querySelectorAll('.blk, .top, .name, .doc p, .doc li, .doc table, .doc h2, .q, .kq, .rt').forEach(el => {
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
          if (gx < 4 && gy < 4) res.push(`page ${n}: ${boxes[a][0].className} and ${boxes[c][0].className} touch or overlap (no gutter)`);
        }
        d.gaps.push(Math.round(ftop - low));
        pg.querySelectorAll('.pt, .pm, .psub, .prem, .pk, .tb, .tn, .tm, .tb2, .symbox, .strip .s, .pnote, .q, .kq, .it, .mn, .op, td, th, .ordline, .stripcap').forEach(el => {
          if (getComputedStyle(el).display === 'inline') return;
          const hasG = !!el.querySelector('.bv') || el.matches('.pt, .tn, .pm, .tm'); if ((!hasG && el.scrollHeight > el.clientHeight + 2) || el.scrollWidth > el.clientWidth + 2) res.push(`page ${n}: text clipped in ${el.tagName}.${el.className} (${el.scrollWidth}x${el.scrollHeight} in ${el.clientWidth}x${el.clientHeight}) ${el.innerText.slice(0,30)}`);
        });
        // every text run and every symbol box on a poster stays inside the page margins and inside its parent box
        pg.querySelectorAll('.pt, .pm, .psub, .prem, .pk, .tn, .tm, .tb2, .pnote, .strip .s, .symbox, .tb').forEach(el => {
          const range = document.createRange(); range.selectNodeContents(el);
          for (const rc of range.getClientRects()) if (rc.left < pr.left + 0.35 * 96 || rc.right > pr.right - 0.35 * 96) res.push(`page ${n}: text reaches the page edge in ${el.className}`);
        });
        pg.querySelectorAll('.symbox, .tb, .strip .s').forEach(box => {
          const br = box.getBoundingClientRect();
          box.querySelectorAll('.bv, svg.icon').forEach(ch => {
            const r = ch.getBoundingClientRect();
            const isG = ch.classList.contains('bv'); if (r.left < br.left + 6 || r.right > br.right - 6 || (!isG && (r.top < br.top + 2 || r.bottom > br.bottom - 2))) res.push(`page ${n}: ${ch.className.baseVal || ch.className} does not sit inside its box with padding`);
          });
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
