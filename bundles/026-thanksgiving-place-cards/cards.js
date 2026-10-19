// Shared tent-card geometry + SVG (all units mm). Used by build.js (PDFs) and listing.js (listing photos).
const fs = require('fs'), path = require('path');
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf', RUSSET = '#b4542a', OCHRE = '#d99b3a', OLIVE = '#6b6b3a', SAGE = '#e7e5c9', APRICOT = '#f5dfc4';
const FONT = f => `data:font/ttf;base64,${fs.readFileSync(path.join(__dirname, 'fonts', f)).toString('base64')}`;
const fontCSS = `
@font-face{font-family:Fr;font-weight:700;src:url(${FONT('Fraunces-700.ttf')})}
@font-face{font-family:Fr;font-weight:900;src:url(${FONT('Fraunces-900.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${FONT('Nunito-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${FONT('Nunito-800.ttf')})}`;
const W = 88.9, H = 101.6, FOLD = 50.8; // flat card 3.5 x 4 in, folds to 3.5 x 2 in
const MOTIFS = ['fox', 'hedgehog', 'squirrel', 'owl', 'turkey', 'deer', 'acorns', 'oakleaf', 'wheat', 'mushrooms', 'maple', 'apple'];
const motifData = {}, dims = {};
const { execSync } = require('child_process');
for (const m of MOTIFS) {
  const f = path.join(__dirname, 'art/motifs', m + '.png');
  motifData[m] = 'data:image/png;base64,' + fs.readFileSync(f).toString('base64');
  dims[m] = execSync(`python3 -c "from PIL import Image;print(*Image.open('${f}').size)"`).toString().trim().split(' ').map(Number);
}
const PATS = {
  tartanA: { t: 'tartan', base: PLUM, a: RUSSET, b: OCHRE },
  tartanB: { t: 'tartan', base: OLIVE, a: BERRY, b: GOLD },
  tartanC: { t: 'tartan', base: BERRY, a: PLUM, b: OCHRE },
  gingR: { t: 'gingham', base: CREAM, a: RUSSET },
  gingO: { t: 'gingham', base: CREAM, a: OLIVE },
  gingB: { t: 'gingham', base: CREAM, a: BERRY },
  stripeA: { t: 'stripe', base: RUSSET, a: BERRY },
  stripeO: { t: 'stripe', base: OCHRE, a: RUSSET },
  dotsP: { t: 'dots', base: PLUM, a: OCHRE },
  dotsO: { t: 'dots', base: OLIVE, a: CREAM },
  dotsB: { t: 'dots', base: BERRY, a: GOLD },
  dotsR: { t: 'dots', base: RUSSET, a: CREAM },
};
const DESIGNS = [
  { m: 'fox', g: 'Gather Round', p: 'tartanA', bg: CREAM },
  { m: 'hedgehog', g: 'Cozy Table', p: 'gingO', bg: SAGE },
  { m: 'squirrel', g: 'Thankful', p: 'dotsR', bg: APRICOT },
  { m: 'owl', g: 'Grateful', p: 'stripeO', bg: CREAM },
  { m: 'turkey', g: 'Give Thanks', p: 'tartanB', bg: APRICOT },
  { m: 'deer', g: 'Welcome', p: 'gingR', bg: SAGE },
  { m: 'acorns', g: 'Harvest Home', p: 'dotsP', bg: CREAM },
  { m: 'oakleaf', g: 'Count Blessings', p: 'tartanC', bg: SAGE },
  { m: 'wheat', g: 'Bountiful', p: 'gingB', bg: CREAM },
  { m: 'mushrooms', g: 'Forest Feast', p: 'dotsO', bg: APRICOT },
  { m: 'maple', g: 'Autumn Gathering', p: 'stripeA', bg: SAGE },
  { m: 'apple', g: 'Sweet Season', p: 'dotsB', bg: CREAM },
];
const MENUS = [
  { m: 'turkey', title: 'Mains', p: 'tartanA', bg: CREAM },
  { m: 'wheat', title: 'Sides', p: 'gingO', bg: SAGE },
  { m: 'apple', title: 'Desserts', p: 'dotsR', bg: APRICOT },
  { m: 'acorns', title: 'Drinks', p: 'stripeO', bg: CREAM },
];
function patternDef(id, p) {
  if (p.t === 'gingham') return `<pattern id="${id}" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="${p.base}"/><rect width="3" height="6" fill="${p.a}" opacity=".55"/><rect width="6" height="3" fill="${p.a}" opacity=".55"/></pattern>`;
  if (p.t === 'stripe') return `<pattern id="${id}" width="5" height="5" patternUnits="userSpaceOnUse"><rect width="5" height="5" fill="${p.base}"/><rect width="2.5" height="5" fill="${p.a}"/></pattern>`;
  if (p.t === 'dots') return `<pattern id="${id}" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="${p.base}"/><circle cx="1.5" cy="1.5" r=".8" fill="${p.a}"/><circle cx="4.5" cy="4.5" r=".8" fill="${p.a}"/></pattern>`;
  if (p.t === 'tartan') return `<pattern id="${id}" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="14" height="14" fill="${p.base}"/><rect width="5.5" height="14" fill="${p.a}" opacity=".62"/><rect width="14" height="5.5" fill="${p.a}" opacity=".62"/><rect x="8" width=".9" height="14" fill="${p.b}" opacity=".9"/><rect y="8" width="14" height=".9" fill="${p.b}" opacity=".9"/><rect x="11" width=".4" height="14" fill="${CREAM}" opacity=".5"/><rect y="11" width="14" height=".4" fill="${CREAM}" opacity=".5"/></pattern>`;
}
function motifDefs() {
  return `<svg width="0" height="0" style="position:absolute"><defs>${MOTIFS.map(m => `<image id="m-${m}" href="${motifData[m]}" width="${dims[m][0]}" height="${dims[m][1]}"/>`).join('')}</defs></svg>`;
}
const fit = (m, bx, by, bw, bh) => { const [iw, ih] = dims[m], sc = Math.min(bw / iw, bh / ih); return `translate(${(bx + (bw - iw * sc) / 2).toFixed(2)} ${(by + (bh - ih * sc) / 2).toFixed(2)}) scale(${sc.toFixed(5)})`; };
const BAND = 9; // pattern band centred on the fold
// content of the lower (front) panel, absolute card coordinates
function panel(d, kind) {
  const by = FOLD + BAND / 2; // 56.8
  const line = (y, x0 = 14, x1 = W - 14) => `<path d="M${x0} ${y}H${x1}" stroke="${PLUM}" stroke-width=".32" opacity=".85"/>`;
  if (kind === 'menu') {
    return `<use href="#m-${d.m}" transform="${fit(d.m, 30, by + 2, W - 60, 13)}"/>
    <text x="${W / 2}" y="${by + 23.5}" text-anchor="middle" font-family="Fr" font-weight="900" font-size="7.4" fill="${BERRY}">${d.title}</text>
    <path d="M${W / 2 - 7} ${by + 26}h14" stroke="${OCHRE}" stroke-width=".6" stroke-linecap="round"/>${line(by + 33)}${line(by + 39.2)}`;
  }
  return `<use href="#m-${d.m}" transform="${fit(d.m, 16, by + 2, W - 32, 25)}"/>
    <text x="${W / 2}" y="${by + 32}" text-anchor="middle" font-family="Nu" font-weight="800" font-size="3.1" letter-spacing=".75" fill="${PINE}">${d.g.toUpperCase()}</text>${line(by + 39.4)}`;
}
// full flat card; opts.cut false = no cut/fold marks (listing photos)
function cardSVG(d, kind, uid, opts = {}) {
  const p = PATS[d.p], pid = `p${uid}`, cut = opts.cut !== false;
  const rr = 3.6, r2 = rr - 1.3;
  const ticks = cut ? `<path d="M-4.5 ${FOLD}H-1M${W + 1} ${FOLD}H${W + 4.5}" stroke="#a79bad" stroke-width=".35"/>` : '';
  const content = panel(d, kind);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}mm" height="${H}mm" style="display:block;overflow:visible">
  <defs>${patternDef(pid, p)}<clipPath id="c${uid}"><rect width="${W}" height="${H}" rx="${rr}"/></clipPath></defs>
  <rect width="${W}" height="${H}" rx="${rr}" fill="${d.bg}"/>
  <g clip-path="url(#c${uid})"><rect y="${FOLD - BAND / 2}" width="${W}" height="${BAND}" fill="url(#${pid})"/></g>
  <path d="M0 ${FOLD - BAND / 2}H${W}M0 ${FOLD + BAND / 2}H${W}" stroke="${PLUM}" stroke-width=".35"/>
  <path d="M0 ${FOLD - BAND / 2 - 1}H${W}M0 ${FOLD + BAND / 2 + 1}H${W}" stroke="${GOLD}" stroke-width=".4"/>
  <rect x="2.6" y="2.6" width="${W - 5.2}" height="${H - 5.2}" rx="${r2}" fill="none" stroke="${PLUM}" stroke-width=".3" opacity=".7"/>
  <rect x="2.6" y="2.6" width="${W - 5.2}" height="${H - 5.2}" rx="${r2}" fill="none" stroke="${GOLD}" stroke-width=".3" stroke-dasharray="0" opacity="0"/>
  ${content}
  <g transform="rotate(180 ${W / 2} ${H / 2})">${content}</g>
  <rect width="${W}" height="${H}" rx="${rr}" fill="none" stroke="${cut ? '#a79bad' : 'none'}" stroke-width=".3"/>
  ${cut ? `<path d="M0 ${FOLD}H${W}" stroke="#fff" stroke-width=".35" stroke-dasharray="1.6 1.2" opacity=".9"/><path d="M0 ${FOLD}H${W}" stroke="#a79bad" stroke-width=".18" stroke-dasharray="1.6 1.2" stroke-dashoffset="1.4" opacity=".0"/>` : ''}${ticks}</svg>`;
}
module.exports = { PLUM, PINE, BERRY, GOLD, CREAM, RUSSET, OCHRE, OLIVE, SAGE, APRICOT, fontCSS, W, H, FOLD, DESIGNS, MENUS, cardSVG, motifDefs, MOTIFS };
