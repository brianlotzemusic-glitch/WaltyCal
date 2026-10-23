// Pure helpers (no browser, no network) to read what a PUBLIC TpT product page says about price,
// "free", preview file and page count, and to compare it with the item's tpt.json.
// Used by tools/tpt.js (after publish, after a reupload fix) and mirrored in tools/tpt-verify-live.py.
// Offline test: node tools/test-tpt-live.js  (fixture: tpt/027-thanksgiving-color-by-note/live-page.fixture.html)

// The page embeds the product as JSON ("price", "isFree", "previewUrl", "pageCount"). Related products on the
// same page carry the same keys, so with the product id (the number at the end of its URL) every key is taken from
// the occurrence NEAREST to the product's own "id":<number>. Without an id, or when the id is not in the page, the
// first "isFree" is the anchor (less safe; the result then carries note: "anchored on first isFree").
function parseLive(html, productId) {
  html = String(html || "");
  let anchor = -1, note;
  if (productId) { const m = new RegExp('"(?:id|productId|itemId)"\\s*:\\s*"?' + productId + '\\b').exec(html); if (m) anchor = m.index; }
  if (anchor < 0) { anchor = html.search(/"isFree"\s*:\s*(true|false)/); note = "anchored on first isFree"; }
  if (anchor < 0) return { error: 'no "isFree" field in the page (blocked, login wall or TpT changed the page)' };
  // The product's own fields: from its id to the next other "id":<number> (or 4000 chars); else nearest anywhere.
  let end = anchor + 4000; { const nx = /"(?:id|productId|itemId)"\s*:\s*"?\d+/g; nx.lastIndex = anchor + 6; const m = nx.exec(html); if (m && m.index < end && productId) end = m.index; }
  const near = (re) => {
    let seg = null, m;
    const g = new RegExp(re.source, "g"); g.lastIndex = anchor;
    if ((m = g.exec(html)) && m.index < end) seg = m;
    if (seg) return seg;
    let best = null;
    re = new RegExp(re.source, "g");
    while ((m = re.exec(html))) { const d = Math.abs(m.index - anchor); if (d <= 4000 && (!best || d < best.d)) best = { d, m }; }
    return best && best.m;
  };
  const price = near(/"price"\s*:\s*"?(-?\d+(?:\.\d+)?)"?/);
  const prev = near(/"previewUrl"\s*:\s*(null|"[^"]*")/);
  const pages = near(/"pageCount"\s*:\s*"?(\d+)"?/);
  const free = near(/"isFree"\s*:\s*(true|false)/);
  const t = html.match(/<meta[^>]+property=["']og:title["'][^>]+content=["']([^"]*)["']/i) || html.match(/<title>([^<]*)<\/title>/i);
  const out = {
    price: price ? Number(price[1]).toFixed(2) : null,
    isFree: free ? free[1] === "true" : undefined,
    previewUrl: prev ? (prev[1] === "null" ? null : prev[1].slice(1, -1)) : undefined,
    pageCount: pages ? Number(pages[1]) : null,
    title: t ? t[1].replace(/&amp;/g, "&").replace(/&#39;|&#x27;/g, "'").replace(/&quot;/g, '"').replace(/\s+/g, " ").trim() : null,
  };
  if (note) out.note = note;
  const missing = [];
  if (out.price === null) missing.push("price");
  if (out.isFree === undefined) missing.push("isFree");
  if (out.previewUrl === undefined) { missing.push("previewUrl"); out.previewUrl = null; }
  if (missing.length) out.error = "no " + missing.join("/") + " field found near the product in the page (TpT changed the page?)";
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
  if (expected.pages && live.pageCount !== null && Number(expected.pages) !== live.pageCount) p.push(`pages: live ${live.pageCount}, tpt.json ${expected.pages}`);
  return p;
}

module.exports = { parseLive, compareLive };
