const { chromium } = require('playwright'); const fs=require('fs');
const moth=fs.readFileSync('/tmp/b5/SVG/02-luna-moon-moth.svg','utf8').replace(/width="[^"]*" height="[^"]*"/,'width="100%" height="100%"');
const tint=(s,c)=>s.replace(/fill="#[0-9a-fA-F]{3,6}"/g,`fill="${c}"`);
const BG='radial-gradient(ellipse at 50% 45%, #3a2440 0%, #1f1426 60%, #150e1b 100%)';
const icon=`<body style="margin:0;width:500px;height:500px;background:${BG};display:grid;place-items:center;overflow:hidden">
<div style="position:absolute;width:96px;height:96px;border-radius:50%;box-shadow:-20px 10px 0 0 #ecd9a2;top:40px;left:330px"></div>
<div style="width:300px;height:300px;margin-top:90px">${tint(moth,'#f1e6cf')}</div></body>`;
const stars=Array.from({length:70},(_,i)=>{const x=(i*977)%3360,y=(i*331)%840,r=(i%3)+2;return `<i style="position:absolute;left:${x}px;top:${y}px;width:${r}px;height:${r}px;border-radius:50%;background:#ecd9a2;opacity:${0.25+(i%4)*0.15}"></i>`}).join('');
const banner=`<body style="margin:0;width:3360px;height:840px;background:${BG};position:relative;overflow:hidden;font-family:'DejaVu Serif',Georgia,serif">${stars}
<div style="position:absolute;left:300px;top:170px;width:500px;height:500px">${tint(moth,'#f1e6cf')}</div>
<div style="position:absolute;right:330px;top:230px;width:380px;height:380px;border-radius:50%;box-shadow:-70px 34px 0 0 #ecd9a2"></div>
<div style="position:absolute;left:0;right:0;top:250px;text-align:center;color:#f1e6cf">
<div style="font-size:120px;letter-spacing:4px">Duskwood Designs Co</div>
<div style="font-size:60px;letter-spacing:2px;color:#ecd9a2;margin-top:18px;font-style:italic">Dark &amp; whimsical cut files</div>
<div style="font-size:40px;letter-spacing:8px;color:#c9b6d6;margin-top:30px">SVG · DXF · PNG · CRICUT · SILHOUETTE · LASER</div></div></body>`;
(async()=>{const b=await chromium.launch();
let p=await b.newPage({viewport:{width:500,height:500}});await p.setContent(icon);await p.screenshot({path:'shop-icon-500.png'});
p=await b.newPage({viewport:{width:3360,height:840}});await p.setContent(banner);await p.screenshot({path:'shop-cover-3360x840.png'});
await b.close();})();
