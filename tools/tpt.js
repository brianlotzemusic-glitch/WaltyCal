// Teachers Pay Teachers uploader for the owner's Hudson Beat music line.
// TpT has no seller API, so this drives the website with Playwright, logged in as the
// owner's Virtual Assistant (VA) account. It runs on the OWNER'S MAC (see tpt/LOCAL-SETUP.md):
// the cloud sessions can't reach TpT with a browser, because their proxy's certificate isn't
// trusted by Chromium.
//
// Credentials come from the environment (never committed): TPT_VA_EMAIL, TPT_VA_PASSWORD.
//
// Commands:
//   node tools/tpt.js login           open TpT's login page in a browser window with the VA email and password
//                                     filled in; YOU click Log in and finish any check TpT shows (TpT's
//                                     verification fails when the script clicks). The session is saved in
//                                     ~/.tpt-profile (or TPT_PROFILE_DIR) and reused by discover and publish,
//                                     which stop with "run login" when it has expired.
//   node tools/tpt.js discover        with the saved login, open My-Products/New-Item,
//                                     choose "Digital Download" on the product-type picker, and save:
//                                       tpt/_discover/*.png, *.html   screenshots + page HTML (gitignored, stay on the Mac)
//                                       tpt/FORM-FIELDS.json          labels/names/types of the form fields only,
//                                                                     no account details; commit this one
//                                     Nothing is created, saved or published on TpT.
//   node tools/tpt.js publish tpt/NNN-slug [--dry-run]
//                                     fill TpT's Digital Download form from the item's UPLOAD.md + tpt.json
//                                     (selectors in tpt/FORM.json) and submit it LIVE ("Make Listing Active"
//                                     stays ticked). Refuses items without QA approval or with an `uploaded`
//                                     file; writes `uploaded` on success. --dry-run fills the form, lists any
//                                     values TpT rejects with the options it offers, and does not submit.
//
//   Free items (tpt.json "free": true, price "0.00"): the form's "Free Resource" toggle (F.free = #item-free)
//   is ticked instead of filling the price boxes; a missing selector stops with a clear message.
//   Offline test: node tools/test-tpt-free.js
//
//   Duplicate safety (25 Nov 2026, 080 went live twice): every browser command takes ~/.tpt-state/uploader.lock; publish() reads
//   the logged-in My Products list before filling the form and writes a publish-submitted-at note before clicking Submit (see
//   takeLock below). Offline test: node tools/test-tpt-dupguard.js
//
//   node tools/tpt.js publish-pending
//                                     publish items the cloud Manager has released (a `release` file), at most 6
//                                     per run, unless tpt/PAUSED exists; writes tpt/UPLOADER-STATUS.json.
//                                     Run nightly by tools/tpt-nightly.sh (see tpt/LOCAL-SETUP.md).
//
//   node tools/tpt.js discover-edit [tpt/NNN-slug]
//                                     read-only: open a live product's edit page (an item with `uploaded` +
//                                     `reupload`, or the one named) and record its form fields, edit URL pattern
//                                     and file inputs in tpt/EDIT-FIELDS.json. Saves nothing on TpT.
//   node tools/tpt.js reupload tpt/NNN-slug [--dry-run]
//                                     (owner exception, 22 Oct 2026) REPLACE ONLY THE FILES of an already-live
//                                     product with the current build, for an item the Manager marked with a
//                                     `reupload` file after QA approval. Never touches title, price, description,
//                                     tags, subjects, grades. Writes `reuploaded` (time + sha256 of each file).
//                                     --dry-run is offline: lists what would be replaced, opens nothing.
//   node tools/tpt.js reupload-pending
//                                     nightly step after publish-pending: processes every item with a `reupload`
//                                     marker (max 3, not while tpt/PAUSED). If tpt/EDIT-FIELDS.json is missing it
//                                     runs discover-edit instead and replaces nothing that night.
//                                     A marker may also carry directive lines: `files: none` (replace no files) and
//                                     `fix: price, preview` (owner-approved corrective case, 23 Oct 2026, "fix 027"):
//                                     also set price + license price to tpt.json's values, un-tick Free, attach the
//                                     preview PDF, then verify the PUBLIC page (price == tpt.json, isFree false,
//                                     previewUrl present, title unchanged); any mismatch -> reupload-failed + screenshot.
//                                     When EDIT-FIELDS.json has to be recorded first, the fix runs in the SAME night if the
//                                     recorded edit form has every field the marker needs; otherwise the next night.
//                                     tpt/REUPLOAD-PAUSED stops this step; an `allow: 043` line in it lets only those items through
//                                     (a canary). Edit-form uploads: 3 tries per file (the 3rd via TpT's Select-file chooser), success =
//                                     key set AND the box idle; failures write tpt/_publish/<slug>-reupload-<slot>-diag.json (network,
//                                     TpT's process_file/queue answers, console errors, the box's HTML). Offline: node tools/test-tpt-editupload.js
//   After every publish the public page is read back and compared with tpt.json (tools/tpt-live.js); a mismatch goes to
//   UPLOADER-STATUS.json `live_mismatch` and tpt/NNN/live-mismatch. Manager check for all items: python3 tools/tpt-verify-live.py
//   Offline tests: node tools/test-tpt-reupload.js ; node tools/test-tpt-live.js
//
// When a publish step fails or an upload times out, a screenshot goes to tpt/_publish/ (gitignored)
// along with the list of file inputs on the page.
const fs = require("fs"), path = require("path");
const { parseLive, compareLive } = require("./tpt-live.js");
let chromium;
try { ({ chromium } = require("playwright")); }
catch (e) {
  try { ({ chromium } = require(path.join(require("child_process").execSync("npm root -g").toString().trim(), "playwright"))); }
  catch (e2) { chromium = null; } // browser not needed for dry-runs, refusals and tests; openBrowser() says so if it is
}

const ROOT = path.dirname(__dirname);
const LOGIN_URL = "https://www.teacherspayteachers.com/Login";
const NEW_ITEM_URL = "https://www.teacherspayteachers.com/My-Products/New-Item";
const HEADLESS = process.env.TPT_HEADLESS === "1";
// One saved browser profile (cookies = the logged-in session) reused by every run, outside the repo.
const PROFILE = process.env.TPT_PROFILE_DIR || path.join(require("os").homedir(), ".tpt-profile");
const MY_PRODUCTS_URL = "https://www.teacherspayteachers.com/My-Products";

// ---- one uploader at a time, and never two Submits for one item (25 Nov 2026) ------------------------------------------------------
// 080 went live TWICE on 24 Nov (18497270 at 16:03:37 ET, 18497424 at 16:15:29 ET). publish() clicks Submit once per call and
// publish-pending calls it once per item per run, so the second Submit came from outside that run: the nightly lock
// (~/.tpt-nightly.lock, taken by tools/tpt-nightly.sh) never covered a manual `node tools/tpt.js publish[-pending]` from another
// Terminal or Claude session, possibly in another clone; and the public store page that the duplicate guard read lags new listings.
// Now: (1) every browser command of this file takes ~/.tpt-state/uploader.lock (all clones on this Mac share it); (2) a note
// ~/.tpt-state/submitted/<slug>.json (and tpt/<slug>/publish-submitted-at, gitignored) is written just BEFORE any Submit click and
// removed only when the outcome is known; while it exists the item is not submitted again until the logged-in My Products list,
// read at least 15 minutes after that Submit, shows the title (-> `uploaded`) or does not (-> the note is cleared, the next Submit may
// go); (3) the duplicate guard before every publish reads My Products, never the public store page. A My Products read that fails
// or finds no products is "unknown" and stops the publish (nothing is submitted).
const os = require("os");
const STATE_DIR = () => process.env.TPT_STATE_DIR || path.join(os.homedir(), ".tpt-state");
const LOCK_STALE_MS = 6 * 3600 * 1000; // a lock whose process is gone, or older than this, is a crash
const SUBMIT_SETTLE_MS = 15 * 60 * 1000;
function pidAlive(pid) { try { process.kill(pid, 0); return true; } catch (e) { return e.code === "EPERM"; } }
// Takes the lock or returns { held: owner } without taking it. Released when this process exits.
function takeLock(label, now = Date.now()) {
  const dir = path.join(STATE_DIR(), "uploader.lock"), own = path.join(dir, "owner.json");
  fs.mkdirSync(STATE_DIR(), { recursive: true });
  for (let i = 0; i < 2; i++) {
    try { fs.mkdirSync(dir); }
    catch (e) {
      if (e.code !== "EEXIST") throw e;
      let o = null; try { o = JSON.parse(fs.readFileSync(own, "utf8")); } catch (e2) { /* being written, or a crash between mkdir and write */ }
      const age = o ? now - Date.parse(o.at) : now - fs.statSync(dir).mtimeMs;
      const stale = o ? (!pidAlive(o.pid) || age > LOCK_STALE_MS) : age > 60000;
      if (!stale) return { held: o || { pid: null, at: null, cmd: "(starting)" } };
      console.warn(`removing a stale uploader lock (${o ? `pid ${o.pid}, ${o.cmd}, since ${o.at}` : "no owner file"})`);
      fs.rmSync(dir, { recursive: true, force: true });
      continue;
    }
    fs.writeFileSync(own, JSON.stringify({ pid: process.pid, at: new Date(now).toISOString(), cmd: label, clone: ROOT, host: os.hostname() }) + "\n");
    process.on("exit", () => { try { if (JSON.parse(fs.readFileSync(own, "utf8")).pid === process.pid) fs.rmSync(dir, { recursive: true, force: true }); } catch (e) { /* gone */ } });
    return { held: null };
  }
  return { held: { pid: null, at: null, cmd: "(lock could not be taken)" } };
}
function submittedNotePaths(item) { return [path.join(STATE_DIR(), "submitted", `${path.basename(item)}.json`), path.join(item, "publish-submitted-at")]; }
function readSubmitted(item) {
  for (const f of submittedNotePaths(item)) { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch (e) { /* none */ } }
  return null;
}
function writeSubmitted(item, title, now = Date.now()) {
  const note = JSON.stringify({ at: new Date(now).toISOString(), title, release_sha256: releaseSha(item), host: os.hostname(), pid: process.pid, clone: ROOT }, null, 2) + "\n";
  for (const f of submittedNotePaths(item)) { fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, note); }
}
function clearSubmitted(item) { for (const f of submittedNotePaths(item)) fs.rmSync(f, { force: true }); }
// What to do about an earlier Submit. Pure. note: readSubmitted(); found: My Products URL or null; read: did My Products answer?
//   "none" (no note) | "uploaded" (it is live: write the marker) | "wait" (unknown yet: submit nothing) | "resubmit" (15 min after, not there)
function submittedDecision(note, read, found, now = Date.now()) {
  if (read && found) return "uploaded";
  if (!note) return "none";
  if (!read) return "wait";
  const at = Date.parse(note.at);
  return Number.isFinite(at) && now - at >= SUBMIT_SETTLE_MS ? "resubmit" : "wait";
}
// Read-only: every product link on the logged-in My Products list (up to 10 pages). Opens nothing else, clicks nothing.
async function readMyProductsLinks(page, url = MY_PRODUCTS_URL) {
  const links = [];
  for (let p = 1; p <= 10; p++) {
    await page.goto(p === 1 ? url : `${url}?page=${p}`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(3000);
    if (/\/login/i.test(page.url())) throw new Error("not logged in, or the saved session expired: run `node tools/tpt.js login` and finish logging in in the browser window");
    const got = await page.evaluate(() => [...document.querySelectorAll("a[href]")].map((a) => ({ href: a.getAttribute("href"), text: (a.innerText || "").replace(/\s+/g, " ").trim().slice(0, 160) }))
      .filter((l) => /\/Product\/|editNext|\/items/i.test(l.href)));
    const before = links.length;
    for (const l of got) if (!links.some((x) => x.href === l.href)) links.push(l);
    if (links.length === before) break;
  }
  return links;
}
// { read, url }: read=false when My Products could not be read or showed no products (unknown, never "not live").
async function findOnMyProducts(page, title, url = MY_PRODUCTS_URL) {
  try {
    const links = await readMyProductsLinks(page, url);
    if (!links.length) return { read: false, url: null, why: "My Products showed no product links" };
    return { read: true, url: matchMyProducts(title, links), links: links.length };
  } catch (e) {
    if (/not logged in/i.test(e.message)) throw e;
    return { read: false, url: null, why: e.message.split("\n")[0] };
  }
}

async function openBrowser() {
  if (!chromium) throw new Error("playwright is not installed here (this command needs the owner's Mac): see tpt/LOCAL-SETUP.md");
  const context = await chromium.launchPersistentContext(PROFILE, { headless: HEADLESS, viewport: { width: 1400, height: 1000 } });
  const page = context.pages()[0] || await context.newPage();
  page.setDefaultTimeout(30000);
  return { context, page };
}

// discover and publish never type the password: they use the session saved by `login`.
async function ensureLoggedIn(page) {
  await page.goto(MY_PRODUCTS_URL, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2000);
  if (/\/login/i.test(page.url())) throw new Error("not logged in, or the saved session expired: run `node tools/tpt.js login` and finish logging in in the browser window");
}

function env(name) {
  const v = process.env[name];
  if (!v) { console.error(`missing ${name}: see tpt/LOCAL-SETUP.md step 4`); process.exit(2); }
  return v;
}

async function login(page) {
  await page.goto(LOGIN_URL, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
  if (!/\/login/i.test(page.url())) { console.log("Already logged in."); return; }
  // TpT's own ids only: a generic input[type=email] list can match a hidden input first.
  const email = page.locator("#lc-email-username-input"), pass = page.locator("#lc-password-input");
  try { await email.waitFor({ state: "visible", timeout: 30000 }); }
  catch (e) { await loginFailed(page, "the email box (#lc-email-username-input) never appeared"); }
  // The page can re-render after load and clear what was typed, so check and refill.
  for (let i = 0; i < 3; i++) {
    await email.fill(env("TPT_VA_EMAIL"));
    await pass.fill(env("TPT_VA_PASSWORD"));
    await page.waitForTimeout(1000);
    if ((await email.inputValue()) && (await pass.inputValue())) break;
    if (i === 2) await loginFailed(page, "the email/password boxes stayed empty after filling them 3 times");
    await page.waitForTimeout(2000);
  }
  // TpT's verification fails when the script clicks Log in, so a person clicks it.
  console.log("Email and password are filled in. Click Log in in the browser window and finish any check TpT shows (5 minutes)...");
  try {
    await page.waitForURL((u) => !/\/login/i.test(u.toString()), { timeout: 300000 });
  } catch (e) {
    await loginFailed(page, "still on the login page after 5 minutes: Log in wasn't clicked, or TpT's verification didn't finish");
  }
  await page.waitForLoadState("domcontentloaded");
  await page.waitForTimeout(2000);
}

// Saves tpt/_discover/00-login-failed.png/.html and prints any on-page error text, then stops.
async function loginCmd() {
  const { context, page } = await openBrowser();
  try {
    await login(page);
    await ensureLoggedIn(page);
    console.log(`Logged in. The session is saved in ${PROFILE}; discover and publish will reuse it.`);
  } finally {
    await context.close();
  }
}

async function loginFailed(page, why) {
  await page.locator("#lc-password-input").fill("", { timeout: 2000 }).catch(() => {}); // keep the password out of the saved HTML
  await snap(page, path.join(ROOT, "tpt", "_discover"), "00-login-failed").catch(() => {});
  const msgs = await page.locator('[role="alert"], [aria-live="assertive"], [class*="error" i]').allInnerTexts().catch(() => []);
  const text = msgs.map((m) => String(m == null ? "" : m).trim()).filter(Boolean).join(" | ").slice(0, 300);
  throw new Error(`login failed: ${why}${text ? `\nTpT says: ${text}` : ""}\nScreenshot: tpt/_discover/00-login-failed.png`);
}

// Diagnostics must never turn a possibly successful submit into a reported failure (061, 19 Nov 2026: with TpT's page busy after Submit
// (spinner left spinning), a bare page.screenshot timed out after 30 s and its error replaced the real one). So: short timeouts, CSS
// animations frozen (the Submit spinner), caret hidden, a viewport-only fallback, a bounded page.content(), and NEVER a throw.
async function snap(page, dir, name) {
  try { fs.mkdirSync(dir, { recursive: true }); } catch (e) { return; }
  const png = path.join(dir, `${name}.png`);
  try { await page.screenshot({ path: png, fullPage: true, timeout: 10000, animations: "disabled", caret: "initial" }); }
  catch (e) {
    try { await page.screenshot({ path: png, timeout: 5000, animations: "disabled" }); }
    catch (e2) { console.warn(`screenshot ${name} skipped (page busy): ${String(e2.message).split("\n")[0]}`); }
  }
  try { fs.writeFileSync(path.join(dir, `${name}.html`), await Promise.race([page.content(), new Promise((_, no) => setTimeout(() => no(new Error("content() timed out")), 10000))])); }
  catch (e) { console.warn(`page HTML ${name} skipped: ${String(e.message).split("\n")[0]}`); }
}

// Shared by the new-item flow and the reupload fix. Opens a listbox combobox and picks `want`.
// Returns null on success, else an error string (the caller screenshots + fails).
async function pickListbox(page, name, toggle, want) {
  await page.locator(toggle).click();
  const opts = page.getByRole("option");
  await opts.first().waitFor({ timeout: 5000 }).catch(() => {});
  const texts = (await opts.allInnerTexts()).map((t) => t.trim());
  const i = texts.findIndex((t) => t.toLowerCase() === String(want).toLowerCase());
  if (i < 0) { await page.keyboard.press("Escape"); return `${name}: "${want}" is not an option. Options: ${texts.join(" | ")}`; }
  await opts.nth(i).click();
  return null;
}

// Is TpT's "Free Resource" toggle (#item-free) ON? aria-checked, native checked, or the hidden data[Item][free] input.
async function freeIsOn(page, sel) {
  const box = page.locator(sel).first();
  return (await box.getAttribute("aria-checked").catch(() => null)) === "true" || (await box.isChecked().catch(() => false))
    || (await page.locator('input[name="data[Item][free]"]').first().isChecked().catch(() => false));
}

// ids/names of every visible form control (for the untick diagnostics).
async function visibleFieldIds(page) {
  return page.evaluate(() => [...document.querySelectorAll("input,button,select,textarea,[role=combobox]")]
    .filter((e) => e.offsetParent !== null).map((e) => e.id || e.name || "").filter(Boolean));
}

// Labels, names and types of the form controls only (no values), so it is safe to commit.
async function formFields(page) {
  return page.evaluate(() => {
    const labelFor = (el) => {
      if (el.id) { const l = document.querySelector(`label[for="${CSS.escape(el.id)}"]`); if (l) return l.innerText.trim(); }
      const wrap = el.closest("label"); if (wrap) return wrap.innerText.trim();
      return el.getAttribute("aria-label") || el.getAttribute("placeholder") || "";
    };
    return [...document.querySelectorAll("input, select, textarea, [contenteditable=true], button")]
      .filter((el) => !(el.type === "hidden"))
      .map((el) => ({
        tag: el.tagName.toLowerCase(), type: el.type || null, id: el.id || null, name: el.name || null,
        label: labelFor(el).slice(0, 120), text: el.tagName === "BUTTON" ? el.innerText.trim().slice(0, 60) : null,
        required: !!el.required, accept: el.accept || null, multiple: !!el.multiple,
        options: el.tagName === "SELECT" ? [...el.options].map((o) => o.text.trim()).slice(0, 60) : null,
        testid: el.getAttribute("data-testid"),
      }));
  });
}

async function discover() {
  const dir = path.join(ROOT, "tpt", "_discover");
  const { context, page } = await openBrowser();
  const out = { discovered_at: new Date().toISOString(), pages: [] };
  try {
    await ensureLoggedIn(page);
    await snap(page, dir, "01-after-login");
    out.pages.push({ step: "after-login", url: page.url() });
    for (const url of ["https://www.teacherspayteachers.com/My-Products", "https://www.teacherspayteachers.com/Dashboard"]) {
      await page.goto(url, { waitUntil: "domcontentloaded" }).catch(() => {});
      await page.waitForTimeout(2500);
      await snap(page, dir, "02-" + url.split("/").pop().toLowerCase());
      out.pages.push({ step: url.split("/").pop(), url: page.url() });
    }
    // New-Item opens on a "Select a Product Type" picker; the listing form only appears after
    // choosing Digital Download. Choosing a type saves nothing. If it opens a file chooser, the
    // listener below catches it and no file is attached.
    let chooser = null;
    page.on("filechooser", (fc) => { chooser = { multiple: fc.isMultiple() }; });
    await page.goto(NEW_ITEM_URL, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(3000);
    await snap(page, dir, "03-product-type");
    out.pages.push({ step: "product-type", url: page.url(), fields: await formFields(page) });
    const dd = page.getByText(/^\s*Digital Download\s*$/i).first();
    if (await dd.count()) {
      await dd.click();
      await page.waitForLoadState("domcontentloaded");
      await page.waitForTimeout(4000);
      await snap(page, dir, "04-digital-download-form");
      out.pages.push({ step: "digital-download-form", url: page.url(), file_chooser_opened: chooser, fields: await formFields(page) });
    } else {
      out.pages.push({ step: "digital-download-form", error: "no 'Digital Download' option found on the product-type page" });
    }
  } finally {
    fs.writeFileSync(path.join(ROOT, "tpt", "FORM-FIELDS.json"), JSON.stringify(out, null, 2));
    await context.close();
  }
  console.log("Done. Nothing was created on TpT.");
  console.log("Screenshots (keep private): tpt/_discover/   Field list (commit this): tpt/FORM-FIELDS.json");
}

// ---- publish ----------------------------------------------------------------------------
// Reads tpt/NNN-slug/UPLOAD.md (title = code block under "## 1.", description = code block
// under "## 2.") and tpt/NNN-slug/tpt.json (everything else; see tpt/README.md). Selectors come
// from tpt/FORM.json. "Make Listing Active" stays ticked (owner, 4 Oct 2026: publish live).
// --dry-run fills the whole form, reports every problem with the options TpT offers, and
// stops before Submit. A live run stops at the first problem, before Submit.

function codeBlockUnder(md, heading) {
  const i = md.search(new RegExp(`^## ${heading}`, "m"));
  if (i < 0) return null;
  const m = md.slice(i).match(/```[^\n]*\n([\s\S]*?)\n```/);
  return m ? m[1].trim() : null;
}

function loadItem(item) {
  const md = fs.readFileSync(path.join(item, "UPLOAD.md"), "utf8");
  const cfg = JSON.parse(fs.readFileSync(path.join(item, "tpt.json"), "utf8"));
  return { ...cfg, title: codeBlockUnder(md, "1\\."), description: codeBlockUnder(md, "2\\.") };
}

// Typeahead helpers (pure, tested offline by tools/test-tpt-typeahead.js).
// Strings to type into a react-select box, most specific first: the full text, then progressively
// shorter word prefixes ("Career and Technical Education" -> "Career and Technical" -> "Career and" -> "Career").
function typeaheadPrefixes(v) {
  const words = String(v).trim().split(/\s+/).filter(Boolean), out = [];
  for (let n = words.length; n >= 1; n--) { const s = words.slice(0, n).join(" "); if (!out.includes(s)) out.push(s); }
  return out;
}
// Index of the option whose text (or any line of it, since TpT may add a group label) equals `want`, case-insensitively; -1 if none.
function matchOption(texts, want) {
  // "&" == "and", any dash == "-" (TpT may rename "Career and Technical Education" to "Career & Technical Education").
  const norm = (x) => String(x).replace(/&/g, " and ").replace(/[‐-―]/g, "-").replace(/\s*-\s*/g, " - ").replace(/\s+/g, " ").trim().toLowerCase(), w = norm(want);
  let i = texts.findIndex((t) => norm(t) === w);
  if (i < 0) i = texts.findIndex((t) => String(t).split("\n").some((l) => norm(l) === w));
  return i;
}
// Ordered list of the price-/free-dependent publish steps for an item. Free items have no Tax Code listbox
// (TpT hides it on a Free Resource: 028 timed out clicking #taxCode-toggle-button); paid items are unchanged.
function publishSteps(it) {
  return it.free === true ? ["free resource checkbox"] : ["prices", "tax_code"];
}

// Checks that need no browser. Returns a list of problems.
function checkItem(item, it, F) {
  const p = [];
  if (!it.title) p.push("UPLOAD.md: no title code block under '## 1.'");
  else if (it.title.length > 80) p.push(`title is ${it.title.length} characters (max 80)`);
  if (!it.description) p.push("UPLOAD.md: no description code block under '## 2.'");
  for (const k of ["price", "license_price"]) if (!/^\d+(\.\d{2})?$/.test(String(it[k] ?? ""))) p.push(`tpt.json: ${k} must be like "3.50" (got ${JSON.stringify(it[k])})`);
  if (!it.tax_code) p.push("tpt.json: tax_code is not set");
  if (!it.grades?.length || (it.grades.length > 4 && !it.grades.includes("not-grade-specific"))) p.push("tpt.json: grades needs 1-4 slugs");
  if (!it.subjects?.length || it.subjects.length > 3) p.push("tpt.json: subjects needs 1-3 entries");
  // Subject Area is a closed list (133 options, saved from the live dropdown in tpt/SUBJECT-OPTIONS.json); a name outside it fails here, offline (030, 25 Oct 2026: "Career and Technical Education" is not an option).
  if (!fs.existsSync(path.join(item, "uploaded"))) try { // (already-uploaded kits like 008 are history: not re-checked)
    const opts = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "SUBJECT-OPTIONS.json"), "utf8"));
    if (Array.isArray(opts) && opts.length) for (const s of it.subjects || []) if (!opts.includes(s)) p.push(`tpt.json: subject "${s}" is not in tpt/SUBJECT-OPTIONS.json (the ${opts.length} options TpT's Subject Area dropdown offers); use the exact name of an option`);
  } catch (e) { /* no saved list: the browser check on the Mac still applies */ }
  if (!it.tags?.length || it.tags.length > 6) p.push("tpt.json: tags needs 1-6 entries");
  if ((it.formats || []).length > 3) p.push("tpt.json: at most 3 formats");
  // A paid item must never go out free by accident (027, 22 Oct 2026: live page showed 0.00 / Free / no preview).
  if (it.free !== undefined && typeof it.free !== "boolean") p.push(`tpt.json: free must be true or false (got ${JSON.stringify(it.free)})`);
  if (it.free !== true) for (const k of ["price", "license_price"]) {
    if (/^\d+(\.\d{2})?$/.test(String(it[k] ?? "")) && !(Number(it[k]) > 0)) p.push(`tpt.json: ${k} is ${JSON.stringify(it[k])} but the item is not marked "free": true; a paid item needs a price above 0 (or set "free": true)`);
  }
  if (!(it.files || {}).preview && it.no_preview !== true) p.push('tpt.json: files.preview is not set (every item needs its watermarked preview PDF; "no_preview": true only if the owner agreed)');
  if (it.free === true) { // free items only: paid items never reach these checks
    if (!F.free) p.push("tpt/FORM.json has no `free` selector (the Free Resource checkbox, #item-free per FORM-FIELDS.json): cannot publish a free item");
    for (const k of ["price", "license_price"]) if (Number(it[k]) !== 0) p.push(`tpt.json: free item needs ${k} "0.00" (got ${JSON.stringify(it[k])})`);
  }
  const files = it.files || {};
  if (!files.product) p.push("tpt.json: files.product is not set");
  for (const [k, f] of Object.entries(files)) {
    const spec = F.files[k];
    if (!spec) { p.push(`tpt.json: unknown file slot ${k}`); continue; }
    const fp = path.join(item, f);
    if (!fs.existsSync(fp)) { p.push(`missing file ${fp}`); continue; }
    const mb = fs.statSync(fp).size / 1048576;
    if (mb > spec.max_mb) p.push(`${f} is ${mb.toFixed(1)} MB (max ${spec.max_mb} MB for ${k})`);
  }
  return p;
}

