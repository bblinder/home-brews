#!/bin/bash

set -euo pipefail # unofficial bash 'strict mode'
IFS=$'\n\t'

BACKUP_FILE="bblinder_backup-$(date +%F).tar.gz"
BACKUP_DIR="$HOME/BackUps"

cd /tmp/ && echo "Compressing..."

COMPRESS(){
    tar -cpzf "$BACKUP_FILE" ~/Documents ~/Downloads ~/.gnupg\
	    ~/.irssi ~/Music/MP3_convert.sh ~/Pictures ~/.ssh ~/.bashrc\
	    ~/.zshrc ~/Videos /etc/vim/vimrc ~/.config/terminator/config || return 1
}

COMPRESS # just adding a comment, since this looks lonely sitting here by itself.

if [[ COMPRESS ]] ; then
	mv /tmp/"$BACKUP_FILE" "$BACKUP_DIR"
	echo "All done. File size is $(du -sh "$BACKUP_DIR"/"$BACKUP_FILE" \
		| awk '{ print $1 }')"
else
	echo "Compression Failed."
fi

