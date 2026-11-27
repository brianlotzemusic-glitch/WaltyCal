// Offline test (no TpT: temp state dir, local chromium with every request intercepted) for the duplicate-listing fixes in
// tools/tpt.js (25 + 27 Nov 2026): the uploader lock, one save request per Submit click, publish-unverified (never a second Submit),
// the My Products reader and the duplicate-title check. Run: node tools/test-tpt-dupguard.js
const assert = require("assert"), fs = require("fs"), os = require("os"), path = require("path"), cp = require("child_process");
const ROOT = path.dirname(__dirname);
const state = fs.mkdtempSync(path.join(os.tmpdir(), "tpt-state-"));
process.env.TPT_STATE_DIR = state;
const T = require("./tpt.js");
const lockDir = path.join(state, "uploader.lock"), owner = path.join(lockDir, "owner.json");
const MIN = 60000;

(async () => {
  // ---- lock: held by a live process -> refused; a dead pid -> taken over; released on exit
  fs.mkdirSync(lockDir, { recursive: true });
  fs.writeFileSync(owner, JSON.stringify({ pid: process.pid, at: new Date(Date.now() - 8 * 3600 * 1000).toISOString(), cmd: "publish-pending" }));
  assert.strictEqual(T.takeLock("x").held.cmd, "publish-pending", "a live holder keeps the lock, even after 8 h (26 Nov: a 7 h 20 min run)");
  const status = path.join(ROOT, "tpt", "UPLOADER-STATUS.json"), before = fs.existsSync(status) ? fs.readFileSync(status, "utf8") : null;
  const env = { ...process.env, TPT_STATE_DIR: state, HTTPS_PROXY: "http://127.0.0.1:9", HTTP_PROXY: "http://127.0.0.1:9" };
  for (const [args, code] of [[["publish-pending"], 0], [["publish", "tpt/081-may-music-sub-plans-k5"], 1], [["duplicates"], 1]]) {
    const r = cp.spawnSync("node", [path.join(ROOT, "tools", "tpt.js"), ...args], { env, encoding: "utf8", timeout: 20000 });
    assert.strictEqual(r.status, code, args + ": " + r.stderr); assert(/holds the uploader lock/.test(r.stdout), r.stdout);
  }
  assert.strictEqual(fs.existsSync(status) ? fs.readFileSync(status, "utf8") : null, before, "a refused run writes no status");
  const dead = cp.spawnSync("node", ["-e", "console.log(process.pid)"], { encoding: "utf8" }).stdout.trim();
  fs.writeFileSync(owner, JSON.stringify({ pid: Number(dead), at: new Date().toISOString(), cmd: "publish" }));
  assert.strictEqual(T.takeLock("mine").held, null, "a dead pid's lock is taken over");
  assert(T.takeLock("again").held, "the same process cannot take it twice");
  fs.rmSync(lockDir, { recursive: true, force: true });
  let r = cp.spawnSync("node", ["-e", `process.env.TPT_STATE_DIR=${JSON.stringify(state)}; const T=require(${JSON.stringify(path.join(ROOT, "tools", "tpt.js"))}); if (T.takeLock("c").held) process.exit(3);`], { encoding: "utf8" });
  assert.strictEqual(r.status, 0, r.stderr); assert(!fs.existsSync(lockDir), "released on exit");
  console.log("ok lock: a live holder blocks publish, publish-pending and duplicates at any age; a dead one is replaced; released on exit");

  // ---- pure helpers
  assert.strictEqual(T.productIdFrom("https://www.teacherspayteachers.com/Product/May-Music-Sub-Plans-K-5-18518940"), "18518940");
  assert.strictEqual(T.productIdFrom("/My-Products/editNext/18519136?x=1"), "18519136");
  assert.strictEqual(T.productIdFrom('{"ok":true,"itemId":18522075}'), "18522075");
  assert.strictEqual(T.productIdFrom("/My-Products/New/Digital-Next"), null);
  assert.strictEqual(T.productUrlFor("May Music Sub Plans K-5", "18518940"), "https://www.teacherspayteachers.com/Product/May-Music-Sub-Plans-K-5-18518940");
  const dups = T.duplicateTitles([{ href: "/Product/May-Music-Sub-Plans-K-5-18518940" }, { href: "/Product/May-Music-Sub-Plans-K-5-18519136" }, { href: "/Product/Other-18400001" }, { href: "/Product/May-Music-Sub-Plans-K-5-18518940?x" }]);
  assert.deepStrictEqual(dups, [{ slug: "may-music-sub-plans-k-5", ids: ["18518940", "18519136"] }]);
  console.log("ok product id from TpT's answers; duplicate titles found on a My Products link list");

  // ---- fake TpT new-item form (every request intercepted; anything for the real domain is aborted and fails the test)
  const { chromium } = require("playwright");
  const browser = await chromium.launch();
  const real = [];
  const FORM = "https://tpt.test/My-Products/New/Digital-Next";
  const form = (mode) => `<html><body><form id="ItemAddForm" method="post" action="${mode === "refuse" ? "/My-Products/New/Digital-Next" : "/items/add"}"><input name="title" value="May Music Sub Plans K-5"></form>
<div class="error" style="display:none">We cannot generate images from your file</div>${mode === "refused-page" ? '<div class="error">Price is required</div>' : ""}
<button type="submit" form="ItemAddForm" id="go">Submit</button>
<script>window.clicks = 0; document.getElementById("go").addEventListener("click", (e) => { window.clicks++;
  ${mode === "convert" ? `e.preventDefault(); (async () => { await fetch("/converter/generate_thumbs", { method: "POST" }); for (let i = 0; i < 3; i++) await fetch("/queue/results", { method: "POST" }); document.getElementById("ItemAddForm").submit(); })();` : ""}
  ${mode === "hang" ? `e.preventDefault(); const send = () => fetch("/items/add", { method: "POST", body: "title=May" }).catch(() => {}); send(); setTimeout(send, 1500); setTimeout(send, 3000);` : ""} });</script></body></html>`;
  const fakePage = async (mode, saves) => {
    const page = await browser.newPage();
    await page.route("**/*", async (route) => {
      const q = route.request(), u = new URL(q.url());
      if (/teacherspayteachers\.com$/.test(u.hostname)) { real.push(u.href); return route.abort(); }
      if (q.method() === "POST") {
        saves.push(`${q.method()} ${u.pathname}`);
        if (mode === "hang") return; // TpT never answers this save
        if (/\/(converter|queue)\//.test(u.pathname)) return route.fulfill({ contentType: "application/json", body: '{"status":1}' });
        if (mode === "created" || mode === "convert") return route.fulfill({ status: 302, headers: { location: "https://tpt.test/Product/May-Music-Sub-Plans-K-5-18518940" }, body: "" });
        if (mode === "refuse") return route.fulfill({ contentType: "text/html", body: form("refused-page") });
      }
      if (u.pathname.startsWith("/Product/")) return route.fulfill({ contentType: "text/html", body: "<h1>May Music Sub Plans K-5</h1>" });
      return route.fulfill({ contentType: "text/html", body: form(mode) });
    });
    await page.goto(FORM);
    return page;
  };
  const SUBMIT = 'button[type="submit"][form="ItemAddForm"]';

  // (a) the 081 case: Submit never navigates, TpT never answers, and the page sends the save again by itself (twice)
  let saves = [], page = await fakePage("hang", saves);
  let sub = await T.submitNewItem(page, SUBMIT, { title: "May Music Sub Plans K-5", limitMs: 6000, pollMs: 200 });
  assert.strictEqual(await page.evaluate(() => window.clicks), 1, "exactly one Submit click");
  assert.deepStrictEqual(saves, ["POST /items/add"], "exactly one save request reached TpT: " + JSON.stringify(saves));
  assert.strictEqual(sub.blocked.length, 2, "both repeats blocked: " + JSON.stringify(sub));
  assert.strictEqual(sub.outcome, "unverified"); assert.strictEqual(sub.id, null);
  await page.close();
  // (b) TpT answers with a redirect to the new product: created, id from the answer
  saves = []; page = await fakePage("created", saves);
  sub = await T.submitNewItem(page, SUBMIT, { title: "May Music Sub Plans K-5", limitMs: 10000, pollMs: 200 });
  assert.deepStrictEqual([sub.outcome, sub.id, sub.url], ["created", "18518940", "https://www.teacherspayteachers.com/Product/May-Music-Sub-Plans-K-5-18518940"], JSON.stringify(sub));
  assert.strictEqual(saves.length, 1); await page.close();
  // (b2) the real order (17 Nov): thumbnail conversion, queue polls, THEN the form post: nothing is blocked, the id is read
  saves = []; page = await fakePage("convert", saves);
  sub = await T.submitNewItem(page, SUBMIT, { title: "May Music Sub Plans K-5", limitMs: 10000, pollMs: 200 });
  assert.deepStrictEqual([sub.outcome, sub.id, sub.blocked.length], ["created", "18518940", 0], JSON.stringify(sub));
  assert.deepStrictEqual(saves, ["POST /converter/generate_thumbs", "POST /queue/results", "POST /queue/results", "POST /queue/results", "POST /items/add"]);
  await page.close();
  // (c) TpT shows the form again with a visible error: refused (the hidden error template is ignored)
  saves = []; page = await fakePage("refuse", saves);
  sub = await T.submitNewItem(page, SUBMIT, { title: "May Music Sub Plans K-5", limitMs: 10000, pollMs: 200 });
  assert.strictEqual(sub.outcome, "refused", JSON.stringify(sub)); assert.deepStrictEqual(sub.messages, ["Price is required"]);
  await page.close();
  console.log("ok one Submit = one save: a hung save's repeats are blocked (unverified), a redirect gives the id, a visible error = refused");

  // ---- publish-unverified after (a): My Products empty for 40 min, then the title shows; runs every 10 min; never a second Submit
  const item = fs.mkdtempSync(path.join(os.tmpdir(), "081-x-")); fs.writeFileSync(path.join(item, "release"), "2026-11-25 released\n");
  const t0 = Date.parse("2026-11-26T13:52:00Z"), title = "May Music Sub Plans K-5", URL81 = "https://www.teacherspayteachers.com/Product/May-Music-Sub-Plans-K-5-18518940";
  T.writeUnverified(item, { submitted_at: new Date(t0).toISOString(), title, release_sha256: "sha-a", looks: [], state: "no answer" });
  assert(fs.existsSync(path.join(item, "publish-unverified")) && fs.existsSync(path.join(state, "submitted", path.basename(item) + ".json")));
  assert(T.unverifiedBlocks(T.readUnverified(item), "sha-a"), "an open record blocks every Submit");
  let looks = [], res;
  const listsAt = (now) => async (t) => { looks.push((now - t0) / MIN); const url = now - t0 >= 40 * MIN ? URL81 : null; return { my_products: { read: true, url }, store: { read: true, url: null } }; };
  for (let m = 10; m <= 240; m += 10) {
    const now = t0 + m * MIN;
    assert(T.unverifiedBlocks(T.readUnverified(item), "sha-a") || fs.existsSync(path.join(item, "uploaded")), `blocked at ${m} min`);
    res = await T.checkPublishUnverified(item, { now, look: listsAt(now) });
    if (res.state === "uploaded") break;
  }
  assert.deepStrictEqual(looks, [70], "one look, at the first run past 70 min");
  assert.strictEqual(res.state, "uploaded"); assert(fs.readFileSync(path.join(item, "uploaded"), "utf8").includes(URL81));
  assert.strictEqual(T.readUnverified(item), null, "record cleared once found");
  console.log("ok 40-minute lag: blocked throughout, found at the 70-minute look, uploaded written, no second Submit");

  // never shows: looks at 70 and 180 min, then final -> owner; blocked until the cloud rewrites `release`; an unreadable look does not count
  fs.rmSync(path.join(item, "uploaded"));
  T.writeUnverified(item, { submitted_at: new Date(t0).toISOString(), title, release_sha256: "sha-a", looks: [] });
  looks = [];
  const absentAt = (now, storeOk = true) => async () => { looks.push((now - t0) / MIN); return { my_products: { read: true, url: null }, store: storeOk ? { read: true, url: null } : { read: false, why: "x" } }; };
  assert.strictEqual((await T.checkPublishUnverified(item, { now: t0 + 75 * MIN, look: absentAt(t0 + 75 * MIN, false) })).state, "absent");
  assert.strictEqual(T.readUnverified(item).looks.length, 0, "a look with the store unreadable is not proof");
  assert.strictEqual((await T.checkPublishUnverified(item, { now: t0 + 95 * MIN, look: absentAt(t0 + 95 * MIN) })).state, "absent");
  assert.strictEqual((await T.checkPublishUnverified(item, { now: t0 + 120 * MIN, look: absentAt(t0 + 120 * MIN) })).state, "not-due");
  assert.strictEqual((await T.checkPublishUnverified(item, { now: t0 + 185 * MIN, look: absentAt(t0 + 185 * MIN) })).state, "final-absent");
  assert.deepStrictEqual(looks, [75, 95, 185]);
  const fin = T.readUnverified(item); assert(fin.final);
  assert(T.unverifiedBlocks(fin, "sha-a"), "final but the same release: still blocked");
  assert(!T.unverifiedBlocks(fin, "sha-b"), "final and the cloud rewrote release (owner told): one new Submit allowed");
  assert(T.unverifiedBlocks({ ...fin, final: false }, "sha-b"), "not final: a rewritten release does not unblock");
  T.clearUnverified(item);
  console.log("ok never found: looks at 70 and 180 min (an unreadable store is retried), final -> owner, blocked until release is rewritten");

  // ---- static checks on publish(): guard before the form, record before the single click, no second click anywhere
  const src = fs.readFileSync(path.join(ROOT, "tools", "tpt.js"), "utf8");
  const pub = src.slice(src.indexOf("async function publish(item"), src.indexOf("// ---- publish-pending")).replace(/^\s*\/\/.*$/gm, "");
  assert(!/locator\(F\.submit\)\.click/.test(pub) && (pub.match(/submitNewItem\(/g) || []).length === 1, "publish() submits only through submitNewItem, once");
  assert(pub.indexOf("writeUnverified(item") < pub.indexOf("submitNewItem("), "record before the click");
  assert(pub.indexOf("unverifiedBlocks(") < pub.indexOf('step = "open the listing form"'), "guard before the form");
  assert(!/SUBMIT_SETTLE|submittedDecision|"resubmit"/.test(src), "the 15-minute resubmit rule is gone");
  console.log("ok publish(): guard before the form, publish-unverified before the only Submit, no 15-minute resubmit");

  // ---- My Products reader against the fake host
  page = await browser.newPage();
  let pages = {};
  await page.route("**/*", (route) => {
    const u = new URL(route.request().url());
    if (/teacherspayteachers\.com$/.test(u.hostname)) { real.push(u.href); return route.abort(); }
    if (u.pathname === "/Login") return route.fulfill({ contentType: "text/html", body: "<p>log in</p>" });
    if (pages.redirect) return route.fulfill({ contentType: "text/html", body: '<script>location.replace("/Login")</script>' });
    return route.fulfill({ contentType: "text/html", body: `<html><body>${pages[u.searchParams.get("page") || "1"] || ""}</body></html>` });
  });
  const MP = "https://tpt.test/My-Products", link = (s, id) => `<a href="/Product/${s}-${id}">${s}</a>`;
  pages = { 1: link("Other", 18400001) + link("May-Music-Sub-Plans-K-5", 18518940), 2: link("May-Music-Sub-Plans-K-5", 18519136) };
  const links = await T.readMyProductsLinks(page, MP);
  assert.deepStrictEqual(T.duplicateTitles(links), [{ slug: "may-music-sub-plans-k-5", ids: ["18518940", "18519136"] }]);
  const st = {}; assert.strictEqual((await T.duplicateCheck(st, { links })).length, 1); assert(st.duplicates && /3 product links read, 1 duplicate/.test(st.duplicate_check));
  assert(fs.readFileSync(path.join(state, "duplicates.json"), "utf8").includes("18519136"));
  let f = await T.findOnMyProducts(page, title, MP); assert.deepStrictEqual([f.read, f.url], [true, URL81]);
  pages = { 1: "<p>Something went wrong</p>" };
  f = await T.findOnMyProducts(page, title, MP); assert.strictEqual(f.read, false, "no products = unknown, never 'not live'");
  pages = { redirect: true };
  await assert.rejects(T.findOnMyProducts(page, title, MP), /not logged in/);
  await browser.close();
  assert.deepStrictEqual(real, [], "no request reached the real TpT domain");
  console.log("ok My Products: duplicates found across pages, title lookup, unknown when empty, login redirect says log in");

  fs.rmSync(state, { recursive: true, force: true }); fs.rmSync(item, { recursive: true, force: true });
  console.log("all dupguard tests passed");
})().catch((e) => { console.error(e); process.exit(1); });
