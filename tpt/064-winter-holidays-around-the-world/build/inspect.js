
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
      d.readings = A('[data-reading]', e => ({ k: e.dataset.reading, page: pageNo(e), text: T(e) }));
      d.rqs = A('[data-rq]', e => ({ k: e.dataset.rq, n: +e.dataset.n, page: pageNo(e), text: T(e), lines: e.querySelectorAll('.rl').length }));
      d.principles = A('[data-principle]', e => ({ page: pageNo(e), cells: [...e.children].map(c => T(c)) }));
      d.facts = A('[data-fact]', e => ({ k: e.dataset.fact, page: pageNo(e), cells: [...e.children].map(c => T(c)) }));
      d.prompts = A('[data-prompt]', e => ({ k: e.dataset.prompt, celeb: e.dataset.celeb, n: +e.dataset.n, page: pageNo(e), head: T(e.querySelector('.ph b')),
                                              opts: [...e.querySelectorAll('.opts span')].map(s => T(s)), lp: T(e.querySelector('.lp')),
                                              lineH: e.querySelector('.ln') ? e.querySelector('.ln').getBoundingClientRect().height : 0 }));
      d.exbox = A('.ex', e => ({ page: pageNo(e), text: T(e) }));
      d.terms = A('[data-term]', e => ({ t: e.dataset.term, page: pageNo(e), text: T(e) }));
      d.elems = A('[data-elem]', e => ({ e: e.dataset.elem, text: T(e) }));
      d.cmp = A('[data-cmp]', e => ({ k: e.dataset.cmp, page: pageNo(e), text: T(e.children[0]) }));
      d.chart = A('[data-chart]', e => ({ k: e.dataset.chart, page: pageNo(e), text: T(e.children[0]), cells: e.children.length }));
      d.rubric = A('[data-rubric]', e => ({ n: +e.dataset.rubric, cells: e.children.length, text: T(e) }));
      d.rubricHead = A('.rub th', e => T(e));
      d.rubricTotal = A('[data-total]', e => ({ v: +e.dataset.total, text: T(e) }));
      d.steps = A('[data-step]', e => ({ n: +e.dataset.step, min: +e.dataset.min, text: T(e) }));
      d.mintotal = A('[data-mintotal]', e => ({ v: +e.dataset.mintotal, text: T(e) }));
      d.ak = A('[data-ak]', e => ({ k: e.dataset.ak, n: +e.dataset.n, page: pageNo(e), text: T(e) }));
      d.reflect = A('[data-reflect]', e => ({ text: T(e), boxes: e.querySelectorAll('.bx').length }));
      d.refs = A('[data-ref]', e => ({ page: pageNo(e), kind: e.dataset.ref, n: +e.dataset.n, kind2: e.dataset.ref2 || '', n2: +(e.dataset.n2 || 0), txt: T(e) }));
      d.pagetext = A('.page', pg => T(pg));
      d.pagetextNoFoot = A('.page', pg => { const c = pg.cloneNode(true); c.querySelectorAll('.foot,.wm').forEach(x => x.remove()); return c.innerText.replace(/\s+/g, ' ').trim(); });
      d.foots = A('.page', pg => T(pg.querySelector('.foot')));
      d.svgs = A('svg[data-svg]', s => {
        const g = s.querySelector('g.art'); const bb = g.getBBox(); const sw = +s.dataset.sw; const vb = s.viewBox.baseVal;
        return { page: pageNo(s), name: s.dataset.svg, x0: bb.x, y0: bb.y, x1: bb.x + bb.width, y1: bb.y + bb.height, sw, w: vb.width, h: vb.height };
      });
      d.imgs = A('img', im => ({ page: pageNo(im), ok: im.complete && im.naturalWidth > 0 }));
      const res = [];
      d.gaps = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const n = i + 1, pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${n}: content overflows the page`);
        let low = 0;
        // every element inside the page except the footer, the watermark and the spacer: its bottom keeps 8px+ clear of the footer rule
        pg.querySelectorAll('*').forEach(el => {
          if (ft && (ft === el || ft.contains(el))) return;
          if (el.closest('.wm') || el.classList.contains('wm') || el.classList.contains('fill')) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0 || r.width === 0) return;
          if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') return;
          low = Math.max(low, r.bottom);
          if (r.bottom > ftop - 8) res.push(`page ${n}: ${el.tagName}.${el.className} bottom is ${(ftop - r.bottom).toFixed(1)}px above the footer rule (needs >= 8)`);
          if (n > 1 && (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5)) res.push(`page ${n}: ${el.tagName}.${el.className} too close to the page edge`);
        });
        d.gaps.push(Math.round(ftop - low));
        pg.querySelectorAll('.pc, .ex, .fact, .notes, td, th, .vc, .ck, .kq, .read, .rq li, .tx, .lp, .opts').forEach(el => {
          if (getComputedStyle(el).display === 'inline') return;
          if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) res.push(`page ${n}: text clipped in ${el.tagName}.${el.className} (${el.scrollWidth}x${el.scrollHeight} in ${el.clientWidth}x${el.clientHeight}) ${el.innerText.slice(0, 40)}`);
        });
        pg.querySelectorAll('p, li, .read, .lp, .tx, .vc p').forEach(el => {
          const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          const lines = {}; let node;
          while ((node = walker.nextNode())) {
            const re = /\S+/g; let m;
            while ((m = re.exec(node.textContent))) {
              const rg = document.createRange(); rg.setStart(node, m.index); rg.setEnd(node, m.index + m[0].length);
              const rc = rg.getClientRects()[0]; if (!rc) continue;
              const k = Math.round((rc.top + rc.bottom) / 8); (lines[k] = lines[k] || []).push(m[0]);
            }
          }
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length > 1 && lines[ks[ks.length - 1]].length === 1)
            res.push(`page ${n}: one-word last line "${lines[ks[ks.length - 1]][0]}" in ${el.tagName}.${el.className}`);
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
