#!/bin/bash

# Tested only on Debian 8 "Jessie"

pip list | awk '{ print $1 }' | egrep -i "(pip)|(livestreamer)|(youtube-dl)|\
    (thefuck)|(tldr)|(zenmap)|(paramiko)|(clf)|(Fabric)|\
    (speedtest-cli)" > /tmp/pip_list.txt

pip_upgrade(){
    while read package; do
        sudo pip install "$package" --upgrade
    done < /tmp/pip_list.txt &> /dev/null ; return 0 || return 1
}

if [[ -f /tmp/pip_list.txt ]] ; then
    echo "Updating..."
    pip_upgrade
else
    echo "Error: No update list found."
    exit 1
fi


if [[ pip_upgrade -eq 0 ]] ; then
    echo "Done."
    rm /tmp/pip_list.txt
else
    echo "There was an error. Please try again."
fi
