// Valentine card + gift tag geometry and SVG (all units mm). Used by build.js (PDFs) and listing.js (listing photos).
const fs = require('fs'), path = require('path'), { execSync } = require('child_process');
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f7eddb', ROSE = '#c7455b', BLUSH = '#f6dcdc', PINK = '#ecb4b8', SAGE = '#a3ad98', MIST = '#e9ecde', DEEP = '#5a1f3a';
const FONT = f => `data:font/ttf;base64,${fs.readFileSync(path.join(__dirname, 'fonts', f)).toString('base64')}`;
const fontCSS = `
@font-face{font-family:Fr;font-weight:700;src:url(${FONT('Fraunces-700.ttf')})}
@font-face{font-family:Fr;font-weight:900;src:url(${FONT('Fraunces-900.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${FONT('Nunito-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${FONT('Nunito-800.ttf')})}`;
const CW = 95.25, CH = 127;      // card 3.75 x 5 in
const TW = 57.15, TH = 82.55;    // tag 2.25 x 3.25 in
const MOTIFS = ['lovebirds', 'dove', 'bluebird', 'bunny', 'hedgehog', 'fox', 'heartwreath', 'rose', 'peony', 'tulips', 'fernheart', 'posy'];
const motifData = {}, dims = {};
for (const m of MOTIFS) {
  const f = path.join(__dirname, 'art/motifs', m + '.png');
  motifData[m] = 'data:image/png;base64,' + fs.readFileSync(f).toString('base64');
  dims[m] = execSync(`python3 -c "from PIL import Image;print(*Image.open('${f}').size)"`).toString().trim().split(' ').map(Number);
}
const PATS = {
  ginR: { t: 'gingham', base: CREAM, a: ROSE }, ginB: { t: 'gingham', base: CREAM, a: BERRY }, ginS: { t: 'gingham', base: CREAM, a: PINE },
  tarB: { t: 'tartan', base: BERRY, a: DEEP, b: GOLD }, tarP: { t: 'tartan', base: PLUM, a: ROSE, b: GOLD }, tarS: { t: 'tartan', base: PINE, a: BERRY, b: GOLD },
  strR: { t: 'stripe', base: BLUSH, a: ROSE }, strB: { t: 'stripe', base: CREAM, a: BERRY }, strS: { t: 'stripe', base: MIST, a: SAGE },
  dotR: { t: 'dots', base: ROSE, a: CREAM }, dotP: { t: 'dots', base: DEEP, a: PINK }, dotS: { t: 'dots', base: PINE, a: BLUSH },
};
const CARDS = [
  { m: 'lovebirds', g: 'Be Mine', s: 'Happy Valentine’s Day', p: 'ginR', bg: BLUSH },
  { m: 'dove', g: 'Peace & Love', s: 'Happy Valentine’s Day', p: 'tarP', bg: CREAM },
  { m: 'heartwreath', g: 'With All My Heart', s: 'Happy Valentine’s Day', p: 'strR', bg: MIST },
  { m: 'fox', g: 'You’re Fox-y', s: 'Happy Valentine’s Day', p: 'dotR', bg: CREAM },
  { m: 'bunny', g: 'Some Bunny Loves You', s: 'Happy Valentine’s Day', p: 'ginS', bg: BLUSH },
  { m: 'peony', g: 'Sweet as Can Be', s: 'Happy Valentine’s Day', p: 'tarB', bg: CREAM },
  { m: 'hedgehog', g: 'Stuck on You', s: 'Happy Valentine’s Day', p: 'strS', bg: BLUSH },
  { m: 'tulips', g: 'Thinking of You', s: 'Happy Valentine’s Day', p: 'dotP', bg: MIST },
];
const TAGS = [
  { m: 'lovebirds', g: 'Be Mine', p: 'ginR', bg: BLUSH }, { m: 'dove', g: 'Love You', p: 'tarP', bg: CREAM }, { m: 'bluebird', g: 'Tweet Heart', p: 'strB', bg: MIST },
  { m: 'bunny', g: 'Hop to It', p: 'ginS', bg: BLUSH }, { m: 'hedgehog', g: 'Stuck on You', p: 'dotP', bg: CREAM }, { m: 'fox', g: 'Foxy Valentine', p: 'tarB', bg: MIST },
  { m: 'heartwreath', g: 'Sweetheart', p: 'strR', bg: CREAM }, { m: 'rose', g: 'Roses for You', p: 'dotR', bg: BLUSH }, { m: 'peony', g: 'Pretty Please', p: 'ginB', bg: CREAM },
  { m: 'tulips', g: 'Just Because', p: 'tarS', bg: BLUSH }, { m: 'fernheart', g: 'Heart & Soul', p: 'strS', bg: CREAM }, { m: 'posy', g: 'Be My Valentine', p: 'dotS', bg: BLUSH },
  { m: 'lovebirds', g: 'Happy Valentine’s', p: 'tarB', bg: CREAM }, { m: 'heartwreath', g: 'Be Mine', p: 'ginB', bg: MIST }, { m: 'rose', g: 'To My Love', p: 'tarP', bg: CREAM },
  { m: 'dove', g: 'Peace & Love', p: 'dotR', bg: BLUSH }, { m: 'posy', g: 'For You', p: 'strB', bg: MIST }, { m: 'fox', g: 'Love You', p: 'ginR', bg: CREAM },
];
function patternDef(id, p) {
  if (p.t === 'gingham') return `<pattern id="${id}" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="${p.base}"/><rect width="3" height="6" fill="${p.a}" opacity=".5"/><rect width="6" height="3" fill="${p.a}" opacity=".5"/></pattern>`;
  if (p.t === 'stripe') return `<pattern id="${id}" width="5" height="5" patternUnits="userSpaceOnUse"><rect width="5" height="5" fill="${p.base}"/><rect width="2.5" height="5" fill="${p.a}"/></pattern>`;
  if (p.t === 'dots') return `<pattern id="${id}" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="${p.base}"/><circle cx="1.5" cy="1.5" r=".8" fill="${p.a}"/><circle cx="4.5" cy="4.5" r=".8" fill="${p.a}"/></pattern>`;
  return `<pattern id="${id}" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="14" height="14" fill="${p.base}"/><rect width="5.5" height="14" fill="${p.a}" opacity=".62"/><rect width="14" height="5.5" fill="${p.a}" opacity=".62"/><rect x="8" width=".9" height="14" fill="${p.b}" opacity=".9"/><rect y="8" width="14" height=".9" fill="${p.b}" opacity=".9"/><rect x="11" width=".4" height="14" fill="${CREAM}" opacity=".5"/><rect y="11" width="14" height=".4" fill="${CREAM}" opacity=".5"/></pattern>`;
}
function motifDefs() { return `<svg width="0" height="0" style="position:absolute"><defs>${MOTIFS.map(m => `<image id="m-${m}" href="${motifData[m]}" width="${dims[m][0]}" height="${dims[m][1]}"/>`).join('')}</defs></svg>`; }
const fit = (m, bx, by, bw, bh) => { const [iw, ih] = dims[m], sc = Math.min(bw / iw, bh / ih); return `translate(${(bx + (bw - iw * sc) / 2).toFixed(2)} ${(by + (bh - ih * sc) / 2).toFixed(2)}) scale(${sc.toFixed(5)})`; };
const GREY = '#a79bad';
function cardSVG(d, uid, opts = {}) {
  const p = PATS[d.p], pid = `p${uid}`, cut = opts.cut !== false, rr = 4, B = 8;
  const line = (y, x0 = 16, x1 = CW - 16) => `<path d="M${x0} ${y}H${x1}" stroke="${PLUM}" stroke-width=".3" opacity=".85"/>`;
  const gsz = d.g.length > 16 ? 6.2 : 7.4;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${CW} ${CH}" width="${CW}mm" height="${CH}mm" style="display:block;overflow:visible">
  <defs>${patternDef(pid, p)}<clipPath id="c${uid}"><rect width="${CW}" height="${CH}" rx="${rr}"/></clipPath></defs>
  <rect width="${CW}" height="${CH}" rx="${rr}" fill="${d.bg}"/>
  <g clip-path="url(#c${uid})"><rect width="${CW}" height="${B}" fill="url(#${pid})"/><rect y="${CH - B}" width="${CW}" height="${B}" fill="url(#${pid})"/></g>
  <path d="M0 ${B}H${CW}M0 ${CH - B}H${CW}" stroke="${PLUM}" stroke-width=".35"/><path d="M0 ${B + 1}H${CW}M0 ${CH - B - 1}H${CW}" stroke="${GOLD}" stroke-width=".4"/>
  <use href="#m-${d.m}" transform="${fit(d.m, 12, B + 5, CW - 24, 58)}"/>
  <text x="${CW / 2}" y="${B + 5 + 58 + 14}" text-anchor="middle" font-family="Fr" font-weight="900" font-size="${gsz}" fill="${BERRY}">${d.g}</text>
  <text x="${CW / 2}" y="${B + 5 + 58 + 21}" text-anchor="middle" font-family="Nu" font-weight="800" font-size="2.7" letter-spacing=".7" fill="${PINE}">${d.s.toUpperCase()}</text>
  <path d="M${CW / 2 - 7} ${B + 5 + 58 + 24.5}h14" stroke="${ROSE}" stroke-width=".55" stroke-linecap="round"/>
  <text x="16" y="${CH - B - 17.2}" font-family="Nu" font-weight="800" font-size="2.7" letter-spacing=".5" fill="${PLUM}">TO</text>${line(CH - B - 17.8, 24)}
  <text x="16" y="${CH - B - 8.2}" font-family="Nu" font-weight="800" font-size="2.7" letter-spacing=".5" fill="${PLUM}">FROM</text>${line(CH - B - 8.8, 30)}
  <rect x="2.6" y="2.6" width="${CW - 5.2}" height="${CH - 5.2}" rx="${rr - 1.3}" fill="none" stroke="${PLUM}" stroke-width=".28" opacity=".6"/>
  <rect width="${CW}" height="${CH}" rx="${rr}" fill="none" stroke="${cut ? GREY : 'none'}" stroke-width=".3"/></svg>`;
}
const tagPath = (c = 7) => `M${c} 0H${TW - c}L${TW} ${c}V${TH - 3.5}Q${TW} ${TH} ${TW - 3.5} ${TH}H3.5Q0 ${TH} 0 ${TH - 3.5}V${c}Z`;
function tagSVG(d, uid, opts = {}) {
  const p = PATS[d.p], pid = `p${uid}`, cut = opts.cut !== false, B = 15;
  const gsz = d.g.length > 13 ? 4.6 : 5.6;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${TW} ${TH}" width="${TW}mm" height="${TH}mm" style="display:block;overflow:visible">
  <defs>${patternDef(pid, p)}<clipPath id="c${uid}"><path d="${tagPath()}"/></clipPath></defs>
  <path d="${tagPath()}" fill="${d.bg}"/>
  <g clip-path="url(#c${uid})"><rect width="${TW}" height="${B}" fill="url(#${pid})"/></g>
  <path d="M0 ${B}H${TW}" stroke="${PLUM}" stroke-width=".3"/><path d="M0 ${B + .9}H${TW}" stroke="${GOLD}" stroke-width=".35"/>
  <circle cx="${TW / 2}" cy="7.2" r="3.9" fill="${CREAM}" stroke="${PLUM}" stroke-width=".3"/><circle cx="${TW / 2}" cy="7.2" r="2.1" fill="#fff" stroke="${GREY}" stroke-width=".3"/>
  <use href="#m-${d.m}" transform="${fit(d.m, 6, B + 4, TW - 12, 33)}"/>
  <text x="${TW / 2}" y="${B + 4 + 33 + 8}" text-anchor="middle" font-family="Fr" font-weight="900" font-size="${gsz}" fill="${BERRY}">${d.g}</text>
  <text x="7" y="${TH - 14.4}" font-family="Nu" font-weight="800" font-size="2.3" fill="${PLUM}">TO</text><path d="M13 ${TH - 15}H${TW - 7}" stroke="${PLUM}" stroke-width=".28" opacity=".85"/>
  <text x="7" y="${TH - 7.4}" font-family="Nu" font-weight="800" font-size="2.3" fill="${PLUM}">FROM</text><path d="M16.5 ${TH - 8}H${TW - 7}" stroke="${PLUM}" stroke-width=".28" opacity=".85"/>
  <path d="${tagPath()}" fill="none" stroke="${cut ? GREY : 'none'}" stroke-width=".3"/></svg>`;
}
module.exports = { PLUM, PINE, BERRY, GOLD, CREAM, ROSE, BLUSH, PINK, SAGE, MIST, DEEP, fontCSS, CW, CH, TW, TH, CARDS, TAGS, cardSVG, tagSVG, motifDefs, MOTIFS };
