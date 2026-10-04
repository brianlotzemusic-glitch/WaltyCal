# TpT discover report — 2026-10-04 (owner's Mac)

**Status: BLOCKED at step 2 (global Playwright install). `discover` was not run in this pass.
Nothing was created, saved or published on TpT.**

The earlier cloud report (blocked by `ERR_CERT_AUTHORITY_INVALID` behind the container proxy) is
superseded: on the owner's Mac, TpT loads normally.

## What ran

1. Branch `shop-factory`, pulled (already up to date at `d4a9c92`).
   - `TPT_VA_EMAIL`: set. `TPT_VA_PASSWORD`: set. (Both come from `~/.tpt-env`; neither is in the
     default shell environment, so `source ~/.tpt-env` is needed first, as LOCAL-SETUP.md says.)
2. Node.js v24.14.1 (`/usr/local/bin/node`) is installed. `npm install -g playwright` failed:

```
npm error code EACCES
npm error syscall mkdir
npm error path /usr/local/lib/node_modules/playwright
Error: EACCES: permission denied, mkdir '/usr/local/lib/node_modules/playwright'
```

`/usr/local/lib/node_modules` is owned by `root`, so a global install needs `sudo` (or an npm
prefix the user owns). Per the instructions, no workaround was attempted and `discover` was not run.

## Before re-running: the login step will also fail

An earlier run today (same Mac, Playwright installed locally in the repo with
`npm install playwright`, still present as untracked `node_modules/`) showed that
`tools/tpt.js` cannot log in as written:

```
page.fill: Timeout 30000ms exceeded.
  - waiting for locator('input[type="email"], input[name="email"], input[name="username"]')
```

TpT's login page (`https://www.teacherspayteachers.com/Login`) has:

| Field | Selector | Type |
| --- | --- | --- |
| Email or username | `#lc-email-username-input` | `text` (no `name`) |
| Password | `#lc-password-input` | `password` (no `name`) |
| Log in button | `#login_button_submit` | `submit` |

None of the script's email selectors match. Add `#lc-email-username-input` to the fill selector.

With that one selector added (run from a patched copy outside the repo; the repo script was not
changed), login succeeded with no CAPTCHA, no verification code and no bot block. That run
produced the `FORM-FIELDS.json` committed in `d4a9c92`.

## What that earlier run found about the form

- **Add-resource URL:** `https://www.teacherspayteachers.com/My-Products/New-Item`
- **Step 1 is a product-type picker, not the form.** Heading "Select a Product Type". Options:
  - Single Product: **Digital Download** ("Select a file from your computer"), **Video**,
    **Google Drive**, **Easel** (Easel Activities/Assessments listed by themselves)
  - Bundle of products: **Bundle of Resources**
- `discover` stops on this page, so `FORM-FIELDS.json` holds only the site header/footer
  controls and a reCAPTCHA token textarea (`#g-recaptcha-response-100000`,
  `name="g-recaptcha-response"`). The type options were not captured (they aren't
  `input`/`button` elements matched by `formFields`).
- **Not yet known:** the listing form's own fields (title, description, grades, subjects, price,
  resource file, thumbnails, preview, accepted file types, size limits) and its step order,
  because `discover` has to click **Digital Download** first.

## Fragility noted so far

- Login fields have stable ids but no `name` or `type=email`; selectors must use the ids.
- A reCAPTCHA token field is present on the New-Item page, so TpT may challenge automated
  sessions even though this login wasn't challenged.
- The new-item flow is multi-step (type picker, then form), and the picker's options aren't
  plain buttons, so they need role/text-based locators.
- The "add resource" entry is found by visible text (`/add (a )?(new )?(product|resource)/i`),
  which breaks on wording changes. Navigating straight to `/My-Products/New-Item` would avoid it.

## To unblock

1. Owner: install Playwright where the script can find it: either `sudo npm install -g playwright`
   (needs the Mac password), or keep using the repo-local `node_modules/` that already exists
   (`require("playwright")` finds it before the `npm root -g` fallback).
2. Factory: add `#lc-email-username-input` to the login selector, and make `discover` click
   **Digital Download** and capture the form after it.
3. `node_modules/`, `package.json` and `package-lock.json` are untracked in the repo;
   consider gitignoring them so they don't get committed by accident.
