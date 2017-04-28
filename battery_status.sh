#!/bin/bash

# A script to trigger a music file if battery level falls below 20%.
# Mac OS X only

# Bash "strict" mode
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]] ; then
    echo "This will only run on Mac OS X."
    exit 1
fi

battery_level="$(pmset -g batt | egrep "([0-9]+\%).*" -o --colour=auto | cut -f1 -d';' | sed -e 's/%//')"

music_file=/path/to/file

if [[ "$battery_level" -lt 20 ]] ; then
	if [[ -e /usr/local/bin/noti ]] ; then
		noti -t "WARNING" -m "Battery level at $battery_level%"
		afplay -t 30 "$music_file"
	else
		afplay -t 30 "$music_file"
	fi
fi
