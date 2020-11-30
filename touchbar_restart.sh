#!/usr/bin/env bash

#restarts the touchbar on my 2019 MBP

if [[ "$(id -u)" -ne 0 ]] ; then
	echo "::: Please run as root."
	exit
fi

if [[ "$(uname -s)" == "Darwin" ]] ; then
    pkill "Touch Bar agent"
    killall ControlStrip
else
    echo "This will only run on MacOS with a touchbar"
    exit 1
fi
