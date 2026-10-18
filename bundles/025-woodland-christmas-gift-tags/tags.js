// Shared tag geometry + SVG (all units mm). Used by build.js (PDFs) and listing.js (listing photos).
const fs = require('fs'), path = require('path');
const PLUM = '#2c1b36', VIOLET = '#4a2c55', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf', KRAFT = '#c9a679';
const FONT = f => `data:font/ttf;base64,${fs.readFileSync(path.join(__dirname, 'fonts', f)).toString('base64')}`;
const fontCSS = `
@font-face{font-family:Fr;font-weight:700;src:url(${FONT('Fraunces-700.ttf')})}
@font-face{font-family:Fr;font-weight:900;src:url(${FONT('Fraunces-900.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${FONT('Nunito-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${FONT('Nunito-800.ttf')})}`;

const SIZES = { large: { w: 63.5, h: 101.6, name: 'Large', label: '2.5 x 4 in' }, small: { w: 44.45, h: 69.85, name: 'Small', label: '1.75 x 2.75 in' } };
const MOTIFS = ['fox', 'owl', 'stag', 'robin', 'hedgehog', 'rabbit', 'toadstools', 'pine', 'moth', 'holly', 'mistletoe', 'moon'];
const motifData = {};
for (const m of MOTIFS) { const f = path.join(__dirname, 'art/motifs', m + '.png'); const b = fs.readFileSync(f); motifData[m] = 'data:image/png;base64,' + b.toString('base64'); }
const dims = {}; // px sizes for aspect
const { execSync } = require('child_process');
for (const m of MOTIFS) { const o = execSync(`python3 -c "from PIL import Image;print(*Image.open('${path.join(__dirname, 'art/motifs', m + '.png')}').size)"`).toString().trim().split(' ').map(Number); dims[m] = o; }

// designs: motif, greeting, shape, pattern (large); the small set re-mixes shapes and patterns
const PATS = {
  tartanA: { t: 'tartan', base: PINE, a: BERRY, b: GOLD },
  tartanB: { t: 'tartan', base: PLUM, a: BERRY, b: GOLD },
  tartanC: { t: 'tartan', base: VIOLET, a: GOLD, b: CREAM },
  gingB: { t: 'gingham', base: CREAM, a: BERRY },
  gingP: { t: 'gingham', base: CREAM, a: PINE },
  stripeP: { t: 'stripe', base: PLUM, a: VIOLET },
  stripeK: { t: 'stripe', base: KRAFT, a: '#b8925f' },
  dotsPine: { t: 'dots', base: PINE, a: CREAM },
  dotsVio: { t: 'dots', base: VIOLET, a: GOLD },
  dotsPlum: { t: 'dots', base: PLUM, a: GOLD },
  solidBerry: { t: 'solid', base: BERRY },
  kraft: { t: 'solid', base: KRAFT },
};
const DESIGNS = [
  { m: 'fox', g: 'Merry Christmas', s: 'luggage', p: 'tartanA' },
  { m: 'owl', g: 'Happy Holidays', s: 'arch', p: 'dotsPlum' },
  { m: 'stag', g: 'Warm Wishes', s: 'round', p: 'kraft' },
  { m: 'robin', g: 'Joy to You', s: 'scallop', p: 'gingB' },
  { m: 'hedgehog', g: 'Cozy Christmas', s: 'bevel', p: 'dotsPine' },
  { m: 'rabbit', g: 'Season of Joy', s: 'luggage', p: 'gingP' },
  { m: 'toadstools', g: 'Merry and Bright', s: 'arch', p: 'tartanB' },
  { m: 'pine', g: 'Happy Holidays', s: 'round', p: 'stripeP' },
  { m: 'moth', g: 'Winter Wishes', s: 'bevel', p: 'dotsVio' },
  { m: 'holly', g: 'Merry Christmas', s: 'scallop', p: 'solidBerry' },
  { m: 'mistletoe', g: 'Peace and Joy', s: 'luggage', p: 'stripeK' },
  { m: 'moon', g: 'Peaceful Night', s: 'arch', p: 'tartanC' },
];
const SHAPES = ['luggage', 'arch', 'round', 'scallop', 'bevel'];
const PATKEYS = Object.keys(PATS);
const smallDesigns = DESIGNS.map((d, i) => ({ ...d, s: SHAPES[(SHAPES.indexOf(d.s) + 2) % 5], p: ['gingB', 'tartanB', 'stripeK', 'dotsVio', 'tartanA', 'solidBerry', 'gingP', 'dotsPlum', 'tartanC', 'kraft', 'stripeP', 'dotsPine'][i] }));

