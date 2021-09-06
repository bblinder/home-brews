#!/usr/bin/env bash

# Tested only on Debian 8 "Jessie" and Mac OS X 10.10

# Bash strict mode
set -euo pipefail
IFS=$'\n\t'


LIST='/tmp/pip2_list.txt' # Where we're temporarily keeping our stuff.
trap '{ rm -f "$LIST"; }' EXIT # cleaning up on exit or ctrl-c.

general_packages(){
	python2 -m pip list --outdated | \
		awk '{ print $1 }' | sed -e '/^\s*$/d' | \
		tail -n +3 > "$LIST"
}

pip2_upgrade(){
    while read -r package; do
	    python2 -m pip install "$package" --upgrade --user --no-python-version-warning
    done < "$LIST" || return 1
}

if [[ -z "$LIST" ]] ; then
	rm "$LIST"
fi

echo -e "::: Updating python2 packages... please wait..."
general_packages
pip2_upgrade

if [[ pip2_upgrade ]] ; then
    echo "Done."
    rm "$LIST"
else
    echo "::: There was an error. Please try again."
fi
