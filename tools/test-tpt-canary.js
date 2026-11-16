// Offline test for tools/tpt-reupload-canary.py (temp repo copy, nothing in the real tree is touched). Run: node tools/test-tpt-canary.js
const assert = require("assert"), fs = require("fs"), os = require("os"), path = require("path"), cp = require("child_process"), crypto = require("crypto");
const ROOT = path.dirname(__dirname);
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "canary-")), tpt = path.join(tmp, "tpt");
fs.mkdirSync(tpt);
const run = (...a) => cp.spawnSync("python3", ["-I", path.join(ROOT, "tools", "tpt-reupload-canary.py"), ...a, "--root", tmp], { encoding: "utf8" });
const mk = (name, marker, extra = {}) => { const d = path.join(tpt, name); fs.mkdirSync(d); if (marker) fs.writeFileSync(path.join(d, "reupload"), marker); fs.writeFileSync(path.join(d, "uploaded"), "x\nhttps://www.teacherspayteachers.com/Product/a-1\n"); for (const [k, v] of Object.entries(extra)) fs.writeFileSync(path.join(d, k), v); return d; };
const h = (t) => crypto.createHash("sha256").update(t).digest("hex");
const M = "2026-11-16 fix: x\n";
const d001 = mk("001-halloween", M), d043 = mk("043-drills", M), d042 = mk("042-escape", M), d002 = mk("002-fall", M, { "reupload-failed": JSON.stringify({ marker_sha256: h(M), step: "s", error: "e" }) });
const d010 = mk("010-done", M, { reuploaded: JSON.stringify({ marker_sha256: h(M) }) });
const pause = path.join(tpt, "REUPLOAD-PAUSED");

fs.writeFileSync(pause, "Paused.\n");
assert(/PAUSED-ALL/.test(run("status").stdout));
fs.writeFileSync(pause, "Paused 2026-11-16.\nallow: 043\n");
let o = run("status").stdout; assert(/^WAITING\s+canary 043-drills/m.test(o) && /wait for the Mac/.test(o), o);
assert.strictEqual(run("release").status, 1); assert(fs.existsSync(pause));
fs.writeFileSync(path.join(d043, "reupload-failed"), JSON.stringify({ marker_sha256: h(M), step: "replace product", error: "TpT did not accept" }));
o = run("status").stdout; assert(/^FAILED\s+canary 043-drills \| replace product: TpT did not accept/m.test(o) && /convert/.test(o), o);
// re-armed canary (new marker text) is WAITING again; then PASSED
fs.writeFileSync(path.join(d043, "reupload"), M + "re-armed after fix 2\n");
assert(/^WAITING/m.test(run("status").stdout));
fs.writeFileSync(path.join(d043, "reuploaded"), JSON.stringify({ marker_sha256: h(M + "re-armed after fix 2\n") }));
o = run("status").stdout; assert(/^PASSED/m.test(o) && /release/.test(o), o);
assert.strictEqual(run("release").status, 0); assert(!fs.existsSync(pause));
assert(/NOT-PAUSED/.test(run("status").stdout));
console.log("ok status WAITING/FAILED/PASSED, release only after PASSED");

// convert: every waiting reupload except 001 and already-replaced items becomes republish (same text); pause removed
fs.writeFileSync(pause, "Paused.\nallow: 043\n");
fs.rmSync(path.join(d043, "reuploaded")); // pretend 043 failed for good
o = run("convert", "--dry-run").stdout; assert(/would convert 042-escape/.test(o) && fs.existsSync(path.join(d042, "reupload")) && fs.existsSync(pause));
o = run("convert").stdout;
for (const d of [d042, d043, d002]) { assert(!fs.existsSync(path.join(d, "reupload")), d); assert(fs.existsSync(path.join(d, "republish")), d); }
assert.strictEqual(fs.readFileSync(path.join(d042, "republish"), "utf8"), M);
assert(fs.existsSync(path.join(d001, "reupload")) && !fs.existsSync(path.join(d001, "republish")), "001 is never converted");
assert(fs.existsSync(path.join(d010, "reupload")) && !fs.existsSync(path.join(d010, "republish")), "a done replacement is not republished");
assert(!fs.existsSync(pause));
console.log("ok convert: all waiting except 001 and done ones -> republish (same text), pause deleted");
fs.rmSync(tmp, { recursive: true });
