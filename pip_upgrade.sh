#!/usr/bin/env bash

# Tested only on Debian 8 "Jessie" and Mac OS X 10.10

# Bash strict mode
set -euo pipefail
IFS=$'\n\t'


LIST='/tmp/pip2_list.txt' # Where we're temporarily keeping our stuff.

general_packages(){
	pip2 list | awk '{ print $1 }' | sed -e 's/-//g' -e 's/youtubedl/youtube-dl/g' -e '/^\s*$/d' | tail -n +2 > "$LIST"
}

pip2_upgrade(){
    while read -r package; do
        sudo -H pip2 install "$package" --upgrade
    done < "$LIST" || return 1
}

if [[ -z "$LIST" ]] ; then
	rm "$LIST"
fi

general_packages
pip2_upgrade

if [[ pip2_upgrade ]] ; then
    echo "Done."
    rm "$LIST"
else
    echo "There was an error. Please try again."
fi

