
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const r = await p.evaluate(() => {
    const res = [];
    const ink = el => {
      const cv = document.createElement('canvas').getContext('2d');
      const fs = parseFloat(el.getAttribute('font-size'));
      cv.font = `${el.getAttribute('font-weight')} 100px ${getComputedStyle(el).fontFamily}`;
      const m = cv.measureText(el.textContent), k = fs / 100;
      const x = parseFloat(el.getAttribute('x')), y = parseFloat(el.getAttribute('y'));
      const sh = el.getAttribute('text-anchor') === 'middle' ? m.width * k / 2 : 0;
      const x0 = x - sh - m.actualBoundingBoxLeft * k, x1 = x - sh + m.actualBoundingBoxRight * k;
      return { x: x0, y: y - m.actualBoundingBoxAscent * k, width: x1 - x0, height: (m.actualBoundingBoxAscent + m.actualBoundingBoxDescent) * k };
    };
    document.querySelectorAll('svg').forEach(sv => sv.querySelectorAll('text.cwn').forEach(n => {
      const l = sv.querySelector(`text.cwl[data-r="${n.dataset.r}"][data-c="${n.dataset.c}"]`);
      const a = ink(n), c = ink(l);
      const cell = sv.querySelector(`rect.cwc[data-r="${n.dataset.r}"][data-c="${n.dataset.c}"]`).getBBox();
      if (a.x < c.x + c.width && c.x < a.x + a.width && a.y < c.y + c.height && c.y < a.y + a.height) res.push(`number ${n.textContent} overlaps letter ${l.textContent}`);
      for (const t of [a, c]) if (t.x < cell.x + 0.3 || t.y < cell.y || t.x + t.width > cell.x + cell.width || t.y + t.height > cell.y + cell.height) res.push(`number ${n.textContent} or letter ${l.textContent} leaves its cell`);
    }));
    return res;
  });
  await b.close();
  console.log(JSON.stringify(r));
})().catch(e => { console.error(e); process.exit(1); });
