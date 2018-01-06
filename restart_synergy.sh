#!/bin/bash

# quick and dirty script to restart synergy on my OS's.

set -euo pipefail
IFS=$'\n\t'

if [[ "$(id -u)" -ne 0 ]] ; then
	echo "::: Please run as root."
	exit
fi

if [[ "$(uname -s)" == "Darwin" ]] ; then 
	launchctl unload /Library/LaunchAgents/com.symless.synergy.synergy-service.plist
	killall synergy-core &
	sleep 0.5
	launchctl load /Library/LaunchAgents/com.symless.synergy.synergy-service.plist
	open -n /Applications/Synergy.app
elif
	[[ "$(uname -s)" == "Linux" ]] ; then
	systemctl restart synergy
fi

