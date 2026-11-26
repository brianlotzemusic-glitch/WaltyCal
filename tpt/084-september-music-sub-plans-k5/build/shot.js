const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1100,height:520},deviceScaleFactor:1.5});
await p.goto('file://'+process.argv[2]);await p.screenshot({path:process.argv[3]});await b.close();})();
