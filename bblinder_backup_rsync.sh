#########
# This is now deprecated, and kept here mainly for learning and historical purposes.
# I recommend using Restic (https://restic.net/) for your backup needs.
#########

#!/bin/bash

set -euo pipefail
#unofficial bash 'strict mode'
IFS=$'\n\t'

# Assumes you've encrypted with GPG.
FILE_TO_TRANSFER="$HOME/path/to/backup-$(date +%F).tar.gz.gpg"
SSH_KEY="$HOME/path/to/ssh/key"

SYNC(){
    rsync -e "ssh -p [port] -i $SSH_KEY" -avh --progress --compress-level=0 "$FILE_TO_TRANSFER" \
	    [pi]@[ip_address]:/path/to/backup/folder || return 1
}

if [[ -e "$FILE_TO_TRANSFER" ]] ; then
	SYNC
else
	echo "::: File to transfer not found."
	echo ""
	echo "::: Perhaps run the back up script first?"
	exit 1
fi

if [[ SYNC ]] ; then
	echo "::: All done."
else
        echo "::: Sync failed."
fi
