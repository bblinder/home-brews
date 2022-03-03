#!/usr/bin/env bash

set -Eeuo pipefail
#IFS=$'\n\t'


COMMANDS="spotdl yt-dlp"

for cmd in $COMMANDS; do
    if ! command -v "$cmd" &> /dev/null ; then
    echo "$cmd not found. Please install with a package manager, e.g. brew install $cmd."
    exit 1
    fi
done

: '
if [[ ! "$(command -v spotdl)" ]]  ; then
    echo "::: spot-dl not installed. Exiting."
    exit 1
fi

if [[ ! "$(command -v yt-dlp)" ]] ; then
    echo "::: YT-dlp not installed. Exiting."
    exit 1
fi
'

spotdl "$@" --path-template '{playlist}/{artist} - {title}.{ext}'

## TODO
## use getops to provide options
## See: https://www.redhat.com/sysadmin/arguments-options-bash-scripts

