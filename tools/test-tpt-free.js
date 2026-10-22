// Offline test for the free-item support in tools/tpt.js (no browser, no TpT). Run: node tools/test-tpt-free.js
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = path.dirname(__dirname);
const { checkItem, loadItem } = require("./tpt.js");
const F = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM.json"), "utf8"));
const fields = JSON.parse(fs.readFileSync(path.join(ROOT, "tpt", "FORM-FIELDS.json"), "utf8"));

// 1. FORM.json's free selector is an id that FORM-FIELDS.json lists on the Digital Download form.
assert.strictEqual(F.free, "#item-free");
const form = fields.pages.find((p) => p.step === "digital-download-form").fields;
const hit = form.find((f) => "#" + f.id === F.free);
assert(hit && /free resource/i.test(hit.label), "#item-free not in FORM-FIELDS.json");
console.log("ok selector", F.free, "->", hit.tag, JSON.stringify(hit.label));

// 2. The real free item passes the offline checks.
const item = path.join(ROOT, "tpt", "028-free-color-by-note-sampler");
const it = loadItem(item);
assert.strictEqual(it.free, true);
assert.deepStrictEqual(checkItem(item, it, F), []);
console.log("ok 028 passes checkItem");

// 3. Missing selector fails safely; non-zero price on a free item is flagged.
const noSel = { ...F }; delete noSel.free;
assert(checkItem(item, it, noSel).some((m) => /no `free` selector/.test(m)));
assert(checkItem(item, { ...it, price: "3.00" }, F).some((m) => /free item needs price/.test(m)));
console.log("ok missing selector and non-zero price are reported");

// 4. Paid items: free:false/absent gives exactly the same result as before, with or without the selector.
const paid = { ...it, free: undefined, price: "3.50", license_price: "5.00" };
assert.deepStrictEqual(checkItem(item, paid, F), checkItem(item, paid, noSel));
assert.deepStrictEqual(checkItem(item, { ...paid, free: false }, noSel), []);
console.log("ok paid items unaffected");
