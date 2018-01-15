#!/usr/bin/env bash

# Changes/restores my machine's MAC address. Useful for hostile or unfamiliar networks.

set -eu pipefail
IFS=$'\n\t'

if [[ "$(uname -s)" != "Linux" ]] ; then
    echo "::: ERROR this will only run on Linux systems"
    echo "::: Exiting..."
    exit 1
fi

if [[ "$EUID" -ne 0 ]] ; then
    echo "::: Please run as root" ; exit
fi

interface="wlp2s0" # insert whatever 'ifconfig' or similar shows you
current_mac="$(macchanger -s $interface | grep -i 'Current Mac:' | awk '{ print $3 }')"
permanent_mac="$(macchanger -s $interface | grep -i 'Permanent Mac:' | awk '{ print $3 }')"

if [[ ! -n "$interface" ]] ; then
    echo "::: Network interface can't be empty. Try running 'ifconfig' to get it."
    exit 1
fi

CHANGE_MAC(){
    ifconfig "$interface" down
    echo "::: Changing the MAC Address to random value..."
    macchanger -A "$interface"
    ifconfig "$interface" up
    service network-manager restart
}

RESTORE_MAC(){
    ifconfig "$interface" down
    echo "::: Restoring MAC Address to original, permanent value...\n\n"
    macchanger -p "$interface"
    ifconfig "$interface" up
    service network-manager restart
}

if [[ "$(command -v macchanger)" ]] ; then
    echo "::: Current MAC Address: '$current_mac'"
    echo "::: Permanent MAC Address: '$permanent_mac'"
    
    if [[ "$current_mac" != "$permanent_mac" ]] ; then
        read -rp "Change MAC address (1) or restore MAC address (2)? -->   " MAC_change_restore
        case "$MAC_change_restore" in
            1)
                CHANGE_MAC
                ;; 
            2)
                RESTORE_MAC
                ;;
            *)
                echo "::: Please enter (1) or (2)"
                ;;
        esac
    else
        read -rp "Change MAC address? [y/n] -->  " MAC_change
        case "$MAC_change" in
            [yY])
                CHANGE_MAC
                ;;
            [nN])
                exit
                ;;
            *)
                echo "::: Enter Y/N"
                ;;
        esac
    fi
fi

