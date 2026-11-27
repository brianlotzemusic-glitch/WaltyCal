// Offline test (local chromium, fake HTML, no TpT) for TpT's "Error during file upload, please try again" on a file card:
// tools/tpt.js uploadWaiter() clicks the card's Cancel and attaches the same file ONCE more, then gives up on a second error.
// Run: node tools/test-tpt-uploaderror.js
const assert = require("assert"), fs = require("fs"), os = require("os"), path = require("path");
const { chromium } = require("playwright");
const { uploadErrorCard, uploadWaiter } = require("./tpt.js");

// Two upload boxes like TpT's form (preview + thumbnail 4). failTimes = how many attaches end in TpT's error before one succeeds.
const page = (failTimes) => `<form>
<div id="prevbox"><label>Select file<input type="file" id="ItemDigitalPreview" style="display:none"></label><input type="hidden" id="prevkey" value=""><div id="prevcard"></div></div>
<div id="t4box"><label>Select file<input type="file" id="ItemDigitalThumb4" style="display:none"></label><input type="hidden" id="t4key" value=""><div id="t4card"></div></div>
<div class="error" style="display:none">Error during file upload, please try again</div>
</form>
<script>
window.attaches = 0; window.cancels = 0;
const box = (inp, card, key) => document.getElementById(inp).addEventListener("change", (e) => {
  const n = ++window.attaches, f = e.target.files[0].name, c = document.getElementById(card);
  c.innerHTML = '<span>' + f + '</span><div role="progressbar" style="width:90px;height:4px"></div>';
  setTimeout(() => {
    if (n <= ${failTimes}) {
      c.innerHTML = '<span>' + f + '</span><div role="progressbar" style="width:99px;height:4px"></div><p>Error during file upload, please try again</p><a href="#" class="cancel">Cancel</a>';
      c.querySelector(".cancel").onclick = (ev) => { ev.preventDefault(); window.cancels++; c.innerHTML = ""; e.target.value = ""; };
    } else { c.innerHTML = '<span>' + f + '</span> 99 kB'; document.getElementById(key).value = "key-" + n; }
  }, 300);
});
box("ItemDigitalPreview", "prevcard", "prevkey"); box("ItemDigitalThumb4", "t4card", "t4key");
</script>`;

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "uperr-")), fp = path.join(tmp, "may-PREVIEW.pdf");
  fs.writeFileSync(fp, "%PDF-1.4 fake");
  const browser = await chromium.launch();
  const real = [];
  const open = async (failTimes) => {
    const p = await browser.newPage();
    await p.route("**/*", (r) => { const u = r.request().url(); if (/teacherspayteachers\.com/.test(u)) { real.push(u); return r.abort(); } return r.fulfill({ contentType: "text/html", body: page(failTimes) }); });
    await p.goto("https://tpt.test/My-Products/New/Digital-Next");
    return p;
  };
  const quiet = [], log = (m) => quiet.push(m);
  const mk = (p, input = "#ItemDigitalPreview", key = "#prevkey") => uploadWaiter({ page: p, keySel: key, inputSel: input, fp, fileName: "may-PREVIEW.pdf", pollMs: 200, log });

  // the hidden error template alone is not an error on this card
  let p = await open(0);
  assert.strictEqual(await uploadErrorCard(p, "may-PREVIEW.pdf", "#ItemDigitalPreview"), null);
  await p.close();

  // (1) one TpT error, then success: Cancel clicked once, file attached twice, key set
  p = await open(1);
  let W = mk(p);
  await p.locator("#ItemDigitalPreview").setInputFiles(fp);
  assert.strictEqual(await W.wait(5000), true, quiet.join(" | "));
  assert.deepStrictEqual(await p.evaluate(() => [window.attaches, window.cancels, document.getElementById("prevkey").value]), [2, 1, "key-2"]);
  assert.strictEqual(W.st.retried, true); assert.deepStrictEqual(W.st.errors, ["Error during file upload, please try again"]);
  await p.close();
  console.log("ok one TpT upload error: the card's Cancel is clicked, the same file attached again, the key fills");

  // (2) TpT errors twice: exactly one re-attach, then the wait ends at once (not after the whole step limit) and st.gaveUp is set
  p = await open(5);
  W = mk(p);
  await p.locator("#ItemDigitalPreview").setInputFiles(fp);
  const t0 = Date.now();
  assert.strictEqual(await W.wait(60000), false);
  assert(Date.now() - t0 < 15000, "gave up quickly, not after 60 s");
  assert.deepStrictEqual(await p.evaluate(() => [window.attaches, window.cancels]), [2, 1], "at most one retry per file");
  assert(W.st.gaveUp && W.st.errors.length === 2);
  assert.strictEqual(await W.wait(60000), false, "a waiter that gave up never retries again");
  assert.deepStrictEqual(await p.evaluate(() => window.attaches), 2);
  await p.close();
  console.log("ok a second error: no third attach, the wait ends at once and upload() falls through to its failure");

  // (3) the error is on ANOTHER slot's card (thumbnail 4): the preview waiter does not touch it
  p = await open(1);
  await p.locator("#ItemDigitalThumb4").setInputFiles(fp);
  await p.waitForTimeout(600);
  const other = uploadWaiter({ page: p, keySel: "#prevkey", inputSel: "#ItemDigitalPreview", fp: path.join(tmp, "x.pdf"), fileName: "cover.png", pollMs: 200, log });
  assert.strictEqual(await other.wait(1500), false);
  assert.deepStrictEqual(await p.evaluate(() => [window.attaches, window.cancels]), [1, 0], "nothing clicked on another slot's card");
  assert.strictEqual(other.st.retried, false);
  await p.close();
  console.log("ok an error on another slot's card is left alone");

  await browser.close();
  fs.rmSync(tmp, { recursive: true, force: true });
  assert.deepStrictEqual(real, [], "no request reached TpT");
  console.log("all upload-error tests passed");
})().catch((e) => { console.error(e); process.exit(1); });
