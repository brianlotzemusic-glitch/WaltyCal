// Offline test for `reupload` in tools/tpt.js (no browser, no TpT). Run: node tools/test-tpt-reupload.js
const fs = require("fs"), path = require("path"), os = require("os"), assert = require("assert"), cp = require("child_process");
const ROOT = path.dirname(__dirname);
const T = require("./tpt.js");
const F = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8"));
const URL = "https://www.teacherspayteachers.com/Product/Fall-Color-by-Note-18040698";
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "reup-"));
const mk = (name, o = {}) => {
  const d = path.join(tmp, name); fs.mkdirSync(d);
  fs.writeFileSync(path.join(d, "QA.md"), "**Verdict: APPROVED**\n");
  fs.writeFileSync(path.join(d, "a.pdf"), "pdfdata"); fs.writeFileSync(path.join(d, "c.png"), "png");
  fs.writeFileSync(path.join(d, "tpt.json"), JSON.stringify({ files: { product: "a.pdf", thumb1: "c.png" } }));
  for (const [k, v] of Object.entries(o)) if (v !== null) fs.writeFileSync(path.join(d, k), v);
  return d;
};
const up = `2026-10-22T13:17:38Z published live\n${URL}\n`;
const ef = { fields: [{ id: "ItemDigitalProduct" }, { id: "ItemDigitalThumb1" }], edit_url_template: "https://x/{id}" };

assert.strictEqual(T.reuploadState(mk("nomarker", { uploaded: up })).state, "no-marker");
assert.strictEqual(T.reuploadState(mk("nourl", { reupload: "m1\n" })).state, "no-url");
assert.strictEqual(T.reuploadState(mk("badurl", { reupload: "m1\n", uploaded: "x\nhttps://evil.example/Product/a-1\n" })).state, "no-url");
const d = mk("ok", { reupload: "m1\n", uploaded: up });
let st = T.reuploadState(d); assert.strictEqual(st.state, "pending"); assert.strictEqual(st.productId, "18040698");
console.log("ok refusals and pending");

let pl = T.prepareReupload(d, F, ef);
assert.deepStrictEqual(pl.problems, []); assert.strictEqual(pl.files.length, 2);
assert.strictEqual(pl.files[0].sha256, T.sha256File(path.join(d, "a.pdf")));
assert(T.prepareReupload(d, F, null).problems[0].includes("EDIT-FIELDS.json is missing"));
assert(T.prepareReupload(d, F, { ...ef, fields: [{ id: "ItemDigitalProduct" }] }).problems.some((m) => /no file box for thumb1/.test(m)));
assert.deepStrictEqual(T.prepareReupload(d, F, undefined).problems, []);
console.log("ok hashing, EDIT-FIELDS gate");

// state machine: done holds until a NEW marker; failed holds until a new marker
fs.writeFileSync(path.join(d, "reuploaded"), JSON.stringify({ marker_sha256: st.markerHash }));
assert.strictEqual(T.reuploadState(d).state, "done");
fs.writeFileSync(path.join(d, "reupload"), "m2 new date\n");
assert.strictEqual(T.reuploadState(d).state, "pending");
fs.writeFileSync(path.join(d, "reupload-failed"), JSON.stringify({ marker_sha256: T.reuploadState(d).markerHash }));
assert.strictEqual(T.reuploadState(d).state, "failed-hold");
fs.writeFileSync(path.join(d, "reupload"), "m3\n");
assert.strictEqual(T.reuploadState(d).state, "pending");
fs.writeFileSync(path.join(d, "QA.md"), "**Verdict: REJECT**\n");
assert.strictEqual(T.reuploadState(d).state, "not-approved");
console.log("ok state machine");

// CLI: real repo. 001 untouched, 027 dry-run lists files and writes nothing.
const run = (...a) => cp.spawnSync("node", [path.join(ROOT, "tools", "tpt.js"), ...a], { encoding: "utf8" });
const before = cp.execSync("git status --porcelain", { cwd: ROOT }).toString();
// 16 Nov 2026: 001 DOES carry a `reupload` marker now (art fix; it has a sale, so file replacement is its only route). The refusal
// check therefore uses a temp copy of 001 WITHOUT the marker; the real 001 must dry-run (offline, lists its files, writes nothing).
const t001 = fs.mkdtempSync(path.join(os.tmpdir(), "r001-"));
fs.cpSync(path.join(ROOT, "tpt", "001-halloween-color-by-note"), t001, { recursive: true, filter: (s) => !/build|__pycache__/.test(s) });
fs.rmSync(path.join(t001, "reupload"), { force: true });
const r1 = run("reupload", t001, "--dry-run");
assert.notStrictEqual(r1.status, 0); assert(/no `reupload` marker/.test(r1.stderr));
const r2 = run("reupload", t001);
assert.notStrictEqual(r2.status, 0); assert(/no `reupload` marker/.test(r2.stderr));
fs.rmSync(t001, { recursive: true });
if (fs.existsSync(path.join(ROOT, "tpt", "001-halloween-color-by-note", "reupload"))) {
  const r0 = run("reupload", "tpt/001-halloween-color-by-note", "--dry-run");
  assert(r0.status === 0 ? /DRY RUN/.test(r0.stdout) : /reupload-failed|already processed|QA\.md/.test(r0.stderr), r0.stdout + r0.stderr);
}
// a COPY of 027 without the Mac's result markers (the real folder's state changes with every Mac run)
const t027 = fs.mkdtempSync(path.join(os.tmpdir(), "c027-"));
fs.cpSync(path.join(ROOT, "tpt", "027-thanksgiving-color-by-note"), t027, { recursive: true, filter: (s) => !/build|__pycache__/.test(s) });
for (const f of ["reuploaded", "reupload-failed", "reupload-unverified"]) fs.rmSync(path.join(t027, f), { force: true });
const r3 = run("reupload", t027, "--dry-run");
assert.strictEqual(r3.status, 0, r3.stderr);
for (const f of ["thanksgiving-color-by-note.pdf", "thanksgiving-color-by-note-PREVIEW.pdf", "cover.png", "preview-1.png", "preview-2.png", "preview-3.png"]) assert(r3.stdout.includes(f), f);
assert(/Would NOT change: title, /.test(r3.stdout));
if (!fs.existsSync(path.join(ROOT, "tpt", "EDIT-FIELDS.json"))) { // real run must refuse before opening any browser
  const r4 = run("reupload", "tpt/027-thanksgiving-color-by-note");
  assert.notStrictEqual(r4.status, 0); assert(/EDIT-FIELDS\.json is missing/.test(r4.stderr), r4.stderr);
}
assert.strictEqual(cp.execSync("git status --porcelain", { cwd: ROOT }).toString(), before);
console.log("ok CLI: 001 refused, 027 dry-run lists 6 files, real run refuses without EDIT-FIELDS.json, nothing written");
fs.rmSync(tmp, { recursive: true });

