// Builds the pattern PDFs from motifs.json. Run from this folder: NODE_PATH=$(npm root -g) node build.js
//   bundle/woodland-christmas-cross-stitch-{US-Letter,A4}.pdf, 28 pages each:
//     1 cover, 2 contents + all motifs, 3 how to stitch & finish as an ornament, 4 floss shopping list,
//     5-16 colour charts (one per motif), 17-28 one-colour charts (DMC 3371)
// Symbols are drawn as SVG paths (no symbol font needed). Fails if any text box overflows.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const D = JSON.parse(fs.readFileSync('motifs.json', 'utf8'));
const PLUM = '#2c1b36', PINE = '#2f4a3a', BERRY = '#8b2f3c', GOLD = '#e8c97a', CREAM = '#f1e6cf', MUTED = '#6d5f73';
const FONT = f => `data:font/ttf;base64,${fs.readFileSync(path.join('fonts', f)).toString('base64')}`;
const SHOP = 'Duskwood Designs Co';
const PAL = D.palette, MONO = D.mono, SPS = D.stitches_per_skein;
const SLUG = 'woodland-christmas-cross-stitch';
const RG = D.ranges;

// ---- symbols, in a 1x1 cell (stroke widths in cell units)
function symbol(id, x, y, col) {
  const c = (a, b) => `${(x + a).toFixed(3)} ${(y + b).toFixed(3)}`;
  const sw = 0.11, st = `fill="none" stroke="${col}" stroke-width="${sw}" stroke-linejoin="round" stroke-linecap="round"`;
  switch (id) {
    case 'dot': return `<circle cx="${x + .5}" cy="${y + .5}" r=".27" fill="${col}"/>`;
    case 'ocircle': return `<circle cx="${x + .5}" cy="${y + .5}" r=".26" ${st}/>`;
    case 'diamond': return `<path d="M${c(.5, .18)}L${c(.82, .5)}L${c(.5, .82)}L${c(.18, .5)}Z" fill="${col}"/>`;
    case 'odiamond': return `<path d="M${c(.5, .18)}L${c(.82, .5)}L${c(.5, .82)}L${c(.18, .5)}Z" ${st}/>`;
    case 'tri': return `<path d="M${c(.5, .2)}L${c(.82, .78)}L${c(.18, .78)}Z" fill="${col}"/>`;
    case 'otri': return `<path d="M${c(.5, .22)}L${c(.8, .76)}L${c(.2, .76)}Z" ${st}/>`;
    case 'cross': return `<path d="M${c(.24, .24)}L${c(.76, .76)}M${c(.76, .24)}L${c(.24, .76)}" ${st} stroke-width=".13"/>`;
    case 'hsquare': return `<rect x="${x + .22}" y="${y + .22}" width=".56" height=".56" ${st}/><path d="M${c(.22, .22)}L${c(.78, .78)}L${c(.22, .78)}Z" fill="${col}"/>`;
    case 'plus': return `<path d="M${c(.5, .2)}L${c(.5, .8)}M${c(.2, .5)}L${c(.8, .5)}" ${st} stroke-width=".13"/>`;
    case 'osquare': return `<rect x="${x + .25}" y="${y + .25}" width=".5" height=".5" ${st}/>`;
    case 'star': {
      let p = ''; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, r = i % 2 ? .15 : .34; p += (i ? 'L' : 'M') + c(.5 + r * Math.cos(a), .53 + r * Math.sin(a)); }
      return `<path d="${p}Z" fill="${col}"/>`;
    }
  }
  throw new Error('symbol ' + id);
}
const lum = hex => { const n = parseInt(hex.slice(1), 16); return (0.299 * (n >> 16) + 0.587 * (n >> 8 & 255) + 0.114 * (n & 255)) / 255; };
const ink = hex => lum(hex) < 0.5 ? '#ffffff' : '#1e1108';
const MONO_FILL = '#e6dfe8';
const swatch = (sym, fill, size = 6) => `<svg viewBox="0 0 1 1" style="width:${size}mm;height:${size}mm;display:block;border:0.25mm solid #8a7f8f"><rect width="1" height="1" fill="${fill}"/>${symbol(sym, 0, 0, fill === '#ffffff' ? '#1e1108' : ink(fill))}</svg>`;

