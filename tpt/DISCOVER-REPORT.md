# TpT discover report — 2026-10-04

**Status: BLOCKED before login. No form data collected. Nothing was created, saved or published on TpT.**

## What ran

1. Branch `shop-factory`. `TPT_VA_EMAIL`: set. `TPT_VA_PASSWORD`: set.
2. `node tools/tpt.js discover` failed on the first navigation:

```
page.goto: net::ERR_CERT_AUTHORITY_INVALID at https://www.teacherspayteachers.com/Login
```

Process exited with code 1. No screenshots or HTML were written; `tpt/_discover/` was never created.

## Cause

The cloud container sends outbound HTTPS through an agent proxy that re-signs TLS with its
own CA (`/root/.ccr/ca-bundle.crt`). Headless Chromium launched by Playwright does not trust
that CA, so the TpT login page never loaded. This is a container/browser trust issue, not a
TpT login failure: the credentials were never submitted, and there is no evidence yet about
CAPTCHA, verification codes or bot blocking.

Per the test instructions, no workaround was attempted.

## Sections not filled (no data)

- Login result / CAPTCHA / verification / bot block: unknown (page never loaded)
- Add-resource form URL: unknown
- Form fields per step (label, type, selector, required): unknown
- File upload fields (resource file, thumbnails, preview): unknown
- Step/page order: unknown

## Options for the owner to decide (not done)

- Make Chromium trust the proxy CA, e.g. launch with `ignoreHTTPSErrors: true` on the
  browser context in `tools/tpt.js`, or add the CA to the NSS database Chromium reads
  (`certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n ccr -i /root/.ccr/ca-bundle.crt`).
  The first option disables certificate checking for the whole session, which matters
  because the session submits the VA password; the NSS option keeps verification on.
- Or run `discover` on a local machine outside the proxy.

## Fragility already visible (from reading `tools/tpt.js`)

- Login waits a fixed 3 s after pressing Enter and decides success by "URL no longer
  contains `/Login`"; a slow redirect or an interstitial would be misread.
- CAPTCHA/2FA detection is a regex over the whole page HTML (`captcha|verify it's you|...`);
  pages that merely load a CAPTCHA script (e.g. reCAPTCHA on the login page) would trip it
  even after a successful login.
- The "add resource" button is found by visible text (`/add (a )?(new )?(product|resource)/i`),
  which breaks on wording changes.
