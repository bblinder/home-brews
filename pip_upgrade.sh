#!/usr/bin/env bash

# Tested only on Debian 8 "Jessie" and Mac OS X 10.10

# Bash strict mode
set -euo pipefail
IFS=$'\n\t'


LIST='/tmp/pip2_list.txt' # Where we're temporarily keeping our stuff.

general_packages(){
	pip2 list | awk '{ print $1 }' | sed -e 's/-//g' -e 's/youtubedl/youtube-dl/g' -e '/^\s*$/d' | tail -n +2 > "$LIST"
}

choice_packages(){
	pip2 list | awk '{ print $1 }' | grep -Ei "pip2|livestreamer|youtube-dl|\
		thefuck|tldr|zenmap|paramiko|clf|Fabric|\
		speedtest-cli|setuptools|ohmu|haxor-news|httpie|stormssh|waybackpack|\
		http-prompt|glances|musicrepair" > "$LIST" 
}

pip2_upgrade(){
    while read -r package; do
        sudo -H pip2 install "$package" --upgrade
    done < "$LIST" || return 1
}

if [[ -z "$LIST" ]] ; then
	rm "$LIST"
fi

read -rp "General update (1) or just the favorites? (2)  " CHOICE

case "$CHOICE" in
	1)
		general_packages
		pip2_upgrade
		;;
	2)
		choice_packages
		pip2_upgrade
		;;
	*)
		echo "Please enter (1) or (2)"
		;;
esac

if [[ pip2_upgrade ]] ; then
    echo "Done."
    rm "$LIST"
else
    echo "There was an error. Please try again."
fi

