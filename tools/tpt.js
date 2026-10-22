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
//   node tools/tpt.js publish-pending
//                                     publish items the cloud Manager has released (a `release` file), at most 3
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
//   Offline test: node tools/test-tpt-reupload.js
//
// When a publish step fails or an upload times out, a screenshot goes to tpt/_publish/ (gitignored)
// along with the list of file inputs on the page.
const fs = require("fs"), path = require("path");
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
  const text = msgs.map((m) => m.trim()).filter(Boolean).join(" | ").slice(0, 300);
  throw new Error(`login failed: ${why}${text ? `\nTpT says: ${text}` : ""}\nScreenshot: tpt/_discover/00-login-failed.png`);
}

async function snap(page, dir, name) {
  fs.mkdirSync(dir, { recursive: true });
  await page.screenshot({ path: path.join(dir, `${name}.png`), fullPage: true });
  fs.writeFileSync(path.join(dir, `${name}.html`), await page.content());
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
  if (!it.tags?.length || it.tags.length > 6) p.push("tpt.json: tags needs 1-6 entries");
  if ((it.formats || []).length > 3) p.push("tpt.json: at most 3 formats");
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

function isApproved(item) {
  const qa = path.join(item, "QA.md");
  return fs.existsSync(qa) && /^\*\*Verdict:\s*APPROVED\*\*/m.test(fs.readFileSync(qa, "utf8"));
}

async function publish(item, dryRun) {
  if (!item) throw new Error("usage: node tools/tpt.js publish tpt/NNN-slug [--dry-run]");
  item = path.resolve(item);
  const F = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8"));
  if (fs.existsSync(path.join(item, "uploaded"))) throw new Error(`already uploaded: ${item}`);
  if (!isApproved(item)) throw new Error("QA.md has no '**Verdict: APPROVED**' line");
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
    const files = it.files || {};
    if (files.product) await upload("product", files.product, 15);
    if (files.preview) await upload("preview", files.preview, 5);
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

    if (it.free === true) {
      // Free item: tick TpT's "Free Resource" toggle (#item-free) and leave the price boxes alone.
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
    } else {
    step = "prices";
    await page.locator(F.price).fill(String(it.price ?? ""));
    await page.locator(F.license_price).fill(String(it.license_price ?? ""));
    }

    // Listbox comboboxes (tax code, answer key, teaching duration).
    const listbox = async (name, toggle, want) => {
      step = name;
      await page.locator(toggle).click();
      const opts = page.getByRole("option");
      await opts.first().waitFor({ timeout: 5000 }).catch(() => {});
      const texts = (await opts.allInnerTexts()).map((t) => t.trim());
      const i = texts.findIndex((t) => t.toLowerCase() === String(want).toLowerCase());
      if (i < 0) { await page.keyboard.press("Escape"); return fail(`${name}: "${want}" is not an option. Options: ${texts.join(" | ")}`); }
      await opts.nth(i).click();
    };
    await listbox("tax_code", F.tax_code.toggle, it.tax_code);

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
        const control = input.locator('xpath=ancestor::*[contains(@class, "control")][1]');
        const chosen = (await control.count()) ? (await control.innerText()).split("\n").map((t) => t.trim().toLowerCase()) : [];
        if (chosen.includes(v.toLowerCase())) continue;
        await input.click();
        await input.fill(v);
        const opts = page.getByRole("option");
        let texts = [];
        for (let t = 0; t < 10; t++) { // up to 5 s for TpT's option list
          await page.waitForTimeout(500);
          texts = (await opts.allInnerTexts()).map((x) => x.trim());
          if (texts.some((x) => x.toLowerCase() === v.toLowerCase())) break;
        }
        const i = texts.findIndex((t) => t.toLowerCase() === v.toLowerCase());
        if (i < 0) { await input.fill(""); await page.keyboard.press("Escape"); fail(`${name}: "${v}" is not an option. Typing it offered: ${texts.join(" | ") || "(nothing)"}`); continue; }
        await opts.nth(i).click();
        await page.keyboard.press("Escape");
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

    await snap(page, shots, `${slug}-filled`);
    if (dryRun) {
      console.log(problems.length ? "DRY RUN: problems to fix before publishing:\n- " + problems.join("\n- ") : "DRY RUN: every field filled with no problems.");
      console.log(`Form filled but NOT submitted. Screenshot: tpt/_publish/${slug}-filled.png`);
      return;
    }

    step = "submit";
    await page.locator(F.submit).click();
    try {
      await page.waitForURL((u) => !u.toString().includes("/My-Products/New/"), { timeout: 120000 });
    } catch (e) {
      await snap(page, shots, `${slug}-submit-failed`);
      const msgs = await page.locator('[role="alert"], [aria-live="assertive"], [class*="error" i]').allInnerTexts().catch(() => []);
      throw new Error(`still on the form 2 minutes after Submit; check My Products on TpT before retrying, it may have been created.\n` +
        `TpT says: ${msgs.map((m) => m.trim()).filter(Boolean).join(" | ").slice(0, 500) || "(nothing)"}\nScreenshot: tpt/_publish/${slug}-submit-failed.png`);
    }
    await snap(page, shots, `${slug}-submitted`);
    fs.writeFileSync(path.join(item, "uploaded"), `${new Date().toISOString()} published live by tools/tpt.js\n${page.url()}\n`);
    console.log(`Published: ${it.title}\nTpT went to ${page.url()}\nWrote ${path.relative(ROOT, item)}/uploaded`);
  } catch (e) {
    if (step === "submit" || step === "check login") throw e;
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
const MAX_PER_RUN = 3;
function pendingItems() {
  const dir = path.join(ROOT, "tpt");
  return fs.readdirSync(dir).filter((d) => /^\d{3}-/.test(d)).map((d) => path.join(dir, d))
    .filter((d) => fs.existsSync(path.join(d, "tpt.json")) && fs.existsSync(path.join(d, "release"))
      && isApproved(d) && !fs.existsSync(path.join(d, "uploaded")))
    .sort();
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
  console.log(items.length ? `Released and waiting: ${status.pending_before.join(", ")}` : "Nothing released to publish.");
  for (const item of items) {
    const slug = path.basename(item);
    try {
      await publish(item, false);
      status.published.push({ item: slug, url: (fs.readFileSync(path.join(item, "uploaded"), "utf8").split("\n")[1] || "").trim() });
    } catch (e) {
      const msg = e.message.split("\n").slice(0, 3).join(" ").slice(0, 400);
      status.failed.push({ item: slug, error: msg });
      console.error(`${slug}: ${msg}`);
      if (/not logged in|session expired|login failed/i.test(msg)) { status.needs_login = true; break; }
    }
  }
  status.ok = !status.needs_login && status.failed.length === 0;
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

// One of: no-marker | no-url | not-approved | done | failed-hold | pending. Pure file reads.
function reuploadState(item) {
  const marker = readTrim(path.join(item, "reupload"));
  if (marker === null || !marker.trim()) return { state: "no-marker", reason: "no `reupload` marker (the Manager writes it after QA approves the rebuild)" };
  const markerHash = crypto.createHash("sha256").update(marker).digest("hex");
  const up = readTrim(path.join(item, "uploaded"));
  const url = up ? (up.split("\n")[1] || "").trim() : "";
  if (!up) return { state: "no-url", markerHash, reason: "no `uploaded` file: the product is not live, nothing to replace (publish it instead)" };
  if (!PRODUCT_URL_RE.test(url)) return { state: "no-url", markerHash, reason: `\`uploaded\` line 2 is not a TpT product URL: ${JSON.stringify(url)}` };
  if (!isApproved(item)) return { state: "not-approved", markerHash, url, reason: "QA.md has no '**Verdict: APPROVED**' line" };
  const done = readTrim(path.join(item, "reuploaded"));
  if (done) { try { if (JSON.parse(done).marker_sha256 === markerHash) return { state: "done", markerHash, url, reason: "this reupload marker was already processed (see `reuploaded`); write a new marker to replace again" }; } catch (e) { /* unreadable: treat as not done */ } }
  const failed = readTrim(path.join(item, "reupload-failed"));
  if (failed) { try { if (JSON.parse(failed).marker_sha256 === markerHash) return { state: "failed-hold", markerHash, url, reason: "an earlier attempt for this marker failed (see `reupload-failed`); not retrying until a new marker is written or that file is deleted" }; } catch (e) { return { state: "failed-hold", markerHash, url, reason: "`reupload-failed` exists and is unreadable; not retrying" }; } }
  return { state: "pending", markerHash, url, productId: url.match(PRODUCT_URL_RE)[1] };
}

function idOf(sel) { const m = String(sel || "").match(/#([\w-]+)\s*$/); return m ? m[1] : null; }
function editSel(F, slot) { return { ...(F.files[slot] || {}), ...((F.edit && F.edit.files && F.edit.files[slot]) || {}) }; }

// Everything checkable without a browser. Returns { problems, files, state }.
function prepareReupload(item, F, editFields) {
  const st = reuploadState(item), problems = [], files = [];
  if (st.state !== "pending") return { problems: [st.reason], files, state: st };
  let cfg; try { cfg = JSON.parse(fs.readFileSync(path.join(item, "tpt.json"), "utf8")); } catch (e) { return { problems: ["tpt.json unreadable: " + e.message], files, state: st }; }
  const listed = cfg.files || {};
  if (!listed.product) problems.push("tpt.json: files.product is not set");
  for (const slot of FILE_SLOTS) {
    if (!listed[slot]) continue;
    const fp = path.join(item, listed[slot]);
    if (!fs.existsSync(fp)) { problems.push(`missing file ${fp}`); continue; }
    const bytes = fs.statSync(fp).size, spec = F.files[slot];
    if (!spec) { problems.push(`FORM.json has no file slot ${slot}`); continue; }
    if (!bytes) problems.push(`${listed[slot]} is empty`);
    if (bytes / 1048576 > spec.max_mb) problems.push(`${listed[slot]} is ${(bytes / 1048576).toFixed(1)} MB (max ${spec.max_mb} MB for ${slot})`);
    files.push({ slot, file: listed[slot], path: fp, bytes, sha256: sha256File(fp) });
  }
  for (const k of Object.keys(listed)) if (!FILE_SLOTS.includes(k)) problems.push(`tpt.json: unknown file slot ${k}`);
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
    }
  }
  return { problems, files, state: st };
}

function readEditFields() { try { return JSON.parse(fs.readFileSync(EDIT_FIELDS(), "utf8")); } catch (e) { return null; } }

function recordReuploadStatus(patch) {
  const fp = path.join(ROOT, "tpt", "UPLOADER-STATUS.json");
  let cur = {}; try { cur = JSON.parse(fs.readFileSync(fp, "utf8")); } catch (e) { /* new file */ }
  cur.reupload = { ...(cur.reupload || {}), ...patch };
  fs.writeFileSync(fp, JSON.stringify(cur, null, 2) + "\n");
}

async function reupload(item, dryRun) {
  if (!item) throw new Error("usage: node tools/tpt.js reupload tpt/NNN-slug [--dry-run]");
  item = path.resolve(item);
  const slug = path.basename(item), shots = path.join(ROOT, "tpt", "_publish");
  const F = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8"));
  const editFields = readEditFields();
  const plan = prepareReupload(item, F, dryRun ? undefined : editFields);
  if (plan.problems.length) throw new Error(`not replacing files for ${slug}:\n- ` + plan.problems.join("\n- "));
  const { files, state } = plan;
  if (dryRun) {
    console.log(`DRY RUN (offline, TpT not opened): would replace ONLY these files on ${state.url}`);
    for (const f of files) console.log(`  ${f.slot.padEnd(8)} ${f.file}  ${f.bytes} bytes  sha256 ${f.sha256}`);
    console.log("Would NOT change: title, price, description, tags, subjects, grades, listing status.");
    console.log(`Would write ${path.relative(ROOT, item)}/reuploaded on success. tpt/EDIT-FIELDS.json: ${editFields ? "present" : "MISSING (a real run would stop; the nightly records it first)"}.`);
    return;
  }

  const fail = async (page, step, msg) => { // record, screenshot, never retry this marker
    await snap(page, shots, `${slug}-reupload-failed`).catch(() => {});
    const rec = { at: new Date().toISOString(), marker_sha256: state.markerHash, step, error: msg, files: files.map((f) => ({ slot: f.slot, file: f.file, sha256: f.sha256 })), screenshot: `tpt/_publish/${slug}-reupload-failed.png` };
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
    if (!before.title) await fail(page, step, `the edit page did not show the title box (${F.title}); wrong page or TpT changed`);

    const keys = {};
    for (const f of files) {
      step = `replace ${f.slot} (${f.file})`;
      const spec = editSel(F, f.slot), input = page.locator(spec.input);
      try { await input.waitFor({ state: "attached", timeout: 20000 }); } catch (e) { await fail(page, step, `no upload box ${spec.input} on the edit page`); }
      const oldKey = await page.locator(spec.key).first().inputValue().catch(() => "");
      await input.setInputFiles(f.path, { timeout: 30000 });
      const minutes = f.slot === "product" ? 15 : f.slot === "preview" ? 5 : 3;
      const ok = await page.waitForFunction(([s, old]) => { const el = document.querySelector(s); return el && el.value && el.value !== old; }, [spec.key, oldKey], { timeout: minutes * 60000 }).then(() => true, () => false);
      if (!ok) await fail(page, step, `TpT did not accept ${f.file} within ${minutes} min (the upload key never changed)`);
      keys[f.slot] = await page.locator(spec.key).first().inputValue();
    }

    step = "save";
    const submit = page.locator((F.edit && F.edit.submit) || F.submit);
    if (!(await submit.count())) await fail(page, step, "no save button found");
    saved = true; // from here on TpT may have changed
    await submit.first().click();
    await page.waitForLoadState("domcontentloaded", { timeout: 120000 }).catch(() => {});
    await page.waitForTimeout(5000);

    step = "verify";
    const r2 = await page.goto(state.url, { waitUntil: "domcontentloaded" });
    if (!r2 || r2.status() >= 400) await fail(page, step, `product page answered ${r2 ? r2.status() : "nothing"} after saving`);
    await page.goto(editUrl, { waitUntil: "domcontentloaded" }); await page.waitForTimeout(3000);
    const after = await readGuard();
    for (const k of Object.keys(before)) if (before[k] !== after[k]) await fail(page, step, `field "${k}" changed during the save (before ${JSON.stringify(before[k])}, after ${JSON.stringify(after[k])})`);
    const text = await page.locator("body").innerText().catch(() => "");
    let filled = 0;
    for (const f of files) {
      const spec = editSel(F, f.slot), v = await page.locator(spec.key).first().inputValue().catch(() => "");
      if (v) filled++; else await fail(page, step, `after saving, ${f.slot} (${f.file}) shows no file on the edit page`);
      if ((f.slot === "product" || f.slot === "preview") && !text.includes(path.basename(f.file)) && !v.includes(path.basename(f.file)))
        await fail(page, step, `after saving, the edit page does not list the file name ${f.file} for ${f.slot}`);
    }
    if (filled !== files.length) await fail(page, step, `expected ${files.length} files on the product, found ${filled}`);

    fs.writeFileSync(path.join(item, "reuploaded"), JSON.stringify({
      at: new Date().toISOString(), tool: "tools/tpt.js reupload", url: state.url, marker_sha256: state.markerHash,
      files: files.map((f) => ({ slot: f.slot, file: f.file, bytes: f.bytes, sha256: f.sha256 })),
    }, null, 2) + "\n");
    console.log(`Replaced ${files.length} files on ${state.url}; wrote ${path.relative(ROOT, item)}/reuploaded`);
    return { url: state.url, files: files.length };
  } catch (e) {
    if (e.recorded) throw e;
    if (step !== "check login" && step !== "open browser") { // unexpected error: same rule, record and hold
      try { await fail(page, step, e.message.split("\n")[0] + (saved ? " (the save click had already happened: check the product on TpT)" : " (nothing was saved)")); } catch (e2) { throw e2; }
    }
    throw e;
  } finally {
    await context.close();
  }
}

async function reuploadPending() {
  const dir = path.join(ROOT, "tpt");
  const res = { ran_at: new Date().toISOString(), replaced: [], failed: [], waiting: [], skipped: [], needs_login: false, needs_edit_fields: false, discovered_edit: false };
  const done = (ok) => { res.ok = ok; recordReuploadStatus(res); console.log(`Reupload: replaced ${res.replaced.length}, failed ${res.failed.length}, waiting ${res.waiting.length}.`); if (!ok) process.exitCode = 1; };
  if (fs.existsSync(path.join(dir, "PAUSED"))) { res.skipped.push("tpt/PAUSED exists"); console.log("tpt/PAUSED exists: replacing nothing."); return done(true); }
  const marked = fs.readdirSync(dir).filter((d) => /^\d{3}-/.test(d)).map((d) => path.join(dir, d)).filter((d) => fs.existsSync(path.join(d, "reupload"))).sort();
  const pending = marked.filter((d) => reuploadState(d).state === "pending");
  for (const d of marked) if (!pending.includes(d)) { const s = reuploadState(d); if (s.state !== "done") res.skipped.push(`${path.basename(d)}: ${s.state}`); }
  res.waiting = pending.map((d) => path.basename(d));
  if (!pending.length) { console.log("No item waiting for a file replacement."); return done(true); }
  console.log(`Marked for reupload: ${res.waiting.join(", ")}`);
  if (!readEditFields()) { // first run: learn the edit form, change nothing
    res.needs_edit_fields = true;
    try { await discoverEdit(pending[0]); res.discovered_edit = true; console.log("Recorded tpt/EDIT-FIELDS.json; files are replaced from the next run."); }
    catch (e) { res.failed.push({ item: path.basename(pending[0]), error: "discover-edit: " + e.message.split("\n").slice(0, 2).join(" ").slice(0, 300) }); if (/not logged in|session expired/i.test(e.message)) res.needs_login = true; }
    return done(res.discovered_edit);
  }
  for (const item of pending.slice(0, MAX_PER_RUN)) {
    const slug = path.basename(item);
    try { const r = await reupload(item, false); res.replaced.push({ item: slug, url: r.url, files: r.files }); res.waiting = res.waiting.filter((x) => x !== slug); }
    catch (e) {
      const msg = e.message.split("\n").slice(0, 3).join(" ").slice(0, 400);
      res.failed.push({ item: slug, error: msg }); console.error(`${slug}: ${msg}`);
      if (/not logged in|session expired/i.test(msg)) { res.needs_login = true; break; }
      if (e.recorded || /stopped at/.test(msg)) break; // a TpT-side mismatch: stop the whole step, do not push on to other items
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

module.exports = { checkItem, loadItem, isApproved, reuploadState, prepareReupload, sha256File, idOf };
const [cmd, arg] = process.argv.slice(2);
const dryRun = process.argv.includes("--dry-run");
if (require.main === module)
(cmd === "login" ? loginCmd() : cmd === "discover" ? discover() : cmd === "publish" ? publish(arg, dryRun)
  : cmd === "publish-pending" ? publishPending()
  : cmd === "reupload" ? reupload(arg, dryRun)
  : cmd === "reupload-pending" ? reuploadPending()
  : cmd === "discover-edit" ? discoverEdit(arg && !arg.startsWith("--") ? arg : null)
  : Promise.reject(new Error("usage: login | discover | publish <tpt/NNN-slug> [--dry-run] | publish-pending | discover-edit [item] | reupload <tpt/NNN-slug> [--dry-run] | reupload-pending")))
  .catch((e) => { console.error(e.message); process.exit(1); });
