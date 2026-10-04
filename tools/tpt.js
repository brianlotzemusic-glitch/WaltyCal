// Teachers Pay Teachers uploader for the owner's Hudson Beat music line.
// TpT has no seller API, so this drives the website with Playwright, logged in as the
// owner's Virtual Assistant (VA) account. It runs on the OWNER'S MAC (see tpt/LOCAL-SETUP.md):
// the cloud sessions can't reach TpT with a browser, because their proxy's certificate isn't
// trusted by Chromium.
//
// Credentials come from the environment (never committed): TPT_VA_EMAIL, TPT_VA_PASSWORD.
//
// Commands:
//   node tools/tpt.js discover        log in (a visible browser window opens), open the "add a resource"
//                                     form, and save:
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
const HEADLESS = process.env.TPT_HEADLESS === "1";

function env(name) {
  const v = process.env[name];
  if (!v) { console.error(`missing ${name}: see tpt/LOCAL-SETUP.md step 4`); process.exit(2); }
  return v;
}

async function login(page) {
  await page.goto(LOGIN_URL, { waitUntil: "domcontentloaded" });
  await page.fill('input[type="email"], input[name="email"], input[name="username"]', env("TPT_VA_EMAIL"));
  await page.fill('input[type="password"]', env("TPT_VA_PASSWORD"));
  await page.keyboard.press("Enter");
  console.log("Logging in. If TpT asks for a CAPTCHA or a code, complete it in the browser window...");
  try {
    await page.waitForURL((u) => !/\/login/i.test(u.toString()), { timeout: 180000 });
  } catch (e) {
    throw new Error("still on the login page after 3 minutes: check the VA email/password, or finish TpT's verification step");
  }
  await page.waitForLoadState("domcontentloaded");
  await page.waitForTimeout(2000);
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
    const add = page.getByRole("link", { name: /add (a )?(new )?(product|resource)/i })
      .or(page.getByRole("button", { name: /add (a )?(new )?(product|resource)/i })).first();
    if (await add.count()) {
      await add.click();
      await page.waitForLoadState("domcontentloaded");
      await page.waitForTimeout(3000);
      await snap(page, dir, "03-add-resource-form");
      out.pages.push({ step: "add-resource-form", url: page.url(), fields: await formFields(page) });
    } else {
      out.pages.push({ step: "add-resource-form", error: "no 'Add a resource' link or button found on My-Products/Dashboard" });
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