function shapePath(k, w, h) {
  const f = n => +n.toFixed(2);
  if (k === 'luggage') { const c = 11; return `M${c} 0H${w - c}L${w} ${c}V${h - 4}A4 4 0 0 1 ${w - 4} ${h}H4A4 4 0 0 1 0 ${h - 4}V${c}Z`; }
  if (k === 'arch') { const r = w / 2; return `M0 ${r}A${r} ${r} 0 0 1 ${w} ${r}V${h - 4}A4 4 0 0 1 ${w - 4} ${h}H4A4 4 0 0 1 0 ${h - 4}Z`; }
  if (k === 'round') return `M5 0H${w - 5}A5 5 0 0 1 ${w} 5V${h - 5}A5 5 0 0 1 ${w - 5} ${h}H5A5 5 0 0 1 0 ${h - 5}V5A5 5 0 0 1 5 0Z`;
  if (k === 'bevel') { const c = 11; return `M${c} 0H${w - c}L${w} ${c}V${h - 6}L${w - 6} ${h}H6L0 ${h - 6}V${c}Z`; }
  if (k === 'scallop') { const n = Math.round(w / 8), s = w / n / 2; let d = `M0 ${f(s)}`; for (let i = 0; i < n; i++) d += `A${f(s)} ${f(s)} 0 0 1 ${f((i + 1) * 2 * s)} ${f(s)}`; d += `V${f(h - s)}`; for (let i = 0; i < n; i++) d += `A${f(s)} ${f(s)} 0 0 1 ${f(w - (i + 1) * 2 * s)} ${f(h - s)}`; return d + 'Z'; }
}
function patternDef(id, p) {
  if (p.t === 'solid') return '';
  if (p.t === 'gingham') return `<pattern id="${id}" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="${p.base}"/><rect width="4" height="8" fill="${p.a}" opacity=".5"/><rect width="8" height="4" fill="${p.a}" opacity=".5"/></pattern>`;
  if (p.t === 'stripe') return `<pattern id="${id}" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="${p.base}"/><rect width="3" height="6" fill="${p.a}"/></pattern>`;
  if (p.t === 'dots') return `<pattern id="${id}" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="${p.base}"/><circle cx="2" cy="2" r=".85" fill="${p.a}"/><circle cx="6" cy="6" r=".85" fill="${p.a}"/></pattern>`;
  if (p.t === 'tartan') return `<pattern id="${id}" width="18" height="18" patternUnits="userSpaceOnUse"><rect width="18" height="18" fill="${p.base}"/><rect x="0" width="7" height="18" fill="${p.a}" opacity=".62"/><rect y="0" width="18" height="7" fill="${p.a}" opacity=".62"/><rect x="10" width="1.2" height="18" fill="${p.b}" opacity=".9"/><rect y="10" width="18" height="1.2" fill="${p.b}" opacity=".9"/><rect x="14" width=".5" height="18" fill="${CREAM}" opacity=".5"/><rect y="14" width="18" height=".5" fill="${CREAM}" opacity=".5"/></pattern>`;
}
const fillOf = (id, p) => p.t === 'solid' ? p.base : `url(#${id})`;
function motifDefs() { // once per document
  return `<svg width="0" height="0" style="position:absolute"><defs>${MOTIFS.map(m => `<image id="m-${m}" href="${motifData[m]}" width="${dims[m][0]}" height="${dims[m][1]}"/>`).join('')}</defs></svg>`;
}
const esc = s => s.replace(/&/g, '&amp;');
// returns an <svg> for one tag, in mm. kind = 'large' | 'small'. opts.cut = draw grey cut line
function tagSVG(d, kind, uid, opts = {}) {
  const { w, h } = SIZES[kind], big = kind === 'large';
  const p = PATS[d.p], pid = `p${uid}`;
  const hy = d.s === 'scallop' ? (big ? 11 : 8.5) : (big ? 9.5 : 7), hr = big ? 4.6 : 3.4, hole = big ? 2.6 : 2.0;
  const px = big ? 4 : 3, py = big ? 17 : 12.5, pb = big ? 5 : 3.6;
  const pw = w - 2 * px, ph = h - py - pb;
  const mb = big ? { x: px + 4, y: py + 3, w: pw - 8, h: 44 } : { x: px + 3, y: py + 2.5, w: pw - 6, h: 33 };
  const [iw, ih] = dims[d.m], sc = Math.min(mb.w / iw, mb.h / ih);
  const mw = iw * sc, mh = ih * sc, mx = mb.x + (mb.w - mw) / 2, my = mb.y + (mb.h - mh) / 2;
  let t = '';
  const lineX0 = px + (big ? 11 : 8), lineX1 = w - px - (big ? 4 : 3);
  const fs1 = big ? 3.3 : 2.6;
  if (big) {
    const gy = py + 3 + 44 + 6.5;
    t += `<text x="${w / 2}" y="${gy}" text-anchor="middle" font-family="Fr" font-weight="700" font-size="4.6" fill="${BERRY}">${esc(d.g)}</text>`;
    t += `<path d="M${w / 2 - 6} ${gy + 2.6}h12" stroke="${GOLD}" stroke-width=".6" stroke-linecap="round"/>`;
    for (const [k, lab] of [[0, 'To:'], [1, 'From:']]) { const y = gy + 11.5 + k * 9.2; t += `<text x="${px + 4}" y="${y}" font-family="Nu" font-weight="800" font-size="${fs1}" fill="${PLUM}">${lab}</text><path d="M${lineX0 + (k ? 3 : 0)} ${y + .4}H${lineX1}" stroke="${PLUM}" stroke-width=".3" opacity=".8"/>`; }
  } else {
    const y0 = py + 2.5 + 33 + 8.5;
    for (const [k, lab] of [[0, 'To:'], [1, 'From:']]) { const y = y0 + k * 8; t += `<text x="${px + 3}" y="${y}" font-family="Nu" font-weight="800" font-size="${fs1}" fill="${PLUM}">${lab}</text><path d="M${lineX0 + (k ? 3 : 0)} ${y + .4}H${lineX1}" stroke="${PLUM}" stroke-width=".28" opacity=".8"/>`; }
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${w} ${h}" width="${w}mm" height="${h}mm" style="display:block;overflow:visible">
  <defs>${patternDef(pid, p)}</defs>
  <path d="${shapePath(d.s, w, h)}" fill="${fillOf(pid, p)}" stroke="${opts.cut === false ? 'none' : '#a79bad'}" stroke-width=".3"/>
  <rect x="${px}" y="${py}" width="${pw}" height="${ph}" rx="3" fill="${CREAM}" stroke="${PLUM}" stroke-width=".35"/>
  <rect x="${px + 1.1}" y="${py + 1.1}" width="${pw - 2.2}" height="${ph - 2.2}" rx="2.2" fill="none" stroke="${GOLD}" stroke-width=".3"/>
  <circle cx="${w / 2}" cy="${hy}" r="${hr}" fill="${CREAM}" stroke="${PLUM}" stroke-width=".35"/>
  <circle cx="${w / 2}" cy="${hy}" r="${hole}" fill="#fff" stroke="#a79bad" stroke-width=".25" stroke-dasharray=".8 .6"/>
  <use href="#m-${d.m}" transform="translate(${mx.toFixed(2)} ${my.toFixed(2)}) scale(${sc.toFixed(5)})"/>
  ${t}</svg>`;
}
module.exports = { PLUM, VIOLET, PINE, BERRY, GOLD, CREAM, KRAFT, fontCSS, SIZES, DESIGNS, smallDesigns, tagSVG, motifDefs, MOTIFS };
