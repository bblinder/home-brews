#!/bin//bash

SYNC(){
    rsync -e ssh -avh --progress --delete --inplace --compress-level=0 ~/BackUps/ \
	    bblinder_backup-$(date +%F).tar.gz pi@raspberrypi:/path/to/.bblinder_backup/ ; return 0 \
	    || return 1
}

SYNC

if [[ $SYNC -eq 0 ]]; then
	echo "All done."
else
    echo "Sync failed."
fi

