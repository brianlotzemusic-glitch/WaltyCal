
const { chromium } = require('playwright'); const url = require('url'); const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')); const out = [];
  const browser = await chromium.launch();
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.kind === 'sq' ? 1000 : 816, height: j.kind === 'sq' ? 1000 : 1056 } });
    await page.goto(url.pathToFileURL(j.html).href); await page.evaluate(() => document.fonts.ready);
    const res = await page.evaluate((kind) => {
      const probs = [];
      if (kind === 'page') {
        document.querySelectorAll('.page').forEach((pg, i) => {
          const pr = pg.getBoundingClientRect(); const ft = pg.querySelector('.foot'); const fr = ft ? ft.getBoundingClientRect() : null;
          if (pg.scrollHeight > pg.clientHeight + 1) probs.push(`page ${i+1}: content taller than the page (${pg.scrollHeight} > ${pg.clientHeight})`);
          pg.querySelectorAll('*').forEach(el => {
            if (el.closest('.foot') || el.closest('.wm') || el.tagName === 'tspan') return;
            const r = el.getBoundingClientRect(); if (r.width === 0 || r.height === 0) return;
            if (fr && r.bottom > fr.top + 0.5 && !el.contains(ft) && !ft.contains(el)) probs.push(`page ${i+1}: <${el.tagName.toLowerCase()} class="${el.className && el.className.baseVal === undefined ? el.className : ''}"> overlaps the footer`);
            if (r.right > pr.right - 0.3 * 96 + 0.5 && !el.closest('.cover')) probs.push(`page ${i+1}: <${el.tagName.toLowerCase()}> reaches ${Math.round(r.right - pr.left)}px of ${Math.round(pr.width)}`);
          });
        });
      } else {
        const sq = document.querySelector('.sq'); const band = sq.querySelector('.band'); const bt = band.getBoundingClientRect().top;
        sq.querySelectorAll('.shot, .lbl, .pcard, .hd, .sub, img, svg').forEach(el => {
          const r = el.getBoundingClientRect(); if (r.bottom > bt - 8) probs.push(`${el.className || el.tagName}: bottom ${Math.round(r.bottom)} runs into the band at ${Math.round(bt)}`);
          if (r.right > 1000 || r.left < 0) probs.push(`${el.className || el.tagName}: outside the image`);
        });
        sq.querySelectorAll('.shot').forEach(s => { const img = s.querySelector('img'); if (img && img.getBoundingClientRect().height > s.getBoundingClientRect().height + 4) probs.push('shot clips its page image'); });
        const w = sq.querySelectorAll('.swm').length, sh = sq.querySelectorAll('.shot').length; if (w !== sh) probs.push(`watermarks ${w} vs shots ${sh}`);
      }
      return [...new Set(probs)];
    }, j.kind);
    out.push({ html: j.html, probs: res }); await page.close();
  }
  await browser.close(); console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
