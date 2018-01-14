#!/usr/bin/env bash

# Changes/restores my machine's MAC address. Useful for hostile or unfamiliar networks."

set -euo pipefail
IFS=$'\n\t'

if [[ "$(uname -s)" != "Linux" ]] ; then
    echo "::: ERROR this will only run on Linux systems"
    echo "::: Exiting..."
    exit 1
fi

if [[ "$EUID" -ne 0 ]] ; then
    echo "::: Please run as root" ; exit
fi

interface='wlp2s0'

if [[ ! "$(command -v macchanger)" ]] ; then
    echo "::: macchanger not installed"
    read -rp "::: Install it? [y/n] -->   "macchanger_response
    case "$macchanger_response" in
        [yY])
            apt-get install macchanger
            ;;
        [nN])
            exit
            ;;
    esac
else
    read -rp "Change MAC address (1) or restore MAC address (2)? -->   " MAC_change
    case "$MAC_change" in
        1)
            ifconfig "$interface" down
            echo "::: Changing MAC address to random value..."
            macchanger -A "$interface"
            ifconfig "$interface" up
            service network-manager restart
            ;;
        2)
            ifconfig "$interface" down
            echo "::: Restoring MAC address to original permanent value..."
            macchanger -p "$interface"
            ifconfig "$interface" up
            service network-manager restart
            ;;
        *)
            echo "::: Please enter (1) or (2)"
            ;;
    esac
fi
