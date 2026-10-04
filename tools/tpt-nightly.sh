#!/bin/bash
# Nightly TpT publish on the owner's Mac, run by launchd (installed by tools/tpt-install-nightly.sh).
# 1. pull shop-factory  2. publish items the cloud Manager released (tools/tpt.js publish-pending)
# 3. commit + push the `uploaded` markers and tpt/UPLOADER-STATUS.json so the Manager sees the result.
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

git add tpt/UPLOADER-STATUS.json tpt/*/uploaded 2>/dev/null
if ! git diff --cached --quiet; then
  git commit -q -m "TpT nightly publish ($(hostname -s)): $(date +%Y-%m-%d)"
  git push -q origin shop-factory || { git pull -q --no-rebase origin shop-factory && git push -q origin shop-factory; }
fi
echo "=== done (publish-pending exit $rc)"
exit $rc
