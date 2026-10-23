// Offline test (no browser, no TpT, no network) for the "paid item came out free" fixes (027, 22 Oct 2026):
// publish guards, public-page parser, reupload `fix` marker, tools/tpt-verify-live.py. Run: node tools/test-tpt-live.js
const fs = require("fs"), path = require("path"), os = require("os"), assert = require("assert"), cp = require("child_process");
const ROOT = path.dirname(__dirname);
const T = require("./tpt.js"), L = require("./tpt-live.js");
const F = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8"));
const I27 = path.join(ROOT, "tpt", "027-thanksgiving-color-by-note");
const html = fs.readFileSync(path.join(I27, "live-page.fixture.html"), "utf8");
const cfg27 = JSON.parse(fs.readFileSync(path.join(I27, "tpt.json"), "utf8"));

// 1. public-page parser: the broken 027 page is detected, the related product on the page is ignored
let live = L.parseLive(html, "18040698");
assert.deepStrictEqual([live.price, live.isFree, live.previewUrl, live.pageCount], ["0.00", true, null, 58]);
const probs = L.compareLive(cfg27, live);
assert.strictEqual(probs.length, 3, probs.join("|"));
assert(probs.some((m) => /^price/.test(m)) && probs.some((m) => /^isFree/.test(m)) && probs.some((m) => /^previewUrl/.test(m)));
const fixed = html.replace('"price":"0.00","isFree":true,"previewUrl":null', '"price":"3.75","isFree":false,"previewUrl":"https://example.invalid/p.pdf"');
assert.deepStrictEqual(L.compareLive(cfg27, L.parseLive(fixed, "18040698")), []);
assert(L.compareLive(cfg27, L.parseLive("<html>login wall</html>", "1")).length > 0); // unparsable page = mismatch, never a pass
assert.strictEqual(L.compareLive({ ...cfg27, free: true, price: "0.00", license_price: "0.00" }, L.parseLive(html, "18040698")).some((m) => /isFree/.test(m)), false);
console.log("ok parser: broken 027 page gives price/isFree/previewUrl mismatches, fixed page passes, junk page fails");

// 2. publish guards (checkItem)
const base = () => ({ ...T.loadItem(I27) });
assert.deepStrictEqual(T.checkItem(I27, base(), F), []);
for (const bad of [{ price: undefined }, { price: "0.00", license_price: "0.00" }, { price: "0" }, { license_price: "0.00" }])
  assert(T.checkItem(I27, { ...base(), ...bad }, F).length > 0, JSON.stringify(bad));
assert(T.checkItem(I27, { ...base(), price: "0.00", license_price: "0.00" }, F).some((m) => /not marked "free": true/.test(m)));
assert(T.checkItem(I27, { ...base(), free: "true" }, F).some((m) => /free must be true or false/.test(m)));
{ const it = base(); it.files = { ...it.files }; delete it.files.preview; assert(T.checkItem(I27, it, F).some((m) => /files\.preview is not set/.test(m))); }
{ const it = base(); it.files = { ...it.files, preview: "nope-PREVIEW.pdf" }; assert(T.checkItem(I27, it, F).some((m) => /missing file/.test(m))); }
console.log("ok publish guards: missing/0 price without free:true, string free, missing preview declaration, missing preview file");

// 3. every item (live or not) passes; 028-030 are complete (price, preview, free flag as intended)
for (const d of fs.readdirSync(path.join(ROOT, "tpt")).filter((n) => /^\d{3}-/.test(n))) {
  const dir = path.join(ROOT, "tpt", d), it = T.loadItem(dir);
  assert.deepStrictEqual(T.checkItem(dir, it, F), [], d);
}
const t = (n) => JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", n, "tpt.json"), "utf8"));
assert.deepStrictEqual([t("028-free-color-by-note-sampler").free, t("028-free-color-by-note-sampler").price], [true, "0.00"]);
for (const [n, price] of [["029-winter-color-by-note", "3.75"], ["030-dmp1-units-1-6-bundle", "49.00"]]) {
  const c = t(n); assert.strictEqual(c.price, price); assert.strictEqual(c.license_price, price); assert.notStrictEqual(c.free, true);
  assert(fs.existsSync(path.join(ROOT, "tpt", n, c.files.preview)), n + " preview");
}
console.log("ok all items pass checkItem; 028 free, 029 3.75, 030 49.00 with preview files");

