// Teachers Pay Teachers uploader for the owner's Hudson Beat music line.
// TpT has no seller API, so this drives the website with Playwright, logged in as the
// owner's Virtual Assistant (VA) account. The owner creates that VA login and adds:
//   TPT_VA_EMAIL, TPT_VA_PASSWORD   (cloud environment settings, never committed)
//
// Commands (Playwright is found in the global npm root automatically):
//   node tools/tpt.js discover                 log in, open the "add a resource" form, save a screenshot
//                                              and the HTML of every step to tpt/_discover/ (nothing is saved on TpT)
//   node tools/tpt.js publish tpt/NNN-slug     fill the form from UPLOAD.md, attach the files, publish;
//                                              writes tpt/NNN-slug/uploaded with the product URL
//
// publish refuses to run until tpt/FORM.json exists. That file maps form fields to selectors and
// is written from a discover run, because the form cannot be seen without logging in.
const fs = require("fs"), path = require("path");
let chromium;
try { ({ chromium } = require("playwright")); }
catch (e) { ({ chromium } = require(path.join(require("child_process").execSync("npm root -g").toString().trim(), "playwright"))); }

const ROOT = path.dirname(__dirname);
const LOGIN_URL = "https://www.teacherspayteachers.com/Login";

function env(name) {
  const v = process.env[name];
  if (!v) { console.error(`missing ${name}: the owner adds it in the cloud environment settings`); process.exit(2); }
  return v;
}

async function login(page) {
  await page.goto(LOGIN_URL, { waitUntil: "domcontentloaded" });
  await page.fill('input[type="email"], input[name="email"], input[name="username"]', env("TPT_VA_EMAIL"));
  await page.fill('input[type="password"]', env("TPT_VA_PASSWORD"));
  await Promise.all([page.waitForLoadState("networkidle").catch(() => {}), page.keyboard.press("Enter")]);
  await page.waitForTimeout(3000);
  const body = (await page.content()).toLowerCase();
  if (/captcha|verify it's you|verification code|two-factor/.test(body)) {
    throw new Error("TpT asked for a CAPTCHA or verification code: the owner must complete it once by hand, or switch off two-step login for the VA account");
  }
  if (page.url().includes("/Login")) throw new Error("login failed: check TPT_VA_EMAIL / TPT_VA_PASSWORD");
}

async function snap(page, dir, name) {
  fs.mkdirSync(dir, { recursive: true });
  await page.screenshot({ path: path.join(dir, `${name}.png`), fullPage: true });
  fs.writeFileSync(path.join(dir, `${name}.html`), await page.content());
}

async function discover() {
  const dir = path.join(ROOT, "tpt", "_discover");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  try {
    await login(page);
    await snap(page, dir, "01-after-login");
    for (const url of ["https://www.teacherspayteachers.com/My-Products", "https://www.teacherspayteachers.com/Dashboard"]) {
      await page.goto(url, { waitUntil: "domcontentloaded" }).catch(() => {});
      await page.waitForTimeout(2000);
      await snap(page, dir, "02-" + url.split("/").pop().toLowerCase());
    }
    const add = page.getByText(/add (a )?(new )?(product|resource)/i).first();
    if (await add.count()) {
      await add.click();
      await page.waitForTimeout(3000);
      await snap(page, dir, "03-add-resource-form");
    } else {
      console.log("no 'add resource' button found; see the screenshots");
    }
    console.log(`saved screenshots + HTML to ${dir} (nothing was created on TpT)`);
  } finally {
    await browser.close();
  }
}

async function publish(item) {
  const formMap = path.join(ROOT, "tpt", "FORM.json");
  if (!fs.existsSync(formMap)) {
    console.error("tpt/FORM.json does not exist yet: run `discover` first and map the fields");
    process.exit(3);
  }
  if (fs.existsSync(path.join(item, "uploaded"))) { console.error(`already uploaded: ${item}`); process.exit(1); }
  if (!/APPROVED/.test(fs.readFileSync(path.join(item, "QA.md"), "utf8"))) { console.error("QA has not approved this item"); process.exit(1); }
  throw new Error("publish is written once FORM.json exists (field names come from the discover run)");
}

const [cmd, arg] = process.argv.slice(2);
(cmd === "discover" ? discover() : cmd === "publish" ? publish(arg) : Promise.reject(new Error("usage: discover | publish <tpt/NNN-slug>")))
  .catch((e) => { console.error(e.message); process.exit(1); });
