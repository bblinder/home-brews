#!/bin/bash

set -euo pipefail
#unofficial bash 'strict mode'
IFS=$'\n\t'

# Assumes you've encrypted with GPG.
FILE_TO_TRANSFER="$HOME/path/to/backup-$(date +%F).tar.gz.gpg"

SYNC(){
    rsync -e ssh -avh --progress --compress-level=0 "$FILE_TO_TRANSFER" \
	    pi@[ip_address]:/path/to/backup/folder || return 1
}

if [[ -e "$FILE_TO_TRANSFER" ]] ; then
	SYNC
else
	echo "File to transfer not found."
	exit 1
fi

if [[ SYNC ]] ; then
	echo "All done."
else
    echo "Sync failed."
fi

