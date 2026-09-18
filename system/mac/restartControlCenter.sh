#!/usr/bin/env bash
set -euo pipefail

# --- Gates ---
[ "$(uname)" = "Darwin" ] || { echo "::: macOS only"; exit 1; }
[ "$EUID" -eq 0 ]         || { echo "::: Run as root"; exit 1; }

CONSOLE_USER="$(stat -f '%Su' /dev/console)"
[ "$CONSOLE_USER" != "root" ] || { echo "::: No GUI user logged in"; exit 1; }

# --- Args ---
DRY_RUN=0
case "${1:-}" in
  "")              ;;
  -n|--dry-run)    DRY_RUN=1 ;;
  *)               echo "usage: sudo $0 [-n|--dry-run]"; exit 2 ;;
esac

# --- Helpers ---
restart_agent() {
  local name="$1"
  local pids

  pids="$(pgrep -u "$CONSOLE_USER" -x "$name")" || {
    echo "::: $name: not running for $CONSOLE_USER"
    return 0
  }

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "::: $name: running (pids: $pids) — would restart"
    return 0
  fi

  killall -u "$CONSOLE_USER" "$name"
  sleep 1
  if pgrep -q -u "$CONSOLE_USER" -x "$name"; then
    echo "::: $name: restarted"
  else
    echo "::: $name: signaled, not yet respawned"
  fi
}

restart_agent ControlCenter
restart_agent NotificationCenter
