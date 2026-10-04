# TpT discover report — 2026-10-04, run 3 (owner's Mac, script at `955a298`)

**Status: BLOCKED at login. The browser stayed on the TpT login page until the script's 3-minute
timeout. No form data collected. Nothing was created, saved or published on TpT.**

## What ran

1. Branch `shop-factory`, pulled; includes `955a298`.
2. After `source ~/.tpt-env`: `TPT_VA_EMAIL`: set. `TPT_VA_PASSWORD`: set.
3. `node -e "require('playwright')"`: OK (repo-local `node_modules/`). Nothing installed.
4. `node tools/tpt.js discover` (unmodified), exit code 1:

```
Logging in. If TpT asks for a CAPTCHA or a code, complete it in the browser window...
still on the login page after 3 minutes: check the VA email/password, or finish TpT's verification step
```

## What the owner saw

The headed browser ("Google Chrome for Testing") sat on the login page "doing nothing" for the
whole wait. **No CAPTCHA, verification-code prompt or bot-block message was seen.** Nobody clicked
or typed in the window.

## Evidence

None from this run. The script only snapshots after a successful login, so a login failure leaves no
screenshot or HTML, and `FORM-FIELDS.json` was written as `{"pages": []}`. The files currently in
`tpt/_discover/` are from the 14:05 run and do not describe this run.

## Sections not filled (no data from this run)

- URL after choosing Digital Download, `file_chooser_opened`: not reached
- Listing-form fields, upload fields (resource file, thumbnails, preview), types and size limits: not reached
- Step/page order beyond the product-type picker: not reached

Still valid from the 14:05 run (same account, same Mac): login worked then with a selector change
equivalent to `955a298`, with no CAPTCHA or code; the add-resource URL is
`https://www.teacherspayteachers.com/My-Products/New-Item`, which opens a "Select a Product Type"
picker (Digital Download, Video, Google Drive, Easel, Bundle of Resources).

## Likely causes (not verified; no workaround attempted)

- **The fill happened before the login form was ready.** The script fills right after
  `domcontentloaded`. If TpT's login component renders or re-renders after that, the typed values are
  lost and Enter submits nothing, which matches a page that "does nothing". At 14:05 the same
  sequence worked, so this would be a timing race.
- **A silent block after repeated logins.** This was the third automated login today. TpT loads
  reCAPTCHA; an invisible challenge or rate limit can refuse the submit without showing a message.
- **Enter didn't submit.** The page has a real submit button, `#login_button_submit`; the script
  presses Enter instead of clicking it.

## Suggested script changes (for the factory; not made)

1. Before filling, wait until `#lc-email-username-input` is visible and enabled; after filling,
   check the value stuck; then click `#login_button_submit` instead of pressing Enter.
2. On login timeout, save `00-login-failed.png` / `.html` to `tpt/_discover/`, so the next report
   can quote any on-page error (wrong password, "too many attempts", challenge).
3. Leave some time before the next attempt, in case it's a rate limit.
