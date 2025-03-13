#!/usr/bin/env bash 

set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]] ; then
    echo "::: This script will only run on Linux systems"
    exit 1
elif 
    [[ "$linux_version" != "VERSION=8" ]] ; then
    echo "::: This script will only run on systems with systemd (Debian Jessie, etc.)"
    exit 1
fi

linux_version=$(cat /etc/*-release | grep -i "version=" | awk '{ print $1 }' | sed -e 's/"//g')

disable_suspend(){
    sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
}

enable_suspend(){
    sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target
}

read -rp "Disable (1) or Enable (2) Suspend? >  " SUSPEND_RESPONSE

case "$SUSPEND_RESPONSE" in
    1)
        disable_suspend
        ;;
    2)
        enable_suspend
        ;;
    *)
        echo "Please enter (1) or (2)"
        ;;
esac
