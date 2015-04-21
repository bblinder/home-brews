#!/bin//bash

SYNC(){
    rsync -e ssh -avh --progress --delete --inplace --compress-level=0 ~/BackUps/bblinder_backup-$(date +%F).tar.gz pi@192.168.0.7:/media/GooseHaus1/shares/.bblinder_backup/ ; return 0

}

SYNC
if [[ $SYNC -eq 0 ]]
then
    echo "All done."
else
    echo "Sync failed."
fi

