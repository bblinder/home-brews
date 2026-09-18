#!/usr/bin/env bash

set -Eeuo pipefail

DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    -n|--dry-run) DRY_RUN=1 ;;
    -h|--help) echo "usage: sudo $0 [-n|--dry-run]"; exit 0 ;;
    *) echo "::: Unknown argument: $arg"; exit 2 ;;
  esac
done

if [ "$(uname)" != "Darwin" ]; then
  echo "::: This script will run on MacOS only"
  exit 1
fi

if [ "$EUID" -ne 0 ]; then
  echo "::: Please run as root"
  exit 1
fi

CONSOLE_USER="$(stat -f '%Su' /dev/console)"
if [ "$CONSOLE_USER" = "root" ]; then
  echo "::: No GUI user logged in; nothing to restart."
  exit 1
fi

probe_agent() {
  # $1 = process name
  local pids
  if ! pids="$(pgrep -u "$CONSOLE_USER" -x "$1")"; then
    echo "::: DRY-RUN: $1 not running for $CONSOLE_USER — live run would report 'not running'."
    return 0
  fi
  local pid ok=1
  for pid in $pids; do
    # kill -0: full existence + permission check, no signal delivered
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "::: DRY-RUN: $1 (pid $pid) exists but cannot be signaled."
      ok=0
    fi
  done
  if [ "$ok" -eq 1 ]; then
    echo "::: DRY-RUN: $1 is running (pids: $(echo $pids | tr '\n' ' ')) and signalable. Live run would succeed."
  fi
}

restart_agent() {
  # $1 = process name, $2 = display name
  if [ "$DRY_RUN" -eq 1 ]; then
    probe_agent "$1"
    return 0
  fi
  if killall -u "$CONSOLE_USER" "$1" 2>/dev/null; then
    sleep 1
    if pgrep -u "$CONSOLE_USER" -x "$1" > /dev/null; then
      echo "::: $2 restarted (relaunched by launchd)."
    else
      echo "::: $2 signaled, but launchd has not relaunched it."
    fi
  else
    echo "::: $2 was not running for $CONSOLE_USER (or signal failed)."
  fi
}

[ "$DRY_RUN" -eq 1 ] && echo "::: Dry-run mode: no signals will be sent."

restart_agent "ControlCenter" "ControlCenter"
restart_agent "NotificationCenter" "NotificationCenter"
