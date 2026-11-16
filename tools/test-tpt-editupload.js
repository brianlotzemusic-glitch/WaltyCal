// Offline test (local chromium, fake HTML, no TpT) for the EDIT-form upload of `reupload` (16 Nov 2026 fix).
// Run: node tools/test-tpt-editupload.js
// Fake of what the 007 screenshot showed: after the old card's X, the new file climbs to 99% and TpT's box turns red with
// "Error during file upload, please try again." and a Cancel link, and the hidden key stays empty.
const assert = require("assert"), fs = require("fs"), os = require("os"), path = require("path");
const { chromium } = require("playwright");
const T = require("./tpt.js");

// ---- pure helpers
{
  assert.deepStrictEqual(T.classifyWidget("music-sub-plans-k5.pdf 414.27 kB 99% Cancel Error during file upload, please try again."), { error: true, processing: false, percent: 99 });
  assert.deepStrictEqual(T.classifyWidget("Processing..."), { error: false, processing: true, percent: null });
  assert.deepStrictEqual(T.classifyWidget("a.pdf 204.37 kB Last updated: Nov 15 See Revision History"), { error: false, processing: false, percent: null });
  const r = T.redact('PUT https://s3.amazonaws.com/live.digital.upload/x/product/abc?X-Amz-Signature=deadbeef1234&Policy=zz {"csrf_token":"abcdef123456","ok":1} authenticity_token=QWERTY123456');
  assert(!/deadbeef|abcdef123456|QWERTY123456/.test(r), r); assert(/live\.digital\.upload\/x\/product\/abc/.test(r) && /"ok":1/.test(r), r);
  console.log("ok classifyWidget + redact");
  assert.deepStrictEqual(T.parsePause(null), { paused: false, allow: null });
  assert.deepStrictEqual(T.parsePause("Paused 2026-11-16: everything\n"), { paused: true, allow: null });
  assert.deepStrictEqual(T.parsePause("Paused.\nallow: 043\n").allow, ["043"]);
  assert.deepStrictEqual(T.parsePause("allow: 43, 012 007-music-sub-plans-k5\n").allow, ["043", "012", "007"]);
  const p = T.parsePause("x\nallow: 043\n");
  assert(T.pauseAllows(p, "/r/tpt/043-note-naming-speed-drills") && !T.pauseAllows(p, "/r/tpt/042-winter-music-escape-room"));
  assert(!T.pauseAllows(T.parsePause("paused\n"), "/r/tpt/043-x") && T.pauseAllows(T.parsePause(null), "/r/tpt/042-x"));
  console.log("ok REUPLOAD-PAUSED with and without an allow: line");
}

const page_ = (mode) => `<form>
<input type="hidden" name="data[ItemDigital][product]" value=""><input type="hidden" name="data[ItemsProperty][product_uploaded]" value="1">
<input type="hidden" name="data[ItemDigital][preview]" value=""><input type="hidden" name="data[ItemsProperty][preview_uploaded]" value="1">
<h3>Files</h3>
<div id="pbox"><div id="pcard" style="position:relative;width:500px;height:80px">Old.pdf 204 kB <span id="px" style="position:absolute;right:8px;top:8px;cursor:pointer">✖</span>
<div>Last updated: Nov 15</div><a href="#rev">See Revision History</a></div>
<div id="pstate"></div><label id="plab" style="display:none"><button type="button" id="psel">Select file</button><input type="file" id="ItemDigitalProduct" style="display:none"></label></div>
<h3>Product Previews</h3>
<div id="vbox"><div id="vcard" style="position:relative;width:300px;height:80px">Preview demo.pdf <span id="vx" class="delete-btn" style="position:absolute;right:8px;top:8px;cursor:pointer">✖</span>
<div>Last updated: Oct 8</div><a href="#rev2">See Revision History</a></div><input type="file" id="ItemDigitalPreview" style="display:none"></div>
</form>
<script>(() => {
window.tries = 0; window.mode = ${JSON.stringify(mode)};
const key = document.querySelector('[name="data[ItemDigital][product]"]'), st = document.getElementById("pstate"), inp = document.getElementById("ItemDigitalProduct");
document.getElementById("px").onclick = () => { document.getElementById("pcard").remove(); document.querySelector('[name="data[ItemsProperty][product_uploaded]"]').value = "0"; document.getElementById("plab").style.display = ""; };
document.getElementById("vx").onclick = () => { window.previewRemoved = true; document.getElementById("vcard").remove(); document.querySelector('[name="data[ItemsProperty][preview_uploaded]"]').value = "0"; };
document.getElementById("psel").onclick = () => { window.chooserUsed = true; inp.click(); };
inp.onchange = () => {
  const n = inp.files[0] && inp.files[0].name; if (!n) return; window.tries++;
  document.getElementById("plab").style.display = "none";
  st.innerHTML = n + " 40%";
  setTimeout(() => {
    const bad = window.mode === "always-error" || (window.mode === "error-once" && window.tries === 1);
    if (bad) { st.innerHTML = '<div style="border:1px dashed red">' + n + ' 414 kB 99% <a href="#" id="cancel">Cancel</a></div><p>Error during file upload, please try again.</p>';
      document.getElementById("cancel").onclick = (e) => { e.preventDefault(); st.innerHTML = ""; inp.value = ""; document.getElementById("plab").style.display = ""; }; return; }
    key.value = "v3.tmp"; st.innerHTML = "Processing...";
    setTimeout(() => { st.innerHTML = n + " 414 kB"; key.value = "v3.final"; }, 1500);
  }, 400);
};
})();</script>`;

