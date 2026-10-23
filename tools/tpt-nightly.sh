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

# One path at a time: a single `git add` with a pathspec that matches nothing (e.g. no reupload-failed
# markers) aborts the WHOLE add and stages nothing. Same files as before.
for f in tpt/UPLOADER-STATUS.json tpt/EDIT-FIELDS.json tpt/*/uploaded tpt/*/reuploaded tpt/*/reupload-failed; do
  [ -e "$f" ] && { git add -- "$f" || echo "git add $f FAILED (exit $?)"; }
done
# Failure screenshots live in the gitignored tpt/_publish/: force-add the small list so the cloud Manager can see them.
. "$(dirname "$0")/tpt-add-shots.sh"; tpt_add_shots
if ! git diff --cached --quiet; then
  CANON=https://github.com/brianlotzemusic-glitch/WaltyCal.git
  case "$(git remote get-url origin)" in *waltycal*) echo "origin was the old lowercase URL; switching to $CANON"; git remote set-url origin "$CANON";; esac
  echo "--- git state before commit: branch $(git branch --show-current), origin $(git remote get-url origin)"
  git status -sb
  git commit -q -m "TpT nightly publish ($(hostname -s)): $(date +%Y-%m-%d)"; echo "--- git commit exit $?"
  git push origin shop-factory; prc=$?; echo "--- git push exit $prc"
  if [ "$prc" -ne 0 ]; then
    git pull --no-rebase origin shop-factory; echo "--- git pull exit $?"
    git push origin shop-factory; prc=$?; echo "--- git push (retry) exit $prc"
  fi
  if [ "$prc" -ne 0 ]; then echo "!!!!!! PUSH FAILED (exit $prc): markers are committed locally but NOT on GitHub. Run: bash tools/tpt-collect-diagnostics.sh"; [ "$rc" -eq 0 ] && rc=$prc; fi
  git status -sb | head -3
fi
echo "=== done (publish-pending/reupload-pending exit $rc)"
exit $rc
