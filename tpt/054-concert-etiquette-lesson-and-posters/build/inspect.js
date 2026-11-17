
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
      d.posters = A('[data-poster]', e => ({ i: +e.dataset.poster, page: pageNo(e), text: T(e), sw: e.scrollWidth, cw: e.clientWidth, sh: e.scrollHeight, ch: e.clientHeight,
                                              lines: Math.round(e.getBoundingClientRect().height / parseFloat(getComputedStyle(e).lineHeight)),
                                              icon: (e.closest('.page').querySelector('svg.icon') || {dataset: {}}).dataset.icon || '' }));
      d.icons = A('svg.icon', s => {
        const g = s.querySelector('g.art'); const bb = g.getBBox(); const sw = +s.dataset.sw; const vb = s.viewBox.baseVal;
        return { page: pageNo(s), icon: s.dataset.icon, x0: bb.x, y0: bb.y, x1: bb.x + bb.width, y1: bb.y + bb.height, sw, w: vb.width, h: vb.height };
      });
      d.aud = A('[data-aud]', e => ({ i: +e.dataset.aud, page: pageNo(e), text: T(e.querySelector('.tx')), boxes: e.querySelectorAll('.bx').length,
                                       pref: e.querySelector('[data-pref]') ? +e.querySelector('[data-pref]').dataset.pref : 0, ppage: e.querySelector('[data-pref]') ? +e.querySelector('[data-pref]').dataset.ppage : 0, rftxt: T(e.querySelector('.rf')) }));
      d.perf = A('[data-perf]', e => ({ i: +e.dataset.perf, page: pageNo(e), text: T(e.querySelector('.tx')), boxes: e.querySelectorAll('.bx').length, group: e.querySelector('.gp').dataset.group }));
      d.perfhead = A('[data-groups]', e => ({ g: e.dataset.groups, txt: T(e.closest('.ckh')) }));
      d.prefs = A('[data-pref]', e => ({ page: pageNo(e), pref: +e.dataset.pref, ppage: +e.dataset.ppage, txt: T(e) }));
      d.tickets = A('[data-ticket]', e => ({ t: +e.dataset.ticket, page: pageNo(e), qs: [...e.querySelectorAll('[data-q]')].map(q => ({ n: q.dataset.q, text: T(q) })),
                                              opts: [...e.querySelectorAll('[data-opt]')].map(o => ({ l: o.dataset.opt, text: T(o.querySelector('span')) })), lines: e.querySelectorAll('.rl').length,
                                              hasKey: /answer:/i.test(T(e)) }));
      d.keyqs = A('[data-keyq]', e => ({ n: e.dataset.keyq, correct: e.dataset.correct || '', text: T(e.querySelector('.kh')), q: T(e.querySelector('p')),
                                         opts: [...e.querySelectorAll('[data-keyopt]')].map(o => ({ l: o.dataset.keyopt, ok: o.classList.contains('ok'), text: T(o.querySelector('span')) })) }));
      d.stepsRows = A('[data-step]', e => ({ n: +e.dataset.step, min: +e.dataset.min, txt: T(e.children[2]), name: T(e.children[1]) }));
      d.mintotal = A('[data-mintotal]', e => ({ v: +e.dataset.mintotal, txt: T(e) }));
      d.stepheads = A('[data-stephead]', e => ({ n: +e.dataset.stephead, min: +e.dataset.min, page: pageNo(e), txt: T(e) }));
      d.stepRefs = A('[data-stepref]', e => ({ n: +e.dataset.stepref, page: pageNo(e), txt: T(e) }));
      d.disc = A('[data-disc]', e => ({ i: +e.dataset.disc, page: pageNo(e), text: T(e) }));
      d.roles = A('[data-role]', e => ({ l: e.dataset.role, page: pageNo(e), text: T(e) }));
      d.habits = A('[data-habit]', e => ({ i: +e.dataset.habit, text: T(e), page: pageNo(e) }));
      d.refs = A('[data-ref]', e => ({ page: pageNo(e), kind: e.dataset.ref, n: +e.dataset.n, kind2: e.dataset.ref2 || '', n2: +(e.dataset.n2 || 0), txt: T(e) }));
      d.pagetext = A('.page', pg => T(pg));
      d.pagetextNoFoot = A('.page', pg => { const c = pg.cloneNode(true); c.querySelectorAll('.foot,.wm').forEach(x => x.remove()); return c.innerText.replace(/\s+/g, ' ').trim(); });
      d.foots = A('.page', pg => T(pg.querySelector('.foot')));
      const res = [];
      d.gaps = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const n = i + 1, pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${n}: content overflows the page`);
        let low = 0; const boxes = [];
        pg.querySelectorAll('.blk, .rl, .top, .name, .how, .doc p, .doc li, .doc table, .doc h2, .ck, .tk, .sh, .say, .do, .rc').forEach(el => {
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
        pg.querySelectorAll('.ck, .tk, .box, td, .rc, .say, .do, .how, .pt, .psub, .prem, .pk, .sh, .tx').forEach(el => {
          if (getComputedStyle(el).display === 'inline') return;
          if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) res.push(`page ${n}: text clipped in ${el.tagName}.${el.className} (${el.scrollWidth}x${el.scrollHeight} in ${el.clientWidth}x${el.clientHeight}) ${el.innerText.slice(0,30)}`);
        });
        pg.querySelectorAll('p, li, .how, .psub, .prem, .tx, .say, .do').forEach(el => {
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
        // poster text must lie inside the page margins
        pg.querySelectorAll('.pt, .psub, .prem, .pk').forEach(el => {
          const range = document.createRange(); range.selectNodeContents(el);
          for (const rc of range.getClientRects()) if (rc.left < pr.left + 0.35 * 96 || rc.right > pr.right - 0.35 * 96) res.push(`page ${n}: poster text reaches the page edge in ${el.className}`);
        });
        pg.querySelectorAll('img').forEach(im => {
          const r = im.getBoundingClientRect();
          if (r.left < pr.left + 0.2 * 96 || r.right > pr.right - 0.2 * 96 || r.top < pr.top + 0.2 * 96 || r.bottom > ftop) res.push(`page ${n}: an image is too near the page edge`);
          const par = im.parentElement.getBoundingClientRect();
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