(async () => {
  const shots = fs.mkdtempSync(path.join(os.tmpdir(), "editup-"));
  const pdf = path.join(shots, "music-sub-plans-k5.pdf"); fs.writeFileSync(pdf, "%PDF-1.4 fake");
  const spec = { input: 'input[type="file"]#ItemDigitalProduct', key: 'input[name="data[ItemDigital][product]"]' };
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on("console", () => {});
  const run = () => T.uploadEditSlot(page, { slot: "product", spec, filePath: pdf, slug: "t", shots, minutesPerTry: 0.1, resetWaitMs: 200 });
  try {
    await page.setContent(page_("ok"));
    let r = await run();
    assert(r.ok, JSON.stringify(r.error || r)); assert.strictEqual(r.key, "v3.final", "must wait until Processing is over, not take the first key");
    assert(!(await page.evaluate(() => window.previewRemoved)), "the PREVIEW card must not be touched by the product step");
    console.log("ok clean upload: waits through Processing... and returns the final key; preview card untouched");

    await page.setContent(page_("error-once"));
    r = await run();
    assert(r.ok, JSON.stringify(r.error || r)); assert.strictEqual(await page.evaluate(() => window.tries), 2);
    assert.strictEqual(r.diag.attempts.length, 2); assert(/Error during file upload/.test(r.diag.attempts[0].result)); assert(/clicked a "Cancel"/.test(r.diag.attempts[0].reset), r.diag.attempts[0].reset);
    console.log("ok TpT's 'Error during file upload' at 99% -> Cancel, upload again -> accepted");

    await page.setContent(page_("always-error"));
    r = await run();
    assert(r.error && /after 3 tries/.test(r.error), JSON.stringify(r));
    assert(await page.evaluate(() => window.chooserUsed), "try 3 must go through TpT's own Select file button");
    const d = r.diagnostics;
    assert(d.diag_file.endsWith("t-reupload-product-diag.json") && fs.existsSync(path.join(shots, "t-reupload-product-diag.json")));
    assert.strictEqual(d.attempts.length, 3); assert(d.widget_last.some((w) => /Error during file upload/.test(w.html || "")), "the box HTML is captured");
    assert(Array.isArray(d.non_get) && Array.isArray(d.console_errors) && Array.isArray(d.tpt_upload_answers));
    console.log("ok always-error: 3 tries (3rd via the file chooser), box HTML + network + console written to the diag file");

    // proximity: with two "Last updated" cards, the preview removal picks the PREVIEW card (002, 16 Nov)
    await page.setContent(page_("ok"));
    const rm = await T.removeExistingFile(page, "preview", { inputSel: 'input[type="file"]#ItemDigitalPreview' });
    assert(rm.ok, JSON.stringify(rm)); assert(await page.evaluate(() => window.previewRemoved));
    assert.strictEqual(await page.locator("#pcard").count(), 1, "product card must stay");
    console.log("ok preview removal picks the card next to the preview input, not the product card");
  } finally { await browser.close(); fs.rmSync(shots, { recursive: true }); }
})().catch((e) => { console.error(e); process.exit(1); });
