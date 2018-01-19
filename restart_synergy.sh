#!/bin/bash

# quick and dirty script to restart synergy on my OS's.

set -euo pipefail
IFS=$'\n\t'

if [[ "$(id -u)" -ne 0 ]] ; then
	echo "::: Please run as root."
	exit
fi

if [[ "$(uname -s)" == "Darwin" ]] ; then
	read -rp "::: Restart (1) or Kill (2)? -->  " restart_choice
	case "$restart_choice" in
		1)
			launchctl unload /Library/LaunchAgents/com.symless.synergy.synergy-service.plist
			killall synergy-core &
			sleep 0.5
			launchctl load /Library/LaunchAgents/com.symless.synergy.synergy-service.plist
			open -n /Applications/Synergy.app
			;;
		2)
			killall synergy-core
			;;
	esac
elif
	[[ "$(uname -s)" == "Linux" ]] ; then
	systemctl restart synergy
fi