// ---- small preview (colour squares, or "stitched" look) in an SVG of given width
function preview(m, mono, opts = {}) {
  const g = mono ? m.mono : m.colour;
  let s = '';
  g.forEach((r, y) => [...r].forEach((ch, x) => {
    if (ch === '.') return;
    const col = mono ? MONO.hex : PAL[ch].hex;
    s += `<rect x="${x}" y="${y}" width="1.02" height="1.02" fill="${col}"/>`;
  }));
  return `<svg viewBox="-0.5 -0.5 ${m.w + 1} ${m.h + 1}" style="${opts.style || ''}" preserveAspectRatio="xMidYMid meet">${s}</svg>`;
}

// ---- the chart
function chart(m, mono, cell) {
  const g = mono ? m.mono : m.colour, W = m.w, H = m.h;
  const lab = 7 / cell; // label band (in cells) on top/left
  const arr = 2.6 / cell; // arrow band on bottom/right
  let s = '';
  // cells
  g.forEach((r, y) => [...r].forEach((ch, x) => {
    if (ch === '.') return;
    if (mono) { s += `<rect x="${x}" y="${y}" width="1" height="1" fill="${MONO_FILL}"/>` + symbol(MONO.symbol, x, y, '#1e1108'); }
    else { const p = PAL[ch]; s += `<rect x="${x}" y="${y}" width="1" height="1" fill="${p.hex}"/>` + symbol(p.symbol, x, y, ink(p.hex)); }
  }));
  // grid lines
  const thin = 0.15 / cell, bold = 0.5 / cell;
  for (let x = 0; x <= W; x++) if (x % 10) s += `<line x1="${x}" y1="0" x2="${x}" y2="${H}" stroke="#9c939f" stroke-width="${thin}"/>`;
  for (let y = 0; y <= H; y++) if (y % 10) s += `<line x1="0" y1="${y}" x2="${W}" y2="${y}" stroke="#9c939f" stroke-width="${thin}"/>`;
  for (let x = 0; x <= W; x += 10) s += `<line x1="${x}" y1="0" x2="${x}" y2="${H}" stroke="${PLUM}" stroke-width="${bold}"/>`;
  for (let y = 0; y <= H; y += 10) s += `<line x1="0" y1="${y}" x2="${W}" y2="${y}" stroke="${PLUM}" stroke-width="${bold}"/>`;
  s += `<rect x="0" y="0" width="${W}" height="${H}" fill="none" stroke="${PLUM}" stroke-width="${bold}"/>`;
  // numbers: every 5 on top and left (bold at 10s)
  const fs_ = 2.5 / cell;
  for (let x = 5; x <= W; x += 5) s += `<text x="${x - 0.5}" y="${-0.9 / cell - 0.15}" font-size="${fs_}" text-anchor="middle" font-family="Nu" font-weight="${x % 10 ? 400 : 800}" fill="${PLUM}">${x}</text>`;
  for (let y = 5; y <= H; y += 5) s += `<text x="${-1.2 / cell}" y="${y - 0.5 + fs_ * 0.35}" font-size="${fs_}" text-anchor="end" font-family="Nu" font-weight="${y % 10 ? 400 : 800}" fill="${PLUM}">${y}</text>`;
  // centre arrows on all four sides
  const cx = W / 2, cy = H / 2, a = 1.9 / cell, gap = 0.6 / cell;
  const tri = (pts) => `<path d="M${pts.map(p => p.map(v => v.toFixed(3)).join(' ')).join('L')}Z" fill="${BERRY}"/>`;
  s += tri([[cx - a, -gap - a * 1.5 - lab * 0.55], [cx + a, -gap - a * 1.5 - lab * 0.55], [cx, -gap - lab * 0.55]]);
  s += tri([[cx - a, H + gap + a * 1.5], [cx + a, H + gap + a * 1.5], [cx, H + gap]]);
  s += tri([[-gap - a * 1.5 - lab * 0.55, cy - a], [-gap - a * 1.5 - lab * 0.55, cy + a], [-gap - lab * 0.55, cy]]);
  s += tri([[W + gap + a * 1.5, cy - a], [W + gap + a * 1.5, cy + a], [W + gap, cy]]);
  const vx = -lab - 0.2, vy = -lab - 0.2, vw = W + lab + arr + 0.4, vh = H + lab + arr + 0.4;
  return `<svg class=chart viewBox="${vx} ${vy} ${vw} ${vh}" style="width:${vw * cell}mm;height:${vh * cell}mm">${s}</svg>`;
}

