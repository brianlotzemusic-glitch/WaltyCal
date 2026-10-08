#!/bin/bash
# Installs (or reinstalls) the nightly TpT publish job on the owner's Mac.
#   bash tools/tpt-install-nightly.sh          run at 8:30pm every day
#   bash tools/tpt-install-nightly.sh 21 15    run at 9:15pm instead
#   bash tools/tpt-install-nightly.sh remove   uninstall
set -eu
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.hudsonbeat.tpt-nightly"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
if [ "${1:-}" = "remove" ]; then rm -f "$PLIST"; echo "Removed the nightly TpT job. (Its clone in ~/tpt-nightly, if any, can be deleted.)"; exit 0; fi
HOUR="${1:-20}"; MIN="${2:-30}"
# macOS privacy protection stops launchd jobs reading ~/Documents, ~/Desktop, ~/Downloads and iCloud
# Drive ("Operation not permitted", exit 126). If this repo lives there, the job runs from its own
# clone in ~/tpt-nightly/waltycal instead; both clones stay in sync through GitHub.
case "$REPO/" in
  "$HOME/Documents/"*|"$HOME/Desktop/"*|"$HOME/Downloads/"*|"$HOME/Library/Mobile Documents/"*)
    RUNNER="${TPT_RUNNER_DIR:-$HOME/tpt-nightly/waltycal}"
    if [ ! -d "$RUNNER/.git" ]; then
      mkdir -p "$(dirname "$RUNNER")"
      git clone -q --branch shop-factory "$(git -C "$REPO" remote get-url origin)" "$RUNNER"
    fi
    git -C "$RUNNER" checkout -q shop-factory
    git -C "$RUNNER" pull -q --no-rebase origin shop-factory
    if [ ! -d "$RUNNER/node_modules/playwright" ]; then (cd "$RUNNER" && npm install --silent --no-audit --no-fund playwright); fi
    # Each Playwright version needs its own Chromium build; fetch it if missing (quick when present).
    (cd "$RUNNER" && npx --no-install playwright install chromium)
    echo "This repo is in a folder macOS hides from background jobs, so the job runs from $RUNNER."
    REPO="$RUNNER";;
esac
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
chmod +x "$REPO/tools/tpt-nightly.sh"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$REPO/tools/tpt-nightly.sh</string></array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>$HOUR</integer><key>Minute</key><integer>$MIN</integer></dict>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/tpt-nightly.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/tpt-nightly.log</string>
</dict></plist>
EOF
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installed: the TpT job runs every day at $(printf %02d:%02d "$HOUR" "$MIN") while you're logged in to the Mac."
echo "Log: ~/Library/Logs/tpt-nightly.log   Run it now: launchctl kickstart gui/$(id -u)/$LABEL"
