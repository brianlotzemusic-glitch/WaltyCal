#!/bin/bash
# Nightly TpT publish on the owner's Mac, run by launchd (installed by tools/tpt-install-nightly.sh).
# 1. pull shop-factory  2. publish items the cloud Manager released (tools/tpt.js publish-pending)
# 3. commit + push the `uploaded`/`reuploaded`/`reupload-failed` markers and tpt/UPLOADER-STATUS.json so the Manager sees the result.
# Log: ~/Library/Logs/tpt-nightly.log
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
cd "$REPO" || exit 1
echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) tpt-nightly in $REPO"

git checkout -q shop-factory || { echo "not on shop-factory and can't switch; stopping"; exit 1; }
git pull -q --no-rebase origin shop-factory || { echo "git pull failed; stopping"; exit 1; }

[ -f "$HOME/.tpt-env" ] && source "$HOME/.tpt-env"
node tools/tpt.js publish-pending
rc=$?

# 2b. Owner exception 22 Oct 2026: replace ONLY the files of live products the Manager marked with a
# `reupload` file after QA approved the rebuild. First run records tpt/EDIT-FIELDS.json instead.
node tools/tpt.js reupload-pending
rc2=$?
[ "$rc" -eq 0 ] && rc=$rc2

git add tpt/UPLOADER-STATUS.json tpt/EDIT-FIELDS.json tpt/*/uploaded tpt/*/reuploaded tpt/*/reupload-failed 2>/dev/null
if ! git diff --cached --quiet; then
  git commit -q -m "TpT nightly publish ($(hostname -s)): $(date +%Y-%m-%d)"
  git push -q origin shop-factory || { git pull -q --no-rebase origin shop-factory && git push -q origin shop-factory; }
fi
echo "=== done (publish-pending/reupload-pending exit $rc)"
exit $rc
