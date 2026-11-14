#!/bin/bash
# TpT publish job on the owner's Mac, run by launchd (installed by tools/tpt-install-nightly.sh).
# 1. pull shop-factory  2. publish items the cloud released (tools/tpt.js publish-pending)
# 3. commit + push the `uploaded`/`publish-failed`/`reuploaded`/`reupload-failed` markers and
#    tpt/UPLOADER-STATUS.json so the cloud sees the result.
# Log: ~/Library/Logs/tpt-nightly.log
#
# Owner, 12 Nov 2026 ("keep the Mac, make it forgiving"): the job no longer depends on the Mac being
# awake at 8:30pm. It waits for the network after a wake, runs one at a time, and installs a second
# launchd job (com.hudsonbeat.tpt-catchup) that runs it at login and at several times of day. A run
# with nothing to publish opens no browser and takes a few seconds.
# Written for the bash 3.2 that ships with macOS.
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
cd "$REPO" || exit 1
echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) tpt-nightly in $REPO (${1:-nightly})"

# One run at a time (the two launchd jobs can fire together). A lock older than 90 minutes is a crash.
LOCK="$HOME/.tpt-nightly.lock"
if [ -z "${TPT_REEXEC:-}" ]; then
  if [ -d "$LOCK" ] && [ -n "$(find "$LOCK" -maxdepth 0 -mmin +90 2>/dev/null)" ]; then echo "removing a stale lock"; rmdir "$LOCK" 2>/dev/null; fi
  mkdir "$LOCK" 2>/dev/null || { echo "another run is in progress; nothing to do"; exit 0; }
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

git checkout -q shop-factory || { echo "not on shop-factory and can't switch; stopping"; exit 1; }
# Right after a wake the network is often not up yet: try for about 5 minutes before giving up.
OLD_HEAD="$(git rev-parse HEAD 2>/dev/null)"
pulled=0
for try in 1 2 3 4 5 6 7 8 9 10; do
  if git pull -q --no-rebase origin shop-factory; then pulled=1; break; fi
  echo "git pull failed (try $try of 10; the network may not be up yet); waiting 30 s"
  sleep 30
done
[ "$pulled" -eq 1 ] || { echo "git pull failed 10 times; stopping"; exit 1; }
# If the pull changed this script, run the new version now instead of next time.
if [ -z "${TPT_REEXEC:-}" ] && [ -n "$OLD_HEAD" ] && ! git diff --quiet "$OLD_HEAD" HEAD -- tools/tpt-nightly.sh; then
  echo "this script was updated; restarting with the new version"
  TPT_REEXEC=1 exec /bin/bash "$0" ${1+"$@"}
fi

# Tell the owner on the Mac itself when something needs them, at most once a day per problem. The cloud
# can't see this Mac, and a lost GitHub login went unnoticed for a week (7-14 Nov 2026).
notify() {  # $1 = key, $2 = message
  [ "$(uname)" = "Darwin" ] || return 0
  local stamp="$HOME/.tpt-notified-$1"
  [ -n "$(find "$stamp" -mmin -1440 2>/dev/null)" ] && return 0
  touch "$stamp"
  osascript -e "display notification \"$2\" with title \"TpT uploader\"" >/dev/null 2>&1 || true
}

# The catch-up schedule: a second launchd job that runs this same script at login and through the day.
# Added once; the 8:30pm job stays as it is. To remove it:
#   launchctl bootout gui/$(id -u)/com.hudsonbeat.tpt-catchup; rm ~/Library/LaunchAgents/com.hudsonbeat.tpt-catchup.plist
install_catchup() {
  [ "$(uname)" = "Darwin" ] || return 0
  local label="com.hudsonbeat.tpt-catchup"
  local plist="$HOME/Library/LaunchAgents/$label.plist"
  [ -f "$plist" ] && return 0
  mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
  cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$REPO/tools/tpt-nightly.sh</string><string>catchup</string></array>
  <key>RunAtLoad</key><true/>
  <key>StartCalendarInterval</key><array>
    <dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>15</integer></dict>
    <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>45</integer></dict>
    <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>15</integer></dict>
    <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>15</integer></dict>
    <dict><key>Hour</key><integer>17</integer><key>Minute</key><integer>45</integer></dict>
    <dict><key>Hour</key><integer>22</integer><key>Minute</key><integer>15</integer></dict>
  </array>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/tpt-nightly.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/tpt-nightly.log</string>
</dict></plist>
EOF
  if launchctl bootstrap "gui/$(id -u)" "$plist"; then
    echo "installed the catch-up schedule ($label): at login and at 7:15, 9:45, 12:15, 15:15, 17:45 and 22:15"
  else
    echo "wrote $plist but could not load it now; macOS loads it at the next login"
  fi
}
install_catchup