const fontCSS = `
@font-face{font-family:Fr;font-weight:700;src:url(${FONT('Fraunces-700.ttf')})}
@font-face{font-family:Fr;font-weight:900;src:url(${FONT('Fraunces-900.ttf')})}
@font-face{font-family:Nu;font-weight:400;src:url(${FONT('Nunito-400.ttf')})}
@font-face{font-family:Nu;font-weight:700;src:url(${FONT('Nunito-700.ttf')})}
@font-face{font-family:Nu;font-weight:800;src:url(${FONT('Nunito-800.ttf')})}`;

const css = (W, H) => `${fontCSS}
@page{size:${W}mm ${H}mm;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:Nu;color:${PLUM};-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:${W}mm;height:${H}mm;position:relative;overflow:hidden;page-break-after:always;background:#fff}
.frame{position:absolute;inset:9mm;border:0.5mm solid ${PLUM};border-radius:4mm}
.frame::after{content:'';position:absolute;inset:1.3mm;border:0.2mm solid ${PINE};border-radius:3mm}
.kick{font-weight:800;font-size:3mm;letter-spacing:1mm;color:${PINE};text-transform:uppercase}
h1{font-family:Fr;font-weight:900;margin:0;color:${PLUM};line-height:1.1}
h1 em,h2 em{font-style:normal;color:${BERRY}}
h2{font-family:Fr;font-weight:700;font-size:5.2mm;margin:0 0 1.6mm;color:${BERRY}}
p,li{font-size:3.75mm;line-height:1.42;margin:0 0 1.8mm}
ul,ol{margin:0 0 2mm;padding-left:5mm}
.foot{position:absolute;left:0;right:0;bottom:11.5mm;text-align:center;font-size:2.4mm;color:${MUTED}}
/* cover */
.cover{background:${CREAM}}
.cover .head{position:absolute;top:22mm;left:16mm;right:16mm;text-align:center}
.cover h1{font-size:14mm;margin-top:2mm;line-height:1.3}
.cover .sub{font-size:4mm;font-weight:700;color:${PINE};margin-top:3mm}
.orn{position:absolute;display:grid;grid-template-columns:repeat(4,1fr);gap:5mm 4mm}
.orn .o{aspect-ratio:1;border-radius:50%;background:#fbf8f0;border:0.8mm solid ${GOLD};display:flex;align-items:center;justify-content:center;position:relative;box-shadow:0 0 0 0.35mm ${PLUM}}
.orn .o::before{content:'';position:absolute;top:-3.2mm;left:50%;width:0.4mm;height:3mm;background:${BERRY}}
.orn svg{width:64%;height:64%}
.badges{position:absolute;left:16mm;right:16mm;display:flex;justify-content:center;gap:3mm;flex-wrap:wrap}
.badges span{background:${PLUM};color:${CREAM};font-weight:800;font-size:3mm;padding:1.4mm 3.2mm;border-radius:5mm;letter-spacing:.3mm}
/* contents */
.ctop{position:absolute;top:15mm;left:16mm;right:16mm}
.ctop h1{font-size:9mm}
.grid12{position:absolute;left:15mm;right:15mm;display:grid;grid-template-columns:repeat(3,1fr);gap:3mm}
.grid12 .m{border:0.3mm solid #d8cfdb;border-radius:2.5mm;padding:2mm 2mm 1.6mm;display:flex;flex-direction:column}
.grid12 .pv{display:flex;gap:2mm;justify-content:center;align-items:center;flex:1;min-height:0}
.grid12 .pv svg{width:46%;height:100%}
.grid12 b{font-family:Fr;font-weight:700;font-size:3.6mm;display:block;margin-top:1.2mm;white-space:nowrap}
.grid12 span{font-size:2.6mm;color:${MUTED};display:block}
/* text pages */
.txt{position:absolute;top:15mm;left:17mm;right:17mm;bottom:17mm;overflow:hidden}
.txt h1{font-size:8.5mm;margin-bottom:4mm}
.two{display:grid;grid-template-columns:1fr 1fr;column-gap:7mm}
.note{background:#f6f1e6;border-left:1.2mm solid ${GOLD};padding:2.4mm 3mm;border-radius:1.5mm;margin:1mm 0 3mm}
table{border-collapse:collapse;width:100%;font-size:3.2mm}
th{text-align:left;font-size:2.6mm;letter-spacing:.4mm;text-transform:uppercase;color:${PINE};border-bottom:0.4mm solid ${PLUM};padding:1.2mm 1.5mm}
td{border-bottom:0.2mm solid #e2dbe4;padding:1.1mm 1.5mm;vertical-align:middle}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.chk{display:inline-block;width:3.6mm;height:3.6mm;border:0.35mm solid ${PLUM};border-radius:.8mm;vertical-align:middle}
/* chart pages */
.chead{position:absolute;top:11mm;left:14mm;right:14mm;display:flex;align-items:flex-end;justify-content:space-between;border-bottom:0.4mm solid ${PLUM};padding-bottom:1.6mm}
.chead h1{font-size:7.4mm;white-space:nowrap}
.chead .r{text-align:right;font-size:2.8mm;color:${MUTED};line-height:1.35}
.chartbox{position:absolute;left:12mm;right:12mm;display:flex;align-items:center;justify-content:center}
.info{position:absolute;left:14mm;right:14mm;display:grid;grid-template-columns:62mm 1fr;column-gap:6mm;border-top:0.3mm solid #d8cfdb;padding-top:3mm}
.info .facts p{font-size:3.05mm;margin:0 0 1.2mm;line-height:1.35}
.info .facts b{color:${PLUM}}
.info table{font-size:2.95mm}.info td{padding:.8mm 1.4mm}.info th{padding:.8mm 1.4mm;font-size:2.4mm}
.keysw{width:6mm}
`;

