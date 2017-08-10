#!/bin/bash

# Bash strict mode
set -euo pipefail
IFS=$'\n\t'

LIST='/tmp/pip3_list.txt'

general_packages(){
	pip3 list | awk '{ print $1 }' > "$LIST"
}

pip3_upgrade(){
	while read -r package; do
		sudo -H pip3 install "$package" --upgrade
	done < "$LIST" || return 1
}

if [[ -z "$LIST" ]] ; then
	rm "$LIST"
fi

general_packages && pip3_upgrade

if [[ pip3_upgrade ]] ; then
	echo "Done."
	rm "$LIST"
else
	echo "There was a problem. Try again."
fi

