#!/bin/bash

## BlindySupport Cask/Brewfile

if [[ $(uname -s) != "Darwin" ]] ; then
    echo "ERROR: This script will only run on Mac OS X"
    exit 1
fi

# Be sure to install HomeBrew first via 'brew.sh'
# Or via ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Unix utilities
brew_array={archey axel curl exiftool csshx cowsay htop icdiff\
	irssi lynx mplayer mtr netcat osxfuse p7zip pstree sshfs\
	speedtest_cli pv rtmpdump tldr wget youtube-dl zsh git\
	gnu-units lnav ranger watch iftop}

# Casks
cask_array={alfred flux ccleaner virtualbox google-chrome firefox\
	vivaldi iterm2 adium slack skype sublime-text atom xquartz\
	spotify beardedspice livestream-producer gpgtools vlc wireshark\
	spectacle github gfxcardstatus superduper chrome-remote-desktop-host\
	handbrake teamviewer carbon-copy-cloner}

INSTALL_STUFF(){
	# Install utilities
	brew_install='brew install'

	for item in ${brew_array[*]} ; do
		$brew_install $item
	done
	
	# Install Caskroom
	$brew_install caskroom/cask/brew-cask

	cask_install='brew cask install'

	for item in ${cask_array[*]} ; do
		$cask_install $item
	done

	# Cleaning up after ourselves
	brew cleanup ; brew cask cleanup ; brew prune
}

UNINSTALL_STUFF(){
	UNINSTALL='brew uninstall'
	ZAP='brew cask zap'

	# killing brew utils
	for item in ${brew_array[*]} ; do
		$UNINSTALL $item
	done

	# zapping casks
	for item in ${cask_array[*]} ; do
		$ZAP $item
	done

	brew cleanup ; brew cask cleanup ; brew prune

	brew uninstall caskroom/cask/brew-cask
}

# Now onto the actual work...

echo "Install (1) or Uninstall (2) ?"
read response

case $response in
	1)
		INSTALL_STUFF
		;;
	2)
		echo "Are you sure? [y/n]"
		read response
		if [[ $response == "y" ]] ; then
			UNINSTALL_STUFF
		else
			exit
		fi
		;;
	*)
		echo "Please enter (1) or (2)"
		;;
esac

