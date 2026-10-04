# TpT discover report — 2026-10-04, run 4 (owner's Mac, script at `f81e012`)

**Status: OK. Logged in, opened the product-type picker, chose Digital Download and captured the
listing form. Nothing was typed into the listing form, and nothing was saved, submitted or published.**

## Run

- Branch `shop-factory` includes `f81e012`. `TPT_VA_EMAIL`: set. `TPT_VA_PASSWORD`: set.
  `require('playwright')`: OK (repo-local). Nothing installed. Script unmodified.
- `node tools/tpt.js discover` exited 0: `Done. Nothing was created on TpT.`

## Login

- **Worked.** No CAPTCHA, no verification code, no bot-block message. No `00-login-failed.*` was written.
- reCAPTCHA **Enterprise** is loaded invisibly (anchor iframe from `google.com/recaptcha/enterprise`, plus a
  `textarea#g-recaptcha-response-100000`) on New-Item and on the listing form. It didn't challenge
  this session, but it scores sessions, so later runs could be challenged (see run 3, which stalled on
  the login page with no message).

## URLs

| Step | URL |
| --- | --- |
| Add resource (product-type picker) | `https://www.teacherspayteachers.com/My-Products/New-Item` |
| After choosing Digital Download | `https://www.teacherspayteachers.com/My-Products/New/Digital-Next` |

- Choosing Digital Download did **not** open a file picker: `file_chooser_opened` is `null` in
  FORM-FIELDS.json. It's an ordinary link (`a[data-testid="select-product-type-digital-download"]`,
  `href="/My-Products/New/Digital-Next"`); `discover` could navigate to that URL directly.

## Step / page order

1. `/Login`
2. `/My-Products/New-Item`: "Select a Product Type". Options and their selectors (only Digital Download opened):
   - Digital Download: `[data-testid="select-product-type-digital-download"]`, `/My-Products/New/Digital-Next`
   - Video: `[data-testid="select-product-type-video"]`, `/My-Products/New/Video-Next`
   - Google Drive: in `#type-online-resource`, `/My-Products/New/Online-Resource`
   - Easel: `[data-testid="select-product-type-easel"]`, `/My-Products/New/Easel`
   - Bundle of Resources: `[data-testid="select-product-type-bundle"]` (no href; handled in JS)
3. `/My-Products/New/Digital-Next`: **one long page**, `form#ItemAddForm`
   (`action="/My-Products/New/Digital-Next"`, `method="post"`, `enctype="multipart/form-data"`). Sections in
   order: Name, Files, Product Previews, Thumbnails, Description, Price, Tax Code, Categories, Education
   Standards, Details, Copyright, Product Status, then **Submit** / Cancel. Not opened.
4. After Submit (not seen): the page says "Please allow up to one hour for new or edited products to appear
   in your store listings."

## Listing-form fields (`/My-Products/New/Digital-Next`)

"Req" = the page shows "Required". Ids containing dots need attribute selectors, e.g. `[id="data.Grade.Grade-checkbox_1st-grade"]`.

| Section | Label | Control | Selector | Req |
| --- | --- | --- | --- | --- |
| Name | Title | text input | `#ItemName` / `[data-testid="upload-form-item-name"]` (`name="data[Item][name]"`) | yes |
| Files | Downloadable File | file input | `input[type="file"]#ItemDigitalProduct` | yes |
| Previews | Preview | file input | `input[type="file"]#ItemDigitalPreview` | no |
| Previews | Video Preview | file input | `input[type="file"]#UploadVideopreview` | no |
| Thumbnails | Auto generate thumbnails from the product file (**default**) | radio | `#ItemGenerateThumbnail1` (`name="data[Item][generate_thumbnail]"`) | one of three |
| Thumbnails | Upload thumbnails now | radio | `#ItemGenerateThumbnail2` (value `2`) | |
| Thumbnails | Upload thumbnails later | radio | `#ItemGenerateThumbnail3` | |
| Thumbnails | Main Cover | file input | `input[type="file"]#ItemDigitalThumb1` (shown only with "Upload thumbnails now") | with option 2 |
| Thumbnails | Thumbnail (Optional) ×3 | file inputs | `input[type="file"]#ItemDigitalThumb2` … `#ItemDigitalThumb4` | no |
| Description | Description | rich-text editor (Lexical, `contenteditable`) | `[data-testid="description-editor-frame"] [contenteditable="true"]` (`aria-label="Description"`) | yes |
| Price | Free Resource | checkbox (Radix button) | `#item-free` (hidden input `name="data[Item][free]"`) | no |
| Price | Price | text input | `#item-price` / `[data-testid="upload-form-item-price"]` (`name="data[Item][price]"`) | yes |
| Price | Multiple Licenses | text input | `#item-license-price` / `[data-testid="upload-form-item-license-price"]` (`name="data[Item][license_price]"`) | yes |
| Price | Bundle Discount Price | text input | `#item-bundle-price` / `[data-testid="upload-form-item-discount-price"]` (`name="data[Item][discountprice]"`) | no |
| Tax Code | Tax Code | listbox combobox | `#taxCode-toggle-button` (`name="data.ItemTaxCode.tax_code_id"`, menu `#taxCode-menu`) | yes |
| Categories | Grade Level (up to four; or "Not Grade Specific") | 17 checkboxes (Radix buttons) | `[id="data.Grade.Grade-checkbox_<slug>"]`, slugs: `preschool`, `kindergarten`, `1st-grade` … `12th-grade`, `higher-education`, `adult-education`, `not-grade-specific` | yes |
| Categories | Subject Area (up to three) | react-select autocomplete | `#subject-areas` | yes |
| Categories | Tag (Theme, Audience, Language; up to six) | react-select autocomplete | `#tags` | yes |
| Categories | Format (up to three) | react-select autocomplete | `#formats` | no |
| Categories | Custom Category | react-select autocomplete | `#custom-categories` | no |
| Standards | CCSS / NGSS / TEKS / VA SOL | buttons that open pickers | text "Select CCSS", "Select NGSS", "Select TEKS", "Select VA SOL" (sections `[data-testid^="standards-section-"]`) | no |
| Details | Teaching Duration (default "N/A") | listbox combobox | `#teachingDuration-toggle-button` (`name="data.ItemsProperty.duration"`) | no |
| Details | Number of Pages or Slides | text input | `#numberOfPagesOrSlides` / `[data-testid="upload-form-item-pages"]` (`name="data[ItemsProperty][pages]"`) | no |
| Details | Answer Key (default "N/A") | listbox combobox | `#answerKey-toggle-button` (`name="data.ItemsProperty.answer_key"`) | no |
| Copyright | "original work" attestation (**preselected**) | radio (Radix button) | `[id="data.ItemsProperty.copyright_declaration-0"]` (value `1`) | one of two |
| Copyright | "used copyrighted and/or trademarked materials" attestation | radio (Radix button) | `[id="data.ItemsProperty.copyright_declaration-1"]` | |
| Product Status | Make Listing Active (**checked by default**) | checkbox (Radix button) | `#makeProductActive` (hidden input `name="data[Item][status_user]"`) | no |
| Actions | Submit | submit button | `button[type="submit"][form="ItemAddForm"]` | n/a |
| Actions | Cancel | button | text "Cancel" | n/a |

