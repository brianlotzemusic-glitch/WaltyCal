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
// When a publish step fails or an upload times out, a screenshot goes to tpt/_publish/ (gitignored)
// along with the list of file inputs on the page.
const fs = require("fs"), path = require("path");
let chromium;
try { ({ chromium } = require("playwright")); }
catch (e) { ({ chromium } = require(path.join(require("child_process").execSync("npm root -g").toString().trim(), "playwright"))); }

const ROOT = path.dirname(__dirname);
const LOGIN_URL = "https://www.teacherspayteachers.com/Login";
const NEW_ITEM_URL = "https://www.teacherspayteachers.com/My-Products/New-Item";
const HEADLESS = process.env.TPT_HEADLESS === "1";
// One saved browser profile (cookies = the logged-in session) reused by every run, outside the repo.
const PROFILE = process.env.TPT_PROFILE_DIR || path.join(require("os").homedir(), ".tpt-profile");
const MY_PRODUCTS_URL = "https://www.teacherspayteachers.com/My-Products";

async function openBrowser() {
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

async function publish(item, dryRun) {
  if (!item) { console.error("usage: node tools/tpt.js publish tpt/NNN-slug [--dry-run]"); process.exit(1); }
  item = path.resolve(item);
  const F = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8"));
  if (fs.existsSync(path.join(item, "uploaded"))) { console.error(`already uploaded: ${item}`); process.exit(1); }
  if (!/^\*\*Verdict:\s*APPROVED\*\*/m.test(fs.readFileSync(path.join(item, "QA.md"), "utf8"))) { console.error("QA.md has no '**Verdict: APPROVED**' line"); process.exit(1); }
  const it = loadItem(item);
  const problems = checkItem(item, it, F);
  if (problems.length && !dryRun) { console.error("not publishing:\n- " + problems.join("\n- ")); process.exit(1); }

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

    // Uploads go to TpT as soon as a file is chosen; wait for TpT's hidden key field to fill.
    // Each upload has its own time limit; a missing or changed upload box fails this step only.
    const upload = async (slot, file, minutes) => {
      step = `upload ${slot} (${file})`;
      const spec = F.files[slot];
      try {
        await page.locator(spec.input).waitFor({ state: "attached", timeout: 20000 });
        await page.locator(spec.input).setInputFiles(path.join(item, file), { timeout: 30000 });
      } catch (e) {
        await snap(page, shots, `${slug}-${slot}-box`).catch(() => {});
        return fail(`${slot}: no upload box matching ${spec.input} (screenshot tpt/_publish/${slug}-${slot}-box.png). File inputs on the page: ${await fileInputs()}`);
      }
      try {
        await page.waitForFunction((sel) => { const el = document.querySelector(sel); return el && el.value; }, spec.key, { timeout: minutes * 60000 });
      } catch (e) {
        await snap(page, shots, `${slug}-${slot}-timeout`).catch(() => {});
        fail(`upload of ${file} (${slot}) did not finish within ${minutes} min (screenshot tpt/_publish/${slug}-${slot}-timeout.png)`);
      }
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

    step = "prices";
    await page.locator(F.price).fill(String(it.price ?? ""));
    await page.locator(F.license_price).fill(String(it.license_price ?? ""));

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

    // react-select comboboxes: type, then pick the option whose text matches exactly.
    const pick = async (name, sel, values) => {
      for (const v of values || []) {
        step = `${name}: ${v}`;
        const input = page.locator(sel);
        await input.click();
        await input.fill(v);
        await page.waitForTimeout(1500);
        const opts = page.getByRole("option");
        const texts = (await opts.allInnerTexts()).map((t) => t.trim());
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

const [cmd, arg] = process.argv.slice(2);
const dryRun = process.argv.includes("--dry-run");
(cmd === "login" ? loginCmd() : cmd === "discover" ? discover() : cmd === "publish" ? publish(arg, dryRun)
  : Promise.reject(new Error("usage: login | discover | publish <tpt/NNN-slug> [--dry-run]")))
  .catch((e) => { console.error(e.message); process.exit(1); });