// 4. marker directives + reupload fix planning
const m = T.parseMarker(fs.readFileSync(path.join(I27, "reupload"), "utf8"));
assert.deepStrictEqual([m.files, m.fix, m.problems], [true, ["price", "preview"], []]);
assert.deepStrictEqual(T.parseMarker("2026 old marker\n").fix, []);
assert(T.parseMarker("fix: price, colour\n").problems.length === 1);
assert.strictEqual(T.parseMarker("files: none\nfix: preview").files, false);
const st = T.reuploadState(I27);
assert.strictEqual(st.state, "pending"); assert.deepStrictEqual(st.directives.fix, ["price", "preview"]);
const ids = ["ItemDigitalProduct", "ItemDigitalPreview", "ItemDigitalThumb1", "ItemDigitalThumb2", "ItemDigitalThumb3", "ItemDigitalThumb4", "item-price", "item-license-price", "item-free"];
const ef = { fields: ids.map((id) => ({ id })), edit_url_template: "https://x/{id}" };
let pl = T.prepareReupload(I27, F, ef);
assert.deepStrictEqual(pl.problems, []); assert.strictEqual(pl.files.length, 6); assert.deepStrictEqual(pl.fix, ["price", "preview"]);
// same-night gate: an edit form without the price/free boxes is NOT ready for the fix
const noFree = T.prepareReupload(I27, F, { ...ef, fields: ef.fields.filter((f) => f.id !== "item-free") });
assert(noFree.problems.some((p) => /fix price: edit form has no field for free/.test(p)));
// price 0 in tpt.json can never be "fixed" into the product
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "fix-"));
fs.cpSync(I27, tmp, { recursive: true, filter: (s) => !/build|__pycache__/.test(s) });
fs.writeFileSync(path.join(tmp, "tpt.json"), JSON.stringify({ ...cfg27, price: "0.00", license_price: "0.00" }));
assert(T.prepareReupload(tmp, F, ef).problems.some((p) => /fix price: tpt.json price must be a price above 0/.test(p)));
fs.writeFileSync(path.join(tmp, "tpt.json"), JSON.stringify(cfg27));
fs.writeFileSync(path.join(tmp, "reupload"), "files: none\nfix: preview\n");
pl = T.prepareReupload(tmp, F, ef); assert.deepStrictEqual(pl.files.map((f) => f.slot), ["preview"]);
fs.writeFileSync(path.join(tmp, "reupload"), "files: none\n");
assert(T.prepareReupload(tmp, F, ef).problems.some((p) => /asks for nothing/.test(p)));
fs.rmSync(tmp, { recursive: true });
console.log("ok marker directives, fix planning, same-night gate");

// 5. CLI dry-run of the real 027 marker is offline and writes nothing
const before = cp.execSync("git status --porcelain", { cwd: ROOT }).toString();
const r = cp.spawnSync("node", [path.join(ROOT, "tools", "tpt.js"), "reupload", "tpt/027-thanksgiving-color-by-note", "--dry-run"], { encoding: "utf8" });
assert.strictEqual(r.status, 0, r.stderr);
assert(/price 3\.75 and license price 3\.75/.test(r.stdout) && /un-tick/.test(r.stdout) && /PREVIEW\.pdf/.test(r.stdout), r.stdout);
assert.strictEqual(cp.execSync("git status --porcelain", { cwd: ROOT }).toString(), before);
console.log("ok CLI dry-run lists the price/preview fix");

// 6. Manager script against the saved copy (offline) exits 1 on the broken page, 0 on a fixed one
const dir = fs.mkdtempSync(path.join(os.tmpdir(), "live-"));
const py = (...a) => cp.spawnSync("python3", ["-I", path.join(ROOT, "tools", "tpt-verify-live.py"), ...a], { encoding: "utf8" });
fs.writeFileSync(path.join(dir, "027-thanksgiving-color-by-note.html"), html);
let o = py("027", "--offline", dir); assert.strictEqual(o.status, 1, o.stdout + o.stderr); assert(/MISMATCH/.test(o.stdout) && /isFree/.test(o.stdout));
fs.writeFileSync(path.join(dir, "027-thanksgiving-color-by-note.html"), fixed);
o = py("027", "--offline", dir); assert.strictEqual(o.status, 0, o.stdout + o.stderr);
fs.writeFileSync(path.join(dir, "027-thanksgiving-color-by-note.html"), "<html></html>");
assert.strictEqual(py("027", "--offline", dir).status, 1);
fs.rmSync(dir, { recursive: true });
console.log("ok tools/tpt-verify-live.py exit codes");
