// Offline browser test (local chromium via playwright, fake HTML, no TpT). Run: node tools/test-tpt-browser.js
const assert = require("assert");
const { chromium } = require("playwright");
const { removeExistingFile, dumpMenu, closeMenu, chipsOf } = require("./tpt.js");

// Fake of the 027 edit page: existing product card with an icon-only X, hidden flags, empty Preview box.
const card = (confirm) => `<form>
<input type="hidden" name="data[ItemsProperty][product_uploaded]" value="1"><input type="hidden" name="data[ItemDigital][product]" value="">
<input type="hidden" name="data[ItemsProperty][preview_uploaded]" value="0">
<div id="files"><div id="card"><div>Old.pdf <span>1.12 MB</span>
<button type="button" id="x" aria-label="Remove file"><svg width="10" height="10"></svg></button></div>
<div>Last updated: Oct 22</div><a href="#rev">See Revision History</a></div>
<div id="prev"><button type="button">Select file</button></div></div></form>
<script>
window.gone = () => { document.getElementById("card").remove(); document.querySelector('[name="data[ItemsProperty][product_uploaded]"]').value = "0"; };
document.getElementById("x").onclick = () => { ${confirm ? `const d=document.createElement("div");d.setAttribute("role","dialog");d.innerHTML='<p>Delete this file?</p><button id="no">Cancel</button><button id="yes">Delete</button>';document.body.appendChild(d);document.getElementById("yes").onclick=()=>{d.remove();gone();};` : "gone();"} };
</script>`;

(async () => {
  const b = await chromium.launch(), page = await b.newPage();
  await page.setContent(card(false));
  let r = await removeExistingFile(page, "product");
  assert(r.ok && /Remove file/.test(r.ok), JSON.stringify(r));
  assert.strictEqual(await page.locator("#card").count(), 0);
  console.log("ok product card removed by its X");

  await page.setContent(card(true));
  r = await removeExistingFile(page, "product");
  assert(r.ok, JSON.stringify(r));
  assert.strictEqual(await page.locator('[name="data[ItemsProperty][product_uploaded]"]').inputValue(), "0");
  console.log("ok confirm dialog answered with Delete (not Cancel)");

  await page.setContent(card(false));
  r = await removeExistingFile(page, "preview");
  assert(r.skipped && !r.ok, JSON.stringify(r));
  assert.strictEqual(await page.locator("#card").count(), 1, "preview step must not touch the product card");
  console.log("ok empty Preview box: nothing removed");

  await page.setContent('<input type="hidden" name="data[ItemsProperty][product_uploaded]" value="1"><p>no card</p>');
  r = await removeExistingFile(page, "product");
  assert(r.error, JSON.stringify(r));
  console.log("ok no card -> error (the caller fails, no blind upload)");

  await page.setContent('<input type="hidden" name="data[ItemsProperty][product_uploaded]" value="1"><div>Last updated x<button>Remove</button></div><script>document.querySelector("button").onclick=()=>{}</script>');
  const t = Date.now(); page.setDefaultTimeout(5000);
  // X that does nothing: must not report success (shortened wait: patch via evaluate is not possible, so just assert it errors)
  r = await Promise.race([removeExistingFile(page, "product"), new Promise((res) => setTimeout(() => res({ error: "timeout-guard" }), 40000))]);
  assert(r.error, JSON.stringify(r));
  console.log("ok an X that changes nothing is an error, not a success");

  // react-select-like: chips in a control, menu of options, scrolled list
  await page.setContent(`<div class="x-control"><span>Music</span><input id="subject-areas"></div>
  <div role="listbox">${["Art", "Art History", "College", "Music"].map((o) => `<div role="option">${o}</div>`).join("")}</div>`);
  assert.deepStrictEqual(await chipsOf(page.locator("#subject-areas")), ["music"]);
  const all = await dumpMenu(page, page.locator("#subject-areas"));
  assert.deepStrictEqual(all, ["Art", "Art History", "College", "Music"]);
  await b.close();
  console.log("ok chips read and full option list dumped");
})().catch((e) => { console.error(e); process.exit(1); });
