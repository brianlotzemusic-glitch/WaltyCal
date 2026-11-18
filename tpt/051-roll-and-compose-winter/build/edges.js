
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = [];
  const SC = 6;
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 816, height: 1056 } });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    const items = await p.evaluate(() => [...document.querySelectorAll('svg.die, svg[data-icon]')].map(e => {
      const o = e.cloneNode(true);
      return { html: o.outerHTML, w: e.getBoundingClientRect().width, h: e.getBoundingClientRect().height, sw: Number(e.getAttribute('data-sw') || e.getAttribute('data-icon-sw') || 2), vb: e.getAttribute('viewBox') };
    }));
    const seen = new Set();
    for (const it of items) {
      if (seen.has(it.html)) continue;
      seen.add(it.html);
      const q = await b.newPage({ viewport: { width: Math.ceil(it.w) + 8, height: Math.ceil(it.h) + 8 }, deviceScaleFactor: SC });
      await q.setContent('<html><body style="margin:0;background:transparent"><div id="x" style="position:absolute;left:4px;top:4px">' + it.html.replace(/display:inline-block;vertical-align:middle/, 'display:block') + '</div></body></html>');
      const buf = await q.locator('#x svg').screenshot({ omitBackground: true });
      const png = buf.toString('base64');
      const r = await q.evaluate(async (png) => {
        const im = new Image(); im.src = 'data:image/png;base64,' + png; await im.decode();
        const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
        const g = c.getContext('2d'); g.drawImage(im, 0, 0);
        const d = g.getImageData(0, 0, c.width, c.height).data;
        let x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1;
        for (let y = 0; y < c.height; y++) for (let x = 0; x < c.width; x++) if (d[(y * c.width + x) * 4 + 3] > 8) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
        return { W: c.width, H: c.height, x0, y0, x1, y1 };
      }, png);
      const vbw = Number(it.vb.split(/\s+/)[2]);
      const upu = r.W / vbw;               // pixels per viewBox unit
      const need = Math.max(1, it.sw * upu * 0.999);
      const m = [r.x0, r.y0, r.W - 1 - r.x1, r.H - 1 - r.y1];
      if (r.x1 < 0) out.push(f.split('/').pop() + ': an icon rendered empty');
      else if (Math.min(...m) < 1) out.push(f.split('/').pop() + ': ' + (it.html.match(/data-n="(\d)"/) ? 'die ' + it.html.match(/data-n="(\d)"/)[1] : 'icon') + ' touches the edge of its render box (margins ' + m.join('/') + 'px)');
      else if (Math.min(...m) < need) out.push(f.split('/').pop() + ': ' + (it.html.match(/data-n="(\d)"/) ? 'die ' + it.html.match(/data-n="(\d)"/)[1] : 'icon') + ' has less padding than its stroke (margins ' + m.join('/') + 'px, needs ' + need.toFixed(1) + ')');
      await q.close();
    }
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
