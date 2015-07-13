#!/bin/bash

cd /tmp/

echo "Compressing..."

COMPRESS(){
    tar -cpzf bblinder_backup-$(date +%F).tar.gz ~/Documents ~/Downloads ~/.gnupg ~/.irssi ~/Music/MP3_convert.sh ~/Pictures ~/.ssh ~/.bashrc ~/.zshrc ~/Videos /etc/vim/vimrc ~/.config/terminator/config ; return 0 || return 1

}

COMPRESS

if [[ $COMPRESS -eq 0 ]] ; then
	mv /tmp/bblinder_backup-$(date +%F).tar.gz ~/BackUps
	echo "All done. File size is $(du -sh ~/BackUps/bblinder_backup-$(date +%F).tar.gz | awk '{ print $1 }')"
else
	echo "Compression Failed."
fi

