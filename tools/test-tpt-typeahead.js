// Offline test for the typeahead and free-item step logic in tools/tpt.js (no browser, no TpT). Run: node tools/test-tpt-typeahead.js
const assert = require("assert");
const { typeaheadPrefixes, matchOption, publishSteps } = require("./tpt.js");

// Selector order: full text first, then progressively shorter prefixes.
assert.deepStrictEqual(typeaheadPrefixes("Career and Technical Education"),
  ["Career and Technical Education", "Career and Technical", "Career and", "Career"]);
assert.deepStrictEqual(typeaheadPrefixes("Music"), ["Music"]);
assert.deepStrictEqual(typeaheadPrefixes("  Computer Science - Technology "), ["Computer Science - Technology", "Computer Science -", "Computer Science", "Computer"]);
console.log("ok prefix order");

// Option matching: case-insensitive, whitespace-normalised, exact (no partial matches), group labels tolerated.
assert.strictEqual(matchOption(["Career and Technical Education", "Career Education"], "career and technical education"), 0);
assert.strictEqual(matchOption(["Music", "Music Composition"], "Music"), 0);
assert.strictEqual(matchOption(["Music Composition"], "Music"), -1);
assert.strictEqual(matchOption(["Specialty\nCareer and  Technical Education"], "Career and Technical Education"), 0);
assert.strictEqual(matchOption([], "Music"), -1);
console.log("ok option matching");

// Step list: free items skip tax_code and prices; paid items (free false/absent) are unchanged.
assert.deepStrictEqual(publishSteps({ free: true }), ["free resource checkbox"]);
assert.deepStrictEqual(publishSteps({ free: false }), ["prices", "tax_code"]);
assert.deepStrictEqual(publishSteps({}), ["prices", "tax_code"]);
const fs = require("fs"), path = require("path");
const { loadItem } = require("./tpt.js");
const free = loadItem(path.join(__dirname, "..", "tpt", "028-free-color-by-note-sampler"));
assert(!publishSteps(free).includes("tax_code"));
const paid = loadItem(path.join(__dirname, "..", "tpt", "029-winter-color-by-note"));
assert(publishSteps(paid).includes("tax_code"));
console.log("ok step lists (028 free skips tax_code, 029 paid keeps it)");

// Renamed options still match (& vs and, dash variants).
assert.strictEqual(matchOption(["Career & Technical Education"], "Career and Technical Education"), 0);
assert.strictEqual(matchOption(["Computer Science – Technology"], "Computer Science - Technology"), 0);
assert.strictEqual(matchOption(["Career Education"], "Career and Technical Education"), -1);
console.log("ok normalised option matching");