const pageNo = { cover: 1, contents: 2, how: 3, shop: 4, colour: n => 4 + n, mono: n => 16 + n };
const sz = (n, c) => `${(n / c).toFixed(1)} in (${(n / c * 2.54).toFixed(1)} cm)`;
const skeinTxt = n => `1 (uses ${Math.max(1, Math.round(n / SPS * 100))}%)`;

function cover(W, H) {
  const top = 80, gw = W - 54;
  return `<div class="page cover"><div class=frame></div>
  <div class=head><div class=kick>Counted cross stitch pattern · pdf</div><h1>Woodland <em>Christmas</em></h1>
  <div class=sub>12 mini ornaments · colour and one-colour charts</div></div>
  <div class=orn style="left:27mm;width:${gw}mm;top:${top}mm">${D.motifs.map(m => `<div class=o>${preview(m, false)}</div>`).join('')}</div>
  <div class=badges style="top:${H - 58}mm"><span>12 CHARTS × 2 VERSIONS</span><span>${RG.in14.toUpperCase()} ON 14-COUNT</span><span>US LETTER + A4</span></div>
  <div class=foot>© ${SHOP} · personal use pattern · finished pieces may be sold in small quantities (see README)</div></div>`;
}

function contents(W, H) {
  const top = 43, bottom = 20;
  const rows = 4, cellH = (H - top - bottom - 3 * 3) / rows;
  return `<div class=page><div class=frame></div>
  <div class=ctop><div class=kick>Contents</div><h1>All 12 <em>ornaments</em></h1>
  <p style="margin-top:1.5mm;font-size:3.1mm">Page 3: how to stitch &amp; finish · page 4: floss shopping list · colour charts pp 5–16 · one-colour charts pp 17–28</p></div>
  <div class=grid12 style="top:${top}mm;grid-auto-rows:${cellH}mm">${D.motifs.map(m => `<div class=m><div class=pv>${preview(m, false, { style: 'height:100%' })}${preview(m, true, { style: 'height:100%' })}</div>
    <b>${m.n}. ${m.title}</b><span>${m.w} × ${m.h} stitches · ${Object.keys(m.counts).length} colours · pp ${pageNo.colour(m.n)} / ${pageNo.mono(m.n)}</span></div>`).join('')}</div>
  <div class=foot>© ${SHOP} · Woodland Christmas mini ornaments</div></div>`;
}

