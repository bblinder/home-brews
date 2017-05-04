#!/bin/bash

## Blindy Cask/Brewfile

if [[ $(uname -s) != "Darwin" ]] ; then
	# Ruling out non-Mac OS X systems
	echo "::: ERROR: This script will only run on Mac OS X"
	exit 1
fi

# Be sure to install HomeBrew first via 'brew.sh'
# Or via ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# *nix utilities
brew_array=(archey ack axel curl cmus exiftool csshx cowsay htop icdiff\
	irssi httpie lynx mplayer mtr osxfuse p7zip pstree sshfs\
	speedtest_cli pv rtmpdump tldr wget youtube-dl zsh git\
	gnu-units lnav ranger watch iftop ffmpeg ssh-copy-id spoof-mac\
	newsbeuter parallel pdfgrep dtrx lepton sslh jq woof\
	zsh-syntax-highlighting mediainfo pandoc cheat figlet rig fortune httrack)

# Casks/GUI stuff
cask_array=(alfred flux ccleaner virtualbox google-chrome firefox\
	opera iterm2 adium slack skype sublime-text atom xquartz\
	spotify beardedspice the-unarchiver gpgtools vlc wireshark\
	spectacle github-desktop gfxcardstatus superduper chrome-remote-desktop-host\
	handbrake carbon-copy-cloner clipmenu etrecheck charles\
	malwarebytes-anti-malware postman jadengeller-helium oversight)

INSTALL_STUFF(){
	# Install HomeBrew
	ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

	# Install utilities
	brew_install='brew install'

	for item in ${brew_array[*]} ; do
		$brew_install "$item"
	done

	# Install Caskroom
	$brew_install caskroom/cask/brew-cask

	cask_install='brew cask install'

	for item in ${cask_array[*]} ; do
		$cask_install "$item"
	done

	# Cleaning up after ourselves
	brew cleanup ; brew cask cleanup ; brew prune
}

UNINSTALL_STUFF(){
	UNINSTALL='brew uninstall'
	ZAP='brew cask zap'

	# killing brew utils
	for item in ${brew_array[*]} ; do
		$UNINSTALL "$item"
	done

	# zapping casks
	for item in ${cask_array[*]} ; do
		$ZAP "$item"
	done

	brew cleanup ; brew cask cleanup ; brew prune

	brew uninstall caskroom/cask/brew-cask

}

PURGE_HOMEBREW(){
	read -rp "Do you want to remove HomeBrew as well? [y/n]   " response
	if [[ $response == "y" ]] ; then
		## a rare instance where homebrew requires sudo privileges.
		sudo ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/uninstall)"
	else
		exit 0
	fi
}

# Now onto the actual work...

read -rp "Install (1) or Uninstall (2) ?   " response
case $response in
	1)
		INSTALL_STUFF
		;;
	2)
		read -rp "Are you sure? [y/n]  " uninstall_response
		if [[ $uninstall_response == "y" ]] ; then
			UNINSTALL_STUFF
			PURGE_HOMEBREW
		else
			exit
		fi
		;;
	*)
		echo "::: Please enter (1) or (2)"
		;;
esac
