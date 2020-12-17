#!/usr/bin/env bash

## Blindy Cask/Brewfile

if [[ $(uname -s) != "Darwin" ]] ; then
	# Ruling out non-Mac OS systems
	echo "::: ERROR: This script will only run on Mac OS"
	exit 1
fi

# Be sure to install HomeBrew first via 'brew.sh'
# Or via ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# *nix utilities
brew_array=(ccat neofetch ack axel curl cmus exiftool csshx cowsay htop icdiff\
	irssi httpie lynx mplayer mtr osxfuse p7zip pstree sshfs tcpdump\
	speedtest_cli pv rtmpdump tldr wget youtube-dl zsh git m-cli\
	gnu-units lnav ranger watch iftop ffmpeg ssh-copy-id spoof-mac\
	parallel pdfgrep dtrx lepton sslh jq woof coreutils goaccess exa wifi-password\
	zsh-syntax-highlighting mediainfo pandoc rtv cheat figlet rig fortune httrack\
	akamai bat prettyping magic-wormhole python3 heroku streamlink imagemagick aria2\
	restic ncdu minikube lazydocker dive plantuml rkhunter switchaudio-osx rga)

# Casks/GUI stuff
cask_array=(alfred firefox krisp nightowl docker lulu obsidian onedrive \
	iterm2 xquartz caprine calibre ransomwhere microsoft-edge telegram \
	spotify beardedspice the-unarchiver gpgtools iina visual-studio-code \
	numi handbrake carbon-copy-cloner jumpcut etrecheckpro rectangle typora \
	charles visual-studio-code malwarebytes postman anki appcleaner \
	oversight font-input grandperspective bunch signal android-platform-tools \
	imageoptim deckset lastpass backblaze do-not-disturb reikey gas-mask appcleaner)

INSTALL_STUFF(){
	# Install HomeBrew
	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

	# Install utilities
	brew_install='brew install'

	if which brew >/dev/null 2>&1 ; then
		for item in ${brew_array[*]} ; do
			$brew_install "$item"
		done
	fi

	# Install Caskroom
	$brew_install caskroom/cask/brew-cask

	cask_install='brew install --cask'

	for item in ${cask_array[*]} ; do
		$cask_install "$item"
	done

	# Cleaning up after ourselves
	brew cleanup ; brew cask cleanup ; brew prune
}

UNINSTALL_STUFF(){
	UNINSTALL='brew uninstall'
	ZAP='brew uninstall --cask --zap'

	# killing brew utils
	for item in ${brew_array[*]} ; do
		$UNINSTALL "$item"
	done

	# zapping casks
	for item in ${cask_array[*]} ; do
		$ZAP "$item"
	done

	brew cleanup -s

	brew uninstall caskroom/cask/brew-cask

}

PURGE_HOMEBREW(){
	read -rp "Do you want to remove HomeBrew as well? [y/n]   " response
	if [[ $response == "y" ]] ; then
		## a rare instance where homebrew requires sudo privileges.
		/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/uninstall.sh)"
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
