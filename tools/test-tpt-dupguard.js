// Offline test (no TpT: temp state dir, local chromium with every request intercepted) for the 25 Nov 2026 double-publish fix in
// tools/tpt.js: the uploader lock, the publish-submitted-at note and the My Products duplicate guard. Run: node tools/test-tpt-dupguard.js
const assert = require("assert"), fs = require("fs"), os = require("os"), path = require("path"), cp = require("child_process");
const ROOT = path.dirname(__dirname);
const state = fs.mkdtempSync(path.join(os.tmpdir(), "tpt-state-"));
process.env.TPT_STATE_DIR = state;
const T = require("./tpt.js");
const lockDir = path.join(state, "uploader.lock"), owner = path.join(lockDir, "owner.json");

(async () => {
  // ---- lock: held by a live process -> refused; a dead pid -> taken over; released on exit
  fs.mkdirSync(lockDir, { recursive: true });
  fs.writeFileSync(owner, JSON.stringify({ pid: process.pid, at: new Date().toISOString(), cmd: "publish-pending" }));
  assert.strictEqual(T.takeLock("x").held.cmd, "publish-pending", "a live holder keeps the lock");
  // the CLI respects it and does nothing (it exits before any browser or network): pending -> 0, manual publish -> 1
  const status = path.join(ROOT, "tpt", "UPLOADER-STATUS.json"), before = fs.existsSync(status) ? fs.readFileSync(status, "utf8") : null;
  const env = { ...process.env, TPT_STATE_DIR: state, HTTPS_PROXY: "http://127.0.0.1:9", HTTP_PROXY: "http://127.0.0.1:9" };
  let r = cp.spawnSync("node", [path.join(ROOT, "tools", "tpt.js"), "publish-pending"], { env, encoding: "utf8", timeout: 20000 });
  assert.strictEqual(r.status, 0, r.stderr); assert(/holds the uploader lock/.test(r.stdout), r.stdout);
  r = cp.spawnSync("node", [path.join(ROOT, "tools", "tpt.js"), "publish", "tpt/080-holiday-radio-ident-logic"], { env, encoding: "utf8", timeout: 20000 });
  assert.strictEqual(r.status, 1); assert(/holds the uploader lock/.test(r.stdout), r.stdout);
  assert.strictEqual(fs.existsSync(status) ? fs.readFileSync(status, "utf8") : null, before, "a refused run writes no status");
  // a dead holder is stale
  const dead = cp.spawnSync("node", ["-e", "console.log(process.pid)"], { encoding: "utf8" }).stdout.trim();
  fs.writeFileSync(owner, JSON.stringify({ pid: Number(dead), at: new Date().toISOString(), cmd: "publish" }));
  assert.strictEqual(T.takeLock("mine").held, null, "a dead pid's lock is taken over");
  assert.strictEqual(JSON.parse(fs.readFileSync(owner, "utf8")).pid, process.pid);
  assert(T.takeLock("again").held, "the same process cannot take it twice");
  // a child that takes the lock and exits leaves no lock behind
  fs.rmSync(lockDir, { recursive: true, force: true });
  r = cp.spawnSync("node", ["-e", `process.env.TPT_STATE_DIR=${JSON.stringify(state)}; const T=require(${JSON.stringify(path.join(ROOT, "tools", "tpt.js"))}); if (T.takeLock("c").held) process.exit(3);`], { encoding: "utf8" });
  assert.strictEqual(r.status, 0, r.stderr); assert(!fs.existsSync(lockDir), "released on exit");
  console.log("ok lock: a live holder blocks publish and publish-pending (no status written), a dead one is replaced, released on exit");

  // ---- the publish-submitted-at note
  const item = fs.mkdtempSync(path.join(os.tmpdir(), "080-x-")); fs.writeFileSync(path.join(item, "release"), "2026-11-24 released\n");
  assert.strictEqual(T.readSubmitted(item), null);
  const t0 = Date.parse("2026-11-24T21:03:30Z");
  T.writeSubmitted(item, "Logic Pro Radio Ident Project", t0);
  assert(fs.existsSync(path.join(item, "publish-submitted-at")) && fs.existsSync(path.join(state, "submitted", path.basename(item) + ".json")), "both copies");
  fs.rmSync(path.join(item, "publish-submitted-at")); // another clone of the repo still sees the copy in the state dir
  const note = T.readSubmitted(item); assert.strictEqual(note.at, "2026-11-24T21:03:30.000Z"); assert(note.release_sha256);
  const D = T.submittedDecision, min = 60000, url = "https://www.teacherspayteachers.com/Product/X-18497270";
  assert.strictEqual(D(null, true, null), "none");
  assert.strictEqual(D(null, true, url), "uploaded", "the guard catches a listing even without a note");
  assert.strictEqual(D(note, true, url, t0 + 2 * min), "uploaded");
  assert.strictEqual(D(note, true, null, t0 + 12 * min), "wait", "the 080 case: the second Submit came 12 min after the first");
  assert.strictEqual(D(note, false, null, t0 + 600 * min), "wait", "My Products unreadable never allows a Submit");
  assert.strictEqual(D(note, true, null, t0 + 15 * min), "resubmit");
  T.clearSubmitted(item); assert.strictEqual(T.readSubmitted(item), null);
  console.log("ok note: written in the state dir and the item, 'wait' for 15 min or while My Products is unreadable, 'uploaded' when listed");

  // ---- static order checks in publish(): the note is written before the click; no store-page guard is left in publish-pending
  const src = fs.readFileSync(path.join(ROOT, "tools", "tpt.js"), "utf8");
  const pub = src.slice(src.indexOf("async function publish(item"), src.indexOf("// ---- publish-pending"));
  assert(pub.indexOf("writeSubmitted(item") > 0 && pub.indexOf("writeSubmitted(item") < pub.indexOf("locator(F.submit).click"), "note before the click");
  assert.strictEqual((pub.match(/locator\(F\.submit\)\.click/g) || []).length, 1, "one Submit click per publish()");
  assert(pub.indexOf("findOnMyProducts(page, it.title)") < pub.indexOf('step = "open the listing form"'), "guard before the form");
  assert(!/fetchStoreHtml|liveUrlForTitle/.test(pub), "publish() no longer uses the public store page");
  const pp = src.slice(src.indexOf("async function publishPending"), src.indexOf("// ---- reupload: replace ONLY"));
  assert(!/fetchStoreHtml|liveUrlForTitle/.test(pp), "publish-pending no longer uses the public store page");
  console.log("ok publish(): guard before the form, note before the single Submit click, no public-store guard");

  // ---- findOnMyProducts against a fake host (every request intercepted; anything for TpT's real domain is aborted and fails the test)
  const { chromium } = require("playwright");
  const browser = await chromium.launch(), page = await browser.newPage();
  const real = [];
  const title = "Logic Pro Radio Ident Project: Voice, Music Bed, Ducking & EQ | High School";
  const link = (slug, id, text) => `<a href="/Product/${slug}-${id}">${text}</a>`;
  let pages = {};
  await page.route("**/*", (route) => {
    const u = new URL(route.request().url());
    if (/teacherspayteachers\.com$/.test(u.hostname)) { real.push(u.href); return route.abort(); }
    if (u.pathname === "/Login") return route.fulfill({ contentType: "text/html", body: "<p>log in</p>" });
    const p = u.searchParams.get("page") || "1";
    if (pages.redirect) return route.fulfill({ contentType: "text/html", body: '<script>location.replace("/Login")</script>' }); // TpT's expired-login bounce
    return route.fulfill({ contentType: "text/html", body: `<html><body>${pages[p] || ""}</body></html>` });
  });
  const MP = "https://tpt.test/My-Products";
  pages = { 1: link("Other-Item", 18400001, "Other") + link("Second", 18400002, "Second"), 2: link("Logic-Pro-Radio-Ident-Project-Voice-Music-Bed-Ducking-EQ-High-School", 18497270, title) };
  let f = await T.findOnMyProducts(page, title, MP);
  assert.deepStrictEqual([f.read, f.url, f.links], [true, "https://www.teacherspayteachers.com/Product/Logic-Pro-Radio-Ident-Project-Voice-Music-Bed-Ducking-EQ-High-School-18497270", 3], JSON.stringify(f));
  pages = { 1: link("Other-Item", 18400001, "Other") };
  f = await T.findOnMyProducts(page, title, MP); assert.deepStrictEqual([f.read, f.url], [true, null]);
  pages = { 1: "<p>Something went wrong</p>" };
  f = await T.findOnMyProducts(page, title, MP); assert.strictEqual(f.read, false, "no products = unknown, never 'not live'");
  pages = { redirect: true };
  await assert.rejects(T.findOnMyProducts(page, title, MP), /not logged in/);
  await browser.close();
  assert.deepStrictEqual(real, [], "no request reached the real TpT domain");
  console.log("ok My Products guard: finds the title on page 2, an empty or broken list is unknown, a login redirect says log in");

  fs.rmSync(state, { recursive: true, force: true }); fs.rmSync(item, { recursive: true, force: true });
  console.log("all dupguard tests passed");
})().catch((e) => { console.error(e); process.exit(1); });
