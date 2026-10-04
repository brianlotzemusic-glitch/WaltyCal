# TpT uploader on your Mac: one-time setup (about 15 minutes)

The factory builds and QA-checks the Hudson Beat items in the cloud. Uploads to Teachers Pay Teachers run on your Mac, because the cloud's network proxy stops the automated browser from opening TpT.

## 1. Install Node.js
- Go to https://nodejs.org, download the **LTS** installer for macOS, and run it.
- Check it worked: open **Terminal** (Spotlight → "Terminal") and type `node -v`. It should print a version number such as `v22.x`.

## 2. Get the repo onto your Mac with GitHub Desktop
- Install GitHub Desktop from https://desktop.github.com and sign in with your GitHub account.
- **File → Clone repository** → choose `brianlotzemusic-glitch/waltycal` → Clone. The default location is `~/Documents/GitHub/waltycal`.
- At the top, click **Current branch** and choose **shop-factory**.

## 3. Install the browser automation (once)
In Terminal:
```
cd ~/Documents/GitHub/waltycal
npm install playwright
npx playwright install chromium
```
If you cloned somewhere else, use that folder instead.

## 4. Store the TpT VA login on your Mac only
This puts the login in a private file in your home folder. It is NOT in the repo.
```
nano ~/.tpt-env
```
Type these two lines, using your VA account's details:
```
export TPT_VA_EMAIL="the-va-email@example.com"
export TPT_VA_PASSWORD="the-va-password"
```
Save with **Ctrl+O**, then Enter, then **Ctrl+X**. Then make the file private:
```
chmod 600 ~/.tpt-env
```

## 5. First run: discover (nothing is uploaded)
```
cd ~/Documents/GitHub/waltycal
source ~/.tpt-env
node tools/tpt.js discover
```
- A browser window opens and logs in as the VA. If TpT shows a CAPTCHA or asks for a code, complete it in that window; the script waits up to 3 minutes.
- It opens the "Add a resource" form, saves screenshots, and closes. **Nothing is created on TpT.**
- It writes two things:
  - `tpt/_discover/`: screenshots. These stay on your Mac and aren't committed.
  - `tpt/FORM-FIELDS.json`: only the form's field names and labels, no account details.

## 6. Send the field list back
In GitHub Desktop you'll see `tpt/FORM-FIELDS.json` as a change.
- Write a summary such as "TpT form fields", click **Commit to shop-factory**, then **Push origin**.
- Tell the factory "discover done". It maps the form and enables `publish`.

## After that (each batch, about 1 minute of your time)
When the factory tells you items are ready:
1. In GitHub Desktop, click **Fetch origin**, then **Pull**.
2. In Terminal:
   ```
   cd ~/Documents/GitHub/waltycal && source ~/.tpt-env && node tools/tpt.js publish tpt/NNN-slug
   ```
   The factory will give you the exact command. A single command for all waiting items comes later.
3. In GitHub Desktop, commit and push the `uploaded` marker the script writes, so the factory knows.
