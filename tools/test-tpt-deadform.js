// Offline test (local chromium, fake host, no TpT) for the 27 Nov 2026 "dead form" case (079, 084, 088, 089, 090): the listing form
// loaded but its Downloadable File box ignored the file AND its Select file button opened no picker. tools/tpt.js now reloads a fresh
// form and runs the whole fill ONCE more (fillWithFreshRetry), never clicking Submit. Run: node tools/test-tpt-deadform.js
const assert = require("assert"), fs = require("fs"), os = require("os"), path = require("path");
const { chromium } = require("playwright");
const T = require("./tpt.js");

// deadLoads = how many loads of the form come up with its scripts not running
const form = (dead) => `<form id="ItemAddForm"><input id="title"><label id="sel">Select file<input type="file" id="ItemDigitalProduct" style="display:none"></label>
<input type="hidden" id="key" value=""></form><button type="submit" form="ItemAddForm" id="go">Submit</button>
<script>window.submits = 0; document.getElementById("go").addEventListener("click", (e) => { e.preventDefault(); window.submits++; });
${dead ? `document.getElementById("sel").addEventListener("click", (e) => e.preventDefault(), true); /* the page's JS never came up */`
         : `document.getElementById("ItemDigitalProduct").addEventListener("change", () => setTimeout(() => { document.getElementById("key").value = "k1"; }, 200));`}
</script>`;

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "dead-")), fp = path.join(tmp, "july.pdf"); fs.writeFileSync(fp, "%PDF fake");
  const browser = await chromium.launch(), real = [];
  const run = async (deadLoads, dryRun = false) => {
    const page = await browser.newPage();
    let loads = 0, submits = 0, retries = [];
    await page.route("**/*", (r) => {
      const u = new URL(r.request().url());
      if (/teacherspayteachers\.com$/.test(u.hostname)) { real.push(u.href); return r.abort(); }
      if (u.pathname === "/My-Products/New/Digital-Next") loads++;
      return r.fulfill({ contentType: "text/html", body: form(loads <= deadLoads) });
    });
    let dead = null;
    // a cut-down copy of publish()'s fill: load the form, fill the title, set the file, then the picker fallback
    const fill = async () => {
      await T.gotoRetry(page, "https://tpt.test/My-Products/New/Digital-Next", () => page.locator("#title").waitFor({ timeout: 2000 }), () => {});
      await page.locator("#title").fill("July Music Sub Plans K-5");
      await page.locator("#ItemDigitalProduct").setInputFiles(fp);
      const keySet = (ms) => page.waitForFunction(() => document.getElementById("key").value, null, { timeout: ms }).then(() => true, () => false);
      if (await keySet(1500)) return "attached";
      try {
        const [ch] = await Promise.all([page.waitForEvent("filechooser", { timeout: 1500 }), page.locator("#sel").click({ timeout: 1500 })]);
        await ch.setFiles(fp);
        if (await keySet(1500)) return "attached via picker";
      } catch (e) { /* no picker */ }
      if (!(await keySet(200))) dead = "product";
      throw new Error("not submitted: product: TpT ignored the file, and its \"Select file\" button didn't open a file picker");
    };
    let out, err;
    try { out = await T.fillWithFreshRetry({ page, fill, dead: () => dead, reset: () => { dead = null; }, dryRun, onRetry: async (s) => { retries.push(s); } }); }
    catch (e) { err = e; }
    submits = await page.evaluate(() => window.submits).catch(() => 0);
    await page.close();
    return { out, err, loads, submits, retries };
  };

  let r = await run(1);
  assert.deepStrictEqual([r.out, r.loads, r.retries, r.submits], ["attached", 2, ["product"], 0], JSON.stringify(r));
  console.log("ok dead form once: a fresh form is loaded, the whole fill runs again and the file attaches; Submit never clicked");

  r = await run(5);
  assert(r.err && /didn't open a file picker/.test(r.err.message)); assert.deepStrictEqual([r.loads, r.retries.length, r.submits], [2, 1, 0]);
  console.log("ok dead twice: exactly one fresh-form retry, then the same 'nothing submitted' failure as before");

  r = await run(0);
  assert.deepStrictEqual([r.out, r.loads, r.retries.length], ["attached", 1, 0]);
  r = await run(1, true);
  assert(r.err); assert.deepStrictEqual([r.loads, r.retries.length], [1, 0], "a dry run never retries");
  console.log("ok a live form needs no retry; a dry run reports instead of retrying");

  // other failures (not a dead box) are never retried
  const page = await browser.newPage();
  let calls = 0;
  await assert.rejects(T.fillWithFreshRetry({ page, fill: async () => { calls++; throw new Error("subjects: Music is not an option"); }, dead: () => null, reset: () => {} }), /subjects/);
  assert.strictEqual(calls, 1); await page.close();
  console.log("ok any other failure goes up at once, without a retry");

  // the publish() wiring: the retry wraps the fill, the fill ends before the (single) Submit, the picker failure marks the slot dead
  const src = fs.readFileSync(path.join(__dirname, "tpt.js"), "utf8");
  const pub = src.slice(src.indexOf("async function publish(item"), src.indexOf("// ---- publish-pending")).replace(/^\s*\/\/.*$/gm, "");
  assert(pub.indexOf("fillWithFreshRetry(") > 0 && pub.indexOf("fillWithFreshRetry(") < pub.indexOf("submitNewItem("), "retry only before Submit");
  assert(/deadPicker = slot/.test(pub) && /writeConsole\(/.test(pub), "dead slot recorded, console log written");
  await browser.close();
  fs.rmSync(tmp, { recursive: true, force: true });
  assert.deepStrictEqual(real, [], "no request reached TpT");
  console.log("all dead-form tests passed");
})().catch((e) => { console.error(e); process.exit(1); });
