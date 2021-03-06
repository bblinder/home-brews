#!/usr/bin/env bash

# Bash strict mode
set -euo pipefail
IFS=$'\n\t'

LIST='/tmp/pip3_list.txt' # where we're temporarily keeping our stuff
trap '{ rm -f "$LIST"; }' EXIT # cleaning up on successful exit or ctrl-c.

general_packages(){
	python3 -m pip list --outdated | awk '{ print $1 }' | sed -e '/^\s*$/d' | tail -n +3 > "$LIST"
}

pip3_upgrade(){
	while read -r package; do
		python3 -m pip install "$package" --upgrade --user
	done < "$LIST" || return 1
}

if [[ -z "$LIST" ]] ; then
	rm "$LIST"
fi

echo -e "::: Updating python3 packages... please wait..."
general_packages && pip3_upgrade

if [[ pip3_upgrade ]] ; then
	echo "Done."
	rm "$LIST"
else
	echo "There was a problem. Try again."
fi
