
const { chromium } = require('playwright'); const url = require('url'); const fs = require('fs');
(async () => { const files = JSON.parse(process.argv[2]); const b = await chromium.launch(); const out = [];
 for (const f of files) { const p = await (await b.newContext({viewport:{width:1000,height:1000}})).newPage();
  await p.goto(url.pathToFileURL(f).href, {waitUntil:'load'}); await p.evaluate(() => document.fonts.ready);
  out.push(await p.evaluate(() => { const band = document.querySelector('.band').getBoundingClientRect().top; let maxb = 0, maxr = 0, minl = 9999, minimg = [];
   document.querySelectorAll('.sq *').forEach(e => { if (e.closest('.band') || e.classList.contains('body') || e.classList.contains('sq')) return;
     const r = e.getBoundingClientRect(); if (r.width === 0 || r.height === 0) return; if (e.children.length && !e.matches('svg,img,text')) return;
     maxb = Math.max(maxb, r.bottom); maxr = Math.max(maxr, r.right); minl = Math.min(minl, r.left); });
   const imgs = [...document.querySelectorAll('.shot img')].map(i => ({nat: i.naturalHeight / i.naturalWidth, w: i.clientWidth, h: i.clientHeight, par: i.parentElement.clientHeight}));
   const shots = [...document.querySelectorAll('.shot')].map(s => s.getBoundingClientRect().bottom + 8);
   return { band, maxb, maxr, minl, imgs, shotsBottom: Math.max(0, ...shots), wm: document.querySelectorAll('.swm,.wm').length }; })); }
 console.log(JSON.stringify(out)); await b.close(); })();
