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
if [ "${1:-}" = "remove" ]; then rm -f "$PLIST"; echo "Removed the nightly TpT job."; exit 0; fi
HOUR="${1:-20}"; MIN="${2:-30}"
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