function how(W, H) {
  return `<div class=page><div class=frame></div><div class=txt>
  <div class=kick>Before you start</div><h1>How to stitch &amp; <em>finish as an ornament</em></h1>
  <div class=two><div>
  <h2>You will need</h2>
  <ul><li>14-count Aida in white, antique white or cream (or 18-count for smaller ornaments): about 6 × 6 in (15 × 15 cm) per ornament</li>
  <li>DMC six-strand embroidery floss (see the shopping list on page 4)</li>
  <li>A size 24 tapestry needle (size 26 for 18-count)</li>
  <li>A 4 in hoop to hold the fabric while you stitch</li>
  <li>To finish: felt, card, fabric glue, ribbon or twine</li></ul>
  <h2>Reading the charts</h2>
  <ul><li>One square = one full cross stitch. Each colour has its own symbol, shown in the key on every chart page</li>
  <li>Bold lines mark every 10 stitches; the red arrows mark the centre</li>
  <li>Choose the colour chart or the one-colour chart (all stitches in DMC 3371, or any single colour you like)</li></ul>
  <h2>Stitching</h2>
  <ul><li>Fold the fabric in half both ways to find the centre and start there, matching the arrows</li>
  <li>Use <b>2 strands</b> of floss on 14-count (1 or 2 on 18-count). Full cross stitches only: no backstitch, no fractional stitches</li>
  <li>Make every cross with the top leg in the same direction for a neat finish</li>
  <li>Don't knot: hold a tail at the back and stitch over it, then weave the end under a few stitches</li></ul>
  </div><div>
  <h2>Finishing as a flat ornament</h2>
  <ol><li>Wash gently if needed and press face down on a towel</li>
  <li>Draw a circle about 3 in (7.5 cm) across on thin card, cut it out and centre it behind the stitching</li>
  <li>Trim the fabric to leave 0.5 in (1.5 cm) all round, snip small notches into the edge and glue it to the back of the card</li>
  <li>Glue a ribbon loop at the top, then a felt circle the same size over the back</li>
  <li>Optional: blanket-stitch round the edge, or glue a twisted cord along it</li></ol>
  <h2>Mini hoop ornament</h2>
  <ol><li>Mount the stitching in a 3 in (7.5 cm) hoop, centred and drum-tight</li>
  <li>Trim the fabric to 0.75 in beyond the hoop, run a gathering stitch round it and pull it closed at the back</li>
  <li>Cover the back with a felt circle and hang it by the hoop screw with ribbon</li></ol>
  <h2>Sizes</h2>
  <p>Each chart page gives the stitch count and the finished size on 14-count and 18-count. The designs are ${RG.stitches}: about ${RG.in14} on 14-count and ${RG.in18} on 18-count.</p>
  <div class=note><b>Tip:</b> cream (DMC 712) is a soft highlight colour. On white fabric it shows as a gentle ivory; on cream or antique white Aida it blends in, which suits the snow and the owl's face.</div>
  </div></div></div>
  <div class=foot>© ${SHOP} · page ${pageNo.how}</div></div>`;
}