// Real EDIT-FIELDS.json (recorded 23 Oct from 027's edit form): #item-free exists but price/license/tax boxes do NOT
// (hidden while Free Resource is ON). The 027 `fix: price, preview` marker must pass the prerequisite check.
{
  const real = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "EDIT-FIELDS.json"), "utf8"));
  const ids = real.fields.map((f) => f.id);
  assert(ids.includes("item-free") && !ids.includes("item-price") && !ids.includes("item-license-price"));
  // a COPY of 027 with its 23 Oct `fix: price, preview` marker (the real marker is rewritten by other sessions)
  const item27 = fs.mkdtempSync(path.join(os.tmpdir(), "r027-"));
  fs.cpSync(path.join(ROOT, "tpt", "027-thanksgiving-color-by-note"), item27, { recursive: true, filter: (s) => !/build|__pycache__/.test(s) });
  for (const f of ["reuploaded", "reupload-failed"]) fs.rmSync(path.join(item27, f), { force: true });
  fs.writeFileSync(path.join(item27, "reupload"), "2026-10-23 fix 027\nfix: price, preview\n");
  const p27 = T.prepareReupload(item27, F, real);
  assert.deepStrictEqual(p27.problems, []);
  assert(p27.fix.includes("price") && p27.fix.includes("preview") && p27.cfg.tax_code);
  // without #item-free the fix price prerequisite must refuse
  const noFree = { ...real, fields: real.fields.filter((f) => f.id !== "item-free") };
  assert(T.prepareReupload(item27, F, noFree).problems.some((m) => /no Free Resource control/.test(m)));
  console.log("ok real EDIT-FIELDS: 027 passes, refuses without #item-free");
}
// shared helpers exported for the fix
assert.strictEqual(typeof T.pickListbox, "function"); assert.strictEqual(typeof T.freeIsOn, "function");
// screenshot push list: only failure shots, <= 1.5 MB, force-added
{
  const sh = fs.readFileSync(path.join(ROOT, "tools", "tpt-add-shots.sh"), "utf8");
  for (const g of ["*-failed*.png", "*-free*.png", "*-dropdown*.png", "*-fix-subject*.png", "*-fix-untick*.png", "git add -f", "1572864"]) assert(sh.includes(g), g);
  assert(!/-filled|-submitted/.test(sh.replace(/#.*$/gm, "")));
  for (const n of ["tpt-nightly.sh", "tpt-collect-diagnostics.sh"]) assert(fs.readFileSync(path.join(ROOT, "tools", n), "utf8").includes("tpt_add_shots"), n);
  console.log("ok screenshot push list");
}

// QA verdict formats (22 Oct bug: 027 "## Verdict: APPROVE", 029 "**Verdict: APPROVE (...)**" were not recognised)
{
  const t2 = fs.mkdtempSync(path.join(os.tmpdir(), "qa-"));
  const qa = (txt, rel) => { const x = fs.mkdtempSync(path.join(t2, "i-")); fs.writeFileSync(path.join(x, "QA.md"), txt); if (rel) fs.writeFileSync(path.join(x, "release"), rel); return x; };
  assert(T.isApproved(qa("**Verdict: APPROVED**\n")));
  assert(T.isApproved(qa("**Verdict: REJECT (x)**\n\n## Verdict: APPROVE\n")));
  assert(T.isApproved(qa("# Round 3\n\n**Verdict: APPROVE (every picture B)**\n")));
  assert(!T.isApproved(qa("**Verdict: APPROVE**\n\n**Verdict: REJECTED** (tags)\n")));
  assert(!T.isApproved(qa("no verdict here\n")));
  assert(T.releasedOverQA(qa("**Verdict: REJECTED**\n", "released; fix verified by Manager")));
  assert(!T.releasedOverQA(qa("**Verdict: REJECTED**\n", "released")));
  console.log("ok QA verdict parsing");
}