// QA.md approval = the LAST "Verdict:" line says APPROVE or APPROVED. Accepts "**Verdict: APPROVED**",
// "## Verdict: APPROVE" and "**Verdict: APPROVE (reason)**" (QA wrote all three); a later REJECT wins.
function isApproved(item) {
  const qa = path.join(item, "QA.md");
  if (!fs.existsSync(qa)) return false;
  const v = [...fs.readFileSync(qa, "utf8").matchAll(/^[#>*\s-]*Verdict:?\**\s*(APPROVED?|REJECT(?:ED)?)\b/gim)];
  return v.length > 0 && /^APPROVE/i.test(v[v.length - 1][1]);
}
// The Manager may release an item whose last QA verdict is a mechanical REJECT it verified itself; it
// must say so in the `release` file ("... verified by Manager ...").
function releasedOverQA(item) {
  try { return /verified by Manager/i.test(fs.readFileSync(path.join(item, "release"), "utf8")); } catch (e) { return false; }
}

// ---- react-select helpers (030, 23 Oct 2026) ----
// Everything the open menu offers, scrolled to the end (menus can be virtualised). Never types a filter.
async function dumpMenu(page, input) {
  const seen = [];
  try {
    await input.fill(""); await input.click();
    const opts = page.getByRole("option");
    if (!(await opts.count())) await page.keyboard.press("ArrowDown");
    for (let i = 0; i < 60; i++) {
      await page.waitForTimeout(250);
      const before = seen.length;
      for (const t of await opts.allInnerTexts()) { const x = t.trim().replace(/\s+/g, " "); if (x && !seen.includes(x)) seen.push(x); }
      if (i > 2 && seen.length === before) break; // nothing new after a scroll
      await opts.last().scrollIntoViewIfNeeded({ timeout: 1000 }).catch(() => {});
      await page.mouse.wheel(0, 600).catch(() => {});
    }
  } catch (e) { /* diagnostics only */ }
  return seen;
}
// 027 (edit page of live product 18040698, 23 Oct 2026): the Files area shows the EXISTING file as a card (name, size, "Last updated",
// "See Revision History", an X at the top right) and TpT's hidden flag data[ItemsProperty][product_uploaded] is 1 with an empty key; there
// is no "Select file" box for the product until that card is removed. Setting a file on the hidden input did nothing for 15 min.
// The empty Preview box (preview_uploaded=0) needs no removal. So: if `<slot>_uploaded` is 1, click the card's X (and confirm, if a dialog
// asks), then wait for the flag to drop / the card to go. Nothing is saved until the whole step list has passed, so a failed upload
// afterwards leaves TpT's stored file untouched (UNVERIFIED: that the X only changes the unsaved form and does not delete server-side).
// Returns { skipped: reason } | { ok: description } | { error }.
async function removeExistingFile(page, slot, opts = {}) {
  const flag = page.locator(`input[name="data[ItemsProperty][${slot}_uploaded]"]`);
  const flagVal = async () => ((await flag.count()) ? await flag.first().inputValue().catch(() => "") : "");
  if ((await flagVal()) !== "1") return { skipped: `${slot}_uploaded is ${JSON.stringify(await flagVal())}: no existing file to remove` };
  const shot = async (tag) => { if (opts.shots && opts.slug) await snap(page, opts.shots, `${opts.slug}-${slot}-remove-${tag}`).catch(() => {}); };
  // 16 Nov 2026 (043 thumb1 diag): TpT's thumbnail/preview widgets are <div id="upload-<slot>"> with an empty <div class="delete-btn">
  // (an icon shown on hover) and a <div class="cancel-btn">Cancel</div> for uploads in flight. Use the delete-btn directly: hover the
  // box so it shows, click it (forced: it may have no size until hovered), confirm a dialog if one opens, wait for the flag to drop.
  const box = page.locator(`#upload-${slot}`).first();
  if (/^thumb/.test(slot) && (await box.count()) && (await box.locator(".delete-btn").count())) { // product + preview: proven path below
    await box.scrollIntoViewIfNeeded({ timeout: 5000 }).catch(() => {});
    await box.hover({ timeout: 5000 }).catch(() => {});
    await shot("before");
    await box.locator(".delete-btn").first().click({ timeout: 10000, force: true }).catch(() => {});
    await page.waitForTimeout(1500);
    const dlg = page.locator('[role="dialog"], [role="alertdialog"]').filter({ has: page.locator("button") }).first();
    if (await dlg.isVisible().catch(() => false)) { const yes = dlg.getByRole("button", { name: /^(yes,? )?(delete|remove|confirm|yes|ok|continue)\b/i }).last(); if (await yes.count()) await yes.click({ timeout: 10000 }); }
    for (const t0 = Date.now(); Date.now() - t0 < 15000; await page.waitForTimeout(500)) {
      if ((await flagVal()) !== "1") { await shot("after"); return { ok: `#upload-${slot} .delete-btn -> ${slot}_uploaded is now ${JSON.stringify(await flagVal())}` }; }
    }
    // not conclusive: fall through to the general search below
  }
  // 25 Oct 2026 (027 Mac log + screenshot): the card's X is a bold icon-font glyph (not a <button>/<svg>/role=button), so the old
  // control search found only the file-name link and clicked THAT (a download link): nothing happened, no dialog. Now: candidates are
  // ranked (labelled remove/close/delete/trash/times > a lone x/×/✕ glyph > icon-ish or clickable leaf in the card's top-right corner >
  // buttons) and an <a href> (the file name, revision history) is never a candidate unless it is labelled remove/delete.
  const found = await page.evaluate(([slotName, inputSel]) => {
    document.querySelectorAll("[data-tpt-remove]").forEach((e) => e.removeAttribute("data-tpt-remove"));
    const isCard = (e) => /Last updated/i.test(e.innerText || "");
    const all = [...document.querySelectorAll("div, li, section, article")].filter(isCard);
    const inner = all.filter((e) => !all.some((o) => o !== e && e.contains(o)));
    // 16 Nov 2026 (002): while the new product file was still "Processing...", the PREVIEW removal clicked controls of another
    // box (select-and-remove-file-section / delete-btn) and the preview flag stayed 1. The card that belongs to this slot is the
    // one closest to the slot's own file input (deepest common ancestor); only without that input fall back to the old guess.
    const near = (() => {
      const inp = inputSel ? document.querySelector(inputSel) : null;
      if (!inp || !inner.length) return null;
      const chain = []; for (let a = inp; a; a = a.parentElement) chain.push(a);
      let best = null, bestDepth = Infinity;
      for (const c of inner) { const i = chain.findIndex((a) => a.contains(c)); if (i >= 0 && i < bestDepth) { bestDepth = i; best = c; } }
      // a tie (two cards share the same nearest ancestor) means the input does not single one out
      if (best && inner.filter((c) => chain[bestDepth].contains(c)).length > 1) return null;
      return best;
    })();
    const seed = near || (slotName === "product" ? (inner.find((e) => /Revision History/i.test(e.innerText)) || inner[0])
      : slotName === "preview" ? (inner.find((e) => /preview/i.test((e.closest("div") && e.closest("div").parentElement && e.closest("div").parentElement.innerText) || "")) || inner[0]) : inner[0]);
    if (!seed) return { error: "no file card (text 'Last updated') found on the page" };
    const cardCtl = (root) => [...root.querySelectorAll("*")].filter((e) => !/^(SCRIPT|STYLE|PATH|G)$/i.test(e.tagName));
    const realLink = (e) => { const a = e.closest("a[href]"); return a && !/^(#|javascript:)/i.test(a.getAttribute("href") || "#"); };
    const label = (e) => `${e.getAttribute("aria-label") || ""} ${e.getAttribute("title") || ""} ${e.getAttribute("data-testid") || ""} ${typeof e.className === "string" ? e.className : (e.className && e.className.baseVal) || ""} ${e.getAttribute("data-action") || ""}`;
    const labelled = (e) => /remove|delete|close|clear|trash|times|dismiss|cancel/i.test(label(e)) && !/revision|history/i.test(e.innerText || "");
    // climb until the card holds a labelled control or a lone-x glyph (never past the form)
    const glyph = (e) => !e.children.length && /^[x×✕✖✗╳]$/i.test((e.textContent || "").trim());
    let card = seed;
    // 16 Nov 2026 (007/027/042/043 reupload-failed + screenshots): the X IS on the page (top-right of the card, a bold x glyph) but the
    // "Last updated ... See Revision History" text lives in a small inner block whose only button-like child is the Revision History
    // control, so the old climb stopped there (card text had no file name) and the X, a sibling further up, was never searched.
    // Now the climb ignores revision/history controls, and must also reach the file-name link / an x-like control.
    const ctlOk = (e) => labelled(e) || glyph(e) || (e.matches("button, [role=button]") && !/revision|history/i.test(e.innerText || ""));
    while (!cardCtl(card).some(ctlOk) && card.parentElement && !card.parentElement.matches("form, main, body")) card = card.parentElement;
    // never swallow a second card (e.g. the Preview card): step back down if the card holds several "Last updated" blocks
    if (inner.filter((o) => card.contains(o)).length > 1 && card !== seed) { let c = seed; while (c.parentElement && c.parentElement !== card && inner.filter((o) => c.parentElement.contains(o)).length === 1) c = c.parentElement; card = c; }
    const cr = card.getBoundingClientRect();
    const visible = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
    const corner = (e) => { const r = e.getBoundingClientRect(); return r.width <= 48 && r.height <= 48 && r.left > cr.left + cr.width * 0.6 && r.top < cr.top + Math.min(cr.height * 0.5, 80); };
    const clickableLeaf = (e) => !e.children.length || [...e.children].every((c) => /^(svg|path|use|i)$/i.test(c.tagName));
    const els = cardCtl(card).filter(visible);
    const tiers = [
      els.filter((e) => labelled(e) && (!realLink(e) || /remove|delete|trash/i.test(label(e)))),
      els.filter((e) => glyph(e) && !realLink(e)),
      els.filter((e) => corner(e) && !realLink(e) && clickableLeaf(e) && (/^(i|svg|span|button)$/i.test(e.tagName) || e.matches("[role=button], [onclick], [tabindex]") || getComputedStyle(e).cursor === "pointer")),
      els.filter((e) => e.matches("button, [role=button]") && !realLink(e) && !/revision|history|select file|browse/i.test(e.innerText || "")),
    ];
    const picked = [];
    for (const t of tiers) for (const e of t) {
      const target = e.closest("button, [role=button]") || (e.tagName.toLowerCase() === "path" ? e.ownerSVGElement : e);
      if (target && !picked.includes(target) && !picked.some((p) => p.contains(target) && p !== target && false)) picked.push(target);
    }
    if (!picked.length) {
      // fallback tiers: overflow menu / replace-style control / file input on the card or its parent, then widen to the parent block
      const wide = card.parentElement && !card.parentElement.matches("form, main, body") && inner.filter((o) => card.parentElement.contains(o)).length === 1 ? card.parentElement : card;
      const alt = cardCtl(wide).filter(visible).filter((e) => !realLink(e) || /remove|delete|trash|replace/i.test(label(e)))
        .filter((e) => /remove|delete|trash|replace|update|new version|upload|more|menu|kebab|ellipsis|options|actions|\u22EE|\u2026/i.test(`${label(e)} ${(e.innerText || "").slice(0, 40)}`) && !/revision|history/i.test(e.innerText || ""));
      alt.slice(0, 3).forEach((e, i) => { const t = e.closest("button, [role=button]") || e; if (!picked.includes(t)) picked.push(t); });
    }
    if (!picked.length) {
      const trim = (n) => (n || "").replace(/\s+/g, " ").trim().slice(0, 60);
      const diag = {
        cardHtml: card.outerHTML.replace(/\s+/g, " ").slice(0, 4000),
        parentHtml: card.parentElement ? card.parentElement.outerHTML.replace(/\s+/g, " ").slice(0, 4000) : "",
        controls: [...card.parentElement.querySelectorAll("button, a, [role=button], input, svg, i, [onclick], [tabindex]")].slice(0, 40)
          .map((e) => `${e.tagName.toLowerCase()} text=${trim(e.innerText || e.value)} aria=${trim(e.getAttribute("aria-label"))} title=${trim(e.getAttribute("title"))} testid=${trim(e.getAttribute("data-testid"))} class=${trim(typeof e.className === "string" ? e.className : e.className && e.className.baseVal)}`),
      };
      return { error: "the file card has no X-like control (no labelled remove/close, no x glyph, no icon in its top-right corner, no menu/replace control); card text: " + (card.innerText || "").replace(/\s+/g, " ").slice(0, 80), diag };
    }
    const describe = [];
    picked.slice(0, 4).forEach((e, i) => { e.setAttribute("data-tpt-remove", String(i + 1)); describe.push(`${e.tagName.toLowerCase()} ${label(e).replace(/\s+/g, " ").trim().slice(0, 60)}`); });
    return { cardText: (card.innerText || "").replace(/\s+/g, " ").slice(0, 80), describe };
  }, [slot, opts.inputSel || null]);
  if (found.error) { await shot("nocontrol"); return { error: found.error, diag: found.diag }; }
  const visibleButtons = () => page.evaluate(() => [...document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"]')]
    .filter((e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; })
    .map((e) => (e.innerText || e.value || e.getAttribute("aria-label") || "").trim().replace(/\s+/g, " ")).filter(Boolean));
  const confirmRe = /^(yes,? )?(delete|remove|confirm|yes|ok|continue|replace|proceed)\b/i;
  const log = [];
  await shot("before");
  for (let i = 0; i < Math.min(found.describe.length, 3); i++) {
    const before = await visibleButtons();
    const target = page.locator(`[data-tpt-remove="${i + 1}"]`).first();
    await target.scrollIntoViewIfNeeded({ timeout: 5000 }).catch(() => {});
    await target.click({ timeout: 10000 });
    log.push(`click ${i + 1} (${found.describe[i]})`);
    await page.waitForTimeout(1500);
    // a confirmation may be a dialog/modal or an inline "Are you sure?" row: any NEW visible button (or one in a dialog) that reads Delete/Remove/Yes/...
    const dialog = page.locator('[role="dialog"], [role="alertdialog"], [class*="modal" i], [class*="popover" i], [class*="confirm" i]').filter({ has: page.locator("button, [role=button]") }).first();
    const inDialog = await dialog.isVisible().catch(() => false);
    const now = await visibleButtons();
    const fresh = now.filter((t) => !before.includes(t));
    log.push(`buttons seen after: ${now.slice(0, 12).join(" | ") || "(none)"}; new: ${fresh.join(" | ") || "(none)"}${inDialog ? "; a dialog is open" : ""}`);
    if (inDialog || fresh.length) {
      await shot(`confirm-${i + 1}`);
      const scope = inDialog ? dialog : page;
      const yes = scope.getByRole("button", { name: confirmRe }).last();
      if (await yes.count()) { log.push(`confirm: clicked "${((await yes.innerText().catch(() => "")) || "").trim()}"`); await yes.click({ timeout: 10000 }); }
      else if (inDialog) return { error: `a dialog opened after the X but has no Delete/Remove/Yes button (saw: ${now.join(" | ").slice(0, 160)})` };
    }
    const t0 = Date.now();
    while (Date.now() - t0 < (i === 0 ? 15000 : 8000)) {
      const gone = (await page.locator(`[data-tpt-remove="${i + 1}"]`).count()) === 0;
      if ((await flagVal()) !== "1" || gone) { await shot("after"); return { ok: `card "${found.cardText}" -> ${log.join("; ")}` }; }
      await page.waitForTimeout(500);
    }
  }
  await shot("after");
  return { error: `${log.join("; ")}; but ${slot}_uploaded is still 1 and the card is still there` };
}

// Close an open react-select menu WITHOUT risking the chips: Escape on an already-closed select can clear the value.
async function closeMenu(page) {
  if (await page.getByRole("option").count().catch(() => 0)) await page.keyboard.press("Escape");
}
// Text of the chips currently shown in the select's control, lower-cased; null when the control cannot be found.
async function chipsOf(input) {
  const control = input.locator('xpath=ancestor::*[contains(@class, "control")][1]');
  if (!(await control.count())) return null;
  return (await control.innerText()).split("\n").map((t) => t.trim().toLowerCase()).filter(Boolean);
}

async function publish(item, dryRun) {
  if (!item) throw new Error("usage: node tools/tpt.js publish tpt/NNN-slug [--dry-run]");
  item = path.resolve(item);
  const F = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8"));
  if (fs.existsSync(path.join(item, "uploaded"))) throw new Error(`already uploaded: ${item}`);
  if (!isApproved(item) && !releasedOverQA(item)) throw new Error("QA.md last verdict is not APPROVE (and the release file does not say \"verified by Manager\")");
  const it = loadItem(item);
  const problems = checkItem(item, it, F);
  if (problems.length && !dryRun) throw new Error("not publishing:\n- " + problems.join("\n- "));

  const slug = path.basename(item), shots = path.join(ROOT, "tpt", "_publish");
  const fail = (msg) => { if (!dryRun) throw new Error(`not submitted: ${msg}`); problems.push(msg); };
  let step = "open browser";
  const fileInputs = () => page.evaluate(() => [...document.querySelectorAll('input[type="file"]')]
    .map((e) => `#${e.id || "-"} name=${e.name || "-"}${e.offsetParent ? "" : " (hidden)"}`).join(", ") || "(none)");
  const { context, page } = await openBrowser();
  try {
    step = "check login";
    await ensureLoggedIn(page);
    // Duplicate guard (25 Nov 2026): the logged-in My Products list, never the public store page (it lags new listings), and an
    // earlier Submit for this item (publish-submitted-at) blocks a new one until My Products has been read 15 minutes after it.
    if (!dryRun) {
      step = "duplicate guard (My Products)";
      const note = readSubmitted(item), mp = await findOnMyProducts(page, it.title);
      const d = submittedDecision(note, mp.read, mp.url);
      if (d === "uploaded") {
        fs.writeFileSync(path.join(item, "uploaded"), `${new Date().toISOString()} found already on My Products by its exact title (not uploaded again${note ? `; Submit was clicked at ${note.at}` : ""})\n${mp.url}\n`);
        clearSubmitted(item);
        console.log(`${slug}: already on My Products at ${mp.url}; marked uploaded and NOT uploading it again.`);
        return { url: mp.url, already: true };
      }
      if (!mp.read) { const e = new Error(`not submitted: duplicate guard could not read My Products (${mp.why}); nothing is submitted while it is unknown`); e.unknown = true; throw e; }
      if (d === "wait") { const e = new Error(`not submitted: Submit was already clicked for this item at ${note.at} (${note.clone || "?"}, pid ${note.pid}); waiting until My Products has been read ${SUBMIT_SETTLE_MS / 60000} minutes after it`); e.waiting = true; throw e; }
      if (d === "resubmit") { console.warn(`${slug}: Submit at ${note.at} left nothing on My Products ${Math.round((Date.now() - Date.parse(note.at)) / 60000)} min later (${mp.links} products read); clearing the note and submitting again.`); clearSubmitted(item); }
    }
    step = "open the listing form";
    await page.goto(F.form_url, { waitUntil: "domcontentloaded" });
    await page.locator(F.title).waitFor({ state: "visible", timeout: 30000 });

    step = "title";
    await page.locator(F.title).fill(it.title || "");

    // Uploads go to TpT as soon as a file is chosen; TpT then fills a hidden key field.
    // Attempt 1 sets the file on the input directly (worked for preview and thumbnails). If TpT
    // hasn't taken it after 45 s (run 5: the main-file box ignored it), attempt 2 clicks the box's
    // own "Select file" label and answers the file picker, the way a person would.
    // Each upload has its own time limit; a missing box or a timeout fails this step only.
    await page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {});
    const keySet = (sel, ms) => page.waitForFunction((s) => { const el = document.querySelector(s); return el && el.value; }, sel, { timeout: ms })
      .then(() => true, () => false);
    const upload = async (slot, file, minutes) => {
      step = `upload ${slot} (${file})`;
      const spec = F.files[slot], fp = path.join(item, file), input = page.locator(spec.input);
      try {
        await input.waitFor({ state: "attached", timeout: 20000 });
      } catch (e) {
        await snap(page, shots, `${slug}-${slot}-box`).catch(() => {});
        return fail(`${slot}: no upload box matching ${spec.input} (screenshot tpt/_publish/${slug}-${slot}-box.png). File inputs on the page: ${await fileInputs()}`);
      }
      await input.setInputFiles(fp, { timeout: 30000 });
      if (await keySet(spec.key, 45000)) return;
      // 19 Nov 2026 (059, 060): the screenshots show TpT HAD taken the file (its name and size card was on the page) but the hidden key
      // was slow to fill; the "Select file" button is gone once a file is attached, so attempt 2 could only fail. If the card shows
      // the file, keep waiting for the key instead of trying the picker.
      // 25 Nov 2026 (079): the preview card WAS on the page with a progress bar still running (TpT slow), but .first() can hit a hidden
      // node, so test every match, and also treat the card's "Cancel" link / progress bar as "TpT has the file".
      const attached = () => page.evaluate((name) => {
        const vis = (e) => !!(e.offsetParent || e.getClientRects().length);
        const hit = [...document.querySelectorAll("body *")].some((e) => e.children.length === 0 && (e.textContent || "").includes(name) && vis(e));
        const busy = [...document.querySelectorAll('[role="progressbar"], progress, [class*="progress" i]')].some(vis);
        return hit || busy;
      }, path.basename(file)).catch(() => false);
      const shown = await attached();
      if (shown) {
        console.log(`${slot}: TpT shows ${file} but the key is not set yet; waiting up to ${minutes} min more`);
        if (await keySet(spec.key, minutes * 60000)) { console.log(`${slot}: key set after the longer wait`); return; }
      }
      if (await keySet(spec.key, 1000)) return; // it may have attached while we were deciding
      if (await attached()) { // never open the picker over a file TpT already holds; give it a last long wait
        console.log(`${slot}: file still shown by TpT after the wait; waiting ${minutes} more min`);
        if (await keySet(spec.key, minutes * 60000)) return;
        await snap(page, shots, `${slug}-${slot}-timeout`).catch(() => {});
        return fail(`upload of ${file} (${slot}) shown by TpT but its key never filled within ${minutes * 2} min (screenshot tpt/_publish/${slug}-${slot}-timeout.png)`);
      }
      step = `upload ${slot} (${file}), attempt 2 via the file picker`;
      console.log(`${slot}: TpT didn't take the file after 45 s; trying its "Select file" button instead`);
      try {
        const label = page.locator("label", { has: input }).first();
        const [chooser] = await Promise.all([page.waitForEvent("filechooser", { timeout: 15000 }), label.click({ timeout: 15000 })]);
        await chooser.setFiles(fp);
      } catch (e) {
        await snap(page, shots, `${slug}-${slot}-picker`).catch(() => {});
        return fail(`${slot}: TpT ignored the file, and its "Select file" button didn't open a file picker (screenshot tpt/_publish/${slug}-${slot}-picker.png). File inputs on the page: ${await fileInputs()}`);
      }
      if (await keySet(spec.key, minutes * 60000)) { console.log(`${slot}: uploaded on attempt 2`); return; }
      await snap(page, shots, `${slug}-${slot}-timeout`).catch(() => {});
      fail(`upload of ${file} (${slot}) did not finish within ${minutes} min, even via the file picker (screenshot tpt/_publish/${slug}-${slot}-timeout.png)`);
    };
    // Free item: tick TpT's "Free Resource" toggle (#item-free) and leave the price boxes alone. Done BEFORE the uploads:
    // on 028 (free) TpT showed no Preview box once Free was ticked and the listing went live without its preview.
    const tickFree = async () => {
      step = "free resource checkbox";
      const box = page.locator(F.free);
      if (!(await box.count())) fail(`free: no "Free Resource" control matching ${F.free}; TpT's form changed, rerun discover`);
      else {
        const on = async () => (await box.getAttribute("aria-checked")) === "true" || (await box.isChecked().catch(() => false))
          || (await page.locator('input[name="data[Item][free]"]').isChecked().catch(() => false));
        if (!(await on())) { await box.click(); await page.waitForTimeout(1000); }
        if (!(await on())) {
          await snap(page, shots, `${slug}-free`).catch(() => {});
          fail(`free: clicked ${F.free} but it does not show as ticked (screenshot tpt/_publish/${slug}-free.png)`);
        }
      }
    };
    if (it.free === true) await tickFree();
    const files = it.files || {};
    if (files.product) await upload("product", files.product, 15);
    let previewAbsent = false;
    if (files.preview) {
      if (it.free === true && !(await page.locator(F.files.preview.input).count())) {
        previewAbsent = true; // 028: no Preview box on the form once Free Resource was ticked
        console.warn(`WARNING: TpT shows no Preview upload box on this Free Resource form; publishing WITHOUT the preview (${files.preview}). The live check will report previewUrl.`);
      } else await upload("preview", files.preview, 5);
    }
    if (["thumb1", "thumb2", "thumb3", "thumb4"].some((k) => files[k])) {
      step = "choose 'Upload thumbnails now'";
      await page.locator(F.upload_thumbnails_now).check();
      for (const k of ["thumb1", "thumb2", "thumb3", "thumb4"]) if (files[k]) await upload(k, files[k], 3);
    }

    // Lexical editor: type line by line; Enter makes a new paragraph.
    step = "description";
    const ed = page.locator(F.description);
    await ed.click();
    const lines = (it.description || "").split("\n");
    for (let i = 0; i < lines.length; i++) {
      if (lines[i]) await page.keyboard.insertText(lines[i]);
      if (i < lines.length - 1) await page.keyboard.press("Enter");
    }
    if (!(await ed.innerText()).includes((it.description || "").slice(0, 40))) fail("description did not appear in the editor");

    if (it.free === true) await tickFree(); // idempotent re-check: still ticked after the uploads and the description
    else {
    step = "prices";
    await page.locator(F.price).fill(String(it.price ?? ""));
    await page.locator(F.license_price).fill(String(it.license_price ?? ""));
    }

    // Listbox comboboxes (tax code, answer key, teaching duration).
    const listbox = async (name, toggle, want) => {
      step = name;
      const err = await pickListbox(page, name, toggle, want);
      if (err) return fail(err);
    };
    if (publishSteps(it).includes("tax_code")) await listbox("tax_code", F.tax_code.toggle, it.tax_code);
    else console.log("tax_code: skipped (free item; TpT hides the Tax Code box on a Free Resource)");

    step = "grades";
    for (const g of it.grades || []) {
      const box = page.locator(F.grade_checkbox.replace("{slug}", g));
      if (!(await box.count())) { fail(`grade "${g}" has no checkbox`); continue; }
      if ((await box.getAttribute("aria-checked")) !== "true") await box.click();
    }

    // react-select comboboxes: type, then pick the option whose text matches exactly. A value that
    // is already selected is skipped: TpT adds some itself (run 6: Format "PDF" after a PDF upload),
    // and react-select doesn't offer selected values again.
    const pick = async (name, sel, values) => {
      for (const v of values || []) {
        step = `${name}: ${v}`;
        const input = page.locator(sel);
        const chosen = (await chipsOf(input)) || [];
        if (chosen.includes(v.toLowerCase())) continue;
        await input.click();
        let i = -1, texts = [];
        const log = [`already selected: ${chosen.filter(Boolean).join(" | ") || "(none)"}`];
        for (const typed of typeaheadPrefixes(v)) {
          await input.fill("");
          await input.fill(typed);
          const opts = page.getByRole("option");
          texts = [];
          for (let t = 0; t < 10; t++) { // up to 5 s for TpT's option list
            await page.waitForTimeout(500);
            texts = (await opts.allInnerTexts()).map((x) => x.trim());
            if (matchOption(texts, v) >= 0) break;
          }
          log.push(`"${typed}" -> ${texts.join(" | ") || "(nothing)"}`);
          i = matchOption(texts, v);
          if (i >= 0) { await opts.nth(i).click(); break; }
        }
        if (i < 0) {
          // Fallbacks (030, 23 Oct: nothing offered for any prefix). (1) real key presses instead of fill(): react-select may
          // ignore a programmatic value; (2) empty input + ArrowDown/click to list ALL options, scrolling the menu, and match by
          // normalised text. A value that still is not found fails loudly (never dropped silently).
          for (const mode of ["keys", "list-all"]) {
            if (i >= 0) break;
            await input.fill(""); await input.click();
            if (mode === "keys") { await input.pressSequentially(String(v).split(/\s+/)[0], { delay: 120 }); }
            else await page.keyboard.press("ArrowDown");
            const opts = page.getByRole("option"), seenAll = new Set();
            for (let t = 0; t < (mode === "keys" ? 8 : 40) && i < 0; t++) {
              await page.waitForTimeout(500);
              texts = (await opts.allInnerTexts()).map((x) => x.trim());
              texts.forEach((x) => seenAll.add(x));
              i = matchOption(texts, v);
              if (i < 0 && mode === "list-all") { await page.keyboard.press("PageDown").catch(() => {}); await page.mouse.wheel(0, 400).catch(() => {}); }
            }
            const menu = await page.locator('[class*="menu" i], [role="listbox"]').first().innerText().catch(() => "");
            log.push(`${mode} -> ${[...seenAll].slice(0, 40).join(" | ") || "(nothing)"}${menu && !seenAll.size ? ` [menu text: ${menu.replace(/\s+/g, " ").slice(0, 80)}]` : ""}`);
            if (i >= 0) await opts.nth(i).click();
          }
        }
        if (i < 0) {
          // Dropdown still open: screenshot + the COMPLETE option list (030: the 400-char status line cut it off after "Art | Art History | Col").
          const slugv = v.replace(/[^A-Za-z0-9]+/g, "-").slice(0, 40);
          await snap(page, shots, `${slug}-${name}-${slugv}`).catch(() => {});
          const all = await dumpMenu(page, input);
          try { fs.writeFileSync(path.join(shots, `${slug}-${name}-options.json`), JSON.stringify({ wanted: v, typed_log: log, options: all }, null, 2) + "\n"); } catch (e) { /* diagnostics only */ }
          await input.fill(""); await closeMenu(page);
          const typedNothing = log.filter((l) => l.startsWith('"')).every((l) => l.endsWith("-> (nothing)"));
          fail(`${name}: "${v}" is not an option (${all.length} options in the menu${all.length ? ", e.g. " + all.slice(0, 6).join(" | ") : ""}; ${typedNothing ? "typing offered nothing" : "typed: " + log.slice(1).join("; ").slice(0, 120)}; full list in tpt/_publish/${slug}-${name}-options.json). ${log[0]}`);
          continue;
        }
        await closeMenu(page);
        // Read back: the value must now show as a chip (a select that silently dropped it would fail the form later).
        const now = await chipsOf(input);
        if (now && !now.some((t) => matchOption([t], v) >= 0 || t === v.toLowerCase())) {
          await snap(page, shots, `${slug}-${name}-dropped`).catch(() => {});
          fail(`${name}: picked "${v}" but the field now shows: ${now.join(" | ") || "(empty)"}`);
        }
      }
    };
    await pick("subjects", F.subjects, it.subjects);
    await pick("tags", F.tags, it.tags);
    await pick("formats", F.formats, it.formats);
    await pick("custom_categories", F.custom_categories, it.custom_categories);

    step = "pages";
    if (it.pages) await page.locator(F.pages).fill(String(it.pages));
    if (it.answer_key) await listbox("answer_key", F.answer_key.toggle, it.answer_key);
    if (it.teaching_duration) await listbox("teaching_duration", F.teaching_duration.toggle, it.teaching_duration);

    step = "copyright and listing status";
    const orig = page.locator(F.copyright_original);
    if ((await orig.getAttribute("aria-checked")) !== "true") await orig.click();
    const active = page.locator(F.make_active);
    if ((await active.getAttribute("aria-checked")) !== "true") await active.click();

    // Read back what the form will submit: price boxes, Free toggle and the hidden preview key. A form that
    // silently dropped a value would otherwise go live free / without a preview (027).
    step = "read back the form";
    {
      const num = async (sel) => { const v = await page.locator(sel).first().inputValue().catch(() => ""); return v === "" ? null : Number(v); };
      if (it.free === true) {
        if (F.free && (await page.locator(F.free).count())) {
          const t = (await page.locator(F.free).getAttribute("aria-checked")) === "true" || (await page.locator(F.free).isChecked().catch(() => false));
          if (!t) fail("read-back: Free Resource is not ticked");
        }
      } else {
        const t = F.free && (await page.locator(F.free).count())
          && ((await page.locator(F.free).getAttribute("aria-checked")) === "true" || (await page.locator(F.free).isChecked().catch(() => false)));
        if (t) fail('read-back: "Free Resource" is ticked on a paid item');
        for (const k of ["price", "license_price"]) {
          const v = await num(F[k]);
          if (v === null || Math.abs(v - Number(it[k])) > 0.001) fail(`read-back: ${k} box shows ${v === null ? "nothing" : v}, tpt.json says ${it[k]}`);
        }
      }
      if (files.preview && !previewAbsent) {
        const key = await page.locator(F.files.preview.key).first().inputValue().catch(() => "");
        if (!key) fail("read-back: the preview upload key is empty (the preview file is not attached)");
      }
      if (files.product) {
        const key = await page.locator(F.files.product.key).first().inputValue().catch(() => "");
        if (!key) fail("read-back: the product file key is empty");
      }
    }

    await snap(page, shots, `${slug}-filled`);
    if (dryRun) {
      console.log(problems.length ? "DRY RUN: problems to fix before publishing:\n- " + problems.join("\n- ") : "DRY RUN: every field filled with no problems.");
      console.log(`Form filled but NOT submitted. Screenshot: tpt/_publish/${slug}-filled.png`);
      return;
    }

    step = "submit";
    // Written BEFORE the click: if anything dies after it, the item is not submitted again blind (see takeLock above).
    const submittedAt = Date.now();
    writeSubmitted(item, it.title, submittedAt);
    // 20 Nov 2026 (061, 3.4 MB zip): TpT converts thumbnails and saves in the background after Submit and can take several minutes
    // (the edit form's wait allows 4+). noWaitAfter so a slow navigation never throws out of click(); wait up to 5 min for the page to leave.
    try { await page.locator(F.submit).click({ noWaitAfter: true, timeout: 30000 }); }
    catch (e) { if (!/click action done|navigation/i.test(e.message)) throw e; }
    const leftForm = () => { try { return !page.url().includes("/My-Products/New/"); } catch (e) { return false; } };
    let liveFromList = null;
    try {
      await page.waitForURL((u) => !u.toString().includes("/My-Products/New/"), { timeout: 300000 });
    } catch (e) {
      await snap(page, shots, `${slug}-submit-failed`);
      // No clear success. The product may still have been created. Look for it on the logged-in My Products list in a SECOND tab (the
      // form tab is left alone so TpT's save is never cut off) once a minute until 15 minutes after the click. Never Submit again here.
      let tab = null, last = { read: false, why: "not read yet" };
      try { tab = await context.newPage(); } catch (e2) { last.why = "could not open a tab: " + e2.message.split("\n")[0]; }
      while (tab && !liveFromList && !leftForm()) {
        try { last = await findOnMyProducts(tab, it.title); } catch (e2) { last = { read: false, why: e2.message.split("\n")[0] }; }
        if (last.url) { liveFromList = last.url; break; }
        if (Date.now() - submittedAt >= SUBMIT_SETTLE_MS) break;
        await new Promise((ok) => setTimeout(ok, 60000));
      }
      if (tab) await tab.close().catch(() => {});
      if (!liveFromList && !leftForm()) {
        const msgs = await page.locator('[role="alert"], [aria-live="assertive"], [class*="error" i]').allInnerTexts().catch(() => []);
        throw new Error(`still on the form after Submit and the title is not on My Products ${Math.round((Date.now() - submittedAt) / 60000)} min later (${last.read ? "read OK" : "My Products unreadable: " + last.why}). ` +
          `The publish-submitted-at note stays: no run submits this item again until My Products, read 15+ min after this Submit, settles it.\n` +
          `TpT says: ${msgs.map((m) => String(m == null ? "" : m).trim()).filter(Boolean).join(" | ").slice(0, 500) || "(nothing)"}\nScreenshot: tpt/_publish/${slug}-submit-failed.png`);
      }
      if (liveFromList) console.warn(`Submit gave no answer, but ${it.title} is on My Products: ${liveFromList}`);
    }
    await snap(page, shots, `${slug}-submitted`);
    const doneUrl = liveFromList || page.url();
    fs.writeFileSync(path.join(item, "uploaded"), `${new Date().toISOString()} published live by tools/tpt.js${liveFromList ? " (found on My Products after Submit gave no answer)" : ""}\n${doneUrl}\n`);
    clearSubmitted(item);
    console.log(`Published: ${it.title}\nTpT went to ${doneUrl}\nWrote ${path.relative(ROOT, item)}/uploaded`);
    // Verify the PUBLIC page against tpt.json (price, isFree, preview, pages). The item is already live, so a
    // mismatch is recorded (UPLOADER-STATUS.json live_mismatch, `live-mismatch` file) rather than thrown.
    const liveUrl = doneUrl, id = (liveUrl.match(PRODUCT_URL_RE) || [])[1];
    let verify = { ok: false, problems: ["could not read the public page"] };
    for (let attempt = 0; attempt < 4; attempt++) {
      try {
        await page.goto(liveUrl, { waitUntil: "domcontentloaded" }); await page.waitForTimeout(3000);
        const live = parseLive(await page.content(), id);
        const problems = compareLive(it, live);
        verify = { ok: problems.length === 0, problems, live };
        if (verify.ok) break;
      } catch (e) { verify = { ok: false, problems: ["could not read the public page: " + e.message.split("\n")[0]] }; }
      await page.waitForTimeout(20000); // TpT may need a moment to show a new listing
    }
    if (!verify.ok) {
      await snap(page, shots, `${slug}-live-mismatch`).catch(() => {});
      fs.writeFileSync(path.join(item, "live-mismatch"), JSON.stringify({ at: new Date().toISOString(), url: liveUrl, problems: verify.problems, live: verify.live || null }, null, 2) + "\n");
      console.error(`LIVE MISMATCH for ${slug}: ${verify.problems.join("; ")}`);
    } else console.log(`Verified on the public page: price ${verify.live.price}, isFree ${verify.live.isFree}, preview ${verify.live.previewUrl ? "yes" : "no"}.`);
    return { url: liveUrl, verify };
  } catch (e) {
    if (step === "submit" || step === "check login" || e.waiting || e.unknown) throw e;
    await snap(page, shots, `${slug}-failed`).catch(() => {});
    throw new Error(`${dryRun ? "dry run" : "publish"} stopped at step "${step}" (nothing was submitted): ${e.message.split("\n")[0]}\n` +
      `Screenshot: tpt/_publish/${slug}-failed.png\nFile inputs on the page: ${await fileInputs().catch(() => "(unreadable)")}`);
  } finally {
    await context.close();
  }
}


// ---- publish-pending (the nightly job on the owner's Mac, overseen by the cloud Manager) ----
// Publishes only items the Manager has RELEASED: tpt/NNN-slug/ with tpt.json, a QA APPROVED
// verdict, a `release` file written by the Manager, and no `uploaded` file. Does nothing while
// tpt/PAUSED exists (the owner's or the Manager's stop switch). Publishes at most MAX_PER_RUN
// items per night. Writes tpt/UPLOADER-STATUS.json, which tools/tpt-nightly.sh commits so the
// Manager can check every run and tell the owner when they're needed.
const MAX_PER_RUN = 6; // owner, 12 Nov 2026: 4 products a day plus catch-up (was 3)
// A publish that fails writes `publish-failed` (JSON: release_sha256, count, error, at). After
// PUBLISH_TRIES failures for the same `release` file the item is HELD: it is not tried again until the
// cloud rewrites `release` (any new text) after fixing the cause. The job now runs several times a day,
// and this stops one broken item from being retried, with a browser window, on every run.
const PUBLISH_TRIES = 2;
function releaseSha(d) { try { return require("crypto").createHash("sha256").update(fs.readFileSync(path.join(d, "release"))).digest("hex"); } catch (e) { return null; } }
function publishFails(d) {
  try { const j = JSON.parse(fs.readFileSync(path.join(d, "publish-failed"), "utf8")); return j.release_sha256 === releaseSha(d) ? (j.count || 0) : 0; } catch (e) { return 0; }
}
function publishHeld(d) { return publishFails(d) >= PUBLISH_TRIES; }
function pendingItems() {
  const dir = path.join(ROOT, "tpt");
  return fs.readdirSync(dir).filter((d) => /^\d{3}-/.test(d)).map((d) => path.join(dir, d))
    .filter((d) => fs.existsSync(path.join(d, "tpt.json")) && fs.existsSync(path.join(d, "release"))
      && (isApproved(d) || releasedOverQA(d)) && !fs.existsSync(path.join(d, "uploaded")) && !publishHeld(d))
    .sort();
}

// Released items (release file, no uploaded) that pendingItems() did NOT pick up, with the reason.
function releasedButSkipped() {
  const dir = path.join(ROOT, "tpt"), out = [];
  for (const n of fs.readdirSync(dir).filter((x) => /^\d{3}-/.test(x)).sort()) {
    const d = path.join(dir, n);
    if (!fs.existsSync(path.join(d, "release")) || fs.existsSync(path.join(d, "uploaded"))) continue;
    if (!fs.existsSync(path.join(d, "tpt.json"))) out.push(`${n}: no tpt.json`);
    else if (!(isApproved(d) || releasedOverQA(d))) out.push(`${n}: QA.md last verdict is not APPROVE`);
  }
  return out;
}

// Duplicate guard (13 Nov 2026). The 12 Nov run published four products but its report never reached GitHub,
// so the repo still listed them as waiting. If this machine ever loses its `uploaded` markers (a second clone,
// a failed push, a reset), the next run would publish them AGAIN. Before each publish, look for the item's exact
// title on the PUBLIC store page; if it is already live, write the marker instead of uploading.
// TpT's page addresses carry the whole title: lowercase words joined by "-", "&" and quotes dropped.
// 17 Nov 2026: the store was renamed (brian-lotze -> hudson-beat; the old address answers 404), which silently switched this guard
// off. All pages are read now, and a store page with no product links counts as "unknown" (logged), never as "not live".
const STORE_URL = "https://www.teacherspayteachers.com/store/hudson-beat?order=Most-Recent";
function slugNorm(s) { return String(s).toLowerCase().replace(/&/g, " ").replace(/'/g, "").replace(/[^a-z0-9]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, ""); }
function liveUrlForTitle(title, html) {
  const t = slugNorm(title), re = /href="(\/Product\/([^"?#]+?)-(\d+))"/g;
  let m;
  while ((m = re.exec(html))) { const slug = slugNorm(m[2]); if (slug === t || (slug.length >= 60 && t.startsWith(slug))) return "https://www.teacherspayteachers.com" + m[1]; }
  return null;
}
async function fetchStoreHtml() {
  const ua = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36" };
  const ids = new Set(); let all = "";
  try {
    for (let p = 1; p <= 10; p++) {
      const r = await fetch(p === 1 ? STORE_URL : `${STORE_URL}&page=${p}`, { headers: ua });
      if (!r.ok) { if (p === 1) { console.warn(`store page ${STORE_URL} answered ${r.status}: duplicate guard off for this run`); return null; } break; }
      const html = await r.text(), before = ids.size;
      for (const m of html.matchAll(/href="\/Product\/[^"?#]+?-(\d+)"/g)) ids.add(m[1]);
      if (ids.size === before) break; // a page with nothing new: past the last page
      all += html;
    }
  } catch (e) { return all || null; } // unknown: carry on and publish as before
  if (!ids.size) { console.warn("the store page shows no products (renamed again?): duplicate guard off for this run"); return null; }
  return all;
}

async function publishPending() {
  const status = { ran_at: new Date().toISOString(), published: [], failed: [], needs_login: false, paused: false, pending_before: [] };
  try { status.reupload = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "UPLOADER-STATUS.json"), "utf8")).reupload; } catch (e) { /* none yet */ }
  if (!status.reupload) delete status.reupload;
  const write = () => fs.writeFileSync(path.join(ROOT, "tpt", "UPLOADER-STATUS.json"), JSON.stringify(status, null, 2) + "\n");
  if (fs.existsSync(path.join(ROOT, "tpt", "PAUSED"))) {
    status.paused = true; status.ok = true; write();
    console.log("tpt/PAUSED exists: publishing nothing."); return;
  }
  const items = pendingItems().slice(0, MAX_PER_RUN);
  status.pending_before = items.map((d) => path.basename(d));
  const skipped = releasedButSkipped();
  if (skipped.length) { status.warning = `released items NOT published: ${skipped.join("; ")}`; console.warn("WARNING: " + status.warning); }
  const held = fs.readdirSync(path.join(ROOT, "tpt")).filter((n) => /^\d{3}-/.test(n) && !fs.existsSync(path.join(ROOT, "tpt", n, "uploaded")) && publishHeld(path.join(ROOT, "tpt", n)));
  if (held.length) { status.held = held; console.log(`Held after ${PUBLISH_TRIES} failed tries (rewrite \`release\` to retry): ${held.join(", ")}`); }
  const relNoUp = fs.readdirSync(path.join(ROOT, "tpt")).filter((n) => /^\d{3}-/.test(n) && fs.existsSync(path.join(ROOT, "tpt", n, "release")) && !fs.existsSync(path.join(ROOT, "tpt", n, "uploaded")) && !held.includes(n));
  if (!items.length && relNoUp.length) {
    status.warning = (status.warning ? status.warning + " | " : "") + `SANITY: 0 pending but release files without \`uploaded\` exist (${relNoUp.join(", ")}); check the repo is current and tools/tpt.js is up to date on this machine`;
    console.warn("WARNING: " + status.warning);
  }
  console.log(items.length ? `Released and waiting: ${status.pending_before.join(", ")}` : "Nothing released to publish.");
  // The duplicate guard is inside publish(): the logged-in My Products list, read before every Submit (25 Nov 2026).
  for (const item of items) {
    const slug = path.basename(item);
    const note = readSubmitted(item);
    if (note && submittedDecision(note, true, null) === "wait") {  // too early to settle: don't even open a browser
      (status.waiting = status.waiting || []).push({ item: slug, submitted_at: note.at, note: "Submit already clicked; settles on My Products 15 min after it" });
      console.log(`${slug}: Submit was clicked at ${note.at}; not submitting again until My Products settles it (15 min after).`);
      continue;
    }
    try {
      const r = await publish(item, false);
      status.published.push({ item: slug, url: (fs.readFileSync(path.join(item, "uploaded"), "utf8").split("\n")[1] || "").trim(), ...(r && r.already ? { note: "already on My Products; marker written, nothing uploaded" } : {}) });
      if (r && r.already) continue;
      try { fs.unlinkSync(path.join(item, "publish-failed")); } catch (e) { /* none */ }
      if (r && r.verify && !r.verify.ok) (status.live_mismatch = status.live_mismatch || []).push({ item: slug, url: r.url, problems: r.verify.problems });
    } catch (e) {
      const msg = e.message.split("\n").slice(0, 3).join(" ").slice(0, 400);
      status.failed.push({ item: slug, error: msg });
      console.error(`${slug}: ${msg}`);
      if (/not logged in|session expired|login failed/i.test(msg)) { status.needs_login = true; break; }
      if (e.waiting) { status.failed.pop(); (status.waiting = status.waiting || []).push({ item: slug, note: msg }); continue; }
      if (e.unknown) continue; // My Products unreadable: reported, not counted against the item
      // Count the failure (a login problem above is not the item's fault and is not counted).
      fs.writeFileSync(path.join(item, "publish-failed"), JSON.stringify({ at: new Date().toISOString(), release_sha256: releaseSha(item), count: publishFails(item) + 1, error: msg }, null, 2) + "\n");
    }
  }
  status.ok = !status.needs_login && status.failed.length === 0 && !(status.live_mismatch || []).length;
  write();
  console.log(`Published ${status.published.length}, failed ${status.failed.length}${status.needs_login ? " (TpT login expired: run node tools/tpt.js login)" : ""}.`);
  if (!status.ok) process.exitCode = 1;
}

// ---- reupload: replace ONLY the files of a live product (owner exception, 22 Oct 2026) ----------
// Markers in tpt/NNN-slug/ (all written/read as plain files; git is the state):
//   uploaded        written by publish; line 2 is the product URL
//   reupload        written by the Manager after QA approval of the rebuild (date + reason). A new
//                   marker (different content) is the ONLY thing that allows another replacement.
//   reuploaded      written here on success: JSON, time + marker hash + sha256 of every file replaced
//   reupload-failed written here on any mismatch/failure: holds the marker hash so the same marker is
//                   never retried blindly. The Manager reads UPLOADER-STATUS.json, then writes a new
//                   marker (or the owner deletes this file) once the cause is understood.
const crypto = require("crypto");
const EDIT_FIELDS = () => path.join(ROOT, "tpt", "EDIT-FIELDS.json");
const PRODUCT_URL_RE = /^https:\/\/www\.teacherspayteachers\.com\/Product\/[^\s]+-(\d+)$/;
const FILE_SLOTS = ["product", "preview", "thumb1", "thumb2", "thumb3", "thumb4"];

function sha256File(fp) { return crypto.createHash("sha256").update(fs.readFileSync(fp)).digest("hex"); }
function readTrim(fp) { try { return fs.readFileSync(fp, "utf8"); } catch (e) { return null; } }

// One of: tpt-bundle | no-marker | no-url | not-approved | done | failed-hold | pending. Pure file reads.
// `tpt-bundle` (23 Nov 2026, 030): the listing was upgraded on TpT to a real Bundle (it links the single units; no ZIP slot), so the
// ZIP-replacing flow must never touch it, whatever the `reupload` marker says. Delete the file only if the listing goes back to a ZIP.
function reuploadState(item) {
  const bundle = readTrim(path.join(item, "tpt-bundle"));
  if (bundle !== null) return { state: "tpt-bundle", reason: "`tpt-bundle` file: this listing is a TpT Bundle (linked units, no product ZIP); file replacement is never done here. Edit it on TpT by hand" };
  const marker = readTrim(path.join(item, "reupload"));
  if (marker === null || !marker.trim()) return { state: "no-marker", reason: "no `reupload` marker (the Manager writes it after QA approves the rebuild)" };
  const markerHash = crypto.createHash("sha256").update(marker).digest("hex");
  const up = readTrim(path.join(item, "uploaded"));
  let url = up ? (up.split("\n")[1] || "").trim() : "";
  // 014 (17 Nov 2026): `uploaded` says "owner confirmed live ... (URL not yet recorded)". The Mac then looks the listing up on the
  // logged-in My Products page by its exact title and writes the URL into `live-url` (line 1); `uploaded` is never rewritten.
  if (up && !PRODUCT_URL_RE.test(url)) { const lu = (readTrim(path.join(item, "live-url")) || "").split("\n")[0].trim(); if (PRODUCT_URL_RE.test(lu)) url = lu; }
  if (!up) return { state: "no-url", markerHash, reason: "no `uploaded` file: the product is not live, nothing to replace (publish it instead)" };
  if (!PRODUCT_URL_RE.test(url)) return { state: "no-url", markerHash, lookup: true, reason: `\`uploaded\` line 2 is not a TpT product URL (${JSON.stringify(url)}) and there is no \`live-url\`: the Mac looks it up on My Products by title` };
  if (!isApproved(item)) return { state: "not-approved", markerHash, url, reason: "QA.md has no '**Verdict: APPROVED**' line" };
  const done = readTrim(path.join(item, "reuploaded"));
  if (done) { try { if (JSON.parse(done).marker_sha256 === markerHash) return { state: "done", markerHash, url, reason: "this reupload marker was already processed (see `reuploaded`); write a new marker to replace again" }; } catch (e) { /* unreadable: treat as not done */ } }
  const unv = readTrim(path.join(item, "reupload-unverified"));
  if (unv) { try { const u = JSON.parse(unv); if (u.marker_sha256 === markerHash) return { state: "unverified", markerHash, url, rec: u, reason: "submitted; waiting to see the new files on the edit page (never resubmitted)" }; } catch (e) { return { state: "failed-hold", markerHash, url, reason: "`reupload-unverified` is unreadable; a person must check the product on TpT" }; } }
  const failed = readTrim(path.join(item, "reupload-failed"));
  if (failed) { try { if (JSON.parse(failed).marker_sha256 === markerHash) return { state: "failed-hold", markerHash, url, reason: "an earlier attempt for this marker failed (see `reupload-failed`); not retrying until a new marker is written or that file is deleted" }; } catch (e) { return { state: "failed-hold", markerHash, url, reason: "`reupload-failed` exists and is unreadable; not retrying" }; } }
  return { state: "pending", markerHash, url, productId: url.match(PRODUCT_URL_RE)[1], directives: parseMarker(marker) };
}

// Marker directives (plain lines in the `reupload` file; everything else is free text for humans):
//   files: none           replace no files (default: replace every file listed in tpt.json)
//   fix: price, preview   OWNER-APPROVED CORRECTIVE CASE (23 Oct 2026, "fix 027"): also set the product's
//                         price + license price to tpt.json's values and un-tick Free (`price`), and attach the
//                         preview PDF (`preview`), then verify the public page. Nothing else may be fixed.
const FIX_TOKENS = ["price", "preview"];
function parseMarker(text) {
  const out = { files: true, fix: [], problems: [] };
  for (const line of String(text || "").split("\n")) {
    let m = line.match(/^\s*files\s*:\s*(.*?)\s*$/i);
    if (m) { if (/^none$/i.test(m[1])) out.files = false; else if (!/^(yes|all)?$/i.test(m[1])) out.problems.push(`marker: unknown \`files:\` value ${JSON.stringify(m[1])} (use \`files: none\` or leave it out)`); continue; }
    m = line.match(/^\s*fix\s*:\s*(.*?)\s*$/i);
    if (m) for (const t of m[1].split(/[\s,]+/).filter(Boolean)) {
      if (!FIX_TOKENS.includes(t.toLowerCase())) out.problems.push(`marker: unknown fix ${JSON.stringify(t)} (allowed: ${FIX_TOKENS.join(", ")})`);
      else if (!out.fix.includes(t.toLowerCase())) out.fix.push(t.toLowerCase());
    }
  }
  return out;
}

function idOf(sel) { const m = String(sel || "").match(/#([\w-]+)\s*$/); return m ? m[1] : null; }
function editSel(F, slot) { return { ...(F.files[slot] || {}), ...((F.edit && F.edit.files && F.edit.files[slot]) || {}) }; }

// Everything checkable without a browser. Returns { problems, files, state }.
function prepareReupload(item, F, editFields) {
  const st = reuploadState(item), problems = [], files = [];
  if (st.state !== "pending") return { problems: [st.reason], files, state: st };
  let cfg; try { cfg = JSON.parse(fs.readFileSync(path.join(item, "tpt.json"), "utf8")); } catch (e) { return { problems: ["tpt.json unreadable: " + e.message], files, state: st }; }
  const dir = st.directives, fix = dir.fix;
  problems.push(...dir.problems);
  const listed = cfg.files || {};
  if (dir.files && !listed.product) problems.push("tpt.json: files.product is not set");
  if (fix.includes("price")) {
    for (const k of ["price", "license_price"]) if (!/^\d+(\.\d{2})?$/.test(String(cfg[k] ?? "")) || !(Number(cfg[k]) > 0)) problems.push(`fix price: tpt.json ${k} must be a price above 0 like "3.75" (got ${JSON.stringify(cfg[k])})`);
    if (cfg.free === true) problems.push('fix price: tpt.json says "free": true; this fix only sets a paid price');
    if (!cfg.tax_code) problems.push("fix price: tpt.json tax_code is not set");
  }
  if (fix.includes("preview") && !listed.preview) problems.push("fix preview: tpt.json files.preview is not set");
  for (const slot of FILE_SLOTS) {
    if (!listed[slot]) continue;
    if (!dir.files && !(fix.includes("preview") && slot === "preview")) continue; // files: none -> only what a fix needs
    const fp = path.join(item, listed[slot]);
    if (!fs.existsSync(fp)) { problems.push(`missing file ${fp}`); continue; }
    const bytes = fs.statSync(fp).size, spec = F.files[slot];
    if (!spec) { problems.push(`FORM.json has no file slot ${slot}`); continue; }
    if (!bytes) problems.push(`${listed[slot]} is empty`);
    if (bytes / 1048576 > spec.max_mb) problems.push(`${listed[slot]} is ${(bytes / 1048576).toFixed(1)} MB (max ${spec.max_mb} MB for ${slot})`);
    files.push({ slot, file: listed[slot], path: fp, bytes, sha256: sha256File(fp) });
  }
  for (const k of Object.keys(listed)) if (!FILE_SLOTS.includes(k)) problems.push(`tpt.json: unknown file slot ${k}`);
  if (!files.length && !fix.length) problems.push("marker asks for nothing: no files and no fix");
  if (editFields !== undefined) { // null/invalid = discover-edit has not run yet
    if (!editFields || !Array.isArray(editFields.fields) || !editFields.fields.length)
      problems.push("tpt/EDIT-FIELDS.json is missing or empty: the edit form is not recorded yet. The next nightly run records it (node tools/tpt.js discover-edit); reupload acts after that");
    else {
      if (!editFields.edit_url_template && !editFields.edit_link_text) problems.push("tpt/EDIT-FIELDS.json records no way to reach the edit page (edit_url_template / edit_link_text)");
      const ids = new Set(editFields.fields.map((f) => f.id).filter(Boolean));
      for (const f of files) {
        const id = idOf(editSel(F, f.slot).input);
        if (!id || !ids.has(id)) problems.push(`edit form has no file box for ${f.slot} (${editSel(F, f.slot).input}); set edit.files.${f.slot} in tpt/FORM.json from tpt/EDIT-FIELDS.json`);
      }
      // Price, license price and tax code are CONDITIONAL on the edit form: TpT hides them while Free Resource is ON
      // (027 went live free). So the only control that must already exist is the Free Resource toggle.
      if (fix.includes("price")) {
        const id = idOf(F.free);
        if (!id || !ids.has(id)) problems.push(`fix price: edit form has no Free Resource control (${F.free}); see tpt/EDIT-FIELDS.json`);
      }
    }
  }
  return { problems, files, state: st, fix, cfg };
}

function readEditFields() { try { return JSON.parse(fs.readFileSync(EDIT_FIELDS(), "utf8")); } catch (e) { return null; } }

function recordReuploadStatus(patch) {
  const fp = path.join(ROOT, "tpt", "UPLOADER-STATUS.json");
  let cur = {}; try { cur = JSON.parse(fs.readFileSync(fp, "utf8")); } catch (e) { /* new file */ }
  cur.reupload = { ...(cur.reupload || {}), ...patch };
  fs.writeFileSync(fp, JSON.stringify(cur, null, 2) + "\n");
}

// ---- edit-form upload helpers (16 Nov 2026) ------------------------------------------------------------------------------
// EVIDENCE (007, run of 16 Nov 17:15 UTC, screenshot tpt/_publish/007-music-sub-plans-k5-reupload-failed.png): after the old card was
// removed, the new file went to S3 (PUT 200), TpT's own processing ran (POST /uploads/process_file 200, then POST /queue/results x3),
// and the Files box then showed "music-sub-plans-k5.pdf 99% Cancel" in a red box with "Error during file upload, please try again."
// TpT's widget clears the hidden key on that error, so the old code waited 15 min for a key that could never come. In 002 (same code,
// same morning) the product upload DID register (key set) and was still "Processing..." when the preview step started; the preview
// removal then clicked controls of the processing product box. So: (1) watch the widget itself, not only the key: an error means
// "clear it and try again" (up to 3 tries, the third through TpT's own Select-file chooser), and success means key set AND no
// "Processing"/percent/error left in this slot's box; (2) keep every non-GET request/response, the bodies of TpT's process_file and
// queue/results answers, console errors and the box's HTML, and write them next to the screenshot so one more failure shows WHY.
function classifyWidget(text) {
  const t = String(text || "").replace(/\s+/g, " ");
  const pct = t.match(/\b(\d{1,3})\s?%/);
  return {
    error: /error during (the )?file upload|please try again|upload failed|could not be (uploaded|processed)|failed to (upload|process)|something went wrong/i.test(t),
    processing: /processing|uploading|please wait/i.test(t),
    percent: pct ? Number(pct[1]) : null,
  };
}
// Diagnostics are pushed to GitHub: drop query strings and anything that looks like a token or signature.
function redact(str) {
  return String(str == null ? "" : str)
    .replace(/(https?:\/\/[^\s"'?]+)\?[^\s"']*/g, "$1?…")
    .replace(/("?(?:[\w-]*token|csrf[\w-]*|signature|policy|x-amz-[\w-]+|authenticity[\w-]*|password|session[\w-]*|cookie)"?\s*[:=]\s*"?)[^"&\s,}]{6,}/gi, "$1[redacted]");
}
// tpt/REUPLOAD-PAUSED: pauses every file replacement. A line `allow: 043, 012` lets ONLY those item numbers through (a canary).
function parsePause(text) {
  if (text === null || text === undefined) return { paused: false, allow: null };
  const allow = [];
  for (const line of String(text).split("\n")) {
    const m = line.match(/^\s*allow\s*:\s*(.*)$/i);
    if (m) for (const n of m[1].split(/[\s,]+/).filter(Boolean)) { const d = n.match(/^(\d{1,3})/); if (d) allow.push(d[1].padStart(3, "0")); }
  }
  return { paused: true, allow: allow.length ? allow : null };
}
function pauseAllows(pause, item) {
  if (!pause.paused) return true;
  return !!pause.allow && pause.allow.includes(path.basename(item).slice(0, 3));
}
// This slot's upload box: climb from its file input while the parent holds no OTHER file input; without the input (TpT may drop it
// while a file is in flight), the smallest block that names the file or shows the upload error.
async function widgetState(page, inputSel, fileName) {
  const raw = await page.evaluate(([sel, name]) => {
    const inp = sel ? document.querySelector(sel) : null;
    let box = null;
    if (inp) { box = inp; while (box.parentElement && !box.parentElement.matches("form, main, body") && box.parentElement.querySelectorAll('input[type="file"]').length <= 1) box = box.parentElement; }
    if (!box) {
      const cands = [...document.querySelectorAll("div, li, section")].filter((e) => (e.innerText || "").includes(name) || /error during (the )?file upload/i.test(e.innerText || ""));
      box = cands.filter((e) => !cands.some((o) => o !== e && e.contains(o)))[0] || null;
      if (box) for (let i = 0; i < 3 && box.parentElement && !box.parentElement.matches("form, main, body"); i++) box = box.parentElement;
    }
    return { inputFound: !!inp, inputVisible: !!(inp && inp.offsetParent), boxFound: !!box, text: box ? (box.innerText || "").replace(/\s+/g, " ").trim().slice(0, 600) : "", html: box ? box.outerHTML.replace(/\s+/g, " ").slice(0, 6000) : "" };
  }, [inputSel, fileName]).catch((e) => ({ inputFound: false, boxFound: false, text: "", html: "", evalError: e.message.split("\n")[0] }));
  return { ...raw, ...classifyWidget(raw.text) };
}
// Records, until stop(): every non-GET request and its answer, failed requests, bodies of TpT's upload answers, console errors.
function startCapture(page) {
  const log = { requests: [], failed: [], bodies: [], console: [] };
  const t0 = Date.now(), at = () => `+${((Date.now() - t0) / 1000).toFixed(1)}s`;
  const onReq = (q) => { try { if (q.method() !== "GET") log.requests.push(`${at()} -> ${q.method()} ${redact(q.url()).slice(0, 140)}${/process_file|queue\/results|upload/i.test(q.url()) && q.postData() ? " body " + redact(q.postData()).slice(0, 400) : ""}`); } catch (e) {} };
  const onResp = async (r) => {
    try {
      const q = r.request(); if (q.method() === "GET") return;
      log.requests.push(`${at()} <- ${q.method()} ${r.status()} ${redact(r.url()).slice(0, 140)}`);
      if (/teacherspayteachers\.com\/(uploads|queue)\//i.test(r.url()) && log.bodies.length < 40) log.bodies.push(`${at()} ${q.method()} ${r.status()} ${redact(r.url()).slice(0, 100)} => ${redact(await r.text().catch(() => "(unreadable)")).replace(/\s+/g, " ").slice(0, 1000)}`);
    } catch (e) {}
  };
  const onFail = (q) => { try { log.failed.push(`${at()} ${q.method()} ${redact(q.url()).slice(0, 140)}: ${(q.failure() && q.failure().errorText) || "?"}`); } catch (e) {} };
  const onConsole = (m) => { try { if (/error|warning/.test(m.type()) && log.console.length < 60) log.console.push(`${at()} ${m.type()}: ${redact(m.text()).slice(0, 300)}`); } catch (e) {} };
  const onPageErr = (e) => { if (log.console.length < 60) log.console.push(`${at()} pageerror: ${redact(e.message).slice(0, 300)}`); };
  page.on("request", onReq); page.on("response", onResp); page.on("requestfailed", onFail); page.on("console", onConsole); page.on("pageerror", onPageErr);
  return { log, stop: () => { page.off("request", onReq); page.off("response", onResp); page.off("requestfailed", onFail); page.off("console", onConsole); page.off("pageerror", onPageErr); return log; } };
}
// After a widget error: press the box's own Cancel / remove control (never a link, never revision history), then wait for the box to
// be empty again. Returns a short description of what happened.
async function resetWidget(page, inputSel, fileName) {
  const clicked = await page.evaluate(([sel, name]) => {
    const inp = sel ? document.querySelector(sel) : null;
    let box = inp;
    if (box) while (box.parentElement && !box.parentElement.matches("form, main, body") && box.parentElement.querySelectorAll('input[type="file"]').length <= 1) box = box.parentElement;
    if (!box) {
      const c = [...document.querySelectorAll("div, li, section")].filter((e) => (e.innerText || "").includes(name) || /error during (the )?file upload/i.test(e.innerText || ""));
      box = c.filter((e) => !c.some((o) => o !== e && e.contains(o)))[0];
      for (let i = 0; box && i < 3 && box.parentElement && !box.parentElement.matches("form, main, body"); i++) box = box.parentElement;
    }
    if (!box) return null;
    const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
    const ctl = [...box.querySelectorAll("button, [role=button], a, span, i, div")].filter(vis)
      .filter((e) => !/revision|history|select file/i.test(e.innerText || "") && !(e.closest("a[href]") && !/^(#|javascript:)/i.test(e.closest("a[href]").getAttribute("href") || "#")))
      .find((e) => /^(cancel|remove|delete|try again|retry|[x×✕✖])$/i.test((e.innerText || "").trim()) || /cancel|remove|delete|close/i.test(`${e.getAttribute("aria-label") || ""} ${typeof e.className === "string" ? e.className : ""}`));
    if (!ctl) return null;
    const t = ctl.closest("button, [role=button]") || ctl; t.setAttribute("data-tpt-reset", "1");
    return `${t.tagName.toLowerCase()} "${(t.innerText || t.getAttribute("aria-label") || "").trim().slice(0, 30)}"`;
  }, [inputSel, fileName]).catch(() => null);
  if (!clicked) return "no Cancel/remove control in the box";
  await page.locator('[data-tpt-reset="1"]').first().click({ timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(1500);
  const dialog = page.locator('[role="dialog"], [role="alertdialog"]').filter({ has: page.locator("button") }).first();
  if (await dialog.isVisible().catch(() => false)) { const yes = dialog.getByRole("button", { name: /^(yes,? )?(cancel upload|remove|delete|confirm|yes|ok)\b/i }).last(); if (await yes.count()) await yes.click({ timeout: 10000 }).catch(() => {}); }
  await page.evaluate(() => document.querySelectorAll("[data-tpt-reset]").forEach((e) => e.removeAttribute("data-tpt-reset"))).catch(() => {});
  await page.waitForTimeout(3000);
  return `clicked ${clicked}`;
}

// ---- save + verify (16 Nov 2026, canary 043 run 2) -----------------------------------------------------------------------------------
// 043 uploaded every file and clicked Submit; the check then failed and the edit page still showed the OLD files. Two bugs of ours:
// (a) after Submit the code waited ~5 s and navigated away, which can cut TpT's save off (publish() waits up to 120 s for the page to
// leave the form); (b) it verified by the hidden upload key, which is ALWAYS empty for stored files on a fresh edit page. Now: wait for
// the save like publish() does and record TpT's answer; verify by the FILE CARDS (size for PDFs; "Last updated" moved forward for
// any file, since TpT shows thumbnails at a converted size). If the cards still show the old files right after a save that TpT
// answered, write `reupload-unverified`; later runs look again (>= 70 min, then >= 3 h) and NEVER resubmit meanwhile.
const UNVERIFIED_CHECKS_MIN = [70, 180];
function parseCard(text) {
  const t = String(text || "").replace(/\s+/g, " ");
  const name = (t.match(/([\w\-.()]+\.(?:pdf|png|jpe?g|gif|zip|pptx?|docx?))/i) || [])[1];
  const sz = t.match(/([\d.,]+)\s*(kB|KB|MB|bytes)\b/);
  const sizeKb = sz ? Number(sz[1].replace(/,/g, "")) * (/MB/.test(sz[2]) ? 1024 : /bytes/.test(sz[2]) ? 1 / 1024 : 1) : null;
  const u = t.match(/Last updated:?\s*([A-Z][a-z]{2,8} \d{1,2}, \d{4}) at (\d{1,2}:\d{2}) ?([AP]M)\s*(EST|EDT|PST|PDT|CST|CDT|MST|MDT|UTC|GMT)?/);
  let updated = null;
  if (u) {
    const off = { EST: "-0500", EDT: "-0400", CST: "-0600", CDT: "-0500", MST: "-0700", MDT: "-0600", PST: "-0800", PDT: "-0700", UTC: "+0000", GMT: "+0000" }[u[4] || "EST"];
    const ms = Date.parse(`${u[1]} ${u[2]} ${u[3]} GMT${off}`);
    updated = Number.isFinite(ms) ? ms : null;
  }
  return { name: name || null, sizeKb, updated, text: t.trim().slice(0, 200) };
}
// TpT already holds this product/preview PDF: its card shows exactly the file's size (kB, 2 decimals). Never for thumbnails. Pure.
function sameFileOnTpt(slot, card, bytes) {
  if (!/^(product|preview)$/.test(slot)) return false;
  const c = parseCard(card);
  return c.sizeKb !== null && Math.abs(c.sizeKb - bytes / 1024) <= 0.006;
}
// "match" (the new file is on the card) | "old" (still the old file) | "unknown". Pure.
function cardVerdict(oldCard, newCard, file, slot) {
  const o = parseCard(oldCard), n = parseCard(newCard), wantKb = file.bytes / 1024;
  // 028 (18 Nov): a FREE item's edit form keeps no preview (TpT shows an empty "Select file" box before and after); nothing to verify
  const empty = (t) => /select file/i.test(t || "") && !parseCard(t).name; // "Up to 30 MB" is not a file
  if (slot === "preview" && file.free && empty(oldCard) && empty(newCard)) return "match";
  const sizeOk = n.sizeKb !== null && Math.abs(n.sizeKb - wantKb) <= Math.max(0.6, wantKb * 0.005);
  if (sizeOk && !/^thumb/.test(slot)) return "match"; // TpT shows thumbnails at a converted size: only the date counts for them
  if (n.updated && o.updated && n.updated > o.updated) return "match";
  if (n.updated && !o.updated && file.savedAt && n.updated >= file.savedAt - 2 * 3600e3) return "match";
  if (o.text && n.sizeKb === o.sizeKb && n.updated === o.updated) return "old";
  return "unknown";
}
// Text of each slot's file card on the edit page (the box around the slot's file input).
async function readCards(page, F, slots) {
  const out = {};
  for (const slot of slots) out[slot] = (await widgetState(page, editSel(F, slot).input, "")).text || "";
  return out;
}
// Click Submit and wait for TpT to answer, like publish(): the page leaves the edit URL, or TpT's save request (a non-GET page
// navigation) answers, or a success message shows. Records the request and messages. Returns { ok, how, status, messages, network }.
async function submitAndWait(page, submit, editUrl, opts = {}) {
  const cap = startCapture(page), limit = opts.timeoutMs || 240000; // thumbnail conversion runs before the real save
  const t0 = Date.now();
  // 17 Nov 2026 (020-036 stuck "unverified"): Submit first POSTs the thumbnails to /converter/convert_thumbs (a navigation request,
  // answered 200), polls /queue/results ({"status":0} = still converting), and only THEN posts the real form, which answers 302. The
  // old wait took that first 200 as "the save answered" and navigated away ~3 s later, aborting TpT's real save. Now only the MAIN
  // frame's form post to the product (not converter/queue/analytics) counts: 3xx = saved; 2xx = TpT showed the form again = refused.
  const isSave = (r) => { try { const q = r.request(); return q.method() !== "GET" && q.isNavigationRequest() && r.frame() === page.mainFrame() && !/\/(converter|queue|uploads)\//i.test(r.url()) && /\/(itemsDigital|items|My-Products|product)/i.test(r.url()); } catch (e) { return false; } };
  const navResp = page.waitForResponse(isSave, { timeout: limit }).catch(() => null);
  const left = page.waitForURL((u) => u.toString().split("#")[0] !== editUrl.split("#")[0], { timeout: limit }).then(() => true, () => false);
  // click() waits for the navigation it starts and throws after its timeout; a slow save is exactly what we want to wait out, so a
  // timeout AFTER the click was done is not an error (the loop below keeps waiting up to `limit`).
  try { await submit.first().click({ noWaitAfter: true, timeout: 15000 }); }
  catch (e) { if (!/click action done|navigation/i.test(e.message)) { cap.stop(); throw e; } }
  const okRe = /(successfully|has been (saved|updated)|changes (were |have been )?saved|product (was |has been )?updated)/i;
  const errRe = /(error|failed|is required|please (correct|fix)|could not|cannot|can't)/i;
  // 17 Nov 2026 (canary 3): an SVG matched by these class selectors (the spinner beside Submit) has NO innerText, so allInnerTexts()
  // gave null and x.replace threw "Cannot read properties of undefined (reading 'replace')" in the middle of the save; the browser
  // then closed and very likely cut the save off. SVGs are excluded, a missing text reads as "", and the whole read can never throw.
  // only VISIBLE messages: TpT keeps hidden templates in the page (e.g. "We cannot generate images from your file", which showed up in
  // every 17 Nov record although nothing was shown)
  const readMsgs = () => page.locator(':is([role="alert"], [aria-live="assertive"], [class*="flash" i], [class*="alert" i], [class*="success" i], [class*="error-message" i], [class*="error" i]):not(svg, svg *)')
    .evaluateAll((els) => els.filter((e) => { const r = e.getBoundingClientRect(), cs = getComputedStyle(e); return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none"; })
      .map((e) => String(e.innerText == null ? "" : e.innerText).replace(/\s+/g, " ").trim()).filter(Boolean).filter((t, i, a) => a.indexOf(t) === i).slice(0, 12)).catch(() => []);
  let how = null, status = null, messages = [];
  let navDone = null, leftDone = false, refused = false;
  navResp.then((r) => { navDone = r; });
  left.then((v) => { leftDone = v; });
  const loopErrors = [];
  while (Date.now() - t0 < limit && !how) {
    // ANY unexpected error in here is logged (with its stack) and the wait goes on: the save is in flight and must not be cut off.
    try {
    await page.waitForTimeout(500);
    if (navDone) {
      status = navDone.status(); await page.waitForLoadState("domcontentloaded", { timeout: 60000 }).catch(() => {});
      how = `TpT answered the save (${navDone.request().method()} ${status} ${navDone.url().replace(/\?.*/, "").slice(0, 100)})`;
      if (status >= 200 && status < 300) refused = true; // the form came back instead of a redirect: TpT did not save it
      break;
    }
    if (leftDone) { how = `the page left the edit form (${page.url().replace(/\?.*/, "")})`; break; }
    // the edit form may save with a background request instead of a page load: a 2xx/3xx answer to a non-GET request to TpT's
    // product endpoints (not graphql/analytics) counts as the save answer once the page has been quiet for 3 s
    const xhr = cap.log.requests.filter((x) => /<- (POST|PUT|PATCH) [23]\d\d https:\/\/(www\.)?(teacherspayteachers\.com|tpt\.test)\/(itemsDigital|items|My-Products|product)/i.test(x) && !/\/(converter|queue|uploads)\//i.test(x));
    if (xhr.length && Date.now() - t0 > 3000) { await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {}); status = Number((xhr[xhr.length - 1].match(/ ([23]\d\d) /) || [])[1]) || null; how = `TpT answered the save (${xhr[xhr.length - 1].replace(/^\S+ <- /, "").slice(0, 120)})`; break; }
    messages = await readMsgs();
    if (messages.some((m) => okRe.test(m))) { how = "TpT showed a success message"; break; }
    } catch (e) {
      const st = String((e && e.stack) || e).split("\n").slice(0, 8).join(" | ");
      if (loopErrors.length < 5) loopErrors.push(st);
      console.error(`save wait: unexpected error (still waiting for TpT): ${st}`);
      await new Promise((ok) => setTimeout(ok, 1000));
    }
  }
  if (!how) await page.waitForLoadState("networkidle", { timeout: Math.max(1000, limit - (Date.now() - t0)) }).catch(() => {}); // never leave mid-save
  await page.waitForTimeout(opts.settleMs ?? 3000).catch(() => {});
  messages = await readMsgs();
  const network = cap.stop();
  const bad = refused || (status !== null && status >= 400) || messages.some((m) => errRe.test(m) && !okRe.test(m));
  return { ok: !!how && !bad, how: (how || `no answer from TpT within ${Math.round(limit / 1000)} s`) + (refused ? " = TpT showed the form again (not saved)" : ""), status, messages, loop_errors: loopErrors,
    network: { requests: network.requests.slice(-30), bodies: network.bodies.slice(-6), failed: network.failed.slice(-10), console: network.console.slice(-15) } };
}

// One file slot on the EDIT form: remove the old card, upload, retry on TpT's own error. Returns { ok, key, diag } or
// { error, diagnostics } (the caller records it). opts: { slot, spec: {input, key}, filePath, slug, shots, minutesPerTry, resetWaitMs }.
async function uploadEditSlot(page, opts) {
  const { slot, spec, filePath, slug, shots } = opts, base = path.basename(filePath);
  const cap = startCapture(page); // from BEFORE the removal: the X click may itself talk to TpT
  const diag = { slot: slot, file: path.basename(filePath), attempts: [], widget: [] };
  const diagFile = path.join(shots, `${slug}-reupload-${slot}-diag.json`);
  const failSlot = async (msg) => {
    diag.network = cap.stop();
    try { fs.mkdirSync(shots, { recursive: true }); fs.writeFileSync(diagFile, JSON.stringify(diag, null, 2) + "\n"); } catch (e) { /* diagnostics only */ }
    return { error: msg, diagnostics: { diag_file: path.relative(ROOT, diagFile), attempts: diag.attempts, widget_last: diag.widget.slice(-2),
      tpt_upload_answers: diag.network.bodies.slice(-8), non_get: diag.network.requests.slice(-40), request_failures: diag.network.failed.slice(-10), console_errors: diag.network.console.slice(-20) } };
  };
  const rm = await removeExistingFile(page, slot, { shots, slug, inputSel: spec.input });
  console.log(`${slot}: existing file: ${rm.skipped || rm.ok || "ERROR " + rm.error}`);
  await snap(page, shots, `${slug}-reupload-${slot}-after-remove`).catch(() => {});
  diag.remove = rm;
  diag.widget.push({ when: "after remove", ...(await widgetState(page, spec.input, base)) });
  // A thumbnail's input stays in its box next to the old card, and success requires the key to CHANGE from the old value, so a
  // thumbnail whose card could not be removed is uploaded in place; the product/preview still stop (their box has no usable input then).
  if (rm.error && !/^thumb/.test(slot)) return failSlot(`could not remove the existing ${slot} file before uploading: ${rm.error}`);
  if (rm.error) { console.log(`${slot}: card not removed (${rm.error.slice(0, 120)}); uploading in place, the key must change`); diag.replaced_in_place = true; }
  try { await page.locator(spec.input).waitFor({ state: "attached", timeout: 20000 }); } catch (e) { return failSlot(`no upload box ${spec.input} on the edit page after removing the old file`); }
  const minutes = opts.minutesPerTry || (slot === "product" ? 6 : slot === "preview" ? 4 : 2); // PER attempt, 3 attempts
  const keyProbe = () => page.evaluate(([s, slot]) => {
    let el = document.querySelector(s);
    const hidden = [...document.querySelectorAll('input[type="hidden"]')].filter((e) => /ItemDigital|upload|file/i.test(e.name || e.id || ""));
    if (!el) el = hidden.find((e) => new RegExp(slot.replace(/\d+$/, (d) => ".*" + d), "i").test(e.name || e.id || "")) || null;
    return { found: !!el, name: el ? el.name || el.id : null, value: el ? el.value : "", hidden: hidden.map((e) => `${e.name || e.id}=${String(e.value).slice(0, 40)}`).slice(0, 25) };
  }, [spec.key, slot]);
  const oldKey = (await keyProbe()).value;
  // Wait for THIS slot's widget: error -> { error }, key set and the box idle (no processing / percent / error) twice in a row -> { ok }.
  const settle = async (ms) => {
    const t0 = Date.now(); let goodSince = null, w = null, k = null;
    while (Date.now() - t0 < ms) {
      k = await keyProbe().catch(() => null); w = await widgetState(page, spec.input, base);
      if (w.error) return { error: w.text, w, k };
      const keyOk = k && k.found && k.value && k.value !== oldKey;
      const idle = !w.processing && !(w.percent !== null && w.percent < 100) ;
      if (keyOk && idle) { if (goodSince && Date.now() - goodSince >= 2000) return { ok: true, w, k }; goodSince = goodSince || Date.now(); }
      else goodSince = null;
      await page.waitForTimeout(1000);
    }
    return { timeout: true, w, k };
  };
  let got = null;
  for (let attempt = 1; attempt <= 3 && !got; attempt++) {
    const how = attempt < 3 ? "setInputFiles" : "TpT's Select-file button + file chooser";
    const rec = { attempt, how, started: new Date().toISOString() };
    diag.attempts.push(rec);
    try {
      if (attempt < 3) await page.locator(spec.input).setInputFiles(filePath, { timeout: 30000 });
      else {
        const area = page.locator(spec.input).locator("xpath=ancestor::*[.//button[normalize-space()='Select file'] or .//label][1]");
        const label = page.locator("label", { has: page.locator(spec.input) }).first();
        const btn = area.getByRole("button", { name: /select file/i }).first();
        const clicker = (await btn.count()) ? btn : label;
        const [chooser] = await Promise.all([page.waitForEvent("filechooser", { timeout: 15000 }), clicker.click({ timeout: 15000 })]);
        await chooser.setFiles(filePath);
      }
    } catch (e) { rec.result = "could not set the file: " + e.message.split("\n")[0]; diag.widget.push({ when: `attempt ${attempt} set failed`, ...(await widgetState(page, spec.input, base)) }); continue; }
    const r = await settle(minutes * 60000);
    diag.widget.push({ when: `attempt ${attempt} end`, ...r.w, key: r.k ? `${r.k.name}=${r.k.value ? "set" : "empty"}` : "?" });
    if (r.ok) { got = r.k; rec.result = "ok"; break; }
    rec.result = r.error ? `TpT's box says: ${r.error.slice(0, 200)}` : `no result in ${minutes} min (box: ${(r.w && r.w.text || "").slice(0, 120)}; key ${r.k && r.k.value ? "set" : "empty"})`;
    console.log(`${slot}: attempt ${attempt} (${how}) failed: ${rec.result}`);
    await snap(page, shots, `${slug}-reupload-${slot}-attempt${attempt}-failed`).catch(() => {});
    if (attempt < 3) { rec.reset = await resetWidget(page, spec.input, base); await page.waitForTimeout(opts.resetWaitMs ?? 20000); diag.widget.push({ when: `after reset ${attempt}`, ...(await widgetState(page, spec.input, base)) }); }
  }
  if (!got) {
    const k = await keyProbe().catch(() => ({ found: false, hidden: [], value: "" }));
    return failSlot(`TpT did not accept ${path.basename(filePath)} after 3 tries (${diag.attempts.map((x) => `#${x.attempt} ${x.how}: ${x.result}`).join(" | ").slice(0, 600)}). Key ${k.found ? k.name : "NOT FOUND with " + spec.key} ${k.value ? "set" : "empty"}; hidden inputs: ${k.hidden.join(", ") || "(none)"}. Full diagnostics: ${path.relative(ROOT, diagFile)}`);
  }
  const log = cap.stop();
  console.log(`${slot}: uploaded (${diag.attempts.length} ${diag.attempts.length === 1 ? "try" : "tries"}); TpT answers: ${log.bodies.slice(-2).join(" | ").slice(0, 300) || "(none)"}`);
  return { ok: true, key: got.value, diag };
}

async function reupload(item, dryRun) {
  if (!item) throw new Error("usage: node tools/tpt.js reupload tpt/NNN-slug [--dry-run]");
  item = path.resolve(item);
  const slug = path.basename(item), shots = path.join(ROOT, "tpt", "_publish");
  const F = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8"));
  const editFields = readEditFields();
  const plan = prepareReupload(item, F, dryRun ? undefined : editFields);
  if (plan.problems.length) throw new Error(`not replacing files for ${slug}:\n- ` + plan.problems.join("\n- "));
  const { files, state, fix, cfg } = plan;
  const fixPrice = fix.includes("price");
  if (dryRun) {
    console.log(`DRY RUN (offline, TpT not opened): would replace ONLY these files on ${state.url}`);
    for (const f of files) console.log(`  ${f.slot.padEnd(8)} ${f.file}  ${f.bytes} bytes  sha256 ${f.sha256}`);
    if (fix.length) {
      console.log(`Marker asks for the corrective fix: ${fix.join(", ")}`);
      if (fixPrice) console.log(`  price: would set price ${cfg.price}, license price ${cfg.license_price}, tax code ${cfg.tax_code} (tpt.json), un-tick "Free Resource" if ticked`);
      if (fix.includes("preview")) console.log(`  preview: would attach ${cfg.files.preview}`);
      console.log("  afterwards: public page must show price == tpt.json, isFree false, previewUrl present, title unchanged (description checked on the edit form); any mismatch -> reupload-failed + screenshot, no retry");
    }
    console.log(`Would NOT change: title, ${fixPrice ? "" : "price, "}description, tags, subjects, grades, listing status.`);
    console.log(`Would write ${path.relative(ROOT, item)}/reuploaded on success. tpt/EDIT-FIELDS.json: ${editFields ? "present" : "MISSING (a real run would stop; the nightly records it first)"}.`);
    return;
  }

  const fail = async (page, step, msg, diag) => { // record, screenshot, never retry this marker
    await snap(page, shots, `${slug}-reupload-failed`).catch(() => {});
    const rec = { at: new Date().toISOString(), marker_sha256: state.markerHash, step, error: msg, files: files.map((f) => ({ slot: f.slot, file: f.file, sha256: f.sha256 })), screenshot: `tpt/_publish/${slug}-reupload-failed.png` };
    if (diag) rec.diagnostics = diag;
    fs.writeFileSync(path.join(item, "reupload-failed"), JSON.stringify(rec, null, 2) + "\n");
    throw Object.assign(new Error(`reupload stopped at "${step}": ${msg}\nScreenshot: ${rec.screenshot}. Not retrying this marker.`), { recorded: true });
  };
  let step = "open browser", page, context, saved = false;
  ({ context, page } = await openBrowser());
  try {
    step = "check login"; await ensureLoggedIn(page);

    step = "open the live product page";
    const resp = await page.goto(state.url, { waitUntil: "domcontentloaded" });
    if (!resp || resp.status() >= 400) await fail(page, step, `${state.url} answered ${resp ? resp.status() : "nothing"}`);

    step = "open the edit page";
    if (editFields.edit_url_template) await page.goto(editFields.edit_url_template.replace("{id}", state.productId), { waitUntil: "domcontentloaded" });
    else {
      const link = page.getByRole("link", { name: new RegExp(editFields.edit_link_text, "i") }).first();
      if (!(await link.count())) await fail(page, step, `no link "${editFields.edit_link_text}" on the product page`);
      await link.click(); await page.waitForLoadState("domcontentloaded");
    }
    await page.waitForTimeout(3000);
    if (/\/login/i.test(page.url())) await fail(page, step, "TpT sent us to the login page");
    const editUrl = page.url();

    // Fields that must NOT change: read now, compare after saving.
    const readGuard = async () => {
      const g = {};
      for (const k of ["title", "price", "license_price"]) {
        const loc = F[k] && page.locator(F[k]);
        g[k] = loc && (await loc.count()) ? await loc.first().inputValue().catch(() => null) : null;
      }
      const d = F.description && page.locator(F.description);
      g.description = d && (await d.count()) ? (await d.first().innerText().catch(() => "")).trim().slice(0, 300) : null;
      return g;
    };
    const before = await readGuard();
    const liveBefore = parseLive(await (async () => { const pg = await context.newPage(); try { await pg.goto(state.url, { waitUntil: "domcontentloaded" }); await pg.waitForTimeout(2000); return await pg.content(); } catch (e) { return ""; } finally { await pg.close(); } })(), state.productId);
    if (!before.title) await fail(page, step, `the edit page did not show the title box (${F.title}); wrong page or TpT changed`);

    // 16 Nov 2026 (043 canary, 19:40Z): product and preview were replaced, then thumb1 failed with "no X-like control". The edit form
    // opens with "Upload thumbnails later" selected, which HIDES the four thumbnail boxes (#upload-thumb1..4: cover.png card with a
    // .delete-btn and the file input are in the DOM but invisible). publish() ticks "Upload thumbnails now" before its thumbnails; do the same.
    // Ticks "Upload thumbnails now" (16 Nov: the edit form opens with "Upload thumbnails later", which HIDES the thumbnail boxes).
    const thumbsNow = async () => {
      if (!files.some((f) => /^thumb/.test(f.slot))) return;
      step = "choose 'Upload thumbnails now'";
      const now = page.locator(F.upload_thumbnails_now);
      if (!(await now.count())) await fail(page, step, `no "Upload thumbnails now" option (${F.upload_thumbnails_now}) on the edit page`);
      await now.first().check({ timeout: 10000 }).catch(async () => { await now.first().click({ force: true }); });
      await page.waitForTimeout(1500);
      const shown = await page.locator(editSel(F, files.find((f) => /^thumb/.test(f.slot)).slot).input).first()
        .evaluate((el) => { const box = el.closest('[id^="upload-thumb"]') || el.parentElement; const r = box.getBoundingClientRect(); return r.width > 0 && r.height > 0; }).catch(() => false);
      console.log(`thumbnails: ticked "Upload thumbnails now"; thumbnail boxes ${shown ? "visible" : "STILL HIDDEN"}`);
      if (!shown) await snap(page, shots, `${slug}-reupload-thumbs-hidden-failed`).catch(() => {});
    };
    await thumbsNow();
    const oldCards = await readCards(page, F, files.map((f) => f.slot)); // compared with the cards after the save
    // 17 Nov 2026: a product/preview PDF whose card on TpT already shows exactly the new file's size (TpT shows kB with 2 decimals,
    // i.e. to ~10 bytes) is the same file: it is not uploaded again (e.g. items where only the thumbnails changed). Thumbnails are
    // never skipped: TpT shows them at a converted size.
    const skipped = files.filter((f) => sameFileOnTpt(f.slot, oldCards[f.slot], f.bytes));
    for (const f of skipped) console.log(`${f.slot}: TpT already has ${f.file} (${(f.bytes / 1024).toFixed(2)} kB, same size): not uploading it again`);
    const toUpload = files.filter((f) => !skipped.includes(f));
    const keys = {};
    // 17 Nov 2026 (044): a thumbnail upload can hang for good (TpT's S3 answered 502; the widget sat in "Cancel ..." with no key, and its
    // Cancel left a stale upload that aborted the next try: "User aborted the upload"). Nothing is saved until Submit, so on a slot that
    // fails, the edit page is loaded FRESH and every file is done again, once.
    for (let round = 1; round <= 2; round++) {
      let failed = null;
      for (const f of toUpload) {
        step = `replace ${f.slot} (${f.file})`;
        const spec = editSel(F, f.slot);
        const up = await uploadEditSlot(page, { slot: f.slot, spec, filePath: f.path, slug, shots }).catch((e) => ({ error: "unexpected error in the upload step: " + e.message.split("\n")[0] }));
        if (up.error) { failed = { step, up }; break; }
        keys[f.slot] = up.key;
      }
      if (!failed) break;
      if (round === 2) await fail(page, failed.step, `${failed.up.error} (second try, on a freshly loaded edit page)`, failed.up.diagnostics);
      console.log(`${failed.step}: ${failed.up.error.slice(0, 200)}; loading the edit page fresh (nothing was saved) and doing every file again`);
      await snap(page, shots, `${slug}-reupload-round1-failed`).catch(() => {});
      await page.goto(editUrl, { waitUntil: "domcontentloaded" });
      await page.locator(F.title).waitFor({ state: "visible", timeout: 30000 }).catch(() => {});
      await page.waitForTimeout(3000);
      await thumbsNow();
    }

    if (fixPrice) {
      // TpT hides price, license price and tax code while Free Resource is ON. So: screenshot, read #item-free, untick
      // it if ON, WAIT for the three controls to appear (fail safe with a screenshot + newly visible ids if they do
      // not), then fill them. UNVERIFIED (23 Oct 2026): the selectors of the revealed boxes (F.price, F.license_price,
      // F.tax_code) come from tpt/FORM.json, recorded on the NEW-item form, and are ASSUMED to match the edit form.
      // The run therefore logs the revealed field ids and snaps -fix-subject / -fix-untick (before / after).
      step = "fix price: un-tick Free Resource";
      const box = page.locator(F.free);
      if (!(await box.count())) await fail(page, step, `no "Free Resource" control ${F.free} on the edit page`);
      const idsBefore = await visibleFieldIds(page);
      await snap(page, shots, `${slug}-fix-subject`).catch(() => {});
      const wasOn = await freeIsOn(page, F.free);
      console.log(`fix price: ${F.free} is ${wasOn ? "ON" : "OFF"}; visible field ids before: ${idsBefore.join(", ")}`);
      const priceSels = [["price", F.price], ["license_price", F.license_price], ["tax_code", F.tax_code.toggle]];
      if (wasOn) {
        await box.first().click();
        await page.waitForTimeout(1000);
        if (await freeIsOn(page, F.free)) { await snap(page, shots, `${slug}-fix-untick`).catch(() => {}); await fail(page, step, `clicked ${F.free} but "Free Resource" still shows as ticked`); }
      }
      step = "fix price: wait for price, license price and tax code controls";
      const appeared = async () => { for (const [, sel] of priceSels) if (!(await page.locator(sel).first().isVisible().catch(() => false))) return false; return true; };
      const t0 = Date.now(); let ok = await appeared();
      while (!ok && Date.now() - t0 < 20000) { await page.waitForTimeout(500); ok = await appeared(); }
      const idsAfter = await visibleFieldIds(page);
      const fresh = idsAfter.filter((x) => !idsBefore.includes(x));
      console.log(`fix price: after untick, newly visible field ids: ${fresh.join(", ") || "(none)"}`);
      await snap(page, shots, `${slug}-fix-untick`).catch(() => {});
      if (!ok) await fail(page, step, `after un-ticking Free, ${priceSels.map(([k, x]) => k + " " + x).join(", ")} did not all appear within 20 s. Newly visible fields: ${fresh.join(", ") || "(none)"}`);
      step = "fix price: set price and license price";
      for (const k of ["price", "license_price"]) {
        const loc = page.locator(F[k]).first();
        await loc.fill(String(cfg[k]));
        const got = await loc.inputValue().catch(() => "");
        if (Math.abs(Number(got) - Number(cfg[k])) > 0.001) await fail(page, step, `typed ${cfg[k]} into ${k} but the box shows ${JSON.stringify(got)}`);
      }
      step = "fix price: tax code";
      const taxErr = await pickListbox(page, "tax_code", F.tax_code.toggle, cfg.tax_code);
      if (taxErr) { await snap(page, shots, `${slug}-fix-dropdown`).catch(() => {}); await fail(page, step, taxErr); }
      if (await freeIsOn(page, F.free)) await fail(page, step, '"Free Resource" got ticked again after setting the price');
    }
    if (fix.includes("preview") && !keys.preview && !skipped.some((f) => f.slot === "preview")) await fail(page, "fix preview", "the preview file was not uploaded (no key)");

    step = "save";
    let submit = page.locator((F.edit && F.edit.submit) || F.submit);
    if (!(await submit.count())) submit = page.getByRole("button", { name: /^\s*submit\s*$/i });
    if (!(await submit.count())) await fail(page, step, "no save button found");
    saved = true; // from here on TpT may have changed
    const savedAt = Date.now();
    const sv = await submitAndWait(page, submit, editUrl);
    console.log(`save: ${sv.how}; messages: ${sv.messages.join(" | ").slice(0, 200) || "(none)"}`);
    await snap(page, shots, `${slug}-reupload-after-submit`).catch(() => {});
    const saveDiag = { save: { how: sv.how, status: sv.status, messages: sv.messages, loop_errors: sv.loop_errors, ...sv.network } };
    if (!sv.ok) await fail(page, step, `after Submit: ${sv.how}; TpT says: ${sv.messages.join(" | ").slice(0, 300) || "(nothing)"} (Submit WAS clicked: check the product on TpT)`, saveDiag);

    step = "verify";
    const r2 = await page.goto(state.url, { waitUntil: "domcontentloaded" });
    if (!r2 || r2.status() >= 400) await fail(page, step, `product page answered ${r2 ? r2.status() : "nothing"} after saving`, saveDiag);
    await page.goto(editUrl, { waitUntil: "domcontentloaded" }); await page.waitForTimeout(3000);
    const after = await readGuard();
    for (const k of Object.keys(before)) if (!(fixPrice && (k === "price" || k === "license_price")) && before[k] !== after[k]) await fail(page, step, `field "${k}" changed during the save (before ${JSON.stringify(before[k])}, after ${JSON.stringify(after[k])})`, saveDiag);
    // Verify by the FILE CARDS, not the hidden key (empty for stored files on a fresh page).
    const newCards = await readCards(page, F, files.map((f) => f.slot));
    const verdicts = files.map((f) => ({ slot: f.slot, file: f.file, verdict: cardVerdict(oldCards[f.slot], newCards[f.slot], { ...f, savedAt, free: cfg.free === true }, f.slot), before: oldCards[f.slot].slice(0, 160), after: newCards[f.slot].slice(0, 160) }));
    console.log("verify: " + verdicts.map((v) => `${v.slot} ${v.verdict}`).join(", "));
    if (verdicts.some((v) => v.verdict !== "match")) {
      // TpT answered the save but the cards do not show the new files yet ("allow up to one hour"). Look again later; never resubmit.
      await snap(page, shots, `${slug}-reupload-unverified`).catch(() => {});
      fs.writeFileSync(path.join(item, "reupload-unverified"), JSON.stringify({
        at: new Date(savedAt).toISOString(), marker_sha256: state.markerHash, url: state.url, edit_url: editUrl, checks: [{ at: new Date().toISOString(), verdicts }],
        files: files.map((f) => ({ slot: f.slot, file: f.file, bytes: f.bytes, sha256: f.sha256 })), old_cards: oldCards, ...saveDiag,
        note: `Submitted; the edit page still showed old files right after. The Mac looks again at >= ${UNVERIFIED_CHECKS_MIN.join(" and >= ")} min after the save; it is NOT resubmitted meanwhile.`,
      }, null, 2) + "\n");
      console.log(`${slug}: saved, not visible yet: wrote reupload-unverified (looked at again after ${UNVERIFIED_CHECKS_MIN.join(" and ")} min)`);
      return { url: state.url, files: files.length, unverified: true };
    }
    if (fixPrice) {
      for (const k of ["price", "license_price"]) if (Math.abs(Number(after[k]) - Number(cfg[k])) > 0.001) await fail(page, step, `after saving, ${k} on the edit form is ${JSON.stringify(after[k])}, expected ${cfg[k]}`);
      if (F.free && (await page.locator(F.free).count()) && (await freeIsOn(page, F.free)))
        await fail(page, step, 'after saving, "Free Resource" is ticked on the edit form');
    }
    if (fix.length) { // the PUBLIC page is the judge (TpT may take a moment to show the change)
      step = "verify the public page";
      let problems = [], live;
      for (let attempt = 0; attempt < 6; attempt++) {
        await page.goto(state.url, { waitUntil: "domcontentloaded" }); await page.waitForTimeout(3000);
        live = parseLive(await page.content(), state.productId);
        problems = compareLive({ ...cfg, free: false, pages: undefined }, live).filter((m) => !(fix.every((x) => x !== "preview") && /^previewUrl/.test(m)));
        if (!fix.includes("price")) problems = problems.filter((m) => !/^(price|isFree)/.test(m));
        if (liveBefore.title && live.title && liveBefore.title !== live.title) problems.push(`title changed: before ${JSON.stringify(liveBefore.title)}, now ${JSON.stringify(live.title)}`);
        if (!problems.length) break;
        await page.waitForTimeout(20000);
      }
      if (problems.length) await fail(page, step, "public page does not match tpt.json after the fix: " + problems.join("; "));
    }

    fs.writeFileSync(path.join(item, "reuploaded"), JSON.stringify({
      at: new Date().toISOString(), tool: "tools/tpt.js reupload", url: state.url, marker_sha256: state.markerHash,
      files: files.map((f) => ({ slot: f.slot, file: f.file, bytes: f.bytes, sha256: f.sha256, ...(skipped.includes(f) ? { not_uploaded: "TpT already had a file of exactly this size" } : {}) })),
      fix, fix_verified: fix.length ? { price: cfg.price, license_price: cfg.license_price, preview: cfg.files.preview, verified_on_public_page: true } : undefined,
      verified_by: "file cards on the edit page", verdicts, save: saveDiag.save.how,
    }, null, 2) + "\n");
    console.log(`Replaced ${files.length} files on ${state.url}; wrote ${path.relative(ROOT, item)}/reuploaded`);
    return { url: state.url, files: files.length };
  } catch (e) {
    if (e.recorded) throw e;
    if (step !== "check login" && step !== "open browser") { // unexpected error: same rule, record and hold
      // after the Submit click, let TpT finish whatever it is doing before the browser closes (closing can cut a save off)
      if (saved) await page.waitForLoadState("networkidle", { timeout: 120000 }).catch(() => {});
      const stack = String(e.stack || e).split("\n").slice(0, 8);
      try { await fail(page, step, String(e.message || e).split("\n")[0] + (saved ? " (the save click had already happened: check the product on TpT)" : " (nothing was saved)"), { stack }); } catch (e2) { throw e2; }
    }
    throw e;
  } finally {
    await context.close();
  }
}

// ---- live URL lookup for an item whose `uploaded` has no URL (014, 17 Nov 2026) ---------------------------------------------------
// Read-only: open the logged-in My Products list (all pages), match the item's EXACT title against the product links (by the
// title slug in /Product/<slug>-<id>, or by the link text), write `live-url` (URL, then how it was found). At most once in 20 h per
// item (`live-url-lookup` records each try). The links seen go to tpt/_publish/<slug>-my-products-links.json.
function matchMyProducts(title, links) {
  const t = slugNorm(title), nt = normTitle(title);
  for (const l of links) {
    const m = String(l.href || "").match(/\/Product\/([^"?#\/]+?)-(\d{6,})(?:[?#]|$)/);
    if (m && (slugNorm(m[1]) === t || (slugNorm(m[1]).length >= 60 && t.startsWith(slugNorm(m[1]))))) return `https://www.teacherspayteachers.com/Product/${m[1]}-${m[2]}`;
  }
  for (const l of links) {
    if (normTitle(l.text) !== nt) continue;
    const id = (String(l.href || "").match(/(?:Product\/[^"?#]*-|editNext\/|\/)(\d{6,})(?:[?#\/]|$)/) || [])[1];
    if (id) return `https://www.teacherspayteachers.com/Product/${slugNorm(title).split("-").map((w) => w[0].toUpperCase() + w.slice(1)).join("-")}-${id}`;
  }
  return null;
}
function normTitle(t) { return String(t || "").replace(/&amp;/g, "&").replace(/[‘’]/g, "'").replace(/\s+/g, " ").trim(); }
async function lookupLiveUrl(item) {
  const slug = path.basename(item), title = loadItem(item).title, out = path.join(ROOT, "tpt", "_publish", `${slug}-my-products-links.json`);
  const { context, page } = await openBrowser();
  const links = [];
  try {
    await ensureLoggedIn(page);
    for (let p = 1; p <= 10; p++) {
      await page.goto(p === 1 ? MY_PRODUCTS_URL : `${MY_PRODUCTS_URL}?page=${p}`, { waitUntil: "domcontentloaded" });
      await page.waitForTimeout(3000);
      const got = await page.evaluate(() => [...document.querySelectorAll("a[href]")].map((a) => ({ href: a.getAttribute("href"), text: (a.innerText || "").replace(/\s+/g, " ").trim().slice(0, 160) }))
        .filter((l) => /\/Product\/|editNext|\/items/i.test(l.href)));
      const before = links.length;
      for (const l of got) if (!links.some((x) => x.href === l.href)) links.push(l);
      if (links.length === before) break;
    }
  } finally {
    try { fs.mkdirSync(path.dirname(out), { recursive: true }); fs.writeFileSync(out, JSON.stringify({ at: new Date().toISOString(), title, links: links.slice(0, 400) }, null, 2) + "\n"); } catch (e) { /* diagnostics only */ }
    await context.close();
  }
  const url = matchMyProducts(title, links);
  fs.writeFileSync(path.join(item, "live-url-lookup"), JSON.stringify({ at: new Date().toISOString(), title, found: url, links_seen: links.length, links_file: path.relative(ROOT, out) }, null, 2) + "\n");
  if (url) fs.writeFileSync(path.join(item, "live-url"), `${url}\nfound on the logged-in My Products list by its exact title, ${new Date().toISOString()} (tools/tpt.js)\n`);
  return url;
}

// When a `reupload-unverified` record is due for a look: { due, final }. Pure. Looks at >= 70 min and >= 180 min after the save;
// the look at >= 180 min is final (still old -> reupload-failed).
function unverifiedDue(rec, now = Date.now()) {
  const age = (now - Date.parse(rec.at)) / 60000;
  const looked = (rec.checks || []).slice(1).map((c) => (Date.parse(c.at) - Date.parse(rec.at)) / 60000); // checks[0] = right after the save
  const last = UNVERIFIED_CHECKS_MIN[UNVERIFIED_CHECKS_MIN.length - 1];
  if (age >= last) return { due: true, final: true };
  const next = UNVERIFIED_CHECKS_MIN.find((m) => !looked.some((l) => l >= m));
  return { due: next !== undefined && age >= next, final: false };
}
// Read-only look at a submitted-but-unverified product: open its edit page, compare the file cards with the old ones. Never submits.
// Returns "verified" | "waiting" | "failed". deps.readCardsNow (tests only) replaces the browser.
async function checkUnverified(item, deps = {}) {
  item = path.resolve(item);
  const slug = path.basename(item), st = reuploadState(item), shots = path.join(ROOT, "tpt", "_publish");
  if (st.state !== "unverified") return "skip";
  const rec = st.rec, when = unverifiedDue(rec, deps.now);
  if (!when.due) return "waiting";
  let cards, shot = null;
  if (deps.readCardsNow) cards = await deps.readCardsNow(rec);
  else {
    const F = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8"));
    const { context, page } = await openBrowser();
    try {
      await ensureLoggedIn(page);
      await page.goto(rec.edit_url, { waitUntil: "domcontentloaded" }); await page.waitForTimeout(4000);
      if (/\/login/i.test(page.url())) throw new Error("not logged in (TpT sent us to the login page)");
      cards = await readCards(page, F, rec.files.map((f) => f.slot));
      shot = `tpt/_publish/${slug}-reupload-recheck.png`; await snap(page, shots, `${slug}-reupload-recheck`).catch(() => {});
    } finally { await context.close(); }
  }
  const savedAt = Date.parse(rec.at);
  let free = false; try { free = JSON.parse(fs.readFileSync(path.join(item, "tpt.json"), "utf8")).free === true; } catch (e) { /* paid */ }
  const verdicts = rec.files.map((f) => ({ slot: f.slot, file: f.file, verdict: cardVerdict(rec.old_cards[f.slot] || "", cards[f.slot] || "", { ...f, savedAt, free }, f.slot), after: (cards[f.slot] || "").slice(0, 160) }));
  rec.checks = [...(rec.checks || []), { at: new Date(deps.now || Date.now()).toISOString(), verdicts, screenshot: shot }];
  if (verdicts.every((v) => v.verdict === "match")) {
    fs.writeFileSync(path.join(item, "reuploaded"), JSON.stringify({ at: new Date().toISOString(), tool: "tools/tpt.js reupload (verified later)", url: rec.url, marker_sha256: rec.marker_sha256,
      saved_at: rec.at, files: rec.files, verified_by: "file cards on the edit page", verdicts, checks: rec.checks.length }, null, 2) + "\n");
    fs.rmSync(path.join(item, "reupload-unverified"), { force: true });
    console.log(`${slug}: the new files now show on the edit page: wrote reuploaded`);
    return "verified";
  }
  if (when.final) {
    fs.writeFileSync(path.join(item, "reupload-failed"), JSON.stringify({ at: new Date().toISOString(), marker_sha256: rec.marker_sha256, step: "verify (later)",
      error: `submitted at ${rec.at}, but ${Math.round((Date.now() - savedAt) / 60000)} min later the edit page still shows: ${verdicts.filter((v) => v.verdict !== "match").map((v) => `${v.slot} ${v.verdict} (${v.after.slice(0, 80)})`).join("; ")}`,
      files: rec.files, screenshot: shot, diagnostics: { save: rec.save, checks: rec.checks } }, null, 2) + "\n");
    fs.rmSync(path.join(item, "reupload-unverified"), { force: true });
    console.log(`${slug}: still the old files ${UNVERIFIED_CHECKS_MIN[UNVERIFIED_CHECKS_MIN.length - 1]}+ min after the save: wrote reupload-failed`);
    return "failed";
  }
  fs.writeFileSync(path.join(item, "reupload-unverified"), JSON.stringify(rec, null, 2) + "\n");
  console.log(`${slug}: not visible yet; will look again at ${UNVERIFIED_CHECKS_MIN[UNVERIFIED_CHECKS_MIN.length - 1]} min`);
  return "waiting";
}

// 17 Nov 2026: gentler runs. One S3 502 was seen during a burst; there is no proof of throttling, but each replacement is ~10
// uploads, so at most 3 items a run with a 60 s pause between them (the job runs 7 times a day).
const REUPLOAD_MAX_PER_RUN = 3, REUPLOAD_GAP_S = 60;
async function reuploadPending() {
  const dir = path.join(ROOT, "tpt");
  const res = { ran_at: new Date().toISOString(), replaced: [], failed: [], waiting: [], skipped: [], needs_login: false, needs_edit_fields: false, discovered_edit: false };
  const done = (ok) => { res.ok = ok; recordReuploadStatus(res); console.log(`Reupload: replaced ${res.replaced.length}, failed ${res.failed.length}, waiting ${res.waiting.length}.`); if (!ok) process.exitCode = 1; };
  if (fs.existsSync(path.join(dir, "PAUSED"))) { res.skipped.push("tpt/PAUSED exists"); console.log("tpt/PAUSED exists: replacing nothing."); return done(true); }
  // 16 Nov 2026: pauses ONLY the file replacement (publishing new products carries on). The replace step has failed on every try since
  // October (TpT's edit form never registers the new product file), so with ~28 replacements queued the Mac would open Chrome for hours
  // and fail each one. Delete tpt/REUPLOAD-PAUSED when the cause is fixed.
  // An `allow: 043` line in it lets only the listed items through (one canary after a fix; see TPT-FACTORY.md "The Mac uploader").
  const pause = parsePause(readTrim(path.join(dir, "REUPLOAD-PAUSED")));
  if (pause.paused && !pause.allow) { res.skipped.push("tpt/REUPLOAD-PAUSED exists"); console.log("tpt/REUPLOAD-PAUSED exists: replacing nothing."); return done(true); }
  if (pause.paused) { res.canary = pause.allow; console.log(`tpt/REUPLOAD-PAUSED allows only: ${pause.allow.join(", ")}`); }
  const marked = fs.readdirSync(dir).filter((d) => /^\d{3}-/.test(d)).map((d) => path.join(dir, d)).filter((d) => fs.existsSync(path.join(d, "reupload"))).sort();
  let pending = marked.filter((d) => reuploadState(d).state === "pending");
  for (const d of pending) if (!pauseAllows(pause, d)) res.skipped.push(`${path.basename(d)}: paused (tpt/REUPLOAD-PAUSED allows only ${pause.allow.join(", ")})`);
  pending = pending.filter((d) => pauseAllows(pause, d));
  for (const d of marked) if (!pending.includes(d)) { const s = reuploadState(d); if (s.state !== "done") res.skipped.push(`${path.basename(d)}: ${s.state}`); }
  // Items live on TpT whose `uploaded` has no URL (014): look the URL up on My Products, at most once in 20 h each, read-only.
  for (const d of marked.filter((x) => reuploadState(x).lookup && pauseAllows(pause, x))) {
    let last = null; try { last = JSON.parse(fs.readFileSync(path.join(d, "live-url-lookup"), "utf8")); } catch (e) { /* never tried */ }
    if (last && Date.now() - Date.parse(last.at) < 20 * 3600e3) continue;
    try { const u = await lookupLiveUrl(d); console.log(`${path.basename(d)}: live URL ${u ? "found: " + u : "NOT found on My Products by its title"}`); if (u && reuploadState(d).state === "pending") pending.push(d); }
    catch (e) { console.error(`${path.basename(d)}: live URL lookup: ${e.message.split("\n")[0]}`); if (/not logged in|session expired/i.test(e.message)) { res.needs_login = true; return done(false); } }
  }
  // Submitted-but-unverified items first: a read-only look when due, never a resubmit.
  res.unverified = [];
  for (const d of marked.filter((x) => reuploadState(x).state === "unverified" && pauseAllows(pause, x))) {
    try {
      const r = await checkUnverified(d);
      if (r === "verified") res.replaced.push({ item: path.basename(d), note: "verified on a later run" });
      else if (r === "failed") res.failed.push({ item: path.basename(d), error: "submitted, but the edit page still shows the old files 3 h later (see reupload-failed)" });
      else res.unverified.push(path.basename(d));
    } catch (e) {
      const msg = e.message.split("\n")[0].slice(0, 300); res.unverified.push(path.basename(d)); console.error(`${path.basename(d)}: recheck: ${msg}`);
      if (/not logged in|session expired/i.test(msg)) { res.needs_login = true; return done(false); }
    }
  }
  res.waiting = pending.map((d) => path.basename(d));
  if (!pending.length) { console.log("No item waiting for a file replacement."); return done(!res.failed.length); }
  console.log(`Marked for reupload: ${res.waiting.join(", ")}`);
  if (!readEditFields()) { // first run: learn the edit form, change nothing
    res.needs_edit_fields = true;
    try { await discoverEdit(pending[0]); res.discovered_edit = true; }
    catch (e) { res.failed.push({ item: path.basename(pending[0]), error: "discover-edit: " + e.message.split("\n").slice(0, 2).join(" ").slice(0, 300) }); if (/not logged in|session expired/i.test(e.message)) res.needs_login = true; }
    if (!res.discovered_edit) return done(false);
    // Same run, when safe: discover-edit is read-only, and prepareReupload() now checks every field the marker needs
    // (file boxes, and for `fix: price` the price, license price and Free boxes) against the freshly recorded edit
    // form. Items that pass go ahead tonight; the rest wait for the Manager (nothing is attempted blind).
    const F0 = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8")), ef = readEditFields();
    const ready = pending.filter((d) => !prepareReupload(d, F0, ef).problems.length);
    for (const d of pending) if (!ready.includes(d)) res.skipped.push(`${path.basename(d)}: edit form check failed after discover-edit: ${prepareReupload(d, F0, ef).problems.join("; ").slice(0, 300)}`);
    if (!ready.length) { console.log("Recorded tpt/EDIT-FIELDS.json; nothing is safe to replace tonight (see skipped in UPLOADER-STATUS.json)."); return done(true); }
    console.log("Recorded tpt/EDIT-FIELDS.json; the edit form has every field the marker needs, so the replacement/fix runs now (same night).");
    pending = ready;
  }
  // One failed or unverified item no longer stops the others (16 Nov 2026). Only a login problem, or 3 failures IN A ROW (a site-wide
  // change: no point opening Chrome for the rest), ends the run early.
  let inARow = 0, n = 0;
  for (const item of pending.slice(0, REUPLOAD_MAX_PER_RUN)) {
    const slug = path.basename(item);
    if (n++) { console.log(`waiting ${REUPLOAD_GAP_S} s before the next replacement`); await new Promise((ok) => setTimeout(ok, REUPLOAD_GAP_S * 1000)); }
    try {
      const r = await reupload(item, false);
      if (r.unverified) res.unverified.push(slug); else res.replaced.push({ item: slug, url: r.url, files: r.files });
      res.waiting = res.waiting.filter((x) => x !== slug); inARow = 0;
    } catch (e) {
      const msg = e.message.split("\n").slice(0, 3).join(" ").slice(0, 400);
      res.failed.push({ item: slug, error: msg }); console.error(`${slug}: ${msg}`);
      if (/not logged in|session expired/i.test(msg)) { res.needs_login = true; break; }
      if (++inARow >= 3) { console.error("3 replacements failed in a row: stopping this run"); break; }
    }
  }
  done(!res.needs_login && res.failed.length === 0);
}

// Read-only: records the edit form's structure for a live product. Saves nothing on TpT.
async function discoverEdit(arg) {
  let item = arg && path.resolve(arg);
  if (!item) {
    const dir = path.join(ROOT, "tpt");
    item = fs.readdirSync(dir).filter((d) => /^\d{3}-/.test(d)).map((d) => path.join(dir, d)).sort().find((d) => reuploadState(d).state === "pending");
    if (!item) throw new Error("discover-edit: no item with a `reupload` marker and an `uploaded` URL; name one: node tools/tpt.js discover-edit tpt/NNN-slug");
  }
  const url = (readTrim(path.join(item, "uploaded")) || "").split("\n")[1] || "";
  const m = url.trim().match(PRODUCT_URL_RE);
  if (!m) throw new Error(`discover-edit: ${path.basename(item)} has no TpT product URL in \`uploaded\``);
  const dir = path.join(ROOT, "tpt", "_discover"), out = { discovered_at: new Date().toISOString(), source_item: path.basename(item), product_page_links: [] };
  const { context, page } = await openBrowser();
  try {
    await ensureLoggedIn(page);
    await page.goto(url.trim(), { waitUntil: "domcontentloaded" }); await page.waitForTimeout(3000);
    await snap(page, dir, "10-product-page");
    const links = await page.evaluate(() => [...document.querySelectorAll("a")].map((a) => ({ text: a.innerText.trim().slice(0, 60), href: a.getAttribute("href") || "" }))
      .filter((l) => /edit/i.test(l.text) || /\/edit|My-Products\/(Edit|New)/i.test(l.href)));
    out.product_page_links = links.map((l) => ({ text: l.text, href: l.href.replace(m[1], "{id}") }));
    let target = links.find((l) => /^\s*edit\b/i.test(l.text)) || links[0];
    if (!target) throw new Error("no Edit link found on the product page (screenshot tpt/_discover/10-product-page.png); TpT may only show it to the seller account");
    const href = new URL(target.href, page.url()).toString();
    await page.goto(href, { waitUntil: "domcontentloaded" }); await page.waitForTimeout(4000); // opens the form only; nothing is clicked or typed
    await snap(page, dir, "11-edit-page");
    if (/\/login/i.test(page.url())) throw new Error("edit page sent us to login");
    out.edit_link_text = target.text || "Edit";
    out.edit_url_template = page.url().includes(m[1]) ? page.url().split(m[1]).join("{id}") : null;
    out.edit_url_example = page.url().split(m[1]).join("{id}");
    out.fields = await formFields(page);
    out.file_input_ids = out.fields.filter((f) => f.type === "file").map((f) => f.id);
    out.note = "Read-only discovery of the live product's edit form. Nothing was changed on TpT.";
  } finally {
    if (out.fields) fs.writeFileSync(EDIT_FIELDS(), JSON.stringify(out, null, 2) + "\n");
    await context.close();
  }
  console.log(`Recorded the edit form (${out.fields.length} fields, file boxes: ${out.file_input_ids.join(", ") || "none"}) in tpt/EDIT-FIELDS.json. Nothing was changed on TpT.`);
}

module.exports = { takeLock, readSubmitted, writeSubmitted, clearSubmitted, submittedDecision, readMyProductsLinks, findOnMyProducts, SUBMIT_SETTLE_MS, matchMyProducts, liveUrlForTitle, fetchStoreHtml, sameFileOnTpt, parseCard, cardVerdict, readCards, submitAndWait, unverifiedDue, checkUnverified, reuploadPending, uploadEditSlot, classifyWidget, redact, parsePause, pauseAllows, widgetState, resetWidget, startCapture, removeExistingFile, dumpMenu, closeMenu, chipsOf, pickListbox, freeIsOn, typeaheadPrefixes, matchOption, publishSteps, parseMarker, pendingItems, releasedButSkipped, releasedOverQA, checkItem, loadItem, isApproved, reuploadState, prepareReupload, sha256File, idOf };
const [cmd, arg] = process.argv.slice(2);
const dryRun = process.argv.includes("--dry-run");
// Every command that opens the TpT browser profile takes the uploader lock (only offline dry-run reupload does not).
const LOCKED = new Set(["login", "discover", "publish", "publish-pending", "reupload", "reupload-pending", "discover-edit"]);
if (require.main === module && LOCKED.has(cmd) && !(cmd === "reupload" && dryRun)) {
  const { held } = takeLock(`${cmd}${arg && !arg.startsWith("--") ? " " + arg : ""}`);
  if (held) {
    console.log(`another tools/tpt.js run holds the uploader lock (pid ${held.pid}, "${held.cmd}", since ${held.at}${held.clone ? ", " + held.clone : ""}); doing nothing.`);
    process.exit(/-pending$/.test(cmd) ? 0 : 1);
  }
}
if (require.main === module)
(cmd === "login" ? loginCmd() : cmd === "discover" ? discover() : cmd === "publish" ? publish(arg, dryRun)
  : cmd === "publish-pending" ? publishPending()
  : cmd === "reupload" ? reupload(arg, dryRun)
  : cmd === "reupload-pending" ? reuploadPending()
  : cmd === "discover-edit" ? discoverEdit(arg && !arg.startsWith("--") ? arg : null)
  : Promise.reject(new Error("usage: login | discover | publish <tpt/NNN-slug> [--dry-run] | publish-pending | discover-edit [item] | reupload <tpt/NNN-slug> [--dry-run] | reupload-pending")))
  .catch((e) => { console.error(e.message); process.exit(1); });
