# TpT music line

One folder per item (`tpt/NNN-slug/`). See FACTORY.md "Teachers Pay Teachers". The owner uploads by hand using each item's UPLOAD.md.

## Publishing with `tools/tpt.js publish` (owner's Mac only)

First run `node tools/tpt.js login` (after `source ~/.tpt-env`): it fills in the VA email and password,
you click **Log in** yourself and finish any check TpT shows, and the session is saved in `~/.tpt-profile`
for later runs. Run it again whenever a command says the session expired.

`node tools/tpt.js publish tpt/NNN-slug` fills TpT's Digital Download form and submits it **live**
(owner, 4 Oct 2026). Add `--dry-run` to fill the form and stop before Submit; it lists every value
TpT doesn't accept, with the options TpT offers. Selectors live in `tpt/FORM.json`.

It refuses an item unless `QA.md` has a `**Verdict: APPROVED**` line and there is no `uploaded`
file, and it writes `uploaded` (date + TpT URL) after a successful submit. Title and description
come from the code blocks under `## 1.` and `## 2.` in `UPLOAD.md`. Everything else comes from
`tpt.json` in the item folder:

| Key | Required | Example / notes |
| --- | --- | --- |
| `price`, `license_price` | yes | `"3.50"` (multiple-license price is required by TpT) |
| `tax_code` | yes | exact option text from TpT's Tax Code list (a dry run lists them) |
| `grades` | yes, 1-4 | slugs: `preschool`, `kindergarten`, `1st-grade` … `12th-grade`, `higher-education`, `adult-education`, `not-grade-specific` |
| `subjects` | yes, 1-3 | exact Subject Area option text, e.g. `"Music"` |
| `tags` | yes, 1-6 | exact Tag option text (theme, audience, language) |
| `formats`, `custom_categories` | no | exact option text; up to 3 formats |
| `pages`, `answer_key`, `teaching_duration` | no | `58`, `"Included"` (option text) |
| `files` | `product` required | slots `product`, `preview`, `thumb1` (main cover) … `thumb4`; paths relative to the item folder |
