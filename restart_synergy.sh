#!/bin/bash

# quick and dirty script to restart synergy on my OS's.

set -euo pipefail

if [[ "$(uname -s)" == "Darwin" ]] ; then 
	launchctl unload /Library/LaunchAgents/com.symless.synergy.synergy-service.plist
	sudo killall synergy-core &
	launchctl load /Library/LaunchAgents/com.symless.synergy.synergy-service.plist
	open -n /Applications/Synergy.app
elif
	[[ "$(uname -s)" == "Linux" ]] ; then
	sudo systemctl restart synergy
fi