function shopping(W, H) {
  const tot = {}, used = {};
  D.motifs.forEach(m => Object.entries(m.counts).forEach(([k, n]) => { tot[k] = (tot[k] || 0) + n; (used[k] = used[k] || []).push(m.n); }));
  const monoTot = D.motifs.reduce((a, m) => a + m.mono_count, 0);
  const rows = Object.keys(PAL).filter(k => tot[k]).map(k => { const p = PAL[k];
    return `<tr><td><span class=chk></span></td><td>${swatch(p.symbol, p.hex, 5.5)}</td><td><b>DMC ${p.dmc}</b></td><td>${p.name}</td><td>${used[k].length === 12 ? 'all 12' : used[k].join(', ')}</td><td class=num>${tot[k]}</td><td class=num><b>${Math.ceil(tot[k] / SPS)}</b></td></tr>`; }).join('');
  return `<div class=page><div class=frame></div><div class=txt>
  <div class=kick>Floss shopping list</div><h1>DMC colours <em>to buy</em></h1>
  <h2>Colour version: ${Object.keys(tot).length} colours</h2>
  <table><tr><th></th><th>Key</th><th>Number</th><th>Name</th><th>Used in charts</th><th style="text-align:right">Stitches</th><th style="text-align:right">Skeins</th></tr>${rows}</table>
  <p style="margin-top:2mm;font-size:3mm;color:${MUTED}">Skeins are for stitching all 12 colour ornaments with 2 strands on 14-count, rounded up (about ${SPS} full crosses per 8 m skein, with a margin). Each chart page lists the colours for that ornament only: one skein of each is plenty for a single ornament.</p>
  <h2 style="margin-top:5mm">One-colour version</h2>
  <table><tr><th></th><th>Key</th><th>Number</th><th>Name</th><th>Used in charts</th><th style="text-align:right">Stitches</th><th style="text-align:right">Skeins</th></tr>
  <tr><td><span class=chk></span></td><td>${swatch(MONO.symbol, MONO_FILL, 5.5)}</td><td><b>DMC ${MONO.dmc}</b></td><td>${MONO.name}</td><td>all 12</td><td class=num>${monoTot}</td><td class=num><b>${Math.ceil(monoTot / SPS)}</b></td></tr></table>
  <p style="margin-top:2mm;font-size:3mm;color:${MUTED}">Any single colour works for the one-colour charts: try 815 Garnet Medium or 500 Blue Green Very Dark for a classic Christmas sampler look.</p>
  <h2 style="margin-top:5mm">Fabric and notions</h2>
  <ul><li>14-count Aida: a 6 × 6 in (15 × 15 cm) piece per ornament. A fat quarter (about 18 × 21 in) cuts 9 pieces, so get two for all 12</li>
  <li>Size 24 tapestry needle, 4 in hoop, small scissors</li>
  <li>For finishing: felt, thin card, fabric glue, ribbon or twine (3 in mini hoops are optional)</li></ul>
  </div><div class=foot>© ${SHOP} · page ${pageNo.shop} · DMC numbers are given so you can buy matching floss; this pattern is not made or endorsed by DMC</div></div>`;
}