[ -f "$HOME/.tpt-env" ] && source "$HOME/.tpt-env"
# Keep the Mac awake while a publish is running (it may still sleep when the lid is closed on battery).
AWAKE=""; command -v caffeinate >/dev/null 2>&1 && AWAKE="caffeinate -i"
$AWAKE node tools/tpt.js publish-pending
rc=$?

# 2b. Owner exception 22 Oct 2026: replace ONLY the files of live products the cloud marked with a
# `reupload` file after QA approved the rebuild. First run records tpt/EDIT-FIELDS.json instead.
$AWAKE node tools/tpt.js reupload-pending
rc2=$?
[ "$rc" -eq 0 ] && rc=$rc2

# One path at a time: a single `git add` with a pathspec that matches nothing (e.g. no reupload-failed
# markers) aborts the WHOLE add and stages nothing.
for f in tpt/UPLOADER-STATUS.json tpt/EDIT-FIELDS.json tpt/*/uploaded tpt/*/publish-failed tpt/*/reuploaded tpt/*/reupload-failed; do
  [ -e "$f" ] && { git add -- "$f" || echo "git add $f FAILED (exit $?)"; }
done
# A `publish-failed` marker removed after a later success must leave git too.
git ls-files 'tpt/*/publish-failed' | while IFS= read -r f; do [ -e "$f" ] || git rm -q --cached -- "$f"; done
# Failure screenshots live in the gitignored tpt/_publish/: force-add the small list so the cloud can see them.
. "$(dirname "$0")/tpt-add-shots.sh"; tpt_add_shots

# The job now runs several times a day. When the only change is the run time in the status file, push
# that heartbeat at most once in 20 hours, so the branch isn't filled with empty commits.
if [ "$(git diff --cached --name-only)" = "tpt/UPLOADER-STATUS.json" ]; then
  changed="$(git diff --cached --numstat | awk '{print $1 " " $2}')"
  last="$(git log -1 --format=%ct -- tpt/UPLOADER-STATUS.json 2>/dev/null)"
  if { [ "$changed" = "1 1" ] || [ "$changed" = "2 2" ]; } && [ -n "$last" ] && [ $(( $(date +%s) - last )) -lt 72000 ]; then
    echo "nothing new to report (the last heartbeat is under 20 hours old)"
    git reset -q
    git checkout -q -- tpt/UPLOADER-STATUS.json
  fi
fi

if ! git diff --cached --quiet; then
  CANON=https://github.com/brianlotzemusic-glitch/WaltyCal.git
  case "$(git remote get-url origin)" in *waltycal*) echo "origin was the old lowercase URL; switching to $CANON"; git remote set-url origin "$CANON";; esac
  echo "--- git state before commit: branch $(git branch --show-current), origin $(git remote get-url origin)"
  git status -sb
  git commit -q -m "TpT publish ($(hostname -s)): $(date +%Y-%m-%d)"; echo "--- git commit exit $?"
  git push origin shop-factory; prc=$?; echo "--- git push exit $prc"
  if [ "$prc" -ne 0 ]; then
    git pull --no-rebase origin shop-factory; echo "--- git pull exit $?"
    git push origin shop-factory; prc=$?; echo "--- git push (retry) exit $prc"
  fi
  if [ "$prc" -ne 0 ]; then
    echo "!!!!!! PUSH FAILED (exit $prc): markers are committed locally but NOT on GitHub. Run: bash tools/tpt-collect-diagnostics.sh"
    notify push "Can't save upload results to GitHub (login missing). In Terminal run: gh auth login"
    [ "$rc" -eq 0 ] && rc=$prc
  fi
  git status -sb | head -3
fi
grep -q '"needs_login": true' tpt/UPLOADER-STATUS.json 2>/dev/null && notify login "TpT login expired. In Terminal run: source ~/.tpt-env && node tools/tpt.js login, then click Log in"
echo "=== done (publish-pending/reupload-pending exit $rc)"
exit $rc
