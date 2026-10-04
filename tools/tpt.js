// Teachers Pay Teachers uploader for the owner's Hudson Beat music line.
// TpT has no seller API, so this drives the website with Playwright, logged in as the
// owner's Virtual Assistant (VA) account. It runs on the OWNER'S MAC (see tpt/LOCAL-SETUP.md):
// the cloud sessions can't reach TpT with a browser, because their proxy's certificate isn't
// trusted by Chromium.
//
// Credentials come from the environment (never committed): TPT_VA_EMAIL, TPT_VA_PASSWORD.
//
// Commands:
//   node tools/tpt.js discover        log in (a visible browser window opens), open My-Products/New-Item,
//                                     choose "Digital Download" on the product-type picker, and save:
//                                       tpt/_discover/*.png, *.html   screenshots + page HTML (gitignored, stay on the Mac)
//                                       tpt/FORM-FIELDS.json          labels/names/types of the form fields only,
//                                                                     no account details; commit this one
//                                     Nothing is created, saved or published on TpT.
//   node tools/tpt.js publish tpt/NNN-slug
//                                     (enabled once tpt/FORM.json has been written from FORM-FIELDS.json)
//
// If TpT shows a CAPTCHA or asks for a verification code, complete it in the browser window;
// the script waits up to 3 minutes for the login to finish.
const fs = require("fs"), path = require("path");
let chromium;
try { ({ chromium } = require("playwright")); }
catch (e) { ({ chromium } = require(path.join(require("child_process").execSync("npm root -g").toString().trim(), "playwright"))); }

const ROOT = path.dirname(__dirname);
const LOGIN_URL = "https://www.teacherspayteachers.com/Login";
const NEW_ITEM_URL = "https://www.teacherspayteachers.com/My-Products/New-Item";
const HEADLESS = process.env.TPT_HEADLESS === "1";

function env(name) {
  const v = process.env[name];
  if (!v) { console.error(`missing ${name}: see tpt/LOCAL-SETUP.md step 4`); process.exit(2); }
  return v;
}

async function login(page) {
  await page.goto(LOGIN_URL, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
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
  const submit = page.locator("#login_button_submit");
  if (await submit.count()) await submit.click(); else await pass.press("Enter");
  console.log("Logging in. If TpT asks for a CAPTCHA or a code, complete it in the browser window...");
  try {
    await page.waitForURL((u) => !/\/login/i.test(u.toString()), { timeout: 180000 });
  } catch (e) {
    await loginFailed(page, "still on the login page after 3 minutes: check the VA email/password, or finish TpT's verification step");
  }
  await page.waitForLoadState("domcontentloaded");
  await page.waitForTimeout(2000);
}

// Saves tpt/_discover/00-login-failed.png/.html and prints any on-page error text, then stops.
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
  const browser = await chromium.launch({ headless: HEADLESS });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const out = { discovered_at: new Date().toISOString(), pages: [] };
  try {
    await login(page);
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
    await browser.close();
  }
  console.log("Done. Nothing was created on TpT.");
  console.log("Screenshots (keep private): tpt/_discover/   Field list (commit this): tpt/FORM-FIELDS.json");
}

async function publish(item) {
  if (!item) { console.error("usage: node tools/tpt.js publish tpt/NNN-slug"); process.exit(1); }
  const formMap = path.join(ROOT, "tpt", "FORM.json");
  if (!fs.existsSync(formMap)) {
    console.error("publish isn't enabled yet: run `discover` and commit tpt/FORM-FIELDS.json first");
    process.exit(3);
  }
  if (fs.existsSync(path.join(item, "uploaded"))) { console.error(`already uploaded: ${item}`); process.exit(1); }
  if (!/APPROVED/.test(fs.readFileSync(path.join(item, "QA.md"), "utf8"))) { console.error("QA has not approved this item"); process.exit(1); }
  throw new Error("publish is written once FORM.json exists");
}

const [cmd, arg] = process.argv.slice(2);
(cmd === "discover" ? discover() : cmd === "publish" ? publish(arg) : Promise.reject(new Error("usage: discover | publish <tpt/NNN-slug>")))
  .catch((e) => { console.error(e.message); process.exit(1); });
