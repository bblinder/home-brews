#!/bin/bash

set -euo pipefail 
# unofficial bash 'strict mode'
IFS=$'\n\t'

BACKUP_FILE="bblinder_backup-$(date +%F).tar.gz"
BACKUP_DIR="$HOME/BackUps"
FILE_TO_ENCRYPT="$BACKUP_DIR/$BACKUP_FILE"

cd /tmp/ && echo "Compressing..."

COMPRESS(){
    tar -cpzf "$BACKUP_FILE" ~/Documents ~/Downloads ~/.gnupg\
	    ~/.irssi ~/Pictures ~/.ssh ~/.bashrc\
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

ENCRYPT(){
	if [[ "$FILE_TO_ENCRYPT" ]] ; then
		echo "Encrypting... standby..."
		sudo gpg --symmetric "$FILE_TO_ENCRYPT" || return 1
	fi
}

ENCRYPT

if [[ ENCRYPT ]] ; then
	echo "Encryption done... ready for transfer."
	rm "$FILE_TO_ENCRYPT"
else
	echo "Encryption failed."
fi 
