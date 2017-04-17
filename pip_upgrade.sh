#!/bin/bash

# Tested only on Debian 8 "Jessie" and Mac OS X 10.10

# Bash strict mode
set -euo pipefail
IFS=$'\n\t'


LIST='/tmp/pip_list.txt' # Where we're temporarily keeping our stuff.

general_packages(){
	pip list | awk '{ print $1 }' > "$LIST"
}

choice_packages(){
	pip list | awk '{ print $1 }' | grep -Ei "pip|livestreamer|youtube-dl|\
    thefuck|tldr|zenmap|paramiko|clf|Fabric|\
    speedtest-cli|setuptools|ohmu|haxor-news|httpie|stormssh|waybackpack|\
    http-prompt|glances|musicrepair" > "$LIST" 
}

pip_upgrade(){
    while read -r package; do
        sudo -H pip install "$package" --upgrade
    done < "$LIST" || return 1
}

if [[ -z "$LIST" ]] ; then
	rm "$LIST"
fi

read -rp "General update (1) or just the favorites? (2)  " CHOICE

case "$CHOICE" in
	1)
		general_packages
		pip_upgrade
		;;
	2)
		choice_packages
		pip_upgrade
		;;
	*)
		echo "Please enter (1) or (2)"
		;;
esac

if [[ pip_upgrade ]] ; then
    echo "Done."
    rm "$LIST"
else
    echo "There was an error. Please try again."
fi