function chartPage(W, H, m, mono) {
  const infoH = 58, top = 27, bottom = 11;
  const availW = W - 24, availH = H - top - infoH - bottom - 2;
  const cell = Math.min(5.4, availW / (m.w + 12 / 5.0), availH / (m.h + 12 / 5.0));
  const keyRows = mono
    ? `<tr><td class=keysw>${swatch(MONO.symbol, MONO_FILL)}</td><td><b>${MONO.dmc}</b></td><td>${MONO.name}</td><td class=num>${m.mono_count}</td><td class=num>${skeinTxt(m.mono_count)}</td></tr>`
    : Object.entries(m.counts).map(([k, n]) => { const p = PAL[k];
      return `<tr><td class=keysw>${swatch(p.symbol, p.hex)}</td><td><b>${p.dmc}</b></td><td>${p.name}</td><td class=num>${n}</td><td class=num>${skeinTxt(n)}</td></tr>`; }).join('');
  const kind = mono ? 'One-colour chart' : 'Colour chart';
  const pn = mono ? pageNo.mono(m.n) : pageNo.colour(m.n);
  return `<div class=page>
  <div class=chead><div><div class=kick>${kind} · ${m.n} of 12</div><h1>${m.title}</h1></div>
   <div class=r>Woodland Christmas mini ornaments<br>${SHOP} · page ${pn}</div></div>
  <div class=chartbox style="top:${top}mm;height:${availH}mm">${chart(m, mono, cell)}</div>
  <div class=info style="top:${H - infoH - bottom}mm;height:${infoH}mm">
   <div class=facts>
    <p><b>Stitch count:</b> ${m.w} W × ${m.h} H</p>
    <p><b>14-count:</b> ${sz(m.w, 14)} × ${sz(m.h, 14)}</p>
    <p><b>18-count:</b> ${sz(m.w, 18)} × ${sz(m.h, 18)}</p>
    <p><b>Stitches:</b> 2 strands, full cross stitch only. No backstitch needed.</p>
    <p><b>Fabric:</b> 6 × 6 in of 14-count Aida (white, antique white or cream). Start at the centre arrows.</p>
   </div>
   <div><table><tr><th>Key</th><th>DMC</th><th>Name</th><th style="text-align:right">Stitches</th><th style="text-align:right">Skeins</th></tr>${keyRows}</table>
   ${mono ? `<p style="font-size:2.7mm;color:${MUTED};margin-top:1.6mm">Every marked square is one stitch in DMC 3371 (or one colour of your choice). Blank squares stay unstitched.</p>` : ''}</div>
  </div></div>`;
}

const SIZES = { 'US-Letter': [215.9, 279.4], A4: [210, 297] };
async function overflow(p) {
  const o = await p.evaluate(() => [...document.querySelectorAll('.txt,.info,.chead h1,.grid12 b,.cover h1')].filter(e => e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1)
    .map(e => `${e.className || e.tagName} ${e.scrollWidth}x${e.scrollHeight} > ${e.clientWidth}x${e.clientHeight}`));
  const c = await p.evaluate(() => [...document.querySelectorAll('.chartbox')].filter(b => { const s = b.querySelector('svg').getBoundingClientRect(), r = b.getBoundingClientRect(); return s.width > r.width + 1 || s.height > r.height + 1; }).length);
  if (o.length) console.log(o.join('\n'));
  if (c) console.log(`${c} charts larger than their box`);
  return o.length + c;
}
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  fs.mkdirSync('bundle', { recursive: true });
  let bad = 0;
  for (const [key, [W, H]] of Object.entries(SIZES)) {
    const pages = [cover(W, H), contents(W, H), how(W, H), shopping(W, H),
      ...D.motifs.map(m => chartPage(W, H, m, false)), ...D.motifs.map(m => chartPage(W, H, m, true))];
    const file = `${SLUG}-${key}.pdf`;
    await p.setContent(`<!doctype html><html><head><meta charset=utf-8><style>${css(W, H)}</style></head><body>${pages.join('')}</body></html>`, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const o = await overflow(p); bad += o;
    await p.pdf({ path: `bundle/${file}`, width: `${W}mm`, height: `${H}mm`, printBackground: true, preferCSSPageSize: true });
    console.log(`bundle/${file}${o ? `  OVERFLOW in ${o} boxes` : ''}`);
  }
  await b.close();
  if (bad) { console.error('overflow'); process.exit(1); }
})();
