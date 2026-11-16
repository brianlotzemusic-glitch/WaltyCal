// Offline test for the `republish` fallback in tools/tpt.js (no TpT; browser steps are fakes or a local fake page).
// Run: node tools/test-tpt-republish.js
const assert = require("assert"), fs = require("fs"), os = require("os"), path = require("path"), cp = require("child_process");
const { chromium } = require("playwright");
const T = require("./tpt.js");
const ROOT = path.dirname(__dirname);
const OLD = "https://www.teacherspayteachers.com/Product/Note-Naming-Worksheets-Treble-Bass-Alto-Clef-Speed-Drills-Grades-3-8-18352419";
const NEW = "https://www.teacherspayteachers.com/Product/Note-Naming-Worksheets-Treble-Bass-Alto-Clef-Speed-Drills-Grades-3-8-18999999";
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "repub-"));
const tptDir = path.join(tmp, "tpt"); fs.mkdirSync(tptDir);
const SRC = path.join(ROOT, "tpt", "043-note-naming-speed-drills");
const mk = (name, marker = "2026-11-16 republish: edit form will not take the new file\n") => {
  const d = path.join(tptDir, name);
  fs.mkdirSync(d);
  for (const f of ["UPLOAD.md", "tpt.json"]) fs.copyFileSync(path.join(SRC, f), path.join(d, f));
  fs.writeFileSync(path.join(d, "QA.md"), "**Verdict: APPROVED**\n");
  fs.writeFileSync(path.join(d, "uploaded"), `2026-11-15T12:22:51Z published live by tools/tpt.js\n${OLD}\n`);
  if (marker !== null) fs.writeFileSync(path.join(d, "republish"), marker);
  return d;
};
const title = T.loadItem(SRC).title;
const read = (d, f) => fs.readFileSync(path.join(d, f), "utf8");
const J = (d, f) => JSON.parse(read(d, f));
const calls = [];
const fakePublish = (url) => async (d) => { calls.push(["publish", path.basename(d)]); fs.writeFileSync(path.join(d, "uploaded"), `${new Date().toISOString()} published live by tools/tpt.js\n${url}\n`); };
const fakeDeactivate = (ok) => async (u, t) => { calls.push(["deactivate", u, t]); if (!ok) throw new Error("deactivate: Submit did nothing"); return { ok: true }; };