## File uploads

From the page text and the upload config embedded in the HTML:

| Upload | Selector | Max size | Accepted types |
| --- | --- | --- | --- |
| Downloadable File (required) | `input[type="file"]#ItemDigitalProduct` | 4 GB | avi, bmp, bnk, doc, docx, dot, epub, flp, flipchart, flv, gif, htm, html, ink, jpeg, jpg, key, knt, mov, m4a, m4v, mp3, mp4, png, mpeg, mpg, mv4, notebook, ods, **pdf**, pps, ppsx, ppt, pptx, pub, ram, rm, rtf, swf, tif, tiff, txt, wav, wpd, wmv, xls, xlsx, xlt, xltx, **zip** |
| Preview | `input[type="file"]#ItemDigitalPreview` | 30 MB | same list as the downloadable file |
| Video Preview | `input[type="file"]#UploadVideopreview` | 1 GB | avi, mov, m4a, m4v, mp4, mv4, mpeg, mpg, mkv, wmv |
| Main Cover + 3 thumbnails | `input[type="file"]#ItemDigitalThumb1` … `#ItemDigitalThumb4` | 4 MB each | bmp, gif, jpg, jpeg, png, tif, tiff |

- Each upload sends the file straight away (progress bar), then fills a hidden field:
  `data[ItemDigital][product|preview|thumb1..4]` (class `upload-key`). A matching
  `data[ItemsProperty][*_uploaded]` flag flips from `0`. Automation should wait for the flag before
  moving on.
- A "Supported File Types" button opens a dialog; the list above is the same information.

## What makes automation fragile

- **"Make Listing Active" is on by default.** Submit publishes immediately unless it's unticked.
  To save a draft, untick `#makeProductActive` first (the page itself suggests this).
- **Duplicate ids.** Each file input shares its id with a hidden input (e.g. two `#ItemDigitalProduct`),
  so always qualify the selector with `input[type="file"]`.
- **Custom widgets, not native inputs.** Grades, Free, Copyright and Make Listing Active are Radix
  buttons (`role="checkbox"`/`role="radio"`, `aria-checked`) with hidden inputs, so click the button,
  not the input. Tax Code, Teaching Duration and Answer Key are listbox comboboxes. Subject Area, Tags,
  Format and Custom Category are react-select comboboxes: type, then pick an option from the menu.
  The Description is a Lexical editor, so type into the `contenteditable`; `fill()` on a hidden field
  won't work.
- **Generated class names** (`Button-module__…--RJx94`, `Select-module__…`) change between TpT
  releases; use the ids, `name`s and `data-testid`s above instead.
- **Hidden-until-chosen sections.** Thumbnail inputs show only after "Upload thumbnails now";
  standards pickers and "Supported File Types" open dialogs with "Done" buttons.
- **iframes:** reCAPTCHA Enterprise (scoring) and a Pinterest tracking iframe. The form itself isn't
  in an iframe.
- **Server form token.** The form has a hidden `data[_Token][unlocked]` (CakePHP security token), so the
  form has to be driven in the page; posting fields directly would be rejected.
- **Bundle has no URL.** Its picker option has no href, so bundles have to be started by clicking.
- **Not checked:** whether choosing a product type creates a draft. My Products was snapshotted
  *before* Digital Download was chosen. Check My Products after the next run.

## Files

- `tpt/FORM-FIELDS.json`: committed. Checked: contains no email, username, password, name or
  earnings; URLs are TpT pages only.
- `tpt/_discover/`: screenshots and HTML from this run (`01`–`04`), gitignored, kept on the Mac.
  The dashboard screenshots contain the store name and earnings; they aren't described here.
  `03-add-resource-form.*` is left over from the 14:06 run.
