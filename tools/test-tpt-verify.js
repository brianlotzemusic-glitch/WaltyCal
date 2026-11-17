// Offline test (no TpT; local chromium with intercepted requests) for the save wait, the file-card verify and the deferred
// `reupload-unverified` check of tools/tpt.js (canary 043 run 2, 16 Nov 2026). Run: node tools/test-tpt-verify.js
const assert = require("assert"), fs = require("fs"), os = require("os"), path = require("path"), crypto = require("crypto");
const { chromium } = require("playwright");
const T = require("./tpt.js");
const ROOT = path.dirname(__dirname);

(async () => {
  // ---- card parsing: the real 043 cards (old Nov 15 card, new card shown before the save)
  const OLD = "NoteNamingWorksheetsTrebleBassAltoClefSpeedDrillsGrades38.pdf 204.37 kB Last updated: Nov 15, 2026 at 7:22 AM EST See Revision History";
  const NEW = "note-naming-speed-drills.pdf 304.37 kB Last updated: Nov 16, 2026 at 3:41 PM EST See Revision History";
  let c = T.parseCard(OLD);
  assert.strictEqual(c.sizeKb, 204.37); assert.strictEqual(c.updated, Date.parse("2026-11-15T12:22:00Z")); assert(/Grades38\.pdf$/.test(c.name));
  assert.strictEqual(T.parseCard("cover.png (22.58 kB) Last updated: Nov 15, 2026 at 8:22 AM EST").sizeKb, 22.58);
  assert.strictEqual(T.parseCard("x.pdf 1.5 MB").sizeKb, 1536);
  assert.strictEqual(T.parseCard("Processing...").updated, null);
  const pdf = { bytes: 311678 };
  assert.strictEqual(T.cardVerdict(OLD, NEW, pdf, "product"), "match", "size 304.37 kB = 311678 bytes");
  assert.strictEqual(T.cardVerdict(OLD, OLD, pdf, "product"), "old");
  assert.strictEqual(T.cardVerdict(OLD, "", pdf, "product"), "unknown");
  const TH_OLD = "Cancel Main Cover cover.png (22.58 kB) Last updated: Nov 15, 2026 at 8:22 AM EST";
  assert.strictEqual(T.cardVerdict(TH_OLD, TH_OLD, { bytes: 101942 }, "thumb1"), "old");
  assert.strictEqual(T.cardVerdict(TH_OLD, "Cancel Main Cover cover.png (24.10 kB) Last updated: Nov 16, 2026 at 3:55 PM EST", { bytes: 101942 }, "thumb1"), "match", "thumbnail: converted size, newer date");
  assert.strictEqual(T.cardVerdict(TH_OLD, "Cancel Main Cover cover.png (99.55 kB) Last updated: Nov 15, 2026 at 8:22 AM EST", { bytes: 101942 }, "thumb1"), "unknown", "a thumbnail is never matched by size alone");
  console.log("ok file cards: size for PDFs, 'Last updated' for every slot; the old card reads as old");

  // ---- deferred schedule
  const at = "2026-11-16T20:00:00Z", t = (m) => Date.parse(at) + m * 60000;
  const rec = { at, checks: [{ at }] };
  assert.deepStrictEqual(T.unverifiedDue(rec, t(30)), { due: false, final: false });
  assert.deepStrictEqual(T.unverifiedDue(rec, t(71)), { due: true, final: false });
  assert.deepStrictEqual(T.unverifiedDue({ at, checks: [{ at }, { at: new Date(t(75)).toISOString() }] }, t(120)), { due: false, final: false });
  assert.deepStrictEqual(T.unverifiedDue({ at, checks: [{ at }, { at: new Date(t(75)).toISOString() }] }, t(181)), { due: true, final: true });
  assert.deepStrictEqual(T.unverifiedDue(rec, t(400)), { due: true, final: true }, "a Mac that was off: one final look");
  console.log("ok deferred looks at >= 70 min and >= 180 min (final)");

  // ---- checkUnverified on a temp item: waiting / verified / failed; never submits (no browser at all here)
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "unv-"));
  const mk = (name) => {
    const d = path.join(tmp, name); fs.mkdirSync(d);
    fs.writeFileSync(path.join(d, "QA.md"), "**Verdict: APPROVED**\n"); fs.writeFileSync(path.join(d, "reupload"), "2026-11-16 canary\n");
    fs.writeFileSync(path.join(d, "uploaded"), "x\nhttps://www.teacherspayteachers.com/Product/Note-Naming-18352419\n");
    const mh = crypto.createHash("sha256").update("2026-11-16 canary\n").digest("hex");
    fs.writeFileSync(path.join(d, "reupload-unverified"), JSON.stringify({ at, marker_sha256: mh, url: "u", edit_url: "e", checks: [{ at }],
      files: [{ slot: "product", file: "a.pdf", bytes: 311678 }, { slot: "thumb1", file: "cover.png", bytes: 101942 }], old_cards: { product: OLD, thumb1: TH_OLD } }));
    return d;
  };
  const d = mk("043-a");
  assert.strictEqual(T.reuploadState(d).state, "unverified");
  let reads = 0;
  const still = async () => { reads++; return { product: OLD, thumb1: TH_OLD }; };
  assert.strictEqual(await T.checkUnverified(d, { now: t(30), readCardsNow: still }), "waiting"); assert.strictEqual(reads, 0, "not due: no look at all");
  assert.strictEqual(await T.checkUnverified(d, { now: t(75), readCardsNow: still }), "waiting"); assert.strictEqual(reads, 1);
  assert.strictEqual(JSON.parse(fs.readFileSync(path.join(d, "reupload-unverified"), "utf8")).checks.length, 2);
  assert.strictEqual(await T.checkUnverified(d, { now: t(120), readCardsNow: still }), "waiting"); assert.strictEqual(reads, 1, "70-min look done, 180 not due");
  assert.strictEqual(await T.checkUnverified(d, { now: t(185), readCardsNow: async () => ({ product: NEW, thumb1: "cover.png (24 kB) Last updated: Nov 16, 2026 at 3:55 PM EST" }) }), "verified");
  assert(fs.existsSync(path.join(d, "reuploaded")) && !fs.existsSync(path.join(d, "reupload-unverified")));
  assert.strictEqual(T.reuploadState(d).state, "done");
  const d2 = mk("042-b");
  assert.strictEqual(await T.checkUnverified(d2, { now: t(200), readCardsNow: still }), "failed");
  const f = JSON.parse(fs.readFileSync(path.join(d2, "reupload-failed"), "utf8"));
  assert.strictEqual(f.step, "verify (later)"); assert(/still shows/.test(f.error)); assert(!fs.existsSync(path.join(d2, "reupload-unverified")));
  assert.strictEqual(T.reuploadState(d2).state, "failed-hold", "no resubmit after a final failure");
  fs.rmSync(tmp, { recursive: true });
  console.log("ok reupload-unverified: waits, looks at 70 min, verified -> reuploaded; still old at 3 h -> reupload-failed; never resubmitted");

  // ---- submitAndWait: a slow save must be waited for (the old code left after ~5 s); errors and silence are failures
  const browser = await chromium.launch();
  try {
    // Everything runs on a FAKE host (tpt.test); every other request is aborted, so nothing ever reaches the real TpT site.
    const ctx = await browser.newContext();
    await ctx.route("**/*", (route) => route.abort()); // page routes below answer tpt.test; anything else (and tpt.test after an unroute) is aborted
    const page = await ctx.newPage();
    const EDIT = "https://tpt.test/itemsDigital/editNext/18352419";
    let saves = 0, saveDelay = 0, saveStatus = 302;
    await page.route("https://tpt.test/**", async (route) => {
      const r = route.request();
      if (r.method() === "POST") {
        saves++; await new Promise((ok) => setTimeout(ok, saveDelay));
        if (saveStatus === 302) return route.fulfill({ status: 302, headers: { location: "https://tpt.test/My-Products?saved=1" } });
        return route.fulfill({ status: saveStatus, contentType: "text/html", body: '<div class="alert error">Something went wrong</div>' });
      }
      if (/My-Products/.test(r.url())) return route.fulfill({ status: 200, contentType: "text/html", body: '<div role="alert">Your product has been updated successfully</div>' });
      return route.fulfill({ status: 200, contentType: "text/html", body: '<form id="ItemAddForm" method="post" action="/itemsDigital/editNext/18352419"><input name="a" value="1"></form><button type="submit" form="ItemAddForm">Submit</button>' });
    });
    const go = async (ms = 20000) => { await page.goto(EDIT); return T.submitAndWait(page, page.locator('button[type="submit"][form="ItemAddForm"]'), EDIT, { timeoutMs: ms, settleMs: 200 }); };
    saveDelay = 40000; let t0 = Date.now(); let r = await go(60000);
    assert(r.ok, JSON.stringify(r)); assert(Date.now() - t0 >= 39000, "waited for the slow save"); assert.strictEqual(saves, 1);
    assert(r.network.requests.some((x) => /POST 302/.test(x)), JSON.stringify(r.network.requests));
    console.log(`ok save: waited ${Math.round((Date.now() - t0) / 1000)} s for a slow save (longer than click()'s own 30 s); POST recorded (${r.how})`);
    saveDelay = 0; saveStatus = 500; r = await go();
    assert(!r.ok && r.status === 500, JSON.stringify(r));
    console.log("ok save: TpT answering 500 is a failure");
    saveDelay = 8000; saveStatus = 302; t0 = Date.now(); r = await go(3000);
    assert(!r.ok && /no answer from TpT/.test(r.how), JSON.stringify(r));
    console.log("ok save: no answer in time is a failure (reported, not retried)");
    await page.waitForTimeout(6000);
    // a form that saves with fetch() (no page load): the 200 answer counts
    await page.unroute("https://tpt.test/**"); saves = 0;
    await page.route("https://tpt.test/**", (route) => route.request().method() === "POST" ? (saves++, route.fulfill({ status: 200, contentType: "application/json", body: '{"ok":true}' }))
      : route.fulfill({ status: 200, contentType: "text/html", body: `<button id="s" onclick="setTimeout(() => fetch('/itemsDigital/save/18352419', {method: 'POST', body: 'x'}), 500)">Submit</button>` }));
    await page.goto(EDIT); r = await T.submitAndWait(page, page.locator("#s"), EDIT, { timeoutMs: 20000, settleMs: 200 });
    assert(r.ok && /POST 200/.test(r.how) && saves === 1, JSON.stringify(r));
    console.log("ok save: a background (fetch) save answered 200 counts");
    await page.waitForTimeout(6000);

    // canary 3 (17 Nov): TpT's edit form saves with a background request and shows a spinner SVG beside Submit meanwhile. The SVG
    // matches the message selectors and has no innerText (null): the old read threw "Cannot read properties of undefined (reading
    // 'replace')" (reproduced with the old code) and the browser closed mid-save.
    await page.unroute("https://tpt.test/**"); saves = 0;
    await page.route("https://tpt.test/**", async (route) => {
      if (route.request().method() === "POST") { saves++; await new Promise((ok) => setTimeout(ok, 6000)); return route.fulfill({ status: 200, contentType: "application/json", body: "{}" }); }
      return route.fulfill({ status: 200, contentType: "text/html", body: `<button id="s" onclick="this.insertAdjacentHTML('afterend', '<svg class=&quot;spinner alert-success&quot; width=9 height=9></svg>'); fetch('/itemsDigital/save/1', {method: 'POST', body: 'x'})">Submit</button>` });
    });
    await page.goto(EDIT); r = await T.submitAndWait(page, page.locator("#s"), EDIT, { timeoutMs: 20000, settleMs: 200 });
    assert(r.ok && saves === 1 && /POST 200/.test(r.how), JSON.stringify(r)); assert.deepStrictEqual(r.loop_errors, []);
    console.log("ok save: the spinner SVG beside Submit (canary 3 crash) no longer throws; the background save is waited for");
    await page.waitForTimeout(500);

    // 17 Nov (020-036 stuck): TpT's real Submit sequence. First the thumbnails go to /converter/convert_thumbs (a form post into an
    // iframe, 200), then /queue/results is polled ({"status":0}) for a few seconds, THEN the real form posts (302). A hidden template
    // "We cannot generate images from your file" is always in the page. The old wait stopped at the first 200 and left mid-save.
    const tptLike = (finalStatus) => async (route) => {
      const r = route.request(), u = r.url();
      if (r.method() === "POST" && /convert_thumbs/.test(u)) return route.fulfill({ status: 200, contentType: "text/html", body: "<p>queued</p>" });
      if (r.method() === "POST" && /queue\/results/.test(u)) return route.fulfill({ status: 200, contentType: "application/json", body: '{"status":0,"data":[]}' });
      if (r.method() === "POST") { saves++; return finalStatus === 302 ? route.fulfill({ status: 302, headers: { location: "https://tpt.test/My-Products" } })
        : route.fulfill({ status: 200, contentType: "text/html", body: '<div class="alert alert-error">Please correct the errors below</div><form></form>' }); }
      if (/My-Products/.test(u)) return route.fulfill({ status: 200, contentType: "text/html", body: "<p>My products</p>" });
      return route.fulfill({ status: 200, contentType: "text/html", body: `<div class="error-message" style="display:none">We cannot generate images from your file. Please upload a different file or your own thumbnail images.</div>
        <iframe name="conv" style="display:none"></iframe><form id="conv" method="post" action="/converter/convert_thumbs" target="conv"><input name="t" value="1"></form>
        <form id="ItemAddForm" method="post" action="/itemsDigital/editNext/18352419"><input name="a" value="1"></form>
        <button id="s" onclick="document.getElementById('conv').submit(); let n = 0; const t = setInterval(() => { fetch('/queue/results', {method: 'POST', body: 'job=1'}); if (++n === 6) { clearInterval(t); document.getElementById('ItemAddForm').submit(); } }, 1000)">Submit</button>` });
    };
    await page.unroute("https://tpt.test/**"); saves = 0;
    await page.route("https://tpt.test/**", tptLike(302));
    t0 = Date.now(); await page.goto(EDIT); r = await T.submitAndWait(page, page.locator("#s"), EDIT, { timeoutMs: 30000, settleMs: 200 });
    assert(r.ok && saves === 1 && /302/.test(r.how) && Date.now() - t0 > 5500, JSON.stringify({ how: r.how, ok: r.ok, saves }));
    assert(!r.messages.some((m) => /cannot generate/.test(m)), "hidden templates are not messages");
    console.log(`ok save: waits through convert_thumbs (200) + queue polling for TpT's real form post (${r.how})`);
    await page.unroute("https://tpt.test/**"); saves = 0;
    await page.route("https://tpt.test/**", tptLike(200));
    await page.goto(EDIT); r = await T.submitAndWait(page, page.locator("#s"), EDIT, { timeoutMs: 30000, settleMs: 200 });
    assert(!r.ok && saves === 1 && /not saved/.test(r.how), JSON.stringify({ how: r.how, ok: r.ok }));
    console.log("ok save: the form coming back with 200 (no redirect) is NOT a save");
    await page.waitForTimeout(500);

    // ---- readCards on TpT's real markup shape: the card text is read from the box around each slot's input
    const F = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8"));
    await page.unroute("https://tpt.test/**");
    await page.setContent(`<div id="files"><div id="upload-product"><div>NoteNaming.pdf 204.37 kB</div><div>Last updated: Nov 15, 2026 at 7:22 AM EST</div><input type="file" id="ItemDigitalProduct" style="display:none"></div></div>
      <div id="thumbs" style="display:none"><div id="upload-thumb1"><div class="title">Main Cover</div><a href="#">cover.png</a> <span>(22.58 kB)</span> <div>Last updated: Nov 15, 2026 at 8:22 AM EST</div><input type="file" id="ItemDigitalThumb1"></div>
      <div id="upload-thumb2"><a href="#">preview-1.png</a> (40 kB)<input type="file" id="ItemDigitalThumb2"></div></div>`);
    const cards = await T.readCards(page, F, ["product", "thumb1"]);
    assert(/204\.37 kB/.test(cards.product) && /Nov 15, 2026 at 7:22/.test(cards.product), cards.product);
    assert(/cover\.png/.test(cards.thumb1) && /22\.58/.test(cards.thumb1) && !/preview-1/.test(cards.thumb1), "hidden thumbnail boxes are still read, each on its own: " + cards.thumb1);
    assert.strictEqual(T.cardVerdict(OLD, cards.product, pdf, "product"), "old");
    console.log("ok readCards: per-slot card text, also for the hidden thumbnail boxes");
  } finally { await browser.close(); }
})().catch((e) => { console.error(e); process.exit(1); });
