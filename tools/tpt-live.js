// Pure helpers (no browser, no network) to read what a PUBLIC TpT product page says about price,
// "free", preview file and page count, and to compare it with the item's tpt.json.
// Used by tools/tpt.js (after publish, after a reupload fix) and mirrored in tools/tpt-verify-live.py.
// Offline test: node tools/test-tpt-live.js  (fixture: tpt/027-thanksgiving-color-by-note/live-page.fixture.html)

// Real TpT product page (checked 23 Oct 2026): JSON-LD Offer `"@type":"Offer",...,"price":"3.75"` and the embedded app JSON
// `"isFree":false`, `"pageCount":"58"`, `"previewUrl":null|"\u002FPreview\u002F..."`. The FIRST occurrence of each is the product's
// own (related products come later). Quotes may be backslash-escaped and whitespace may vary. Anything not found is an
// error, so a changed/blocked page can never pass as a match (fail-safe). productId is accepted for compatibility, unused.
function parseLive(html) {
  html = String(html || "");
  const q = '\\\\?"'; // optional backslash before a quote
  const first = (re) => { const m = re.exec(html); return m ? m[1] : undefined; };
  const offer = /@type\\?"\s*:\s*\\?"Offer\\?"[\s\S]{0,600}?price\\?"\s*:\s*\\?"?(-?\d+(?:\.\d+)?)/.exec(html);
  const free = first(/isFree\\?"\s*:\s*(true|false)/);
  const prev = first(/previewUrl\\?"\s*:\s*(null|\\?"[^"]+)/);
  const pages = first(/pageCount\\?"\s*:\s*\\?"?(\d+)/);
  const t = html.match(/<meta[^>]+property=["']og:title["'][^>]+content=["']([^"]*)["']/i) || html.match(/<title>([^<]*)<\/title>/i);
  const out = {
    price: offer ? Number(offer[1]).toFixed(2) : null,
    isFree: free === undefined ? undefined : free === "true",
    previewUrl: prev === undefined ? undefined : prev === "null" ? null : prev.replace(/^\\?"/, ""),
    pageCount: pages ? Number(pages) : null,
    title: t ? t[1].replace(/&amp;/g, "&").replace(/&#39;|&#x27;/g, "'").replace(/&quot;/g, '"').replace(/\s+/g, " ").trim() : null,
  };
  const missing = [];
  if (out.price === null) missing.push("price");
  if (out.isFree === undefined) missing.push("isFree");
  if (out.previewUrl === undefined) { missing.push("previewUrl"); out.previewUrl = null; }
  if (missing.length) out.error = "no " + missing.join("/") + " field found in the page (blocked, login wall or TpT changed the page)";
  return out;
}

// expected = tpt.json object. Returns a list of mismatch strings ([] = the live page matches).
function compareLive(expected, live) {
  const p = [];
  if (live.error) p.push(live.error);
  const wantFree = expected.free === true;
  if (live.price !== null && Number(live.price) !== Number(expected.price)) p.push(`price: live ${live.price}, tpt.json ${Number(expected.price).toFixed(2)}`);
  if (live.isFree !== undefined && live.isFree !== wantFree) p.push(`isFree: live ${live.isFree}, expected ${wantFree}`);
  const wantPreview = !!(expected.files && expected.files.preview);
  if (wantPreview && !live.previewUrl && !live.error) p.push("previewUrl: live page has no preview file (tpt.json declares one)");
  return p;
}

// Page count differs from tpt.json: a WARNING only (TpT derives it itself; 015-018 show 1-2 fewer pages live than
// tpt.json on 23 Oct 2026). Never makes compareLive fail.
function pageWarning(expected, live) {
  return expected.pages && live.pageCount !== null && Number(expected.pages) !== live.pageCount ? `pages: live ${live.pageCount}, tpt.json ${expected.pages}` : null;
}

module.exports = { parseLive, compareLive, pageWarning };
