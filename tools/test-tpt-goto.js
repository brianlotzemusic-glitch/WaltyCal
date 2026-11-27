// Offline test (local chromium, fake host, no TpT) for gotoRetry() in tools/tpt.js: page loads before Submit get a longer timeout and
// ONE reload-and-retry; when the second load also fails, the error goes up (the My Products check reads as "unknown", the form step
// fails) and nothing is submitted. Run: node tools/test-tpt-goto.js
process.env.TPT_GOTO_MS = "1500"; // the real limit is 90 s; short here so the test is quick
const assert = require("assert");
const { chromium } = require("playwright");
const T = require("./tpt.js");

(async () => {
  const browser = await chromium.launch(), real = [];
  // hangs[path+query] = how many loads of that path never answer before one does (Infinity = never)
  const open = async (hangs, body) => {
    const page = await browser.newPage(), seen = {};
    await page.route("**/*", (route) => {
      const u = new URL(route.request().url());
      if (/teacherspayteachers\.com$/.test(u.hostname)) { real.push(u.href); return route.abort(); }
      const k = u.pathname + u.search, n = seen[k] = (seen[k] || 0) + 1;
      if (n <= (hangs[k] || 0)) return; // TpT never answers this load
      return route.fulfill({ contentType: "text/html", body: body(u, n) });
    });
    return { page, seen };
  };
  const products = () => '<a href="/Product/May-Music-Sub-Plans-K-5-18518940">May</a>';
  const logs = [];

  // (1) My Products: first load hangs, the reload answers -> the title is found
  let { page, seen } = await open({ "/My-Products": 1 }, products);
  let f = await T.findOnMyProducts(page, "May Music Sub Plans K-5", "https://tpt.test/My-Products");
  assert.deepStrictEqual([f.read, f.url], [true, "https://www.teacherspayteachers.com/Product/May-Music-Sub-Plans-K-5-18518940"], JSON.stringify(f));
  assert.strictEqual(seen["/My-Products"], 2, "one reload, no more");
  await page.close();
  console.log("ok My Products: a load that times out is reloaded once and then read");

  // (2) My Products never answers: exactly two loads, then "unknown" (the guard submits nothing)
  ({ page, seen } = await open({ "/My-Products": Infinity }, products));
  f = await T.findOnMyProducts(page, "May Music Sub Plans K-5", "https://tpt.test/My-Products");
  assert.strictEqual(f.read, false, "unreadable stays unknown"); assert(/Timeout/i.test(f.why), f.why);
  assert.strictEqual(seen["/My-Products"], 2, "exactly one retry");
  await page.close();
  console.log("ok My Products never answers: two loads, then unknown (fail-safe, nothing submitted)");

  // (3) the listing form: the first load comes back without the title box, the reload has it
  const form = (u, n) => n === 1 ? "<p>Something went wrong</p>" : '<input id="ItemTitle">';
  ({ page, seen } = await open({}, form));
  await T.gotoRetry(page, "https://tpt.test/My-Products/New/Digital-Next", () => page.locator("#ItemTitle").waitFor({ state: "visible", timeout: 1500 }), (m) => logs.push(m));
  assert.strictEqual(seen["/My-Products/New/Digital-Next"], 2); assert(/reloading once/.test(logs.join(" ")));
  await page.close();
  // (4) the form never shows its title box: the error goes up after two loads
  ({ page, seen } = await open({}, () => "<p>Something went wrong</p>"));
  await assert.rejects(T.gotoRetry(page, "https://tpt.test/My-Products/New/Digital-Next", () => page.locator("#ItemTitle").waitFor({ state: "visible", timeout: 1500 }), () => {}), /Timeout/i);
  assert.strictEqual(seen["/My-Products/New/Digital-Next"], 2);
  await page.close();
  console.log("ok listing form: reloaded once when the title box is missing; still missing -> the step fails");

  await browser.close();
  assert.deepStrictEqual(real, [], "no request reached TpT");
  // static: gotoRetry is never used after the Submit click in publish()
  const src = require("fs").readFileSync(require("path").join(__dirname, "tpt.js"), "utf8");
  const pub = src.slice(src.indexOf("async function publish(item"), src.indexOf("// ---- publish-pending"));
  assert(pub.lastIndexOf("gotoRetry(") < pub.indexOf("submitNewItem("), "no reload after Submit");
  console.log("all goto tests passed");
})().catch((e) => { console.error(e); process.exit(1); });
