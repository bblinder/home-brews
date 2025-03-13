#!/usr/bin/env bash

# Toggles "airplane mode" on my laptop.
# Enables/disables Wi-Fi and Bluetooth.
# Assumes you have "blueutil" installed.
# Works on MacOS only.

# usage: ./airplane-mode.sh [on|off]

set -Eeuo pipefail
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

# check if MacOS
if [[ "$(uname)" != "Darwin" ]]; then
  echo "::: This script will run on MacOS only"
  exit 1
fi

# checking that blueutil is installed
if ! command -v blueutil &> /dev/null; then
    echo "Error: blueutil is not installed"
    exit 1
fi

toggle_bluetooth(){
    blueutil -p "$1"
}

toggle_wifi(){
    networksetup -setairportpower en0 "$1"
}

usage() {
    echo "Usage: $0 [on|off]"
    echo "  off  Disable airplane mode (turn on WiFi and Bluetooth)"
    echo "  on   Enable airplane mode (turn off WiFi and Bluetooth)"
    exit 1
}

case "${1:-}" in
    off)
        toggle_bluetooth 1
        toggle_wifi on
        echo "Airplane mode disabled"
        ;;
    on)
        toggle_bluetooth 0
        toggle_wifi off
        echo "Airplane mode enabled"
        ;;
    *)
        usage
        ;;
esac