(async () => {
  // ---- states and refusals
  assert.strictEqual(T.republishState(mk("010-a", null)).state, "no-marker");
  const d001 = mk("001-halloween-color-by-note");
  assert.strictEqual(T.republishState(d001).state, "refused");
  let r = await T.republishOne(d001, { publish: fakePublish(NEW), deactivate: fakeDeactivate(true), storeHtml: "" });
  assert.strictEqual(r.action, "none"); assert.strictEqual(calls.length, 0, "001 is never published again");
  const dNo = mk("011-b"); fs.writeFileSync(path.join(dNo, "QA.md"), "**Verdict: REJECTED**\n");
  assert.strictEqual(T.republishState(dNo).state, "not-approved");
  const dUrl = mk("012-c"); fs.rmSync(path.join(dUrl, "uploaded"));
  assert.strictEqual(T.republishState(dUrl).state, "no-url");
  console.log("ok refusals: no marker, 001 never, not approved, not live");

  // ---- happy path
  const d = mk("043-note-naming-speed-drills");
  const oldUploaded = read(d, "uploaded");
  assert.strictEqual(T.republishState(d).state, "pending");
  r = await T.republishOne(d, { publish: fakePublish(NEW), deactivate: fakeDeactivate(true), storeHtml: `<a href="/Product/x-${OLD.split("-").pop()}">` });
  assert.strictEqual(r.action, "republished");
  assert.strictEqual(read(d, "uploaded-previous"), oldUploaded);
  assert(read(d, "uploaded").includes(NEW));
  let rep = J(d, "republished"); assert.strictEqual(rep.old_url, OLD); assert.strictEqual(rep.new_url, NEW); assert.strictEqual(rep.old_deactivated, true);
  assert.deepStrictEqual(calls.slice(-2), [["publish", "043-note-naming-speed-drills"], ["deactivate", OLD, title]]);
  assert.strictEqual(T.republishState(d).state, "done");
  const n = calls.length;
  r = await T.republishOne(d, { publish: fakePublish(NEW), deactivate: fakeDeactivate(true), storeHtml: "" });
  assert.strictEqual(r.action, "none"); assert.strictEqual(calls.length, n, "a done marker does nothing");
  console.log("ok publish new -> uploaded-previous + uploaded + republished -> old listing deactivated with the item title; done is final");

  // ---- deactivation fails: two listings live, retried next run WITHOUT publishing again
  const d2 = mk("042-winter");
  await assert.rejects(T.republishOne(d2, { publish: fakePublish(NEW), deactivate: fakeDeactivate(false), storeHtml: "" }), /could not be deactivated/);
  let f = J(d2, "republish-failed"); assert.strictEqual(f.stage, "deactivate"); assert.strictEqual(f.two_listings_live, true); assert.strictEqual(f.tries, 1);
  assert.strictEqual(J(d2, "republished").old_deactivated, false);
  assert.strictEqual(T.republishState(d2).state, "deactivate-pending");
  await assert.rejects(T.republishOne(d2, { publish: fakePublish("https://www.teacherspayteachers.com/Product/third-1"), deactivate: fakeDeactivate(false), storeHtml: "" }));
  assert.strictEqual(J(d2, "republish-failed").tries, 2);
  const before = calls.filter((c) => c[0] === "publish").length;
  r = await T.republishOne(d2, { publish: fakePublish("https://www.teacherspayteachers.com/Product/third-1"), deactivate: fakeDeactivate(true), storeHtml: "" });
  assert.strictEqual(r.action, "deactivated"); assert.strictEqual(calls.filter((c) => c[0] === "publish").length, before, "never a third copy");
  assert(read(d2, "uploaded").includes(NEW)); assert(!fs.existsSync(path.join(d2, "republish-failed"))); assert.strictEqual(T.republishState(d2).state, "done");
  console.log("ok old listing not deactivated -> republish-failed (two listings live), retries only the deactivation, never publishes again");

  // ---- publish fails: old marker restored, held until a new marker text
  const d3 = mk("044-d");
  const up3 = read(d3, "uploaded");
  await assert.rejects(T.republishOne(d3, { publish: async () => { throw new Error('publish stopped at step "tags" (nothing was submitted): x'); }, deactivate: fakeDeactivate(true), storeHtml: "" }));
  assert.strictEqual(read(d3, "uploaded"), up3); assert(!fs.existsSync(path.join(d3, "uploaded-previous")));
  f = J(d3, "republish-failed"); assert.strictEqual(f.stage, "publish"); assert(/untouched/.test(f.note));
  assert.strictEqual(T.republishState(d3).state, "failed-hold");
  fs.writeFileSync(path.join(d3, "republish"), "2026-11-17 republish again after the tags fix\n");
  assert.strictEqual(T.republishState(d3).state, "pending");
  await assert.rejects(T.republishOne(d3, { publish: async () => { throw new Error("still on the form 2 minutes after Submit; check My Products on TpT before retrying, it may have been created."); }, deactivate: fakeDeactivate(true), storeHtml: "" }));
  assert(/MAY exist/.test(J(d3, "republish-failed").note));
  console.log("ok publish failure: `uploaded` restored, held; unsure submit says a listing MAY exist");

  // ---- a second listing with this title already live (lost marker): adopt it, publish nothing
  const d4 = mk("045-e");
  const pubs = calls.filter((c) => c[0] === "publish").length;
  const html = `<a href="${OLD.replace("https://www.teacherspayteachers.com", "")}">old</a><a href="${NEW.replace("https://www.teacherspayteachers.com", "")}">new</a>`;
  assert.strictEqual(T.otherListing(title, html, OLD), NEW);
  r = await T.republishOne(d4, { publish: fakePublish("https://www.teacherspayteachers.com/Product/z-5"), deactivate: fakeDeactivate(true), storeHtml: html });
  assert.strictEqual(r.new_url, NEW); assert.strictEqual(calls.filter((c) => c[0] === "publish").length, pubs); assert.strictEqual(J(d4, "republished").adopted_existing, true);
  console.log("ok an existing second listing is adopted, nothing published (no third copy)");

  // ---- republish-pending: max 3, deactivation retries first, status file
  const t2 = path.join(tmp, "t2"); fs.mkdirSync(t2);
  const P = (name) => { const x = path.join(t2, name); fs.cpSync(mk("zz-" + name), x, { recursive: true }); return x; };
  const items = ["050-a", "051-b", "052-c", "053-d", "001-halloween"].map(P);
  // 053 is mid-way: new listing up, old still active
  fs.writeFileSync(path.join(items[3], "republished"), JSON.stringify({ marker_sha256: T.republishState(items[3]).markerHash, old_url: OLD, new_url: NEW, old_deactivated: false }));
  const order = [];
  const res = await T.republishPending({ dir: t2, storeHtml: "", publish: async (x) => { order.push("p " + path.basename(x)); fs.writeFileSync(path.join(x, "uploaded"), `t\nhttps://www.teacherspayteachers.com/Product/n-${700 + order.length}\n`); }, deactivate: async (u) => { order.push("d " + u.split("-").pop()); return { ok: true }; } });
  assert.deepStrictEqual(order.filter((o) => o.startsWith("p")), ["p 050-a", "p 051-b"], "3 per run, the deactivation retry counts and goes first");
  assert.strictEqual(order[0], "d 18352419");
  assert.strictEqual(res.deactivated.length, 1); assert.strictEqual(res.republished.length, 2); assert.deepStrictEqual(res.waiting, ["052-c"]);
  assert(res.skipped.some((s) => /^001-halloween: refused/.test(s)));
  assert(JSON.parse(fs.readFileSync(path.join(t2, "UPLOADER-STATUS.json"), "utf8")).republish.ok);
  fs.writeFileSync(path.join(t2, "PAUSED"), "x");
  assert.strictEqual((await T.republishPending({ dir: t2, storeHtml: "", publish: async () => { throw new Error("must not run"); } })).republished.length, 0);
  console.log("ok republish-pending: max 3, deactivation retries first, 001 refused, PAUSED respected, status written");

  // ---- title safeguard on a fake edit page (local chromium, requests intercepted, nothing leaves the machine)
  assert(T.titleMatches("Note  Naming &amp; Drills ", "Note Naming & Drills"));
  assert(!T.titleMatches("Note Naming Drills, Grades 3-8", "Note Naming Drills"));
  assert(!T.titleMatches("", "") && !T.titleMatches("x", ""));
  const F = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8"));
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    const id = "18352419", editUrl = `https://www.teacherspayteachers.com/itemsDigital/editNext/${id}`;
    let server = { title, active: true, saves: 0 };
    await page.route("https://www.teacherspayteachers.com/**", async (route) => {
      const u = route.request().url();
      if (u.endsWith("/save")) { server.saves++; server.active = JSON.parse(route.request().postData()).active; return route.fulfill({ status: 200, body: "{}" }); }
      return route.fulfill({ status: 200, contentType: "text/html", body: `<form id="ItemAddForm"><input id="ItemName" value="${server.title.replace(/"/g, "&quot;")}">
        <button type="button" id="makeProductActive" role="switch" aria-checked="${server.active}" onclick="this.setAttribute('aria-checked', this.getAttribute('aria-checked') === 'true' ? 'false' : 'true')">Make Listing Active</button></form>
        <button type="submit" form="ItemAddForm" onclick="event.preventDefault(); fetch('/save', {method: 'POST', body: JSON.stringify({active: document.getElementById('makeProductActive').getAttribute('aria-checked') === 'true'})})">Submit</button>` });
    });
    const shots = path.join(tmp, "shots");
    server.title = "Some Other Product";
    await assert.rejects(T.deactivateOnPage(page, { editUrl, id, title, F, shots, slug: "t", oldUrl: OLD, settleMs: 300 }), /REFUSED/);
    assert.strictEqual(server.saves, 0); assert.strictEqual(server.active, true);
    server.title = title;
    const ok = await T.deactivateOnPage(page, { editUrl, id, title, F, shots, slug: "t", oldUrl: OLD, settleMs: 300 });
    assert(ok.ok); assert.strictEqual(server.saves, 1); assert.strictEqual(server.active, false);
    assert.strictEqual((await T.deactivateOnPage(page, { editUrl, id, title, F, shots, slug: "t", oldUrl: OLD, settleMs: 300 })).note, "already inactive");
    console.log("ok deactivation: refuses a different title (nothing saved); unticks Make Listing Active, saves, verifies; idempotent");
  } finally { await browser.close(); }

  // ---- CLI: nothing in the real repo is republish-ready by accident; 001 refused
  const r1 = cp.spawnSync("node", [path.join(ROOT, "tools", "tpt.js"), "republish", d001], { encoding: "utf8" });
  assert.strictEqual(r1.status, 0, r1.stderr); assert(/"refused"/.test(r1.stdout));
  fs.rmSync(tmp, { recursive: true });
})().catch((e) => { console.error(e); process.exit(1); });
