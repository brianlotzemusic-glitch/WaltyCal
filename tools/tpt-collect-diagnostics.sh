#!/bin/bash
# Run on the Mac from the runner clone (~/tpt-nightly/waltycal): bash tools/tpt-collect-diagnostics.sh
# Commits ONLY the failure screenshots (see tpt-add-shots.sh), tpt/EDIT-FIELDS.json, tpt/UPLOADER-STATUS.json and tpt/*/uploaded,
# then pulls (merge) and pushes shop-factory, printing all git output.
set -u
URL=https://github.com/brianlotzemusic-glitch/WaltyCal.git
cd "$(dirname "$0")/.." || exit 1
echo "== repo: $(pwd)"; echo "== branch: $(git branch --show-current)"
echo "== origin: $(git remote get-url origin)"
case "$(git remote get-url origin)" in
  *waltycal*) echo "== origin is the old lowercase URL; switching to $URL"; git remote set-url origin "$URL";; esac
git checkout shop-factory || { echo "!! cannot switch to shop-factory"; exit 1; }
for f in tpt/EDIT-FIELDS.json tpt/UPLOADER-STATUS.json tpt/*/uploaded; do
  [ -e "$f" ] && { git add -- "$f" || echo "git add $f FAILED (exit $?)"; }
done
. "$(dirname "$0")/tpt-add-shots.sh"; tpt_add_shots   # git add -f of the small failure-screenshot list only
echo "== staged:"; git diff --cached --stat
if ! git diff --cached --quiet; then
  git commit -m "TpT diagnostics from $(hostname -s): $(date +%Y-%m-%d)"; echo "== commit exit $?"
else echo "== nothing new to commit"; fi
git pull --no-rebase origin shop-factory; echo "== pull exit $?"
git push origin shop-factory; rc=$?; echo "== push exit $rc"
git status -sb | head -5
[ "$rc" -eq 0 ] && echo "== OK: pushed" || echo "!! PUSH FAILED (exit $rc)"
exit $rc
